r"""Private exact finite-order smooth germs, without analyticity.

The kth Taylor polynomial represents the germ modulo terms of degree k+1.
Multiplication and composition compute jets by the product and chain rules.
The consumer selects the order; all orders of a represented smooth function
remain available. Coefficients are owned exact reals.
"""

from itertools import product
from math import factorial, prod

from sage.symbolic.ring import SR


def _indices(n, order):
    return (alpha for alpha in product(range(order + 1), repeat=n)
            if sum(alpha) <= order)


class _TaylorJet:
    """Taylor polynomial modulo total degree greater than its order."""

    def __init__(self, field, n, order, coefficients):
        self.field, self.n, self.order = field, n, order
        self.coefficients = coefficients

    @classmethod
    def constant(cls, field, n, order, value):
        return cls(field, n, order, {(0,) * n: field(value)})

    @classmethod
    def derivatives(cls, field, n, order, derivative):
        return cls(field, n, order, {
            alpha: field(derivative(alpha)) / field(prod(factorial(a) for a in alpha))
            for alpha in _indices(n, order)
        })

    def coefficient(self, alpha):
        return self.coefficients.get(tuple(alpha), self.field.zero())

    def value(self):
        return self.coefficient((0,) * self.n)

    def truncate(self, order):
        assert order <= self.order
        return _TaylorJet(self.field, self.n, order,
                          {a: c for a, c in self.coefficients.items() if sum(a) <= order})

    def __add__(self, other):
        assert (self.n, self.order) == (other.n, other.order)
        return _TaylorJet(self.field, self.n, self.order, {
            a: self.coefficient(a) + other.coefficient(a)
            for a in self.coefficients.keys() | other.coefficients.keys()
        })

    def scale(self, scalar):
        return _TaylorJet(self.field, self.n, self.order,
                          {a: scalar * c for a, c in self.coefficients.items()})

    def __neg__(self):
        return self.scale(-self.field.one())

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        assert (self.n, self.order) == (other.n, other.order)
        coefficients = {}
        zero = self.field.zero()
        for a, x in self.coefficients.items():
            for b, y in other.coefficients.items():
                c = tuple(i + j for i, j in zip(a, b, strict=True))
                if sum(c) <= self.order:
                    coefficients[c] = coefficients.get(c, zero) + x * y
        return _TaylorJet(self.field, self.n, self.order, coefficients)

    def reciprocal(self):

        inverse = self.field.one() / self.value()
        one = self.constant(self.field, self.n, self.order, self.field.one())
        q = _TaylorJet(self.field, self.n, self.order,
                       {a: -inverse*c for a,c in self.coefficients.items() if any(a)})
        term = result = one
        for _ in range(self.order):
            term = term * q
            result = result + term
        return result.scale(inverse)

    def partial(self, i):
        assert self.order > 0
        result = {}
        for a in _indices(self.n, self.order - 1):
            b = tuple(v + (j == i) for j, v in enumerate(a))
            result[a] = self.field(b[i]) * self.coefficient(b)
        return _TaylorJet(self.field, self.n, self.order - 1, result)

    def compose(self, arguments):
        """Pull back the germ by coordinate germs at their base point."""
        assert len(arguments) == self.n
        if not arguments:
            return self
        n, order = arguments[0].n, arguments[0].order
        assert self.order >= order
        one = self.constant(self.field, n, order, self.field.one())
        result = self.constant(self.field, n, order, self.field.zero())
        powers = []
        for argument in arguments:
            centered = _TaylorJet(self.field, n, order,
                                  {a: c for a,c in argument.coefficients.items() if any(a)})
            sequence = [one]
            for _ in range(order):
                sequence.append(sequence[-1] * centered)
            powers.append(sequence)
        for a, coefficient in self.coefficients.items():
            if sum(a) > order:
                continue
            term = one.scale(coefficient)
            for i, exponent in enumerate(a):
                term = term * powers[i][exponent]
            result = result + term
        return result


def _symbolic_jet(field, formula, symbols, values, order):
    substitution = dict(zip(symbols, values, strict=True))
    def derivative(alpha):
        expression = SR(formula)
        for x, count in zip(symbols, alpha, strict=True):
            for _ in range(count):
                expression = expression.diff(x)
        from sage_extensions.rings.real import RR
        if field is RR:
            return field._evaluate_formula(expression, symbols, values)
        return field(expression.subs(substitution))
    return _TaylorJet.derivatives(field, len(symbols), order, derivative)


def _has_cauchy_coordinate(values):
    from sage_extensions.rings.real import ExactRealNumber

    return any(isinstance(value, ExactRealNumber) and value._symbolic_expression() is None
               for value in values)


def _point_coordinate_values(point):
    r"""Use the actual owned coordinates when symbolic serialization is unavailable."""
    from sage_extensions.categories.manifolds import _engine_manifold_expression

    coordinates = tuple(point.coordinates())
    if _has_cauchy_coordinate(coordinates):
        return coordinates
    return tuple(_engine_manifold_expression(value) for value in coordinates)


def _valid_exact_coordinates(chart, coordinates):
    r"""Decide represented chart membership in the owned exact real field.

    This is the real chart's bounds and the engine's stated Boolean
    combinations of restrictions, evaluated over RR. Undefined or undecided
    relations do not certify membership. A proved false conjunct excludes the
    point even when another conjunct has no value there.
    """
    from operator import eq, ne, lt, le, gt, ge
    from sage.rings.infinity import Infinity
    from sage_extensions.rings.real import RR
    from sage_extensions.logic import ask

    if len(coordinates) != len(tuple(chart[:])):
        return False
    coordinates = tuple(RR(c) for c in coordinates)
    symbols = tuple(chart[:])

    def conjunction(answers):
        answers = tuple(answers)
        return False if False in answers else True if all(a is True for a in answers) else None

    def disjunction(answers):
        answers = tuple(answers)
        return True if True in answers else False if all(a is False for a in answers) else None

    def relation(condition):
        if isinstance(condition, tuple):
            return disjunction(relation(c) for c in condition)
        if isinstance(condition, (list, set, frozenset)):
            return conjunction(relation(c) for c in condition)
        if condition is True or condition is False:
            return condition
        if not hasattr(condition, "operator") or condition.operator() not in (eq, ne, lt, le, gt, ge):
            return None
        try:
            value = RR._evaluate_formula(condition.lhs()-condition.rhs(), symbols, coordinates)
        except (ZeroDivisionError, NotImplementedError):
            return None
        answer = ask(condition.operator()(value, RR.zero()))
        return answer if answer is True or answer is False else None

    bounds = []
    if hasattr(chart, "coord_bounds"):
        for value, (low, high) in zip(coordinates, chart.coord_bounds(), strict=True):
            if low[1] == "periodic":
                continue
            if low[0] != -Infinity:
                bounds.append(ask(value >= RR(low[0])) if low[1] else ask(value > RR(low[0])))
            if high[0] != Infinity:
                bounds.append(ask(value <= RR(high[0])) if high[1] else ask(value < RR(high[0])))
    if chart._restrictions:
        bounds.append(relation(chart._restrictions))
    for condition in getattr(chart, "_owned_open_conditions", ()):
        bounds.append(condition(coordinates))
    return conjunction(bounds)


def _coordinate_germ(source, values, target):
    """Read an actual germ of a native chart change at a point.

    Native transitions have restricted source and target charts on their
    overlaps. Traverse a leg only if its source and image coordinates
    satisfy their respective restrictions. Restriction/superchart edges
    preserve coordinates. No transition is extrapolated.
    """
    if source.domain().manifold() is not target.domain().manifold():
        return None
    symbols = tuple(source[:])
    exact = _has_cauchy_coordinate(values)
    if exact:
        from sage_extensions.rings.real import RR

        def valid(chart, coordinates):
            return _valid_exact_coordinates(chart, coordinates) is True

        def evaluate(chart, change, coordinates):
            return tuple(RR._evaluate_formula(expression, tuple(chart[:]), coordinates)
                         for expression in change._transf.expr())
    else:
        def valid(chart, coordinates):
            return chart.valid_coordinates(*coordinates) and all(
                condition(coordinates) is True
                for condition in getattr(chart, "_owned_open_conditions", ()))

        def evaluate(chart, change, coordinates):
            return tuple(change(*coordinates))
    changes = source.domain().manifold().coord_changes()
    pending = [(source, symbols, tuple(values))]
    visited = set()
    while pending:
        chart, formulas, current = pending.pop()
        if chart in visited or not valid(chart, current):
            continue
        visited.add(chart)
        if chart is target:
            return formulas, current
        for neighbor in chart._subcharts | chart._supercharts:
            if neighbor not in visited and valid(neighbor, current):
                pending.append((neighbor, formulas, current))
        substitution = dict(zip(tuple(chart[:]), formulas, strict=True))
        for (left, right), change in changes.items():
            if left is not chart or right in visited:
                continue
            image = evaluate(chart, change, current)
            if not valid(right, image):
                continue
            expressions = tuple(SR(f).subs(substitution) for f in change._transf.expr())
            pending.append((right, expressions, image))
    return None


def _coordinate_change_jets(source, values, target, field, order):
    """The finite jet of an actual atlas change at a point.

    A symbolic change is one representation of a smooth transition. For
    transitions given by all-order smooth coordinate functions, compose
    their jets along an actual chain of overlaps instead. Restriction
    edges have identity jets, and no edge is read outside its domain.
    """
    if source.domain().manifold() is not target.domain().manifold():
        return None
    values = tuple(field(c) for c in values)
    dimension = len(values)
    if source is target:
        if _valid_exact_coordinates(source, values) is not True:
            return None
        return tuple(_TaylorJet.derivatives(field, dimension, order,
            lambda alpha, i=i: values[i] if sum(alpha) == 0 else
            field.one() if sum(alpha) == 1 and alpha[i] == 1 else field.zero())
            for i in range(dimension))
    if not getattr(source.domain().manifold(), "_owned_coordinate_data", False):
        lowered = tuple(c if _has_cauchy_coordinate((c,)) else c.expression() for c in values)
        change = _coordinate_germ(source, lowered, target)
        if change is None:
            return None
        return tuple(_symbolic_jet(field, expression, tuple(source[:]), values, order)
                     for expression in change[0])
    initial = tuple(_TaylorJet.derivatives(field, dimension, order,
        lambda alpha, i=i: values[i] if sum(alpha) == 0 else
        field.one() if sum(alpha) == 1 and alpha[i] == 1 else field.zero())
        for i in range(dimension))
    native_changes = source.domain().manifold().coord_changes()
    pending, visited = [(source, initial)], set()
    while pending:
        chart, accumulated = pending.pop()
        current = tuple(jet.value() for jet in accumulated)
        if chart in visited or _valid_exact_coordinates(chart, current) is not True:
            continue
        visited.add(chart)
        if chart is target:
            return accumulated
        for neighbor in chart._subcharts | chart._supercharts:
            if neighbor not in visited:
                pending.append((neighbor, accumulated))
        for (left, right), transition in native_changes.items():
            if left is chart and right not in visited:
                edge = tuple(_symbolic_jet(field, expression, tuple(chart[:]), current, order)
                             for expression in transition._transf.expr())
                pending.append((right, tuple(jet.compose(accumulated) for jet in edge)))
        for right, provider in getattr(chart, "_owned_coordinate_transitions", {}).items():
            if right not in visited:
                edge = provider(current, order)
                pending.append((right, tuple(jet.compose(accumulated) for jet in edge)))
    return None


def _coordinates_in_chart(chart, point):
    from sage_extensions.categories.manifolds import (
        _engine_manifold_chart, _engine_manifold_expression, CoverageUndecided,
    )
    start = _engine_manifold_chart(point.chart())
    target = _engine_manifold_chart(chart)
    values = _point_coordinate_values(point)
    if start is target:
        return tuple(point.coordinates())
    field = chart.manifold().coordinate_field()
    change = _coordinate_change_jets(start, values, target, field, 0)
    if change is None:
        raise CoverageUndecided(f"no represented coordinate germ places {point} in {chart.label()}")
    return tuple(jet.value() for jet in change)


def _coordinate_jets(chart, point, order):
    """Jets of the actual chart coordinates, with identity first derivative."""
    from sage_extensions.categories.manifolds import _engine_manifold_chart

    field = chart.manifold().coordinate_field()
    if _engine_manifold_chart(point.chart()) is _engine_manifold_chart(chart):
        values = tuple(point.coordinates())
    else:
        values = tuple(field(c) for c in _coordinates_in_chart(chart, point))
    dimension = len(values)
    return tuple(_TaylorJet.derivatives(field, dimension, order,
        lambda alpha, i=i: values[i] if sum(alpha) == 0 else
        field.one() if sum(alpha) == 1 and alpha[i] == 1 else field.zero())
        for i in range(dimension))


def _pullback_jet(jet, chart, point, target_engine, order):
    from sage_extensions.categories.manifolds import _engine_manifold_chart, CoverageUndecided
    source = _engine_manifold_chart(chart)
    values = _coordinates_in_chart(chart, point)
    args = _coordinate_change_jets(source, values, target_engine, jet.field, order)
    if args is None:
        raise CoverageUndecided("no actual overlap represents the requested smooth germ")
    return jet.compose(args)


class _SmoothGermFunction:
    """A smooth map with a provider of its jets of every finite order.

    The provider is defining smooth-function data: on each chart its
    coefficients are actual derivatives of the same smooth map in the
    indicated coordinates. It is not a sampled approximation.
    """

    def __init__(self, manifold, provider, *, charts=None):
        self.manifold, self.provider = manifold, provider
        self.charts = charts

    def __call__(self, point):
        return self.jet(point.chart(), point, 0).value()

    def jet(self, chart, point, order):
        from sage_extensions.categories.manifolds import _engine_manifold_chart, CoverageUndecided
        source = _engine_manifold_chart(chart)
        if self.charts is None:




            if chart.manifold() is self.manifold:
                values = _coordinates_in_chart(chart, point)
                local_point = self.manifold.point(
                    tuple(self.manifold.coordinate_field()(c) for c in values), chart.label())
                return self.provider(chart, local_point, order)
            atlas = self.manifold.atlas()
            labels = self.manifold.chart_labels()
            preferred = (chart.label(), point.chart().label())
            selected = tuple(dict.fromkeys(
                (*preferred, *self.manifold.selected_finite_chart_labels())))
            locals = tuple(atlas[label] for label in selected if label in labels)
        else:
            locals = self.charts
        if _engine_manifold_chart(point.chart()) is source:
            for local in locals:
                if _engine_manifold_chart(local) is source:
                    local_point = self.manifold.point(point.coordinates(), local.label())
                    return self.provider(local, local_point, order)
        values = _coordinates_in_chart(chart, point)
        for local in sorted(locals, key=lambda item: _engine_manifold_chart(item) is not source):
            engine = _engine_manifold_chart(local)
            field = self.manifold.coordinate_field()
            change = _coordinate_change_jets(source, values, engine, field, order)
            if change is None:
                continue
            coordinates = tuple(jet.value() for jet in change)
            local_point = self.manifold.point(coordinates, local.label())
            germ = self.provider(local, local_point, order)
            if engine is source:
                return germ
            return germ.compose(change)
        raise CoverageUndecided("no local presentation of the smooth map contains the point")


def _function_jet(function, chart, point, order):
    """Read an exact local jet of an owned scalar function."""
    from sage_extensions.categories.manifolds import (
        _ChartExpression, _ChartwiseFunction, _RestrictedManifoldFunction,
        _SectionRatio, _manifold_function_definition, _engine_manifold_chart,
        CoverageUndecided,
    )
    from sage_extensions.categories.functions.real_functions import (
        _ConstantMap, _pointwise_product, _function_formula,
    )
    from sage_extensions.categories.modules.general_modules import _PointwiseValues
    from sage_extensions.categories.modules.pure.modules import (
        _pointwise_negative, _pointwise_scalar_multiple, _pointwise_sum, _pointwise_zero,
    )
    from functools import partial

    field = chart.manifold().coordinate_field()
    source = _engine_manifold_chart(chart)
    symbols = tuple(source[:])
    n = len(symbols)

    def from_formula(formula, target):
        if target is source and _engine_manifold_chart(point.chart()) is source:
            expression = SR(formula)
            if not expression.variables():
                return _TaylorJet.constant(field, n, order, field(expression))
            for i, symbol in enumerate(symbols):
                if expression == symbol:
                    return _coordinate_jets(chart, point, order)[i]
            return _symbolic_jet(field, expression, symbols, point.coordinates(), order)
        values = _coordinates_in_chart(chart, point)
        change = _coordinate_change_jets(source, values, target, field, order)
        if change is None:
            return None
        return _symbolic_jet(field, formula, tuple(target[:]),
                             tuple(jet.value() for jet in change), order).compose(change)

    def read(value):
        if isinstance(value, _SectionRatio):
            return read(value.numerator()) * read(value.denominator()).reciprocal()
        definition = _manifold_function_definition(value)
        if isinstance(definition, _SmoothGermFunction):
            return definition.jet(chart, point, order)
        if isinstance(definition, _RestrictedManifoldFunction):
            return read(definition.function)
        if isinstance(definition, _ChartExpression):
            result = from_formula(definition.engine_expression(), definition._engine_chart)
            if result is not None:
                return result
        if isinstance(definition, _ChartwiseFunction):
            for label, expression in definition.expressions().items():
                target = _engine_manifold_chart(definition.manifold().atlas()[label])
                if target is not source and _coordinate_change_jets(
                        source, _coordinates_in_chart(chart, point), target, field, 0) is None:
                    continue
                if label in definition.formulas():
                    result = from_formula(definition.formulas()[label], target)
                    if result is not None:
                        return result
                return read(expression)
        if isinstance(definition, _ConstantMap):
            return _TaylorJet.constant(field, n, order, definition.value())
        if isinstance(definition, _PointwiseValues):
            operation = definition.operation()
            if operation is _pointwise_zero:
                return _TaylorJet.constant(field, n, order, field.zero())
            operands = tuple(read(operand) for operand in definition.operands())
            if operation is _pointwise_sum:
                return operands[0] + operands[1]
            if operation is _pointwise_negative:
                return -operands[0]
            if operation is _pointwise_product:
                return operands[0] * operands[1]
            if isinstance(operation, partial) and operation.func is _pointwise_scalar_multiple:
                return operands[0].scale(field(operation.args[0]))
        from sage_extensions.rings.real import RR
        formula = _function_formula(definition)
        if formula is not None and not formula[0].variables():
            return _TaylorJet.constant(field, n, order, field(formula[0]))
        if chart.manifold() is RR:
            if formula is not None:
                body, variable = formula
                target = _engine_manifold_chart(RR.identity_chart())
                result = from_formula(body.subs({variable: tuple(target[:])[0]}), target)
                if result is not None:
                    return result
        if order == 0:
            return _TaylorJet.constant(field, n, order, value(point))
        raise CoverageUndecided("the smooth map has no represented germ of the requested derivative order")

    return read(function)


def _flat_derivative(argument, order):
    r"""Read the flat step's derivatives through its scalar formula owner."""
    from sage_extensions.categories.functions.real_functions import (
        flat_exponential, _flat_exponential_exact,
    )
    from sage_extensions.rings.real import RR

    argument = RR(argument)
    if argument._symbolic_expression() is not None:
        return RR(flat_exponential(0, order, 0, SR.one(), argument.expression()))
    return _flat_exponential_exact(0, order, 0, RR.one(), argument)


def _flat_jet(argument):
    field = argument.field
    value = argument.value()
    scalar = _TaylorJet.derivatives(field, 1, argument.order,
                                   lambda alpha: _flat_derivative(value, alpha[0]))
    return scalar.compose((argument,))


def _exact_bump_coordinate_jet(arguments, center, radius, index):
    r"""Pull back the smooth step of squared distance using finite jets."""
    from sage_extensions.logic import ask

    field = arguments[0].field
    n, order = arguments[0].n, arguments[0].order
    constant = lambda value: _TaylorJet.constant(field, n, order, field(value))
    squared = constant(0)
    for coordinate, origin in zip(arguments, center, strict=True):
        delta = coordinate - constant(origin)
        squared = squared + delta * delta
    radius = field(radius)
    outer_squared, inner_squared = radius**2, (radius/field(2))**2
    distance = squared.value()
    if ask(distance < inner_squared) is True:
        return arguments[index]
    if ask(distance > outer_squared) is True:
        return constant(0)
    scale = outer_squared - inner_squared
    t = (constant(outer_squared) - squared).scale(field.one()/scale)
    rising, falling = _flat_jet(t), _flat_jet(constant(1)-t)
    return arguments[index] * rising * (rising+falling).reciprocal()


def _local_radius(chart, values):
    """Certify a closed coordinate ball contained in an actual open chart.

    Use interval enclosures of continuous chart inequalities on an enclosing
    box. Shrinking the box is not sampling: each accepted box is contained
    in the chart by a strict interval inequality.
    """
    from itertools import count
    from operator import eq, ne, lt, le, gt, ge
    from sage.ext.fast_callable import fast_callable
    from sage.rings.infinity import Infinity
    from sage.rings.real_mpfi import RealIntervalField
    from sage.rings.rational_field import QQ
    from sage_extensions.categories.manifolds import (
        _engine_manifold_chart, _engine_manifold_expression, CoverageUndecided,
    )

    native = _engine_manifold_chart(chart)
    selected_radius = getattr(native, "_owned_local_radius", None)
    if selected_radius is not None:
        radius = QQ(_engine_manifold_expression(selected_radius(
            tuple(chart.manifold().coordinate_field()(c) for c in values))))
        assert radius > 0, "a chart's selected closed-ball radius is positive"
        return radius
    symbols = tuple(native[:])
    bounds = tuple(native.coord_bounds())
    restrictions = list(native._restrictions or ())


    if chart.cut_from() is not None:
        change = chart.manifold().transition(chart.label(), chart.cut_from())
        substitutions = dict(zip(
            tuple(_engine_manifold_chart(change.target())[:]),
            tuple(_engine_manifold_expression(c) for c in change.forward_expressions()),
            strict=True,
        ))
        restrictions.extend(
            SR(_engine_manifold_expression(c)).subs(substitutions) != 0
            for c in change.target_overlap()
        )
    if not restrictions and all(low[0] == -Infinity and high[0] == Infinity
                                for low, high in bounds):
        return QQ.one()
    if any(callable(item) and not hasattr(item, "operator") and not isinstance(item, (list, tuple))
           for item in restrictions):
        raise CoverageUndecided("an opaque chart restriction requires a certified local ball")

    def certified(relation, box, field):
        if isinstance(relation, tuple):
            return any(certified(item, box, field) for item in relation)
        if isinstance(relation, (list, set, frozenset)):
            return all(certified(item, box, field) for item in relation)
        if relation is True:
            return True
        if relation is False:
            return False
        op = relation.operator()
        if op not in (eq, ne, lt, le, gt, ge):
            raise CoverageUndecided("the chart restriction has no interval inequality representation")
        residual = SR(relation.lhs() - relation.rhs())
        if op is eq:
            return residual == 0
        enclosure = fast_callable(residual, vars=symbols, domain=field)(*box)
        if op is ne:
            return enclosure.lower() > 0 or enclosure.upper() < 0
        if op in (lt, le):
            return enclosure.upper() < 0
        return enclosure.lower() > 0

    for exponent in count():
        field = RealIntervalField(max(64, 4 * exponent + 64))
        radius = QQ(1) / (2 ** exponent)
        from sage_extensions.rings.real import RR
        from sage.rings.real_arb import RealBallField

        def enclosing_interval(value):
            enclosure = RR(value)._arb_(RealBallField(field.precision()))
            lower, upper = enclosure.endpoints()
            return field(lower.exact_rational(), upper.exact_rational())

        box = tuple(enclosing_interval(value) + field(-radius, radius) for value in values)
        if any((low[0] != -Infinity and not interval.lower() > field(low[0]).upper())
               or (high[0] != Infinity and not interval.upper() < field(high[0]).lower())
               for interval, (low, high) in zip(box, bounds, strict=True)):
            continue
        try:
            if all(certified(relation, box, field) for relation in restrictions):
                return radius
        except (TypeError, ValueError, NotImplementedError) as error:
            raise CoverageUndecided("the chart restriction requires a certified local ball") from error


def _bump_extended_coordinate(manifold, home, center, index):
    """A global smooth function agreeing with a coordinate near center.

    The closed ball lies in the chart image by _local_radius. Its inverse
    image is compact, hence closed in the Hausdorff manifold. The smooth
    step is identically zero beyond the ball, so extension by zero is
    smooth, with every derivative zero off the support.
    """
    from sage_extensions.categories.functions.real_functions import smooth_step
    from sage_extensions.categories.manifolds import (
        _engine_manifold_chart, _engine_manifold_expression, CoverageUndecided,
    )
    from sage_extensions.logic import ask

    field = manifold.coordinate_field()
    native = _engine_manifold_chart(home)
    symbols = tuple(native[:])
    radius = _local_radius(home, center)
    inner = radius / 2
    formula = None
    if not _has_cauchy_coordinate(center):
        centers = tuple(_engine_manifold_expression(field(p)) for p in center)
        squared = sum((x - p)**2 for x, p in zip(symbols, centers, strict=True))
        formula = symbols[index] * smooth_step(radius**2 - squared, squared - inner**2,
                                               radius**2 - inner**2)

    def provider(chart, point, order):
        source = _engine_manifold_chart(chart)
        values = _coordinates_in_chart(chart, point)
        change = _coordinate_change_jets(source, values, native, field, order)
        if change is not None:
            if formula is None or _has_cauchy_coordinate(values) or getattr(
                    source.domain().manifold(), "_owned_coordinate_data", False):
                return _exact_bump_coordinate_jet(change, center, radius, index)
            return _symbolic_jet(field, formula, symbols,
                                 tuple(jet.value() for jet in change), order).compose(change)



        for label, target_label in manifold.transitions().keys():
            if target_label != home.label():
                continue
            current = manifold.atlas()[label]
            coordinates = _coordinate_change_jets(source, values, _engine_manifold_chart(current), field, 0)
            if coordinates is None:
                continue
            transition = manifold.transition(label, home.label())
            overlap = _engine_manifold_chart(transition.source_overlap_chart())
            local_values = tuple(jet.value() for jet in coordinates)
            if _valid_exact_coordinates(overlap, local_values) is False:
                return _TaylorJet.constant(field, len(values), order, field.zero())
            local = manifold.point(local_values, label)
            if any(ask(c(local) == field.zero()) is True
                   for c in transition.source_overlap()):
                return _TaylorJet.constant(field, len(values), order, field.zero())
        raise CoverageUndecided("the atlas does not certify whether the point belongs to the bump chart")

    return manifold.smooth_functions()(_SmoothGermFunction(manifold, provider))
