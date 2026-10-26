r"""Exterior and divided-power algebras assembled from their graded pieces.

For a finitely presented module ``M`` the authoritative degree pieces are the
module constructions ``Lambda^n(M)`` and ``Gamma^n(M)``.  This module forms
their direct sum as an algebra; no second quotient-ring presentation is kept.
"""

from sage.categories.map import Map
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
)
from sage_extensions.categories.algebras.algebras import Algebras, MultiplicativeAlgebraMorphism, _algebra_on_module
from sage_extensions.categories.algebras.graded_algebras import _graded_multiplication_from_components
from sage_extensions.categories.modules.graded_modules import GradedModuleMorphismMethods, GradedModules
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import OwnedSetMorphism
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _PowerAlgebra:
    r"""The power construction on a graded module, without duplicate arithmetic."""

    def __init__(self, generating_module, power_flavor, **rest) -> None:
        self._generating_module = generating_module
        self._power_flavor = power_flavor
        super().__init__(**rest)

    def generating_module(self):
        r"""The exact input M of Lambda(M) or Gamma(M), not its full graded sum.

        In Gamma(M), degree one need not generate the ordinary algebra;
        generating_module names the input of the divided-power functor.
        """
        return self._generating_module

    def degree_one_generator(self, label):
        r"""Return the canonical degree-one image of a selected generator of ``M``."""
        source = self.generating_module()
        return self.from_component(1, source.module_generator(label))

    def _power_algebra_mor_class(self):
        return PowerAlgebraMor

    def _element_constructor_(self, value):
        source = element_parent(value)
        match value:
            case _ if source is self:
                return value
            case _ if source is self.base_ring():
                # If the input module is R itself, its degree-one copy and
                # the algebra's scalars are different maps. Ordinary scalar
                # ingress uses degree zero; from_component(1, value) retains
                # the explicit degree-one inclusion.
                return self.scalar_multiple(value, self.one())
            case _ if source is self.generating_module():
                return self.from_component(1, value)
            case _ if source is self.unformed_module():
                # The algebra is built on the graded module M: an element of
                # M passes by the module-level coercion of that construction.
                return super()._element_constructor_(value)
            case dict():
                return super()._element_constructor_(value)
            case _ if self.base_ring().is_parent_of(value) is True:
                # Membership is a proposition; only a decided one routes here.
                return self.scalar_multiple(self.base_ring()(value), self.one())
            case _:
                return super()._element_constructor_(value)

    def _commutativity_decision(self):
        match self._power_flavor:
            case "divided":
                return True
            case _:
                if (self.base_ring()(2) == self.base_ring().zero()) is True:
                    return True
                size = self.generating_module().module_generating_set().cardinality()
                # A cyclic module has no nonzero exterior degrees above one.
                # The owned cardinal comparison may itself remain undecided.
                if (size <= 1) is True:
                    return True
                return AtomicProposition("is_commutative", self)

    def _repr_(self):
        symbol = "Lambda" if self._power_flavor == "alternating" else "Gamma"
        return f"{symbol}({self.generating_module()})"


class _PowerAlgebraElement:
    r"""An element of ``Lambda(M)`` or ``Gamma(M)`` as the sum of its homogeneous components.

    The degree-zero piece is ``Lambda^0(M) = Gamma^0(M) = R``, so its component
    is written as the scalar the augmentation ``Lambda(M) -> R`` reads from it;
    a component of positive degree is written in its own power module.
    """

    def _repr_(self):
        terms = []
        for degree, component in self.homogeneous_components().items():
            match degree:
                case _ if degree == 0:
                    terms.append(str(self.parent().augmentation()(self)))
                case _:
                    terms.append(str(component))
        return " + ".join(terms) if terms else "0"


class PowerAlgebraMorphism:
    r"""A power-construction map, or an exact map with its graded algebra laws.

    A map ``M -> N`` induces the degreewise power maps. For exterior
    algebras a map with the literal whole-algebra endpoints retains that
    function and its ordinary law diagnostics. Divided-power construction
    maps require the degree-one datum: a graded ordinary algebra map need
    not preserve divided powers. Generator images in the target algebra retain the
    equations identifying them with their degree-one components; zero is
    a legitimate such image, and unresolved equations remain premises.
    """

    @cached_method
    def _degree_one_image_decision(self):
        r"""The retained generator-image equations, without enumerating an infinite family."""
        data = self._degree_one_image_data
        if data is None:
            return True
        labels = data.index_set()
        if labels.is_finite() is not True:
            return AtomicProposition("degree_one_images", data)
        return conjunction(data[label][2] for label in labels)

    def _elementwise_linearity_derivation(self):
        if self._power_source_map is not None:
            return self._power_linear_map.linearity_decision()
        return conjunction((
            self.degree_one_map().linearity_decision(),
            self._degree_one_image_decision(),
        ))

    def _multiplicativity_derivation(self):
        if self._power_source_map is not None:
            from sage_extensions.categories.group.magmas import Magmas

            if self._power_source_map in Magmas().Mor(self.domain(), self.codomain()):
                return self._power_source_map.is_multiplicative()
            return None
        return True if self._elementwise_linearity_derivation() is True else None

    def _unit_preservation_derivation(self):
        # The induced degree-zero map is id_R, independently of whether
        # the degree-one linearity premise has been decided.
        if self._power_source_map is None:
            return True
        unital = Algebras(self.domain().algebra_base_ring()).Unital()
        if self._power_source_map in unital.Mor(self.domain(), self.codomain()):
            return self._power_source_map.preserves_unit()
        return None

    def _degree_preservation_derivation(self):
        if self._power_source_map is None:
            return True
        if isinstance(self._power_source_map, GradedModuleMorphismMethods):
            return self._power_source_map.degree_preservation_decision()
        return None

    def __init__(self, parent, degree_one_map) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        source_module = domain.generating_module()
        target_module = codomain.generating_module()
        generator_mor = source_module.module_category().Mor(source_module, target_module)
        linear_mor = domain.module_category().Mor(domain, codomain)
        # AlgebraMorphism is also an actual generated lower provider and
        # owns _source_element_map; keep this construction's datum distinct.
        self._power_source_map = None
        self._power_linear_map = None
        self._degree_one_map = None
        self._degree_one_image_data = None
        linear = None
        if isinstance(degree_one_map, Map):
            if degree_one_map.domain() is domain and degree_one_map.codomain() is codomain:
                assert domain._power_flavor == "alternating", (
                    f"a map of divided-power constructions {domain} -> {codomain} needs its "
                    f"selected linear map {source_module} -> {target_module}; there is no selected "
                    "procedure here proving that this whole algebra map preserves all divided powers"
                )
                self._power_source_map = degree_one_map
                linear = linear_mor.elementwise(degree_one_map)
                self._degree_one_map = generator_mor._from_constructed_element_map(
                    lambda element: linear(domain.from_component(1, element)).homogeneous_component(1),
                    premises=(linear,),
                )
            elif degree_one_map.domain() is source_module and degree_one_map.codomain() is target_module:
                self._degree_one_map = (
                    degree_one_map if degree_one_map in generator_mor
                    else generator_mor.elementwise(degree_one_map)
                )
            elif degree_one_map.domain() is not source_module.module_generating_set():
                raise ValueError(
                    f"cannot view {degree_one_map} as the degree-one part {source_module} -> {target_module} of a "
                    f"power algebra morphism or an exact whole map {domain} -> {codomain}: it is a map "
                    f"{degree_one_map.domain()} -> {degree_one_map.codomain()}"
                )
        if self._degree_one_map is None:
            def target_data(label):
                image = degree_one_map[label] if isinstance(degree_one_map, dict) else degree_one_map(label)
                if element_parent(image) is codomain:
                    component = image.homogeneous_component(1)
                    equation = image == codomain.from_component(1, component)
                    if equation is False:
                        raise ValueError(
                            f"the image {image} of the generator {label} must lie in degree 1 of {codomain}"
                        )
                    return image, component, equation
                if image not in target_module:
                    raise ValueError(
                        f"the image {image} of the generator {label} must lie in {target_module}"
                    )
                return image, target_module(image), True

            self._degree_one_image_data = indexed_family(
                source_module.module_generating_set(), target_data,
                name="Degree-one images and their reconstruction equations",
            )
            self._degree_one_map = generator_mor(
                lambda label: self._degree_one_image_data[label][1]
            )
        if linear is None:
            linear = linear_mor._from_constructed_element_map(
                lambda element: self._call_(element),
                premises=(self.degree_one_map(),),
            )
        self._power_linear_map = linear
        super().__init__(parent, linear)

    def degree_one_map(self):
        return self._degree_one_map

    def _call_(self, element):
        if element_parent(element) is not self.domain():
            element = self.domain()(element)
        if self._power_source_map is not None:
            return self.codomain()(self._power_source_map(element))
        result = self.codomain().zero()
        degree_one_map = self.degree_one_map()
        for degree, component in element.homogeneous_components().items():
            match self.domain()._power_flavor:
                case "alternating":
                    mapped = degree_one_map.exterior_power(degree)(component)
                case "divided":
                    mapped = degree_one_map.divided_power(degree)(component)
            result += self.codomain().from_component(degree, mapped)
        return result

    def __call__(self, element):
        return self._call_(element)

    is_identity = OwnedSetMorphism.is_identity

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if other not in self.parent():
            return op == op_NE
        if self is other:
            return op == op_EQ
        if (
            isinstance(other, PowerAlgebraMorphism)
            and self._power_source_map is None
            and other._power_source_map is None
        ):
            left, right = self.degree_one_map(), other.degree_one_map()
            if left is right:
                return op == op_EQ
            mor = left.domain().module_category().Mor(left.domain(), left.codomain())
            equal = mor.elementwise(left) == mor.elementwise(right)
        else:
            forget = Algebras(self.domain().algebra_base_ring()).underlying_module()
            equal = forget(self) == forget(other)
        return equal if op == op_EQ else negation(equal)

    def __mul__(self, other):
        if (
            not isinstance(other, PowerAlgebraMorphism)
            or other.codomain() is not self.domain()
            or self._power_source_map is not None
            or other._power_source_map is not None
        ):
            return MultiplicativeAlgebraMorphism.__mul__(self, other)
        if self.domain() is self.codomain() and self is self.parent().identity():
            return other
        if other.domain() is other.codomain() and other is other.parent().identity():
            return self
        return self.parent().mor_category().Mor(other.domain(), self.codomain())(
            self.degree_one_map() * other.degree_one_map()
        )


class PowerAlgebraMor(CategoricalMor):
    ElementMethods = PowerAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        category = mor_family.base_category()
        assert domain in category and codomain in category, (
            f"a morphism in {category} needs two of its objects, but got {domain} and {codomain}"
        )
        if domain._power_flavor != codomain._power_flavor:
            raise ValueError(
                f"morphisms of power algebras preserve the construction, but {domain} is {domain._power_flavor} and "
                f"{codomain} is {codomain._power_flavor}"
            )
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"morphisms of power algebras {domain} -> {codomain} need one base ring, but they are over "
                f"{domain.base_ring()} and {codomain.base_ring()}"
            )
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def _element_constructor_(self, degree_one_map):
        return self.element_class(self, degree_one_map)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        module = self.domain().generating_module()
        return self(module.module_category().Mor(module, module).identity())



def PowerAlgebraElement(parent, components):
    r"""Construct a power-algebra element from homogeneous components."""
    return parent.from_components(components)


def PowerAlgebra(module, flavor):
    r"""The named power construction, through its category entry."""
    from sage_extensions.categories.algebras.free_algebras import AlternatingAlgebras, DividedPowerAlgebras

    match flavor:
        case "alternating":
            return AlternatingAlgebras(module.base_ring())(module)
        case "divided":
            return DividedPowerAlgebras(module.base_ring())(module)
        case _:
            raise ValueError(
                f"a power algebra is alternating or divided, but got flavor {flavor!r}"
            )


@cached_function(key=lambda source, flavor: (id(source), flavor))
def _power_algebra_of(source, flavor):
    r"""The graded sum and product of the module's exterior or divided powers.

    The degree owners supply the wedge/divided product, including their
    relations; distributive extension is the shared graded-algebra classifier.
    See Mathlib LinearAlgebra/ExteriorAlgebra/Basic and Algebra/DirectSum/Ring;
    divided-power multiplication uses the identities in Stacks, Tag 07GL.
    """
    from sage_extensions.categories.algebras.free_algebras import AlternatingAlgebras, DividedPowerAlgebras
    from sage_extensions.categories.algebras.algebras import _scalar_module
    from sage_extensions.categories.algebras.augmented_algebras import (
        _augmented_algebra,
    )
    from sage_extensions.categories.algebras.comparison_maps import (
        _constructed_algebra_morphism,
    )
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )
    from sage_extensions.categories.modules.pure.modules import (
        ModulesWithChosenFinitePresentation,
    )

    ring = source.base_ring()
    if source not in FramedFreeModules(ring) and source not in ModulesWithChosenFinitePresentation(ring):
        raise NotImplementedError(
            f"the {flavor} algebra of {source} exists over {ring}, but its "
            "current graded-piece realization requires a selected free "
            "framing or finite module presentation"
        )
    graded = GradedModules(ring)
    match flavor:
        case "alternating":
            category = AlternatingAlgebras(ring)
            power = source.exterior_power
            product = source.exterior_power_product
        case "divided":
            category = DividedPowerAlgebras(ring)
            power = source.divided_power_module
            product = source.divided_power_product
        case _:
            raise ValueError(
                f"a power algebra is alternating or divided, but got flavor {flavor!r}"
            )

    def piece(degree):
        match degree < 0:
            case True:
                return ring.free_module(0)
            case False:
                return power(degree)

    module = graded(indexed_family(graded.grading_monoid(), piece))
    multiplication = _graded_multiplication_from_components(module, product)
    unit = module.from_component(0, module.graded_piece(0).module_generator(0))
    law_decisions = {"associativity": True, "unit": True, "grading": True}
    match flavor:
        case "divided":
            law_decisions["commutativity"] = True
            algebra_generating_family = indexed_family(
                module.module_generating_set(),
                module.module_generator,
            )
        case "alternating":
            algebra_generating_family = indexed_family(
                source.module_generating_set(),
                lambda label: module.from_component(1, source.module_generator(label)),
            )
    algebra = _algebra_on_module(
        module, multiplication, placement=(category,), unit=unit,
        construction_data={
            "generating_module": source,
            "power_flavor": flavor,
            "algebra_generating_family": algebra_generating_family,
        },
        law_decisions=law_decisions,
    )

    def augmentation_value(value):
        component = algebra(value).homogeneous_component(0)
        coordinates = algebra.graded_piece(0).framing_morphism().lift(component)
        return ring(coordinates(0))

    # Every nonzero homogeneous degree is positive. The degree-zero
    # projection is therefore an algebra map, and its restriction to the
    # scalar summand is the identity. AugmentedAlgebras supplies that same
    # structural arrow on the resulting enriched object.
    augmentation = _constructed_algebra_morphism(
        algebra, _scalar_module(ring), augmentation_value,
    )
    return _augmented_algebra(augmentation, constructing_category=category)


def _alternating_algebra_of(module):
    return PowerAlgebra(module, "alternating")


def _divided_power_algebra_of(module):
    return PowerAlgebra(module, "divided")


def _alternating_extension(module_morphism):
    r"""Extend an alternating linear map uniquely to ``Lambda(M) -> A``.

    The target is an arbitrary represented unital associative algebra over the
    same base ring.  The selected generator images must square to zero and
    anticommute, exactly the relations defining the exterior algebra.  The
    current verification is finite-framing based; no finite subset is sampled
    from an infinite framing. Undecided square and pair equations are retained
    with the actual linear-map premise, rather than declared proved.
    """
    from sage_extensions.categories.algebras.algebras import Algebras
    from sage_extensions.categories.algebras.comparison_maps import (
        _constructed_algebra_morphism,
    )
    from sage_extensions.logic import conjunction

    if not isinstance(module_morphism, ModuleMorphismMethods):
        raise TypeError(
            f"the extension Lambda(M) -> A starts from a module morphism M -> A, but {module_morphism!r} "
            "is not one"
        )
    module = module_morphism.domain()
    target = module_morphism.codomain()
    base = module.base_ring()
    if target not in Algebras(base).Associative().Unital():
        raise TypeError(
            f"the extension Lambda(M) -> A needs A to be a unital associative algebra, but {target} is not one"
        )
    assert module.has_selected_module_resolution(), (
        f"computing the extension Lambda({module}) -> {target} needs a selected "
        "finite module-generating family; no such presentation is retained"
    )
    labels = module.module_generating_set()
    cardinality = labels.cardinality()
    assert cardinality.is_finite(), (
        f"the extension Lambda(M) -> A is checked on finitely many generators of M = {module}, but it "
        f"has {cardinality}"
    )
    labels = tuple(labels)
    images = {
        label: target(module_morphism(module.module_generator(label)))
        for label in labels
    }
    zero = target.zero()
    square_equations = tuple(image * image == zero for image in images.values())
    if conjunction(square_equations) is False:
        raise ValueError(
            f"{module_morphism} does not extend to Lambda(M) -> A: some generator image does not square to "
            f"0 in {target}"
        )
    pair_equations = tuple(
        images[left] * images[right] + images[right] * images[left] == zero
        for position, left in enumerate(labels)
        for right in labels[position + 1 :]
    )
    if conjunction(pair_equations) is False:
        raise ValueError(
            f"{module_morphism} does not extend to Lambda(M) -> A: some generator images do not "
            f"anticommute in {target}"
        )

    source = module.exterior_algebra()

    def evaluate(element):
        element = source(element)
        result = target.zero()
        for degree, component in element.homogeneous_components().items():
            piece = source.graded_piece(degree)
            coordinates = piece.framing_morphism().lift(component)
            for basis_label in coordinates.support().domain():
                coefficient = coordinates(basis_label)
                if degree == 0:
                    value = target.one()
                elif degree == 1:
                    value = images[basis_label]
                else:
                    value = target.one()
                    for generator_label in basis_label:
                        value *= images[generator_label]
                result += coefficient * value
        return result

    return _constructed_algebra_morphism(
        source,
        target,
        evaluate,
        linearity_premises=(module_morphism,),
        equations=square_equations + pair_equations,
    )


__all__ = [
    "PowerAlgebra",
    "PowerAlgebraElement",
    "PowerAlgebraMor",
    "PowerAlgebraMorphism",
]
