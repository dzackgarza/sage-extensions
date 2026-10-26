r"""Differential graded algebra categories and their morphisms."""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    _algebra_on_module,
    _root_algebra_law_decisions,
)
from sage_extensions.categories.algebras.derivations import GradedDerivation
from sage_extensions.categories.algebras.graded_algebras import (
    GradedAlgebraMorphism,
    GradedAlgebras,
)
from sage_extensions.categories.modules.cochain_complexes import CochainComplexes
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.logic import AtomicProposition, Propositions
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def DegreewiseLinearMorphism(domain, codomain, function):
    r"""Construct a degreewise map as an element of its actual module Mor."""
    if domain.base_ring() is not codomain.base_ring():
        raise ValueError(
            f"a component {domain} -> {codomain} of a differential needs both pieces over one base ring, but "
            f"they are over {domain.base_ring()} and {codomain.base_ring()}"
        )
    parent = domain.module_category().Mor(domain, codomain)
    morphism = parent.element_class(parent, function, elementwise=True, linearity_premises=())
    morphism._elementwise_linearity_witness = True
    return morphism


DifferentialComponentMorphism = DegreewiseLinearMorphism


class DifferentialGradedAlgebras(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""That de Rham algebra, whose differential makes it a DGA."""
        from sage_extensions.categories.algebras.de_rham_algebras import DeRhamAlgebras

        ring = self.base_ring()
        return DeRhamAlgebras(ring).an_object()

    def _call_(self, algebra, differential):
        r"""Equip one exact graded algebra with one selected differential.

        The graded algebra is retained as defining data.  A caller-supplied
        function supplies no decision of its graded-Leibniz or square-zero
        law, so each law is the proposition that states it; construction-derived differentials use
        :meth:`_from_constructed_differential` instead of turning generator
        observations into proofs.
        """
        graded = GradedAlgebras(self.base_ring())
        if algebra not in graded:
            raise TypeError(
                f"a differential graded algebra over {self.base_ring()} is built on a graded algebra over "
                f"{self.base_ring()}, but {algebra} is not one"
            )
        if isinstance(differential, Differential):
            if differential.algebra() is not algebra:
                raise ValueError(
                    f"the differential {differential} is a differential on {differential.algebra()}, not on {algebra}"
                )
            function = differential
            decisions = (
                differential.graded_leibniz_decision(),
                differential.square_zero_decision(),
            )
        elif callable(differential):
            function = differential
            decisions = (None, None)
        else:
            raise TypeError(
                f"a differential on {algebra} is a map of degree one on elements, but got {differential!r}"
            )
        return self._from_differential_data(algebra, function, decisions)

    def _from_constructed_differential(self, algebra, differential):
        r"""Construct when the supplying owner proves Leibniz and square-zero."""
        if not callable(differential):
            raise TypeError(
                f"a differential on {algebra} needs a map on elements, but {differential!r} is not callable"
            )
        return self._from_differential_data(algebra, differential, (True, True))

    def _from_differential_data(self, algebra, differential, decisions):
        graded = GradedAlgebras(self.base_ring())
        if algebra not in graded:
            raise TypeError(
                f"a differential graded algebra over {self.base_ring()} is built on a graded algebra over "
                f"{self.base_ring()}, but {algebra} is not one"
            )
        leibniz, square_zero = decisions
        if not _is_recorded_law_decision(leibniz) or not _is_recorded_law_decision(square_zero):
            raise ValueError(
                f"the Leibniz rule and d^2 = 0 are recorded only as True, a proposition or None, but got "
                f"{leibniz} and {square_zero}"
            )
        placements = [self]
        ring = self.base_ring()
        supercommutative = algebra in graded.Supercommutative()
        if (
            not supercommutative
            and algebra in graded.Commutative()
            and (-ring.one() == ring.one()) is True
        ):
            # In characteristic two the Koszul sign is always +1, so ordinary
            # graded commutativity implies the supercommutative sign rule.
            supercommutative = True
        if supercommutative:
            placements.append(self.Supercommutative())
        if algebra in graded.Supercommutative().Alternating():
            placements.append(self.Supercommutative().Alternating())
        law_decisions = _root_algebra_law_decisions(algebra)
        law_decisions["grading"] = algebra.grading_compatibility_decision()
        return _algebra_on_module(
            algebra,
            algebra.multiplication_morphism(),
            placement=tuple(placements),
            unit=algebra.one(),
            construction_data={
                "dga_underlying_algebra": algebra,
                "dga_differential_function": differential,
                "dga_differential_decisions": (leibniz, square_zero),
            },
            law_decisions=law_decisions,
        )

    def _repr_object_names(self):
        return f"differential graded algebras over {self.base_ring()}"

    def super_categories(self):

        return [GradedAlgebras(self.base_ring()), CochainComplexes(self.base_ring())]

    _MorCategory = None

    def degree_zero_algebra(self):
        r"""Return the functor taking a DGA to its degree-zero algebra."""
        from sage_extensions.categories.functors.de_rham import (
            _degree_zero_dga_functor,
        )

        return _degree_zero_dga_functor(self.base_ring())

    def cohomology_algebra(self):
        r"""Return the graded cohomology-algebra functor ``H^*`` on this category."""
        from sage_extensions.categories.functors.cohomology import (
            _cohomology_algebra_functor,
        )

        return _cohomology_algebra_functor(self.base_ring())

    class ParentMethods:
        def __init__(
            self,
            dga_underlying_algebra=None,
            dga_differential_function=None,
            dga_differential_decisions=None,
            **rest,
        ) -> None:
            self._preamble_dga_underlying_algebra = (
                self if dga_underlying_algebra is None else dga_underlying_algebra
            )
            self._preamble_differential = None
            super().__init__(**rest)
            if dga_differential_function is not None:
                decisions = (
                    (None, None)
                    if dga_differential_decisions is None
                    else tuple(dga_differential_decisions)
                )
                _fix_selected_differential(
                    self,
                    dga_differential_function,
                    graded_leibniz=decisions[0],
                    square_zero=decisions[1],
                )

        def underlying_graded_algebra(self):
            r"""Return the exact graded algebra equipped with this differential."""
            return self._preamble_dga_underlying_algebra

        def cohomology_algebra(self):
            r"""Return the represented graded cohomology algebra ``H^*(self)``."""
            from sage_extensions.categories.algebras.cohomology_algebras import (
                CohomologyAlgebras,
            )

            return CohomologyAlgebras(self.base_ring())(self)

        def degree_index_set(self):
            r"""Return the grading object as the inherited cochain degree set."""
            return self.grading_monoid()

        def graded_algebra(self):
            return self

        def dga(self):
            return self

        @cached_method
        def regular_dg_module(self):
            r"""Return the canonical right DG-module built on this DGA's module datum."""
            from sage_extensions.categories.modules.dg_modules import (
                DifferentialGradedModules,
            )

            dga = self
            source = self.unformed_module()

            def right_action(module_element, algebra_element):
                module = module_element.parent()
                return module(dga(module_element) * dga(algebra_element))

            return source._module_with_structure(
                (DifferentialGradedModules(self),),
                {
                    "graded_algebra": self,
                    "graded_algebra_action": right_action,
                    "dg_algebra": self,
                    "dg_module_leibniz_decision": True,
                    "regular_module_source": source,
                },
            )

        def right_action(self):
            return lambda module_element, algebra_element: module_element * algebra_element

        def act(self, module_element, algebra_element):
            return module_element * algebra_element

        def is_differential_graded_module(self) -> bool:
            return True

        def _Hom_(self, codomain, category=None):
            dgas = DifferentialGradedAlgebras(self.base_ring())
            if codomain in dgas and (
                category is None or category.is_subcategory(dgas)
            ):
                return dgas.Mor(self, codomain)
            return super()._Hom_(codomain, category=category)

        def differential(self):
            return self._preamble_differential

        @cached_method
        def _negative_cochain_zero_module(self):
            r"""The represented zero module used by the inherited cochain complex."""
            return self.base_ring().free_module(finite_ordered_set(()))

        def differential_component(self, degree):
            degree = int(degree)
            if degree < 0:
                source = self._negative_cochain_zero_module()
                if degree == -1:
                    target = self.graded_piece(0)
                else:
                    target = source
                return DifferentialComponentMorphism(
                    source,
                    target,
                    lambda _element: target.zero(),
                )
            source = self.graded_piece(degree)
            target = self.graded_piece(degree + 1)

            def component(element):
                source_element = self.from_graded_piece(degree, element)
                image = self.d(source_element)
                return image.homogeneous_component(degree + 1)

            return DifferentialComponentMorphism(source, target, component)


def StrictlyCommutativeDifferentialGradedAlgebras(base_ring):
    r"""The computed join ``DifferentialGradedAlgebras(R).Supercommutative().Alternating()``.

    The specification names the category; the join has no class of its own.
    """
    return DifferentialGradedAlgebras(base_ring).Supercommutative().Alternating()


class Differential(GradedDerivation):
    r"""A represented degree-one square-zero graded derivation."""

    def __init__(self, algebra, function) -> None:
        GradedDerivation.__init__(
            self,
            algebra.graded_derivations(algebra, shift=1),
            function,
        )

    def _square_zero_derivation(self):
        return None

    @cached_method
    def square_zero_decision(self):
        r"""The decision on ``d^2 = 0`` that the construction supplies, read on the first request (``OWN-22``)."""
        derived = self._square_zero_derivation()
        match derived:
            case None:
                return AtomicProposition("is_square_zero", self)
            case decision if decision is True or decision in Propositions:
                return decision
            case _:
                raise ValueError(f"d^2 = 0 is recorded only as True or a proposition, but got {derived}")

    @validator
    def validate_square_zero(self) -> None:
        r"""Raise ``ValueError`` when ``d(d(x)) != 0`` on a selected generator ``x`` (``OWN-22``)."""
        if self._square_zero_on_generators() is False:
            raise ValueError(
                f"{self._function} is not a differential on {self.algebra()}: d^2 != 0 on a generator"
            )

    def _square_zero_on_generators(self):
        algebra = self.algebra()
        undecided = AtomicProposition("is_square_zero", self)
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
            match self(self(generator)) == algebra.zero():
                case True:
                    pass
                case False:
                    return False
                case _:
                    return undecided
        return True


class _RetainedDifferential(Differential):
    r"""A differential carrying law decisions established by its constructor."""

    def __init__(self, algebra, function, graded_leibniz, square_zero) -> None:
        self._retained_graded_leibniz = graded_leibniz
        self._retained_square_zero = square_zero
        super().__init__(algebra, function)

    def _graded_derivation_derivation(self):
        return self._retained_graded_leibniz

    def _square_zero_derivation(self):
        return self._retained_square_zero


def _is_recorded_law_decision(decision) -> bool:
    r"""Whether ``decision`` is a recorded law decision: ``True``, a proposition, or ``None`` for none supplied."""
    return decision is True or decision is None or decision in Propositions


def _fix_selected_differential(
    algebra,
    function,
    *,
    graded_leibniz=None,
    square_zero=None,
) -> None:
    r"""Install one selected DGA differential at the DGA owner.

    Protected DGA storage contract under OWN-05. The permitted callers are
    the DGA constructor in this module and the de-Rham-algebra constructor,
    after each has supplied the owned algebra and the exact differential
    operation. The retained datum is read only through ``differential()``;
    callers never open the private storage.
    """
    if algebra._preamble_differential is not None:
        raise ValueError(f"{algebra} already has a differential; it cannot be given a second one")
    if not _is_recorded_law_decision(graded_leibniz) or not _is_recorded_law_decision(square_zero):
        raise ValueError(
            f"the Leibniz rule and d^2 = 0 are recorded only as True, a proposition or None, but got "
            f"{graded_leibniz} and {square_zero}"
        )
    differential = _RetainedDifferential(
        algebra,
        function,
        graded_leibniz,
        square_zero,
    )
    differential.validate_graded_leibniz(check=False)
    differential.validate_square_zero(check=False)
    algebra._preamble_differential = differential


class DGAMorphism:
    r"""A graded algebra morphism commuting with the selected differentials."""

    def __init__(
        self,
        parent,
        morphism,
        *,
        differential_compatibility=None,
        check=False,
    ) -> None:
        source = parent.domain()
        target = parent.codomain()
        graded_mor = GradedAlgebras(
            source.base_ring(), source.grading_monoid()
        ).Mor(source, target)
        if isinstance(morphism, GradedAlgebraMorphism) and morphism.parent() is graded_mor:
            underlying = morphism
        else:
            underlying = graded_mor(morphism)
        super().__init__(parent, underlying)
        if differential_compatibility is None:
            self._differential_compatibility = AtomicProposition(
                "commutes_with_differentials", self
            )
        else:
            if not (
                differential_compatibility is True
                or differential_compatibility in Propositions
            ):
                raise ValueError(
                    f"compatibility f d = d f is recorded only as True or a proposition, but got {differential_compatibility}"
                )
            self._differential_compatibility = differential_compatibility
        if check:
            self.validate_differential_compatibility()

    def differential_compatibility_decision(self):
        return self._differential_compatibility

    def _decide_differential_compatibility(self):
        source = self.domain()
        target = self.codomain()
        undecided = AtomicProposition("commutes_with_differentials", self)
        if not source.is_framed_algebra():
            return undecided
        labels = source.algebra_generating_set()
        finite = labels.cardinality().is_finite()
        if finite is not True:
            return undecided
        comparisons = tuple(
            self(source.d(source.algebra_generator(label)))
            == target.d(self(source.algebra_generator(label)))
            for label in labels
        )
        if any(answer is False for answer in comparisons):
            return False
        linear = (
            self.linearity_decision() is True
            and source.differential().linearity_decision() is True
            and target.differential().linearity_decision() is True
        )
        return True if linear and all(answer is True for answer in comparisons) else undecided

    def validate_differential_compatibility(self):
        r"""Diagnose a proved failure of ``f d = d f`` without forcing unknown equations."""
        observed = self._decide_differential_compatibility()
        if observed is False:
            raise ValueError(
                f"{self} is not a morphism of differential graded algebras {self.domain()} -> "
                f"{self.codomain()}: f d != d f"
            )
        return observed

    def __mul__(self, other):
        if not isinstance(other, DGAMorphism) or other.codomain() is not self.domain():
            return NotImplemented
        source = other.domain()
        decision = (
            True
            if self.differential_compatibility_decision() is True
            and other.differential_compatibility_decision() is True
            else None
        )
        graded = GradedAlgebras(source.base_ring(), source.grading_monoid())
        return DifferentialGradedAlgebras(source.base_ring()).Mor(
            source, self.codomain()
        )._from_differential_preserving_underlying_morphism(
            graded.Mor(self.domain(), self.codomain())(self)
            * graded.Mor(source, self.domain())(other),
            decision,
        )


class DGAMor(CategoricalMor):
    ElementMethods = DGAMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"morphisms of differential graded algebras {domain} -> {codomain} need one base ring, but they "
                f"are over {domain.base_ring()} and {codomain.base_ring()}"
            )
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, morphism, *, check=False):
        return self.element_class(self, morphism, check=check)

    def _from_differential_preserving_generator_map(self, images):
        r"""Construct from generator images when the construction proves all DGA laws."""
        source = self.domain()
        graded = GradedAlgebras(source.base_ring(), source.grading_monoid())
        underlying = graded.Mor(source, self.codomain())._from_degree_preserving_generator_map(
            images
        )
        return self.element_class(
            self,
            underlying,
            differential_compatibility=True,
        )

    def _from_differential_preserving_underlying_morphism(self, morphism, decision=True):
        r"""Lift a graded algebra morphism, with ``decision`` as its decision that it commutes with the differentials.

        ``None`` supplies no construction proof, so the resulting arrow retains
        the proposition that it commutes with the differentials.  An explicit
        diagnostic may later compute generatorwise evidence without changing
        that retained law.
        """
        return self.element_class(
            self,
            morphism,
            differential_compatibility=decision,
        )

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        source = self.domain()
        underlying = GradedAlgebras(
            source.base_ring(), source.grading_monoid()
        ).Mor(source, source).identity()
        return self._from_differential_preserving_underlying_morphism(
            underlying,
            True,
        )


class DGAMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return DGAMor


DifferentialGradedAlgebras._MorCategory = DGAMorCategoryConstruction


__all__ = [
    "DGAMor",
    "DGAMorCategoryConstruction",
    "DGAMorphism",
    "DegreewiseLinearMorphism",
    "Differential",
    "DifferentialComponentMorphism",
    "DifferentialGradedAlgebras",
    "StrictlyCommutativeDifferentialGradedAlgebras",
]
