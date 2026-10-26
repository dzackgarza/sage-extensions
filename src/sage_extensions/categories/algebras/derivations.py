r"""Derivations of represented commutative algebras.

For an ``R``-algebra ``A`` and an ``A``-module ``M``, ``A.derivations(M)``
is the ``A``-module of ``R``-derivations ``A -> M``.  On the live finite
polynomial-presentation backend a derivation is specified on the chosen
algebra generators and evaluated by the formal chain rule on a selected
presentation representative.
"""

import operator
from collections.abc import Mapping

from sage.categories.map import Map
from sage.categories.action import Action
from sage.categories.morphism import Morphism, SetMorphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.element import ModuleElement, parent

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import (
    MorCategories,
    _RestrictedMorCategoryOf,
    RestrictedMorCategoryParent,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
)
from sage_extensions.categories.algebras.finitely_presented_algebras import AlgebrasWithChosenFinitePresentation
from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModuleSubobjectConstruction,
    ModuleSubobjects,
    ModulesWithChosenFinitePresentation,
    _fix_selected_module_resolution,
    _restricted_scalars_view,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _fix_selected_module_presentation,
    _relation_morphism,
)
from sage_extensions.categories.modules.framed.framed_free_modules import _fresh_free_module_on
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphism,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    _engine_element,
    _engine_ring,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family_from_values,
)
from sage_extensions.logic import AtomicProposition, Propositions, conjunction
from sage_extensions.validation import validator


def _commutative_presentation_data(algebra):
    r"""Return ``(P, labels, variables, relations, lift)`` for ``A = P/I``."""

    base = algebra.base_ring()
    if algebra not in Algebras(base).Associative().Unital().Commutative():
        raise TypeError(
            f"Kahler differentials are defined here for commutative algebras, but {algebra} is not known "
            "to be commutative"
        )
    assert (
        algebra in AlgebrasWithChosenFinitePresentation(base)
        or algebra in SymmetricAlgebras(base)
    ), (
        f"Kahler differentials of {algebra} are computed only for a polynomial algebra or an algebra "
        "given by finitely many generators and relations"
    )

    if algebra in AlgebrasWithChosenFinitePresentation(base):
        presentation = algebra.presentation_ring()
        relations = algebra.relations()
        lift = algebra.lift_to_presentation
    elif algebra in SymmetricAlgebras(base):
        presentation = algebra
        relations = finite_ordered_set(())
        lift = presentation

    assert presentation in SymmetricAlgebras(base), (
        f"the selected conormal and differential computation for {algebra} needs "
        f"a polynomial presentation; its retained presentation {presentation} "
        "needs a different differential computation"
    )
    labels = presentation.algebra_generating_set()
    assert labels.cardinality().is_finite() is True, (
        f"the selected conormal and differential computation for {algebra} requires "
        "a known finite family of polynomial generators"
    )
    variables = FiniteOrderedSets().from_indexed(
        labels,
        presentation.algebra_generator,
    )
    return presentation, labels, variables, relations, lift


def _differentiate_representative(algebra, representative, variables):
    presentation, _labels, _variables, _relations, _lift = _commutative_presentation_data(
        algebra
    )
    source = _engine_element(presentation, presentation(representative))
    target = _engine_ring(algebra)

    def derivative(variable):
        engine_variable = _engine_element(presentation, variable)
        return _owned_engine_element(algebra,
            target(source.derivative(engine_variable))
        )

    return tuple(derivative(variable) for variable in variables)


class Derivation(ModuleElement):
    r"""An ``R``-derivation ``D: A -> M`` into an ``A``-module ``M`` (Stacks, Tag 00RN).

    ``D`` is additive, kills the image of the structure morphism
    ``f: R -> A`` and satisfies ``D(ab) = a D(b) + b D(a)``; its values lie
    in ``M`` itself.  :meth:`underlying_linear_morphism` is ``D`` as an
    element of the ``R``-module ``Mor_R(A, Res_f(M))``, of which
    ``Der_R(A, M)`` is a submodule.
    """

    def __init__(self, parent, generator_images) -> None:
        ModuleElement.__init__(self, parent)
        labels = parent.generator_labels()
        # The generator images are a family indexed by the algebra
        # generators; reading a mapping, a family or positional data as that
        # family is the indexed-family owner's work.
        family = finite_indexed_family_from_values(labels, generator_images)
        images = {label: family.value(label) for label in labels}
        target = parent.target_module()
        self._generator_images = {
            label: target(image) if image.parent() is not target else image
            for label, image in images.items()
        }

    def domain(self):
        return self.parent().algebra()

    def codomain(self):
        return self.parent().target_module()

    def restricted_codomain(self):
        return self.parent().restricted_target_module()

    def generator_image(self, label):
        return self._generator_images[label]

    def _evaluate_coefficients(self, coefficients):
        target = self.parent().target_module()
        return sum(
            (
                target.scalar_multiple(coefficient, self._generator_images[label])
                for label, coefficient in zip(
                    self.parent().generator_labels(), coefficients, strict=True
                )
                if coefficient
            ),
            target.zero(),
        )

    @validator
    def validate_relations(self) -> None:
        r"""Raise ``ValueError`` unless the chain rule on the generator images sends every defining relation to zero (``OWN-22``).

        Generator images ``D(x_i) = m_i`` define a derivation of
        ``A = R[x]/(f_1, ..., f_k)`` exactly when
        ``sum_i (df_j/dx_i) m_i = 0`` for every relation ``f_j``.
        """
        algebra = self.domain()
        if algebra in LocalizationRings():
            source = algebra.localization_source()
            presentation, _labels, variables, relations, _lift = (
                _commutative_presentation_data(source)
            )
            localization_map = algebra.localization_map()
            for relation in relations:
                coefficients = _differentiate_representative(
                    source,
                    relation,
                    variables,
                )
                localized_coefficients = tuple(
                    localization_map(coefficient) for coefficient in coefficients
                )
                if (
                    self._evaluate_coefficients(localized_coefficients)
                    == self.codomain().zero()
                ) is False:
                    raise ValueError(
                        f"the generator images do not define a derivation of {self.domain()}: the localized "
                        "derivation rule does not send a defining relation to 0"
                    )
            return

        presentation, _labels, variables, relations, _lift = _commutative_presentation_data(
            algebra
        )
        for relation in relations:
            coefficients = _differentiate_representative(
                algebra,
                relation,
                variables,
            )
            if (
                self._evaluate_coefficients(coefficients) == self.codomain().zero()
            ) is False:
                raise ValueError(
                    f"the generator images do not define a derivation of {self.domain()}: a defining relation "
                    "is not sent to 0"
                )

    def __call__(self, element):
        return self._module_value(element)

    def _module_value(self, element):
        r"""The value ``D(a)`` in the target module ``M``."""
        algebra = self.domain()
        if algebra in LocalizationRings():
            source = algebra.localization_source()
            _presentation, _labels, variables, _relations, lift = (
                _commutative_presentation_data(source)
            )
            localization_map = algebra.localization_map()

            def differentiate_source(value):
                representative = lift(source(value))
                coefficients = _differentiate_representative(
                    source,
                    representative,
                    variables,
                )
                return self._evaluate_coefficients(
                    tuple(localization_map(coefficient) for coefficient in coefficients)
                )

            numerator, denominator = algebra.localization_fraction_data(algebra(element))
            numerator_derivative = differentiate_source(numerator)
            denominator_derivative = differentiate_source(denominator)
            numerator_image = localization_map(numerator)
            denominator_inverse = algebra.fraction(
                source.one(),
                denominator,
            )
            target = self.parent().target_module()
            first = target.scalar_multiple(
                denominator_inverse,
                numerator_derivative,
            )
            second = target.scalar_multiple(
                numerator_image * denominator_inverse * denominator_inverse,
                denominator_derivative,
            )
            return first + (-second)

        presentation, _labels, variables, _relations, lift = _commutative_presentation_data(
            algebra
        )
        representative = lift(algebra(element))
        coefficients = _differentiate_representative(
            algebra,
            representative,
            variables,
        )
        return self._evaluate_coefficients(coefficients)

    def _call_(self, element):
        return self.__call__(element)

    def _repr_(self):
        images = ", ".join(
            f"{label} |-> {self.generator_image(label)}"
            for label in self.parent().generator_labels()
        )
        return f"Derivation of {self.domain()} with {images}"

    def lie_bracket(self, other):
        r"""Return the Lie bracket of two vector fields on one algebra."""
        from sage_extensions.categories.algebras.cartan_calculus import (
            _lie_bracket,
        )

        return _lie_bracket(self, other)

    def interior_product(self):
        r"""Return contraction ``i_X`` on the algebraic de Rham complex."""
        from sage_extensions.categories.algebras.cartan_calculus import (
            _interior_product,
        )

        return _interior_product(self)

    def lie_derivative(self):
        r"""Return the Lie derivative ``L_X=[d,i_X]`` on de Rham forms."""
        from sage_extensions.categories.algebras.cartan_calculus import (
            _lie_derivative,
        )

        return _lie_derivative(self)

    @cached_method
    def underlying_linear_morphism(self):
        return DerivationUnderlyingLinearMorphism(
            self.parent().arrow_set(),
            self,
            lambda element: self.restricted_codomain()(self._module_value(element)),
        )

    as_morphism = underlying_linear_morphism

    @cached_method
    def linear_endomorphism(self):
        r"""A vector field ``X`` in ``Der_R(A) = Der_R(A, A^1)`` as an element of ``End_R(A)``.

        ``X`` is an element of ``Mor_R(A, Res_f(A^1))``; composing with the
        isomorphism ``Res_f(A^1) -> A``, ``a e_0 |-> a``, of ``R``-modules
        gives the ``R``-linear endomorphism of ``A`` that the Lie bracket
        ``[X, Y] = XY - YX`` and contraction ``i_X`` compose.
        """
        algebra = self.domain()
        assert self.codomain() is algebra.regular_module(), (
            f"{self} is a derivation into {self.codomain()}; only a derivation into the regular module "
            f"{algebra.regular_module()} of {algebra} is an endomorphism of {algebra}"
        )
        identification = self.restricted_codomain().regular_module_identification()
        return identification * self.underlying_linear_morphism()

    def _lmul_(self, scalar):
        return self.parent().algebra_multiple(scalar, self)

    _rmul_ = _lmul_

    def __add__(self, other):
        match other:
            case _ if parent(other) is self.parent():
                pass
            case _:
                return NotImplemented
        return self.parent()(
            {
                label: self.generator_image(label) + other.generator_image(label)
                for label in self.parent().generator_labels()
            }
        )

    def __neg__(self):
        return self.parent()(
            {
                label: -self.generator_image(label)
                for label in self.parent().generator_labels()
            }
        )

    def __sub__(self, other):
        return self + (-other)

    def _richcmp_(self, other, op):
        from sage.structure.richcmp import op_EQ, op_NE

        if op not in (op_EQ, op_NE):
            return NotImplemented
        match other:
            case _ if parent(other) is self.parent():
                pass
            case _:
                return op == op_NE
        equal = conjunction(
            self.generator_image(label) == other.generator_image(label)
            for label in self.parent().generator_labels()
        )
        return equal if op == op_EQ else negation(equal)


class DerivationUnderlyingLinearMorphism(ModuleMorphism):
    r"""The selected underlying linear morphism of one algebra derivation."""

    def __init__(self, parent, derivation, function) -> None:
        self._derivation = derivation
        super().__init__(parent, function, elementwise=True)

    def derivation(self):
        return self._derivation

    def _elementwise_linearity_derivation(self):
        return True

    def __rmul__(self, scalar):
        return self.parent().algebra_multiple(scalar, self)

    def _acted_upon_(self, actor, self_on_left):
        try:
            return self.parent().algebra_multiple(actor, self)
        except (TypeError, ValueError):
            return None

    def _repr_(self):
        return f"Derivation {self.domain()} -> {self.codomain()}"


class _DerivationAlgebraAction(Action):
    def __init__(self, algebra, derivations, is_left) -> None:
        self._derivations = derivations
        Action.__init__(self, _engine_ring(algebra), derivations, is_left, operator.mul)

    def _act_(self, scalar, derivation):
        return self._derivations.algebra_multiple(scalar, derivation)


class DerivationSpace(RestrictedMorCategoryParent):
    r"""The ``A``-module ``Der_R(A, M)`` of ``R``-derivations into an ``A``-module ``M``.

    For ``f: R -> A`` the structure morphism, an ``R``-derivation
    ``D: A -> M`` is an ``R``-linear map ``A -> Res_f(M)`` with
    ``D(ab) = a D(b) + b D(a)`` (Stacks, Tag 00RN).  So ``Res_f Der_R(A, M)``
    is the ``R``-submodule of ``Mor_R(A, Res_f(M))`` cut out by the Leibniz
    rule, and ``(a D)(b) = a D(b)`` makes ``Der_R(A, M)`` an ``A``-module.
    The two scalar structures stay distinct: the inclusion into the
    ``R``-linear Mor is only ``R``-linear.  ``Der_R(A) = Der_R(A, A^1)``
    takes values in the regular module ``A^1``.
    """

    Element = Derivation

    # The constructor fixes the presentation transported from the Kahler
    # classifier; the presented-modules slot starts empty, as on ``OwnedMor``.
    _selected_module_presentation = None

    @staticmethod
    def __classcall__(cls, family, algebra, restricted_target):
        r"""``Der_R(A,M)`` is an ``A``-module, with the presentation of ``Mor_A(Omega_{A/R}, M)`` when that has one."""
        target_module = restricted_target.module_over_extension()
        differentials = algebra.kahler_differentials()
        classifiers = differentials.module_category().Mor(differentials, target_module)
        match classifiers:
            case _ if classifiers in ModulesWithChosenFinitePresentation(algebra):
                category = ModulesWithChosenFinitePresentation(algebra)
            case _:
                category = Modules(algebra)
        return RestrictedMorCategoryParent.__classcall__(
            cls, family, algebra, restricted_target, category=category, base_ring=algebra
        )

    def __init__(self, family, domain, codomain, *, category, base=None) -> None:
        algebra, restricted_target = domain, codomain
        target_module = restricted_target.module_over_extension()
        if target_module.base_ring() is not algebra:
            raise TypeError(
                f"an R-derivation A -> M needs M to be a module over A = {algebra}, but {target_module} is a "
                f"module over {target_module.base_ring()}"
            )
        self._algebra = algebra
        self._target_module = target_module
        presentation_algebra = (
            algebra.localization_source()
            if algebra in LocalizationRings()
            else algebra
        )
        _presentation, labels, _variables, _relations, _lift = _commutative_presentation_data(
            presentation_algebra
        )
        self._generator_labels = labels

        structure_map = algebra.algebra_structure_morphism()
        self._restricted_target = restricted_target
        differentials = algebra.kahler_differentials()
        classifiers = differentials.module_category().Mor(differentials, target_module)
        self._preamble_kahler_classifier_module = classifiers
        # Der_R(A,M) is the subcategory of Mor_R(A,Res_f M) carved out by the
        # Leibniz rule, so the existing R-linear Mor category is the base.
        RestrictedMorCategoryParent.__init__(
            self,
            family,
            algebra,
            restricted_target,
            category=category,
            base=base,
        )
        if classifiers in ModulesWithChosenFinitePresentation(algebra):
            framing_labels = classifiers.module_generating_set()
            # The classifier relations, transported label for label onto
            # free modules that frame Der_R(A, M) itself.
            classifier_relations = _relation_morphism(classifiers)
            relation_source = _fresh_free_module_on(
                algebra, classifier_relations.domain().module_generating_set()
            )
            relation_target = _fresh_free_module_on(algebra, framing_labels)

            def transported_relation(relation_label):
                image = classifier_relations(
                    classifier_relations.domain().module_generator(relation_label)
                ).to_vector()
                return relation_target.linear_combination(
                    {label: image(label) for label in image.support().domain()}
                )

            presentation = relation_source.module_category().Mor(relation_source, relation_target)(
                transported_relation
            )
            _fix_selected_module_resolution(
                self,
                algebra,
                framing_labels,
                lambda label: self._from_kahler_classifier(
                    classifiers.module_generator(label)
                ),
                presentation.codomain,
            )
            _fix_selected_module_presentation(
                self,
                algebra,
                presentation,
            )
        self.register_action(_DerivationAlgebraAction(algebra, self, True))
        self.register_action(_DerivationAlgebraAction(algebra, self, False))

        def restricted_inclusion(restricted_module):
            return restricted_module.Mono(self.arrow_set())._subobject_inclusion(
                lambda restricted_derivation: (
                    restricted_derivation.underlying_element().underlying_linear_morphism()
                ),
            )

        self._restricted_module = _restricted_scalars_view(
            self,
            structure_map,
            _subobject_inclusion_factory=restricted_inclusion,
        )

    def algebra(self):
        return self._algebra

    def target_module(self):
        return self._target_module

    def restricted_target_module(self):
        return self._restricted_target

    def restricted_module(self):
        return self._restricted_module

    def inclusion(self):
        return self.restricted_module().inclusion()

    def generator_labels(self):
        return self._generator_labels

    def _kahler_classifier_module(self):
        return self._preamble_kahler_classifier_module

    def _from_kahler_classifier(self, classifier):
        classifiers = self._kahler_classifier_module()
        classifier = classifiers(classifier)
        differentials = classifiers.domain()
        return self(
            {
                label: classifier(differentials.differential_generator(label))
                for label in self.generator_labels()
            }
        )

    def _to_kahler_classifier(self, derivation):
        derivation = self(derivation)
        return self._kahler_classifier_module().domain().from_derivation(derivation)

    def _selected_module_coefficients(self, derivation):
        classifiers = self._kahler_classifier_module()
        coordinates = classifiers.framing_morphism().lift(self._to_kahler_classifier(derivation))
        return {label: coordinates(label) for label in coordinates.support().domain()}

    def __call__(self, generator_images, *, check=False):
        r"""Construct a derivation from its generator images, not an arrow object."""
        return self._element_constructor_(generator_images, check=check)

    def _element_constructor_(self, generator_images, *, check=False):
        r"""Construct the derivation; ``check=True`` runs its validator (``OWN-22``)."""
        match generator_images:
            case _ if parent(generator_images) is self:
                generator_images.validate_relations(check=check)
                return generator_images
            case _ if generator_images in self.arrow_set() and self.accepts(generator_images):
                selected = generator_images.derivation()
                if selected.parent() is self:
                    selected.validate_relations(check=check)
                    return selected
                raise TypeError(f"{generator_images} belongs to another derivation space; apply the mathematical transport")
            case _ if generator_images in self.arrow_set():
                raise ValueError(
                    f"{generator_images} is only a linear map; a derivation must also satisfy the Leibniz rule "
                    "D(ab) = a D(b) + D(a) b"
                )
            case _ if parent(generator_images) in MorCategories():
                raise ValueError(
                    f"cannot view {generator_images} as a derivation {self.algebra()} -> "
                    f"{self.restricted_target_module()}: it is a map {generator_images.domain()} -> "
                    f"{generator_images.codomain()}"
                )
            case Map():
                raise TypeError(f"{generator_images} is an arrow of another Mor; give the derivation generator images")
            case _:
                pass
        match generator_images:
            case Mapping():
                labels = self.generator_labels()
                normalized = {}
                for key, image in generator_images.items():
                    if key in labels:
                        label = key
                    else:
                        matching = tuple(
                            label for label in labels
                            if self.algebra().algebra_generator(label) == key
                        )
                        if len(matching) != 1:
                            raise ValueError(
                                f"{key} does not select one algebra generator of {self.algebra()}"
                            )
                        label = matching[0]
                    if label in normalized:
                        raise ValueError(f"the image of the algebra generator {label} is given twice")
                    normalized[label] = image
                generator_images = normalized
            case _:
                pass
        derivation = Derivation(self, generator_images)
        derivation.validate_relations(check=check)
        return derivation

    def zero(self):
        return self({label: self.target_module().zero() for label in self.generator_labels()})

    def _an_element_(self):
        r"""A module generator of ``Der_R(A,M)`` from its chosen presentation, else ``0``.

        For ``A = R[x]`` and ``M = A`` the generator is ``d/dx``, since
        ``Der_R(R[x], R[x]) = R[x] d/dx`` is free of rank one.
        """
        match self:
            case _ if self in ModulesWithChosenFinitePresentation(self.algebra()):
                return self.module_generator(next(iter(self.module_generating_set())))
            case _:
                return self.zero()

    def algebra_multiple(self, scalar, derivation):
        if derivation.parent() is not self:
            derivation = self(derivation)
        scalar = self.algebra()(scalar)
        target = self.target_module()
        return self(
            {
                label: target.scalar_multiple(scalar, target(derivation.generator_image(label)))
                for label in self.generator_labels()
            }
        )

    def scalar_multiple(self, scalar, derivation):
        return self.algebra_multiple(scalar, derivation)

    def algebra_action(self):

        endomorphisms = Modules(self.algebra()).End(self)
        return SetMorphism(
            self.algebra().Mor(endomorphisms),
            lambda scalar: endomorphisms.elementwise(
                lambda derivation: self.algebra_multiple(scalar, derivation)
            ),
        )

    scalar_action = algebra_action

    def _repr_(self):
        algebra = self.algebra()
        match self.target_module():
            case target if target is algebra.regular_module():
                # Der_R(A) = Der_R(A, A): the values lie in A itself.
                return f"Der_{algebra.base_ring()}({algebra})"
            case target:
                return f"Der_{algebra.base_ring()}({algebra}, {target})"


class DerivationCategoryConstruction(_RestrictedMorCategoryOf):
    _declaration_name = "_DerivationCategory"

    def fixed_category_class(self):
        return DerivationSpace

    def accepts(self, arrow) -> bool:
        return self._accepts_by_placement(arrow)


@cached_function(key=lambda algebra, target_module: (id(algebra), id(target_module)))
def _derivations(algebra, target_module) -> DerivationSpace:
    if target_module.base_ring() is not algebra:
        raise TypeError(
            f"an R-derivation A -> M needs M to be a module over A = {algebra}, but {target_module} is a "
            f"module over {target_module.base_ring()}"
        )
    base = algebra.base_ring()
    restricted_target = target_module.restrict_scalars(
        algebra.algebra_structure_morphism()
    )
    return DerivationCategoryConstruction(Modules(base)).Of(
        algebra,
        restricted_target,
    )


class GradedDerivation(ModuleElement):
    r"""A homogeneous graded derivation of a represented graded algebra.

    For shift ``r`` this represents a map ``D : A^p -> M^(p+r)`` satisfying
    ``D(ab) = D(a)b + (-1)^(r p) a D(b)`` on homogeneous ``a``.  It is an
    actual ``R``-linear morphism, lying in a represented submodule of
    ``Mor_R(A,M)``.
    """

    def __init__(self, parent, function) -> None:
        if not callable(function):
            raise TypeError(
                f"a graded derivation of {parent.algebra()} needs a map on elements, but {function!r} is not callable"
            )
        ModuleElement.__init__(self, parent)
        self._function = function

    def _graded_derivation_derivation(self):
        r"""Return the decision a construction supplies, or ``None`` for a map given as a function on elements."""
        return None

    @cached_method
    def _graded_derivation_decision(self):
        r"""Return the decision on linearity, degree preservation and the graded Leibniz rule.

        For a map given as a function on elements the decision is the
        proposition ``is_graded_derivation(D)``; for a map that a construction
        produced it is the decision that construction supplies, ``True`` or a
        proposition.  Read on the first request, not at construction
        (``OWN-22``).
        """
        derived = self._graded_derivation_derivation()
        match derived:
            case None:
                return AtomicProposition("is_graded_derivation", self)
            case decision if decision is True or decision in Propositions:
                return decision
            case _:
                raise ValueError(
                    f"a graded derivation is recorded only when its defining laws are True or a proposition, but got {derived}"
                )

    def linearity_decision(self):
        r"""``True`` when the derivation laws are decided, else the proposition ``is_linear(D)``."""
        return True if self._graded_derivation_decision() is True else AtomicProposition("is_linear", self)

    def degree_preservation_decision(self):
        r"""``True`` when the derivation laws are decided, else the proposition ``preserves_degree(D)``."""
        return True if self._graded_derivation_decision() is True else AtomicProposition("preserves_degree", self)

    def graded_leibniz_decision(self):
        r"""``True`` when the derivation laws are decided, else the proposition ``satisfies_graded_leibniz_rule(D)``."""
        return (
            True
            if self._graded_derivation_decision() is True
            else AtomicProposition("satisfies_graded_leibniz_rule", self)
        )

    @validator
    def validate_graded_leibniz(self) -> None:
        r"""Raise ``ValueError`` when the finite generator check refutes degree or graded Leibniz (``OWN-22``)."""
        if self.check_on_generators() is False:
            raise ValueError(
                f"{self._function} is not a graded derivation of degree {self.degree_shift()}: it fails the graded "
                "Leibniz rule on a generator"
            )

    def __call__(self, element):
        return self.target()(self._function(self.algebra()(element)))

    def _call_(self, element):
        return self.__call__(element)

    def algebra(self):
        return self.parent().algebra()

    def target(self):
        return self.parent().target()

    def degree_shift(self):
        return self.parent().degree_shift()

    def _repr_(self):
        return f"Degree {self.degree_shift()} graded derivation of {self.algebra()}"

    def graded_commutator(self, other):
        r"""Return the graded commutator with another endo-derivation."""
        from sage_extensions.categories.algebras.cartan_calculus import (
            _graded_commutator,
        )

        return _graded_commutator(self, other)

    @cached_method
    def underlying_linear_morphism(self):
        return GradedDerivationUnderlyingLinearMorphism(
            self.parent().arrow_set(),
            self,
            lambda element: self(element),
        )

    as_morphism = underlying_linear_morphism

    def __add__(self, other):
        match other:
            case _ if parent(other) is self.parent():
                pass
            case _:
                return NotImplemented
        return self.parent()._from_derived_elementwise(
            lambda element: self(element) + other(element),
            self,
            other,
        )

    def __neg__(self):
        return self.parent()._from_derived_elementwise(
            lambda element: -self(element),
            self,
        )

    def __sub__(self, other):
        return self + (-other)

    def _lmul_(self, scalar):
        return self.parent().scalar_multiple_of(scalar, self)

    _rmul_ = _lmul_

    def __rmul__(self, scalar):
        return self.parent().scalar_multiple_of(scalar, self)

    def check_on_generators(self):
        r"""Refute degree/Leibniz on finite selected generators when decidable.

        Passing this finite observation does not prove that an arbitrary
        element map is linear or satisfies Leibniz on all elements; those laws
        remain propositions unless the construction supplies their theorem.
        Where the generator data do not decide the check, the answer is the
        proposition ``check_on_generators(D)``.
        """
        algebra = self.algebra()
        target = self.target()
        undecided = AtomicProposition("check_on_generators", self)
        if not algebra.is_framed_algebra():
            return undecided
        labels = algebra.algebra_generating_set()
        finite = labels.cardinality().is_finite()
        match finite:
            case True:
                pass
            case False:
                return undecided
        for label in labels:
            generator = algebra.algebra_generator(label)
            is_zero = generator == algebra.zero()
            match is_zero:
                case True:
                    continue
                case False:
                    pass
                case _:
                    return undecided
            if not generator.is_homogeneous():
                return undecided
            generator_degree = algebra.homogeneous_degree(generator)
            image = self(generator)
            image_is_zero = image == target.zero()
            match image_is_zero:
                case True:
                    continue
                case False:
                    pass
                case _:
                    return undecided
            if not image.is_homogeneous():
                return False
            image_degree = target.homogeneous_degree(image)
            match image_degree == generator_degree + self.degree_shift():
                case True:
                    pass
                case False:
                    return False
                case _:
                    return undecided
        for left_label in labels:
            left = algebra.algebra_generator(left_label)
            left_is_zero = left == algebra.zero()
            match left_is_zero:
                case True:
                    continue
                case False:
                    pass
                case _:
                    return undecided
            if not left.is_homogeneous():
                return undecided
            left_degree = algebra.homogeneous_degree(left)
            for right_label in labels:
                right = algebra.algebra_generator(right_label)
                signed_second = left * self(right)
                if (self.degree_shift() * left_degree) % 2:
                    signed_second = -signed_second
                match self(left * right) == self(left) * right + signed_second:
                    case True:
                        pass
                    case False:
                        return False
                    case _:
                        return undecided
        return True


def _combined_graded_derivation_decision(derivations):
    r"""Transfer the graded-derivation theorem through an operation on actual derivations."""
    return conjunction(
        decision
        for derivation in derivations
        for decision in (
            derivation.linearity_decision(),
            derivation.degree_preservation_decision(),
            derivation.graded_leibniz_decision(),
        )
    )


class _DerivedGradedDerivation(GradedDerivation):
    r"""A graded derivation whose decision is the conjunction of its operands' decisions."""

    def __init__(self, parent, function, operand_decision) -> None:
        self._operand_graded_derivation_decision = operand_decision
        super().__init__(parent, function)

    def _graded_derivation_derivation(self):
        return self._operand_graded_derivation_decision


class _ConstructedGradedDerivation(GradedDerivation):
    r"""A graded derivation whose defining construction proves its laws."""

    def _graded_derivation_derivation(self):
        return True


class GradedDerivationUnderlyingLinearMorphism(ModuleMorphism):
    r"""The selected underlying linear morphism of one graded derivation."""

    def __init__(self, parent, derivation, function) -> None:
        self._derivation = derivation
        super().__init__(
            parent,
            function,
            elementwise=True,
        )

    def _elementwise_linearity_derivation(self):
        return self.derivation().linearity_decision()

    def derivation(self):
        return self._derivation

    def degree_shift(self):
        return self.derivation().degree_shift()


def _contraction_presentation(algebra, shift):
    r"""The relations of ``Der_R(A)`` when ``algebra`` is ``Omega^*_{A/R}`` and ``shift`` is ``-1``, else ``None``.

    Then ``X |-> i_X`` is an isomorphism ``Der_R(A) -> Der^(-1)(Omega^*_{A/R})``
    (``GradedDerivationSpace``), so the contractions carry the presentation
    of the vector fields.
    """
    from sage_extensions.categories.algebras.de_rham_algebras import DeRhamAlgebras

    match shift:
        case -1 if algebra in DeRhamAlgebras(algebra.base_ring()):
            vector_fields = algebra.de_rham_source_algebra().vector_fields()
        case _:
            return None
    match vector_fields:
        case _ if vector_fields in ModulesWithChosenFinitePresentation(vector_fields.base_ring()):
            return vector_fields.presentation()
        case _:
            return None


class GradedDerivationSpace(RestrictedMorCategoryParent):
    r"""The module ``Der^r(B, M)`` of degree-``r`` graded derivations, a subset of ``Mor_R(B, M)``.

    For a strictly commutative DGA ``B`` and ``M = B`` it is a module over
    ``B^0``: an element ``a`` of ``B^0`` is even, hence central, so
    ``(a theta)(bc) = (a theta)(b) c + (-1)^(rp) b (a theta)(c)``.  Its
    inclusion into ``Mor_R(B, B)`` is then only ``R``-linear, and is the
    inclusion of its restriction of scalars along ``R -> B^0``.  Otherwise it
    is the ``R``-submodule of ``Mor_R(B, M)``.

    For the de Rham algebra ``B = Omega^*_{A/R}`` and ``r = -1``, ``theta``
    vanishes on ``A`` and so is ``A``-linear on ``Omega^1 = Omega_{A/R}``;
    since ``Omega^1`` generates ``B`` over ``A``, ``theta`` is fixed by that
    map, and every ``A``-linear map ``Omega^1 -> A`` extends.  So
    ``X |-> i_X`` is an isomorphism ``Der_R(A) -> Der^(-1)(B)``, and the
    space has the presentation of ``Der_R(A)``.
    """

    Element = GradedDerivation

    # Fixed by the constructor for the contractions of a de Rham algebra;
    # the presented-modules slot starts empty, as on ``DerivationSpace``.
    _selected_module_presentation = None

    @staticmethod
    def __classcall__(cls, family, algebra, target):
        from sage_extensions.categories.algebras.differential_graded_algebras import (
            DifferentialGradedAlgebras,
        )

        ring = algebra.base_ring()
        degree_zero = DifferentialGradedAlgebras(ring).degree_zero_algebra()
        match target:
            case _ if target is algebra and algebra in degree_zero.domain():
                scalars = degree_zero(algebra)
                match _contraction_presentation(algebra, family.degree_shift()):
                    case None:
                        category = Modules(scalars)
                    case _:
                        category = ModulesWithChosenFinitePresentation(scalars)
                return RestrictedMorCategoryParent.__classcall__(
                    cls, family, algebra, target, category=category, base_ring=scalars
                )
            case _:
                return RestrictedMorCategoryParent.__classcall__(
                    cls,
                    family,
                    algebra,
                    target,
                    category=Cat().meet((Modules(ring), ModuleSubobjects(ring))),
                    base_ring=ring,
                    subobject_inclusion_factory=lambda space: space.Mono(space.arrow_set())._subobject_inclusion(
                        lambda derivation: derivation.underlying_linear_morphism(),
                    ),
                )

    def __init__(self, family, domain, codomain, *, category, base=None) -> None:
        algebra, target = domain, codomain
        if algebra.base_ring() is not target.base_ring():
            raise ValueError(
                f"graded derivations {algebra} -> {target} need one coefficient ring, but they are over "
                f"{algebra.base_ring()} and {target.base_ring()}"
            )
        self._algebra = algebra
        self._target = target
        self._shift = family.degree_shift()
        RestrictedMorCategoryParent.__init__(
            self,
            family,
            algebra,
            target,
            category=category,
            base=base,
        )
        presentation = _contraction_presentation(algebra, self._shift)
        match presentation:
            case None:
                pass
            case _ if target is algebra:
                vector_fields = algebra.de_rham_source_algebra().vector_fields()
                _fix_selected_module_resolution(
                    self,
                    self.base_ring(),
                    presentation.codomain().module_generating_set(),
                    lambda label: vector_fields.module_generator(label).interior_product(),
                    presentation.codomain,
                )
                _fix_selected_module_presentation(self, self.base_ring(), presentation)

    @cached_method
    def restricted_module(self):
        r"""``Res_R Der^r(B)`` along ``R -> B^0``, the ``R``-submodule of ``Mor_R(B, B)``."""
        scalars = self.base_ring()
        return _restricted_scalars_view(
            self,
            scalars.algebra_structure_morphism(),
            _subobject_inclusion_factory=lambda restricted: restricted.Mono(self.arrow_set())._subobject_inclusion(
                lambda derivation: derivation.underlying_element().underlying_linear_morphism(),
            ),
        )

    def algebra(self):
        return self._algebra

    def target(self):
        return self._target

    def degree_shift(self):
        return self._shift

    def __call__(self, function, *, check=False):
        r"""Construct a graded derivation, not an arrow object."""
        return self._element_constructor_(function, check=check)

    def _element_constructor_(self, function, *, check=False):
        r"""Construct the graded derivation; ``check=True`` runs its validator (``OWN-22``)."""
        match function:
            case _ if parent(function) is self:
                function.validate_graded_leibniz(check=check)
                return function
            case _ if function in self.arrow_set() and self.accepts(function):
                derivation = function.derivation()
                if derivation.parent() is self:
                    derivation.validate_graded_leibniz(check=check)
                    return derivation
                raise TypeError(f"{function} belongs to another graded derivation space; apply the mathematical transport")
            case _ if function in self.arrow_set():
                raise ValueError(
                    f"{function} is only a linear map; a graded derivation of degree {self.degree_shift()} must "
                    "also satisfy the graded Leibniz rule"
                )
            case _ if parent(function) in MorCategories():
                raise ValueError(
                    f"cannot view {function} as a graded derivation {self.algebra()} -> {self.target()}: it is a "
                    f"map {function.domain()} -> {function.codomain()}"
                )
            case Map():
                raise TypeError(f"{function} is an arrow of another Mor; give the graded derivation defining function")
            case _ if callable(function):
                return self.elementwise(function, check=check)
            case _:
                return self.from_algebra_generator_images(function, check=check)

    def from_algebra_generator_images(self, generator_images, *, check=False):
        r"""The map ``D`` with ``D(x_i) = m_i`` on the algebra generators, extended by the Leibniz rule.

        The extension is the derivation of ``Der_R(A, M)`` with these
        generator images.  It is a graded derivation of degree ``r`` when the
        images have degree ``|x_i| + r`` and the signs ``(-1)^(r |x_i|)`` of
        the graded Leibniz rule are ``1``; that law stays the proposition
        ``is_graded_derivation(D)``, which ``check_on_generators`` decides on
        the generators.
        """
        algebra = self.algebra()
        match self.target():
            case target if target is algebra:
                derivation = algebra.vector_fields()(generator_images)
            case target:
                derivation = algebra.derivations(target)(generator_images)
        return self.elementwise(lambda element: derivation(element), check=check)

    def zero(self):
        return self._from_constructed_elementwise(
            lambda _element: self.target().zero()
        )

    def _an_element_(self):
        r"""A module generator from the chosen presentation, else ``0``.

        For degree ``-1`` on ``Omega^*_{A/R}`` with ``A = R[x]`` it is the
        contraction ``i_{d/dx}``, which sends ``dx`` to ``1``.
        """
        match self:
            case _ if self in ModulesWithChosenFinitePresentation(self.base_ring()):
                return self.module_generator(next(iter(self.module_generating_set())))
            case _:
                return self.zero()

    def elementwise(self, function, *, check=False):
        r"""Construct the graded derivation given on elements; ``check=True`` runs its validator (``OWN-22``)."""
        if isinstance(function, Map):
            return self(function, check=check)
        if not callable(function):
            raise TypeError(
                f"a graded derivation of {self.algebra()} needs a map on elements, but {function!r} is not callable"
            )
        derivation = GradedDerivation(self, function)
        derivation.validate_graded_leibniz(check=check)
        return derivation

    def _from_constructed_elementwise(self, function):
        r"""Construct from a formula whose owner proves linearity, degree and Leibniz."""
        derivation = _ConstructedGradedDerivation(self, function)
        derivation.validate_graded_leibniz(check=False)
        return derivation

    def _from_derived_elementwise(self, function, *derivations):
        r"""Construct by a theorem-preserving operation on represented derivations."""
        derivation = _DerivedGradedDerivation(
            self,
            function,
            _combined_graded_derivation_decision(derivations),
        )
        derivation.validate_graded_leibniz(check=False)
        return derivation

    def scalar_multiple_of(self, scalar, derivation):
        r"""Return ``a theta``, ``(a theta)(b) = a theta(b)``, for ``a`` in the scalars of this module."""
        if derivation.parent() is not self:
            derivation = self(derivation)
        scalar = self.base_ring()(scalar)
        target = self.target()
        match self.base_ring() is self.algebra().base_ring():
            case True:
                return self._from_derived_elementwise(
                    lambda element: target.scalar_multiple(scalar, derivation(element)),
                    derivation,
                )
            case False:
                # (a theta)(b) = a theta(b), with a in B^0 included into B.
                included = self._degree_zero_inclusion()(scalar)
                return self._from_derived_elementwise(
                    lambda element: included * derivation(element),
                    derivation,
                )

    @cached_method
    def _degree_zero_inclusion(self):
        r"""The inclusion ``B^0 -> B`` of the scalars of this ``B^0``-module."""
        from sage_extensions.categories.algebras.differential_graded_algebras import (
            DifferentialGradedAlgebras,
        )

        return DifferentialGradedAlgebras(self.algebra().base_ring()).degree_zero_algebra().inclusion(self.algebra())

    def _repr_(self):
        return (
            f"Degree {self.degree_shift()} graded derivations "
            f"{self.algebra()} -> {self.target()}"
        )


class GradedDerivationCategoryConstruction(_RestrictedMorCategoryOf):
    _declaration_name = "_GradedDerivationCategory"

    @staticmethod
    def __classcall__(cls, base_category, shift):
        return typecall(cls, base_category, int(shift))

    def __init__(self, base_category, shift) -> None:
        self._degree_shift = int(shift)
        super().__init__(base_category)

    def degree_shift(self):
        return self._degree_shift

    def fixed_category_class(self):
        return GradedDerivationSpace

    def accepts(self, arrow) -> bool:
        return self._accepts_by_placement(arrow)


@cached_function(key=lambda algebra, target=None, shift=0: (id(algebra), id(algebra if target is None else target), int(shift)))
def _graded_derivations(algebra, target=None, shift=0) -> GradedDerivationSpace:
    if target is None:
        target = algebra
    ring = algebra.base_ring()
    if target not in Modules(ring):
        raise TypeError("a graded derivation target must be a module over the algebra's coefficient ring")
    graded_modules = algebra._graded_module_placement()
    if target not in graded_modules:
        raise TypeError(
            "a graded derivation target must carry the same declared grading as its algebra"
        )
    return GradedDerivationCategoryConstruction(Modules(ring), shift).Of(
        algebra,
        target,
    )


__all__ = [
    "Derivation",
    "DerivationSpace",
    "GradedDerivation",
    "GradedDerivationSpace",
]
