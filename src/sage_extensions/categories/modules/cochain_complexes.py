r"""Cochain complexes of owned modules and their cohomology."""

from sage.categories.map import Map
from sage.categories.category import Category
from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.modules.pure.modules import ModulesWithChosenFinitePresentation

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.graded_direct_sums import (
    GradedDirectSumElement,
    _DirectSumOfModules,
    _direct_sum_of_modules,
)
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphism,
    _combined_linearity_decision,
    _initialize_module_mor_parent,
)
from sage_extensions.categories.modules.pure.modules import (
    FinitelyPresentedModules,
    LinearEndCategoryConstruction,
    ModuleMorCategoryConstruction,
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.owned_category import owned_category_join
from sage_extensions.logic import AtomicProposition, conjunction
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class CochainComplexes(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The free module of rank one in degree zero, with zero differential."""
        from sage_extensions.categories.modules.pure.modules import Modules

        ring = self.base_ring()
        free = Modules(ring).an_object()
        return self({0: free}, {})

    def _call_(
        self,
        pieces,
        differentials,
        name=None,
        *,
        extra_categories=(),
        extra_construction_data=None,
    ):
        r"""Construct a finite-support cochain complex from its defining data.

        A dictionary of pieces is a declaration that every unlisted integer
        degree is the zero module.  The differentials are the selected maps
        ``C^p -> C^(p+1)``; omitted maps between represented zero pieces are
        zero.  This category constructor is the authoritative finite-support
        construction and the public construction route.
        """
        if not isinstance(pieces, dict) or not isinstance(differentials, dict):
            raise TypeError(
                f"{self}(pieces, differentials) takes a dictionary degree -> module of pieces and a "
                f"dictionary degree -> morphism of differentials, but got pieces {pieces!r} and "
                f"differentials {differentials!r}; for pieces given in every integer degree use "
                f"{self}.from_family"
            )
        return _cochain_complex(
            self,
            pieces,
            differentials,
            name=name,
            extra_categories=extra_categories,
            extra_construction_data=extra_construction_data,
        )

    def from_family(
        self,
        pieces,
        differentials,
        name=None,
        *,
        extra_categories=(),
        extra_construction_data=None,
        _realization=None,
    ):
        r"""Construct a lazy integer-graded complex from two indexed families.

        Unlike :meth:`_call_`, this construction does not assert that degrees
        absent from a finite dictionary are zero: the supplied families define
        the piece and outgoing differential in every owned integer degree.
        """
        if not isinstance(pieces, IndexedFamily) or not isinstance(
            differentials, IndexedFamily
        ):
            raise TypeError(
                f"{self}.from_family takes integer-indexed families of pieces and of differentials, "
                f"but got pieces {pieces!r} and differentials {differentials!r}"
            )
        if pieces.index_set() is not differentials.index_set():
            raise ValueError(
                f"a cochain complex indexes its pieces and its differentials by the same set of degrees, "
                f"but the pieces are indexed by {pieces.index_set()} and the differentials by "
                f"{differentials.index_set()}"
            )
        return _cochain_complex(
            self,
            pieces,
            differentials,
            name=name,
            extra_categories=extra_categories,
            extra_construction_data=extra_construction_data,
            _realization=_realization,
        )

    def _repr_object_names(self):
        return f"cochain complexes over {self.base_ring()}"

    def super_categories(self):

        return [GradedModules(self.base_ring())]

    _MorCategory = None

    def underlying_graded_module(self):
        r"""Return the forgetful functor from cochain complexes to graded modules."""
        from sage_extensions.categories.functors.cochain_complexes import (
            _cochain_underlying_graded_module_functor,
        )

        return _cochain_underlying_graded_module_functor(self.base_ring())

    def cohomology(self, degree):
        r"""Return the degree-``degree`` cohomology functor on this category."""
        from sage_extensions.categories.functors.cohomology import (
            _cohomology_functor,
        )

        return _cohomology_functor(self.base_ring(), degree)

    def localization_at_quasi_isomorphisms(self):
        r"""Return ``Q : Ch(R) -> D(R)``, the localization at quasi-isomorphisms."""
        from sage_extensions.categories.modules.derived_categories import (
            _derived_localization_functor,
        )

        return _derived_localization_functor(self.base_ring())

    class ParentMethods:
        @cached_method
        def differential(self):
            return CochainDifferential(self)

        def d(self, element):
            return self.differential()(element)

        def cycles(self, degree):
            r"""Return ``ker(d^degree)`` as a subobject of ``C^degree``."""
            return self.differential_component(degree).kernel()

        def boundaries(self, degree):
            r"""Return ``im(d^(degree-1))`` as a subobject of ``C^degree``."""
            return self.differential_component(int(degree) - 1).image()

        def cohomology(self, degree):
            return _cohomology(self, degree)


class CohomologyModules(OwnedCategoryOverBaseRing):
    r"""Cohomology modules ``H^p(C)`` retaining a represented cycle quotient.

    The retained data are cochain maps ``r : C -> C'`` and ``s : C' -> C``,
    mutually inverse up to homotopy, and the quotient ``Z^p(C') / B^p(C')``
    of the cycles of ``C'`` by its boundaries.  Homotopic cochain maps
    induce the same map on cohomology, so ``H^p(r)`` and ``H^p(s)`` are
    inverse isomorphisms ``H^p(C) ≅ H^p(C')``: a cocycle ``z`` of ``C`` has
    the class of ``r(z)``, and a class has the representative ``s(z')`` of
    a representative ``z'`` in ``C'``.  The cycle quotient of ``C`` itself is
    the case ``C' = C`` with ``r = s`` the identity.
    """

    def an_object(self):
        r"""The degree-zero cohomology of a one-term complex."""
        return CochainComplexes(self.base_ring()).an_object().cohomology(0)

    def _repr_object_names(self):
        return f"cohomology modules over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            cohomology_complex,
            cohomology_degree,
            cohomology_retraction,
            cohomology_section,
            cohomology_cycles,
            cohomology_boundaries,
            cohomology_boundary_in_cycles,
            **rest,
        ) -> None:
            self._preamble_cohomology_complex = cohomology_complex
            self._preamble_cohomology_degree = cohomology_degree
            self._preamble_cohomology_retraction = cohomology_retraction
            self._preamble_cohomology_section = cohomology_section
            self._preamble_cohomology_cycles = cohomology_cycles
            self._preamble_cohomology_boundaries = cohomology_boundaries
            self._preamble_cohomology_boundary_in_cycles = cohomology_boundary_in_cycles
            super().__init__(**rest)

        def cochain_complex(self):
            return self._preamble_cohomology_complex

        def cohomological_degree(self):
            return self._preamble_cohomology_degree

        degree = cohomological_degree

        def cycle_representative(self, cohomology_class):
            r"""Return the selected closed representative ``s(z')`` in ``C^p``."""

            if cohomology_class.parent() is not self:
                cohomology_class = self(cohomology_class)
            lift = self._framing_lift(self(cohomology_class))
            cycles = self.cokernel_projection().domain()
            # When the presentation's codomain is the cycle module itself, the
            # chosen preimage under ``Z^p ->> H^p`` already is a cycle; a free
            # cover on the cycle generators states its framing coordinates.
            match lift.parent():
                case source if source is cycles:
                    representative = lift
                case _:
                    representative = cycles.linear_combination(
                        {label: lift(label) for label in lift.support().domain()}
                    )
            section = self._preamble_cohomology_section.component(self.cohomological_degree())
            return section(cycles.inclusion()(representative))

        def class_of_cycle(self, cycle):
            r"""Return the class of ``r(z)`` for a closed element ``z`` of ``C^p``."""

            complex_ = self.cochain_complex()
            degree = self.cohomological_degree()
            outgoing = complex_.differential_component(degree)
            current = outgoing.domain()
            if cycle.parent() is not current:
                cycle = current(cycle)
            target = outgoing.codomain()
            closed = outgoing(cycle) == target.zero()
            if closed is False:
                raise ValueError(
                    f"{cycle} has no class in {self}: only a cocycle has a cohomology class, "
                    f"but d^{degree}({cycle}) = {outgoing(cycle)} is nonzero"
                )

            transported = self._preamble_cohomology_retraction.component(degree)(cycle)
            cycles = self._preamble_cohomology_cycles
            cycle_in_cycles = cycles.inclusion().lift(transported)
            return self.cokernel_projection()(cycle_in_cycles)


class CochainDifferential:
    r"""The degree-``+1`` differential of a represented cochain complex."""

    def __init__(self, complex_) -> None:
        self._complex = complex_

    def complex(self):
        return self._complex

    def degree_shift(self):
        return _owned_integers().one()

    def component(self, degree):
        return self.complex().differential_component(degree)

    def __call__(self, element):
        complex_ = self.complex()
        element = complex_(element)
        components = {}
        for degree, component in element.homogeneous_components().items():
            image = self.component(degree)(component)
            target = complex_.graded_piece(degree + 1)
            if image != target.zero():
                components[degree + 1] = image
        return complex_.from_components(components)


class _CochainComplexDirectSum(_DirectSumOfModules):
    r"""A represented integer-graded cochain complex.

    A dictionary presentation has finite support and therefore declares every
    unlisted degree to be the zero module.  An indexed-family presentation is
    lazy over all integer degrees and does not identify an unrequested degree
    with zero.
    """

    def __init__(
        self,
        cochain_finite_support,
        cochain_selected_degrees,
        cochain_selected_differentials,
        cochain_differential_family,
        cochain_name=None,
        **rest,
    ) -> None:
        self._finite_support = bool(cochain_finite_support)
        self._selected_degrees = tuple(cochain_selected_degrees)
        self._selected_differentials = dict(cochain_selected_differentials)
        self._differential_family = cochain_differential_family
        self._cochain_name = cochain_name
        super().__init__(**rest)

    def selected_degrees(self):
        if not self._finite_support:
            raise TypeError(
                f"{self} may be nonzero in infinitely many degrees, so it has no finite list of "
                f"nonzero degrees; use degree_index_set()"
            )
        return self._selected_degrees

    def has_finite_support(self) -> bool:
        return self._finite_support

    def cohomological_degree_set(self):
        return self.degree_index_set()

    def degree_convention(self):
        return "cohomological"

    def _raw_differential_component(self, degree):
        degree = int(degree)
        source = self.graded_piece(degree)
        target = self.graded_piece(degree + 1)
        if self._finite_support:
            selected = self._selected_differentials.get(degree)
            if selected is None:
                return source.module_category().Mor(source, target).zero()
            return selected
        return self._differential_family(self.degree_index_set()(degree))

    def differential_component(self, degree):
        degree = int(degree)
        source = self.graded_piece(degree)
        target = self.graded_piece(degree + 1)
        selected = self._raw_differential_component(degree)
        if selected.domain() is not source or selected.codomain() is not target:
            raise ValueError(
                f"the differential d^{degree} of {self} must be a map C^{degree} -> C^{degree + 1}, "
                f"i.e. {source} -> {target}, but it is {selected.domain()} -> {selected.codomain()}"
            )
        return selected

    def differential_square_zero_decision(self, degree):
        r"""Decide ``d^(p+1)d^p=0`` when the selected source generators determine it."""
        degree = int(degree)
        first = self.differential_component(degree)
        second = self.differential_component(degree + 1)
        source = first.domain()
        if (
            not source.has_selected_module_resolution()
            or source.module_generating_set().cardinality().is_finite() is not True
        ):
            return AtomicProposition("differential_squares_zero", self, degree)
        zero = second.codomain().zero()
        return conjunction(
            second(first(source.module_generator(label))) == zero
            for label in source.module_generating_set()
        )

    def square_zero_decision(self):
        r"""Return the represented decision that the selected differential squares to zero."""
        if not self._finite_support:
            return AtomicProposition("differential_squares_zero", self)
        return conjunction(
            self.differential_square_zero_decision(degree)
            for degree in self.selected_degrees()
        )

    def validate_differentials(self):
        r"""Diagnose a proved violation of ``d^2=0`` without forcing undecided equations."""
        decision = self.square_zero_decision()
        if decision is False:
            raise ValueError(
                f"{self} is not a cochain complex: the selected differential does not square to zero"
            )
        return decision

    _validate_differentials = validate_differentials

    def _repr_(self):
        return self._cochain_name or "Cochain complex"


def _cochain_complex(
    category,
    pieces,
    differentials,
    *,
    name=None,
    extra_categories=(),
    extra_construction_data=None,
    _realization=None,
):
    r"""Construct one integer-graded direct sum carrying its selected differential."""

    ring = category.base_ring()
    integers = _owned_integers()
    match pieces:
        case dict():
            match differentials:
                case dict():
                    pass
                case _:
                    raise TypeError(
                        f"a cochain complex over {ring} with pieces given by a dictionary takes its "
                        f"differentials as a dictionary degree -> morphism, but got {differentials!r}"
                    )
            selected_pieces = {int(degree): module for degree, module in pieces.items()}
            selected_differentials = {
                int(degree): morphism for degree, morphism in differentials.items()
            }
            zero_module = ring.free_module(finite_ordered_set(()))
            family = indexed_family(
                integers,
                lambda degree: selected_pieces.get(int(degree), zero_module),
                name="Cochain-complex pieces",
            )
            finite_support = True
            selected_degrees = tuple(sorted(selected_pieces))
            differential_family = None
        case IndexedFamily():
            match differentials:
                case IndexedFamily():
                    pass
                case _:
                    raise TypeError(
                        f"a cochain complex over {ring} with pieces given by an indexed family takes its "
                        f"differentials as an indexed family, but got {differentials!r}"
                    )
            match (pieces.index_set() is integers, differentials.index_set() is integers):
                case (True, True):
                    pass
                case _:
                    raise ValueError(
                        f"a cochain complex is graded by the integers ZZ, but its pieces are indexed by "
                        f"{pieces.index_set()} and its differentials by {differentials.index_set()}"
                    )
            family = pieces
            finite_support = False
            selected_degrees = ()
            selected_differentials = {}
            differential_family = differentials
        case _:
            raise TypeError(
                f"the pieces of a cochain complex over {ring} are a dictionary degree -> module or an "
                f"integer-indexed family of modules, but got {pieces!r}"
            )

    data = dict(extra_construction_data or {})
    data.update(
        cochain_finite_support=finite_support,
        cochain_selected_degrees=selected_degrees,
        cochain_selected_differentials=selected_differentials,
        cochain_differential_family=differential_family,
        cochain_name=name,
    )
    match _realization:
        case None:
            realization = (_CochainComplexDirectSum, GradedDirectSumElement)
        case selected:
            realization = selected
    return _direct_sum_of_modules(
        ring,
        integers,
        family,
        extra_categories=(category, *tuple(extra_categories)),
        construction_data=data,
        _realization=realization,
    )


def _cochain_components_from_elementwise(domain, codomain, function):
    r"""Return the degreewise linear components of one elementwise cochain map."""
    def component_at(degree):
        degree = int(degree)
        source = domain.graded_piece(degree)
        target = codomain.graded_piece(degree)

        def on_piece(element):
            total = domain.from_component(degree, element)
            image = codomain(function(total))
            return image.homogeneous_component(degree)

        return source.module_category().Mor(source, target).elementwise(on_piece)

    return indexed_family(
        domain.degree_index_set(),
        component_at,
        name="Elementwise cochain-morphism components",
    )


class CochainMorphismMethods:
    r"""A degree-zero morphism commuting with the selected differentials."""

    def _elementwise_linearity_derivation(self):
        r"""Retain the linearity decisions of the supplied component maps.

        Component data specify a degree-preserving map, but a declared
        component may still carry an undecided linearity hypothesis. A
        finite source support reduces this question to those components;
        no infinite family is enumerated to assert its linearity.
        """
        if not self.domain().has_finite_support():
            return AtomicProposition("is_linear", self)
        return _combined_linearity_decision(
            self._selected_degree_component(degree)
            for degree in self.domain().selected_degrees()
        )

    def _degree_preservation_derivation(self):
        return True

    def __init__(self, parent, components, *, cochain_premises=None) -> None:
        if isinstance(components, Map):
            if (
                components.domain() is not parent.domain()
                or components.codomain() is not parent.codomain()
            ):
                raise ValueError(
                    f"{components} is a map {components.domain()} -> {components.codomain()}, "
                    f"not a cochain map {parent.domain()} -> {parent.codomain()}"
                )
            components = _cochain_components_from_elementwise(
                parent.domain(),
                parent.codomain(),
                components,
            )
        self._components = components
        self._cochain_premises = cochain_premises
        super().__init__(
            parent,
            self._evaluate_components,
            elementwise=True,
            linearity_premises=cochain_premises,
        )

    def _raw_component(self, degree):
        degree = int(degree)
        return self._components(self.domain().degree_index_set()(degree))

    @cached_method
    def _selected_degree_component(self, degree):
        r"""Read the retained component as an ordinary linear map over ``S``.

        The cochain datum admits this linearity hypothesis. Forgetting a
        stronger component theory preserves its map and decision; an
        arbitrary declared map retains an unresolved linearity decision.
        The ordinary fixed Mor also retains the full ``Z(S)`` action,
        even when the piece has a richer coefficient-module realization.
        """
        source = self.domain().graded_piece(degree)
        target = self.codomain().graded_piece(degree)
        mor = ModuleMorCategoryConstruction(
            Modules(self.domain().base_ring())
        ).Of(source, target)
        return mor(self._raw_component(degree))

    def _validate_degree_component(self, degree, selected):
        r"""Return the selected component; cochain commutation is checked separately."""
        return selected

    def cochain_degree_decision(self, degree):
        r"""Decide ``d f^p = f^(p+1) d`` when degree ``p`` is finitely determined."""
        if self._cochain_premises is not None:
            return True
        degree = int(degree)
        source = self.domain().graded_piece(degree)
        if (
            not source.has_selected_module_resolution()
            or source.module_generating_set().cardinality().is_finite() is not True
        ):
            return AtomicProposition("commutes_with_differential", self, degree)
        component = self.component(degree)
        following = self.component(degree + 1)
        left = self.codomain().differential_component(degree)
        right = self.domain().differential_component(degree)
        return conjunction(
            left(component(source.module_generator(label)))
            == following(right(source.module_generator(label)))
            for label in source.module_generating_set()
        )

    def cochain_map_decision(self):
        r"""Return the represented decision that all component squares commute."""
        if self._cochain_premises is not None:
            return True
        if not self.domain().has_finite_support():
            return AtomicProposition("commutes_with_differentials", self)
        return conjunction(
            self.cochain_degree_decision(degree)
            for degree in self.domain().selected_degrees()
        )

    def validate_cochain_map(self):
        r"""Diagnose a proved failure of the cochain-map equations without forcing unknown ones."""
        decision = self.cochain_map_decision()
        if decision is False:
            raise ValueError(
                f"{self} is not a cochain map: its selected components do not commute with the differentials"
            )
        return decision

    _validate_components = validate_cochain_map

    def _evaluate_components(self, element):
        element = self.domain()(element)
        return self.codomain().from_components(
            {
                degree: self.component(degree)(component)
                for degree, component in element.homogeneous_components().items()
            }
        )

    def __add__(self, other):
        parent = self.parent()
        if other in parent:
            other = parent(other)
        elif parent.domain() is parent.codomain() and other in parent.base_ring():
            other = parent._scalar_identity(parent.base_ring()(other))
        else:
            return NotImplemented
        return parent._from_constructed_components(
            indexed_family(
                self.domain().degree_index_set(),
                lambda degree: self._selected_degree_component(degree)
                + other._selected_degree_component(degree),
                name="Sum cochain-morphism components",
            ),
            premises=(self, other),
        )

    def __neg__(self):
        return self.parent()._from_constructed_components(
            indexed_family(
                self.domain().degree_index_set(),
                lambda degree: -self._selected_degree_component(degree),
                name="Negative cochain-morphism components",
            ),
            premises=(self,),
        )

    def __sub__(self, other):
        parent = self.parent()
        if other in parent:
            return self + (-parent(other))
        if parent.domain() is parent.codomain() and other in parent.base_ring():
            return self + parent._scalar_identity(-parent.base_ring()(other))
        return NotImplemented

    def __rmul__(self, scalar):
        if isinstance(scalar, (Morphism, CategoricalArrow)) and _precomposable(scalar, self):
            return scalar.__mul__(self)
        return self.parent().scalar_multiple(scalar, self)

    def __mul__(self, other):
        if not isinstance(other, CochainMorphismMethods) or not _precomposable(self, other):
            return NotImplemented
        if other.parent() is self.parent() and self.domain() is self.codomain():
            return self.parent()._compose_endomorphisms(self, other)
        mor = CochainComplexes(self.domain().base_ring()).Mor(
            other.domain(), self.codomain()
        )
        return mor._from_constructed_components(
            indexed_family(
                other.domain().degree_index_set(),
                lambda degree: self._selected_degree_component(degree)
                * other._selected_degree_component(degree),
                name="Composite cochain-morphism components",
            ),
            premises=(self, other),
        )


CochainMorphism = CochainMorphismMethods


class CochainMor(CategoricalMor):
    ElementMethods = CochainMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"there are no cochain maps {domain} -> {codomain}: both complexes must be over one ring, "
                f"but they are over {domain.base_ring()} and {codomain.base_ring()}"
            )
        if domain.degree_index_set() is not codomain.degree_index_set():
            raise ValueError(
                f"there are no cochain maps {domain} -> {codomain}: both complexes must be graded by one "
                f"set of degrees, but they are graded by {domain.degree_index_set()} and "
                f"{codomain.degree_index_set()}"
            )
        _initialize_module_mor_parent(
            self, mor_family, domain, codomain, full_linear_mor=False
        )

    def _degrees(self):
        if not self.domain().has_finite_support() or not self.codomain().has_finite_support():
            raise TypeError(
                f"{self.domain()} or {self.codomain()} may be nonzero in infinitely many degrees, "
                f"so the cochain maps between them have no finite list of degrees"
            )
        return tuple(
            sorted(
                set(self.domain().selected_degrees())
                | set(self.codomain().selected_degrees())
            )
        )

    def _element_constructor_(self, components):
        if isinstance(components, Map):
            if self._already_parented_arrow(components):
                return components
            raise TypeError(f"{components} belongs to another Mor; apply the functor between the categories")
        if isinstance(components, dict):
            selected = {int(degree): morphism for degree, morphism in components.items()}

            def component_at(degree):
                degree = int(degree)
                source = self.domain().graded_piece(degree)
                target = self.codomain().graded_piece(degree)
                chosen = selected.get(degree)
                if chosen is not None:
                    return chosen
                return source.module_category().Mor(source, target).zero()

            components = indexed_family(
                self.domain().degree_index_set(),
                component_at,
                name="Finite-support cochain-morphism components",
            )
        elif callable(components):
            components = indexed_family(
                self.domain().degree_index_set(),
                components,
                name="Declared cochain-morphism components",
            )
        if not isinstance(components, IndexedFamily):
            raise TypeError(
                f"an element of {self} is given by its components, a family of maps indexed by degree, "
                f"but got {components!r}"
            )
        if components.index_set() is not self.domain().degree_index_set():
            raise ValueError(
                f"the components of an element of {self} are indexed by {self.domain().degree_index_set()}, "
                f"but the given family is indexed by {components.index_set()}"
            )
        return self.element_class(self, components)

    def _from_constructed_components(self, components, *, premises=()):
        r"""Retain component formulas and the cochain maps that justify them.

        The additive, scalar and composition operations call this supplier
        with their actual input arrows. The empty family is used only for
        zero and identity, whose laws follow from the module axioms.
        Arbitrary declared families use the ordinary constructor instead.
        """
        if (
            not isinstance(components, IndexedFamily)
            or components.index_set() is not self.domain().degree_index_set()
        ):
            raise TypeError(
                f"constructed components in {self} must be a family indexed by "
                f"{self.domain().degree_index_set()}"
            )
        return self.element_class(
            self,
            components,
            cochain_premises=tuple(premises),
        )

    def _compose_endomorphisms(self, left, right):
        r"""Compose the retained degreewise maps under their cochain laws."""
        if left not in self or right not in self or self.domain() is not self.codomain():
            raise TypeError(f"composition in {self} needs two admitted endomorphisms")
        return self._from_constructed_components(
            indexed_family(
                self.domain().degree_index_set(),
                lambda degree: left._selected_degree_component(degree)
                * right._selected_degree_component(degree),
                name="Composite cochain-endomorphism components",
            ),
            premises=(left, right),
        )

    def _module_scalar_multiple(self, scalar, morphism):
        r"""Scale each component by the retained central scalar action."""
        if morphism not in self:
            raise TypeError(f"scalar multiplication in {self} needs an admitted cochain map")
        morphism = self(morphism)
        scalar = self.base_ring()(scalar)

        def scaled_component(degree):
            component = morphism._selected_degree_component(degree)
            return component.parent().scalar_multiple(scalar, component)

        return self._from_constructed_components(
            indexed_family(
                self.domain().degree_index_set(),
                scaled_component,
                name="Scalar-multiple cochain-morphism components",
            ),
            premises=(morphism,),
        )

    def _owned_scalar_multiple(self, scalar, morphism):
        return self._module_scalar_multiple(scalar, morphism)

    def _scalar_identity(self, scalar):
        return self._module_scalar_multiple(scalar, self.identity())

    def elementwise(self, function):
        if isinstance(function, Map):
            return self(function)
        if not callable(function):
            raise TypeError(
                f"an element of {self} given elementwise needs a function on {self.domain()}, "
                f"but got {function!r}"
            )
        return self.element_class(
            self,
            _cochain_components_from_elementwise(
                self.domain(),
                self.codomain(),
                function,
            ),
        )

    def zero(self):
        def zero_component(degree):
            source = self.domain().graded_piece(degree)
            target = self.codomain().graded_piece(degree)
            return source.module_category().Mor(source, target).zero()

        return self._from_constructed_components(
            indexed_family(
                self.domain().degree_index_set(),
                zero_component,
                name="Zero cochain-morphism components",
            )
        )

    def linear_combination(self, coefficients):
        result = self.zero()
        for morphism, coefficient in coefficients.items():
            result += self.scalar_multiple(coefficient, morphism)
        return result

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"{self} has no identity: an identity map needs domain = codomain, "
                f"but these are {self.domain()} and {self.codomain()}"
            )
        domain = self.domain()

        def identity_component(degree):
            piece = domain.graded_piece(degree)
            return piece.module_category().Mor(piece, piece).identity()

        return self._from_constructed_components(
            indexed_family(
                domain.degree_index_set(),
                identity_component,
                name="Identity cochain-morphism components",
            )
        )


class CochainMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return CochainMor


# The declaration is placed after the concrete fixed-Mor class to avoid a
# module-level forward-reference helper or a second registration mechanism.
CochainComplexes._MorCategory = CochainMorCategoryConstruction
CochainComplexes._EndCategory = LinearEndCategoryConstruction


@cached_function(key=lambda complex_, degree: (id(complex_), int(degree)))
def _cohomology(complex_, degree):
    r"""Return ``H^degree = ker(d^degree) / im(d^(degree-1))``."""
    identity = CochainComplexes(complex_.base_ring()).Mor(complex_, complex_).identity()
    return _cohomology_along(complex_, degree, identity, identity)


def _cohomology_along(complex_, degree, retraction, section):
    r"""Return ``H^degree(C)`` as the cycle quotient of ``C' = retraction.codomain()``.

    ``retraction : C -> C'`` and ``section : C' -> C`` are cochain maps
    inverse to each other up to homotopy, so ``H^degree(C) ≅ H^degree(C')``
    by ``H(retraction)`` with inverse ``H(section)``.
    """
    degree = int(degree)
    ring = complex_.base_ring()
    comparison = retraction.codomain()
    cycles = comparison.cycles(degree)
    boundaries = comparison.boundaries(degree)
    boundary_in_cycles = boundaries.inclusion().factor_through(cycles.inclusion())
    if cycles not in FinitelyPresentedModules(ring):
        raise NotImplementedError(
            f"H^{degree} of {complex_} is ker(d)/im(d) of {comparison}, but this chosen "
            "finite-presentation realization requires finitely presented cycles"
        )
    return ModulesWithChosenFinitePresentation(ring)(
        boundary_in_cycles,
        category=owned_category_join((CohomologyModules(ring),)),
        **{
            "cohomology_complex": complex_,
            "cohomology_degree": degree,
            "cohomology_retraction": retraction,
            "cohomology_section": section,
            "cohomology_cycles": cycles,
            "cohomology_boundaries": boundaries,
            "cohomology_boundary_in_cycles": boundary_in_cycles,
        },
    )


__all__ = [
    "CochainComplexes",
    "CochainDifferential",
    "CochainMor",
    "CochainMorphism",
    "CohomologyModules",
]
