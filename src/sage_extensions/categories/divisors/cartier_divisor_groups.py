r"""Cartier divisors as global sections of the Cartier quotient sheaf.

For a scheme ``X`` let ``K_X`` be the sheaf of total quotient rings.  A
Cartier divisor is, by definition, a global section of

``K_X^* / O_X^*``.

The quotient-sheaf convention is Stacks Project, Tag 02AQ.  A represented
finite-atlas lift of such a section consists of local equations ``f_i`` in the
total quotient rings of the affine charts, with ``f_i/f_j`` a regular unit on
every overlap.  Those lifts are presentations of elements of ``CDiv(X)``;
they are not a second kind of Cartier-divisor object.
"""

from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    OwnedNoetherianRings,
    OwnedRings,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.gluing import (
    FiniteAffineAtlases,
    _AffineChartOpenSubobjects,
)
from sage_extensions.categories.schemes.ringed_spaces import (
    SheafObjects,
    _is_empty_open,
    _open_sheaf_placement,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import Category


def _integers():
    return _owned_integers()


class _TotalQuotientSheafEngine:
    r"""Private realization of the meromorphic-function sheaf ``K_X``.

    In general ``K_X`` is the sheaf associated to
    ``U |-> S(U)^(-1) O_X(U)``, where ``S(U)`` consists of sections whose germ
    is a nonzerodivisor at every point.  On a locally Noetherian scheme this
    sheaf already has ``K_X(U)=Q(O_X(U))`` for every affine open ``U`` (Stacks,
    Tags 01X1 and 02OV).  The latter is the represented computational regime
    used by the finite-atlas lift below.
    """

    def __init__(self, scheme, **rest) -> None:
        self._scheme = scheme
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def sections_on_affine(self, affine_open):
        r"""Return ``K_X(U)=Q(O_X(U))`` in the represented Noetherian regime."""
        ring = affine_open.coordinate_algebra()
        assert ring in OwnedNoetherianRings(), (
            f"cannot compute K_X on the affine open {affine_open}: the total-quotient-ring formula "
            f"K_X(U) = Q(O_X(U)) is implemented only for Noetherian coordinate rings, "
            f"but {ring} is not known to be Noetherian"
        )
        return ring.total_quotient_ring()

    def _repr_(self):
        return f"Total quotient sheaf on {self.scheme()}"


class _TotalQuotientSectionsPresheaf(Functor):
    r"""Total quotient sections on the represented Noetherian affine opens.

    The affine formula and its localization restrictions are those used by
    ``_TotalQuotientSheafEngine`` (Stacks, Tags 01X1 and 02OV).

    A selected affine chart image is an affine open even when the ambient
    scheme is not affine. Its coordinate algebra comes from the structure
    sheaf, including the retained chart transition on restrictions.

    Unexecuted projective-line basis specimen::

        sage: from dzack_research.preamble.all import *
        sage: X = ProjectiveSpaces(QQ)(1)
        sage: atlas = X.standard_affine_atlas()
        sage: site = X.open_subsets_site()
        sage: chart = site(atlas.chart_open_subset(0))
        sage: overlap = site(atlas.chart_open_subset(0, atlas.overlap(0, 1)))
        sage: quotient = CartierDivisorGroups().of_scheme(X).quotient_sheaf()
        sage: K = quotient.numerator_sheaf().ring_sheaf()
        sage: A = atlas.chart(0).coordinate_algebra()
        sage: K.sections(chart) is A.total_quotient_ring()
        True
        sage: opposite = site.opposite()
        sage: inclusion = site.Mor(overlap, chart)()
        sage: arrow = opposite.Mor(opposite(chart), opposite(overlap))(inclusion)
        sage: restriction = K.open_sections_presheaf().on_morphism(arrow)
        sage: restriction(K.sections(chart).one()) == K.sections(overlap).one()
        True
        sage: second = site(atlas.chart_open_subset(1))
        sage: second_arrow = opposite.Mor(opposite(second), opposite(overlap))(site.Mor(overlap, second)())
        sage: change_chart = K.open_sections_presheaf().on_morphism(second_arrow)
        sage: B = atlas.chart(1).coordinate_algebra()
        sage: x = next(iter(A.algebra_generators()))
        sage: y = next(iter(B.algebra_generators()))
        sage: R = atlas.overlap(0, 1).coordinate_algebra()
        sage: change_chart(K.sections(second)(y)) == K.sections(overlap)(R(x)).inverse_of_unit()
        True
    """

    def __init__(self, scheme) -> None:
        self._scheme = scheme
        self._structure_presheaf = scheme.structure_sheaf().open_sections_presheaf()
        super().__init__(
            self._structure_presheaf.domain(), OwnedRings().Commutative()
        )

    def _apply_object(self, opposite_object):
        from sage_extensions.categories.schemes.schemes import Schemes

        if _is_empty_open(self, opposite_object):
            # The empty-cover condition gives the terminal ring (Stacks, 04B3).
            return self._structure_presheaf(opposite_object)
        subset = opposite_object.underlying_object().value()
        assert (
            self._scheme in Schemes(self._scheme.scheme_base_ring()).Affine()
            or subset in _AffineChartOpenSubobjects(self._scheme)
        ), (
            f"total quotient sections on {opposite_object}: not implemented; "
            "the open must be identified with an affine chart before applying "
            "the affine total quotient formula"
        )
        ring = self._structure_presheaf(opposite_object)
        assert ring in OwnedNoetherianRings(), (
            f"total quotient sections on {opposite_object} require a Noetherian "
            f"affine coordinate ring, but {ring} is not known to be Noetherian"
        )
        return ring.total_quotient_ring()

    def _apply_morphism(self, opposite_arrow):
        source = self(opposite_arrow.domain())
        target = self(opposite_arrow.codomain())
        if _is_empty_open(self, opposite_arrow.domain()) or _is_empty_open(self, opposite_arrow.codomain()):
            return self.codomain().Mor(source, target).elementwise(lambda _section: target.zero())
        ring_map = self._structure_presheaf(opposite_arrow)
        return self.codomain().Mor(source, target).elementwise(
            lambda section: _total_quotient_pullback(ring_map, section)
        )


class _UnitSheafEngine:
    r"""Private realization of the sheaf of units of a represented ring sheaf."""

    def __init__(self, ring_sheaf, **rest) -> None:
        self._ring_sheaf = ring_sheaf
        super().__init__(**rest)

    def ring_sheaf(self):
        return self._ring_sheaf

    def scheme(self):
        return self.ring_sheaf().scheme()

    def _repr_(self):
        return f"Unit sheaf of {self.ring_sheaf()}"


class _RegularUnitSheafEngine:
    r"""Private realization of ``O_X^*`` without requiring an affine ``O_X`` engine."""

    def __init__(self, scheme, **rest) -> None:
        self._scheme = scheme
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def _repr_(self):
        return f"Regular unit sheaf O^* on {self.scheme()}"


class _UnitSectionsPresheaf(Functor):
    r"""Apply the unit-group functor to a ring sheaf's sections and restrictions.

    Ring maps preserve units and their inverses, so the same restrictions
    define the sheaf of units (Stacks, Tag 02AQ).
    """

    def __init__(self, ring_presheaf) -> None:
        from sage_extensions.categories.group.magmas import Monoids

        self._ring_presheaf = ring_presheaf
        self._units = Monoids().unit_group()
        super().__init__(ring_presheaf.domain(), self._units.codomain())

    def _apply_object(self, opposite_object):
        return self._units(self._ring_presheaf(opposite_object))

    def _apply_morphism(self, opposite_arrow):
        return self._units(self._ring_presheaf(opposite_arrow))


class _CartierDivisorQuotientSheafEngine:
    r"""Private realization of the quotient sheaf ``K_X^* / O_X^*``."""

    def __init__(self, numerator_sheaf, denominator_sheaf, **rest) -> None:
        self._numerator_sheaf = numerator_sheaf
        self._denominator_sheaf = denominator_sheaf
        assert numerator_sheaf.scheme() is denominator_sheaf.scheme(), (
            f"cannot form the quotient sheaf {numerator_sheaf} / {denominator_sheaf}: the two sheaves "
            f"must live on the same scheme, but they live on {numerator_sheaf.scheme()} and "
            f"{denominator_sheaf.scheme()}"
        )
        super().__init__(**rest)

    def scheme(self):
        return self.numerator_sheaf().scheme()

    def numerator_sheaf(self):
        r"""The sheaf ``K_X^*``."""
        return self._numerator_sheaf

    def denominator_sheaf(self):
        r"""The subsheaf ``O_X^*``."""
        return self._denominator_sheaf

    @cached_method
    def global_sections(self):
        r"""Return ``Gamma(X, K_X^*/O_X^*) = CDiv(X)``."""
        return CartierDivisorGroups()(self)

    def _repr_(self):
        return f"Cartier quotient sheaf K^*/O^* on {self.scheme()}"


class _CartierDivisorSectionsPresheaf(Functor):
    r"""``U |-> CDiv(U)`` on whole, empty and represented affine opens.

    This is the quotient *sheaf* ``K^*/O^*`` (Stacks, Tag 02AQ), not the
    quotient of the two groups of global units. Local lifts are restricted
    on their presentation atlas; another presentation needs a common
    refinement before its local equation can be computed.

    Unexecuted projective-line chart restriction (Stacks, Tag 02AQ)::

        sage: from dzack_research.preamble.all import *
        sage: X = ProjectiveSpaces(QQ)(1)
        sage: atlas = X.standard_affine_atlas()
        sage: A = atlas.chart(0).coordinate_algebra()
        sage: B = atlas.chart(1).coordinate_algebra()
        sage: y = next(iter(B.algebra_generators()))
        sage: divisors = CartierDivisorGroups().of_scheme(X)
        sage: D = divisors.finite_atlas_section(atlas, {0: A.one(), 1: y})
        sage: sheaf = divisors.quotient_sheaf()
        sage: whole = sheaf.descent_data().coverage().whole_open()
        sage: sheaf.sections(whole) is divisors
        True
        sage: site = X.open_subsets_site(); opposite = site.opposite()
        sage: chart = site(atlas.chart_open_subset(1))
        sage: arrow = opposite.Mor(opposite(whole), opposite(chart))(site.Mor(chart, whole)())
        sage: local = sheaf.open_sections_presheaf().on_morphism(arrow)(D)
        sage: local == sheaf.sections(chart).principal_divisor(y)
        True
        sage: overlap = site(atlas.chart_open_subset(0, atlas.overlap(0, 1)))
        sage: restriction = opposite.Mor(opposite(chart), opposite(overlap))(site.Mor(overlap, chart)())
        sage: sheaf.open_sections_presheaf().on_morphism(restriction)(local) == sheaf.sections(overlap).zero()
        True
    """

    def __init__(self, scheme, quotient_sheaf):
        from sage_extensions.categories.modules.pure.modules import Modules

        self._scheme = scheme
        self._quotient_sheaf = quotient_sheaf
        super().__init__(scheme.open_subsets_site().opposite(), Modules(_integers()))

    def _is_whole(self, open_object):
        opens = self.domain().base_category().object_set()
        return open_object.underlying_object().value() is opens.inclusion().codomain().top()

    def _basis(self, open_object):
        from sage_extensions.categories.rings.commutative_algebra import DistinguishedOpenSubobjects
        from sage_extensions.categories.schemes.schemes import Schemes

        subset = open_object.underlying_object().value()
        if self._scheme in Schemes(self._scheme.scheme_base_ring()).Affine():
            assert subset in DistinguishedOpenSubobjects(self._scheme.underlying_space()), (
                "Cartier sections require an affine distinguished-open presentation"
            )
            atlas = FiniteAffineAtlases(self._scheme).identity_atlas()
            return atlas, 0, self._scheme.distinguished_open(subset.function())
        atlas = self._scheme.selected_finite_affine_atlas()
        assert subset in _AffineChartOpenSubobjects(self._scheme) and subset.gluing_datum() is atlas.presentation(), (
            "Cartier sections require a basis open of the selected affine atlas"
        )
        return atlas, subset.chart_index(), subset.chart_open()

    def _apply_object(self, open_object):
        if _is_empty_open(self, open_object):
            return _integers().free_module(0)
        if self._is_whole(open_object):
            return self._quotient_sheaf().global_sections()
        _atlas, _index, selected = self._basis(open_object)
        return CartierDivisorGroups().of_scheme(selected)

    def _apply_morphism(self, arrow):
        source = self(arrow.domain())
        target = self(arrow.codomain())
        if _is_empty_open(self, arrow.domain()) or _is_empty_open(self, arrow.codomain()):
            return self.codomain().Mor(source, target).zero()
        if arrow.domain() is arrow.codomain() or (self._is_whole(arrow.domain()) and self._is_whole(arrow.codomain())):
            return self.codomain().Mor(source, target).identity()
        if self._is_whole(arrow.domain()):
            atlas, index, selected = self._basis(arrow.codomain())
            if atlas.scheme() is atlas.chart(index):
                return source.restriction_map(selected.inclusion())
            return source.restriction_to_chart(atlas, index, selected)
        atlas, source_index, source_open = self._basis(arrow.domain())
        if not self._is_whole(arrow.codomain()):
            target_atlas, target_index, target_open = self._basis(arrow.codomain())
            assert target_atlas is atlas, "Cartier restriction between atlases requires their comparison"
            scalar_map = atlas.basis_coordinate_restriction(source_index, source_open, target_index, target_open)
            from sage_extensions.categories.schemes.schemes import Schemes

            open_map = Schemes(self._scheme.scheme_base_ring()).Mor(target_open, source_open)(scalar_map)
            # The open-site arrow and its basis comparison give this open
            # immersion, including cross-chart coordinate changes.
            return self.codomain().Mor(source, target)._from_constructed_element_map(
                lambda divisor: source(divisor).underlying_element()._restrict_to_affine_open(open_map, target),
            )

        source_atlas = FiniteAffineAtlases(source_open).identity_atlas()

        def restrict(divisor):
            equation = source(divisor).underlying_element()._equation_on_chart(source_atlas, 0)
            equations = {
                index: _total_quotient_pullback(
                    atlas.basis_coordinate_restriction(source_index, source_open, index, atlas.chart(index)),
                    equation,
                )
                for index in atlas.chart_indices()
            }
            return target.finite_atlas_section(atlas, equations)

        return self.codomain().Mor(source, target)._from_constructed_element_map(restrict)


@cached_function(key=lambda scheme: id(scheme))
def _total_quotient_sheaf(scheme):
    sheaves = SheafObjects(scheme)
    fibre, presheaf_data = _open_sheaf_placement(
        scheme,
        _TotalQuotientSectionsPresheaf(scheme),
    )
    return _object_of(
        owned_category_join((sheaves, fibre)),
        _engine=(fibre, _TotalQuotientSheafEngine, None),
        **presheaf_data,
        scheme=scheme,
    )


@cached_function(key=lambda ring_sheaf: id(ring_sheaf))
def _unit_sheaf(ring_sheaf):
    sheaves = SheafObjects(ring_sheaf.scheme())
    fibre, presheaf_data = _open_sheaf_placement(
        ring_sheaf.scheme(),
        _UnitSectionsPresheaf(ring_sheaf.open_sections_presheaf()),
    )
    return _object_of(
        owned_category_join((sheaves, fibre)),
        _engine=(fibre, _UnitSheafEngine, None),
        **presheaf_data,
        ring_sheaf=ring_sheaf,
    )


@cached_function(key=lambda scheme: id(scheme))
def _regular_unit_sheaf(scheme):
    sheaves = SheafObjects(scheme)
    fibre, presheaf_data = _open_sheaf_placement(
        scheme,
        _UnitSectionsPresheaf(scheme.structure_sheaf().open_sections_presheaf()),
    )
    return _object_of(
        owned_category_join((sheaves, fibre)),
        _engine=(fibre, _RegularUnitSheafEngine, None),
        **presheaf_data,
        scheme=scheme,
    )


@cached_function(key=lambda scheme: id(scheme))
def _cartier_divisor_quotient_sheaf(scheme):
    r"""Return the represented quotient sheaf ``K_X^*/O_X^*``."""
    sheaves = SheafObjects(scheme)
    total_quotient_units = _unit_sheaf(_total_quotient_sheaf(scheme))
    regular_units = _regular_unit_sheaf(scheme)
    presheaf = _CartierDivisorSectionsPresheaf(scheme, lambda: sheaf)
    fibre, presheaf_data = _open_sheaf_placement(scheme, presheaf)
    sheaf = _object_of(
        owned_category_join((sheaves, fibre)),
        _engine=(fibre, _CartierDivisorQuotientSheafEngine, None),
        **presheaf_data,
        numerator_sheaf=total_quotient_units,
        denominator_sheaf=regular_units,
    )
    return sheaf


def _total_quotient_pullback(ring_morphism, rational_section):
    r"""Pull a represented total-quotient section along an affine open map.

    The currently represented finite-atlas computation uses a localization
    realization of the source total quotient ring.  The public Cartier group
    is not restricted by this computational case; this is only the adapter
    used to verify one finite-atlas lift.
    """
    source = ring_morphism.domain()
    target = ring_morphism.codomain()
    source_total = source.total_quotient_ring()
    target_total = target.total_quotient_ring()
    rational_section = source_total(rational_section)
    if source_total is source:
        return target_total(ring_morphism(rational_section))
    match source_total in LocalizationRings():
        case True:
            target_map = target.total_quotient_map()
            numerator = target_map(ring_morphism(source(rational_section.numerator())))
            denominator = target_map(
                ring_morphism(source(rational_section.denominator()))
            )
            assert denominator.is_unit(), (
                f"cannot restrict the rational function {rational_section} along {ring_morphism}: its "
                f"denominator maps to {denominator}, which is not a unit of {target_total}"
            )
            return target_total(numerator * denominator.inverse_of_unit())
        case False:
            raise AssertionError(
                f"cannot restrict the rational function {rational_section} along {ring_morphism}: "
                f"restriction is implemented only when the total quotient ring {source_total} "
                f"is a localization of {source}"
            )


def _regular_unit_ratio(ring, left, right):
    r"""Whether ``left/right`` is represented by a unit of ``ring``."""
    total = ring.total_quotient_ring()
    ratio = total(left) * total(right).inverse_of_unit()
    match ratio in ring:
        case True:
            return ring(ratio).is_unit()
        case False:
            return False


class _CartierSectionClass:
    r"""One class in ``Gamma(X,K_X^*/O_X^*)`` with a represented expression."""

    def __init__(
        self,
        parent,
        kind,
        *,
        atlas=None,
        local_equations=None,
        transition_units=None,
        left=None,
        right=None,
        operand=None,
        scalar=None,
    ) -> None:
        self._kind = kind
        self._atlas = atlas
        self._local_equations = local_equations
        self._transition_units = transition_units
        self._left = left
        self._right = right
        self._operand = operand
        self._scalar = scalar
        super().__init__(parent)

    def is_finite_atlas_presentation(self):
        return self._kind == "finite_atlas"

    def gluing_datum(self):
        assert self.is_finite_atlas_presentation(), (
            f"{self} has no gluing data on a finite affine atlas: it was built from other "
            "Cartier divisors by a group operation, not from local equations on an atlas"
        )
        return self._atlas

    def local_equation(self, index):
        atlas = self.gluing_datum()
        return self._local_equations[atlas.normalize_chart_index(index)]

    def _equation_on_chart(self, atlas, index):
        r"""A local lift of this expression on a chart of its given atlas.

        The quotient map ``K^* -> K^*/O^*`` is a group homomorphism:
        addition, negation and integer multiplication lift to product,
        inverse and powers of equations (Stacks, Tag 02AQ). Different
        presentation atlases require a common refinement.
        """
        ring = atlas.chart(index).coordinate_algebra().total_quotient_ring()
        match self._kind:
            case "zero":
                return ring.one()
            case "finite_atlas":
                assert self._atlas is atlas, (
                    "a Cartier local equation on another atlas requires a common refinement"
                )
                return self.local_equation(index)
            case "sum":
                return self._left._equation_on_chart(atlas, index) * self._right._equation_on_chart(atlas, index)
            case "negation":
                return self._operand._equation_on_chart(atlas, index).inverse_of_unit()
            case "multiple":
                return self._operand._equation_on_chart(atlas, index) ** int(self._scalar)
        raise ValueError(f"unrecognized Cartier section expression: {self._kind}")

    def _restrict_to_affine_open(self, morphism, target):
        r"""Restrict along the supplied open map using the whole local cover.

        The Cartier group restriction constructor and the open-site
        sections functor supply the open immersion. Pulling the atlas back
        retains nonprincipal divisors: no global meromorphic lift is chosen
        (Stacks, Tags 02AQ and 01JY).
        """
        match self._kind:
            case "zero":
                return target.zero()
            case "finite_atlas":
                pulled = self._atlas.pullback(morphism)
                equations = {
                    index: _total_quotient_pullback(
                        pulled.chart(index).left_projection().coordinate_algebra_morphism(),
                        self.local_equation(index),
                    )
                    for index in pulled.chart_indices()
                }
                return target.finite_atlas_section(pulled, equations)
            case "sum":
                return self._left._restrict_to_affine_open(morphism, target) + self._right._restrict_to_affine_open(morphism, target)
            case "negation":
                return -self._operand._restrict_to_affine_open(morphism, target)
            case "multiple":
                return self._scalar * self._operand._restrict_to_affine_open(morphism, target)
        raise ValueError(f"unrecognized Cartier section expression: {self._kind}")

    def _local_equation_terms(self, coefficient=1):
        r"""Expand the group expression as signed local-equation lifts."""
        match self._kind:
            case "zero":
                return
            case "finite_atlas":
                yield self, coefficient
            case "sum":
                yield from self._left._local_equation_terms(coefficient)
                yield from self._right._local_equation_terms(coefficient)
            case "negation":
                yield from self._operand._local_equation_terms(-coefficient)
            case "multiple":
                yield from self._operand._local_equation_terms(coefficient * int(self._scalar))
            case _:
                raise ValueError(f"unrecognized Cartier section expression: {self._kind}")

    def transition_unit(self, source_index, target_index):
        atlas = self.gluing_datum()
        source_index = atlas.normalize_chart_index(source_index)
        target_index = atlas.normalize_chart_index(target_index)
        pair = next(
            pair
            for pair in atlas.transition_index_set()
            if {pair[0], pair[1]} == {source_index, target_index}
        )
        unit = self._transition_units[pair]
        match pair == (source_index, target_index):
            case True:
                return unit
            case False:
                reverse = atlas.transition_between(source_index, target_index).forward()
                return reverse.coordinate_algebra_morphism()(unit.inverse_of_unit())

    def _richcmp_(self, other, op):
        match op in (op_EQ, op_NE):
            case False:
                return NotImplemented
            case True:
                pass
        match element_parent(other) is self.parent():
            case False:
                return op == op_NE
            case True:
                pass
        decision = self.parent().equal(self, other)
        return decision if op == op_EQ else negation(decision)

    __hash__ = None

    def _repr_(self):
        match self._kind:
            case "zero":
                return "0"
            case "finite_atlas":
                return (
                    f"Cartier section on {self.parent().scheme()} "
                    "from finite-atlas local equations"
                )
            case "sum":
                return f"({self._left}) + ({self._right})"
            case "negation":
                return f"-({self._operand})"
            case "multiple":
                return f"{self._scalar}*({self._operand})"


class _CartierSectionClasses:
    r"""The underlying set of global Cartier-quotient sections.

    Finite-atlas lifts are identified when their local equations differ by
    regular units on a common cover. For an affine scheme, intersections
    are computed by the affine fibre products of chart embeddings. Over a
    nonaffine scheme a common refinement remains required.
    """

    def __init__(self, quotient_sheaf, **rest) -> None:
        self._quotient_sheaf = quotient_sheaf
        super().__init__(**rest)

    def quotient_sheaf(self):
        return self._quotient_sheaf

    def scheme(self):
        return self.quotient_sheaf().scheme()

    def __contains__(self, value):
        return element_parent(value) is self

    def __call__(self, value):
        match element_parent(value) is self:
            case True:
                return value
            case False:
                raise TypeError(
                    f"{value} is not a global section of {self.quotient_sheaf()}, "
                    f"so it is not a Cartier divisor on {self.scheme()}"
                )

    @cached_method
    def zero(self):
        return self.element_class(self, "zero")

    def finite_atlas(self, atlas, local_equations):
        match atlas in FiniteAffineAtlases(self.scheme()):
            case True:
                pass
            case False:
                raise TypeError(
                    f"cannot define a Cartier divisor on {self.scheme()} from local equations on {atlas}: "
                    "the charts must form a finite affine atlas of that scheme"
                )
        supplied = dict(local_equations)
        assert set(supplied) == set(atlas.chart_indices()), (
            f"a Cartier divisor on {self.scheme()} needs exactly one local equation per chart of "
            f"{atlas}: the charts are indexed by {set(atlas.chart_indices())}, but equations "
            f"were given for {set(supplied)}"
        )
        equations = {}
        for index in atlas.chart_indices():
            ring = atlas.chart(index).coordinate_algebra()
            assert ring in OwnedNoetherianRings(), (
                f"cannot compute K_X on chart {index} of {atlas}: the total-quotient-ring formula is "
                f"implemented only for Noetherian coordinate rings, but {ring} is not known to "
                "be Noetherian"
            )
            total = self.quotient_sheaf().numerator_sheaf().ring_sheaf().sections_on_affine(
                atlas.chart(index)
            )
            equation = total(supplied[index])
            assert equation.is_unit(), (
                f"the local equation {equation} on chart {index} of {atlas} is not a unit of the "
                f"total quotient ring {total}, so it does not define a Cartier divisor"
            )
            equations[index] = equation
        equations = finite_indexed_family(
            atlas.chart_index_set(),
            equations.__getitem__,
            name="Finite-atlas Cartier local equations",
        )
        transitions = {
            pair: self._transition_unit(atlas, equations, *pair)
            for pair in atlas.transition_index_set()
        }
        return self.element_class(
            self,
            "finite_atlas",
            atlas=atlas,
            local_equations=equations,
            transition_units=transitions,
        )

    def _restricted_equation(self, atlas, equations, source_index, target_index):
        overlap = atlas.overlap(source_index, target_index)
        restriction = overlap.inclusion().coordinate_algebra_morphism()
        return _total_quotient_pullback(restriction, equations[source_index])

    def _transition_unit(self, atlas, equations, source_index, target_index):
        source_equation = self._restricted_equation(
            atlas,
            equations,
            source_index,
            target_index,
        )
        target_equation = self._restricted_equation(
            atlas,
            equations,
            target_index,
            source_index,
        )
        transition = atlas.transition_between(source_index, target_index).forward()
        target_on_source = _total_quotient_pullback(
            transition.coordinate_algebra_morphism(),
            target_equation,
        )
        overlap_ring = atlas.overlap(source_index, target_index).coordinate_algebra()
        overlap_total = overlap_ring.total_quotient_ring()
        ratio = overlap_total(source_equation) * overlap_total(
            target_on_source
        ).inverse_of_unit()
        assert ratio in overlap_ring, (
            f"the local equations on charts {source_index} and {target_index} of {atlas} do not "
            f"agree up to a regular function on their overlap: their ratio {ratio} does not "
            f"lie in {overlap_ring}"
        )
        unit = overlap_ring(ratio)
        assert unit.is_unit(), (
            f"the local equations on charts {source_index} and {target_index} of {atlas} do not "
            f"agree up to a unit on their overlap: their ratio {unit} is not a unit of "
            f"{overlap_ring}"
        )
        return unit

    def add(self, left, right):
        left = self(left)
        right = self(right)
        match (left._kind, right._kind):
            case ("zero", _):
                return right
            case (_, "zero"):
                return left
            case ("finite_atlas", "finite_atlas") if left._atlas is right._atlas:
                atlas = left._atlas
                equations = {
                    index: left.local_equation(index) * right.local_equation(index)
                    for index in atlas.chart_indices()
                }
                return self.finite_atlas(atlas, equations)
            case _:
                return self.element_class(self, "sum", left=left, right=right)

    def negate(self, value):
        value = self(value)
        match value._kind:
            case "zero":
                return value
            case "finite_atlas":
                atlas = value._atlas
                return self.finite_atlas(
                    atlas,
                    {
                        index: value.local_equation(index).inverse_of_unit()
                        for index in atlas.chart_indices()
                    },
                )
            case "negation":
                return value._operand
            case _:
                return self.element_class(self, "negation", operand=value)

    def scale(self, scalar, value):
        scalar = _integers()(scalar)
        value = self(value)
        exponent = int(scalar)
        match exponent:
            case 0:
                return self.zero()
            case 1:
                return value
            case _ if value._kind == "finite_atlas":
                atlas = value._atlas
                return self.finite_atlas(
                    atlas,
                    {
                        index: value.local_equation(index) ** exponent
                        for index in atlas.chart_indices()
                    },
                )
            case _:
                return self.element_class(
                    self,
                    "multiple",
                    operand=value,
                    scalar=scalar,
                )

    def _finite_atlas_is_zero(self, value):
        atlas = value._atlas
        return conjunction(
            _regular_unit_ratio(
                atlas.chart(index).coordinate_algebra(),
                value.local_equation(index),
                atlas.chart(index).coordinate_algebra().one(),
            )
            for index in atlas.chart_indices()
        )

    def _same_atlas_equal(self, left, right):
        atlas = left._atlas
        return conjunction(
            _regular_unit_ratio(
                atlas.chart(index).coordinate_algebra(),
                left.local_equation(index),
                right.local_equation(index),
            )
            for index in atlas.chart_indices()
        )

    def _affine_common_refinement_equal(self, left, right):
        r"""Compare expressions on the common cover of their local lifts.

        The iterated affine intersections cover ``X``. Equality in ``K^*/O^*``
        is local, so the two sections agree exactly when every ratio is a
        regular unit (Stacks, Tag 02AQ). The affine pullbacks retain both
        coordinate maps; no local equation is identified across parents.

        Unexecuted comparison of distinct affine presentations::

            sage: from dzack_research.preamble.all import *
            sage: A = QQ['x']; x = A.algebra_generator('x')
            sage: X = AffineSchemes(QQ)(A)
            sage: divisors = CartierDivisorGroups().of_scheme(X)
            sage: D = divisors.principal_divisor(x)
            sage: identity = X.categorical_identity_morphism()
            sage: E = divisors.restriction_map(identity)(D)
            sage: E.gluing_datum() is D.gluing_datum()
            False
            sage: E == D
            True
            sage: E == divisors.principal_divisor(x*x)
            False
            sage: F = divisors.restriction_map(identity)(divisors.principal_divisor(x-A.one()))
            sage: D + F == F + D
            True
            sage: (D + F) + D == 2*D + F
            True
        """
        from sage_extensions.categories.schemes.schemes import Schemes

        schemes = Schemes(self.scheme().scheme_base_ring())

        terms = (*left._local_equation_terms(), *right._local_equation_terms(-1))
        atlases = []
        for section, _coefficient in terms:
            if not any(atlas is section._atlas for atlas in atlases):
                atlases.append(section._atlas)
        if not atlases:
            return True

        def agree(position, chart, chart_to_scheme, indices, projections):
            if position == len(atlases):
                ring = chart.coordinate_algebra()
                product = ring.total_quotient_ring().one()
                for section, coefficient in terms:
                    atlas_index = next(index for index, atlas in enumerate(atlases) if atlas is section._atlas)
                    equation = _total_quotient_pullback(
                        projections[atlas_index].coordinate_algebra_morphism(),
                        section.local_equation(indices[atlas_index]),
                    )
                    product *= equation ** coefficient
                return _regular_unit_ratio(ring, product, ring.one())

            atlas = atlases[position]

            def next_chart(index):
                intersection = schemes.fiber_product(chart_to_scheme, atlas.chart_embedding(index))
                left_projection = intersection.left_projection()
                return agree(
                    position + 1, intersection, chart_to_scheme * left_projection,
                    (*indices, index),
                    (*tuple(projection * left_projection for projection in projections), intersection.right_projection()),
                )

            return conjunction(next_chart(index) for index in atlas.chart_indices())

        first = atlases[0]
        return conjunction(
            agree(1, first.chart(index), first.chart_embedding(index), (index,),
                  (first.chart(index).categorical_identity_morphism(),))
            for index in first.chart_indices()
        )

    def equal(self, left, right):
        r"""Decide ``D = E``, else return the proposition ``equal(D, E)``.

        Equal summands, or equal operands of the same multiple, give equal
        sections; the converse fails (``D + E = E + D``, and the group of
        Cartier divisors of a non-normal scheme can have torsion), so only a
        positive answer is drawn from them.
        """
        left = self(left)
        right = self(right)
        from sage_extensions.categories.schemes.schemes import Schemes

        match (left._kind, right._kind):
            case _ if left is right:
                return True
            case ("zero", "zero"):
                return True
            case ("zero", "finite_atlas"):
                return self._finite_atlas_is_zero(right)
            case ("finite_atlas", "zero"):
                return self._finite_atlas_is_zero(left)
            case ("finite_atlas", "finite_atlas") if left._atlas is right._atlas:
                return self._same_atlas_equal(left, right)
            case ("finite_atlas", "finite_atlas") if self.scheme() in Schemes(self.scheme().scheme_base_ring()).Affine():
                return self._affine_common_refinement_equal(left, right)
            case ("sum", "sum") if (
                self.equal(left._left, right._left) is True
                and self.equal(left._right, right._right) is True
            ):
                return True
            case ("negation", "negation"):
                return self.equal(left._operand, right._operand)
            case ("multiple", "multiple") if (
                left._scalar == right._scalar
                and self.equal(left._operand, right._operand) is True
            ):
                return True
            case _ if self.scheme() in Schemes(self.scheme().scheme_base_ring()).Affine():
                return self._affine_common_refinement_equal(left, right)
            case _:
                return AtomicProposition("equal", left, right)

    def _repr_(self):
        return f"Global sections of {self.quotient_sheaf()}"


@cached_function(key=lambda quotient_sheaf: id(quotient_sheaf))
def _cartier_section_classes(quotient_sheaf):
    return _object_of(
        Sets(),
        _engine=(Sets(), _CartierSectionClasses, _CartierSectionClass),
        quotient_sheaf=quotient_sheaf,
    )


class CartierDivisorGroups(Category):
    r"""The groups ``CDiv(X)=Gamma(X,K_X^*/O_X^*)`` of Cartier divisors.

    The defining datum of an object is the quotient sheaf
    ``K_X^*/O_X^*``.  Since every abelian group is canonically a ``ZZ``-module,
    the group is represented through ``GeneralModules(ZZ)`` without choosing a
    framing or presentation.

    Unverified specimen: a finite-atlas local equation is an element of the
    one owned Cartier divisor group::

        sage: from dzack_research.preamble.all import QQ, ProjectiveSpaces
        sage: line = ProjectiveSpaces(QQ)(1)
        sage: atlas = line.standard_affine_atlas()
        sage: left = atlas.chart(0).coordinate_algebra()
        sage: right = atlas.chart(1).coordinate_algebra()
        sage: x0_over_x1 = right.algebra_generator("x0_over_x1")
        sage: cartier = CartierDivisorGroups().of_scheme(line)
        sage: point = cartier.finite_atlas_section(
        ....:     atlas, {0: left.one(), 1: x0_over_x1}
        ....: )
        sage: point in cartier
        True
        sage: point.parent() is cartier
        True
        sage: cartier.quotient_sheaf().global_sections() is cartier
        True
    """

    @classmethod
    def _repr_object_names(cls):
        return "Cartier divisor groups"

    def super_categories(self):
        return [GeneralModules(_integers())]

    def an_object(self):
        from sage_extensions.categories.divisors.divisor_groups import (
            _affine_line_over_rationals,
        )

        return self.of_scheme(_affine_line_over_rationals())

    def of_scheme(self, scheme):
        r"""Return ``CDiv(X)`` for ``scheme = X``."""
        return _cartier_divisor_quotient_sheaf(scheme).global_sections()

    def _call_(self, quotient_sheaf):
        r"""Construct the global-section group of ``K_X^*/O_X^*``."""
        scheme = quotient_sheaf.scheme()
        assert quotient_sheaf is _cartier_divisor_quotient_sheaf(scheme), (
            f"cannot construct CDiv({scheme}) from {quotient_sheaf}: the Cartier divisor group is "
            f"the group of global sections of K_X^*/O_X^* on {scheme}, and {quotient_sheaf} "
            "is a different sheaf"
        )
        sections = _cartier_section_classes(quotient_sheaf)
        return _object_of(
            self,
            cartier_divisor_sheaf=quotient_sheaf,
            base_ring=_integers(),
            underlying_set=sections,
            addition=sections.add,
            zero=sections.zero(),
            negation=sections.negate,
            scalar_action=sections.scale,
        )

    class ParentMethods:
        def __init__(self, cartier_divisor_sheaf, **rest) -> None:
            self._cartier_divisor_sheaf = cartier_divisor_sheaf
            super().__init__(**rest)

        def quotient_sheaf(self):
            r"""The sheaf ``K_X^*/O_X^*`` whose global sections form this group."""
            return self._cartier_divisor_sheaf

        def divisor_scheme(self):
            r"""The scheme ``X`` in ``CDiv(X)``."""
            return self.quotient_sheaf().scheme()

        def finite_atlas_section(self, atlas, local_equations):
            r"""Construct the section represented by ``(U_i,f_i)`` on ``atlas``."""
            section = self.underlying_set().finite_atlas(atlas, local_equations)
            return self(section)

        def principal_divisor(self, rational_function):
            r"""The Cartier divisor with the single local equation ``f``.

            Here the scheme is affine and ``f`` must be a unit of its total
            quotient ring. The equation on the identity atlas is its image
            in ``K_X^*/O_X^*`` (Stacks, Tag 02AQ). Thus a regular unit gives
            zero, and multiplication of equations gives addition of divisors.

            Unexecuted affine-line assertions::

                sage: from dzack_research.preamble.all import *
                sage: A = QQ['x']; x = A.algebra_generator('x')
                sage: X = AffineSchemes(QQ)(A)
                sage: divisors = CartierDivisorGroups().of_scheme(X)
                sage: D = divisors.principal_divisor(x)
                sage: D + D == divisors.principal_divisor(x*x)
                True
                sage: divisors.principal_divisor(A.one()) == divisors.zero()
                True
                sage: D + divisors.principal_divisor(A.total_quotient_ring()(x).inverse_of_unit()) == divisors.zero()
                True
            """
            atlas = FiniteAffineAtlases(self.divisor_scheme()).identity_atlas()
            return self.finite_atlas_section(atlas, {0: rational_function})

        def restriction_to_chart(self, atlas, index, open_subscheme=None):
            r"""Restrict a Cartier section to an affine chart or its ``D(f)``.

            Local equations restrict through the retained coordinate map;
            regular unit ratios remain units. Hence the map descends to
            ``K^*/O^*`` and is ``ZZ``-linear (Stacks, Tag 02AQ).
            Computing a lift presented on a different atlas requires its
            common refinement with ``atlas``.
            """
            from sage_extensions.categories.modules.pure.modules import Modules
            from sage_extensions.categories.schemes.schemes import OpenImmersions

            if atlas not in FiniteAffineAtlases(self.divisor_scheme()):
                raise ValueError("Cartier restriction requires an atlas of the divisor's scheme")
            index = atlas.normalize_chart_index(index)
            chart = atlas.chart(index)
            selected = chart if open_subscheme is None else open_subscheme
            if selected is not chart:
                assert selected in OpenImmersions(chart) and selected.is_distinguished_open() is True, (
                    "Cartier chart restriction requires the chart or one of its distinguished opens"
                )
            target = CartierDivisorGroups().of_scheme(selected)

            def restrict(divisor):
                equation = self(divisor).underlying_element()._equation_on_chart(atlas, index)
                if selected is not chart:
                    equation = _total_quotient_pullback(selected.inclusion().coordinate_algebra_morphism(), equation)
                return target.principal_divisor(equation)

            return Modules(_integers()).Mor(self, target)._from_constructed_element_map(restrict)

        def restriction_map(self, open_immersion):
            r"""``CDiv(X) -> CDiv(U)`` for a represented affine open map.

            Pull back every local equation on its pulled-back covering
            atlas, with no principal-divisor hypothesis (Stacks, 02AQ).

            Unexecuted local-equation restriction::

                sage: from dzack_research.preamble.all import *
                sage: A = QQ['x']; x = A.algebra_generator('x')
                sage: X = AffineSchemes(QQ)(A); U = X.distinguished_open(x)
                sage: divisors = CartierDivisorGroups().of_scheme(X)
                sage: D = divisors.principal_divisor(x)
                sage: restricted = divisors.restriction_map(U.inclusion())(D)
                sage: pulled = D.gluing_datum().pullback(U.inclusion())
                sage: restricted.gluing_datum() is pulled
                True
                sage: projection = pulled.chart(0).left_projection().coordinate_algebra_morphism()
                sage: expected = pulled.chart(0).coordinate_algebra().total_quotient_ring()(projection(x))
                sage: restricted.local_equation(0) == expected
                True
                sage: restricted == restricted.parent().zero()
                True
            """
            from sage_extensions.categories.modules.pure.modules import Modules

            if open_immersion.codomain() is not self.divisor_scheme():
                raise ValueError("Cartier restriction requires an open map into the divisor scheme")
            assert open_immersion.is_open_immersion() is True, (
                "Cartier restriction requires an established open immersion"
            )
            target = CartierDivisorGroups().of_scheme(open_immersion.domain())
            return Modules(_integers()).Mor(self, target)._from_constructed_element_map(
                lambda divisor: self(divisor).underlying_element()._restrict_to_affine_open(open_immersion, target),
            )

    class ElementMethods:
        def gluing_datum(self):
            r"""The finite atlas of this represented local-equation lift."""
            return self.underlying_element().gluing_datum()

        def local_equation(self, index):
            r"""The chosen local lift ``f_i`` on one chart."""
            return self.underlying_element().local_equation(index)

        def transition_unit(self, source_index, target_index):
            r"""The regular unit ``f_i/f_j`` on the selected overlap."""
            return self.underlying_element().transition_unit(source_index, target_index)

        def associated_invertible_sheaf(self):
            r"""Return ``O_X(D)`` from the transition units of this finite-atlas lift."""
            from sage_extensions.categories.divisors.invertible_sheaves import (
                _finite_atlas_invertible_sheaf,
            )

            atlas = self.gluing_datum()
            units = {
                pair: self.transition_unit(*pair)
                for pair in atlas.transition_index_set()
            }
            return _finite_atlas_invertible_sheaf(
                atlas,
                units,
                associated_divisor=self,
            )

        line_bundle = associated_invertible_sheaf


__all__ = ["CartierDivisorGroups"]
