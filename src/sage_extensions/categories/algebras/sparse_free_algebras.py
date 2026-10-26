r"""Tensor and symmetric products on the module of relationful words."""

from math import prod
from typing import Any

from sage.categories.map import Map
from sage.categories.morphism import SetMorphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import CategoricalMor
from sage_extensions.categories.algebras.algebras import (
    Algebras, MultiplicativeAlgebraMorphism, UnitalMultiplicativeAlgebraMor,
    UnitalMultiplicativeAlgebraMorphism,
    _AlgebraMorCommonMethods, _algebra_on_module,
)
from sage_extensions.categories.algebras.free_algebras import (
    FreeAlgebras, GradedFreeAlgebras, TensorAlgebras, SymmetricAlgebras,
    _symmetric_generator_images_commute,
)
from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.graded_modules import GradedModules, IntegerGradedModules
from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
from sage_extensions.categories.modules.pure.modules import (
    Modules, ModulesWithChosenComponentPresentation,
)
from sage_extensions.categories.modules.word_modules import (
    _WordModule, _WordModuleElement, _module_on_word_quotient, _has_component_presentation,
)
from sage_extensions.categories.rings.ring_foundation import OwnedRings
from sage_extensions.categories.sets.indexed_families import IndexedFamily, indexed_family
from sage_extensions.categories.sets.set_categories import Sets as OwnedSets
from sage_extensions.logic import AtomicProposition, conjunction
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _SparseFreeAlgebra(_WordModule):
    r"""The word-module realization with algebra ingress and word maps.

    The root owns the product.  The actual module quotient, homogeneous
    pieces, framing and arithmetic are inherited from its module realization.
    """

    def __init__(self, word_presentation, **rest) -> None:
        source = word_presentation.source_module()
        match source in FramedFreeModules(source.base_ring()):
            case True:
                # This realization is the free algebra on the selected module
                # basis, so its selected free-algebra framing is the identity.
                rest["algebra_framing_source"] = self
            case False:
                pass
        super().__init__(word_presentation, **rest)

    def flavor(self):
        return self.word_flavor()

    def _source_has_component_protocol(self):
        return _has_component_presentation(self.generating_module())

    def _algebra_mor_class(self):
        return SparseFreeAlgebraMor

    def algebra_mor(self, mor_family, codomain):
        return SparseFreeAlgebraMor(mor_family, self, codomain)

    def _element_constructor_(self, value):
        source = element_parent(value)
        match value:
            case _ if source is self:
                return value
            case _ if source is self.generating_module():
                return self.from_component(1, value)
            case dict():
                return super()._element_constructor_(value)
            case _ if source in Modules(self.base_ring()) and self._built_on_the_same_data(source):
                return self._element_on_the_same_data(source, value)
            case _ if value in self.base_ring():
                return self.scalar_multiple(self.base_ring()(value), self.one())
            case _:
                return super()._element_constructor_(value)

    def _realize_graded_piece_basis_label(self, degree, label):
        return self.from_component(degree, self.graded_piece(degree).module_generator(label))

    def _commutativity_decision(self):
        size = self.algebra_generating_set().cardinality()
        match self.flavor():
            case "symmetric":
                return True
            case _ if size.is_finite() and int(size.finite_value()) <= 1:
                return True
            case _ if self.generating_module() in FramedFreeModules(self.base_ring()) and (self.base_ring().one() != self.base_ring().zero()) is True:
                return False
            case _:
                return AtomicProposition("is_commutative", self)

    def is_central(self, element):
        element = self(element)
        if all(
            int(label.summand_index()) == 0
            for label in self._framing_lift(self(element)).support().domain()
        ):
            return True
        if self.is_commutative() is True:
            return True
        labels = self.algebra_generating_set()
        if not labels.cardinality().is_finite():
            return AtomicProposition("is_central", self, element)
        return conjunction(element * self.algebra_generator(label) == self.algebra_generator(label) * element for label in labels)

    @cached_method
    def ring_center(self):
        if self.is_commutative() is True:
            return self
        return self.predicate_subring(self.is_central, "commutes with all algebra generators", OwnedRings().Commutative())

    def _repr_(self):
        name = "T" if self.flavor() == "tensor" else "Sym"
        return f"{name}({self.generating_module()})"


def _word_product(module, left, right):
    r"""Concatenate words, or add multiset exponents, in the module quotient."""
    def product_label(left_label, right_label):
        s, t = int(left_label.summand_index()), int(right_label.summand_index())
        left_word, right_word = left_label.summand_element(), right_label.summand_element()
        labels = module.degree_basis(s + t)
        match module.word_flavor():
            case "tensor":
                word = labels(lambda i: left_word.component(int(i)) if int(i) < s else right_word.component(int(i) - s))
            case "symmetric":
                support = set(left_word.support()) | set(right_word.support())
                word = labels.from_multiplicities({label: left_word.multiplicity(label) + right_word.multiplicity(label) for label in support})
        return module.basis_label(s + t, word)

    left_coordinates = module.framing_morphism().lift(left)
    right_coordinates = module.framing_morphism().lift(right)
    return sum((
        module.scalar_multiple(left_coordinates(x) * right_coordinates(y), module.module_generator(product_label(x, y)))
        for x in left_coordinates.support().domain()
        for y in right_coordinates.support().domain()
    ), module.zero())


class SparseFreeAlgebraMorphism:
    r"""Word evaluation retaining its generating module map and descent laws.

    Tensor extension uses the actual linear map from the generating module.
    Symmetric extension also needs its images to commute. An exact map on
    the whole algebra retains its evaluator instead of being reinterpreted
    as generator data. The existing module and algebra validators decide
    those retained premises only when requested.
    """

    def _elementwise_linearity_derivation(self):
        if self._source_element_map is not None:
            return super()._elementwise_linearity_derivation()
        linearity = self._generating_module_morphism.linearity_decision()
        source = self.domain().generating_module()
        if (
            self.domain().flavor() == "tensor"
            or source in FramedFreeModules(source.base_ring())
        ):
            return linearity
        # For a relationful symmetric source, degree-one relations alone
        # do not make ordered word evaluation descend linearly. Commuting
        # images supply that implication. A failed implication does not
        # by itself refute linearity of the chosen representative function.
        commuting = _symmetric_generator_images_commute(
            self.codomain(), self._generator_images
        )
        if commuting is not None and commuting is not False and linearity is not False:
            return conjunction((linearity, commuting))
        return super()._elementwise_linearity_derivation()

    def _multiplicativity_derivation(self):
        derived = super()._multiplicativity_derivation()
        if derived is not None:
            return derived
        if self._source_element_map is not None:
            return None
        linearity = self._generating_module_morphism.linearity_decision()
        if self.domain().flavor() == "tensor":
            return linearity
        commuting = _symmetric_generator_images_commute(
            self.codomain(), self._generator_images
        )
        return None if commuting is None else conjunction((linearity, commuting))

    def _unit_preservation_derivation(self):
        derived = super()._unit_preservation_derivation()
        if derived is not None:
            return derived
        return None if self._source_element_map is not None else True

    def __init__(
        self, parent, images, *, _construction_premises=None,
        _transported_morphism=None,
    ) -> None:
        if (
            _transported_morphism is None
            and isinstance(images, UnitalMultiplicativeAlgebraMorphism)
            and images.domain() is parent.domain()
            and images.codomain() is parent.codomain()
        ):
            _transported_morphism = images
        domain = parent.domain()
        codomain = parent.codomain()
        source = domain.generating_module()
        labels = domain.algebra_generating_set()
        self._source_element_map = None
        self._generating_module_morphism = None
        if isinstance(images, Map):
            if images.codomain() is not codomain:
                raise ValueError(
                    f"a map into {codomain} must retain that exact codomain, but {images} "
                    f"ends at {images.codomain()}"
                )
            if images.domain() is domain:
                self._source_element_map = images
                images = indexed_family(
                    labels,
                    lambda label: codomain(self._source_element_map(domain.algebra_generator(label))),
                    name="Generator images",
                )
            elif images.domain() is source:
                generator_mor = Modules(domain.base_ring()).Mor(source, codomain)
                self._generating_module_morphism = (
                    images if images in generator_mor else generator_mor.elementwise(images)
                )
                images = indexed_family(
                    labels,
                    lambda label: self._generating_module_morphism(source.module_generator(label)),
                    name="Generator images",
                )
            elif images.domain() is not labels:
                raise ValueError(
                    f"a map out of {domain} must be stated on that algebra, its generating "
                    f"module {source}, or its generator labels {labels}, not on {images.domain()}"
                )
        if isinstance(images, IndexedFamily):
            source_indices = images.index_set()
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images[source_indices(label)]),
                name="Generator images",
            )
        elif isinstance(images, dict):
            if not labels.cardinality().is_finite():
                raise TypeError(
                    f"a dictionary of generator images needs finitely many algebra generators of {domain}, but it "
                    f"has {labels.cardinality()}; give a function or an indexed family"
                )
            missing = [label for label in labels if label not in images]
            if missing:
                raise ValueError(
                    f"the images of the algebra generators of {domain} must be given for every generator, but "
                    f"{missing} are missing"
                )
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images[label]),
                name="Generator images",
            )
        elif callable(images):
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images(label)),
                name="Generator images",
            )
        else:
            raise TypeError(
                f"a morphism out of {domain} is given by the images of its algebra generators, but got {images!r}"
            )
        self._raw_image = self._generator_images.value
        self._component_maps: dict[Any, Any] = {}
        if self._source_element_map is None and self._generating_module_morphism is None:
            self._generating_module_morphism = Modules(domain.base_ring()).Mor(
                source, codomain
            )(self._raw_image)
        linear_mor = domain.module_category().Mor(domain, codomain)
        if self._source_element_map is not None:
            linear = linear_mor.elementwise(self._source_element_map)
        else:
            # The retained generating map and (for Sym) commutation equations
            # supply linearity above. An arbitrary word evaluator carries no
            # empty-premise certificate at this ordinary module ingress.
            linear = linear_mor.elementwise(lambda element: self._call_(element))
        super().__init__(
            parent, linear, _construction_premises=_construction_premises,
            _transported_morphism=_transported_morphism,
        )

    def algebra_generator_images(self):
        return self._generator_images

    def algebra_generator_morphism(self):
        return SetMorphism(
            OwnedSets().Mor(self.domain().algebra_generating_set(), self.codomain()),
            self._generator_images.value,
        )

    def _component_map(self, key):
        cached = self._component_maps.get(key)
        if cached is not None:
            return cached
        source = self.domain().generating_module()
        component = source.module_component(key)
        certified = component.module_category().Mor(component, self.codomain())(
            lambda component_label: self._raw_image(
                source.module_label_from_component(key, component_label)
            )
        )
        # Evaluation touches this actual component only. Its chosen relations
        # can refute the assignment; undecided equations remain premises.
        if certified.linearity_decision() is False:
            raise ValueError(
                f"the generator images do not respect the module relations of {component}"
            )
        self._component_maps[key] = certified
        return certified

    def _image(self, label):
        source = self.domain().generating_module()
        if not self.domain()._source_has_component_protocol():
            return self._raw_image(label)
        key = source.module_component_key(label)
        component_label = source.module_component_generator_label(label)
        component = source.module_component(key)
        return self._component_map(key)(component.module_generator(component_label))

    def _basis_image(self, basis_label):
        basis_label = self.domain().module_generating_set()(basis_label)
        inner = basis_label.summand_element()
        if self.domain().flavor() == "tensor":
            factors = (self._image(inner.component(position)) for position in inner.parent().index_set())
        else:
            factors = (self._image(label) for label in inner.support() for _ in range(int(inner.multiplicity(label))))
        return prod(factors, start=self.codomain().one())

    def _call_(self, element):
        if self._source_element_map is not None:
            return self.codomain()(self._source_element_map(self.domain()(element)))
        coordinates = self.domain().framing_morphism().lift(element)
        return sum(
            (coordinates(label) * self._basis_image(label) for label in coordinates.support().domain()),
            self.codomain().zero(),
        )

    def __call__(self, element):
        return self._call_(element)

    def __mul__(self, other):
        # Retain the composite of the actual maps, including unresolved or
        # failed premises of whole-algebra input. Generator reconstruction
        # would replace a nonunital zero map by the unital augmentation.
        return MultiplicativeAlgebraMorphism.__mul__(self, other)

    def _postcompose_algebra_morphism(self, morphism):
        r"""Return the exact composite ``morphism ∘ self`` in the common theory."""
        return MultiplicativeAlgebraMorphism.__mul__(morphism, self)


class SparseFreeAlgebraMor(_AlgebraMorCommonMethods, UnitalMultiplicativeAlgebraMor):
    ElementMethods = SparseFreeAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        assert domain in TensorAlgebras(domain.base_ring()) or domain in SymmetricAlgebras(domain.base_ring()), (
            f"a morphism given on words needs a tensor algebra or a symmetric algebra as domain, but "
            f"{domain} is neither"
        )
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, images):
        r"""Extend defining generator data through the free-algebra universal property."""
        if isinstance(images, Map):
            if self._already_parented_arrow(images):
                return images
            source = self.domain()
            generating = source.generating_module()
            labels = source.algebra_generating_set()
            generator_mor = generating.module_category().Mor(generating, self.codomain())
            label_mor = Sets().Mor(labels, self.codomain())
            if not (generator_mor.accepts(images) or label_mor.accepts(images)):
                raise TypeError(f"{images} is a whole arrow of another Mor; give the free-generator map")
        return self.element_class(self, images)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self(lambda label: self.domain().algebra_generator(label))



def SparseFreeAlgebra(module, flavor):
    return _sparse_free_algebra_of(module, flavor)


def SparseFreeAlgebraElement(parent, coefficients):
    return parent.linear_combination(coefficients)


def SparseFreeAlgebraDegreeModule(algebra, degree):
    return algebra.graded_piece(degree)


def SparseFreeAlgebraDegreeElement(parent, algebra_element):
    return parent(algebra_element.homogeneous_component(parent.degree()))


def _sparse_tensor_algebra_of(module):
    return _sparse_free_algebra_of(module, "tensor")


def _sparse_symmetric_algebra_of(module):
    return _sparse_free_algebra_of(module, "symmetric")


@cached_function(key=lambda source, flavor: (id(source), flavor))
def _sparse_free_algebra_of(source, flavor):
    r"""Construct the module quotient, its tensor multiplication, then the algebra."""
    ring = source.base_ring()
    module = _module_on_word_quotient(source, flavor)
    tensor = Modules(ring).tensor_product((module, module))
    multiplication = tensor.from_bilinear_map(module, lambda x, y: _word_product(module, x, y))
    flavor_category = TensorAlgebras(ring) if flavor == "tensor" else SymmetricAlgebras(ring)
    categories = (flavor_category, IntegerGradedModules(ring))
    match source.module_generating_set().is_finite():
        case True:
            categories = (
                *categories,
                Algebras(ring)
                .Associative()
                .Unital()
                .FinitelyGeneratedAsAlgebra(),
            )
        case False:
            pass
    if source in FramedFreeModules(ring):
        # The source basis gives a free direct sum on words or monomials.
        # Projectivity records that theorem while component coordinates
        # remain supplied by the existing word-module realization.
        categories = (
            *categories, FreeAlgebras(ring), GradedFreeAlgebras(ring),
            Modules(ring).Projective(),
        )
        if flavor == "tensor":
            categories += (
                Algebras(ring).Associative().Unital().ProjectiveAsAlgebra(),
            )
        if source.module_generating_set().is_finite() is True:
            # Finite free tensor generators need no relations; a symmetric
            # algebra additionally has finitely many commutator relations.
            categories += (
                Algebras(ring).Associative().Unital().FinitelyPresentedAsAlgebra(),
            )
    realization_owner = Cat().meet((
        GeneralModules(ring), GradedModules(ring),
        ModulesWithChosenComponentPresentation(ring), Algebras(ring), *categories,
    ))
    unit_piece = module.graded_piece(0)
    law_decisions = {"associativity": True, "unit": True, "grading": True}
    match flavor:
        case "symmetric":
            law_decisions["commutativity"] = True
        case "tensor":
            pass
    algebra_generating_family = indexed_family(
        source.module_generating_set(),
        lambda label: module.from_component(1, source.module_generator(label)),
    )
    return _algebra_on_module(
        module, multiplication, placement=categories,
        unit=module.from_component(0, unit_piece.module_generator(0)),
        construction_data={
            "_engine": (realization_owner, _SparseFreeAlgebra, _WordModuleElement),
            "algebra_generating_family": algebra_generating_family,
        },
        law_decisions=law_decisions,
    )


__all__ = [
    "SparseFreeAlgebra", "SparseFreeAlgebraDegreeElement", "SparseFreeAlgebraDegreeModule",
    "SparseFreeAlgebraElement", "SparseFreeAlgebraMor", "SparseFreeAlgebraMorphism",
]
