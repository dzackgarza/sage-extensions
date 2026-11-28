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
    _local_chart_expressions,
    _rational_guard_product,
    _raise_manifold_expression,
    _sum_certificate_covers,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.logic import ask
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
    Each coefficient is supplied with its chart: a coordinate expression is
    a function on that chart's domain, not a scalar constant on every chart.
    """
    engine = _engine_manifold(manifold)
    field = engine.vector_field(name=f"a section of T{manifold.manifold_name()}")
    for label, component in components.items():
        chart = _engine_manifold_chart(manifold.atlas()[label])
        field.restrict(chart.domain())[chart.frame(), :] = [
            chart.domain().scalar_field({chart: _engine_manifold_expression(entry)})
            for entry in component
        ]
    return field


def _tangent_section_jets(section, chart, point, order):
    """Read a tangent section in an actual local coordinate frame."""
    return _section_jets(section, chart, point, order, chart)


def _mapping_germ(mapping, chart, point, order):
    """The smooth map's germ in a target chart that actually contains its image."""
    from sage_extensions.categories.functions.smooth_germs import (
        _coordinate_change_jets, _coordinates_in_chart, _function_jet,
    )

    native = _engine_manifold_chart(chart)
    composition = getattr(mapping, "_defining_composition", None)
    if composition is not None:
        outer, inner = composition
        middle, image, arguments = _mapping_germ(inner, chart, point, order)
        target, result, expressions = _mapping_germ(outer, middle, image, order)
        return target, result, tuple(entry.compose(arguments) for entry in expressions)
    for key in mapping._local_keys(point):
        local, target, entries = mapping.local_representation(key)
        local_native = _engine_manifold_chart(local)
        if not (local_native is native and _engine_manifold_chart(point.chart()) is native):
            if _coordinate_change_jets(native, _coordinates_in_chart(chart, point),
                    local_native, chart.manifold().coordinate_field(), 0) is None:
                continue
        arguments = tuple(_function_jet(entry, chart, point, order) for entry in entries)
        image = mapping.codomain().point(tuple(argument.value() for argument in arguments), target.label())
        return target, image, arguments
    raise CoverageUndecided("no actual local representation of the map contains the point")


def _bundle_image_germ(bundle, chart, point, order):
    """The germ of the composite map to the original tangent bundle's base."""
    from sage_extensions.categories.functions.smooth_germs import _coordinate_jets

    if bundle.is_pullback():
        target, image, arguments = _mapping_germ(bundle.mapping(), chart, point, order)
        original, final, expressions = _bundle_image_germ(bundle.underlying_bundle(), target, image, order)
        return original, final, tuple(entry.compose(arguments) for entry in expressions)
    return chart, point, _coordinate_jets(chart, point, order)


def _section_jets(section, chart, point, order, frame=None):
    """Section coefficient germs in one fibre frame, over the actual local base.

    For a pullback the fibre transition is the target coordinate Jacobian
    evaluated along the composite map to the original tangent bundle base.
    It is not the differential of the pullback map.
    """
    from sage_extensions.categories.functions.smooth_germs import (
        _coordinate_change_jets, _coordinates_in_chart, _function_jet,
    )

    bundle = section.parent().vector_bundle()
    root, image, image_jets = _bundle_image_germ(bundle, chart, point, order)
    if frame is None:
        frame = root
    if section._jet_evaluation is not None:
        return section._jet_evaluation(chart, point, order, frame)
    native = _engine_manifold_chart(chart)
    image_native = _engine_manifold_chart(root)
    target = _engine_manifold_chart(frame)
    field = chart.manifold().coordinate_field()
    for local_chart, original_chart, component in section._local_component_pieces(point):
        local = _engine_manifold_chart(local_chart)
        if not (local is native and _engine_manifold_chart(point.chart()) is native):
            if _coordinate_change_jets(native, _coordinates_in_chart(chart, point),
                    local, field, 0) is None:
                continue
        original = _engine_manifold_chart(original_chart)
        coeffs = tuple(_function_jet(entry, chart, point, order) for entry in component)
        if original is target:
            return coeffs
        image_values = _coordinates_in_chart(root, image)
        forward = _coordinate_change_jets(image_native, image_values, original, field, order)
        if forward is None:
            continue
        backward = _coordinate_change_jets(original, tuple(jet.value() for jet in forward),
                                           target, field, order + 1)
        if backward is None:
            continue
        original_jets = tuple(entry.compose(image_jets) for entry in forward)
        rows = tuple(tuple(entry.partial(i).compose(original_jets)
                           for i in range(len(forward))) for entry in backward)
        return tuple(
            sum((factor * entry for factor, entry in zip(row, coeffs, strict=True)),
                row[0].scale(field.zero()))
            for row in rows
        )
    raise CoverageUndecided("no actual section domain and fibre-frame transition contains the point")


def _jet_determinant(columns):
    """Determinant over the commutative finite-order germ algebra."""
    if len(columns) == 1:
        return columns[0][0]
    field = columns[0][0].field
    result = columns[0][0].scale(field.zero())
    for i, column in enumerate(columns):
        minor = tuple(other[1:] for j, other in enumerate(columns) if j != i)
        result = result + (column[0] * _jet_determinant(minor)).scale(field((-1)**i))
    return result


def _symbolic_section_pieces(section, chart, root, image, map_guards):
    """Coefficient formulas on actual common source domains and one fibre frame."""
    manifold = section.parent().base_manifold()
    symbols = tuple(_engine_manifold_chart(chart)[:])
    root_symbols = tuple(_engine_manifold_chart(root)[:])
    root_substitution = dict(zip(root_symbols, image, strict=True))
    for key, coefficients in section.components().items():
        source = section.component_chart(key)
        paths = {(): None} if source.label() == chart.label() else dict(
            manifold.coordinate_changes(chart.label(), source.label()).items())
        for change in paths.values():
            source_symbols = tuple(_engine_manifold_chart(source)[:])
            in_source = symbols if change is None else tuple(
                SR(_engine_manifold_expression(c)) for c in change.forward_expressions())
            substitute = dict(zip(source_symbols, in_source, strict=True))
            where = tuple(map_guards) + (() if change is None else tuple(
                SR(_engine_manifold_expression(c)) for c in change.source_overlap()))
            where += tuple(SR(_engine_manifold_expression(c)).subs(substitute)
                           for c in section.component_nonvanishing(key))
            if any(guard == 0 for guard in where):
                continue
            entries = tuple(SR(_engine_manifold_expression(c)).subs(substitute)
                            for c in coefficients)
            original = section.component_frame(key)
            if original is root:
                yield entries, where
                continue
            for frame_change in root.manifold().coordinate_changes(root.label(), original.label()).values():
                overlap = tuple(SR(_engine_manifold_expression(c)).subs(root_substitution)
                                for c in frame_change.source_overlap())
                if any(c == 0 for c in overlap):
                    continue
                variables = tuple(_engine_manifold_chart(original)[:])
                in_original = tuple(SR(_engine_manifold_expression(c)).subs(root_substitution)
                                    for c in frame_change.forward_expressions())
                back = dict(zip(variables, in_original, strict=True))
                converted = tuple(sum(SR(_engine_manifold_expression(formula)).diff(var).subs(back) * value
                                      for var, value in zip(variables, entries, strict=True))
                                  for formula in frame_change.inverse_expressions())
                yield converted, where + overlap


def _certify_frame_on_common_refinement(family):
    """Prove the pointwise basis property on a certified common refinement.

    All columns are first expressed in one fibre frame over an actual common
    intersection. A nonzero determinant certificate on those intersections
    and a covering certificate suffice; no point sampling is used.
    """
    from itertools import product
    from sage.matrix.constructor import matrix as _engine_matrix

    module = family[0].parent()
    manifold = module.base_manifold()
    bundle = module.vector_bundle()
    composite = None
    while bundle.is_pullback():
        mapping = bundle.mapping()
        composite = mapping if composite is None else mapping * composite
        bundle = bundle.underlying_bundle()
    witnesses = {}
    for label in manifold.chart_labels():
        chart = manifold.atlas()[label]
        symbols = tuple(_engine_manifold_chart(chart)[:])
        if composite is None:
            images = ((chart, symbols, ()),)
        else:
            images = tuple((composite.codomain().atlas()[target], expressions, where)
                           for target, expressions, where in composite._representations_written_on(label).values())
        for root, image, where in images:
            local = tuple(tuple(_symbolic_section_pieces(section, chart, root, image, where))
                          for section in family)
            for combination in product(*local):
                columns = tuple(entries for entries, _ in combination)
                guards = tuple(c for _, conditions in combination for c in conditions)
                determinant = _engine_matrix(SR, list(zip(*columns, strict=True))).det()
                excluded = tuple(_engine_manifold_expression(c) for c in chart.nonvanishing()) + guards
                if _decided_nowhere_vanishing(determinant, symbols, excluded) is True:
                    witnesses[len(witnesses)] = (
                        label, tuple(_raise_manifold_expression(guard, chart) for guard in guards)
                    )
    return _chart_family_covers(manifold, tuple(witnesses), local_domains=witnesses) is True


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
    formulas = _chartwise_formulas(function, manifold)
    if formulas is None:
        return None
    if label in formulas:
        return SR(formulas[label])
    symbols = tuple(_engine_manifold_chart(manifold.atlas()[label])[:])
    for other, formula in formulas.items():
        requested = _engine_manifold_chart(manifold.atlas()[label])
        given = _engine_manifold_chart(manifold.atlas()[other])
        if (not requested.domain().is_subset(given.domain())
            and _sum_certificate_covers(manifold, (other,), manifold.atlas()[label]) is not True):
            continue
        if given in requested._supercharts:
            return SR(formula).subs(dict(zip(tuple(given[:]), symbols, strict=True)))
        if (label, other) not in manifold.transitions().keys():
            continue
        change = manifold.transition(label, other)
        other_symbols = tuple(_engine_manifold_chart(manifold.atlas()[other])[:])
        pulled = SR(formula).subs(
            dict(
                zip(
                    other_symbols,
                    tuple(
                        SR(_engine_manifold_expression(expression))
                        for expression in change.forward_expressions()
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
        guards = section.component_nonvanishing(label)
        if guards:
            local = {label: (section.component_chart(label).label(), guards)}
            if _sum_certificate_covers(manifold, (label,), manifold.atlas()[label], local_domains=local) is not True:
                raise CoverageUndecided("this local component does not certify a description on the whole requested chart")
            return tuple(_raise_manifold_expression(_engine_manifold_expression(entry), manifold.atlas()[label])
                for entry in stated[label])
        return stated[label]
    bundle = module.vector_bundle()
    rank = int(bundle.rank())
    chart = manifold.atlas()[label]
    target_symbols = tuple(_engine_manifold_chart(chart)[:])
    underlying = bundle.underlying_bundle()
    for source_label, component in stated.items():
        if source_label not in manifold.chart_labels() or section.component_nonvanishing(source_label):
            raise CoverageUndecided("transport of this local component requires its actual domain and fibre frame")
        change = _composed_ambient_transition(manifold, source_label, label)
        if change is None:
            continue
        source_chart = manifold.atlas()[source_label]
        requested = _engine_manifold_chart(chart)
        given = _engine_manifold_chart(source_chart)
        if (not requested.domain().is_subset(given.domain())
            and _sum_certificate_covers(manifold, (source_label,), chart) is not True):
            continue
        if (source_label, label) not in manifold.transitions().keys():
            continue
        change = manifold.transition(source_label, label)
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


def _quadratic_signs(matrix):
    r"""Decide whether the rational symmetric form takes positive/negative values.

    A nonzero diagonal pivot d splits the form by congruence as
    d z^2 + y^T (B - vv^T/d)y, where v is its off-diagonal column
    and B the remaining principal matrix. The change of variables is
    invertible. If all diagonal entries vanish but an off-diagonal entry
    A_ij is nonzero, e_i+e_j and e_i-e_j give opposite signs.
    Thus exact elimination decides both signs, including singular forms.
    """
    positive = negative = False
    while matrix.nrows():
        n = matrix.nrows()
        pivot = next((i for i in range(n) if matrix[i, i] != 0), None)
        if pivot is None:
            return (True, True) if not matrix.is_zero() else (positive, negative)
        diagonal = matrix[pivot, pivot]
        positive = positive or diagonal > 0
        negative = negative or diagonal < 0
        if positive and negative:
            return True, True
        rest = [i for i in range(n) if i != pivot]
        if not rest:
            break
        column = matrix[rest, [pivot]]
        matrix = matrix[rest, rest] - column * column.transpose() / diagonal
    return positive, negative


def _quadratic_minimum(matrix, vector, constant):
    r"""The attained minimum of a positive semidefinite quadratic, or None.

    If b/2 is outside the range of A, symmetry gives a vector in ker A
    with nonzero pairing with b. Along that line the polynomial takes
    every real value. Otherwise solve Au=b/2. Completing the square gives
    (x+u)^T A (x+u) + c - u^T A u and the minimum occurs at -u.
    """
    coefficient_ring = matrix.base_ring()
    target = vector / coefficient_ring(2)
    if matrix.augment(target.column()).rank() != matrix.rank():
        return None
    if target.is_zero():
        return constant
    solution = matrix.solve_right(target)
    assert matrix * solution == target
    return constant - solution.dot_product(matrix * solution)


def _decided_quadratic(polynomial):
    r"""Decide real zero existence for every rational polynomial of degree <=2.

    An indefinite quadratic part takes both signs for sufficiently large
    multiples of suitable vectors, so the polynomial has a zero by
    continuity. Multiply a negative semidefinite form by -1. A nonzero
    positive semidefinite form is unbounded above, and has a zero precisely
    when its attained minimum is nonpositive or its linear term has a
    nonzero component along the kernel. A linear or constant polynomial is
    decided directly. Higher degrees require another certificate.
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
    positive, negative = _quadratic_signs(matrix)
    if positive and negative:
        return False
    if not positive and not negative:
        return vector.is_zero() and constant != 0
    if negative:
        matrix, vector, constant = -matrix, -vector, -constant
    minimum = _quadratic_minimum(matrix, vector, constant)
    return minimum is not None and minimum > 0


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
            The pullback retains this bundle and the chosen map, including for
            an identity or open inclusion.  For an open inclusion the
            differential identifies its tangent pullback with the domain's
            tangent bundle; that isomorphism does not discard the defining map
            of this pullback (Tu, Theorem 20.6).
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

        def __init__(self, parent, components, engine_field, *, charts=None, domains=None, frames=None, local_charts=None, evaluation=None, jet_evaluation=None, local_cover=None, locate=None) -> None:
            Element.__init__(self, parent)
            self._components = components
            self._engine_field = engine_field
            self._section_evaluation = evaluation
            self._jet_evaluation = jet_evaluation
            self._local_cover = local_cover
            self._locate_component = locate
            manifold = parent.base_manifold()
            self._component_charts = (
                {key: manifold.atlas()[key] for key in components}
                if charts is None else charts
            )
            self._component_domains = (
                {key: () for key in components} if domains is None else domains
            )
            self._component_local_charts = (
                self._component_charts if local_charts is None else local_charts
            )
            if frames is None:
                bundle = parent.vector_bundle()
                if bundle.is_pullback():
                    mapping = bundle.mapping()
                    frames = {}
                    for key, chart in self._component_charts.items():
                        pairs = tuple(p for p in mapping.chart_maps().keys() if p[0] == chart.label())
                        assert len(pairs) == 1, "local pullback components require their stated fibre frame"
                        frames[key] = mapping.codomain().atlas()[pairs[0][1]]
                else:
                    frames = self._component_charts
            self._component_frames = frames

        def _local_component_pieces(self, point):
            if self._local_cover is not None:
                yield self._local_cover[self._locate_component(point)]
                return
            for key, component in self._components.items():
                yield self._component_local_charts[key], self._component_frames[key], component

        def local_cover(self):
            """The retained independently indexed cover, when supplied."""
            return self._local_cover

        def components(self):
            r"""Local component tuples, with domains and frames given by their accessors.

            Each coefficient belongs to the function ring of its actual local
            domain.  A local index need not be an atlas label: distinct pieces
            in the same source chart can have different domains and frames.
            For a derived section these are computed local descriptions; its
            retained defining evaluation, not this dictionary, defines the
            global section when the available transitions leave descriptions
            uncomputed.
            """
            return dict(self._components)

        def component_chart(self, index):
            r"""The source coordinates in which this local component is written."""
            return self._component_charts[index]

        def component_domain(self, index):
            r"""The actual open submanifold on which this component is defined."""
            return self._component_local_charts[index].domain()

        def component_nonvanishing(self, index):
            r"""Ordered nonvanishing conditions in the source chart for this local domain."""
            return self._component_domains[index]

        def component_frame(self, index):
            r"""The bundle's coordinate frame used by this local component."""
            return self._component_frames[index]

        def components_at(self, point, frame_label=None):
            r"""Fibre coordinates at a point, in the requested coordinate frame.

            Select an actual local domain before evaluating a coefficient.
            Fibre transitions are evaluated at the image point, with no
            differential of the pullback map (Tu, Proposition 20.7).
            """
            manifold = self.parent().base_manifold()
            point = manifold(point)
            if (self._jet_evaluation is not None or self._local_cover is not None
                    or getattr(_engine_manifold_chart(point.chart()).domain().manifold(),
                               "_owned_coordinate_data", False)):
                bundle = self.parent().vector_bundle()
                root, _image, _jets = _bundle_image_germ(bundle, point.chart(), point, 0)
                frame = root if frame_label is None else root.manifold().atlas()[frame_label]
                return finite_family(tuple(jet.value() for jet in
                    _section_jets(self, point.chart(), point, 0, frame)),
                    name="Fibre coordinates of a smooth section")
            if self._section_evaluation is not None:
                return self._section_evaluation(point, frame_label)
            bundle = self.parent().vector_bundle()
            image = point
            while bundle.is_pullback():
                image = bundle.mapping()(image)
                bundle = bundle.underlying_bundle()
            target_label = image.chart().label() if frame_label is None else frame_label
            source_label = point.chart().label()
            field = manifold.coordinate_field()
            for key, component in self._components.items():
                source = self._component_charts[key]
                changes = (None,) if source.label() == source_label else tuple(
                    manifold.coordinate_changes(source_label, source.label()).values()
                )
                for change in changes:
                    if change is None:
                        local_point = point
                    else:
                        if not all(ask(c(point) != field.zero()) is True for c in change.source_overlap()):
                            continue
                        local_point = manifold.point(tuple(c(point) for c in change.forward_expressions()), source.label())
                    if not all(ask(c(local_point) != field.zero()) is True for c in self._component_domains[key]):
                        continue
                    values = tuple(entry(local_point) for entry in component)
                    frame = self._component_frames[key]
                    if frame.label() == target_label:
                        return finite_family(values, name="Fibre coordinates of a smooth section")
                    frame_points = []
                    if bundle is self.parent().vector_bundle() and frame is source:
                        frame_points.append(local_point)
                    elif image.chart().label() == frame.label():
                        frame_points.append(image)
                    else:
                        for image_change in frame.manifold().coordinate_changes(image.chart().label(), frame.label()).values():
                            if all(ask(c(image) != field.zero()) is True for c in image_change.source_overlap()):
                                frame_points.append(frame.manifold().point(
                                    tuple(c(image) for c in image_change.forward_expressions()), frame.label()))
                    for frame_change in frame.manifold().coordinate_changes(frame.label(), target_label).values():
                        for frame_point in frame_points:
                            if not all(ask(c(frame_point) != field.zero()) is True for c in frame_change.source_overlap()):
                                continue
                            variables = tuple(_engine_manifold_chart(frame)[:])
                            substitution = dict(zip(variables,
                                tuple(_engine_manifold_expression(c) for c in frame_point.coordinates()), strict=True))
                            entries = tuple(
                                sum((
                                    field(SR(_engine_manifold_expression(formula)).diff(variable).subs(substitution)) * value
                                    for variable, value in zip(variables, values, strict=True)
                                ), field.zero())
                                for formula in frame_change.forward_expressions()
                            )
                            return finite_family(entries, name="Fibre coordinates of a smooth section")
            raise CoverageUndecided(f"no represented section domain and frame transition contains {point}")

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
            local_labels = tuple(label for label in self.components()
                                 if label in (formulas or {})
                                 and not self.component_nonvanishing(label))
            if (formulas is None or self._engine_field is None
                or _chart_family_covers(manifold, local_labels) is not True):
                from sage_extensions.categories.functions.smooth_germs import (
                    _SmoothGermFunction, _function_jet, _TaylorJet,
                )

                def provider(chart, point, order):
                    components = _tangent_section_jets(self, chart, point, order)
                    field = chart.manifold().coordinate_field()
                    zero = _TaylorJet.constant(field, int(manifold.dimension()), order, field.zero())



                    from sage_extensions.logic import ask
                    if all(ask(c == field.zero()) is True for component in components
                           for c in component.coefficients.values()):
                        return zero
                    jet = _function_jet(function, chart, point, order + 1)
                    return sum((component * jet.partial(i)
                                for i, component in enumerate(components)), zero)

                return manifold.smooth_functions()(_SmoothGermFunction(manifold, provider))
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
                    for label in local_labels
                }
            )

        def _add_(self, other):
            r"""``V + W``: the section whose value at ``p`` is ``V(p) + W(p)``."""
            components = self.components()
            other_components = other.components()
            if self.parent().vector_bundle().is_pullback():
                def germs(chart, point, order, frame):
                    return tuple(left + right for left, right in zip(
                        _section_jets(self, chart, point, order, frame),
                        _section_jets(other, chart, point, order, frame), strict=True))

                def evaluation(point, frame):
                    return finite_family(tuple(left + right for left, right in zip(
                        self.components_at(point, frame), other.components_at(point, frame), strict=True
                    )), name="Fibre coordinates of the sum of sections")

                pairs = tuple((left, right) for left in components for right in other_components
                    if self.component_chart(left) is other.component_chart(right)
                    and self.component_frame(left) is other.component_frame(right))
                try:
                    formulas = {
                    (a, b): tuple(SR(_engine_manifold_expression(left)) + SR(_engine_manifold_expression(right))
                        for left, right in zip(components[a], other_components[b], strict=True))
                    for a, b in pairs
                    }
                except (AssertionError, TypeError, ValueError, NotImplementedError):
                    return self.parent().element_class(self.parent(), {}, None, jet_evaluation=germs)
                return self.parent()._construct(formulas, charts={(a, b): self.component_chart(a) for a, b in pairs},
                    domains={(a, b): tuple(SR(_engine_manifold_expression(c)) for c in
                        self.component_nonvanishing(a) + other.component_nonvanishing(b)) for a, b in pairs},
                    frames={(a, b): self.component_frame(a) for a, b in pairs}, evaluation=evaluation,
                    jet_evaluation=germs)
            if self._engine_field is None or other._engine_field is None or components.keys() != other_components.keys() or any(
                self.component_nonvanishing(key) or other.component_nonvanishing(key)
                for key in components
            ):
                return self.parent()._from_tangent_jets(
                    lambda chart, point, order: tuple(
                        a + b for a, b in zip(
                            _tangent_section_jets(self, chart, point, order),
                            _tangent_section_jets(other, chart, point, order), strict=True)))
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
            if self.parent().vector_bundle().is_pullback():
                def germs(chart, point, order, frame):
                    return tuple(-entry for entry in _section_jets(self, chart, point, order, frame))
                try:
                    formulas = {key: tuple(-SR(_engine_manifold_expression(entry)) for entry in component)
                                for key, component in self.components().items()}
                except (AssertionError, TypeError, ValueError, NotImplementedError):
                    return self.parent().element_class(self.parent(), {}, None, jet_evaluation=germs)
                return self.parent()._construct(formulas, charts=self._component_charts,
                    domains={key: tuple(SR(_engine_manifold_expression(c)) for c in where)
                        for key, where in self._component_domains.items()}, frames=self._component_frames,
                    evaluation=lambda point, frame: finite_family(tuple(-entry for entry in self.components_at(point, frame)), name="Fibre coordinates of the negative section"),
                    jet_evaluation=germs)
            if self._engine_field is None:
                return self.parent()._from_tangent_jets(
                    lambda chart, point, order: tuple(-entry for entry in
                        _tangent_section_jets(self, chart, point, order)))
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
            r"""Certify equality by matching fibre coordinates on an actual cover.

            A local equality is a witness only on the intersection of its two
            domains, in one source chart and one fibre frame.  Agreement on a
            proper open subset does not determine a general smooth section.
            A nonzero rational residual proves inequality only after proving
            its actual common domain nonempty.  Unsupported comparisons are
            undecided, rather than identities by analytic continuation.
            """
            from sage.rings.infinity import Infinity
            from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

            if self is other:
                return True
            if element_parent(other) is not self.parent():
                return False
            witnesses = {}
            for left_key, component in self._components.items():
                for right_key, other_component in other.components().items():
                    if (self.component_chart(left_key) is not other.component_chart(right_key)
                        or self.component_frame(left_key) is not other.component_frame(right_key)):
                        continue
                    chart = self.component_chart(left_key)
                    conditions = self.component_nonvanishing(left_key) + other.component_nonvanishing(right_key)
                    residuals = tuple(SR(_engine_manifold_expression(left) - _engine_manifold_expression(right)).simplify_full()
                        for left, right in zip(component, other_component, strict=True))
                    if all(residual == 0 for residual in residuals):
                        witnesses[left_key, right_key] = (
                            chart.label(), conditions,
                        )
                        continue
                    engine_chart = _engine_manifold_chart(chart)
                    if (chart.nonvanishing() or engine_chart._restrictions
                        or any(low[0] != -Infinity or high[0] != Infinity
                               for low, high in engine_chart.coord_bounds())):
                        continue
                    symbols = tuple(engine_chart[:])
                    ring = PolynomialRing(QQ, names=tuple(str(s) for s in symbols)) if symbols else QQ
                    for residual in residuals:
                        product = _rational_guard_product((residual,) + tuple(
                            _engine_manifold_expression(c) for c in conditions), ring)



                        if product is not None and product != 0:
                            return False
            if _chart_family_covers(self.parent().base_manifold(), tuple(witnesses), local_domains=witnesses) is True:
                return True
            raise CoverageUndecided("the proved local coefficient equalities do not certify a cover of the base")

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

        def _construct(self, components, *, charts=None, domains=None, frames=None, evaluation=None, engine_field=None, jet_evaluation=None):
            r"""The section with these components, built without re-deciding that they state one object.

            The callers are this module's own operations -- the sum, the negative,
            the scalar multiple -- and the pullback of a section, which produce
            components that agree on the overlaps because their operands do;
            :meth:`section` is where a caller's own components are decided.
            """
            if charts is None:
                if engine_field is None:
                    engine_field = self._engine_field(components)
                return self.element_class(self, components, engine_field, evaluation=evaluation,
                                          jet_evaluation=jet_evaluation)
            source_labels = tuple(chart.label() for chart in charts.values())
            names = {key: (chart.label() if source_labels.count(chart.label()) == 1
                and (chart.label() not in components or chart.label() == key) else key)
                for key, chart in charts.items()}
            admitted, admitted_domains, local_charts = {}, {}, {}
            for key, values in components.items():
                index = names[key]
                admitted[index], admitted_domains[index], local_charts[index] = _local_chart_expressions(
                    charts[key], values, domains[key]
                )
            return self.element_class(
                self, admitted, engine_field, charts={names[key]: chart for key, chart in charts.items()},
                domains=admitted_domains, frames={names[key]: frame for key, frame in frames.items()},
                local_charts=local_charts, evaluation=evaluation, jet_evaluation=jet_evaluation,
            )

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
                try:
                    return _engine_vector_field(self.base_manifold(), components)
                except (AssertionError, TypeError, ValueError, NotImplementedError):


                    return None
            return None

        def _from_tangent_jets(self, provider):
            """The tangent section specified by compatible local coefficient germs."""
            from sage_extensions.categories.functions.smooth_germs import (
                _SmoothGermFunction, _coordinate_change_jets, _coordinates_in_chart,
            )

            manifold = self.base_manifold()
            components = {}
            for label in manifold.selected_finite_chart_labels():
                home = manifold.atlas()[label]
                components[label] = tuple(home.function_ring()(_SmoothGermFunction(
                    home.domain(), lambda chart, point, order, i=i: provider(chart, point, order)[i],
                    charts=(home,)))
                    for i in range(int(self.vector_bundle().rank())))

            def germs(chart, point, order, frame):
                native, target = _engine_manifold_chart(chart), _engine_manifold_chart(frame)
                if native is target:
                    return provider(chart, point, order)
                values = _coordinates_in_chart(chart, point)
                field = manifold.coordinate_field()
                args = _coordinate_change_jets(native, values, target, field, order)
                if args is None:
                    raise CoverageUndecided("the requested tangent frame does not contain the point")
                local_point = frame.domain().point(tuple(jet.value() for jet in args), frame.label())
                return tuple(entry.compose(args) for entry in provider(frame, local_point, order))

            return self.element_class(self, components, None, jet_evaluation=germs)

        def zero(self):
            r"""The zero section: the component zero in every chart's coordinate frame."""
            if self._vector_bundle.is_pullback():
                return self.pullback_of(self._vector_bundle.underlying_bundle().sections().zero())
            manifold = self.base_manifold()
            if manifold._preamble_chart_index_set is not None:
                from sage_extensions.categories.functions.smooth_germs import _TaylorJet
                field = manifold.coordinate_field()
                return self._from_tangent_jets(lambda chart, point, order:
                    tuple(_TaylorJet.constant(field, int(manifold.dimension()), order, field.zero())
                          for _ in range(int(self.vector_bundle().rank()))))
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
            components = element.components()
            if self._vector_bundle.is_pullback():
                from sage_extensions.categories.functions.smooth_germs import _function_jet

                def germs(chart, point, order, frame):
                    factor = _function_jet(scalar, chart, point, order)
                    return tuple(factor * entry for entry in _section_jets(element, chart, point, order, frame))
                formulas = {} if formulas is None else formulas
                described = tuple(key for key in components if element.component_chart(key).label() in formulas)
                try:
                    products = {
                    key: tuple(formulas[element.component_chart(key).label()] * _engine_manifold_expression(entry)
                        for entry in component)
                    for key, component in components.items() if key in described
                    }
                except (AssertionError, TypeError, ValueError, NotImplementedError):
                    return self.element_class(self, {}, None, jet_evaluation=germs)
                return self._construct(products, charts={key: element.component_chart(key) for key in described},
                    domains={key: tuple(SR(_engine_manifold_expression(c)) for c in element.component_nonvanishing(key))
                        for key in described},
                    frames={key: element.component_frame(key) for key in described},
                    evaluation=lambda point, frame: finite_family(tuple(scalar(point) * entry for entry in element.components_at(point, frame)), name="Fibre coordinates of a scaled section"),
                    jet_evaluation=germs)
            if (formulas is None or any(label not in formulas for label in components)
                or element._engine_field is None or any(element.component_nonvanishing(key)
                    for key in components)):
                from sage_extensions.categories.functions.smooth_germs import _function_jet

                def provider(chart, point, order):
                    function = _function_jet(scalar, chart, point, order)
                    return tuple(function * component for component in
                                 _tangent_section_jets(element, chart, point, order))
                return self._from_tangent_jets(provider)
            return self._construct(
                {
                    label: tuple(
                        _raise_manifold_expression(
                            formulas[label] * _engine_manifold_expression(entry),
                            manifold.atlas()[label],
                        )
                        for entry in components[label]
                    )
                    for label in components
                }
            )

        def section(self, components, *, check=True, local_charts=None, fibre_frames=None, domains=None, locate=None):
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

            The check=False construction uses the caller's hypotheses that
            these smooth local coefficients cover and satisfy the stated
            transition law (OWN-22). For an independently indexed local cover,
            local_charts specifies the owned restricted source charts and
            fibre_frames specifies the original tangent bundle coordinate
            frames containing the images of those domains. Domains, if given,
            records the nonvanishing conditions in the source atlas coordinates.
            These data describe a section of a pullback without requiring it
            to be a pullback of any global vector field. A cover, image
            containment, and transition compatibility are hypotheses, not
            numerical tests on the local coefficients.
            """
            manifold = self.base_manifold()
            atlas = manifold.atlas()
            if locate is not None:
                from sage_extensions.categories.sets.set_categories import indexed_family
                assert not check and local_charts is not None and domains is None
                indices = components.index_set()
                assert local_charts.index_set() is indices
                bundle = self._vector_bundle
                root = bundle
                while root.is_pullback():
                    root = root.underlying_bundle()
                original = root.base_manifold()
                if fibre_frames is not None:
                    assert fibre_frames.index_set() is indices
                else:
                    assert not bundle.is_pullback()

                def admit(key):
                    local = local_charts[key]
                    source = atlas[local.label()]
                    assert _engine_manifold_chart(local).domain().is_subset(
                        _engine_manifold_chart(source).domain())
                    frame = source if fibre_frames is None else fibre_frames[key]
                    assert frame is original.atlas()[frame.label()]
                    coefficients = tuple(_admit_manifold_expression(entry, local)
                                         for entry in components[key])
                    assert len(coefficients) == int(bundle.rank())
                    return local, frame, coefficients

                return self.element_class(self, {}, None,
                    local_cover=indexed_family(indices, admit), locate=locate)
            if local_charts is not None:
                assert not check, "general local gluing requires the cover and compatibility hypotheses (check=False)"
                assert set(local_charts) == set(components)
                bundle = self._vector_bundle
                root = bundle
                while root.is_pullback():
                    root = root.underlying_bundle()
                original = root.base_manifold()
                if fibre_frames is None:
                    assert not bundle.is_pullback(), "the original fibre frames must be specified"
                    fibre_frames = {key: atlas[chart.label()] for key, chart in local_charts.items()}
                assert set(fibre_frames) == set(components)
                charts, admitted = {}, {}
                for key, coefficients in components.items():
                    local = local_charts[key]
                    source = atlas[local.label()]
                    assert _engine_manifold_chart(local).domain().is_subset(
                        _engine_manifold_chart(source).domain())
                    assert fibre_frames[key] is original.atlas()[fibre_frames[key].label()]
                    coefficients = tuple(coefficients)
                    assert len(coefficients) == int(bundle.rank())
                    charts[key] = source
                    admitted[key] = tuple(_admit_manifold_expression(entry, local) for entry in coefficients)
                domain_data = {key: () for key in components} if domains is None else domains
                assert set(domain_data) == set(components)
                result = self.element_class(self, admitted, None, charts=charts,
                    local_charts=local_charts, domains=domain_data, frames=fibre_frames)
                def evaluate(point, frame_label):
                    chart, _image, _jets = _bundle_image_germ(bundle, point.chart(), point, 0)
                    frame = chart if frame_label is None else original.atlas()[frame_label]
                    return finite_family(tuple(jet.value() for jet in
                        _section_jets(result, point.chart(), point, 0, frame)),
                        name="Fibre coordinates of a smooth section")
                result._section_evaluation = evaluate
                return result
            assert fibre_frames is None and domains is None

            labels = tuple(components)
            extra = tuple(label for label in labels if label not in manifold.chart_labels())
            assert not extra, (
                f"a section of {self._vector_bundle} is stated on the charts of {manifold}, "
                f"and the components given for {extra} are on charts it does not have"
            )
            coverage = _chart_family_covers(manifold, labels) if check else True
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
            if check and underlying is None:
                _chartwise_family_agrees(manifold, admitted, 1)
            elif check:
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
            r"""Restrict along an actual open inclusion, using TU for vector fields.

            A section is a map into the fibres, so its composite with an open
            inclusion is a section of the pulled-back bundle, and on the charts
            of the open submanifold -- which are the ambient charts read there
            (``SmoothManifolds.open_submanifold``) -- its components are the
            section's own (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 8, where vector fields restrict to open submanifolds).  Nothing
            is extended the other way: a section of the restriction need not
            come from one of the manifold.

            For TM, the differential of the open inclusion identifies its
            pullback with TU.  This restriction uses that canonical tangent
            bundle and remains a derivation of C^infinity(U).  The separately
            chosen pullback still retains the inclusion.  This operation's
            inclusion premise is not inferred from chart labels; arbitrary
            smooth-map pullback is the operation :meth:`pullback_of`.
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
            tangent = self._vector_bundle._bundle_tangent_manifold is manifold
            if not tangent:
                return target.pullback_of(section)
            engine_field = None
            if tangent:
                target = domain.tangent_bundle().sections()
                if section._engine_field is None or getattr(
                    _engine_manifold(manifold).manifold(), "_owned_coordinate_data", False
                ):



                    def provider(chart, point, order):
                        image_chart, image, arguments = _mapping_germ(inclusion, chart, point, order)
                        ambient_frame = manifold.atlas()[chart.label()]
                        return tuple(coefficient.compose(arguments) for coefficient in
                                     _section_jets(section, image_chart, image, order, ambient_frame))
                    return target._from_tangent_jets(provider)
                engine_field = section._engine_field.restrict(_engine_manifold(domain))
            described = section
            components = section.components()
            charts = {key: domain.atlas()[section.component_chart(key).label()]
                for key in components if section.component_chart(key).label() in domain.chart_labels()}
            if not charts:
                if not tangent:
                    return target.pullback_of(section)
                described = self._vector_bundle.pullback_along(inclusion).sections().pullback_of(section)
                components = described.components()
                charts = {key: described.component_chart(key) for key in components
                    if described.component_frame(key).label() == described.component_chart(key).label()}
            return target._construct(
                {key: tuple(SR(_engine_manifold_expression(entry)) for entry in components[key]) for key in charts},
                charts=charts,
                domains={key: tuple(SR(_engine_manifold_expression(c)) for c in described.component_nonvanishing(key))
                    for key in charts},
                frames=charts if tangent else {key: described.component_frame(key) for key in charts},
                evaluation=lambda point, frame: section.components_at(inclusion(point),
                    point.chart().label() if tangent and frame is None else frame),
                engine_field=engine_field,
            )

        def from_derivation(self, derivation):
            r"""The section ``V`` with ``V f = derivation(f)`` for every smooth function ``f``.

            A derivation is local: if f vanishes near p, a bump h supported
            there and equal to one near p gives hf=0 and therefore Df(p)=0
            by Leibniz. Extend each local coordinate by a bump equal to one
            near p. The ith coefficient near p is D of this extended
            coordinate, restricted to that neighbourhood. Thus it is smooth
            and independent of the bump. The germ derivation chain rule gives
            the coordinate transition law and Df = V(f), and also uniqueness.
            This is Lee, Introduction to Smooth Manifolds, 2nd ed., Prop. 8.15.

            A globally spanning symbolic family, when separately certified,
            can compute the same coefficients at once. It is not a condition
            of construction.
            """
            from sage_extensions.categories.functions.smooth_germs import (
                _SmoothGermFunction, _function_jet, _coordinates_in_chart,
                _bump_extended_coordinate,
            )

            manifold = self.base_manifold()
            assert self.vector_bundle()._bundle_tangent_manifold is not None
            functions = manifold.smooth_functions()


            if element_parent(derivation) is self:
                return derivation
            try:
                if manifold._preamble_chart_index_set is not None:
                    raise CoverageUndecided("a general atlas is not enumerated")
                symbolic = self._from_derivation_symbolic(derivation)
            except (CoverageUndecided, AssertionError, TypeError, ValueError, NotImplementedError):
                symbolic = None
            if symbolic is not None:
                return symbolic

            global_charts = tuple(manifold.atlas()[label]
                                  for label in manifold.selected_finite_chart_labels()
                                  if manifold.atlas()[label].domain() is manifold)
            if global_charts:
                home = global_charts[0]
                coordinates = tuple(manifold.smooth_function({home.label(): coordinate})
                                    for coordinate in home.coordinates())
                coefficients = tuple(derivation(coordinate) for coordinate in coordinates)
                assert all(element_parent(coefficient) is functions for coefficient in coefficients), (
                    "the derivation must take values in its smooth function algebra"
                )
                section = self.element_class(self, {home.label(): coefficients}, None)
                if manifold._preamble_chart_index_set is None and len(tuple(manifold.chart_labels())) == 1:
                    return section
                return self._from_tangent_jets(lambda chart, point, order:
                    _section_jets(section, chart, point, order, chart))

            def provider(chart, point, order):
                center = _coordinates_in_chart(chart, point)
                values = []
                for index in range(int(manifold.dimension())):
                    extended = _bump_extended_coordinate(manifold, chart, center, index)
                    derivative = derivation(extended)
                    assert element_parent(derivative) is functions, (
                        "the derivation must take values in its smooth function algebra"
                    )
                    values.append(_function_jet(derivative, chart, point, order))
                return tuple(values)


            return self._from_tangent_jets(provider)

        def _from_derivation_symbolic(self, derivation):
            """Optional simultaneous exact calculation of the local inverse."""
            from sage.matrix.constructor import matrix as _engine_matrix
            from sage.modules.free_module_element import vector as _engine_vector

            manifold = self.base_manifold()
            functions = manifold.smooth_functions()
            global_charts = tuple(chart for chart in manifold.atlas().values()
                                  if chart.domain() is manifold)
            if global_charts:
                chart = global_charts[0]
                spanning = tuple(manifold.smooth_function({chart.label(): coordinate})
                                 for coordinate in chart.coordinates())
            else:
                spanning = manifold._cotangent_spanning_functions()
            if spanning is None:
                return None
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

            On a map representation D in source chart A with image in U,
            and a section description on V, use J_{V->U}(f(q)) s_V(f(q))
            only on D intersect f^{-1}(U intersect V).  Every transition path
            contributes its own actual overlap.  These domains cover the source
            when the input map domains and section domains cover and the atlas
            supplies its transitions on their overlaps.  This is the inverse
            image of a cover, not analytic continuation (Lee, Proposition 2.5,
            Corollary 2.8; Tu, Theorem 20.6 and Proposition 20.7).
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
            def germs(chart, point, order, frame):
                target, image, arguments = _mapping_germ(mapping, chart, point, order)
                return tuple(entry.compose(arguments) for entry in
                             _section_jets(section, target, image, order, frame))
            try:
                if mapping._locate_representation is not None or section._local_cover is not None:
                    raise CoverageUndecided("local indexed covers are evaluated at the point")
                result = self._pullback_of_symbolic(section)
            except (AssertionError, TypeError, ValueError, NotImplementedError, CoverageUndecided):
                result = self.element_class(self, {}, None)
            result._jet_evaluation = germs
            return result

        def _pullback_of_symbolic(self, section):
            """Optional local symbolic descriptions of the defining pullback germ."""
            bundle = self._vector_bundle
            underlying = bundle.underlying_bundle()
            mapping = bundle.mapping()
            domain = bundle.base_manifold()
            base = underlying.base_manifold()
            stated = section.components()
            components = {}
            charts, domains, frames = {}, {}, {}
            for map_index in mapping.chart_maps().index_set():
                source_label, target_label = map_index[:2]
                chart = domain.atlas()[source_label]
                target = base.atlas()[target_label]
                expressions = tuple(
                    SR(_engine_manifold_expression(expression))
                    for expression in mapping.chart_map(*map_index)
                )
                symbols = tuple(_engine_manifold_chart(target)[:])
                substitution = dict(zip(symbols, expressions, strict=True))
                direct = tuple(key for key in stated
                    if section.component_chart(key).label() == target_label
                    and not section.component_nonvanishing(key))
                section_indices = direct[:1] if direct else tuple(stated)
                for section_index in section_indices:
                    section_chart = section.component_chart(section_index)
                    section_label = section_chart.label()
                    changes = {(): None} if section_label == target_label else dict(
                        base.coordinate_changes(target_label, section_label).items()
                    )
                    for path, change in changes.items():
                        where = [SR(_engine_manifold_expression(c)) for c in mapping.chart_map_domain(*map_index)]
                        if any(c == 0 for c in where):
                            continue
                        overlap = () if change is None else change.source_overlap()
                        for condition in overlap:
                            formula = SR(_engine_manifold_expression(condition)).subs(substitution)
                            where.append(formula)
                            if formula == 0:
                                break
                        else:
                            in_section = expressions if change is None else tuple(
                                SR(_engine_manifold_expression(entry)).subs(substitution)
                                for entry in change.forward_expressions()
                            )
                            section_symbols = tuple(_engine_manifold_chart(section_chart)[:])
                            section_substitution = dict(zip(section_symbols, in_section, strict=True))
                            for condition in section.component_nonvanishing(section_index):
                                formula = SR(_engine_manifold_expression(condition)).subs(section_substitution)
                                where.append(formula)
                                if formula == 0:
                                    break
                            else:
                                values = tuple(SR(_engine_manifold_expression(entry)).subs(section_substitution)
                                    for entry in stated[section_index])
                                frame = section.component_frame(section_index)
                                if not underlying.is_pullback() and change is not None:
                                    values = tuple(sum(
                                        SR(_engine_manifold_expression(coordinate)).diff(variable).subs(section_substitution) * value
                                        for variable, value in zip(section_symbols, values, strict=True)
                                    ) for coordinate in change.inverse_expressions())
                                    frame = target
                                key = (map_index, section_index, path)
                                components[key] = values
                                charts[key], domains[key], frames[key] = chart, tuple(where), frame
            return self._construct(components, charts=charts, domains=domains, frames=frames,
                evaluation=lambda point, frame: section.components_at(mapping(point), frame))

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

        def trivialized_by(self, frame, *, check=True):
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
            if not check:


                return _object_of(self.category(), vector_bundle=self._vector_bundle,
                                  base_ring=self.base_ring(), retained_frame=family)


            if any(set(vector.components()) != set(family[0].components())
                   for vector in family) or any(
                key not in self.base_manifold().chart_labels()
                or any(vector.component_chart(key) is not family[0].component_chart(key)
                       or vector.component_frame(key) is not family[0].component_frame(key)
                       for vector in family)
                for key in family[0].components()
            ):
                try:
                    certified = _certify_frame_on_common_refinement(family)
                except (AssertionError, TypeError, ValueError, NotImplementedError, CoverageUndecided):
                    certified = False
                if not certified:
                    raise CoverageUndecided("no certified common local frame refinement covers the base")
                return _object_of(self.category(), vector_bundle=self._vector_bundle,
                                  base_ring=self.base_ring(), retained_frame=family)
            manifold = self.base_manifold()
            stated = tuple(family[0].components())
            domains = {}
            for label in stated:
                if label not in manifold.chart_labels() or any(label not in section.components() for section in family):
                    raise CoverageUndecided("the frame requires a common local coordinate cover")
                if any(section.component_chart(label) is not family[0].component_chart(label)
                    or section.component_frame(label) is not family[0].component_frame(label) for section in family):
                    raise CoverageUndecided("frame columns must be expressed in one common source chart and fibre frame")
                domains[label] = (label, tuple(c for section in family for c in section.component_nonvanishing(label)))
            coverage = _chart_family_covers(manifold, stated, local_domains=domains)
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
                        for condition in tuple(chart.nonvanishing()) + domains[label][1]
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
        assert all(element_parent(f) is manifold.smooth_functions() for f in family)
        try:
            if any(section._local_cover is not None or not section.components()
                   for section in self._frame):
                raise CoverageUndecided("the frame is represented by local germs")
            return self._forward_symbolic(family)
        except (AssertionError, TypeError, ValueError, KeyError, NotImplementedError, CoverageUndecided):
            from sage_extensions.categories.functions.smooth_germs import _function_jet, _TaylorJet

            module = self._bundle.sections()
            def germs(chart, point, order, frame=None):
                factors = tuple(_function_jet(f, chart, point, order) for f in family)
                vectors = tuple(_section_jets(section, chart, point, order, frame)
                                for section in self._frame)
                zero = _TaylorJet.constant(factors[0].field, factors[0].n, order, 0)
                return tuple(sum((a*v for a, v in zip(factors, column, strict=True)), zero)
                             for column in zip(*vectors, strict=True))
            if self._bundle.is_pullback():
                return module.element_class(module, {}, None, jet_evaluation=germs)
            return module._from_tangent_jets(germs)

    def _forward_symbolic(self, family):
        """Optional exact chartwise calculation of the frame map."""
        manifold = self.base_manifold()
        rank = int(self._bundle.rank())
        if self._bundle.is_pullback():
            module = self._bundle.sections()
            result = module.zero()
            for function, vector in zip(family, self._frame, strict=True):
                result = result + module.scalar_multiple(function, vector)
            return result
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
        if any(set(entries) != set(components[0]) for entries in components):
            raise CoverageUndecided("symbolic frame coefficients lack a common cover")
        if any(section.component_nonvanishing(label) for section in self._frame
               for label in components[0]):
            raise CoverageUndecided("the symbolic frame map needs a common local refinement")
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
        manifold = self.base_manifold()
        assert element_parent(section) is self._bundle.sections(), (
            f"{section} is not a section of {self._bundle}: its parent is "
            f"{element_parent(section)}"
        )
        try:
            if any(vector._local_cover is not None or not vector.components()
                   for vector in (*self._frame, section)):
                raise CoverageUndecided("the frame or section is represented by local germs")
            return self._inverse_symbolic(section)
        except (AssertionError, TypeError, ValueError, KeyError, NotImplementedError, CoverageUndecided):
            from sage_extensions.categories.functions.smooth_germs import _SmoothGermFunction

            rank = int(self._bundle.rank())
            def coordinate(index):
                def provider(chart, point, order):
                    frame, _image, _args = _bundle_image_germ(self._bundle, chart, point, order)
                    columns = tuple(_section_jets(v, chart, point, order, frame) for v in self._frame)
                    value = _section_jets(section, chart, point, order, frame)
                    determinant = _jet_determinant(columns)
                    replaced = tuple(value if j == index else col for j, col in enumerate(columns))
                    return _jet_determinant(replaced) * determinant.reciprocal()
                return manifold.smooth_functions()(_SmoothGermFunction(manifold, provider))
            coordinates = tuple(coordinate(i) for i in range(rank))
            return coordinates[0] if rank == 1 else coordinates

    def _inverse_symbolic(self, section):
        """Optional symbolic evaluation of the inverse frame map."""
        from sage.matrix.constructor import matrix as _engine_matrix

        manifold = self.base_manifold()
        rank = int(self._bundle.rank())
        components = tuple(entry.components() for entry in self._frame)
        labels = tuple(components[0])
        if not labels or any(label not in manifold.chart_labels() for label in labels):
            raise CoverageUndecided("the frame has no common whole-chart symbolic description")
        if any(set(entries) != set(labels) for entries in components):
            raise CoverageUndecided("the symbolic frame inverse needs a common local refinement")
        if any(vector.component_nonvanishing(label) for vector in self._frame for label in labels):
            raise CoverageUndecided("the symbolic frame inverse cannot extrapolate a local description")
        if any(vector.component_frame(label) is not self._frame[0].component_frame(label)
               for vector in self._frame for label in labels):
            raise CoverageUndecided("the symbolic frame columns are in different fibre frames")
        if self._bundle.is_pullback() and section._section_evaluation is not None:
            if any(label not in section.components()
                or section.component_frame(label) is not self._frame[0].component_frame(label) for label in labels):
                raise CoverageUndecided("inverse trivialization requires the section in the frame's common fibre coordinates")
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
