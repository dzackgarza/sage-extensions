r"""Owned topological, finite-``C^k`` and smooth manifolds and atlas maps.

SageManifolds is the private chart/transition engine.  The public object keeps
the manifold's dimension and differentiability degree, an owned finite family
of labelled charts, and exact forward/inverse coordinate expressions for each
represented atlas transition.
"""

from functools import partial
from itertools import combinations

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.combinat.root_system.coxeter_group import CoxeterGroup
from sage.combinat.root_system.coxeter_matrix import CoxeterMatrix
from sage.matrix.constructor import matrix as _engine_matrix
from sage.matrix.special import identity_matrix as _engine_identity_matrix
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_import import lazy_import
from sage.rings.infinity import Infinity
from sage.rings.qqbar import QQbar as SageQQbar
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject
from sage.symbolic.ring import SR

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
    _owned_complex_field,
    _owned_engine_element,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import NN, OwnedSetMorphism, Sets
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.logic import ask
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import CategoryWithAxiom
lazy_import("sage_extensions.rings.real", "RR")
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

lazy_import("sage.manifolds.manifold", "Manifold", as_="_SageManifold")

for _manifold_axiom in ("GloballySymmetric", "BoundedSymmetric"):
    if _manifold_axiom not in all_axioms:
        all_axioms.add(_manifold_axiom)


class ManifoldAtlasChart(SageObject):
    r"""One labelled chart of an owned manifold.

    A chart ``phi : U -> RR^n`` is a homeomorphism of an open subset ``U`` of
    the manifold onto an open subset of ``RR^n`` (Lee, *Introduction to Smooth
    Manifolds*, 2nd ed., Ch. 1).  Its coordinates are therefore real-valued
    functions on ``U``: each is retained as a section of the ring of functions
    the manifold assigns to that domain, and evaluating one at a point of the
    domain gives the point's coordinate, an element of the coordinate field.
    """

    def __init__(self, manifold, label, engine_chart, domain, nonvanishing=()) -> None:
        self._manifold = manifold
        self._label = label
        self._engine = engine_chart
        self._domain = domain
        self._function_ring = _manifold_function_ring(domain, manifold)
        self._nonvanishing = tuple(
            _raise_manifold_expression(_engine_manifold_expression(condition), self)
            for condition in nonvanishing
        )
        field = manifold.coordinate_field()
        self._coordinates = finite_family(
            tuple(
                self._function_ring(_ChartCoordinate(engine_chart, index, field))
                for index in range(int(manifold.dimension()))
            ),
            name=f"Coordinates of chart {label}",
        )

    def manifold(self):
        return self._manifold

    def label(self):
        return self._label

    def __hash__(self):
        r"""A chart is identified by the manifold it charts and the label it is registered under.

        No two charts of one manifold share a label (``_register_chart``
        refuses the second one), so the pair identifies the chart and a family
        of charts, such as an atlas, can be indexed by the chart itself.
        """
        return hash((id(self._manifold), self._label))

    def domain(self):
        r"""The open subset of the manifold the chart is defined on."""
        return self._domain

    def nonvanishing(self):
        r"""The functions on this chart whose common nonvanishing locus is its domain.

        A chart read on a proper open subset of the manifold -- a chart cut by
        conditions, or an ambient chart restricted to an open submanifold -- is
        stated there where these functions do not vanish, and the subset they cut
        out in this chart's coordinates is exactly the chart's domain (Lee,
        *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1, for the chart's open
        set).  An empty family states that the chart is read on the whole set its
        coordinates reach; it does not state the opposite.
        """
        return self._nonvanishing

    def function_ring(self):
        r"""The owned ring of real-valued functions on the chart's domain.

        A chart coordinate is a section of this ring, and the ring's elements
        are the functions on the chart's domain the manifold assigns there.
        """
        return self._function_ring

    def coordinates(self):
        return self._coordinates

    def coordinate(self, index):
        position = self.coordinates().index_set()[int(index)]
        return self.coordinates()[position]

    def section_ratio(self, numerator, denominator):
        r"""The quotient of two sections of this chart's function ring, on the open subset where the denominator does not vanish.

        The ring of functions on the chart's domain has no inverse for a
        section that vanishes somewhere, and a chart change can divide by one:
        the stereographic coordinate change ``y = x/|x|^2`` divides by the
        squared norm, which vanishes at the pole the chart projects from.  The
        quotient ``g/f`` is the function ``p |-> g(p)/f(p)`` on the open subset
        ``{f != 0}`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1),
        and ``f`` is what an atlas transition states as its overlap on this
        chart (:meth:`transition_map`): the quotient is read where its
        denominator does not vanish and nowhere else.
        """
        ring = self.function_ring()
        misplaced = tuple(
            operand
            for operand in (numerator, denominator)
            if element_parent(operand) is not ring
        )
        assert not misplaced, (
            f"a quotient of sections of the chart {self.label()} is written with two "
            f"sections of {ring}, the ring of functions the manifold assigns to that chart's "
            f"domain, and {(numerator, denominator)!r} is written with the elements "
            f"{tuple(str(element_parent(operand)) for operand in misplaced)}"
        )
        return _SectionRatio(numerator, denominator)

    def __call__(self, point):
        r"""The coordinates of ``point`` in this chart, one element of the coordinate field per dimension."""
        selected = self.manifold()(point)
        return finite_family(
            tuple(
                self.coordinate(index)(selected)
                for index in range(int(self.manifold().dimension()))
            ),
            name=f"Coordinates of a point of {self.manifold()} in the chart {self.label()}",
        )

    def _engine_chart(self):
        return self._engine

    def transition_to(self, other, forward_expressions, inverse_expressions):
        return self.manifold().transition_map(
            self.label(),
            other.label(),
            forward_expressions,
            inverse_expressions,
        )

    def _repr_(self):
        return f"Chart {self.label()} of {self.manifold()}"


class ManifoldAtlasTransition(SageObject):
    r"""An invertible atlas coordinate change with retained regularity."""

    def __init__(
        self,
        source,
        target,
        engine_transition,
        forward_expressions,
        inverse_expressions,
        source_overlap,
        target_overlap,
    ) -> None:
        self._source = source
        self._target = target
        self._engine = engine_transition
        self._forward = _admit_manifold_expression_family(
            forward_expressions,
            source,
            name=f"Coordinate change {source.label()} to {target.label()}",
        )
        self._inverse_expressions = _admit_manifold_expression_family(
            inverse_expressions,
            target,
            name=f"Coordinate change {target.label()} to {source.label()}",
        )
        self._source_overlap = _admit_manifold_expression_family(
            source_overlap,
            source,
            name=f"Overlap of {source.label()} with {target.label()} in {source.label()}",
        )
        self._target_overlap = _admit_manifold_expression_family(
            target_overlap,
            target,
            name=f"Overlap of {target.label()} with {source.label()} in {target.label()}",
        )
        self._inverse_transition = None

    def source(self):
        return self._source

    def target(self):
        return self._target

    def manifold(self):
        return self.source().manifold()

    def forward_expressions(self):
        return self._forward

    def inverse_expressions(self):
        return self._inverse_expressions

    def source_overlap(self):
        r"""The functions on the source chart whose common nonvanishing locus is the overlap.

        The coordinate change is defined on the image of ``U_s \cap U_t`` in
        the source chart ``U_s``, the open set where every one of these
        functions is nonzero; the empty family is the whole chart.
        """
        return self._source_overlap

    def target_overlap(self):
        r"""The functions on the target chart whose common nonvanishing locus is the overlap."""
        return self._target_overlap

    def regularity(self):
        return self.manifold().regularity()

    def inverse(self):
        if self._inverse_transition is None:
            inverse = ManifoldAtlasTransition(
                self.target(),
                self.source(),
                self._engine.inverse(),
                self.inverse_expressions(),
                self.forward_expressions(),
                self.target_overlap(),
                self.source_overlap(),
            )
            inverse._inverse_transition = self
            self._inverse_transition = inverse
        return self._inverse_transition

    def then(self, other):
        r"""``other o self``: the coordinate change through the chart both changes go through.

        For ``self`` a change ``U_s -> U_c`` and ``other`` one ``U_c -> U_t``, the
        change ``U_s -> U_t`` through ``U_c`` is
        ``(phi_t o phi_c^{-1}) o (phi_c o phi_s^{-1})`` (Lee, *Introduction to
        Smooth Manifolds*, 2nd ed., Ch. 1): its forward expressions are the
        second's read in the first's source coordinates, and its inverse is the
        first's read in the second's target coordinates.  It is defined where both
        are, so its overlap is its source leg's overlap together with the other
        leg's overlap read through the first, and likewise at the target end.
        """
        from sage.symbolic.ring import SR as _SR

        assert self.target() is other.source(), (
            f"cannot compose {self} with {other}: the first ends at {self.target()} and the "
            f"second starts at {other.source()}, so they go through no common chart"
        )
        source = self.source()
        middle = self.target()
        target = other.target()
        middle_symbols = tuple(_engine_manifold_chart(middle)[:])
        forward_of_self = tuple(
            _SR(_engine_manifold_expression(expression))
            for expression in self.forward_expressions()
        )
        inverse_of_other = tuple(
            _SR(_engine_manifold_expression(expression))
            for expression in other.inverse_expressions()
        )
        forward = tuple(
            _SR(_engine_manifold_expression(expression)).subs(
                dict(zip(middle_symbols, forward_of_self, strict=True))
            )
            for expression in other.forward_expressions()
        )
        inverse = tuple(
            _SR(_engine_manifold_expression(expression)).subs(
                dict(zip(middle_symbols, inverse_of_other, strict=True))
            )
            for expression in self.inverse_expressions()
        )
        source_overlap = tuple(
            _SR(_engine_manifold_expression(expression))
            for expression in self.source_overlap()
        ) + tuple(
            _SR(_engine_manifold_expression(expression)).subs(
                dict(zip(middle_symbols, forward_of_self, strict=True))
            )
            for expression in other.source_overlap()
        )
        target_overlap = tuple(
            _SR(_engine_manifold_expression(expression))
            for expression in other.target_overlap()
        ) + tuple(
            _SR(_engine_manifold_expression(expression)).subs(
                dict(zip(middle_symbols, inverse_of_other, strict=True))
            )
            for expression in self.target_overlap()
        )
        forward_owned = _raise_manifold_expression_family(
            forward,
            source,
            name=f"Coordinate change {source.label()} to {target.label()}",
        )
        inverse_owned = _raise_manifold_expression_family(
            inverse,
            target,
            name=f"Coordinate change {target.label()} to {source.label()}",
        )
        source_overlap_owned = _raise_manifold_expression_family(
            source_overlap,
            source,
            name=f"Overlap of {source.label()} with {target.label()} in {source.label()}",
        )
        target_overlap_owned = _raise_manifold_expression_family(
            target_overlap,
            target,
            name=f"Overlap of {source.label()} with {target.label()} in {target.label()}",
        )
        return ManifoldAtlasTransition(
            source,
            target,
            _engine_manifold_chart(source).transition_map(
                _engine_manifold_chart(target),
                forward,
                restrictions1=_engine_nonvanishing_conditions(source_overlap_owned),
                restrictions2=_engine_nonvanishing_conditions(target_overlap_owned),
            ),
            forward_owned,
            inverse_owned,
            source_overlap_owned,
            target_overlap_owned,
        )

    def __call__(self, *coordinates):
        r"""The coordinates in the target chart of the point of the overlap with these source coordinates.

        The coordinate change is ``phi_t o phi_s^{-1}`` on
        ``phi_s(U_s cap U_t)``: the point of the source chart with the given
        coordinates must lie in the overlap, which the overlap functions
        decide, and its ``k``-th coordinate in the target chart is the value
        there of the ``k``-th forward expression, an element of the coordinate
        field.  The inverse coordinate change is the transition's
        ``inverse()``.  Nothing here reads or produces a symbolic expression:
        the value is the value of an owned section at an owned point.
        """
        source = self.source()
        field = self.manifold().coordinate_field()
        point = self.manifold()(coordinates, chart_label=source.label())
        decisions = tuple(
            ask(section(point) != field.zero()) for section in tuple(self.source_overlap())
        )
        assert all(decision is True for decision in decisions), (
            f"cannot read the coordinates of {point} in the chart {self.target().label()}: the "
            f"coordinate change from the chart {source.label()} is defined on the overlap of the "
            f"two charts, and its overlapping functions do not all take a decided nonzero value "
            f"there, so the point is outside the overlap or its membership is undecided"
        )
        return finite_family(
            tuple(expression(point) for expression in self.forward_expressions()),
            name=(
                f"Coordinates of a point of the chart {source.label()} in the chart "
                f"{self.target().label()}"
            ),
        )

    def _repr_(self):
        return (
            f"{self.regularity()} atlas transition "
            f"{self.source().label()} -> {self.target().label()}"
        )


def _engine_manifold(manifold):
    r"""Return a manifold's private Sage realization to this module's adapters.

    Protected manifold contract (\`OWN-05\`--\`OWN-07\`).  The
    implementation endpoint is
    \`TopologicalManifolds.ParentMethods._engine_manifold_realization\`.  Permitted
    callers are the point, chart, holomorphic-map, and analytic-open adapters
    in this module after the corresponding owned construction has been
    selected.  The Sage manifold remains private to those adapters.
    """
    return manifold._engine_manifold_realization()


def _engine_manifold_chart(chart):
    r"""Return a chart's private Sage realization to a manifold adapter.

    The implementation endpoint is :meth:\`ManifoldAtlasChart._engine_chart\`.
    Permitted callers are the point, transition, map, and open-submanifold
    adapters in this module.  The raw chart never becomes mathematical output.
    """
    return chart._engine_chart()


def _manifold_function_ring(domain, manifold):
    r"""The owned ring of functions on ``domain`` valued in the manifold's coordinate field.

    A chart coordinate is a section of this ring: the functions a manifold
    assigns to the chart's domain are the maps there of the manifold's
    differentiability class, valued in the field its coordinates lie in, and
    they form a ring under the pointwise product.  A topological chart has
    continuous coordinates, the ``C^0`` case; a chart of a complex manifold is
    ``CC``-valued, and ``CC`` is its coordinate field.
    """
    from sage_extensions.categories.functions.real_functions import C

    degree = manifold._preamble_differentiability_degree
    return C(NN(0) if degree is None else degree, domain, manifold.coordinate_field())


class _ChartExpression:
    r"""An engine formula in a chart's coordinates, as the function on the chart's domain it is.

    Private computation class (``OWN-06``).  A formula written in the
    coordinates of a chart ``phi : U -> K^n`` defines the function
    ``p |-> formula(phi(p))`` on ``U``, valued in the coordinate field ``K``.
    The engine's formula is retained here because the chart, transition and
    map adapters speak about the function by it; the symbolic engine is not an
    owned object, and this formula is a private representation, never a parent
    of one.
    """

    def __init__(self, engine_chart, engine_formula, field) -> None:
        self._engine_chart = engine_chart
        self._engine_formula = engine_formula
        self._field = field

    def engine_expression(self):
        r"""The engine's formula for this function (private adapter)."""
        return self._engine_formula

    def __call__(self, point):
        r"""The value of the formula at ``point``, in the coordinate field."""
        coordinates = tuple(self._engine_chart(_engine_manifold_point(point)))
        substitutions = dict(zip(tuple(self._engine_chart[:]), coordinates, strict=True))
        return self._field(self._engine_formula.subs(substitutions))


class _ChartCoordinate(_ChartExpression):
    r"""One coordinate of a chart, as the function it is.

    Private computation class (``OWN-06``).  The ``index``-th coordinate of a
    chart is the function ``U -> K`` sending a point of the chart's domain to
    its ``index``-th coordinate.  The engine's own symbol for that coordinate
    is retained here because the chart, transition and point adapters speak
    about a coordinate by it; the symbolic engine is not an owned object, and
    this symbol is a private representation, never a parent of one.
    """

    def __init__(self, engine_chart, index, field) -> None:
        self._index = int(index)
        super().__init__(engine_chart, tuple(engine_chart[:])[self._index], field)


class _SectionRatio:
    r"""The quotient ``numerator / denominator`` of two sections of a chart's function ring, where it is defined.

    A chart's function ring is a ring of functions on the chart's domain, and a
    section that vanishes somewhere has no inverse in it: the quotient ``g/f``
    of two sections is the function ``p |-> g(p)/f(p)`` on the open subset
    ``{f != 0}``, and that open subset is where a chart change with denominator
    ``f`` is read (:meth:`ManifoldAtlasChart.section_ratio`).  Both operands are
    owned sections and the quotient is the function they define there; the
    engine's formula for it is private, as it is for every other chart
    expression of this module.
    """

    def __init__(self, numerator, denominator) -> None:
        self._numerator = numerator
        self._denominator = denominator

    def numerator(self):
        r"""The section divided."""
        return self._numerator

    def denominator(self):
        r"""The section divided by, which does not vanish where the quotient is read."""
        return self._denominator

    def __call__(self, point):
        r"""The quotient of the two values at ``point``, in the coordinate field."""
        value = self._denominator(point)
        assert ask(value != element_parent(value).zero()) is True, (
            f"the quotient {self} is not defined at {point}: its denominator "
            f"{self._denominator} takes the value {value} there, and the quotient is a "
            f"function only on the open subset where the denominator does not vanish"
        )
        return self._numerator(point) / value

    def _repr_(self):
        return f"({self._numerator}) / ({self._denominator})"


def _manifold_function_definition(value):
    r"""The private map a value of a manifold's function ring is defined by, or ``None``.

    Private adapter (``OWN-06``) of this module.  A section is an element of
    ``C^k(U, K)``, the algebra on the condition submodule cut out of ``K^U``,
    so its chain is the section, the module element and the map it is defined
    by; an operand of a pointwise operation on sections is already that module
    element, one level shorter, and is read here too.  Both are values the
    chart adapters translate back into an engine formula.
    """
    section = value
    for _level in range(2):
        underlying = getattr(section, "underlying_element", None)
        if underlying is None:
            break
        section = underlying() if callable(underlying) else underlying
    definition = getattr(section, "_defining_function", None)
    return None if definition is None else definition()


def _retained_chart_expression(value):
    r"""The engine formula a chart section retains, or ``None`` for any other value.

    A section's defining function is read through the chain the function
    spaces' own formula adapter reads, and it is called: what a section retains
    is the result of that call, the private definition of the function, not the
    accessor for it.
    """
    match _manifold_function_definition(value):
        case _ChartExpression() as expression:
            return expression.engine_expression()
        case _:
            return None


def _constant_section_value(value):
    r"""The value a constant section of a manifold's function ring takes, or ``None``.

    The unit of the ring of functions on a chart's domain is the constant map
    with value one, and the zero is the constant map with value zero, so a
    section can be a constant map with no chart formula at all
    (``categories.functions.real_functions._ConstantMap``).  Its value is what
    states it, and the engine's formula for the constants of a chart's
    coordinates is that value.
    """
    from sage_extensions.categories.functions.real_functions import _ConstantMap

    match _manifold_function_definition(value):
        case _ConstantMap() as constant:
            return constant.value()
        case _:
            return None


def _raise_manifold_expression(engine_formula, chart):
    r"""The section of a chart's function ring that an engine formula in its coordinates defines.

    A formula written in the coordinates of the chart ``phi : U -> K^n`` states
    the function ``p |-> formula(phi(p))`` on ``U``, an element of
    ``C^k(U, K)``, the ring of functions the manifold assigns to the chart's
    domain (:meth:`ManifoldAtlasChart.function_ring`).  The engine's formula is
    retained as the private representation of that function and is never a
    parent: the section is the owned object, and the formula is how the engine
    and the private chart adapters speak about it.
    """
    return chart.function_ring()(
        _ChartExpression(
            _engine_manifold_chart(chart),
            engine_formula,
            chart.manifold().coordinate_field(),
        )
    )


def _admit_manifold_expression(value, chart):
    r"""The section of a chart's function ring that ``value`` is, or a statement that it is none.

    A chart formula on ``U`` is an element of the ring of functions the
    manifold assigns to ``U``; nothing else is a formula there, except the
    quotient of two such sections, which is a function on the open subset where
    its denominator does not vanish and is stated as one
    (:class:`_SectionRatio`).  Admission is by the ring's own element type
    (``OWN-01``): the ring is the owner of what a function on the chart's
    domain is, and this adapter only reads it.
    """
    ring = chart.function_ring()
    match value:
        case _SectionRatio() as ratio:
            operands = (ratio.numerator(), ratio.denominator())
        case _:
            operands = (value,)
    misplaced = tuple(
        operand for operand in operands if element_parent(operand) is not ring
    )
    assert not misplaced, (
        f"a chart formula on the chart {chart.label()} is a section of {ring}, the ring of "
        f"functions the manifold assigns to that chart's domain, and {value!r} is written "
        f"with the sections {tuple(str(element_parent(operand)) for operand in misplaced)}"
    )
    return value


def _engine_formula_of_pointwise_section(value):
    r"""The engine formula of a section built out of chart formulas by the pointwise law, or ``None``.

    Private computation adapter (``OWN-06``) of this module.  The pointwise law
    of a module of maps builds a sum, a negative, the zero and a scalar
    multiple of its operands, and the pointwise product of the algebra on those
    maps builds a product, and each records which
    (``categories.functions.real_functions._pointwise_derivation``); a chart
    formula is one such operand.  Rebuilding the recorded operation on the
    operands' engine formulas is what makes an expression written with the
    owned ring's own operations -- ``x + y``, ``-y``, ``2 * x``, ``x * y`` --
    a formula the engine can speak about, without the ring of functions ever
    being the engine's ring.
    """
    from functools import partial

    from sage_extensions.categories.functions.real_functions import (
        _pointwise_derivation,
        _pointwise_product,
    )
    from sage_extensions.categories.modules.pure.modules import (
        _pointwise_negative,
        _pointwise_scalar_multiple,
        _pointwise_sum,
        _pointwise_zero,
    )

    derivation = _pointwise_derivation(value)
    if derivation is None:
        return None
    operation, operands = derivation
    formulas = tuple(_engine_manifold_expression(operand) for operand in operands)
    match operation:
        case _ if operation is _pointwise_sum:
            return formulas[0] + formulas[1]
        case _ if operation is _pointwise_negative:
            return -formulas[0]
        case _ if operation is _pointwise_zero:
            return SR.zero()
        case _ if operation is _pointwise_product:
            return formulas[0] * formulas[1]
        case partial() if operation.func is _pointwise_scalar_multiple:
            return _engine_scalar(operation.args[0]) * formulas[0]
        case _:
            return None


def _engine_scalar(value):
    r"""The engine's symbolic constant for a scalar of a pointwise operation."""
    match element_parent(value):
        case field if field is RR or field is _owned_complex_field():
            return value.expression()
        case _:
            return SR(value)


def _engine_owned_number(value):
    r"""The engine's element for an owned number, in the field the number belongs to.

    Only a number is lowered here.  A section of a ring of functions that is
    neither a chart formula nor a pointwise operation on chart formulas has no
    engine formula, and saying so is this adapter's frontier rather than a
    coercion error deeper in the engine.
    """
    assert not callable(value), (
        f"cannot lower {value!r} to an engine expression: it is a section of "
        f"{element_parent(value)} that is written neither as a chart formula nor as a "
        f"pointwise sum, negative, zero or scalar multiple of chart formulas, and the engine "
        f"has no formula for it"
    )
    match element_parent(value):
        case field if field is RR or field is _owned_complex_field():
            return _engine_element(field, value)
        case _:
            return _engine_element(RR, RR(value))


def _engine_manifold_expression(value):
    r"""Lower one owned manifold value to the engine's expression.

    Protected manifold-expression contract under ``OWN-05``--``OWN-07``.
    Permitted callers are atlas/map/open-submanifold adapters in this module and
    the affine-analytification adapter.  A chart formula is the function it is,
    and the engine's formula retained by :class:`_ChartExpression` is how the
    engine speaks about it; a quotient of sections is the quotient of their
    formulas, a constant section is its value, a formula written with the owned
    ring's pointwise operations is rebuilt from its operands; any other owned
    value is a number in the coordinate field, lowered as its engine element.
    """
    match value:
        case _SectionRatio() as ratio:
            return _engine_manifold_expression(
                ratio.numerator()
            ) / _engine_manifold_expression(ratio.denominator())
        case _:
            return _engine_section_expression(value)


def _engine_section_expression(value):
    r"""Lower a section of a chart's function ring to the engine's expression for it."""
    retained = _retained_chart_expression(value)
    if retained is not None:
        return retained
    constant = _constant_section_value(value)
    if constant is not None:
        return _engine_scalar(constant)
    formula = _engine_formula_of_pointwise_section(value)
    if formula is not None:
        return formula
    return _engine_owned_number(value)


def _composed_ambient_transition(manifold, source_label, target_label):
    r"""The change from ``source_label`` to ``target_label`` along a chain of stated changes, or ``None``.

    The changes an atlas states generate a relation between the charts it carries:
    two charts joined by a chain of stated changes are related by composing them
    step by step, ``(phi_t o phi_c^{-1}) o (phi_c o phi_s^{-1})``
    (:meth:`ManifoldAtlasTransition.then`; Lee, *Introduction to Smooth Manifolds*,
    2nd ed., Ch. 1).  A chart another construction registered may meet only the
    chart it was cut from, so the chain can be longer than one step -- a chart cut
    on the north chart and one cut on the south chart are joined through both
    stereographic charts -- and the composition along the shortest such chain is
    the change the atlas has.  ``None`` says no chain joins them.
    """
    if (source_label, target_label) in manifold._preamble_transitions:
        return manifold.transition(source_label, target_label)
    stated = tuple(manifold._preamble_transitions)
    reached = {source_label: None}
    frontier = [source_label]
    while frontier:
        following = []
        for label in frontier:
            for left, right in stated:
                if left != label or right in reached:
                    continue
                reached[right] = label
                if right == target_label:
                    chain = [right]
                    while reached[chain[-1]] is not None:
                        chain.append(reached[chain[-1]])
                    chain.reverse()
                    change = manifold.transition(chain[0], chain[1])
                    for step in range(1, len(chain) - 1):
                        change = change.then(manifold.transition(chain[step], chain[step + 1]))
                    return change
                following.append(right)
        frontier = following
    return None


def _chart_family_covers(manifold, labels):
    r"""Whether the charts ``labels`` cover ``manifold``, decided by containment.

    A family of charts covers the manifold when every point of the manifold is a
    point of one of them; the decision here is the one the atlas can make from
    its own chart domains -- every chart the manifold carries lies inside one of
    the charts given ``(Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1,
    for a chart's domain)``.  That is a sufficient condition, not a necessary
    one: a family that covers by meeting instead of by containment is not decided
    here, and a caller is told so rather than being told its family covers.
    """
    given = tuple(_engine_manifold_chart(manifold.atlas()[label]) for label in labels)
    for label in manifold.chart_labels():
        if label in labels:
            continue
        domain = _engine_manifold_chart(manifold.atlas()[label]).domain()
        if not any(domain.is_subset(chart.domain()) for chart in given):
            return False
    return True


def _upper_triangle(n):
    r"""The index pairs ``(i, j)``, ``i <= j < n``, of the entries of an ``n x n`` symmetric matrix."""
    return tuple((row, column) for row in range(int(n)) for column in range(row, int(n)))


def _symmetric_entry(coordinates, row, column):
    return coordinates[(min(row, column), max(row, column))]


def _skew_entry(coordinates, row, column):
    match row - column:
        case 0:
            return SR.zero()
        case difference if difference > 0:
            return -coordinates[(column, row)]
        case _:
            return coordinates[(row, column)]


def _engine_positive_definite(hermitian):
    r"""Sylvester's criterion: a Hermitian matrix is positive definite iff each leading principal minor is positive.

    The minors of a Hermitian matrix are real; the conditions compare their
    real parts with ``0`` so that the engine reads each as a real inequality.
    """
    return tuple(
        hermitian[:size, :size].det().real_part() > 0
        for size in range(1, hermitian.nrows() + 1)
    )


def _engine_positive_root_count(diagram, vertices):
    r"""``|Phi_X^+|`` for the subdiagram on ``vertices``: the length of the longest element of ``W_X``."""
    from sage_extensions.categories.coxeter_diagrams import (
        _engine_coxeter_matrix_entry,
    )

    match len(vertices):
        case 0:
            return 0
        case _:
            group = CoxeterGroup(
                CoxeterMatrix(
                    [
                        [
                            _engine_coxeter_matrix_entry(diagram.coxeter_entry(left, right))
                            for right in vertices
                        ]
                        for left in vertices
                    ]
                ),
                implementation="reflection",
            )
            return group.long_element().length()


def _symmetric_space_rank_and_dimension(satake_diagram):
    r"""The real rank ``dim a_0`` and the dimension ``dim p_0`` of ``G/K`` for the real form of a Satake diagram.

    ``a_0`` is a maximal abelian subspace of ``p_0``; its dimension is the
    number of ``tau``-orbits of white nodes (Araki, 1962).  The roots
    vanishing on ``a_0`` are the roots ``Phi_X`` of the black subdiagram, so
    ``dim n_0 = |Phi^+| - |Phi_X^+|``, and the Iwasawa decomposition
    ``g_0 = k_0 + a_0 + n_0`` (Helgason, Ch. VI) gives
    ``dim G/K = dim p_0 = dim a_0 + dim n_0``.
    """
    diagram = satake_diagram.dynkin_diagram()
    tau = satake_diagram.involution()
    black = tuple(satake_diagram.black_nodes())
    vertices = tuple(diagram.index_set())
    white = tuple(vertex for vertex in vertices if vertex not in satake_diagram.black_nodes())
    rank = len({frozenset((vertex, tau(vertex))) for vertex in white})
    return rank, rank + _engine_positive_root_count(diagram, vertices) - _engine_positive_root_count(
        diagram, black
    )


def _admit_manifold_expression_family(values, chart, *, name):
    return finite_family(
        tuple(_admit_manifold_expression(value, chart) for value in values),
        name=name,
    )


def _engine_nonvanishing_conditions(functions):
    r"""Lower the open set ``{f != 0 for every f}`` to SageManifolds chart restrictions.

    SageManifolds reads a list of restrictions as their conjunction; the empty
    family is ``None``, no restriction.
    """
    conditions = [_engine_manifold_expression(function) != 0 for function in functions]
    return conditions or None


def _raise_manifold_expression_family(values, chart, *, name):
    return finite_family(
        tuple(_raise_manifold_expression(value, chart) for value in values),
        name=name,
    )


def _engine_manifold_point(point):
    r"""Return a point's private Sage realization for same-manifold equality."""
    return point._engine_manifold_point()


def _is_a_point_in(manifold, value) -> bool:
    r"""Whether ``value`` is a point of another manifold that lies in ``manifold``.

    The points of an open subset of a manifold are the points of the manifold
    that lie in it (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example
    1.4), so a point of an open submanifold is a point of the manifold it is
    open in, and two open submanifolds that share a point share it.  The point's
    private realization is a point of this manifold exactly when it lies in it,
    which the engine decides; a point of another manifold does not lie in it.
    """
    if element_parent(value) is manifold:
        return False
    if getattr(value, "chart", None) is None:
        return False
    return _engine_manifold_point(value) in _engine_manifold(manifold)


def _coordinates_of_a_point_in(manifold, value):
    r"""The label and the coordinates, in a chart of ``manifold``, of a point of another manifold that lies in it.

    The point is read in the chart it was given by when ``manifold`` carries
    that chart too -- a chart of an open submanifold is a chart of the manifold
    it is open in -- and otherwise in the chart of ``manifold`` the atlas
    presents first, which is where a point of an open submanifold cut out inside
    this manifold's own chart has its coordinates.
    """
    labels = tuple(manifold.chart_labels())
    given = value.chart().label()
    label = given if given in labels else labels[0]
    field = manifold.coordinate_field()
    return label, tuple(
        field(coordinate)
        for coordinate in _engine_manifold_chart(manifold.atlas()[label])(
            _engine_manifold_point(value)
        )
    )


class _DeferredEngineRealization:
    r"""A manifold's private engine, built the first time a reader asks for it.

    A manifold built by this category's constructor is handed its engine ready
    made.  The exact real line is placed in the category by the field's own
    construction, which states its engine as one of these: the engine and the
    charts drawn from it are built when a chart, a point or the topology first
    reads one, and are built once.
    """

    def __init__(self, engine_factory) -> None:
        assert callable(engine_factory), (
            f"a deferred engine realization is a zero-argument construction, but "
            f"{engine_factory!r} is not callable"
        )
        self._engine_factory = engine_factory
        self._engine = None

    def realize(self):
        if self._engine is None:
            self._engine = self._engine_factory()
        return self._engine


class _ChartwiseFunction:
    r"""The chart expressions of a smooth function, as the function they define.

    Private computation class (``OWN-06``).  A smooth function on a manifold is
    a map ``M -> K``; its expression in a chart states it on that chart's
    domain, and the expressions of one function agree on the overlaps where the
    charts meet (``SmoothManifolds.ParentMethods.smooth_function``, which is the
    only constructor).  The engine's formula for each expression is retained
    here because the derivative of a function along a vector field is the
    engine's own computation on formulas; the formulas are a private
    representation, never a parent of an owned object.
    """

    def __init__(self, manifold, expressions, formulas) -> None:
        self._manifold = manifold
        self._expressions = expressions
        self._formulas = formulas

    def manifold(self):
        r"""The manifold the function is on."""
        return self._manifold

    def expressions(self):
        r"""The function's expression in each chart, as sections of that chart's function ring."""
        return self._expressions

    def formulas(self):
        r"""The engine's formula for the function's expression in each chart (private adapter)."""
        return self._formulas

    def __call__(self, point):
        r"""The value of the function at ``point``, in the manifold's coordinate field.

        A function is written on a cover of the manifold, and a point may be given
        in a chart outside that cover: the point's coordinates are then read in a
        chart of the cover through the coordinate change the atlas states between
        them (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).
        """
        manifold = self._manifold
        label = point.chart().label()
        if label not in self._formulas:
            stated = tuple(self._formulas)
            stated_pairs = tuple(pair for pair in manifold.transitions().index_set())
            reachable = tuple(
                other for other in stated if (label, other) in stated_pairs
            )
            assert reachable, (
                f"the function is written on the charts {stated} of {manifold} and {point} is "
                f"given in the chart {label}: the atlas states no coordinate change from that "
                f"chart to any chart the function is written on"
            )
            label = reachable[0]
        chart = _engine_manifold_chart(manifold.atlas()[label])
        coordinates = tuple(chart(_engine_manifold_point(point)))
        substitutions = dict(zip(tuple(chart[:]), coordinates, strict=True))
        return manifold.coordinate_field()(self._formulas[label].subs(substitutions))

    def _repr_(self):
        return f"the smooth function with expressions on the charts {tuple(self._formulas)}"


def _chartwise_formulas(function, manifold):
    r"""The engine's formula for a smooth function in each chart of ``manifold``, or ``None``.

    Private computation adapter (``OWN-06``).  A smooth function is written by
    its chart expressions, and a function built from such functions by the
    pointwise law of the algebra of functions -- a sum, a negative, a scalar
    multiple, a product -- is written by the same law applied to theirs, which
    is what the recorded operation states
    (``categories.functions.real_functions._pointwise_derivation``).  A function
    given only by a callable has no expression in any chart, and an operation
    that needs one states that frontier rather than inventing one.
    """
    return _chartwise_formulas_of_definition(
        _manifold_function_definition(function), manifold
    )


def _chartwise_formulas_of_definition(definition, manifold):
    r"""The per-chart formulas of the function a definition states, or ``None``."""
    from sage_extensions.categories.functions.real_functions import _ConstantMap
    from sage_extensions.categories.modules.general_modules import _PointwiseValues

    match definition:
        case _ChartwiseFunction() as chartwise:
            return chartwise.formulas()
        case _ConstantMap() as constant:
            value = _engine_scalar(constant.value())
            return {label: value for label in tuple(manifold.chart_labels())}
        case _PointwiseValues() as values:
            families = tuple(
                _chartwise_formulas_of_definition(
                    _manifold_function_definition(operand), manifold
                )
                for operand in values.operands()
            )
            if any(family is None for family in families):
                return None
            return {
                label: _rebuilt_pointwise_formula(
                    values.operation(), tuple(family[label] for family in families)
                )
                for label in tuple(manifold.chart_labels())
            }
        case _:
            return None


def _rebuilt_pointwise_formula(operation, operands):
    r"""The engine formula of the pointwise operation ``operation`` on ``operands``."""
    from sage_extensions.categories.functions.real_functions import _pointwise_product
    from sage_extensions.categories.modules.pure.modules import (
        _pointwise_negative,
        _pointwise_scalar_multiple,
        _pointwise_sum,
        _pointwise_zero,
    )

    match operation:
        case _ if operation is _pointwise_sum:
            return operands[0] + operands[1]
        case _ if operation is _pointwise_negative:
            return -operands[0]
        case _ if operation is _pointwise_zero:
            return SR.zero()
        case _ if operation is _pointwise_product:
            return operands[0] * operands[1]
        case _ if (
            isinstance(operation, partial) and operation.func is _pointwise_scalar_multiple
        ):
            return _engine_scalar(operation.args[0]) * operands[0]
        case _:
            return None


def _chartwise_family_agrees(manifold, expressions, order) -> None:
    r"""Decide that a chart-wise family states one object on ``manifold``, or state where it does not.

    ``expressions[chart.label()]`` is the tuple of components of one object in
    that chart's coordinates, and ``order`` is the order of the object: ``0``
    for a function, whose expression is read where it is, and ``1`` for a vector
    field, whose components transform by the derivative of the coordinate
    change.  Writing ``y`` for the coordinates of the target chart as functions
    of the coordinates ``x`` of the source chart, the two statements are
    ``h_t(y(x)) = h_s(x)`` and ``a_t^j(y(x)) = sum_i a_s^i(x) dy_j/dx_i``
    (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3).  The comparison
    is made where the transition is stated -- its own expressions, on the
    overlap its overlap functions cut out -- and a family that fails it is
    refused, naming the two charts and the component.

    Nothing is enumerated: the residuals are rational expressions in the
    charts' coordinates, and their vanishing is decided exactly.
    """
    labels = tuple(expressions)
    dimension = int(manifold.dimension())
    for source_label, target_label in combinations(labels, 2):
        assert (source_label, target_label) in manifold._preamble_transitions, (
            f"cannot decide whether the chart-wise family states one object on {manifold}: the "
            f"charts {source_label} and {target_label} are both given, and the atlas states no "
            f"coordinate change between them"
        )
        for transition in (
            manifold.transition(source_label, target_label),
            manifold.transition(target_label, source_label),
        ):
            source = transition.source()
            target = transition.target()
            variables = tuple(_engine_manifold_chart(source)[:])
            images = tuple(_engine_manifold_chart(target)[:])
            forward = tuple(
                SR(_engine_manifold_expression(expression))
                for expression in transition.forward_expressions()
            )
            stated = tuple(
                SR(_engine_manifold_expression(expression))
                for expression in expressions[source.label()]
            )
            pulled = tuple(
                SR(_engine_manifold_expression(expression)).subs(
                    dict(zip(images, forward, strict=True))
                )
                for expression in expressions[target.label()]
            )
            match int(order):
                case 0:
                    transported = stated
                case 1:
                    jacobian = tuple(
                        tuple(formula.diff(variable) for variable in variables)
                        for formula in forward
                    )
                    transported = tuple(
                        sum(
                            stated[index] * jacobian[position][index]
                            for index in range(dimension)
                        )
                        for position in range(dimension)
                    )
                case _:
                    assert False, (
                        f"a chart-wise family states objects of order 0 or 1, and {order} is "
                        f"neither"
                    )
            for position, (left, right) in enumerate(
                zip(transported, pulled, strict=True)
            ):
                residual = SR(left - right).simplify_rational()
                assert residual == 0, (
                    f"the chart-wise family on {manifold} does not state one object: on the "
                    f"chart {source.label()} the component {position} is {transported[position]}, "
                    f"and the component stated on the chart {target.label()} is {pulled[position]} "
                    f"there, which leaves the residual {residual}"
                )


class _ManifoldTopologyData(SageObject):
    r"""Private topology realization supplied by SageManifolds.

    The native manifold is the maintained representation of the complete
    topology.  The owned topology exposes its open-set object without
    pretending that arbitrary subsets of an infinite manifold are enumerable.
    Exact arbitrary-subset openness is assertion-gated until a represented
    subset is carried by a native open-submanifold construction.

    An open submanifold carries the initial topology along its inclusion: a
    subset of it is open exactly when its image is open in the ambient manifold
    (Mathlib, ``TopologicalSpace.induced`` -- the coarsest topology making the
    inclusion continuous).  That is retained here as a predicate, ``induced_from``
    naming the ambient manifold: the submanifold's decision is asked of the
    ambient manifold on the image of the subset, and no subset of either
    manifold is enumerated.  The ambient manifold decides what it can decide --
    the empty set and itself -- and refuses the rest rather than guessing.
    """

    def __init__(self, engine_manifold, induced_from=None) -> None:
        self._engine_manifold = engine_manifold
        self._induced_from = induced_from

    def _engine_manifold_realization(self):
        engine = self._engine_manifold
        match engine:
            case _DeferredEngineRealization():
                return engine.realize()
            case _:
                return engine

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        power = space.power_set()
        selected = power(subset)
        if selected is power.bottom() or ask(selected == power.bottom()) is True:
            return True
        if selected is power.top() or ask(selected == power.top()) is True:
            return True
        ambient = self._induced_from
        if ambient is not None:
            image = ambient.power_set().from_predicate(
                lambda point: self._is_selected_on(space, selected, point)
            )
            return ambient.is_open_subset(image)
        assert False, (
            f"cannot decide whether {selected} is open in the manifold {space}: "
            f"openness is decided only for the empty set, the whole manifold, "
            f"and open submanifolds constructed as such"
        )

    def _is_selected_on(self, space, selected, point):
        r"""Whether ``point`` of the ambient manifold is the image of a point of the subset.

        The submanifold's points are the ambient manifold's points that lie in it
        (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example 1.4), so the
        image of a subset is the subset itself read on the ambient manifold.  A
        point outside the submanifold has no image to be in the subset, which the
        submanifold's own point construction refuses.
        """
        try:
            inner = space(point)
        except (TypeError, ValueError):
            return False
        return inner in selected


class _ChartDomainRealization:
    r"""An open submanifold of a manifold, realized as the domain of one of its charts; a realization, not a category.

    A chart ``phi : U -> K^n`` is defined on an open subset ``U`` of the
    manifold (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1), and an
    open subset of a manifold, with the restricted atlas, is a manifold of the
    same dimension and class (Lee, Example 1.4).  The chart that the open
    subset is the domain of is registered on it, so the open subset retains the
    chart that presents it and the ambient manifold it is open in.
    """

    def __init__(self, containing_manifold, chart_label, engine_chart, **rest) -> None:
        self._containing_manifold = containing_manifold
        self._chart_label = chart_label
        super().__init__(**rest)
        self._register_chart(chart_label, engine_chart)

    def containing_manifold(self):
        r"""The manifold this open subset is open in."""
        return self._containing_manifold

    def _element_constructor_(self, datum, chart_label=None):
        r"""The point of this open submanifold that a point of the ambient manifold in it is.

        The points of an open submanifold are the points of the manifold that
        lie in it, so a point of the ambient manifold is a point here, read in
        the one chart this open subset carries, the chart it is the domain of.
        A point outside the open subset has no coordinates in that chart, which
        the engine's restricted chart refuses.  Any other datum is a point given
        by coordinates, as on any manifold.
        """
        match element_parent(datum):
            case parent if parent is not self.containing_manifold():
                return super()._element_constructor_(datum, chart_label)
            case _:
                field = self.coordinate_field()
                label = self._chart_label
                engine_chart = _engine_manifold_chart(self.atlas()[label])
                return self._element_constructor_(
                    tuple(
                        field(value)
                        for value in engine_chart(_engine_manifold_point(datum))
                    ),
                    label,
                )

    def _repr_(self):
        return (
            f"{self.dimension()}-dimensional open submanifold {self.manifold_name()} of "
            f"{self.containing_manifold()}, the domain of its chart {self._chart_label}"
        )


def _real_line_engine():
    r"""The private Sage realization of the real line: one smooth 1-manifold, chart named ``x``."""
    return _SageManifold(1, "RR", structure="smooth", unique_tag=object())


def _real_line_smooth_structure(field):
    r"""Establish the smooth structure of the real line on the exact field itself.

    The real line is a one-dimensional smooth manifold whose charts are the
    identity ``x: R -> R`` read on the whole space, and the topology it carries
    is the one that chart presents (Lee, *Introduction to Smooth Manifolds*,
    2nd ed., Example 1.2).  The field's own construction places it in
    ``SmoothManifolds()``, so the manifold level's datum is recorded on the
    field together with the topology that datum presents: the object placed in
    the category is the field, and no manifold is built beside it, since a
    second real line would be equal to ``RR`` in nothing (``CAT-15``,
    ``CAT-23``).

    The engine and the chart are stated as constructions rather than made here,
    so constructing the field does not build a chart of it; the field's
    ``_standard_charts`` states the chart, and the atlas read registers it.
    """
    engine = _DeferredEngineRealization(_real_line_engine)
    TopologicalSpaces.ParentMethods._retain_topology(field, _ManifoldTopologyData(engine))
    TopologicalManifolds.ParentMethods._retain_manifold_structure(
        field,
        engine,
        1,
        "RR",
        "smooth",
        Infinity,
        "real",
    )
    return field


class TopologicalManifolds(OwnedCategory):
    r"""Owned finite-dimensional topological manifolds."""

    def super_categories(self):
        return [TopologicalSpaces()]

    @classmethod
    def _repr_object_names(cls):
        return "topological manifolds"

    def an_object(self):
        return self(1, "M_top")

    def DimensionAtMost(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

        return ManifoldsOfDimensionAtMost(self, dimension)

    def PureDimension(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

        return PureDimensionalManifolds(self, dimension)

    def on(self, underlying_space, atlas):
        r"""Place the exact space under a compatible topological atlas."""
        pass

    def _call_(self, dimension, name):
        dimension = int(dimension)
        if dimension <= 0:
            raise ValueError(
                f"cannot construct a topological manifold {name} of dimension {dimension}: "
                f"the dimension must be positive"
            )
        engine = _SageManifold(
            dimension,
            str(name),
            structure="topological",
            unique_tag=object(),
        )
        return _object_of(
            self,
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="topological",
            differentiability_degree=None,
            manifold_field="real",
        )

    class ElementMethods(Element):
        r"""A point of a manifold, given by its coordinates in a labelled chart.

        A chart is a homeomorphism onto an open subset of ``K^n``, so the
        coordinates of a point are elements of the coordinate field ``K``.
        """

        # A point built here keeps the engine point its coordinates name.  An
        # element that is the manifold's own element -- a real number is a
        # point of the real line -- was not built here and keeps none: the
        # chart it presents reads it through the coordinates it states.
        _engine_point = None

        def __init__(self, parent: Parent, coordinates, chart_label) -> None:
            Element.__init__(self, parent)
            field = parent.coordinate_field()
            self._coordinates = finite_family(
                tuple(field(coordinate) for coordinate in coordinates),
                name=f"Coordinates of point of {parent}",
            )
            self._chart_label = chart_label
            self._engine_point = _engine_manifold(parent)(
                tuple(
                    _engine_manifold_expression(coordinate)
                    for coordinate in self._coordinates
                ),
                chart=_engine_manifold_chart(parent.atlas()[chart_label]),
            )

        def manifold(self):
            return self.parent()

        def coordinates(self):
            return self._coordinates

        def chart(self):
            return self.parent().atlas()[self._chart_label]

        def _engine_manifold_point(self):
            r"""The private engine point of this point.

            A point built by this class keeps the engine point its coordinates
            name.  An element that is the manifold's own element -- a real number
            is a point of the real line -- keeps none, and is read here in the
            chart it presents, at the one coordinate it states.
            """
            engine_point = self._engine_point
            match engine_point:
                case None:
                    manifold = self.manifold()
                    return _engine_manifold(manifold)(
                        tuple(
                            _engine_manifold_expression(coordinate)
                            for coordinate in self.coordinates()
                        ),
                        chart=_engine_manifold_chart(self.chart()),
                    )
                case _:
                    return engine_point

        def __eq__(self, other) -> bool:
            r"""Two points of one manifold are equal when they are the same point, in whichever charts they were given.

            In one chart ``phi``, which is injective, ``p = p'`` exactly when
            ``phi(p) = phi(p')``: the coordinates are compared as elements of
            the coordinate field, which decides the equality of exact numbers.
            Points given in two charts are compared by the private
            SageManifolds points, through the transition map.
            """
            if element_parent(other) is not self.parent():
                return False
            match other.chart().label() == self.chart().label():
                case True:
                    relations = tuple(
                        left == right
                        for left, right in zip(self.coordinates(), other.coordinates(), strict=True)
                    )
                    assert all(relation is True or relation is False for relation in relations), (
                        f"cannot decide whether {self} and {other} are the same point of "
                        f"{self.parent()}: the equality of their coordinates in the chart "
                        f"{self.chart().label()} is undecided"
                    )
                    return all(relation is True for relation in relations)
                case False:
                    return _engine_manifold_point(other) == self._engine_manifold_point()

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash(id(self.parent()))

        def _repr_(self):
            coordinates = ", ".join(str(coordinate) for coordinate in self.coordinates())
            return f"Point ({coordinates}) in the chart {self._chart_label} of {self.manifold()}"

    class ParentMethods:
        def __init__(
            self,
            engine_manifold,
            manifold_dimension,
            manifold_name,
            manifold_structure,
            differentiability_degree,
            manifold_field="real",
            chart_index_set=None,
            chart_provider=None,
            **rest,
        ) -> None:
            r"""Record the manifold this object realizes and its smooth structure.

            ``engine_manifold`` is the engine realization ``M`` of this manifold
            (:meth:`_engine_manifold_realization`): every chart of the atlas is
            a chart of ``M``, and ``M``'s charts are the ones the transition
            maps are read from.  ``manifold_dimension`` is ``dim(M)``,
            ``manifold_name`` the label the manifold is written by,
            ``manifold_structure`` the kind of atlas it carries,
            ``differentiability_degree`` the ``k`` of that atlas' ``C^k``
            maps (``None`` for a topological manifold and ``Infinity`` for a
            smooth one, Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 1), and ``manifold_field`` the field the charts take values
            in, read back by :meth:`coordinate_field`.
            """
            self._retain_manifold_structure(
                engine_manifold,
                manifold_dimension,
                manifold_name,
                manifold_structure,
                differentiability_degree,
                manifold_field,
                chart_index_set,
                chart_provider,
            )
            super().__init__(**rest)

        def _retain_manifold_structure(
            self,
            engine_manifold,
            manifold_dimension,
            manifold_name,
            manifold_structure,
            differentiability_degree,
            manifold_field="real",
            chart_index_set=None,
            chart_provider=None,
        ) -> None:
            r"""Record this level's construction data on the object it is placed on.

            What the data are is stated by the constructor
            (:meth:`__init__`).  The constructor passes its keywords here, and
            an object whose own construction places it in the category states
            the same data from that construction -- the exact real line is the
            field ``RR`` itself -- so the level records it in one place either
            way.
            """
            self._preamble_engine_manifold = engine_manifold
            self._preamble_manifold_dimension = NN(int(manifold_dimension))
            self._preamble_manifold_name = str(manifold_name)
            self._preamble_manifold_structure = str(manifold_structure)
            self._preamble_differentiability_degree = (
                differentiability_degree
                if differentiability_degree is None or differentiability_degree == Infinity
                else NN(int(differentiability_degree))
            )
            self._preamble_manifold_field = str(manifold_field)
            self._preamble_charts = {}
            self._preamble_chart_index_set = chart_index_set
            self._preamble_chart_provider = chart_provider
            self._preamble_transitions = {}

        def dimension(self):
            return self._preamble_manifold_dimension

        def manifold_name(self):
            return self._preamble_manifold_name

        def manifold_structure(self):
            return self._preamble_manifold_structure

        def base_field_type(self):
            return self._preamble_manifold_field

        def coordinate_field(self):
            r"""The field ``RR``: a chart of a real manifold is a homeomorphism onto an open subset of ``RR^n``."""
            return RR

        def regularity(self):
            degree = self._preamble_differentiability_degree
            if degree is None:
                return "topological"
            if degree == Infinity:
                return "smooth"
            return f"C^{degree}"

        def differentiability_degree(self):
            degree = self._preamble_differentiability_degree
            if degree is None:
                raise TypeError(
                    f"{self} has no differentiability degree: it is a topological "
                    f"manifold with no differentiable structure"
                )
            return degree

        def is_smooth(self) -> bool:
            return self._preamble_differentiability_degree == Infinity

        def _engine_manifold_realization(self):
            engine = self._preamble_engine_manifold
            match engine:
                case _DeferredEngineRealization():
                    return engine.realize()
                case _:
                    return engine

        def chart(self, label, coordinates):
            return self._register_chart(label, self._engine_manifold_realization().chart(coordinates))

        def chart_on_open_subset(self, label, coordinates, source_label, nonvanishing):
            r"""Register the chart ``coordinates`` on the open subset where the given sections do not vanish.

            The sections are read in the chart ``source_label`` of this
            manifold, and the open subset they cut out is
            ``{p : f(p) != 0 for every f in nonvanishing}``, open because every
            ``f`` is continuous and nonvanishing at each of its points.  The new
            chart is a chart of this manifold on that subset: its domain is the
            subset, an open submanifold
            (:meth:`ManifoldAtlasChart.domain`), not the whole manifold.  It is
            a chart of the same manifold as the chart that states the
            condition, so a transition map is asked of this manifold.
            """
            source = self.atlas()[source_label]
            conditions = tuple(
                _engine_manifold_expression(section) for section in nonvanishing
            )
            assert conditions, (
                f"cannot register the chart {label!r} on the open subset of {self} where no "
                f"function is required to be nonzero: that subset is the whole chart "
                f"{source_label!r}, and chart() registers the chart of the whole manifold"
            )
            engine_chart = _engine_manifold_chart(source)
            engine_open = engine_chart.domain().open_subset(
                str(label),
                coord_def={engine_chart: conditions},
            )
            chart = self._register_chart(
                label, engine_open.chart(coordinates), nonvanishing=nonvanishing
            )
            # The chart cut on the subset reads the same coordinates there, so the
            # coordinate change to the chart it was cut from is the identity; it is
            # defined on the whole of the cut chart, which is the subset of the chart
            # it was cut from that its conditions select.
            self.transition_map(
                label,
                source_label,
                chart.coordinates(),
                source.coordinates(),
                target_overlap=tuple(nonvanishing),
            )
            return chart

        def _register_chart(self, label, engine_chart, domain=None, nonvanishing=()):
            r"""Record the chart ``engine_chart`` of this manifold's engine under ``label``.

            The chart is defined on ``domain``, an open subset of this manifold.
            A chart handed over without one is defined on the open subset the
            engine's chart is registered on: on this manifold when that chart is
            a chart of the whole manifold, and otherwise on the open submanifold
            the chart's domain is (:meth:`_chart_domain`).  A chart's domain is
            therefore never a claim larger than the set the chart exists on.
            """
            if label in self._preamble_charts:
                raise ValueError(
                    f"cannot add a chart labelled {label!r} to {self}: its atlas already "
                    f"has a chart with that label"
                )
            if domain is None:
                domain = (
                    self
                    if engine_chart.domain() is self._engine_manifold_realization()
                    else self._chart_domain(label, engine_chart)
                )
            chart = ManifoldAtlasChart(
                self, label, engine_chart, domain, nonvanishing=nonvanishing
            )
            self._preamble_charts[label] = chart
            return chart

        def _chart_domain(self, label, engine_chart):
            r"""The open submanifold of this manifold that a chart on a proper open subset is defined on."""
            engine_domain = engine_chart.domain()
            return _object_of(
                self.category(),
                _engine=(self.category(), _ChartDomainRealization, None),
                topology_data=_ManifoldTopologyData(engine_domain, induced_from=self),
                engine_manifold=engine_domain,
                manifold_dimension=self.dimension(),
                manifold_name=str(label),
                manifold_structure=self.manifold_structure(),
                differentiability_degree=self._preamble_differentiability_degree,
                manifold_field=self._preamble_manifold_field,
                containing_manifold=self,
                chart_label=label,
                engine_chart=engine_chart,
                **self._chart_domain_structure(label, engine_chart),
            )

        def _chart_domain_structure(self, label, engine_chart) -> dict:
            r"""The data a chart's domain object carries beyond the chart domain's own.

            An open submanifold inherits the structure its ambient manifold
            carries, so a category whose objects carry chosen structure states
            here what the domain of a chart on it is given.  A manifold with no
            structure beyond its atlas adds nothing.
            """
            return {}

        def __call__(self, *args, **kwargs):
            r"""Construct a point through the owned element construction directly."""
            return self._element_constructor_(*args, **kwargs)

        def _element_constructor_(self, datum, chart_label=None):
            r"""Return the point with coordinates ``datum`` in the chart ``chart_label``, or ``datum`` if it is a point of this manifold.

            A point of a manifold of positive dimension is given by its
            coordinates in a chart.  A chart that is not named is the chart the
            atlas presents first: the atlas' chart labels are a selected finite
            ordered family, so the first of them is a chart of this manifold and
            not a guess among them.  A point of an open submanifold of this
            manifold is a point of this manifold -- the points of an open subset
            are the points of the manifold that lie in it (Lee, *Introduction to
            Smooth Manifolds*, 2nd ed., Example 1.4) -- and is read at the
            coordinates it has in a chart of this manifold.
            """
            match datum:
                case _ if element_parent(datum) is self:
                    return datum
                case _ if _is_a_point_in(self, datum):
                    label, coordinates = _coordinates_of_a_point_in(self, datum)
                    return self.element_class(self, coordinates, label)
                case _:
                    coordinates = tuple(datum)
                    if len(coordinates) != self.dimension():
                        raise ValueError(
                            f"{coordinates} are not the coordinates of a point of {self}: a "
                            f"point of a manifold of dimension {self.dimension()} has "
                            f"{self.dimension()} coordinates, not {len(coordinates)}"
                        )
                    return self.element_class(
                        self, coordinates, self._presented_chart_label(chart_label)
                    )

        def _presented_chart_label(self, chart_label):
            r"""The chart label a point's coordinates are read in, defaulting to the atlas' first chart."""
            match chart_label:
                case None:
                    labels = tuple(self.chart_labels())
                    if not labels:
                        raise ValueError(
                            f"cannot give a point of {self} by its coordinates: the manifold has "
                            f"no chart to read them in"
                        )
                    return labels[0]
                case _:
                    return chart_label

        def point(self, coordinates, chart_label=None):
            return self(coordinates, chart_label)

        def chart_labels(self):
            self._standard_charts()
            if self._preamble_chart_index_set is not None:
                return self._preamble_chart_index_set
            return self.selected_finite_chart_labels()

        def _standard_charts(self):
            r"""Register the charts this manifold's own construction states for it.

            A manifold built by this category's constructor presents the charts its
            caller registers.  A manifold placed in the category by its own
            construction states its charts here, and they are registered when the
            atlas is first read; a manifold that states none -- every manifold the
            constructor builds -- is unaffected.
            """

        def selected_finite_chart_labels(self):
            r"""Labels in the currently registered finite chart realization."""
            return finite_ordered_set(tuple(self._preamble_charts))

        def atlas(self):
            labels = self.chart_labels()
            return indexed_family(
                labels,
                lambda label: (
                    self._preamble_charts[label]
                    if label in self._preamble_charts
                    else self._preamble_chart_provider(label)
                    if self._preamble_chart_provider is not None
                    else self._preamble_charts[label]
                ),
                description=lambda self=self: f"Atlas charts of {self}",
            )

        def open_submanifold(self, open_inclusion):
            r"""Return the open submanifold of this manifold that the inclusion selects.

            An open subset of a manifold, with the restricted atlas, is a manifold of
            the same dimension and class (Lee, *Introduction to Smooth Manifolds*,
            2nd ed., Example 1.4), and the inclusion is its presentation: the domain
            of the inclusion is the open submanifold, and the inclusion selects it in
            this manifold.  Nothing is rebuilt -- a second manifold on the same points
            would be a second authority for the same subset (``OWN-15``) -- so the
            object returned is the inclusion's domain.

            The charts of this manifold restrict to charts of the submanifold: a chart
            read on the intersection of its domain with the submanifold is a chart
            there, and it is registered under the label it has here.  A chart whose
            domain is already a chart of the submanifold is the same chart and is not
            registered again.  Its topology is the initial one along the inclusion,
            retained as the predicate that a subset is open exactly when its image is
            (``_ManifoldTopologyData``); nothing about either manifold is enumerated.
            """
            domain = open_inclusion.domain()
            assert open_inclusion.codomain() is self, (
                f"{open_inclusion} ends at {open_inclusion.codomain()}, not at {self}: an "
                f"open submanifold of {self} is selected by an inclusion into {self}"
            )
            assert domain in self.category(), (
                f"an open submanifold of {self} is a manifold of its dimension and class, "
                f"and {domain} is in {domain.category()}"
            )
            engine_subset = _engine_manifold(domain)
            assert engine_subset.is_open() and engine_subset.is_subset(
                _engine_manifold(self)
            ), (
                f"cannot select {domain} as an open submanifold of {self}: {domain} is not "
                f"an open subset of the points of {self}"
            )
            present = tuple(domain.chart_labels())
            bases = tuple(
                label
                for label in self.chart_labels()
                if self.atlas()[label].domain() is domain
            )
            for label in self.chart_labels():
                if label in present:
                    continue
                engine_chart = _engine_manifold_chart(self.atlas()[label])
                overlap = engine_chart.domain().intersection(engine_subset)
                domain._register_chart(
                    label,
                    engine_chart.restrict(overlap),
                    nonvanishing=tuple(
                        condition
                        for base in bases
                        for condition in _composed_ambient_transition(
                            self, base, label
                        ).target_overlap()
                    ),
                )
            for source_label in tuple(domain.chart_labels()):
                for target_label in tuple(domain.chart_labels()):
                    if source_label == target_label:
                        continue
                    if (source_label, target_label) in domain._preamble_transitions:
                        continue
                    ambient = _composed_ambient_transition(
                        self, source_label, target_label
                    )
                    if ambient is None:
                        continue
                    source_chart = domain.atlas()[source_label]
                    target_chart = domain.atlas()[target_label]
                    # A chart whose domain is already the intersection states the
                    # overlap as the whole of itself; a chart read on the whole
                    # submanifold keeps the ambient overlap, read in its own ring.
                    domain.transition_map(
                        source_label,
                        target_label,
                        tuple(
                            _raise_manifold_expression(
                                _engine_manifold_expression(expression), source_chart
                            )
                            for expression in ambient.forward_expressions()
                        ),
                        tuple(
                            _raise_manifold_expression(
                                _engine_manifold_expression(expression), target_chart
                            )
                            for expression in ambient.inverse_expressions()
                        ),
                        source_overlap=tuple(
                            _raise_manifold_expression(
                                _engine_manifold_expression(expression), source_chart
                            )
                            for expression in (
                                ambient.source_overlap()
                                if source_chart.domain() is domain
                                else ()
                            )
                        ),
                        target_overlap=tuple(
                            _raise_manifold_expression(
                                _engine_manifold_expression(expression), target_chart
                            )
                            for expression in (
                                ambient.target_overlap()
                                if target_chart.domain() is domain
                                else ()
                            )
                        ),
                    )
            return domain

        def open_submanifold_inclusion(self, open_manifold):
            pass

        def transition_map(
            self,
            source_label,
            target_label,
            forward_expressions,
            inverse_expressions,
            source_overlap=(),
            target_overlap=(),
        ):
            r"""Record the coordinate change between the charts ``U_s`` and ``U_t`` on ``U_s \cap U_t``.

            A transition map of an atlas is the homeomorphism
            ``phi_t o phi_s^{-1} : phi_s(U_s \cap U_t) -> phi_t(U_s \cap U_t)``
            (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  Its
            domain is the overlap read in the source chart, given by
            ``source_overlap``: functions on ``U_s`` whose common nonvanishing
            locus is ``U_s \cap U_t``.  ``target_overlap`` gives the same open
            set in ``U_t``.  Empty families state that the overlap is the
            whole chart.  The inverse expressions are the coordinate change
            ``phi_s o phi_t^{-1}``; construction trusts the caller that the two
            are mutually inverse on the overlap.
            """
            source = self.atlas()[source_label]
            target = self.atlas()[target_label]
            forward_expressions = _admit_manifold_expression_family(
                forward_expressions,
                source,
                name=f"Coordinate change {source_label} to {target_label}",
            )
            inverse_expressions = _admit_manifold_expression_family(
                inverse_expressions,
                target,
                name=f"Coordinate change {target_label} to {source_label}",
            )
            source_overlap = _admit_manifold_expression_family(
                source_overlap,
                source,
                name=f"Overlap of {source_label} with {target_label} in {source_label}",
            )
            target_overlap = _admit_manifold_expression_family(
                target_overlap,
                target,
                name=f"Overlap of {source_label} with {target_label} in {target_label}",
            )
            if int(forward_expressions.cardinality()) != self.dimension():
                raise ValueError(
                    f"the coordinate change {source_label} -> {target_label} on {self} must "
                    f"give {self.dimension()} coordinate expressions, one per dimension, but "
                    f"{forward_expressions.cardinality()} were given"
                )
            if int(inverse_expressions.cardinality()) != self.dimension():
                raise ValueError(
                    f"the inverse coordinate change {target_label} -> {source_label} on "
                    f"{self} must give {self.dimension()} coordinate expressions, one per "
                    f"dimension, but {inverse_expressions.cardinality()} were given"
                )
            engine_transition = _engine_manifold_chart(source).transition_map(
                _engine_manifold_chart(target),
                tuple(
                    _engine_manifold_expression(expression)
                    for expression in forward_expressions
                ),
                restrictions1=_engine_nonvanishing_conditions(source_overlap),
                restrictions2=_engine_nonvanishing_conditions(target_overlap),
            )
            engine_transition.set_inverse(
                *(
                    _engine_manifold_expression(expression)
                    for expression in inverse_expressions
                ),
                check=False,
            )
            transition = ManifoldAtlasTransition(
                source,
                target,
                engine_transition,
                forward_expressions,
                inverse_expressions,
                source_overlap,
                target_overlap,
            )
            reverse = transition.inverse()
            self._preamble_transitions[source_label, target_label] = transition
            self._preamble_transitions[target_label, source_label] = reverse
            return transition

        def transition(self, source_label, target_label):
            assert (source_label, target_label) in self._preamble_transitions, (
                f"{self} has no transition map from the chart {source_label!r} to the "
                f"chart {target_label!r}: none was defined with transition_map"
            )
            return self._preamble_transitions[source_label, target_label]

        def transitions(self):
            index_set = finite_ordered_set(tuple(self._preamble_transitions))
            return finite_indexed_family(
                index_set,
                lambda pair: self._preamble_transitions[pair],
                description=lambda self=self: f"Atlas transitions of {self}",
            )

        def _repr_(self):
            return (
                f"{self.dimension()}-dimensional {self.regularity()} manifold "
                f"{self.manifold_name()}"
            )


class DifferentiableManifoldMor(CategoricalMor):
    r"""Chartwise differentiable maps at the degree admitted by their endpoints."""

    class ElementMethods:
        def __init__(self, parent, topological_map, chart_maps, degree):
            Morphism.__init__(self, parent)
            self._topological_map = topological_map
            self._chart_maps = chart_maps
            self._degree = degree

        def underlying_topological_morphism(self):
            return self._topological_map

        def chart_maps(self):
            return self._chart_maps

        def degree(self):
            return self._degree

        def _call_(self, point):
            return self._topological_map(point)

        def weaken_to(self, degree):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, topological_map, chart_maps, degree):
        pass

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("a differentiable identity requires the same source and target")
        pass


class DifferentiableManifoldMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = DifferentiableManifoldMor


class SmoothManifoldMor(CategoricalMor):
    r"""Chartwise smooth maps between selected smooth real manifolds.

    A smooth map ``f : X -> Y`` is given by its coordinate representations
    ``f_{st} = psi_t o f o phi_s^{-1}``, one for each pair of charts ``(s, t)``
    whose source charts ``U_s`` cover ``X`` (Lee, *Introduction to Smooth
    Manifolds*, 2nd ed., Ch. 2).  A representation is a tuple of sections of
    the source chart's ring of functions, one per coordinate of the target
    chart: the value of the map at a point is read from the representation on
    the chart that point is given in, and its composite with a second map is
    the substitution of that map's representation in it.
    """

    class ElementMethods:
        def __init__(self, parent, representations, domains):
            self._representations = representations
            self._representation_domains = domains
            self._map_of_points = Sets().Mor(parent.domain(), parent.codomain())(
                lambda point: self._evaluate_point(point)
            )
            OwnedSetMorphism.__init__(self, parent, self._map_of_points)

        def underlying_topological_morphism(self):
            return self._map_of_points

        def chart_maps(self):
            r"""The coordinate representations of this map, indexed by the chart-label pairs they are given on."""
            return self._representations

        def chart_map(self, source_label, target_label):
            r"""The coordinates of the target chart ``target_label``, as sections on the source chart ``source_label``."""
            return self._representations[source_label, target_label]

        def chart_map_domain(self, source_label, target_label):
            r"""The sections on the source chart whose common nonvanishing locus is where the representation holds.

            A coordinate representation need not hold on the whole of its
            source chart: the map it states is defined where the sections it was
            obtained from do not vanish -- a change of coordinates is defined on
            the overlap of two charts, and the representation restated through it
            holds there.  The empty family is the whole chart.
            """
            return self._representation_domains[source_label, target_label]

        def _representation_at(self, source_label):
            r"""The target chart, the representation and its domain on the source chart ``source_label``, or ``None`` when the map is written on another chart."""
            pairs = tuple(
                pair for pair in self._representations.keys() if pair[0] == source_label
            )
            assert len(pairs) <= 1, (
                f"cannot read {self} on the chart {source_label!r}: the map has "
                f"{len(pairs)} coordinate representations whose source chart it is, and the "
                f"value of a point is read off the one on the chart the point is given in"
            )
            if not pairs:
                return None
            written_source, target_label = pairs[0]
            return (
                target_label,
                self.chart_map(written_source, target_label),
                self.chart_map_domain(written_source, target_label),
            )

        def _representation_on(self, source_label):
            r"""The target chart, the representation and its domain that the map has on the source chart ``source_label``."""
            representation = self._representation_at(source_label)
            assert representation is not None, (
                f"cannot read {self} on the chart {source_label!r}: the map has no coordinate "
                f"representation whose source chart it is, and the value of a point is read off "
                f"the one on the chart the point is given in"
            )
            return representation

        def _representation_written_on(self, source_label):
            r"""The representation on the chart ``source_label``, restated there through the atlas change of coordinates when the map is written on another chart.

            A map written on the chart ``m'`` of its domain is the same map read in
            the chart ``m``, wherever the coordinate change ``m -> m'`` is defined:
            ``f_{mt} = f_{m't} o (phi_{m'} o phi_m^{-1})``, and the change is the
            atlas transition from ``m`` to ``m'``.  The restated representation
            holds where that change does, which the atlas states by the
            transition's source overlap, and where the representation on ``m'``
            already held, read through the same change; both are carried as the
            restated representation's domain.
            """
            written = self._representation_at(source_label)
            if written is not None:
                return written
            changes = tuple(
                pair
                for pair in self.domain().transitions().keys()
                if pair[0] == source_label and self._representation_at(pair[1]) is not None
            )
            assert len(changes) == 1, (
                f"cannot restate {self} on the chart {source_label!r}: the map is written on "
                f"the source charts {tuple(pair[0] for pair in self._representations.keys())}, "
                f"and {self.domain()} states {len(changes)} changes of coordinates from the "
                f"chart {source_label!r} to one of them"
            )
            alternative_label = changes[0][1]
            target_label, expressions, domain = self._representation_on(alternative_label)
            change = self.domain().transition(source_label, alternative_label)
            source = self.domain().atlas()[source_label]
            alternative = self.domain().atlas()[alternative_label]

            def restated(sections):
                return tuple(
                    _raise_manifold_expression(_engine_manifold_expression(section), source)
                    for section in _substitute_chart_coordinates(
                        sections, alternative, change.forward_expressions()
                    )
                )

            return (
                target_label,
                restated(expressions),
                tuple(change.source_overlap()) + restated(domain),
            )

        def _evaluate_point(self, point):
            r"""The point of the codomain that a point of the domain maps to.

            The point is read in the chart it is given in, which is the source
            chart of the map's representation there; each of that
            representation's sections is a coordinate of the target chart, so
            the values of the sections at the point are the coordinates of the
            image, and the image is the codomain's point with them in that
            target chart.
            """
            source_point = self.domain()(point)
            label = source_point.chart().label()
            target_label, representation, where = self._representation_on(label)
            field = self.domain().coordinate_field()
            decisions = tuple(ask(section(source_point) != field.zero()) for section in where)
            assert all(decision is True for decision in decisions), (
                f"cannot evaluate {self} at {source_point}: its representation on the chart "
                f"{label!r} is stated where {tuple(where)} do not vanish, and one of them "
                f"vanishes there or its value is undecided"
            )
            values = tuple(section(source_point) for section in representation)
            return self.codomain().point(values, target_label)

        def _call_(self, point):
            return self._map_of_points(point)

        def weaken_to(self, degree):
            pass

        def as_ck_morphism(self):
            pass

        def __mul__(self, other):
            r"""Return the composite ``self o other`` of smooth maps ``Z -> X -> Y``.

            On the source chart of ``other`` its representation states the
            coordinates of the middle manifold ``X``; substituting those for the
            coordinates of ``self``'s representation on that same chart states
            the coordinates of the composite's target, so the composite is the
            map those substituted sections determine.  When ``self`` is written
            on another chart of that middle manifold, it is first restated on
            the chart ``other`` states its values in, through the atlas change
            of coordinates (:meth:`_representation_written_on`), which is what
            restricts a map of a manifold to the open submanifold its chart is
            the domain of.
            """
            assert other.codomain() is self.domain(), (
                f"cannot compose {self} with {other}: the codomain {other.codomain()} of the "
                f"first map is not the domain {self.domain()} of the second"
            )
            representations = {}
            domains = {}
            for source_label, middle_label in other.chart_maps().keys():
                inner = other.chart_map(source_label, middle_label)
                inner_domain = other.chart_map_domain(source_label, middle_label)
                target_label, outer, outer_domain = self._representation_written_on(
                    middle_label
                )
                source = other.domain().atlas()[source_label]
                middle = self.domain().atlas()[middle_label]

                def written(sections):
                    return tuple(
                        _raise_manifold_expression(
                            _engine_manifold_expression(section), source
                        )
                        for section in _substitute_chart_coordinates(sections, middle, inner)
                    )

                representations[source_label, target_label] = written(outer)
                domains[source_label, target_label] = tuple(inner_domain) + written(
                    outer_domain
                )
            return other.domain().Mor(self.codomain())(representations, domains=domains)

    def _element_constructor_(self, representations, *, domains=None):
        r"""Return the smooth map whose coordinate representations are ``representations``.

        ``representations`` maps a pair ``(s, t)`` of chart labels to the tuple
        of sections of the source chart ``s`` of the domain that are the
        coordinates of the target chart ``t`` of the codomain.  Each section is
        admitted by the source chart's own ring of functions, and there is one
        representation per source chart, so that the value of a point is read
        off the representation on the chart the point is given in.  The caller
        states that the source charts cover the domain: no finite set of charts
        is decided to cover a manifold here.

        ``domains`` maps a pair to the sections of that same source chart whose
        common nonvanishing locus is where the representation holds; a pair it
        omits holds on the whole chart.
        """
        domain = self.domain()
        codomain = self.codomain()
        domains = {} if domains is None else dict(domains)
        assert set(domains) <= set(representations), (
            f"cannot give the domain of a coordinate representation of a map "
            f"{domain} -> {codomain} that is not stated: {tuple(domains)} are not among "
            f"the chart pairs {tuple(representations)}"
        )
        admitted = {}
        admitted_domains = {}
        for pair, expressions in representations.items():
            source_label, target_label = pair
            assert source_label in tuple(domain.chart_labels()), (
                f"cannot represent a map from {domain}: it has the charts "
                f"{tuple(domain.chart_labels())} and not {source_label!r}"
            )
            assert target_label in tuple(codomain.chart_labels()), (
                f"cannot represent a map to {codomain}: it has the charts "
                f"{tuple(codomain.chart_labels())} and not {target_label!r}"
            )
            assert source_label not in tuple(label for label, _target in admitted), (
                f"cannot represent a map from {domain} by two coordinate representations on "
                f"the chart {source_label!r}: a point is given in one chart, and its value is "
                f"read off the one representation on that chart"
            )
            values = _admit_manifold_expression_family(
                expressions,
                domain.atlas()[source_label],
                name=(
                    f"Coordinates of the chart {target_label} on the chart {source_label} "
                    f"of a smooth map to {codomain}"
                ),
            )
            assert values.cardinality() == codomain.dimension(), (
                f"cannot represent a map to {codomain} by the coordinates {tuple(values)}: a "
                f"map to a manifold of dimension {codomain.dimension()} has "
                f"{codomain.dimension()} coordinate functions, and {values.cardinality()} "
                f"were given"
            )
            admitted[pair] = values
            admitted_domains[pair] = _admit_manifold_expression_family(
                domains.get(pair, ()),
                domain.atlas()[source_label],
                name=(
                    f"Domain of the coordinate representation {source_label} to "
                    f"{target_label} of a smooth map to {codomain}"
                ),
            )
        assert admitted, (
            f"cannot construct a smooth map {domain} -> {codomain} that states no "
            f"coordinate representation: its value at every point would be unstated"
        )
        pairs = finite_ordered_set(tuple(admitted))
        return self.element_class(
            self,
            indexed_family(
                pairs,
                lambda pair: admitted[pair],
                name=f"Coordinate representations of a smooth map {domain} -> {codomain}",
            ),
            indexed_family(
                pairs,
                lambda pair: admitted_domains[pair],
                name=f"Domains of the coordinate representations of a smooth map "
                f"{domain} -> {codomain}",
            ),
        )

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("a smooth identity requires the same source and target")
        pass


class SmoothManifoldMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SmoothManifoldMor


class _SmoothCkPresentationFunctor(Functor):
    r"""Place legacy smooth objects and maps in the ``C^∞`` category."""

    def __init__(self, source):
        from sage_extensions.categories.real_ck_manifolds import RealCkManifolds

        super().__init__(source, RealCkManifolds(Infinity))

    def _apply_object(self, manifold):
        return manifold.as_ck_manifold()

    def _apply_morphism(self, morphism):
        return morphism.as_ck_morphism()


class _DifferentiableTopologyFunctor(Functor):
    r"""Forget differentiability on exact manifolds and maps."""

    def __init__(self, source):
        super().__init__(source, TopologicalManifolds())

    def _apply_object(self, manifold):
        return manifold.underlying_topological_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_topological_morphism()


class _SmoothFiniteDegreeFunctor(Functor):
    r"""Forget smoothness to a selected finite ``C^k`` degree."""

    def __init__(self, source, degree):
        from sage_extensions.categories.real_ck_manifolds import RealCkManifolds

        super().__init__(source, RealCkManifolds(degree))

    def _apply_object(self, manifold):
        return manifold.weaken_to(self.codomain().degree())

    def _apply_morphism(self, morphism):
        return morphism.weaken_to(self.codomain().degree())


class DifferentiableManifolds(OwnedCategory):
    r"""Owned real differentiable manifolds.

    The direct constructor records a finite positive ``C^k`` degree.  Smooth
    manifolds form the represented subcategory below and therefore belong here
    as well.
    """

    _MorCategory = DifferentiableManifoldMorCategoryConstruction

    def super_categories(self):
        return [TopologicalManifolds()]

    @classmethod
    def _repr_object_names(cls):
        return "differentiable manifolds"

    def an_object(self):
        return self(1, "M_C1", 1)

    def DimensionAtMost(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

        return ManifoldsOfDimensionAtMost(self, dimension)

    def PureDimension(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

        return PureDimensionalManifolds(self, dimension)

    def on(self, topological_manifold, degree, atlas):
        r"""Place the exact topological manifold under a finite-degree real atlas."""
        pass

    @cached_method
    def forget_topology(self):
        return _DifferentiableTopologyFunctor(self)

    class ParentMethods:
        def underlying_topological_manifold(self):
            pass

    def _call_(self, dimension, name, differentiability_degree):
        dimension = int(dimension)
        degree = int(differentiability_degree)
        if dimension <= 0:
            raise ValueError(
                f"cannot construct a differentiable manifold {name} of dimension "
                f"{dimension}: the dimension must be positive"
            )
        if degree <= 0:
            raise ValueError(
                f"cannot construct a C^{degree} manifold {name}: a finite "
                f"differentiability degree must be a positive integer"
            )
        engine = _SageManifold(
            dimension,
            str(name),
            structure="differentiable",
            diff_degree=degree,
            unique_tag=object(),
        )
        return _object_of(
            self,
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="differentiable",
            differentiability_degree=degree,
            manifold_field="real",
        )


class SmoothManifolds(OwnedCategory):
    r"""Owned smooth real manifolds.

    A smooth manifold is a ``C^k`` manifold for every ``k``, and it is the
    orbifold whose charts all have trivial group (Thurston, *The Geometry and
    Topology of Three-Manifolds*, Ch. 13).  Both forgetful functors send it
    to the same underlying topological space.
    """

    _MorCategory = SmoothManifoldMorCategoryConstruction

    def super_categories(self):
        from sage_extensions.categories.orbifolds import Orbifolds

        return [DifferentiableManifolds(), Orbifolds()]

    @classmethod
    def _repr_object_names(cls):
        return "smooth manifolds"

    def an_object(self):
        return self(1, "M_smooth")

    def DimensionAtMost(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

        return ManifoldsOfDimensionAtMost(self, dimension)

    def PureDimension(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

        return PureDimensionalManifolds(self, dimension)

    def on(self, topological_manifold, atlas):
        r"""Place the exact manifold under a compatible smooth atlas."""
        pass

    @cached_method
    def as_ck(self):
        return _SmoothCkPresentationFunctor(self)

    @cached_method
    def forget_smoothness(self, degree):
        from sage_extensions.categories.real_ck_manifolds import _real_ck_degree

        degree = _real_ck_degree(degree)
        if degree == Infinity:
            raise ValueError("forgetting smoothness requires a finite C^k degree")
        return _SmoothFiniteDegreeFunctor(self, degree)

    @cached_method
    def forget_topology(self):
        return _DifferentiableTopologyFunctor(self)

    class ParentMethods:
        def open_submanifold_inclusion(self, open_manifold):
            r"""Return the inclusion of an open submanifold that is the domain of one of this manifold's charts.

            An open subset of a smooth manifold, with the restricted atlas, is a
            smooth manifold of the same dimension and class (Lee, *Introduction
            to Smooth Manifolds*, 2nd ed., Example 1.4), so its inclusion is a
            smooth map into this manifold.  The chart it is the domain of
            presents it: read in that chart of the open submanifold and in the
            chart of this manifold it is the domain of, the coordinates of a
            point and of its image are the same, because the two charts are the
            same chart on the same set.  The inclusion is therefore the map
            whose source chart is the submanifold's and whose coordinates in the
            ambient chart are its own coordinates -- not the ambient manifold
            itself, and not a chart of the whole manifold.
            """
            labels = tuple(
                label
                for label in self.chart_labels()
                if self.atlas()[label].domain() is open_manifold
            )
            assert len(labels) == 1, (
                f"cannot include {open_manifold} in {self}: the inclusion is presented by a "
                f"chart that has the open submanifold as its domain, and {self} has "
                f"{len(labels)} charts on it, its charts being "
                f"{tuple(label for label in self.chart_labels())}"
            )
            label = labels[0]
            source = open_manifold.atlas()[label]
            return open_manifold.Mor(self)({(label, label): source.coordinates()})

        def as_ck_manifold(self):
            pass

        def underlying_topological_manifold(self):
            pass

        @cached_method
        def smooth_functions(self):
            r"""``C^oo(M)``: the algebra of smooth real-valued functions on ``M``.

            A smooth function is a map ``M -> R`` of class ``C^oo``, and the
            smooth functions form an ``R``-algebra under the pointwise
            operations (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 2).  The algebra is the owned one: its elements are maps on this
            manifold, evaluated at owned points, and the chart expressions that
            state a derivative are the ones :meth:`smooth_function` retains.
            """
            from sage_extensions.categories.functions.real_functions import C

            return C(Infinity, self, self.coordinate_field())

        def smooth_function(self, expressions):
            r"""The smooth function whose expression in each chart is ``expressions[label]``.

            A smooth function is fixed by its expressions in the charts of an
            atlas, provided they agree where the charts meet: on the overlap of
            two charts each expression is the other read through the coordinate
            change (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).
            The family is checked against every represented transition and
            refused when it fails, so that what is returned is one function on
            the manifold and not one function per chart.

            The expressions are sections of each chart's function ring
            (:meth:`ManifoldAtlasChart.function_ring`); a quotient of two
            sections is stated where its denominator does not vanish
            (:meth:`ManifoldAtlasChart.section_ratio`).
            """
            atlas = self.atlas()
            labels = tuple(expressions)
            extra = tuple(label for label in labels if label not in self.chart_labels())
            assert not extra, (
                f"a smooth function on {self} is stated on the charts of the manifold, and the "
                f"expressions given for {extra} are on charts it does not have"
            )
            assert _chart_family_covers(self, labels), (
                f"a smooth function on {self} is stated on a cover of the manifold, and the "
                f"charts {labels} do not cover it: a chart of the atlas lies inside none of them, "
                f"so its points would have no value"
            )
            admitted = {
                label: _admit_manifold_expression(expressions[label], atlas[label])
                for label in labels
            }
            _chartwise_family_agrees(
                self, {label: (admitted[label],) for label in labels}, 0
            )
            return self.smooth_functions()(
                _ChartwiseFunction(
                    self,
                    admitted,
                    {
                        label: _engine_manifold_expression(admitted[label])
                        for label in labels
                    },
                )
            )

        @cached_method
        def tangent_bundle(self):
            r"""``TM``, the tangent bundle of ``M``, as an owned smooth vector bundle.

            The tangent space ``T_pM`` is the space of derivations of the algebra
            of germs of smooth functions at ``p`` (Lee, *Introduction to Smooth
            Manifolds*, 2nd ed., Ch. 3), so the disjoint union of the tangent
            spaces is a smooth vector bundle of rank ``dim(M)`` whose sections
            are the vector fields, and those sections are exactly the
            derivations of ``C^oo(M)`` (Lee, Ch. 3 and Ch. 10).  Whether the
            bundle is trivial is a separate question: a frame is a datum a
            caller states, never a fact read off a list of charts.
            """
            from sage_extensions.categories.vector_bundles import SmoothVectorBundles

            return SmoothVectorBundles(self).tangent_bundle()

        def weaken_to(self, degree):
            pass

    def _call_(self, dimension, name):
        dimension = int(dimension)
        if dimension <= 0:
            raise ValueError(
                f"cannot construct a smooth manifold {name} of dimension {dimension}: "
                f"the dimension must be positive"
            )
        engine = _SageManifold(
            dimension,
            str(name),
            structure="smooth",
            unique_tag=object(),
        )
        return _object_of(
            self,
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="smooth",
            differentiability_degree=Infinity,
            manifold_field="real",
        )

    @cached_method
    def sphere(self, dimension, name=None):
        r"""The unit sphere ``S^n = {x in R^{n+1} : |x| = 1}``, a compact smooth manifold of dimension ``n``.

        The atlas is the stereographic one: ``U_N = S^n - {N}`` and
        ``U_S = S^n - {S}``, projected from the north and the south pole onto
        the equatorial ``R^n``, with coordinate change ``y = x/|x|^2`` on
        ``U_N cap U_S``, where ``|x|^2 != 0`` (Lee, *Introduction to Smooth
        Manifolds*, 2nd ed., Ch. 1).  ``S^n`` is closed and bounded in
        ``R^{n+1}``, so it is compact.  The chart labels are ``U_N`` and
        ``U_S``, with coordinates ``x1, ..., xn`` and ``y1, ..., yn``.  Engine
        adapter: SageManifolds' open subsets, charts and transition maps, the
        atlas of its ``Sphere``.
        """
        dimension = int(dimension)
        if name is None:
            name = f"S^{dimension}"
        assert dimension > 0, (
            f"cannot construct the sphere {name} of dimension {dimension} as a manifold of "
            f"positive dimension"
        )
        engine = _SageManifold(dimension, str(name), structure="smooth", unique_tag=object())
        sphere = _object_of(
            self.Compact(),
            _engine=(SmoothManifolds(), _StandardSphere, None),
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="smooth",
            differentiability_degree=Infinity,
            manifold_field="real",
        )
        north, south = (
            sphere._register_chart(
                label,
                engine.open_subset(label).chart(
                    " ".join(f"{letter}{k}" for k in range(1, dimension + 1))
                ),
            )
            for label, letter in (("U_N", "x"), ("U_S", "y"))
        )

        def inversion(chart):
            r"""The coordinate change ``y = x/|x|^2`` in the coordinates of ``chart``, and its squared norm.

            The squared norm ``|x|^2`` is the pointwise sum of the squares of
            the coordinates, a section of the chart's function ring, and it is
            the function the change is defined away from: the quotient
            ``x_k/|x|^2`` is a section on the open subset where the norm does
            not vanish (:meth:`ManifoldAtlasChart.section_ratio`), which is the
            overlap of the two stereographic charts.
            """
            coordinates = chart.coordinates()
            norm_squared = sum(coordinate**2 for coordinate in coordinates)
            return (
                tuple(
                    chart.section_ratio(coordinate, norm_squared)
                    for coordinate in coordinates
                ),
                norm_squared,
            )

        forward, north_overlap = inversion(north)
        inverse, south_overlap = inversion(south)
        sphere.transition_map(
            "U_N", "U_S", forward, inverse,
            source_overlap=(north_overlap,), target_overlap=(south_overlap,),
        )
        engine.declare_union(engine.subsets())
        return sphere


class _StandardSphere:
    r"""The unit sphere ``S^n``, with the homotopy groups that are known in closed form; a realization, not a category.

    ``S^n`` is path connected for ``n >= 1``, so ``pi_k(S^n, x)`` does not
    depend on the base point ``x`` up to isomorphism, and one module per
    degree serves every base point (Hatcher, *Algebraic Topology*, §4.1).
    """

    def _an_element_(self):
        r"""The south pole: the origin of the chart ``U_N``, stereographic projection from the north pole."""
        return self.point((0,) * self.dimension(), "U_N")

    def _homotopy_group_module(self, base_point, degree):
        r"""``pi_k(S^n, x)`` for ``k < n``, ``k = n``, and ``(n, k) = (2, 3)``.

        ``pi_k(S^n) = 0`` for ``k < n`` (Hatcher, Corollary 4.9);
        ``pi_n(S^n) = ZZ iota_n``, generated by the class of the identity
        (Corollary 4.25); ``pi_3(S^2) = ZZ eta``, generated by the Hopf map
        ``eta: S^3 -> S^2`` (Example 4.51), with ``eta`` the generator of
        Hopf invariant ``1`` (§4.B).  Every other degree is a frontier.
        """
        return self._homotopy_group_in_degree(int(degree))

    @cached_method
    def _homotopy_group_in_degree(self, degree):
        sphere_dimension = int(self.dimension())
        integers = _owned_integers()
        match degree:
            case _ if 1 <= degree < sphere_dimension:
                labels = ()
            case _ if degree == sphere_dimension:
                labels = (f"iota_{sphere_dimension}",)
            case 3 if sphere_dimension == 2:
                labels = ("eta",)
            case _:
                assert False, (
                    f"pi_{degree}({self}) is not presented: the homotopy groups of S^{sphere_dimension} "
                    f"are known here in degrees 1 to {sphere_dimension}"
                    + (" and 3" if sphere_dimension == 2 else "")
                )
        return integers.free_module(finite_ordered_set(labels))

    @cached_method
    def singular_cohomology(self, coefficients):
        r"""``H^*(S^n; R) = R[s]/(s^2)`` with ``|s| = n``.

        ``H^k(S^n; R)`` is ``R`` for ``k = 0, n`` and zero otherwise (Hatcher,
        *Algebraic Topology*, Cor. 2.14 and Thm. 3.2), and the cup square of
        the degree-``n`` class lies in ``H^{2n} = 0``.
        """
        from sage_extensions.categories.algebras.graded_algebras import (
            _truncated_polynomial_graded_algebra,
        )

        return _truncated_polynomial_graded_algebra(coefficients, int(self.dimension()), 1)

    def _fundamental_group_at(self, base_point):
        r"""``pi_1(S^n, x) = 1`` for ``n >= 2`` (Hatcher, Corollary 4.9)."""
        from sage_extensions.categories.group.groups import OwnedGroups

        assert int(self.dimension()) >= 2, (
            f"pi_1({self}) is infinite cyclic (Hatcher, Theorem 1.7), and the infinite cyclic group "
            "is not presented here as a group"
        )
        return OwnedGroups().C(1)

    def _whitehead_pairing(self, base_point, left_degree, right_degree):
        r"""``pi_p(S^n) x pi_q(S^n) -> pi_{p+q-1}(S^n)``, where the factors and the values are known.

        A factor that is zero gives the zero pairing.  On ``S^1`` the product
        ``pi_1 x pi_1 -> pi_1`` is the commutator, which is trivial because
        ``pi_1(S^1)`` is abelian.  On ``S^2``, ``[iota_2, iota_2] = 2 eta``:
        ``[iota_2, iota_2]`` is the attaching map of the 4-cell of ``J(S^2)``,
        whose Hopf invariant is ``2`` (Hatcher, Example 4.52 and §4.B), the
        Hopf invariant is a homomorphism ``pi_3(S^2) -> ZZ``
        (Proposition 4B.1), and ``H(eta) = 1``.
        """
        from sage_extensions.categories.modules.pure.modules import BilinearMap

        left_degree, right_degree = int(left_degree), int(right_degree)
        left = self._homotopy_group_module(base_point, left_degree)
        right = self._homotopy_group_module(base_point, right_degree)
        target = self._homotopy_group_module(base_point, left_degree + right_degree - 1)
        sphere_dimension = int(self.dimension())
        match (left_degree, right_degree):
            case _ if left.module_generating_set().is_empty() is True or right.module_generating_set().is_empty() is True:
                images = {}
            case (1, 1) if sphere_dimension == 1:
                images = {("iota_1", "iota_1"): target.zero()}
            case (2, 2) if sphere_dimension == 2:
                eta = target.module_generator("eta")
                images = {("iota_2", "iota_2"): eta + eta}
            case _:
                assert False, (
                    f"the Whitehead product pi_{left_degree} x pi_{right_degree} -> "
                    f"pi_{left_degree + right_degree - 1} of {self} is not presented"
                )
        return BilinearMap(left, right, target, images)


class RiemannianManifoldMor(CategoricalMor):
    r"""Smooth maps preserving the selected Riemannian metrics."""

    class ElementMethods:
        def __init__(self, parent, smooth_map):
            Morphism.__init__(self, parent)
            self._smooth_map = smooth_map

        def underlying_smooth_morphism(self):
            return self._smooth_map

        def _call_(self, point):
            return self._smooth_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, smooth_map):
        pass

    @object_level
    def identity(self):
        pass


class RiemannianManifoldMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RiemannianManifoldMor


class _RiemannianSmoothFunctor(Functor):
    r"""Forget the selected metric on objects and local isometries."""

    def __init__(self, source):
        super().__init__(source, SmoothManifolds())

    def _apply_object(self, manifold):
        return manifold.underlying_smooth_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_morphism()


class RiemannianManifolds(OwnedCategory):
    r"""Smooth real manifolds ``(M, g)`` with a chosen Riemannian metric ``g``.

    The metric ``g`` is a smooth section of ``Sym^2 T^*M`` that is positive
    definite on every tangent space ``T_p M`` (Helgason, *Differential
    Geometry, Lie Groups, and Symmetric Spaces*, Ch. I, §9; Mathlib
    ``Mathlib/Topology/VectorBundle/Riemannian.lean``, ``RiemannianBundle``).
    A smooth manifold admits many metrics, so the metric is chosen data.
    ``forget_metric()`` sends the structured object to its selected smooth
    manifold ``M``.

    A morphism ``(M, g) -> (N, h)`` is a smooth map ``f`` with ``f^* h = g``,
    a local isometry.  ``isometry_group()`` is the automorphism group of
    ``(M, g)`` in this map category.

    A Riemannian manifold is a smooth manifold, so ``SmoothManifolds()`` is a
    supercategory and the smooth structure's construction data — the engine
    manifold ``M`` and its dimension, name, structure, differentiability
    degree and coordinate field — is read by
    ``TopologicalManifolds.ParentMethods``.  It is also the Riemannian
    orbifold whose charts have trivial group, so ``RiemannianOrbifolds()`` is
    its other supercategory; an orbifold with a chart of nontrivial group is
    not a manifold and declares only the orbifold category.
    """

    _MorCategory = RiemannianManifoldMorCategoryConstruction

    def super_categories(self):
        from sage_extensions.categories.orbifolds import RiemannianOrbifolds

        return [SmoothManifolds(), RiemannianOrbifolds()]

    @classmethod
    def _repr_object_names(cls):
        return "Riemannian manifolds"

    def an_object(self):
        r"""The Euclidean line ``(R, dx^2)``.

        The space is the smooth line ``R`` with its one global chart ``x``: a
        smooth structure is ``SmoothManifolds()``'s data and not this
        category's, so it is taken from there.  The metric is ``dx (x) dx``,
        carried in that chart's coordinates as the single Gram entry ``1``,
        the constant section of ``C^inf(R, RR)`` the formula ``g(d/dx, d/dx)``
        reads.
        """
        line = SmoothManifolds()(1, "R")
        line.chart("x", "x")
        charts = line.chart_labels()
        metric = indexed_family(
            charts,
            lambda label: ((line.atlas()[label].function_ring().one(),),),
            name="Gram matrix of dx (x) dx in each chart of the line",
        )
        return self(line, metric)

    def _call_(self, manifold, metric):
        r"""Select ``(M, g)`` from a smooth manifold ``M`` and the metric's coordinates.

        ``metric`` is a finite indexed family over the chart labels of ``M``
        whose value at a label is the matrix ``(g(d/dx_i, d/dx_j))`` of the
        pairings of that chart's coordinate vector fields.  A Riemannian metric
        is a smooth section of ``Sym^2 T^*M``, and on the domain of a chart its
        two arguments are coordinate vector fields, so those entries are
        functions on that domain and they determine ``g`` there.  The metric is
        chosen data — a smooth manifold admits many, none canonical — and it is
        read from the caller and not computed here, as the inner product of a
        ``EuclideanSpaces()`` space is.

        What is checked is what the data are: that ``M`` is a smooth manifold,
        that the family is indexed by exactly the charts of ``M`` (a metric is
        stated in every chart of the atlas, so no chart is left without one),
        and that each matrix is square of ``dim M``, symmetric, with entries in
        the ring of functions the manifold assigns to that chart's domain.
        Positive definiteness — ``g_p(v, v) > 0`` at every point ``p`` and for
        every ``v != 0`` — is a statement about the entries as functions on an
        open subset, not about finitely many of their values, and is the
        hypothesis the caller states by handing the metric over.  So is the
        agreement of the matrices on overlaps of charts, which says that the
        chart transitions are isometries.
        """
        assert manifold in SmoothManifolds(), (
            f"cannot select a Riemannian metric on {manifold}: a Riemannian manifold is a "
            f"smooth manifold with a metric, and {manifold} is an object of "
            f"{manifold.category()}"
        )
        charts = manifold.chart_labels()
        assert tuple(metric.index_set()) == tuple(charts), (
            f"the metric selected on {manifold} is stated in the charts "
            f"{tuple(metric.index_set())}, but a metric on a manifold is stated in every "
            f"chart of its atlas, and the charts of {manifold} are {tuple(charts)}"
        )
        dimension = int(manifold.dimension())
        for label in charts:
            entries = tuple(tuple(row) for row in metric[label])
            ring = manifold.atlas()[label].function_ring()
            assert len(entries) == dimension, (
                f"the metric selected on {manifold} gives {len(entries)} rows in the chart "
                f"{label!r}, but the Gram matrix of that chart's coordinate vector fields "
                f"has one row per dimension, {dimension}"
            )
            for index, row in enumerate(entries):
                assert len(row) == dimension, (
                    f"the metric selected on {manifold} gives {len(row)} entries in row "
                    f"{index} of the chart {label!r}, but the Gram matrix of that chart's "
                    f"coordinate vector fields is square of size {dimension}"
                )
                for column, entry in enumerate(row):
                    assert entry in ring, (
                        f"the metric selected on {manifold} gives the entry "
                        f"{index},{column} of the chart {label!r} as {entry}, which is not "
                        f"a function on that chart's domain: a Gram entry "
                        f"g(d/dx_{index}, d/dx_{column}) is a section of {ring}"
                    )
            for index in range(dimension):
                for column in range(index + 1, dimension):
                    assert entries[index][column] == entries[column][index], (
                        f"the metric selected on {manifold} is not symmetric in the chart "
                        f"{label!r}: the entries {index},{column} and {column},{index} are "
                        f"{entries[index][column]} and {entries[column][index]}, and a "
                        f"Gram matrix is symmetric"
                    )
        space = manifold._with_structure(
            (self,),
            {"underlying_smooth_manifold": manifold, "metric": metric},
        )
        for label in charts:
            space._register_chart(label, _engine_manifold_chart(manifold.atlas()[label]))
        return space

    @cached_method
    def forget_metric(self):
        r"""Forget the selected metric on objects and on their arrows.

        An object ``(M, g)`` becomes the smooth manifold ``M`` it was selected
        on, and a local isometry becomes the smooth map under it: the arrow
        keeps its map and loses the statement ``f^* h = g``.  The globally
        symmetric axiom keeps a metric too, so ``GloballySymmetric()`` declares
        this same functor with itself as its source.
        """
        return _RiemannianSmoothFunctor(self)

    class SubcategoryMethods:
        def GloballySymmetric(self):
            r"""The axiom: every point is an isolated fixed point of an involutive isometry.

            ``(M, g)`` is a Riemannian globally symmetric space when it is a
            connected analytic Riemannian manifold and each ``p in M`` is an
            isolated fixed point of an involutive isometry ``s_p`` of ``(M, g)``
            (Helgason, Ch. IV, §3, Definition; a Riemannian manifold is
            connected by Helgason's Ch. I, §9 definition).
            """
            return self._with_axiom("GloballySymmetric")

    class ParentMethods:
        def __init__(
            self,
            metric=None,
            underlying_smooth_manifold=None,
            **rest,
        ) -> None:
            r"""Record the selected metric and the smooth manifold it is selected on.

            ``metric`` is the family ``chart label |-> (g(d/dx_i, d/dx_j))`` of
            :meth:`RiemannianManifolds._call_`: the metric's Gram matrix in
            each chart of the atlas, whose entries are sections of the ring of
            functions on that chart's domain.  ``underlying_smooth_manifold``
            is the smooth manifold ``M`` the metric was selected on, which is
            what :meth:`forget_metric` returns.

            Neither is read off the object: a metric is chosen data of the
            object, and an object constructed without one — the symmetric
            space ``noncompact_type`` states, whose ``G``-invariant metric it
            does not construct — carries ``None`` and refuses to answer for it.
            """
            self._preamble_metric = metric
            self._preamble_underlying_smooth_manifold = underlying_smooth_manifold
            super().__init__(**rest)

        def underlying_smooth_manifold(self):
            r"""Return ``M``, the smooth manifold this object selects its metric on."""
            match self._preamble_underlying_smooth_manifold:
                case None:
                    raise ValueError(
                        f"{self} has no underlying smooth manifold: it was constructed "
                        f"from a manifold's own data and not from an object of "
                        f"SmoothManifolds(), so no one object is the manifold to forget "
                        f"the metric to"
                    )
                case manifold:
                    return manifold

        def riemannian_metric(self):
            r"""Return the chosen metric ``g``, a positive definite section of ``Sym^2 T^*M``.

            It is returned as it was stated: the family of its Gram matrices in
            the charts it is stated in, ``chart label |-> (g(d/dx_i, d/dx_j))``
            — the charts of the atlas for an object selected by this category,
            and the charts of the ambient manifold for an open submanifold of
            it, whose metric is the restriction of the ambient one.
            """
            match self._preamble_metric:
                case None:
                    raise ValueError(
                        f"{self} has no chosen metric: a Riemannian manifold's metric is "
                        f"chosen data, and this object was constructed without it"
                    )
                case metric:
                    return metric

        def _chart_domain_structure(self, label, engine_chart) -> dict:
            r"""The domain of a chart on this manifold carries the restricted metric and its smooth domain.

            An open subset of a Riemannian manifold is a Riemannian manifold
            with the restricted metric (Lee, *Introduction to Smooth
            Manifolds*, 2nd ed., Example 1.4, for the atlas; the metric is
            restricted along the inclusion).  The metric is stated in the
            charts it was stated in on the ambient manifold, which restrict to
            the open subset, so the domain is given that same family; its
            underlying smooth manifold is the domain of the same chart on the
            smooth manifold this one is placed on.
            """
            return {
                "metric": self.riemannian_metric(),
                "underlying_smooth_manifold": self.underlying_smooth_manifold()._chart_domain(
                    label, engine_chart
                ),
            }

        def isometry_group(self):
            r"""Return ``I(M, g)``, the group of isometries ``f: M -> M`` with ``f^* g = g``.

            With the compact open topology it is a locally compact
            topological transformation group of ``M`` (Helgason, Ch. IV,
            Theorem 2.5(a)), an object of ``TopologicalGroups()``.  On a
            Riemannian globally symmetric space it is a Lie transformation
            group of ``M`` (Helgason, Ch. IV, Lemma 3.2), an object of
            ``LieGroups()``.
            """
            pass

    class GloballySymmetric(CategoryWithAxiom):
        r"""Riemannian globally symmetric spaces (Helgason, Ch. IV, §3).

        A connected analytic Riemannian manifold ``(M, g)`` in which each point ``p``
        is an isolated fixed point of an involutive isometry ``s_p``, the
        geodesic symmetry at ``p``.
        """

        @cached_method
        def an_object(self):
            r"""The Euclidean line ``(R, dx^2)``, with its geodesic symmetries ``s_p(x) = 2p - x``.

            Every point ``p`` of the line is an isolated fixed point of the
            involutive isometry ``s_p``, which is the axiom (Helgason, Ch. IV,
            §3, Definition), and the line is analytic, so it is an object of
            this category and not only of the Riemannian manifolds.  The
            metric is the Riemannian level's; what this category adds is the
            statement that the space has the geodesic symmetries.
            """
            return RiemannianManifolds().an_object()._with_structure((self,), {})

        @cached_method
        def forget_metric(self):
            r"""Forget the selected metric: the map from this category to ``SmoothManifolds()``.

            A globally symmetric space is a Riemannian manifold, so this is the
            base category's forgetting functor with this category as its
            source: an object becomes its smooth manifold and an arrow its
            smooth map, and the symmetric structure is not what is forgotten.

            It is declared here as well as on ``RiemannianManifolds`` because an
            axiom category's runtime class carries the base category's
            ``SubcategoryMethods`` and ``subcategory_class``, not the base
            category class: ``an_object`` and ``_call_`` of
            ``RiemannianManifolds`` are not reachable from this category
            either.  A construction stated here is the axiom category's own,
            and its source is this category.
            """
            return _RiemannianSmoothFunctor(self)

        @cached_method
        def noncompact_type(self, satake_diagram):
            r"""Return the irreducible symmetric space ``G/K`` of noncompact type of a real form.

            ``satake_diagram`` is an object of ``SatakeDiagrams()`` with a
            connected Dynkin diagram, classifying a noncompact real form
            ``g_0`` of a complex simple Lie algebra.  ``G`` is a connected Lie
            group with Lie algebra ``g_0`` and finite centre, ``K`` a maximal
            compact subgroup, and ``(g_0, theta)`` with ``theta`` a Cartan
            involution is an orthogonal symmetric Lie algebra of the
            noncompact type (Helgason, Ch. V, §1, Definition; the
            irreducible spaces of this type are listed in Ch. X, §6,
            Table V).

            ``G/K`` is the orbit space of the right action of ``K`` on ``G``:
            the coequalizer in ``TopologicalSpaces()`` of the action and the
            projection ``K x G -> G``, returned by ``orbit_space()`` on the
            object of ``GObjects(K, SmoothManifolds())`` with ``k . g = g k^{-1}``;
            right translation is a diffeomorphism of ``G``, not a group morphism.
            The smooth structure and the ``G``-invariant metric induced by
            the Killing form of ``g_0`` restricted to ``p_0`` place it here.

            The construction is the smooth manifold on the one global chart
            ``Exp: p_0 -> G/K``, a diffeomorphism for noncompact type
            (Helgason, Ch. VI, Theorem 1.1), with coordinates ``x_0, ...``
            on ``p_0``.  ``dim p_0`` and the real rank are read from the
            Satake diagram by the Iwasawa decomposition.  The orbit-space
            route above and the metric are not constructed.
            """
            from sage_extensions.categories.satake_diagrams import SatakeDiagrams

            assert satake_diagram in SatakeDiagrams(), (
                f"cannot construct the symmetric space of noncompact type of {satake_diagram}: "
                f"a noncompact real form of a simple Lie algebra is classified by an object "
                f"of SatakeDiagrams(), and {satake_diagram} is in {satake_diagram.category()}"
            )
            assert satake_diagram.dynkin_diagram().is_connected(), (
                f"cannot construct the irreducible symmetric space of {satake_diagram}: an "
                f"irreducible space comes from a simple Lie algebra, whose Dynkin diagram is "
                f"connected"
            )
            rank, dimension = _symmetric_space_rank_and_dimension(satake_diagram)
            assert rank >= 1, (
                f"{satake_diagram} has every node black, so it is the compact real form, and "
                f"its symmetric space G/K is a point, not of the noncompact type"
            )
            manifold = SmoothManifolds()(int(dimension), "G/K")
            manifold.chart("p0", " ".join(f"x{index}" for index in range(int(dimension))))
            space = manifold._with_structure(
                (self,),
                {
                    "satake_diagram": satake_diagram,
                    "real_rank": rank,
                    "underlying_smooth_manifold": manifold,
                },
                engine=_RealFormSymmetricSpace,
            )
            for label in manifold.chart_labels():
                space._register_chart(label, _engine_manifold_chart(manifold.atlas()[label]))
            return space

        def hyperbolic_space(self, component):
            r"""Return the hyperbolic space ``HH(C^+)`` of a chosen positive-cone component.

            ``component`` is an object of ``PositiveConeComponents(L)`` for a
            lattice ``L`` of signature ``(1, n)``, the component ``C^+`` of
            ``{x in L_RR : q(x) > 0}``.  The result is the hyperboloid
            ``{x in C^+ : q(x) = 1}`` of dimension ``n``, with the metric
            ``-b`` on each tangent space ``x^perp``; it is
            ``SO_0(1, n)/SO(n)``, of Cartan type BDI with ``q = 1`` (Helgason,
            Ch. X, §6, Table V), placed in ``HyperbolicSpaces(n)``.

            Its one global chart ``hyperboloid`` has the coordinates
            ``y_0, ..., y_{n-1}`` of the orthogonal projection of ``x`` to
            ``t^perp``, for ``t`` the timelike vector of ``C^+``: ``x = s t + y``
            with ``s = sqrt((1 - q(y))/q(t)) > 0`` is a diffeomorphism
            ``t^perp_RR -> HH(C^+)``, since ``t^perp`` is negative definite.
            """
            from sage_extensions.categories.hyperbolic_geometry import (
                HYPERBOLOID_CHART,
                HyperbolicSpaces,
            )

            dimension = int(component.lattice().module_rank()) - 1
            manifold = SmoothManifolds()(dimension, f"HH^{dimension}")
            manifold.chart(
                HYPERBOLOID_CHART, " ".join(f"y{index}" for index in range(dimension))
            )
            space = manifold._with_structure(
                (HyperbolicSpaces(dimension),),
                {"component": component, "underlying_smooth_manifold": manifold},
            )
            for label in manifold.chart_labels():
                space._register_chart(label, _engine_manifold_chart(manifold.atlas()[label]))
            return space

        class ParentMethods:
            def geodesic_symmetry(self, point):
                r"""Return ``s_p``, the involutive isometry of ``M`` with isolated fixed point ``p``.

                Domain and codomain are ``M``; ``s_p`` reverses every geodesic
                through ``p`` and its differential at ``p`` is ``-1`` on
                ``T_p M``.
                """
                pass


class HolomorphicMapPresentation:
    r"""The coordinate representations defining one represented holomorphic map.

    A holomorphic map ``f : X -> Y`` is given by its coordinate representations
    ``f_{st} = psi_t o f o phi_s^{-1}`` on ``phi_s(U_s cap f^{-1}(V_t))``, for
    chart pairs ``(s, t)`` whose open sets ``U_s cap f^{-1}(V_t)`` cover ``X``
    (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 2).  The domain of
    each representation, read in ``U_s``, is the common nonvanishing locus of
    its domain functions; the empty family is all of ``U_s``.
    """

    def __init__(self, engine_map, representations, source) -> None:
        self._engine_map = engine_map
        self._representations = {
            pair: (
                _admit_manifold_expression_family(
                    expressions,
                    source.atlas()[pair[0]],
                    name=f"Coordinate representation {pair[0]} to {pair[1]}",
                ),
                _admit_manifold_expression_family(
                    domain,
                    source.atlas()[pair[0]],
                    name=f"Domain of the coordinate representation {pair[0]} to {pair[1]}",
                ),
            )
            for pair, (expressions, domain) in representations.items()
        }

    def _engine_map_crossing(self):
        return self._engine_map

    def chart_pairs(self):
        return finite_ordered_set(tuple(self._representations))

    def coordinate_representation(self, source_label, target_label):
        return self._representations[source_label, target_label][0]

    def representation_domain(self, source_label, target_label):
        return self._representations[source_label, target_label][1]


def _engine_holomorphic_map(morphism):
    r"""Return a holomorphic map's private Sage realization to its composition adapter.

    Protected holomorphic-map contract (\`OWN-05\`--\`OWN-07\`).  The
    implementation endpoint is :meth:\`HolomorphicMap._engine_holomorphic_map\`.
    Its sole external role is exact composition of represented holomorphic
    maps; the resulting Sage map is immediately raised by
    :meth:\`ComplexManifoldMor._from_engine_map\`.
    """
    return morphism._engine_holomorphic_map()


def _substitute_chart_coordinates(expressions, chart, values):
    r"""Substitute ``values`` for the coordinates of ``chart`` in each expression, as sections of its ring."""
    substitutions = {
        _engine_manifold_expression(variable): _engine_manifold_expression(value)
        for variable, value in zip(chart.coordinates(), values, strict=True)
    }
    return tuple(
        _raise_manifold_expression(
            _engine_manifold_expression(expression).subs(substitutions), chart
        )
        for expression in expressions
    )


def _is_zero_chart_formula(formula):
    r"""Whether an engine chart formula is the zero function.

    Engine adapter: the numerator of the normalized symbolic expression is
    read as a polynomial with exact coefficients in ``QQbar``.
    """
    return formula.numerator().polynomial(SageQQbar).is_zero()


def _is_zero_rational_function(section):
    r"""Whether a chart section is the zero function."""
    return _is_zero_chart_formula(_engine_manifold_expression(section))


def _representations_agree(first_map, first_pair, second_map, second_pair):
    r"""Whether two holomorphic maps ``X -> Y`` agree where two of their representations are given.

    Read on ``U_s`` for ``first_pair = (s, t)`` and ``second_pair = (s', t')``,
    the overlap of the two domains is cut out by the domain functions of both
    representations, the overlap ``U_s cap U_{s'}`` and the preimage of
    ``V_t cap V_{t'}``; the maps agree on it when
    ``psi_{t'} psi_t^{-1} o f_{st} = g_{s't'} o phi_{s'} phi_s^{-1}``.  Both
    sides are rational functions on an open subset of ``C^n``, and the
    overlap is the nonvanishing locus of finitely many rational functions on
    it: it is empty when one of them is the zero function, and otherwise a
    nonempty open set, on which two rational functions agree only if they are
    equal.
    """
    source_label, target_label = first_pair
    second_source, second_target = second_pair
    source = first_map.domain()
    target = first_map.codomain()
    first = tuple(first_map.coordinate_representation(source_label, target_label))
    conditions = tuple(first_map.representation_domain(source_label, target_label))
    if second_source == source_label:
        second = tuple(second_map.coordinate_representation(second_source, second_target))
        conditions += tuple(second_map.representation_domain(second_source, second_target))
    else:
        change = source.transition(source_label, second_source)
        middle = source.atlas()[second_source]
        coordinates = tuple(change.forward_expressions())
        second = _substitute_chart_coordinates(
            second_map.coordinate_representation(second_source, second_target),
            middle,
            coordinates,
        )
        conditions += tuple(change.source_overlap()) + _substitute_chart_coordinates(
            second_map.representation_domain(second_source, second_target),
            middle,
            coordinates,
        )
    if second_target != target_label:
        change = target.transition(target_label, second_target)
        chart = target.atlas()[target_label]
        conditions += _substitute_chart_coordinates(change.source_overlap(), chart, first)
        first = _substitute_chart_coordinates(change.forward_expressions(), chart, first)
    if any(_is_zero_rational_function(condition) for condition in conditions):
        return True
    return all(
        _is_zero_chart_formula(
            _engine_manifold_expression(left) - _engine_manifold_expression(right)
        )
        for left, right in zip(first, second, strict=True)
    )


class HolomorphicMap:
    r"""A holomorphic map represented by its coordinate representations in selected charts."""

    def __init__(self, parent, presentation) -> None:
        self._presentation = presentation
        set_map = Sets().Mor(parent.domain(), parent.codomain())(
            lambda point: self._evaluate_point(point)
        )
        super().__init__(parent, set_map)

    def presentation(self):
        return self._presentation

    def chart_pairs(self):
        r"""The chart pairs ``(s, t)`` on which a coordinate representation is given."""
        return self.presentation().chart_pairs()

    def coordinate_representation(self, source_label, target_label):
        r"""``psi_t o f o phi_s^{-1}``, the coordinates of ``V_t`` as functions on ``U_s``."""
        return self.presentation().coordinate_representation(source_label, target_label)

    def representation_domain(self, source_label, target_label):
        r"""Functions on ``U_s`` whose common nonvanishing locus is ``U_s cap f^{-1}(V_t)``."""
        return self.presentation().representation_domain(source_label, target_label)

    def _engine_holomorphic_map(self):
        return self.presentation()._engine_map_crossing()

    def underlying_smooth_morphism(self):
        pass

    def _evaluate_point(self, point):
        r"""Evaluate a coordinate representation whose domain contains the owned source point.

        Engine adapter: the point's coordinates are substituted in the
        domain functions, and a representation applies when none vanishes.
        """
        source_point = self.domain()(point)
        chart = source_point.chart()
        applicable = tuple(
            (source_label, target_label)
            for source_label, target_label in self.chart_pairs()
            if source_label == chart.label()
            and all(
                bool(_engine_manifold_expression(value) != 0)
                for value in _substitute_chart_coordinates(
                    self.representation_domain(source_label, target_label),
                    chart,
                    source_point.coordinates(),
                )
            )
        )
        assert applicable, (
            f"cannot evaluate {self} at {source_point}: no coordinate representation of this "
            f"map is given on a domain containing it in the chart {chart.label()!r}"
        )
        source_label, target_label = applicable[0]
        values = _substitute_chart_coordinates(
            self.coordinate_representation(source_label, target_label),
            chart,
            source_point.coordinates(),
        )
        return self.codomain().point(values, target_label)

    def __mul__(self, other):
        r"""Return the composite ``self o other`` of holomorphic maps ``X -> Y -> Z``.

        On ``U_s cap f^{-1}(V_t) cap f^{-1}g^{-1}(W_u)`` the composite
        ``g o f`` has the coordinate representation ``g_{tu} o f_{st}``.
        """
        assert other.codomain() is self.domain(), (
            f"cannot compose {self} with {other}: the codomain {other.codomain()} of the "
            f"first map is not the domain {self.domain()} of the second"
        )
        representations = {}
        for source_label, middle_label in other.chart_pairs():
            inner = other.coordinate_representation(source_label, middle_label)
            middle = self.domain().atlas()[middle_label]
            for outer_source, target_label in self.chart_pairs():
                if outer_source != middle_label or (source_label, target_label) in representations:
                    continue
                representations[source_label, target_label] = (
                    _substitute_chart_coordinates(
                        self.coordinate_representation(middle_label, target_label), middle, inner
                    ),
                    tuple(other.representation_domain(source_label, middle_label))
                    + _substitute_chart_coordinates(
                        self.representation_domain(middle_label, target_label), middle, inner
                    ),
                )
        return other.domain().Mor(self.codomain())._from_engine_map(
            _engine_holomorphic_map(self) * _engine_holomorphic_map(other),
            representations,
        )

    def __eq__(self, other) -> bool:
        r"""Whether ``self`` and ``other`` are the same holomorphic map ``X -> Y``.

        They are when they agree at every point.  Every point lies in the
        domain of a coordinate representation of each, so they are equal
        exactly when every representation of one agrees with every
        representation of the other on the overlap of their domains.
        """
        return element_parent(other) is self.parent() and all(
            _representations_agree(self, first, other, second)
            for first in self.chart_pairs()
            for second in other.chart_pairs()
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        r"""Hash the holomorphic maps of one set of morphisms alike.

        Equality here is extensional: two presentations are one map when every
        coordinate representation of one agrees with every representation of
        the other on the overlap of their domains.  No datum of one
        presentation is invariant under that, so the set of morphisms is what a
        hash reads, which is the rule of :class:`Sets`.
        """
        return hash(id(self.parent()))

    def _repr_(self):
        return f"Holomorphic map {self.domain()} -> {self.codomain()}"


class ComplexManifoldMor(CategoricalMor):
    ElementMethods = HolomorphicMap

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    @staticmethod
    def _unique_chart(manifold):
        labels = tuple(manifold.chart_labels())
        assert len(labels) == 1, (
            f"cannot write a holomorphic map on {manifold} by polynomial formulas: the "
            f"formulas are taken in a single global chart, but {manifold} has the charts "
            f"{labels}"
        )
        return manifold.atlas()[labels[0]]

    def polynomial(self, coordinate_expressions):
        r"""Construct the holomorphic map defined by polynomial chart formulas."""
        source = self._unique_chart(self.domain())
        target = self._unique_chart(self.codomain())
        expressions = _admit_manifold_expression_family(
            coordinate_expressions,
            source,
            name="Holomorphic-map coordinate expressions",
        )
        if int(expressions.cardinality()) != self.codomain().dimension():
            raise ValueError(
                f"{coordinate_expressions} do not define a holomorphic map {self.domain()} -> "
                f"{self.codomain()}: it needs one expression per coordinate of the codomain, "
                f"that is {self.codomain().dimension()}, but {expressions.cardinality()} "
                f"were given"
            )
        engine_variables = tuple(
            _engine_manifold_expression(variable)
            for variable in source.coordinates()
        )
        engine_expressions = tuple(
            _engine_manifold_expression(expression)
            for expression in expressions
        )
        if any(
            not all(expression.is_polynomial(variable) for variable in engine_variables)
            for expression in engine_expressions
        ):
            raise ValueError(
                f"cannot conclude that {coordinate_expressions} define a holomorphic map "
                f"{self.domain()} -> {self.codomain()}: holomorphicity is known here only "
                f"for formulas polynomial in the coordinates {source.coordinates()}, and "
                f"some formula is not"
            )
        engine = _engine_manifold(self.domain()).diff_map(
            _engine_manifold(self.codomain()),
            engine_expressions if len(engine_expressions) != 1 else engine_expressions[0],
            chart1=_engine_manifold_chart(source),
            chart2=_engine_manifold_chart(target),
        )
        return self._from_engine_map(engine, {(source.label(), target.label()): (expressions, ())})

    def rational(self, representations):
        r"""Construct the holomorphic map with the given rational coordinate representations.

        ``representations`` sends a chart pair ``(s, t)`` to the pair
        ``(expressions, domain)``: the coordinates of ``V_t`` as rational
        functions on ``U_s``, and functions on ``U_s`` whose common
        nonvanishing locus is ``U_s cap f^{-1}(V_t)``.  A rational function
        is holomorphic where its denominator does not vanish.  Construction
        trusts the caller that the denominators do not vanish on the stated
        domains, that the domains cover the source, and that the
        representations agree on overlaps through the atlas transitions.
        """
        engine = _engine_manifold(self.domain()).diff_map(
            _engine_manifold(self.codomain()),
            {
                (
                    _engine_manifold_chart(self.domain().atlas()[source_label]),
                    _engine_manifold_chart(self.codomain().atlas()[target_label]),
                ): tuple(_engine_manifold_expression(expression) for expression in expressions)
                for (source_label, target_label), (expressions, _domain) in representations.items()
            },
        )
        return self._from_engine_map(engine, representations)

    def _from_engine_map(self, engine, representations):
        r"""Raise a private Sage map with its coordinate representations into this Mor object."""
        return self.element_class(
            self, HolomorphicMapPresentation(engine, representations, self.domain())
        )

    @object_level
    @cached_method
    def identity(self):
        r"""The identity, represented on each chart ``U_s`` by its own coordinates."""
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity map from {self.domain()} to {self.codomain()}: an "
                f"identity needs its domain and codomain to be the same complex manifold"
            )
        return self.rational(
            {
                (label, label): (self.domain().atlas()[label].coordinates(), ())
                for label in self.domain().chart_labels()
            }
        )


class ComplexManifoldMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return ComplexManifoldMor


class _ComplexRealificationFunctor(Functor):
    r"""Send complex manifolds and holomorphic maps to their real smooth images."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        pass


class ComplexManifolds(OwnedCategory):
    r"""Finite-dimensional complex analytic manifolds with holomorphic atlases.

    A holomorphic map between open subsets of ``C^n`` and ``C^m`` is real
    analytic, so in particular ``C^infinity``, as a map between open subsets of
    ``R^{2n}`` and ``R^{2m}``.  A holomorphic atlas is therefore a smooth atlas
    of the underlying real manifold, of real dimension twice the complex
    dimension, and a holomorphic map is smooth.  Forgetting the complex
    structure is the functor to ``SmoothManifolds()``.  A complex manifold is
    also the complex orbifold whose charts have trivial group, hence a
    reduced, normal complex analytic space (Grauert--Remmert, *Coherent
    Analytic Sheaves*, Ch. 1); both routes send it to the same smooth
    orbifold.
    """

    _MorCategory = ComplexManifoldMorCategoryConstruction

    def super_categories(self):
        from sage_extensions.categories.orbifolds import ComplexOrbifolds

        return [ComplexOrbifolds()]

    @classmethod
    def _repr_object_names(cls):
        return "complex analytic manifolds"

    def an_object(self):
        return self.affine_space(1, name="C")

    def DimensionAtMost(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

        return ManifoldsOfDimensionAtMost(self, dimension)

    def PureDimension(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

        return PureDimensionalManifolds(self, dimension)

    def on(self, topological_manifold, holomorphic_atlas):
        r"""Place the exact manifold under a compatible holomorphic atlas."""
        pass

    @cached_method
    def realification(self):
        return _ComplexRealificationFunctor(self, SmoothManifolds())

    def _call_(self, dimension, name):
        dimension = int(dimension)
        if dimension <= 0:
            raise ValueError(
                f"cannot construct a complex manifold {name} of complex dimension "
                f"{dimension}: the dimension must be positive"
            )
        engine = _SageManifold(
            dimension,
            str(name),
            field="complex",
            structure="smooth",
            unique_tag=object(),
        )
        return _object_of(
            self,
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="complex analytic",
            differentiability_degree=Infinity,
            manifold_field="complex",
        )

    def affine_space(self, dimension, name=None, coordinate_names=None):
        dimension = int(dimension)
        if name is None:
            name = f"C^{dimension}"
        if coordinate_names is None:
            coordinate_names = tuple(f"z{index}" for index in range(dimension))
        coordinate_names = tuple(str(name) for name in coordinate_names)
        if len(coordinate_names) != dimension:
            raise ValueError(
                f"cannot construct complex affine space {name} of dimension {dimension} "
                f"with the coordinates {coordinate_names}: it needs {dimension} coordinate "
                f"names, one per dimension, but {len(coordinate_names)} were given"
            )
        manifold = self(dimension, name)
        manifold.chart("standard", " ".join(coordinate_names))
        return manifold

    def projective_space(self, dimension, name=None):
        r"""Complex projective space ``CP^n = (C^{n+1} - 0)/C^*``, a compact complex manifold.

        The atlas is the standard one (Griffiths--Harris, *Principles of
        Algebraic Geometry*, Ch. 0, Sec. 1): ``U_i = {x_i != 0}`` with chart ``x_k/x_i`` (``k != i``), and on
        ``U_i \cap U_j`` the holomorphic coordinate change
        ``x_k/x_j = (x_k/x_i)/(x_j/x_i)``.  ``CP^n`` is the image of the
        compact sphere ``S^{2n+1}`` under the quotient map, so it is compact.
        The chart labels are ``U0, ..., Un`` and the coordinates are named
        ``x{k}_over_x{i}``, as on the standard affine charts of ``P^n``.
        Engine adapter: SageManifolds' open subsets, charts and transition
        maps, the pattern of its ``RealProjectiveSpace`` with complex field.
        """
        dimension = int(dimension)
        if name is None:
            name = f"CP^{dimension}"
        assert dimension > 0, (
            f"cannot construct the complex projective space {name} of dimension {dimension}: "
            f"the dimension must be positive"
        )
        engine = _SageManifold(
            dimension, str(name), field="complex", structure="smooth", unique_tag=object(),
        )
        manifold = _object_of(
            self.Compact(),
            topology_data=_ManifoldTopologyData(engine),
            engine_manifold=engine,
            manifold_dimension=dimension,
            manifold_name=str(name),
            manifold_structure="complex analytic",
            differentiability_degree=Infinity,
            manifold_field="complex",
        )
        indices = range(dimension + 1)
        charts = {
            i: manifold._register_chart(
                f"U{i}",
                engine.open_subset(f"U{i}").chart(
                    " ".join(f"x{k}_over_x{i}" for k in indices if k != i)
                ),
            )
            for i in indices
        }
        one = SR.one()

        def homogeneous(i):
            # The engine's symbols for the homogeneous coordinates of a point of
            # U_i, normalized by x_i = 1.
            affine = iter(tuple(_engine_manifold_chart(charts[i])[:]))
            return {k: one if k == i else next(affine) for k in indices}

        for i, j in combinations(indices, 2):
            on_i = homogeneous(i)
            on_j = homogeneous(j)
            manifold.transition_map(
                f"U{i}",
                f"U{j}",
                _raise_manifold_expression_family(
                    tuple(on_i[k] / on_i[j] for k in indices if k != j),
                    charts[i],
                    name=f"Coordinate change U{i} to U{j}",
                ),
                _raise_manifold_expression_family(
                    tuple(on_j[k] / on_j[i] for k in indices if k != i),
                    charts[j],
                    name=f"Coordinate change U{j} to U{i}",
                ),
                source_overlap=_raise_manifold_expression_family(
                    (on_i[j],),
                    charts[i],
                    name=f"Overlap of U{i} with U{j} in U{i}",
                ),
                target_overlap=_raise_manifold_expression_family(
                    (on_j[i],),
                    charts[j],
                    name=f"Overlap of U{i} with U{j} in U{j}",
                ),
            )
        engine.declare_union(engine.subsets())
        return manifold

    def _open_submanifold_data(self, containing_manifold, name, restriction):
        r"""The construction data of the open subset ``{restriction}`` of ``containing_manifold``, cut out in its one chart."""
        assert containing_manifold in self, (
            f"cannot cut out the open submanifold {name} of {containing_manifold}: it "
            f"must be an open subset of a complex manifold, and {containing_manifold} is "
            f"in {containing_manifold.category()}"
        )
        labels = tuple(containing_manifold.chart_labels())
        assert len(labels) == 1, (
            f"cannot cut out the open submanifold {name} of {containing_manifold} by "
            f"{restriction}: the condition is read in a single global chart, but "
            f"{containing_manifold} has the charts {labels}"
        )
        chart = containing_manifold.atlas()[labels[0]]
        engine_open = _engine_manifold(containing_manifold).open_subset(
            str(name),
            coord_def={_engine_manifold_chart(chart): restriction},
        )
        return {
            "topology_data": _ManifoldTopologyData(engine_open),
            "engine_manifold": engine_open,
            "manifold_dimension": containing_manifold.dimension(),
            "manifold_name": str(name),
            "manifold_structure": "complex analytic",
            "differentiability_degree": Infinity,
            "manifold_field": "complex",
            "containing_manifold": containing_manifold,
            "open_restriction": restriction,
            "chart_label": labels[0],
        }

    def open_submanifold(self, containing_manifold, name, restriction):
        r"""Return the open subset of ``containing_manifold`` where ``restriction`` holds in its chart."""
        return _object_of(
            self,
            _engine=(self, _ComplexOpenEngine, None),
            **self._open_submanifold_data(containing_manifold, name, restriction),
        )

    def disc(self, radius=1, name="Delta", containing_manifold=None, *, punctured=False):
        r"""Return the disc ``{|z| < radius}``, or with ``punctured`` the disc ``{0 < |z| < radius}``.

        The disc is cut out in the chart of the one-dimensional
        ``containing_manifold``; omitted, that is a fresh complex line.  The
        radius is an exact positive real number, an element of ``RR``.
        """
        radius = RR(radius)
        assert ask(radius > RR.zero()) is True, (
            f"cannot construct the disc {name} of radius {radius}: the radius must be "
            f"a positive real number"
        )
        if containing_manifold is None:
            containing_manifold = self.affine_space(
                1, name=f"{name}_line", coordinate_names=("z",)
            )
        assert containing_manifold.dimension() == 1, (
            f"cannot cut out the disc {name} in {containing_manifold}: a disc lies in a "
            f"complex manifold of dimension one, and {containing_manifold} has dimension "
            f"{containing_manifold.dimension()}"
        )
        z = containing_manifold.atlas()[
            tuple(containing_manifold.chart_labels())[0]
        ].coordinate(0)
        engine_z = _engine_manifold_expression(z)
        match punctured:
            case True:
                restriction = (abs(engine_z) < radius.expression(), engine_z != 0)
            case False:
                restriction = abs(engine_z) < radius.expression()
        return _object_of(
            self,
            _engine=(self, _ComplexDiscEngine, None),
            disc_radius=radius,
            punctured=punctured,
            **self._open_submanifold_data(containing_manifold, name, restriction),
        )

    class ElementMethods(TopologicalManifolds.ElementMethods):
        r"""A point of a complex manifold, given by its coordinates in a labelled chart.

        A point of a complex manifold is a point of a manifold, with its
        coordinates taken in ``CC`` (:meth:`coordinate_field`); the element is
        the manifold point it is, inherited rather than written again.
        """

    class ParentMethods(TopologicalManifolds.ParentMethods):
        r"""A complex manifold is a manifold whose charts take values in ``CC``.

        A holomorphic chart ``phi : U -> CC^n`` is a homeomorphism onto an open
        subset of ``CC^n``, so the chart, atlas, point, transition and open
        subset operations of a manifold are this object's operations, and the
        only datum that changes is the field the coordinates lie in
        (:meth:`coordinate_field`).  They are inherited from the manifold
        parent methods rather than written again here; what a complex manifold
        adds is its complex dimension, the holomorphic maps between them
        (:class:`ComplexManifoldMor`) and the holomorphic open subsets.
        """

        def underlying_smooth_manifold(self):
            pass

        def open_submanifold(self, open_inclusion):
            pass

        def open_submanifold_inclusion(self, open_manifold):
            pass

        def complex_dimension(self):
            return self.dimension()

        def real_dimension(self):
            return 2 * int(self.dimension())

        def coordinate_field(self):
            r"""The field ``CC``: a holomorphic chart is a biholomorphism onto an open subset of ``CC^n``."""
            return _owned_complex_field()

        def is_analytic(self) -> bool:
            return True

        def regularity(self):
            return "analytic"

        def holomorphic_polynomial_map(self, codomain, coordinate_expressions):
            return self.Mor(codomain).polynomial(coordinate_expressions)

        def open_inclusion(self):
            r"""The selected ambient open inclusion, absent for a standalone construction."""
            return None

        def is_open_submanifold(self) -> bool:
            r"""Whether this construction retains an ambient open inclusion."""
            return self.open_inclusion() is not None

    class SubcategoryMethods:
        def BoundedSymmetric(self):
            r"""The axiom: biholomorphic to a bounded symmetric domain.

            A bounded domain ``D`` in ``C^N`` is symmetric when each
            ``p in D`` is an isolated fixed point of an involutive
            biholomorphism of ``D`` (Helgason, Ch. VIII, §7).  The property
            is invariant under biholomorphism, so it is a property of a
            complex manifold, stated by an axiom on ``ComplexManifolds()``.
            Its objects are the Hermitian symmetric spaces of the
            noncompact type with their complex structure (Helgason,
            Ch. VIII, §7, the Harish-Chandra realization).
            """
            return self._with_axiom("BoundedSymmetric")

    class BoundedSymmetric(CategoryWithAxiom):
        r"""Complex manifolds biholomorphic to a bounded symmetric domain (Helgason, Ch. VIII, §7).

        Each object is a product of irreducible ones, and an irreducible
        object is ``G/K`` for ``G`` the identity component of its
        biholomorphism group, a noncompact simple Lie group whose real form
        has a Satake diagram of Hermitian type (Helgason, Ch. X, §6,
        Table V).  The irreducible ones are the four classical families
        ``I_{p,q}``, ``II_n``, ``III_n``, ``IV_n`` and the two exceptional
        domains ``EIII`` and ``EVII``.  The Bergman metric is invariant
        under every biholomorphism and makes the domain a Riemannian
        globally symmetric space of noncompact type.
        """

        def extra_super_categories(self):
            r"""``RiemannianManifolds().GloballySymmetric()``: the domain with its Bergman metric.

            The Bergman metric is determined by the complex structure, so it
            is no choice; with it ``G/K`` is a Riemannian globally symmetric
            space of noncompact type (Helgason, Ch. VIII, §7).
            """
            return [RiemannianManifolds().GloballySymmetric()]

        @cached_method
        def type_I(self, p, q):
            r"""Return ``I_{p,q} = SU(p, q)/S(U(p) x U(q))``, Cartan type AIII.

            Bounded realization ``{Z in M_{p x q}(C) : 1_q - Z^* Z > 0}``,
            of complex dimension ``pq``, for positive integers ``p`` and
            ``q``.  ``I_{1,1}`` is the disc, biholomorphic to
            ``upper_half_plane()``.  The positivity of the Hermitian matrix
            ``1_q - Z^* Z`` is read by Sylvester's criterion: every leading
            principal minor is positive.
            """
            assert p >= 1 and q >= 1, (
                f"I_{{p,q}} is defined for positive integers p and q, not p = {p}, q = {q}"
            )
            index_pairs = tuple(
                (row, column) for row in range(int(p)) for column in range(int(q))
            )
            space, coordinates = self._matrix_coordinate_space(f"I_{p}_{q}", index_pairs)
            matrix = _engine_matrix(
                SR, int(p), int(q), lambda row, column: coordinates[(row, column)]
            )
            return self._bounded_open_domain(
                space,
                f"I_{p}_{q}",
                _engine_positive_definite(
                    _engine_identity_matrix(SR, int(q)) - matrix.conjugate_transpose() * matrix
                ),
            )

        @cached_method
        def type_II(self, n):
            r"""Return ``II_n = SO^*(2n)/U(n)``, Cartan type DIII.

            Bounded realization ``{Z in M_n(C) : Z^t = -Z, 1_n - Z^* Z > 0}``,
            of complex dimension ``n(n - 1)/2``, for an integer ``n >= 2``;
            the coordinates are the entries ``z_{ij}``, ``i < j``.
            """
            assert n >= 2, f"II_n is defined for integers n >= 2, not n = {n}"
            index_pairs = tuple(
                (row, column) for row in range(int(n)) for column in range(row + 1, int(n))
            )
            space, coordinates = self._matrix_coordinate_space(f"II_{n}", index_pairs)
            matrix = _engine_matrix(
                SR, int(n), int(n), lambda row, column: _skew_entry(coordinates, row, column)
            )
            return self._bounded_open_domain(
                space,
                f"II_{n}",
                _engine_positive_definite(
                    _engine_identity_matrix(SR, int(n)) - matrix.conjugate_transpose() * matrix
                ),
            )

        @cached_method
        def type_III(self, n):
            r"""Return ``III_n = Sp_{2n}(RR)/U(n)``, Cartan type CI.

            Bounded realization ``{Z in M_n(C) : Z^t = Z, 1_n - Z^* Z > 0}``,
            of complex dimension ``n(n + 1)/2``, for a positive integer
            ``n``; the coordinates are the entries ``z_{ij}``, ``i <= j``.
            The Cayley transform identifies it with
            ``siegel_upper_half_space(n)``; ``III_1 = I_{1,1}``.
            """
            assert n >= 1, f"III_n is defined for positive integers n, not n = {n}"
            space, coordinates = self._matrix_coordinate_space(
                f"III_{n}", _upper_triangle(n)
            )
            matrix = _engine_matrix(
                SR, int(n), int(n), lambda row, column: _symmetric_entry(coordinates, row, column)
            )
            return self._bounded_open_domain(
                space,
                f"III_{n}",
                _engine_positive_definite(
                    _engine_identity_matrix(SR, int(n)) - matrix.conjugate_transpose() * matrix
                ),
            )

        @cached_method
        def type_IV(self, n):
            r"""Return ``IV_n = SO_0(2, n)/(SO(2) x SO(n))``, Cartan type BDI with ``q = 2``.

            For a real quadratic space ``V`` of signature ``(2, n)`` it is
            one connected component of
            ``{[omega] in P(V_C) : (omega, omega) = 0, (omega, bar omega) > 0}``,
            the space of oriented positive definite real ``2``-planes in
            ``V``, of complex dimension ``n``, for a positive integer ``n``
            (lean-categories FOUNDATIONS, Definition 61.3, which states the
            two components and that choosing one is additional data;
            ``LeanCategories/Lattices/Valued/PeriodDomainData.lean``,
            ``latticePeriodDomainData``).

            The construction is the tube domain
            ``{z in C^n : Im z in C^+}``, ``C^+ = {y : y_1 > 0, (y, y) > 0}``
            for ``(y, y) = y_1^2 - y_2^2 - ... - y_n^2``.  Write
            ``V = U + W`` with ``U`` a hyperbolic plane on ``e, f`` and ``W``
            of signature ``(1, n - 1)``.  A line with ``(omega, e) != 0`` has
            the unique representative ``omega = -(z, z)/2 e + f + z``,
            ``z in W_C``, which is isotropic, and
            ``(omega, bar omega) = 2 (Im z, Im z)``.  No line of the period
            domain has ``(omega, e) = 0``: then ``Re omega`` and
            ``Im omega`` would span a positive definite real ``2``-plane in
            ``e^perp/e = W``, which has one positive direction.  The two
            components of ``{(y, y) > 0}`` are the two components of the
            period domain, and ``y_1 > 0`` chooses one.
            """
            assert n >= 1, f"IV_n is defined for positive integers n, not n = {n}"
            space, coordinates = self._matrix_coordinate_space(
                f"IV_{n}", tuple((0, index) for index in range(int(n)))
            )
            imaginary = tuple(
                coordinates[(0, index)].imag_part() for index in range(int(n))
            )
            return self._bounded_open_domain(
                space,
                f"IV_{n}",
                (
                    imaginary[0] > 0,
                    imaginary[0] ** 2 - sum(y**2 for y in imaginary[1:]) > 0,
                ),
            )

        def type_EIII(self):
            r"""Return ``E_{6(-14)}/(Spin(10) x U(1))``, of complex dimension ``16``.

            Built on the Satake diagram of ``E_{6(-14)}`` (Araki, 1962): in
            Bourbaki's labels the black nodes are ``3, 4, 5`` and ``tau``
            swaps ``1 <-> 6`` and ``3 <-> 5``; real rank ``2``.  The vertices
            of the session's ``E6`` diagram are Bourbaki's labels minus one.
            The bounded realization is ``harish_chandra_realization()``.
            """
            return self._exceptional_domain("EIII", "E6", (2, 3, 4), (5, 1, 4, 3, 2, 0))

        def type_EVII(self):
            r"""Return ``E_{7(-25)}/(E_6 x U(1))``, of complex dimension ``27``.

            Built on the Satake diagram of ``E_{7(-25)}`` (Araki, 1962): in
            Bourbaki's labels the black nodes are ``2, 3, 4, 5`` and ``tau``
            is the identity; real rank ``3``.  The vertices of the session's
            ``E7`` diagram are Bourbaki's labels minus one.
            """
            return self._exceptional_domain("EVII", "E7", (1, 2, 3, 4), (0, 1, 2, 3, 4, 5, 6))

        def _exceptional_domain(self, name, cartan_name, black_nodes, involution_images):
            r"""The Hermitian symmetric domain ``G/K`` of the real form with the given Satake diagram.

            Its complex dimension is ``dim p_0 / 2``; the complex manifold has
            no chart until its Harish-Chandra realization is constructed.
            """
            from sage_extensions.categories.lattices import Lattices
            from sage_extensions.categories.satake_diagrams import SatakeDiagrams

            diagram = Lattices(_owned_integers())(cartan_name).dynkin_diagram()
            satake = SatakeDiagrams()(
                diagram, black_nodes, diagram.Mor(diagram)(involution_images)
            )
            rank, dimension = _symmetric_space_rank_and_dimension(satake)
            engine = _SageManifold(
                dimension // 2,
                name,
                field="complex",
                structure="smooth",
                unique_tag=object(),
            )
            return _object_of(
                self,
                _engine=(SmoothManifolds(), _RealFormSymmetricSpace, None),
                topology_data=_ManifoldTopologyData(engine),
                engine_manifold=engine,
                manifold_dimension=dimension // 2,
                manifold_name=name,
                manifold_structure="complex analytic",
                differentiability_degree=Infinity,
                manifold_field="complex",
                satake_diagram=satake,
                real_rank=rank,
            )

        @cached_method
        def upper_half_plane(self, name="HH"):
            r"""Return the upper half-plane ``{tau in C : Im(tau) > 0}``.

            It is ``SL_2(RR)/SO(2)``, the domain ``I_{1,1} = III_1``, by the
            Cayley transform ``tau -> (tau - i)/(tau + i)`` onto the disc.
            The construction is the open subset of a fresh complex line
            cut out by ``Im(tau) > 0`` in its chart.
            """
            complex_manifolds = self.base_category()
            line = complex_manifolds.affine_space(
                1, name=f"{name}_line", coordinate_names=("tau",)
            )
            tau = _engine_manifold_expression(
                line.atlas()[tuple(line.chart_labels())[0]].coordinate(0)
            )
            return _object_of(
                self,
                _engine=(complex_manifolds, _SiegelUpperHalfSpace, None),
                siegel_genus=1,
                **complex_manifolds._open_submanifold_data(
                    line, name, tau.imag_part() > 0
                ),
            )

        @cached_method
        def siegel_upper_half_space(self, g):
            r"""Return ``H_g = {Z in M_g(C) : Z^t = Z, Im(Z) > 0}``, the Siegel upper half-space.

            It is ``Sp_{2g}(RR)/U(g)``, the domain ``III_g``, of complex
            dimension ``g(g + 1)/2``, for a positive integer ``g``;
            ``H_1 = upper_half_plane()``.  The coordinates are the entries
            ``z_{ij}``, ``i <= j``, of ``Z``, and the positive definiteness
            of the real symmetric matrix ``Im(Z)`` is read by Sylvester's
            criterion: every leading principal minor is positive.
            """
            assert g >= 1, f"H_g is defined for positive integers g, not g = {g}"
            space, coordinates = self._matrix_coordinate_space(
                f"H_{g}", _upper_triangle(g)
            )
            imaginary = _engine_matrix(
                SR,
                int(g),
                int(g),
                lambda row, column: _symmetric_entry(coordinates, row, column).imag_part(),
            )
            complex_manifolds = self.base_category()
            return _object_of(
                self,
                _engine=(complex_manifolds, _SiegelUpperHalfSpace, None),
                siegel_genus=int(g),
                **complex_manifolds._open_submanifold_data(
                    space, f"H_{g}", _engine_positive_definite(imaginary)
                ),
            )

        def _matrix_coordinate_space(self, name, index_pairs):
            r"""The complex affine space with one coordinate ``z_i_j`` per index pair, and its engine coordinates."""
            space = self.base_category().affine_space(
                len(index_pairs),
                name=f"{name}_space",
                coordinate_names=tuple(f"z_{row}_{column}" for row, column in index_pairs),
            )
            chart = space.atlas()[tuple(space.chart_labels())[0]]
            return space, {
                pair: _engine_manifold_expression(chart.coordinate(index))
                for index, pair in enumerate(index_pairs)
            }

        def _bounded_open_domain(self, space, name, restriction):
            r"""The open subset of ``space`` cut out by ``restriction``, an object of this category."""
            complex_manifolds = self.base_category()
            return _object_of(
                self,
                _engine=(complex_manifolds, _ComplexOpenEngine, None),
                **complex_manifolds._open_submanifold_data(space, name, restriction),
            )

        class ParentMethods:
            def harish_chandra_realization(self):
                r"""Return the biholomorphism onto a bounded symmetric domain in ``C^N``.

                Domain ``D``; codomain the open subset of
                ``ComplexManifolds().affine_space(N)`` that it realizes,
                ``N`` the complex dimension of ``D`` (Helgason, Ch. VIII,
                §7).
                """
                assert False, "harish_chandra_realization on ComplexManifolds.BoundedSymmetric: not implemented"

            def bergman_metric_space(self):
                r"""Return ``(D, g_B)``, ``D`` with its Bergman metric.

                The result is an object of
                ``RiemannianManifolds().GloballySymmetric()`` of noncompact
                type; for irreducible ``D`` it is
                ``noncompact_type(satake_diagram)`` for the Satake diagram of
                the real form ``Lie(Aut(D)^0)``.
                """
                assert False, "bergman_metric_space on ComplexManifolds.BoundedSymmetric: not implemented"


class _RealFormSymmetricSpace:
    r"""The symmetric space ``G/K`` of a real form, built on its Satake diagram; a realization, not a category.

    The Satake diagram classifies the real form ``g_0 = Lie(G)`` (Araki,
    1962), so it is the datum the construction is on; the real rank
    ``dim a_0`` is read from it.
    """

    def __init__(self, satake_diagram, real_rank, **rest) -> None:
        self._satake_diagram = satake_diagram
        self._real_rank = real_rank
        super().__init__(**rest)

    def satake_diagram(self):
        r"""Return the Satake diagram of the real form ``g_0`` of which this is ``G/K``."""
        return self._satake_diagram

    def real_rank(self):
        r"""Return ``dim a_0``, the rank of the symmetric space: the number of ``tau``-orbits of white nodes."""
        return self._real_rank

    def _repr_(self):
        diagram = self._satake_diagram
        return (
            f"{self.dimension()}-dimensional {self.manifold_structure()} symmetric space "
            f"{self.manifold_name()} of real rank {self._real_rank}, of the real form of "
            f"{diagram.dynkin_diagram().label()} with black nodes "
            f"{tuple(diagram.black_nodes())} and involution "
            f"{tuple(diagram.involution()(vertex) for vertex in diagram.dynkin_diagram().index_set())}"
        )


class _ComplexOpenEngine:
    r"""Native chart-restriction realization at ComplexManifolds, not a category.

    The retained ambient manifold and restriction determine the inclusion;
    the cooperative constructor registers the restricted native chart.
    """

    def __init__(self, containing_manifold, open_restriction, chart_label, **rest) -> None:
        self._containing_manifold = containing_manifold
        self._open_restriction = open_restriction
        super().__init__(**rest)
        self._register_chart(
            chart_label,
            _engine_manifold_chart(containing_manifold.atlas()[chart_label]).restrict(
                self._engine_manifold_realization()
            ),
        )

    def _engine_open_restriction(self):
        return self._open_restriction

    @cached_method
    def open_inclusion(self):
        r"""Return the holomorphic inclusion of this open subset into the manifold it is open in."""
        label = tuple(self.chart_labels())[0]
        coordinates = self.atlas()[label].coordinates()
        return self.Mor(self._containing_manifold).polynomial(coordinates)


class _SiegelUpperHalfSpace(_ComplexOpenEngine):
    r"""The Siegel upper half-space ``H_g`` with its symplectic action; a realization, not a category.

    ``Sp_{2g}(RR)`` acts on ``H_g`` by biholomorphisms
    ``M . Z = (AZ + B)(CZ + D)^{-1}`` for ``M = [[A, B], [C, D]]`` with
    ``g x g`` blocks; it is transitive with stabilizer ``U(g)`` at ``iI``,
    which presents ``H_g`` as ``Sp_{2g}(RR)/U(g)``, the domain ``III_g``
    (Helgason, Ch. X, §6, Table V).  For ``g = 1`` this is the Möbius
    action of ``SL_2(RR) = Sp_2(RR)`` on the upper half-plane.
    """

    def __init__(self, siegel_genus, **rest) -> None:
        self._siegel_genus = siegel_genus
        super().__init__(**rest)

    def siegel_genus(self):
        return self._siegel_genus

    def symplectic_action(self, group):
        r"""Return the ``Gamma``-space ``(H_g, rho)`` of a group of integral symplectic matrices.

        ``group`` is a group ``Gamma`` of ``2g x 2g`` matrices in
        ``Sp_{2g}(ZZ)``; ``SL_2(ZZ) = Sp_2(ZZ)`` for ``g = 1``.  ``rho``
        restricts the action of ``Sp_{2g}(RR)`` along the inclusion, so
        ``rho(M)`` is the biholomorphism ``Z |-> (AZ + B)(CZ + D)^{-1}``
        of ``H_g``, and ``(MN) . Z = M . (N . Z)`` makes it a left action.
        ``Sp_{2g}(ZZ)`` is discrete in ``Sp_{2g}(RR)`` and the stabilizer
        ``U(g)`` is compact, so ``Gamma`` acts properly discontinuously.  The
        result is an object of
        ``GObjects(Gamma, ComplexManifolds()).ProperlyDiscontinuous()``; its
        ``orbit_space()`` is the complex orbifold ``Gamma\H_g``.
        """
        from sage_extensions.categories.group.g_objects import GObjects

        return GObjects(group, ComplexManifolds()).ProperlyDiscontinuous().on_space(
            self,
            lambda element, point: self._symplectic_transform(group, element, point),
        )

    def _symplectic_transform(self, group, element, point):
        r"""The point ``M . Z = (AZ + B)(CZ + D)^{-1}`` for ``M`` the matrix of ``element``."""
        from sage_extensions.categories.group.groups import (
            _matrix_group_element_matrix,
        )

        g = self._siegel_genus
        point = self(point)
        matrix = _matrix_group_element_matrix(group, element)
        assert matrix.nrows() == 2 * g and matrix.ncols() == 2 * g, (
            f"{element} does not act on {self}: Sp_{2 * g} acts on the Siegel upper "
            f"half-space H_{g} by 2g x 2g = {2 * g} x {2 * g} matrices, and its matrix is "
            f"{matrix.nrows()} x {matrix.ncols()}"
        )
        field = _owned_complex_field()
        engine_field = _engine_ring(field)
        entries = dict(zip(_upper_triangle(g), tuple(point.coordinates()), strict=True))
        Z = _engine_matrix(
            engine_field,
            g,
            g,
            lambda row, column: _engine_element(field, _symmetric_entry(entries, row, column)),
        )
        M = matrix.change_ring(engine_field)
        A, B, C, D = M[:g, :g], M[:g, g:], M[g:, :g], M[g:, g:]
        W = (A * Z + B) * (C * Z + D).inverse()
        return self.point(
            tuple(_owned_engine_element(field, W[row, column]) for row, column in _upper_triangle(g)),
            point.chart().label(),
        )


class _ComplexDiscEngine(_ComplexOpenEngine):
    r"""The disc parameters refine the chart-restriction engine, not the category."""

    def __init__(self, disc_radius, punctured, **rest) -> None:
        self._disc_radius = disc_radius
        self._punctured = punctured
        super().__init__(**rest)

    def disc_radius(self):
        return self._disc_radius

    def is_punctured(self) -> bool:
        return self._punctured

    def _element_constructor_(self, datum, chart_label="standard"):
        r"""Return the point ``z`` of the disc for a complex number ``z``, or the point with coordinates ``datum``.

        A point of the disc ``{|z| < r}`` is a complex number ``z`` with
        ``|z| < r``, and ``z != 0`` when the disc is punctured: its one
        coordinate in the chart cut out of the line.  The chart restriction
        decides membership.
        """
        match datum:
            case _ if element_parent(datum) is self:
                return datum
            case _ if datum in _owned_complex_field():
                return super()._element_constructor_((datum,), chart_label)
            case _:
                return super()._element_constructor_(datum, chart_label)


__all__ = [
    "ComplexManifoldMor",
    "ComplexManifolds",
    "DifferentiableManifolds",
    "HolomorphicMap",
    "ManifoldAtlasChart",
    "ManifoldAtlasTransition",
    "RiemannianManifoldMor",
    "RiemannianManifolds",
    "SmoothManifolds",
    "TopologicalManifolds",
]
