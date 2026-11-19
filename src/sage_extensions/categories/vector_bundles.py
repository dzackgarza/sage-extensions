r"""Smooth real vector bundles on a smooth manifold, and their modules of sections.

A smooth real vector bundle of rank ``r`` over a smooth manifold ``M`` is a
smooth manifold ``E`` with a smooth surjection ``E -> M`` whose fibres are
``r``-dimensional real vector spaces and which is locally a product: every point
of ``M`` has a neighbourhood over which the projection is the projection of
``U x R^r`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  A
section is a smooth map ``s: M -> E`` whose composite with the projection is the
identity, and the sections of one bundle form a module over the algebra
``C^oo(M)`` of smooth functions under the pointwise operations (Lee, Ch. 10).

The bundle this module owns first is the tangent bundle ``TM``, whose fibre at
``p`` is the tangent space ``T_pM`` (Lee, Ch. 3).  A vector field is a section of
``TM``, and it acts on a smooth function as a derivation,
``(V f)(p) = d_p f (V_p)``; conversely every derivation of ``C^oo(M)`` is the
derivative along a unique vector field, because a tangent vector at ``p`` is a
derivation of the algebra of germs of smooth functions there (Lee, Ch. 3).  The
two readings of a vector field are therefore one object, and this module states
both: a section is written by its components in the charts of an atlas, and it
is applied to a smooth function.

SageManifolds is the private realization.  Its tangent bundle, its scalar
fields and its vector fields carry the chart expressions and perform the
differentiation; none of them is a parent of an owned object, and the engine's
own answer to whether a bundle is trivial is never read.  A bundle is trivial
here exactly when a frame is stated for it -- a datum, not a flag about which
frames an engine happens to know.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.rational_field import QQ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject
from sage.symbolic.ring import SR

from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.manifolds import (
    CoverageUndecided,
    SmoothManifolds,
    _chart_family_covers,
    _engine_manifold_chart,
    _admit_manifold_expression,
    _chartwise_family_agrees,
    _chartwise_formulas,
    _engine_manifold,
    _engine_manifold_chart,
    _engine_manifold_expression,
    _raise_manifold_expression,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


def _engine_tangent_bundle(manifold):
    r"""The engine's tangent bundle of ``manifold`` (private adapter)."""
    return _engine_manifold(manifold).tangent_bundle()


def _engine_vector_field(manifold, components):
    r"""The engine's vector field with the given owned components, one tuple per chart.

    A vector field is stated on a chart by the components of its value in that
    chart's coordinate frame, and the engine's own object for it is assembled
    from exactly those: on each chart's domain the engine is told the
    components, and its transition maps are what make the result one object on
    the manifold.  Private computation adapter (``OWN-06``): the engine's
    vector field is the computation, and the owned section is built on it.
    """
    engine = _engine_manifold(manifold)
    field = engine.vector_field(name=f"a section of T{manifold.manifold_name()}")
    for label, component in components.items():
        chart = _engine_manifold_chart(manifold.atlas()[label])
        field.restrict(chart.domain())[chart.frame(), :] = [
            _engine_manifold_expression(entry) for entry in component
        ]
    return field


def _rational_polynomial(expression):
    r"""``expression``, a polynomial in one variable over the rationals, as that polynomial.

    A real polynomial with no real root is never zero, and the roots are found
    in the real algebraic numbers: the coefficients are the chart formulas'
    rational numbers, and an expression whose coefficients are not rational has
    no polynomial reading here and is refused by the caller.
    """
    return SR(expression).polynomial(QQ)


def _function_formula_on(function, manifold, label):
    r"""The engine formula of a smooth function on the chart ``label``, or ``None``.

    A smooth function is fixed by its expressions on a cover of the manifold, so its
    expression on any one chart is read from the chart it is stated on: writing ``y`` for
    the coordinates of ``label`` and ``x`` for those of the chart the function is stated
    on, the expression there is ``x = phi^{-1}(y)`` substituted into it (Lee,
    *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  ``None`` says no coordinate
    change the atlas states carries the function's expression to this chart.
    """
    from sage_extensions.categories.manifolds import _composed_ambient_transition

    formulas = _chartwise_formulas(function, manifold)
    if formulas is None:
        return None
    if label in formulas:
        return SR(formulas[label])
    symbols = tuple(_engine_manifold_chart(manifold.atlas()[label])[:])
    for other, formula in formulas.items():
        change = _composed_ambient_transition(manifold, other, label)
        if change is None:
            continue
        other_symbols = tuple(_engine_manifold_chart(manifold.atlas()[other])[:])
        pulled = SR(formula).subs(
            dict(
                zip(
                    other_symbols,
                    tuple(
                        SR(_engine_manifold_expression(expression))
                        for expression in change.inverse_expressions()
                    ),
                    strict=True,
                )
            )
        )
        if any(variable not in symbols for variable in pulled.variables()):
            continue
        return pulled
    return None


def _pullback_family_agrees(manifold, mapping, components, rank) -> None:
    r"""Decide that a chart-wise family states one section of a pullback, or state where it does not.

    A section of ``f^*E`` over ``N`` assigns to ``q`` an element of the fibre at
    ``f(q)``, and its tuple on a chart of ``N`` is read in the frame of a chart of the
    codomain that this chart is represented in (Lee, *Introduction to Smooth Manifolds*,
    2nd ed., Ch. 10).  Two charts ``W_s`` and ``W_t`` of the base therefore carry two
    frames, ``V_s`` and ``V_t``, and the tuples are related by the codomain's coordinate
    change at the image point:

        a_t(x) = J_{V_s -> V_t}(T_s(x)) a_s(x),

    where ``T_s`` carries a point of ``W_s`` to the coordinates of ``f`` in ``V_s``.  No
    derivative of ``f`` appears: the tuples are coordinates in the bundle's frames, not a
    vector field pushed along ``f``.  For ``f = id`` the codomain's change is the base's
    own, which is the case the earlier specimens exercised.

    The comparison is made on rational expressions, so nothing is sampled.
    """
    from itertools import combinations

    from sage.matrix.constructor import matrix as _engine_matrix

    from sage_extensions.categories.manifolds import _composed_ambient_transition

    labels = tuple(components)
    pairs = tuple(mapping.chart_maps().index_set())
    codomain = mapping.codomain()
    for left_label, right_label in combinations(labels, 2):
        for source_label, target_label in (
            (left_label, right_label),
            (right_label, left_label),
        ):
            change = _composed_ambient_transition(manifold, source_label, target_label)
            assert change is not None, (
                f"cannot decide whether the family states one section of the pullback: the "
                f"charts {source_label} and {target_label} are both given, and no chain of "
                f"stated coordinate changes joins them"
            )
            image_charts = {}
            for label in (source_label, target_label):
                images_in = tuple(pair for pair in pairs if pair[0] == label)
                assert images_in, (
                    f"cannot decide whether the family states one section of the pullback: the "
                    f"map {mapping} is stated in no chart of the codomain on the chart {label}"
                )
                image_charts[label] = images_in[0][1]
            source_symbols = tuple(_engine_manifold_chart(manifold.atlas()[source_label])[:])
            target_symbols = tuple(_engine_manifold_chart(manifold.atlas()[target_label])[:])
            forward = tuple(
                SR(_engine_manifold_expression(expression))
                for expression in change.forward_expressions()
            )
            image_in_source = tuple(
                SR(_engine_manifold_expression(expression))
                for expression in mapping.chart_map(
                    source_label, image_charts[source_label]
                )
            )
            assert len(image_in_source) == int(rank), (
                f"cannot decide whether the family states one section of the pullback: the map "
                f"{mapping} has {len(image_in_source)} coordinates in the chart "
                f"{image_charts[source_label]} and the pulled-back bundle has rank {rank}"
            )
            if image_charts[source_label] == image_charts[target_label]:
                jacobian = _engine_matrix(
                    SR,
                    int(rank),
                    int(rank),
                    [
                        1 if row == column else 0
                        for row in range(int(rank))
                        for column in range(int(rank))
                    ],
                )
            else:
                codomain_change = _composed_ambient_transition(
                    codomain, image_charts[source_label], image_charts[target_label]
                )
                assert codomain_change is not None, (
                    f"cannot decide whether the family states one section of the pullback: the "
                    f"codomain's charts {image_charts[source_label]} and "
                    f"{image_charts[target_label]} are joined by no stated coordinate change"
                )
                source_image_symbols = tuple(
                    _engine_manifold_chart(codomain.atlas()[image_charts[source_label]])[:]
                )
                substitution = dict(zip(source_image_symbols, image_in_source, strict=True))
                jacobian = _engine_matrix(
                    SR,
                    int(rank),
                    int(rank),
                    [
                        SR(_engine_manifold_expression(expression))
                        .diff(symbol)
                        .subs(substitution)
                        for expression in codomain_change.forward_expressions()
                        for symbol in source_image_symbols
                    ],
                )
            stated = tuple(
                SR(_engine_manifold_expression(entry))
                for entry in components[source_label]
            )
            carried = tuple(
                SR(_engine_manifold_expression(entry)).subs(
                    dict(zip(target_symbols, forward, strict=True))
                )
                for entry in components[target_label]
            )
            transported = tuple(
                sum(
                    stated[index] * jacobian[position, index]
                    for index in range(int(rank))
                )
                for position in range(int(rank))
            )
            for position, (left, right) in enumerate(
                zip(transported, carried, strict=True)
            ):
                residual = SR(left - right).simplify_rational()
                assert residual == 0, (
                    f"the family states no one section of the pullback: on the chart "
                    f"{source_label} the component {position} is {transported[position]}, and the "
                    f"component stated on the chart {target_label} is {carried[position]} there, "
                    f"which leaves the residual {residual}"
                )


def _section_components_on(section, label):
    r"""The components of ``section`` on the chart ``label``, transported from a chart it is stated on.

    A section is fixed by its components on a cover, and its components on another chart
    are related to them by the change of frame: for a vector field, writing ``y`` for the
    coordinates of ``label`` as functions of the coordinates ``x`` of a stated chart,
    ``a_t^j = sum_i a_s^i dy_j/dx_i`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
    Ch. 3); for a section of a pullback ``f^*E`` the change is that of the codomain's
    frames at the image point, ``a_t = J_{V_s -> V_t}(T_s(x)) a_s`` (Lee, Ch. 10).  The
    transported tuple is read back in ``y`` through the inverse of the coordinate change,
    as a smooth function's expression is (:func:`_function_formula_on`).
    """
    from sage.matrix.constructor import matrix as _engine_matrix

    from sage_extensions.categories.manifolds import _composed_ambient_transition

    module = element_parent(section)
    manifold = module.base_manifold()
    stated = section.components()
    if label in stated:
        return stated[label]
    bundle = module.vector_bundle()
    rank = int(bundle.rank())
    chart = manifold.atlas()[label]
    target_symbols = tuple(_engine_manifold_chart(chart)[:])
    underlying = bundle.underlying_bundle()
    for source_label, component in stated.items():
        change = _composed_ambient_transition(manifold, source_label, label)
        if change is None:
            continue
        source_symbols = tuple(_engine_manifold_chart(manifold.atlas()[source_label])[:])
        if underlying is None:
            jacobian = _engine_matrix(
                SR,
                rank,
                rank,
                [
                    SR(_engine_manifold_expression(expression)).diff(symbol)
                    for expression in change.forward_expressions()
                    for symbol in source_symbols
                ],
            )
        else:
            mapping = bundle.mapping()
            codomain = mapping.codomain()
            pairs = tuple(mapping.chart_maps().index_set())
            image_source = next(pair[1] for pair in pairs if pair[0] == source_label)
            image_target = next(pair[1] for pair in pairs if pair[0] == label)
            if image_source == image_target:
                jacobian = _engine_matrix(SR, rank, rank, 1)
            else:
                codomain_change = _composed_ambient_transition(
                    codomain, image_source, image_target
                )
                assert codomain_change is not None, (
                    f"cannot carry {section} to the chart {label}: the codomain's charts "
                    f"{image_source} and {image_target} are joined by no stated coordinate change"
                )
                image_symbols = tuple(_engine_manifold_chart(codomain.atlas()[image_source])[:])
                image = tuple(
                    SR(_engine_manifold_expression(expression))
                    for expression in mapping.chart_map(source_label, image_source)
                )
                jacobian = _engine_matrix(
                    SR,
                    rank,
                    rank,
                    [
                        SR(_engine_manifold_expression(expression))
                        .diff(symbol)
                        .subs(dict(zip(image_symbols, image, strict=True)))
                        for expression in codomain_change.forward_expressions()
                        for symbol in image_symbols
                    ],
                )
        back = dict(
            zip(
                source_symbols,
                tuple(
                    SR(_engine_manifold_expression(expression))
                    for expression in change.inverse_expressions()
                ),
                strict=True,
            )
        )
        entries = tuple(
            SR(
                sum(
                    jacobian[row, column] * SR(_engine_manifold_expression(component[column]))
                    for column in range(rank)
                )
            )
            .subs(back)
            .simplify_rational()
            for row in range(rank)
        )
        if any(
            variable not in target_symbols
            for entry in entries
            for variable in entry.variables()
        ):
            continue
        return tuple(_raise_manifold_expression(entry, chart) for entry in entries)
    assert False, (
        f"cannot carry {section} to the chart {label}: it is stated on {tuple(stated)}, and no "
        f"chain of stated coordinate changes joins any of them to {label}"
    )


def _decided_nowhere_vanishing(expression, variables, excluded=()):
    r"""Whether the real function ``expression`` of ``variables`` is decided to take no zero.

    A component of a frame is a real-valued function on a chart's domain, and the
    charts of a manifold take values in the real coordinates, so the component
    vanishes nowhere when its numerator -- it is read as a fraction of
    polynomials, as every chart expression of this tree is -- takes no real zero
    at any point: a real polynomial with no real root is never zero, and a
    constant is decided by the exact reals.  ``True`` and ``False`` are
    decisions, and ``None`` is the statement that this owner does not decide the
    question for the expression it was given.

    ``excluded`` are the functions whose common nonvanishing locus is the
    chart's domain (:meth:`ManifoldAtlasChart.nonvanishing`): the question is
    asked on that domain, so the exact powers of those functions are divided out
    of the numerator first, and the remainder has to vanish nowhere at all.  A
    chart read on a proper open subset therefore decides what a chart of the whole
    manifold cannot: on the south chart of $S^2$, the north chart's coordinate
    frame has determinant $-\lvert y\rvert^4$, whose only zero is the pole the
    chart excludes by $\lvert y\rvert^2 \ne 0$, so the remainder after dividing
    twice is $-1$.

    A denominator is not decided here: a chart expression that divides is stated
    where its denominator does not vanish (``ManifoldAtlasChart.section_ratio``),
    and that nonvanishing is the overlap the chart's own transition states.
    """
    from sage.rings.qqbar import AA

    from sage_extensions.categories.functions.real_functions import _decided_nonzero

    numerator = SR(SR(expression).simplify_rational().numerator())
    for condition in tuple(excluded):
        factor = SR(SR(condition).simplify_rational())
        if not factor.variables():
            continue
        for _factor_power in range(8):
            quotient = SR(numerator / factor).simplify_rational()
            if SR(quotient.denominator()).simplify_rational() != 1:
                break
            if SR(quotient * factor - numerator).simplify_rational() != 0:
                break
            numerator = quotient
    return _decided_no_real_zero(numerator, variables)


def _definiteness(matrix):
    r"""``+1``, ``-1``, ``0`` or ``None``: definite, semidefinite of either sign, or indefinite, by Sylvester's criterion.

    A symmetric matrix over the rationals is positive definite exactly when all of
    its leading principal minors are positive, and negative definite exactly when
    those minors alternate in sign (Sylvester's criterion; Horn and Johnson,
    *Matrix Analysis*, 2nd ed., Thm. 7.2.5).  A matrix that is neither is called
    semidefinite of both signs when every principal minor is nonnegative or every
    one of odd order is nonpositive with every one of even order nonnegative
    (Thm. 7.2.4 for the principal-minor form), and indefinite otherwise.
    """
    size_count = matrix.nrows()
    leading = tuple(
        matrix[: size, : size].det() for size in range(1, size_count + 1)
    )
    if all(entry > 0 for entry in leading):
        return 1
    if all(
        (entry if size % 2 == 0 else -entry) > 0
        for size, entry in enumerate(leading, start=1)
    ):
        return -1
    if size_count > 4:
        return None
    principal = []
    for size in range(1, size_count + 1):
        for subset in _subsets_of_size(size_count, size):
            principal.append((size, matrix[list(subset), list(subset)].det()))
    if all(entry >= 0 for _size, entry in principal):
        return 0
    if all((entry if size % 2 == 0 else -entry) >= 0 for size, entry in principal):
        return 0
    return None


def _subsets_of_size(size_count, size):
    r"""The subsets of ``{0, ..., size_count - 1}`` of ``size`` elements, in order."""
    from itertools import combinations

    return tuple(combinations(range(size_count), size))


def _quadratic_minimum(matrix, vector, constant):
    r"""The minimum of ``x^T matrix x + vector^T x + constant`` over the range of a semidefinite matrix, or ``None``.

    For a positive semidefinite ``A`` the form is ``(x + u)^T A (x + u) + c - u^T A u``
    with ``A u = b/2``: constant along the kernel and minimised at ``-u`` on the
    range (Horn and Johnson, *Matrix Analysis*, 2nd ed., §7.1), so its minimum is
    ``c - u^T A u`` and does not depend on which solution ``u`` is taken.  ``None``
    is the answer when ``b/2`` is not in the range of ``A``, which makes the form
    unbounded below and therefore a form that takes the value zero.
    """
    coefficient_ring = matrix.base_ring()
    half = coefficient_ring(1) / coefficient_ring(2)
    target = half * vector
    augmented = matrix.augment(target.column())
    if augmented.rank() != matrix.rank():
        return None
    if target.is_zero():
        return constant
    try:
        solution = matrix.solve_right(target)
    except (ValueError, ZeroDivisionError):
        return None
    return constant - solution.dot_product(matrix * solution)


def _decided_quadratic(polynomial):
    r"""Whether a polynomial of degree at most two takes no zero, decided by its quadratic form.

    Writing the polynomial as ``x^T A x + b^T x + c`` over the rationals, the form
    takes no zero exactly when its minimum is positive -- a form whose minimum is
    zero takes that value, and one whose minimum is negative takes the value zero on
    the way to its negative values.  The minimum is ``c - (1/4) b^T A^{-1} b`` for a
    definite ``A`` and ``c - u^T A u`` for a semidefinite one with ``A u = b/2``
    (:func:`_quadratic_minimum`).  An indefinite quadratic part makes the form
    unbounded in both directions, so it takes the value zero too.

    ``None`` is answered for a polynomial of higher degree, and for a semidefinite
    form whose linear part leaves the range of its quadratic part in a case this
    decision does not solve.
    """
    from sage.matrix.constructor import matrix as _engine_matrix
    from sage.rings.rational_field import QQ as SageQQ

    ring = polynomial.parent()
    if polynomial.total_degree() > 2:
        return None
    variables = ring.gens()
    number = len(variables)
    linear = [SageQQ.zero() for _index in range(number)]
    form = [[SageQQ.zero() for _index in range(number)] for _index in range(number)]
    constant = SageQQ.zero()
    for exponents, coefficient in polynomial.dict().items():
        powers = tuple(int(power) for power in exponents)
        degree = sum(powers)
        if degree == 0:
            constant = coefficient
        elif degree == 1:
            linear[powers.index(1)] = coefficient
        else:
            filled = tuple(index for index, power in enumerate(powers) if power)
            if len(filled) == 1:
                form[filled[0]][filled[0]] = coefficient
            else:
                first, second = filled
                form[first][second] = coefficient / SageQQ(2)
                form[second][first] = coefficient / SageQQ(2)
    matrix = _engine_matrix(SageQQ, number, number, [entry for row in form for entry in row])
    vector = __import__("sage.modules.free_module_element", fromlist=["vector"]).vector(SageQQ, linear)
    match _definiteness(matrix):
        case 1:
            minimum = constant - (vector.dot_product(matrix.inverse() * vector)) / 4
            return minimum > 0
        case -1:
            minimum = -(constant - (vector.dot_product(matrix.inverse() * vector)) / 4)
            return minimum > 0
        case 0:
            if not matrix.is_zero() and not any(entry != 0 for entry in linear):
                minimum = _quadratic_minimum(matrix, vector, constant)
                return None if minimum is None else minimum > 0
            if matrix.is_zero():
                return False if any(entry != 0 for entry in linear) else None
            return None
        case _:
            return False


def _decided_gram_no_zero(polynomial):
    r"""Whether a quartic bounded away from zero is decided so by a Gram certificate, or ``None``.

    A polynomial ``P`` of degree ``2d`` is a sum of squares of polynomials of degree
    ``d`` when some positive semidefinite ``G`` satisfies ``P - P(0) = u^T G u`` for ``u``
    the monomials of degree ``d``; with ``P(0) > 0`` that makes ``P`` bounded away from
    zero (Lasserre, *Moments, Positive Polynomials and Their Applications*, Ch. 2).  The
    monomials of ``P - P(0)`` are of degree ``2d``, and each splits into two of degree
    ``d`` in finitely many ways; a monomial with more than one split -- ``x^2 y^2`` splits
    as ``(x^2)(y^2)`` and as ``(xy)(xy)`` -- gives a different ``G`` for each choice, and
    the certificate is found by trying them.

    ``True`` is a proof, ``False`` is answered only when the constant term is zero (then
    the chart's origin is a zero), and ``None`` says this certificate does not decide the
    polynomial: it is a sufficient condition, and a quartic that is positive without being
    a sum of squares of quadratics is left undecided.
    """
    from itertools import product as _iproduct

    from sage.matrix.constructor import matrix as _engine_matrix
    from sage.rings.rational_field import QQ as SageQQ

    coefficients = {
        tuple(int(power) for power in monomial): coefficient
        for monomial, coefficient in polynomial.dict().items()
    }
    if not coefficients:
        return False
    variables = polynomial.parent().ngens()
    constant = coefficients.get(tuple(0 for _index in range(variables)), SageQQ.zero())
    degree = max(sum(monomial) for monomial in coefficients)
    if degree % 2 or degree < 4 or degree > 4:
        return None
    half = degree // 2
    part = {
        monomial: coefficient
        for monomial, coefficient in coefficients.items()
        if sum(monomial) > 0
    }
    if not part or any(sum(monomial) != degree for monomial in part):
        return None
    if constant == 0:
        return False
    monomials = [
        exponent
        for exponent in _iproduct(range(half + 1), repeat=variables)
        if sum(exponent) == half
    ]
    position = {exponent: index for index, exponent in enumerate(monomials)}
    splits = {}
    for monomial in part:
        options = [
            (left, tuple(whole - piece for whole, piece in zip(monomial, left)))
            for left in monomials
            if all(piece <= whole for piece, whole in zip(left, monomial))
            and tuple(whole - piece for whole, piece in zip(monomial, left)) in position
        ]
        if not options:
            return None
        splits[monomial] = options
    count = 1
    for options in splits.values():
        count *= len(options)
    if count > 64:
        return None
    order = tuple(part)
    for choice in _iproduct(*[splits[monomial] for monomial in order]):
        size = len(monomials)
        entries = [SageQQ.zero() for _index in range(size * size)]
        for monomial, (left, right) in zip(order, choice):
            coefficient = part[monomial]
            row, column = position[left], position[right]
            if row == column:
                entries[row * size + column] += coefficient
            else:
                entries[row * size + column] += coefficient / SageQQ(2)
                entries[column * size + row] += coefficient / SageQQ(2)
        gram = _engine_matrix(SageQQ, size, size, entries)
        if _gram_is_semidefinite(gram):
            return True
    return None


def _gram_is_semidefinite(matrix) -> bool:
    r"""Whether a symmetric matrix over the rationals has every principal minor nonnegative.

    A symmetric real matrix is positive semidefinite exactly when all of its principal
    minors are nonnegative (Horn and Johnson, *Matrix Analysis*, 2nd ed., Thm. 7.2.4);
    the test is exact over the rationals and is applied only to matrices small enough for
    every principal minor to be taken.
    """
    from itertools import combinations

    size = matrix.nrows()
    for order in range(1, size + 1):
        for rows in combinations(range(size), order):
            if matrix[list(rows), list(rows)].det() < 0:
                return False
    return True


def _decided_no_real_zero(expression, variables):
    r"""Whether the real polynomial ``expression`` is decided to take no zero on the chart.

    Three cases are decided, and each is a proof rather than a sample.  A constant
    is decided by the exact reals.  A polynomial of one variable is decided by
    having no root in the real algebraic numbers, since a real polynomial with no
    real root is never zero.  A polynomial of several variables is decided by its
    monomials: when every exponent is even, every coefficient has the same sign,
    and the constant term is nonzero with that sign, the polynomial is bounded away
    from zero on the whole chart -- ``1 + x^2 + x^2y^2 >= 1`` -- and vanishes
    nowhere; when the constant term is zero it vanishes at the chart's origin,
    which is a decision the other way.  Anything else is undecided here, and the
    caller is told that rather than that its determinant vanishes.
    """
    from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
    from sage.rings.rational_field import QQ as SageQQ

    from sage_extensions.categories.functions.real_functions import _decided_nonzero

    formula = SR(expression).simplify_rational()
    numerator = SR(formula.numerator())
    given = tuple(variables)
    if not tuple(numerator.variables()):
        return _decided_nonzero(numerator)
    if len(given) == 1 and numerator.is_polynomial(given[0]):
        from sage.rings.qqbar import AA

        return not tuple(_rational_polynomial(numerator).roots(AA))
    names = tuple(str(variable) for variable in given)
    ring = PolynomialRing(SageQQ, names=names)
    try:
        polynomial = ring(numerator)
    except (TypeError, ValueError):
        return None
    quadratic = _decided_quadratic(polynomial)
    if quadratic is not None:
        return quadratic
    gram = _decided_gram_no_zero(polynomial)
    if gram is not None:
        return gram
    coefficients = {
        tuple(int(power) for power in monomial): coefficient
        for monomial, coefficient in polynomial.dict().items()
    }
    if not coefficients:
        return False
    monomials = tuple(coefficients)
    if not all(
        all(power % 2 == 0 for power in monomial) for monomial in monomials
    ):
        return None
    constant = coefficients.get(tuple(0 for _ in names), SageQQ.zero())
    if constant == 0:
        return False
    values = tuple(coefficients[monomial] for monomial in monomials)
    if all(value > 0 for value in values) and constant > 0:
        return True
    if all(value < 0 for value in values) and constant < 0:
        return True
    return None


def _is_an_open_inclusion(mapping, domain, manifold) -> bool:
    r"""Whether ``mapping`` is the inclusion of an open submanifold of ``manifold``, read in the charts both carry.

    The inclusion of an open submanifold reads the same coordinates on the
    charts it shares with the manifold (``SmoothManifolds.open_submanifold``),
    so its coordinate representations are the identity: on each shared label the
    ``i``-th coordinate of the target is the ``i``-th coordinate of the source
    (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example 1.4).  A map whose
    representations are not the identity is no inclusion, and the pullback of the
    tangent bundle along it is not the tangent bundle of its domain.
    """
    if int(domain.dimension()) != int(manifold.dimension()):
        return False
    shared = tuple(
        label for label in domain.chart_labels() if label in manifold.chart_labels()
    )
    if not shared:
        return False
    index_set = tuple(mapping.chart_maps().index_set())
    stated = tuple(
        pair for pair in index_set if pair[0] == pair[1] and pair[0] in shared
    )
    if not stated:
        return False
    for source_label, target_label in stated:
        expressions = tuple(mapping.chart_map(source_label, target_label))
        symbols = tuple(_engine_manifold_chart(domain.atlas()[source_label])[:])
        if len(expressions) != len(symbols):
            return False
        for expression, symbol in zip(expressions, symbols, strict=True):
            if SR(_engine_manifold_expression(expression) - symbol).simplify_rational() != 0:
                return False
    # A label it does not state adds no point, exactly when its chart lies inside a
    # chart it does state: the map is then the identity there too.
    presented = tuple(_engine_manifold_chart(domain.atlas()[label]).domain() for label, _ in stated)
    for label in shared:
        if (label, label) in stated:
            continue
        chart_domain = _engine_manifold_chart(domain.atlas()[label]).domain()
        if not any(chart_domain.is_subset(one) for one in presented):
            return False
    return True


class SmoothVectorBundles(OwnedParameterizedCategory):
    r"""Smooth real vector bundles on one smooth manifold.

    An object is a bundle of a stated finite rank over the parameter manifold,
    and its sections are the objects of :class:`SmoothSectionModules`.  The
    tangent bundle is the one every smooth manifold carries, and it is a bundle
    before it is a trivialization: a frame is a datum a caller states, never a
    fact this owner infers from the frames an engine happens to know.
    """

    def parameter_category(self):
        return SmoothManifolds()

    def super_categories(self):
        r"""A bundle is, in particular, a set: the points of its total space.

        No finer owned supercategory is stated here.  A vector bundle over a
        manifold is not a manifold of this tree's own, and naming one would make
        this family a subcategory of a construction that does not exist rather
        than the one datum it does state -- a rank over a base.
        """
        return [Sets()]

    def base_manifold(self):
        r"""The manifold every bundle of this family is over."""
        return self._owned_parameter

    def _repr_object_names(self):
        return f"smooth real vector bundles on {self.base_manifold()}"

    def tangent_bundle(self):
        r"""``TM``, the bundle whose fibre at ``p`` is the tangent space ``T_pM``.

        The tangent space ``T_pM`` is the vector space of derivations of the
        algebra of germs of smooth functions at ``p`` (Lee, *Introduction to
        Smooth Manifolds*, 2nd ed., Ch. 3), so the fibres are real vector spaces
        of dimension ``dim(M)`` and their disjoint union over the charts is a
        smooth vector bundle of that rank (Lee, Ch. 3 and Ch. 10).  No
        trivialization comes with it: a frame is retained only when a caller
        states one (:meth:`SmoothSectionModules.ParentMethods.trivialized_by`).
        """
        manifold = self.base_manifold()
        return _object_of(
            self,
            bundle_base_manifold=manifold,
            bundle_rank=manifold.dimension(),
            engine_bundle=_engine_tangent_bundle(manifold),
            bundle_tangent_manifold=manifold,
        )

    class ParentMethods:
        def __init__(
            self,
            bundle_base_manifold,
            bundle_rank,
            engine_bundle,
            bundle_tangent_manifold=None,
            bundle_underlying=None,
            bundle_mapping=None,
            **rest,
        ) -> None:
            self._bundle_base_manifold = bundle_base_manifold
            self._bundle_rank = bundle_rank
            self._engine_bundle = engine_bundle
            self._bundle_tangent_manifold = bundle_tangent_manifold
            self._bundle_underlying = bundle_underlying
            self._bundle_mapping = bundle_mapping
            super().__init__(**rest)

        def base_manifold(self):
            r"""The manifold this bundle is over."""
            return self._bundle_base_manifold

        def rank(self):
            r"""The rank of this bundle: the dimension of each of its fibres."""
            return self._bundle_rank

        @cached_method
        def sections(self):
            r"""The ``C^oo(M)``-module of smooth sections of this bundle.

            A section assigns to each point of the base a point of the fibre
            over it, smoothly (Lee, *Introduction to Smooth Manifolds*, 2nd
            ed., Ch. 10).  The sections are the objects of
            :class:`SmoothSectionModules`, and the module is this bundle's: two
            bundles that differ only in a frame read the same sections.
            """
            return _object_of(
                SmoothSectionModules(self),
                vector_bundle=self,
                base_ring=self.base_manifold().smooth_functions(),
                retained_frame=None,
            )

        def pullback_along(self, mapping):
            r"""The bundle pulled back along a smooth map into this bundle's base.

            A section of the pullback ``f^*E`` over ``N`` is a map into the fibres
            over the image, ``q |-> s(f(q))`` (Lee, *Introduction to Smooth
            Manifolds*, 2nd ed., Ch. 10, where the pullback of a vector bundle is
            the bundle whose fibre at ``q`` is the fibre of ``E`` at ``f(q)``).
            For an open inclusion the differential is an isomorphism at every
            point, so the pullback of the tangent bundle is the tangent bundle of
            the inclusion's domain, and that is what is returned there.  Along
            any other smooth map the pullback is its own bundle over the map's
            domain: its sections are the pullbacks of the bundle's sections
            (:meth:`SmoothSectionModules.ParentMethods.pullback_of`), and a
            section of it that is not the pullback of one needs the bundle's
            transition functions on a cover of the target, which this owner does
            not retain.
            """
            manifold = self.base_manifold()
            assert mapping.codomain() is manifold, (
                f"cannot pull {self} back along {mapping}: it ends at "
                f"{mapping.codomain()}, not at the bundle's base {manifold}"
            )
            domain = mapping.domain()
            assert domain in SmoothManifolds(), (
                f"cannot pull {self} back along {mapping}: its domain {domain} is not a smooth "
                f"manifold"
            )
            if self._bundle_tangent_manifold is not None and _is_an_open_inclusion(
                mapping, domain, manifold
            ):
                return domain.tangent_bundle()
            from sage_extensions.categories.vector_bundles import SmoothVectorBundles as _bundles

            return _object_of(
                _bundles(domain),
                bundle_base_manifold=domain,
                bundle_rank=self.rank(),
                engine_bundle=self._engine_bundle,
                bundle_underlying=self,
                bundle_mapping=mapping,
            )

        def underlying_bundle(self):
            r"""The bundle this one is pulled back from, or ``None`` for a bundle read on its own base."""
            return self._bundle_underlying

        def mapping(self):
            r"""The smooth map this bundle is pulled back along, or ``None``."""
            return self._bundle_mapping

        def is_pullback(self) -> bool:
            r"""Whether this bundle is a pullback, stated by the bundle and the map it retains."""
            return self._bundle_underlying is not None

        def _repr_(self):
            if self._bundle_underlying is not None:
                return (
                    f"the pullback of {self._bundle_underlying} along {self._bundle_mapping}"
                )
            return (
                f"rank-{self.rank()} smooth real vector bundle on {self.base_manifold()}"
            )


class SmoothSectionModules(OwnedParameterizedCategory):
    r"""The ``C^oo(M)``-module of smooth sections of one smooth vector bundle.

    Sections are added and scaled pointwise in the fibres, so they form a module
    over the functions on the base (Lee, *Introduction to Smooth Manifolds*,
    2nd ed., Ch. 10).  For the tangent bundle the same module is the module of
    derivations of ``C^oo(M)``: a section applies to a smooth function by the
    derivation law the tangent space is defined by (Lee, Ch. 3), and the result
    is the element of ``C^oo(M)`` the derivation takes.

    The module is free exactly when a frame is retained
    (:meth:`SmoothSectionModules.ParentMethods.trivialized_by`); the rank of a
    module of sections is not read off how many charts happen to exist.
    """

    def parameter_category(self):
        return SmoothVectorBundles(self._owned_parameter.base_manifold())

    def vector_bundle(self):
        r"""The bundle whose sections these are."""
        return self._owned_parameter

    def base_ring(self):
        r"""``C^oo(M)``, the algebra the sections are a module over."""
        return self.vector_bundle().base_manifold().smooth_functions()

    def super_categories(self):
        return [Modules(self.base_ring())]

    def _repr_object_names(self):
        return f"smooth sections of {self.vector_bundle()}"

    class ElementMethods(Element):
        r"""A smooth section: one tuple of components per chart, agreeing under the transitions.

        The section is the datum of its components in the charts of the atlas;
        :meth:`SmoothSectionModules.ParentMethods.section` is the one
        constructor, and it decides that the components state one object on the
        manifold rather than one object per chart.
        """

        def __init__(self, parent, components, engine_field) -> None:
            Element.__init__(self, parent)
            self._components = components
            self._engine_field = engine_field

        def components(self):
            r"""The components of the section in each chart's coordinate frame."""
            return self._components

        def __call__(self, function):
            r"""The derivative ``V f`` of a smooth function along this section.

            A vector field is a derivation of the smooth functions (Lee,
            *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3), so applying it
            to ``f`` gives the smooth function whose value at ``p`` is
            ``d_p f (V_p)``.  The engine differentiates the chart expressions
            of ``f`` along the components of ``V``, and the result is raised to
            a smooth function chart by chart.
            """
            manifold = self.parent().base_manifold()
            assert self.parent().vector_bundle()._bundle_tangent_manifold is not None, (
                f"the sections of {self.parent().vector_bundle()} are not vector fields: a "
                f"derivation of C^oo is a section of the tangent bundle, and this bundle is "
                f"not the tangent bundle of its base"
            )
            assert element_parent(function) is manifold.smooth_functions(), (
                f"{function} is not a smooth function on {manifold}: a section of "
                f"{self.parent().vector_bundle()} is a derivation of "
                f"{manifold.smooth_functions()}, and its parent is "
                f"{element_parent(function)}"
            )
            formulas = _chartwise_formulas(function, manifold)
            assert formulas is not None, (
                f"cannot differentiate {function} along {self}: the function is not written by "
                f"chart expressions, and a derivation is computed on the expressions both are "
                f"written by"
            )
            engine = _engine_manifold(manifold)
            scalar_field = engine.scalar_field(
                {
                    _engine_manifold_chart(manifold.atlas()[label]): formula
                    for label, formula in formulas.items()
                }
            )
            derivative = self._engine_field(scalar_field)
            return manifold.smooth_function(
                {
                    label: _raise_manifold_expression(
                        derivative.expr(_engine_manifold_chart(manifold.atlas()[label])),
                        manifold.atlas()[label],
                    )
                    for label in manifold.chart_labels()
                }
            )

        def _add_(self, other):
            r"""``V + W``: the section whose value at ``p`` is ``V(p) + W(p)``."""
            components = self.components()
            other_components = other.components()
            return self.parent()._construct(
                {
                    label: tuple(
                        left + right
                        for left, right in zip(
                            component, other_components[label], strict=True
                        )
                    )
                    for label, component in components.items()
                }
            )

        def _neg_(self):
            r"""``-V``: the section whose value at ``p`` is ``-V(p)``."""
            return self.parent()._construct(
                {
                    label: tuple(-entry for entry in component)
                    for label, component in self.components().items()
                }
            )

        def _lmul_(self, scalar):
            r"""``f V``: the pointwise action of the functions on the base."""
            return self.parent().scalar_multiple(scalar, self)

        def __eq__(self, other) -> bool:
            r"""Two sections of one bundle are equal when their components agree in every chart.

            The components of a section in a chart are its values in that
            chart's coordinate frame, and the frames of the charts of an atlas
            are related by the transitions, so the components agree in one
            chart exactly when they agree in every chart.
            """
            if element_parent(other) is not self.parent():
                return False
            shared = tuple(
                label for label in self._components if label in other.components()
            )
            assert shared, (
                f"cannot decide whether {self} and {other} are equal: they are stated on "
                f"disjoint families of charts, {tuple(self._components)} and "
                f"{tuple(other.components())}"
            )
            for label in shared:
                component = self._components[label]
                other_component = other.components()[label]
                for left, right in zip(component, other_component, strict=True):
                    residual = SR(
                        _engine_manifold_expression(left) - _engine_manifold_expression(right)
                    ).simplify_full()
                    if residual != 0:
                        return False
            return True

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash((id(self.parent()), id(self)))

        def _repr_(self):
            return f"a section of {self.parent().vector_bundle()}"

    class ParentMethods:
        def __init__(self, vector_bundle, base_ring, retained_frame=None, **rest) -> None:
            self._vector_bundle = vector_bundle
            self._base_ring = base_ring
            self._retained_frame = retained_frame
            super().__init__(base_ring=base_ring, **rest)

        def vector_bundle(self):
            r"""The bundle whose sections these are."""
            return self._vector_bundle

        def base_manifold(self):
            r"""The manifold the sections are defined on."""
            return self._vector_bundle.base_manifold()

        def base_ring(self):
            r"""``C^oo(M)``, the algebra the sections are a module over."""
            return self._base_ring

        def _construct(self, components):
            r"""The section with these components, built without re-deciding that they state one object.

            The callers are this module's own operations -- the sum, the negative,
            the scalar multiple -- and the pullback of a section, which produce
            components that agree on the overlaps because their operands do;
            :meth:`section` is where a caller's own components are decided.
            """
            return self.element_class(self, components, self._engine_field(components))

        def _engine_field(self, components):
            r"""The engine vector field of the section with these components, or ``None``.

            Only the tangent bundle's own sections are vector fields on the base,
            and they carry the engine field a derivation is read from; a section of
            a pullback takes its values in the fibres of another bundle, with as
            many components as that bundle's rank, and is no vector field here.
            """
            if (
                self._vector_bundle.underlying_bundle() is None
                and self._vector_bundle._bundle_tangent_manifold is not None
            ):
                return _engine_vector_field(self.base_manifold(), components)
            return None

        def zero(self):
            r"""The zero section: the component zero in every chart's coordinate frame."""
            manifold = self.base_manifold()
            return self.section(
                {
                    label: tuple(
                        manifold.atlas()[label].function_ring().zero()
                        for _index in range(int(self._vector_bundle.rank()))
                    )
                    for label in manifold.chart_labels()
                }
            )

        def scalar_multiple(self, scalar, element):
            r"""``f V``: the section whose value at ``p`` is ``f(p) V(p)``.

            A section is a map into the fibres and the functions on the base act
            on it pointwise, which is what makes the sections a module over
            ``C^oo(M)`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 10).  The product is read from the function's own chart
            expressions and the section's components there.
            """
            manifold = self.base_manifold()
            assert element_parent(scalar) is self.base_ring(), (
                f"{scalar} is not a function on {manifold}: the sections of "
                f"{self._vector_bundle} are a module over {self.base_ring()}, and the scalar's "
                f"parent is {element_parent(scalar)}"
            )
            assert element_parent(element) is self, (
                f"{element} is not a section of {self._vector_bundle}: its parent is "
                f"{element_parent(element)}"
            )
            formulas = _chartwise_formulas(scalar, manifold)
            assert formulas is not None, (
                f"cannot multiply the section {element} by {scalar}: the function is not "
                f"written by chart expressions, and the product is read from the expressions "
                f"both are written by"
            )
            components = element.components()
            return self._construct(
                {
                    label: tuple(
                        _raise_manifold_expression(
                            formulas[label] * _engine_manifold_expression(entry),
                            manifold.atlas()[label],
                        )
                        for entry in components[label]
                    )
                    for label in manifold.chart_labels()
                }
            )

        def section(self, components):
            r"""The section whose component in each chart is ``components[label]``.

            A section is stated on a chart by the components of its value in
            that chart's coordinate frame, and the components of one section are
            related by the derivative of the atlas transitions: writing ``y``
            for the coordinates of the target chart as functions of the
            coordinates ``x`` of the source chart, a vector field's components
            satisfy ``a_t^j(y(x)) = sum_i a_s^i(x) dy_j/dx_i`` (Lee,
            *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3).  A family that
            does not satisfy that is a different vector field on each chart, and
            is refused here rather than becoming a section of anything.
            """
            manifold = self.base_manifold()
            atlas = manifold.atlas()

            labels = tuple(components)
            extra = tuple(label for label in labels if label not in manifold.chart_labels())
            assert not extra, (
                f"a section of {self._vector_bundle} is stated on the charts of {manifold}, "
                f"and the components given for {extra} are on charts it does not have"
            )
            coverage = _chart_family_covers(manifold, labels)
            if coverage is not True:
                if coverage is False:
                    assert False, (
                        f"a section of {self._vector_bundle} is stated on a cover of {manifold}, "
                        f"and the charts {labels} do not cover it: a chart of the atlas lies "
                        f"outside every one of them, so its points would have no component"
                    )
                raise CoverageUndecided(
                    f"whether the charts {labels} cover {manifold} is undecided: no certificate "
                    f"decides it, so a section of {self._vector_bundle} is not refused for failing "
                    f"to cover"
                )
            admitted = {}
            for label in labels:
                chart = atlas[label]
                component = tuple(components[label])
                assert len(component) == int(self._vector_bundle.rank()), (
                    f"a section of the rank-{self._vector_bundle.rank()} bundle "
                    f"{self._vector_bundle} has {self._vector_bundle.rank()} components in every "
                    f"chart, and the component given on the chart {label} has {len(component)}"
                )
                admitted[label] = tuple(
                    _admit_manifold_expression(entry, chart) for entry in component
                )
            underlying = self._vector_bundle.underlying_bundle()
            if underlying is None:
                _chartwise_family_agrees(manifold, admitted, 1)
            else:
                _pullback_family_agrees(
                    manifold,
                    self._vector_bundle.mapping(),
                    admitted,
                    int(self._vector_bundle.rank()),
                )
            return self.element_class(self, admitted, self._engine_field(admitted))

        def coordinate_vector_field(self, chart, index):
            r"""The ``index``-th coordinate vector field of a chart, as a section of this bundle.

            The coordinates of a chart ``phi: U -> R^n`` are functions on ``U``,
            and ``d/dx_i`` is the vector field that differentiates along the
            ``i``-th of them, a basis of the tangent space at every point of the
            chart (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3).  It
            is stated in every chart of the atlas: on its own chart its
            components are the ``index``-th unit vector, and on any other chart
            they are the derivative of the coordinate change -- writing ``y``
            for the other chart's coordinates, the components are
            ``dy_j/dx_index``, read back in the other chart's coordinates.
            """
            from sage.symbolic.ring import SR as _SR

            manifold = self.base_manifold()
            labels = tuple(manifold.chart_labels())
            assert any(chart is present for present in manifold.atlas().values()), (
                f"{chart} is not a chart of {manifold}: its charts are "
                f"{tuple(manifold.chart_labels())}"
            )
            rank = int(self._vector_bundle.rank())
            position = int(index)
            assert 0 <= position < rank, (
                f"the chart {chart.label()} has {rank} coordinates, and there is no "
                f"coordinate {position}"
            )
            ring = chart.function_ring()
            components = {
                chart.label(): tuple(
                    ring.one() if entry == position else ring.zero()
                    for entry in range(rank)
                )
            }
            stated = tuple(pair for pair in manifold.transitions().index_set())
            given_domain = _engine_manifold_chart(chart).domain()
            for label in labels:
                if label == chart.label():
                    continue
                if (chart.label(), label) not in stated:
                    continue
                if _engine_manifold_chart(manifold.atlas()[label]).domain().is_subset(
                    given_domain
                ):
                    continue
                forward_transition = manifold.transition(chart.label(), label)
                variables = tuple(_engine_manifold_chart(forward_transition.source())[:])
                forward = tuple(
                    _SR(_engine_manifold_expression(expression))
                    for expression in forward_transition.forward_expressions()
                )
                column = tuple(
                    expression.diff(variables[position]) for expression in forward
                )
                backward = tuple(
                    _SR(_engine_manifold_expression(expression))
                    for expression in manifold.transition(
                        label, chart.label()
                    ).forward_expressions()
                )
                in_the_chart = tuple(
                    _SR(entry).subs(dict(zip(variables, backward, strict=True)))
                    for entry in column
                )
                components[label] = tuple(
                    _raise_manifold_expression(entry, manifold.atlas()[label])
                    for entry in in_the_chart
                )
            return self.section(components)

        def restrict(self, section, inclusion):
            r"""The section of the pulled-back bundle that ``section`` restricts to.

            A section is a map into the fibres, so its composite with an open
            inclusion is a section of the pulled-back bundle, and on the charts
            of the open submanifold -- which are the ambient charts read there
            (``SmoothManifolds.open_submanifold``) -- its components are the
            section's own (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 8, where vector fields restrict to open submanifolds).  Nothing
            is extended the other way: a section of the restriction need not
            come from one of the manifold.
            """
            manifold = self.base_manifold()
            assert inclusion.codomain() is manifold, (
                f"cannot restrict {section} along {inclusion}: it ends at "
                f"{inclusion.codomain()}, not at {manifold}"
            )
            assert element_parent(section) is self, (
                f"{section} is not a section of {self._vector_bundle}: its parent is "
                f"{element_parent(section)}"
            )
            domain = inclusion.domain()
            target = self._vector_bundle.pullback_along(inclusion).sections()
            components = section.components()
            labels = tuple(
                label for label in components if label in domain.chart_labels()
            )
            assert _chart_family_covers(domain, labels), (
                f"cannot restrict {section} to {domain}: the restriction is stated on the charts "
                f"the section is stated on, {tuple(components)}, and those do not cover {domain} -- "
                f"a chart of the submanifold lies inside none of them, so its points would have no "
                f"component"
            )
            return target.section(
                {
                    label: tuple(
                        _raise_manifold_expression(
                            _engine_manifold_expression(entry), domain.atlas()[label]
                        )
                        for entry in components[label]
                    )
                    for label in labels
                }
            )

        def from_derivation(self, derivation):
            r"""The section ``V`` with ``V f = derivation(f)`` for every smooth function ``f``.

            ``V |-> (f |-> V f)`` is an isomorphism from the sections of ``TM`` onto the
            derivations of ``C^oo(M)`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Prop. 8.15), and its inverse is read on smooth functions ``g_1, ..., g_N`` whose
            differentials span every cotangent space
            (:meth:`SmoothManifolds.ParentMethods._cotangent_spanning_functions`): in a chart
            with coordinates ``x``, ``V(g_k) = sum_i v^i dg_k/dx_i``, so with ``J`` the
            Jacobian ``(dg_k/dx_i)``, of rank ``dim M`` at every point, the components are
            ``v = (J^T J)^{-1} J^T (V(g_1), ..., V(g_N))``.  When one chart presents the
            manifold the family is its coordinates, ``J`` is the identity, and ``v^i`` is
            ``V(x_i)``.
            """
            from sage.matrix.constructor import matrix as _engine_matrix
            from sage.modules.free_module_element import vector as _engine_vector

            manifold = self.base_manifold()
            functions = manifold.smooth_functions()
            spanning = manifold._cotangent_spanning_functions()
            values = tuple(derivation(function) for function in spanning)
            misplaced = tuple(value for value in values if element_parent(value) is not functions)
            assert not misplaced, (
                f"cannot read a section off {derivation}: a derivation of {functions} takes "
                f"its values there, and its values {misplaced} are not elements of it"
            )
            components = {}
            for label in manifold.chart_labels():
                chart = manifold.atlas()[label]
                symbols = tuple(_engine_manifold_chart(chart)[:])
                formulas = tuple(
                    _function_formula_on(function, manifold, label)
                    for function in spanning + values
                )
                assert all(formula is not None for formula in formulas), (
                    f"cannot read a section off {derivation} on the chart {label}: a function "
                    f"it is read on, or one of its values, has no expression there"
                )
                jacobian = _engine_matrix(
                    SR,
                    len(spanning),
                    len(symbols),
                    [
                        formula.diff(symbol)
                        for formula in formulas[: len(spanning)]
                        for symbol in symbols
                    ],
                )
                solved = (jacobian.transpose() * jacobian).inverse() * (
                    jacobian.transpose() * _engine_vector(SR, formulas[len(spanning) :])
                )
                components[label] = tuple(
                    _raise_manifold_expression(SR(entry).simplify_rational(), chart)
                    for entry in solved
                )
            return self.section(components)

        def pullback_of(self, section):
            r"""The section ``q |-> s(f(q))`` of the pullback that ``section`` states.

            A section of the pullback over ``N`` along ``f: N -> M`` is a map into
            the fibres of ``E`` over the image, so a section of ``E`` gives one:
            in a chart ``W`` of ``N`` and the chart ``U`` of ``M`` the map is
            stated in, the pullback's component is the section's component on
            ``U`` composed with the coordinate representation of ``f``, and the
            result is raised to a section of the pulled-back bundle's charts
            (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).
            """
            bundle = self._vector_bundle
            underlying = bundle.underlying_bundle()
            assert underlying is not None, (
                f"the sections of {bundle} are not the sections of a pullback: this bundle is "
                f"read on its own base, and a section there is stated by its components"
            )
            assert element_parent(section) is underlying.sections(), (
                f"{section} is not a section of {underlying}: its parent is "
                f"{element_parent(section)}"
            )
            mapping = bundle.mapping()
            domain = bundle.base_manifold()
            base = underlying.base_manifold()
            stated = section.components()
            index_set = mapping.chart_maps().index_set()
            components = {}
            for label in domain.chart_labels():
                chart = domain.atlas()[label]
                pairs = tuple(pair for pair in index_set if pair[0] == label)
                assert pairs, (
                    f"cannot pull {section} back to {domain}: the map {mapping} is stated in no "
                    f"chart of the target on the chart {label}"
                )
                source_label, target_label = pairs[0]
                assert target_label in stated, (
                    f"cannot read {section} on the chart {target_label} of {base}, which is the "
                    f"chart the map {mapping} carries the chart {label} into"
                )
                expressions = tuple(
                    SR(_engine_manifold_expression(expression))
                    for expression in mapping.chart_map(source_label, target_label)
                )
                symbols = tuple(_engine_manifold_chart(base.atlas()[target_label])[:])
                substitution = dict(zip(symbols, expressions, strict=True))
                components[label] = tuple(
                    _raise_manifold_expression(
                        SR(_engine_manifold_expression(entry)).subs(substitution), chart
                    )
                    for entry in stated[target_label]
                )
            return self.element_class(self, components, self._engine_field(components))

        def module_rank(self):
            r"""The rank of this module as a free ``C^oo(M)``-module.

            A module of sections is free exactly when a global frame is known,
            and a frame is a datum the module retains rather than a fact about
            which charts an engine has coordinates on: without one this refuses,
            because the sections of a nontrivial bundle are not free.
            """
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} has no known rank: it is free "
                f"exactly when a global frame is retained, and no frame is retained here"
            )
            return self._vector_bundle.rank()

        def basis(self):
            r"""The frame that trivializes the bundle, as the basis of this module."""
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} has no known basis: a basis is "
                f"a global frame, and no frame is retained here"
            )
            return tuple(self._retained_frame)

        def trivialized_by(self, frame):
            r"""These sections read through the stated global frame.

            A frame is a family of as many sections as the rank, a basis of
            every fibre (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 10); one section states the rank-one case.  The frame is
            decided to be one: in every chart the determinant of its components
            is decided to take no zero, which is what makes the family a basis
            of each fibre (:func:`_decided_nowhere_vanishing`), and a family
            whose determinant vanishes somewhere, or whose vanishing is not
            decided, is refused.  The result is a module for the same bundle
            that retains the frame and answers its rank and basis; this one is
            unchanged.
            """
            from sage.matrix.constructor import matrix as _engine_matrix

            assert self._retained_frame is None, (
                f"the module of sections of {self._vector_bundle} already retains the frame "
                f"{self._retained_frame}; a second frame states another trivialization, and "
                f"these sections are not re-read through one"
            )
            rank = int(self._vector_bundle.rank())
            family = (
                (frame,) if element_parent(frame) is self else tuple(frame)
            )
            assert len(family) == rank, (
                f"a frame of the rank-{rank} bundle {self._vector_bundle} is a family of "
                f"{rank} sections, and {(len(family))} were given"
            )
            for section in family:
                assert element_parent(section) is self, (
                    f"{section} is not a section of {self._vector_bundle}: its parent is "
                    f"{element_parent(section)}"
                )
            manifold = self.base_manifold()
            stated = tuple(family[0].components())
            coverage = _chart_family_covers(manifold, stated)
            if coverage is not True:
                if coverage is False:
                    assert False, (
                        f"a frame of {self._vector_bundle} is a basis at every point, and the "
                        f"charts {stated} it is stated on do not cover {manifold}: a chart of the "
                        f"atlas lies outside every one of them"
                    )
                raise CoverageUndecided(
                    f"whether the charts {stated} cover {manifold} is undecided, so the frame of "
                    f"{self._vector_bundle} is not decided to be a basis at every point"
                )
            for label in stated:
                chart = manifold.atlas()[label]
                entries = tuple(
                    SR(_engine_manifold_expression(entry))
                    for section in family
                    for entry in section.components()[label]
                )
                determinant = _engine_matrix(SR, rank, rank, entries).det()
                verdict = _decided_nowhere_vanishing(
                    determinant,
                    tuple(_engine_manifold_chart(chart)[:]),
                    tuple(
                        _engine_manifold_expression(condition)
                        for condition in chart.nonvanishing()
                    ),
                )
                assert verdict is True, (
                    f"the family {family} does not trivialize {self._vector_bundle}: its "
                    f"components on the chart {label} have determinant {determinant}, and "
                    + (
                        "that determinant takes the value zero at a point of the chart"
                        if verdict is False
                        else "this owner does not decide that it vanishes nowhere there"
                    )
                )
            return _object_of(
                self.category(),
                vector_bundle=self._vector_bundle,
                base_ring=self.base_ring(),
                retained_frame=family,
            )

        def trivialization(self):
            r"""The isomorphism ``M x R -> E`` that the retained frame states.

            Its forward map sends a smooth function ``a`` to the section
            ``a frame``, and its inverse sends a section to the function that
            reads it in the frame; the two are inverse because the frame is a
            basis of every fibre (Lee, *Introduction to Smooth Manifolds*, 2nd
            ed., Ch. 10).
            """
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} retains no frame, and a "
                f"trivialization of a bundle is read in a frame"
            )
            return SmoothVectorBundleTrivialization(
                self._vector_bundle, self._retained_frame
            )

        def _repr_(self):
            return f"smooth sections of {self._vector_bundle}"


class SmoothVectorBundleTrivialization(SageObject):
    r"""The trivialization ``M x R^r -> E`` that a global frame states.

    A frame is a family ``E_1, ..., E_r`` of sections that is a basis of every
    fibre, and it states the isomorphism in two directions: a family of smooth
    functions ``(a_1, ..., a_r)`` determines the section ``sum_i a_i E_i``, and a
    section ``V`` determines the family with ``V = sum_i a_i E_i`` (Lee,
    *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  In a chart the second
    is the linear system ``V_j = sum_i a_i (E_i)_j``, and its solution is
    Cramer's rule: ``a_i`` is the determinant of the components' matrix with the
    ``i``-th column replaced by the section's components, divided by the
    determinant of the matrix itself.  That denominator is the determinant the
    frame's being a basis decided to vanish nowhere on the chart, so each
    coordinate is a quotient of sections read where its denominator does not
    vanish (:meth:`ManifoldAtlasChart.section_ratio`).
    """

    def __init__(self, bundle, frame) -> None:
        self._bundle = bundle
        self._frame = tuple(frame)

    def bundle(self):
        r"""The bundle this trivialization is of."""
        return self._bundle

    def base_manifold(self):
        r"""The manifold the trivialized bundle is over."""
        return self._bundle.base_manifold()

    def frame(self):
        r"""The global frame the trivialization is read in, as the family of its sections."""
        return self._frame

    def forward(self, functions):
        r"""``(a_1, ..., a_r) |-> sum_i a_i E_i``: the section a family of functions states.

        The product of a function and a section is the pointwise product of
        their components in a chart, and the sum of the basis sections is taken
        there, which is how the ``C^oo(M)``-module structure on sections is
        written (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  One
        function states the rank-one case.
        """
        manifold = self.base_manifold()
        rank = int(self._bundle.rank())
        family = (functions,) if rank == 1 else tuple(functions)
        assert len(family) == rank, (
            f"a section of the rank-{rank} bundle {self._bundle} is written as {rank} "
            f"functions, one per basis section, and {len(family)} were given"
        )
        formulas = []
        for function in family:
            assert element_parent(function) is manifold.smooth_functions(), (
                f"{function} is not a smooth function on {manifold}: its parent is "
                f"{element_parent(function)}, and a trivialization is a map from as many "
                f"copies of {manifold.smooth_functions()} as the rank"
            )
            on_the_frame = tuple(
                _function_formula_on(function, manifold, label)
                for label in self._frame[0].components()
            )
            assert all(formula is not None for formula in on_the_frame), (
                f"cannot multiply the frame of {self._bundle} by {function}: its expressions "
                f"are on {tuple(_chartwise_formulas(function, manifold) or ())} and the frame's "
                f"on {tuple(self._frame[0].components())}, and no coordinate change the atlas "
                f"states carries one to the other"
            )
            formulas.append(
                dict(zip(tuple(self._frame[0].components()), on_the_frame, strict=True))
            )
        components = tuple(section.components() for section in self._frame)
        return self._bundle.sections().section(
            {
                label: tuple(
                    _raise_manifold_expression(
                        sum(
                            SR(formulas[index][label])
                            * _engine_manifold_expression(components[index][label][entry])
                            for index in range(rank)
                        ),
                        manifold.atlas()[label],
                    )
                    for entry in range(rank)
                )
                for label in self._frame[0].components()
            }
        )

    def inverse(self, section):
        r"""``V |-> (a_1, ..., a_r)``: the functions with ``V = sum_i a_i E_i``.

        In a chart the components of ``V`` are ``V_j`` and those of the frame are
        ``(E_i)_j``, and the functions are the solution of
        ``V_j = sum_i a_i (E_i)_j``: by Cramer's rule, ``a_i`` is the
        determinant of the components' matrix with its ``i``-th column replaced
        by ``V``, divided by the determinant of the matrix.  The division is
        stated with :meth:`ManifoldAtlasChart.section_ratio`, which is read where
        its denominator does not vanish -- the whole chart, by the frame's being
        a basis.  The system is solved on the charts the frame is stated on, and
        the section's components there are transported from the charts it is
        stated on (:func:`_section_components_on`).  One function is returned at
        rank one.
        """
        from sage.matrix.constructor import matrix as _engine_matrix

        manifold = self.base_manifold()
        assert element_parent(section) is self._bundle.sections(), (
            f"{section} is not a section of {self._bundle}: its parent is "
            f"{element_parent(section)}"
        )
        rank = int(self._bundle.rank())
        components = tuple(entry.components() for entry in self._frame)
        labels = tuple(components[0])
        section_components = {
            label: _section_components_on(section, label) for label in labels
        }
        coordinates = []
        for index in range(rank):
            per_chart = {}
            for label in labels:
                chart = manifold.atlas()[label]
                entries = tuple(
                    SR(_engine_manifold_expression(components[basis][label][entry]))
                    for entry in range(rank)
                    for basis in range(rank)
                )
                stated = tuple(
                    SR(_engine_manifold_expression(entry))
                    for entry in section_components[label]
                )
                replaced = _engine_matrix(
                    SR,
                    rank,
                    rank,
                    tuple(
                        stated[entry] if basis == index else entries[entry * rank + basis]
                        for entry in range(rank)
                        for basis in range(rank)
                    ),
                )
                per_chart[label] = chart.section_ratio(
                    _raise_manifold_expression(replaced.det(), chart),
                    _raise_manifold_expression(
                        _engine_matrix(SR, rank, rank, entries).det(), chart
                    ),
                )
            coordinates.append(manifold.smooth_function(per_chart))
        return coordinates[0] if rank == 1 else tuple(coordinates)

    def _repr_(self):
        return f"the trivialization of {self._bundle} by the frame {self._frame}"
