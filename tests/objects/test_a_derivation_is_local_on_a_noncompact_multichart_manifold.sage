r"""Derivation recovery does not require a finite compact-support spanning family.

On the real line with an additional chart on its punctured open subset, let
X = (1+x^2) d/dx. The derivation f -> X(f) has local coefficient 1+x^2
everywhere, including points beyond every fixed-radius chart bump. Lee,
Introduction to Smooth Manifolds, 2nd ed., Propositions 3.8, 8.14 and 8.15.
"""

import pytest

from sage_extensions.all import *


def test_flat_function_local_derivatives_and_frame_roundtrip() -> None:
    r"""The flat function exp(-1/t) for t>0, zero for t<=0, is not analytic.

    Its nth derivative for t>0 is exp(-u) P_n(u), u=1/t, where
    P_0=1 and P_(n+1)=u^2(P_n-P'_n). Every derivative vanishes at zero,
    but the function is positive to the right.
    """
    line = SmoothManifolds()(1, "flat line")
    chart = line.chart("U", "t")
    algebra = line.smooth_functions()
    sections = line.tangent_bundle().sections()
    frame = sections.coordinate_vector_field(chart, 0)

    def derivatives(_chart, point, alpha):
        t = point.coordinates()[0]
        if ask(t <= RR(0)) is True:
            return RR(0)
        u = RR(1)/t
        coefficients = {0: 1}
        for _ in range(alpha[0]):
            next_coefficients = {}
            for power, c in coefficients.items():
                next_coefficients[power+2] = next_coefficients.get(power+2, 0) + c
                if power:
                    next_coefficients[power+1] = next_coefficients.get(power+1, 0) - power*c
            coefficients = next_coefficients
        return (-u).exp()*sum((RR(c)*u**power for power,c in coefficients.items()), RR(0))

    f = algebra.from_local_derivatives(derivatives)
    p, z = line((1,)), line((0,))
    assert f(z) == RR(0)
    assert frame(f)(z) == RR(0)
    assert frame(frame(f))(z) == RR(0)
    assert f(p) == (-RR(1)).exp()
    assert frame(f)(p) == (-RR(1)).exp()
    assert frame(frame(f))(p) == -(-RR(1)).exp()
    trivialization = sections.trivialized_by(frame).trivialization()
    back = trivialization.inverse(trivialization.forward(f))
    assert back(p) == f(p)
    assert frame(back)(p) == frame(f)(p)
    mapping = line.Mor(line)({("U", "U"): (f,)})
    target = sections.section({"U": (chart.function_ring().one()+chart.coordinate(0)**2,)})
    pulled = line.tangent_bundle().pullback_along(mapping).sections().pullback_of(target)
    assert tuple(pulled.components_at(p)) == (RR(1)+(-RR(2)).exp(),)
    assert tuple(pulled.components_at(z)) == (RR(1),)


def test_rank_two_frame_stated_on_distinct_covers() -> None:
    r"""The second constant frame vector is given on the cover x!=0 or x!=1."""
    plane = SmoothManifolds()(2, "two-cover plane")
    u = plane.chart("U", "x y")
    x, y = u.coordinates()
    v = plane.chart_on_open_subset("V", "x y", "U", (x,), same_coordinates=True)
    w = plane.chart_on_open_subset("W", "x y", "U", (x-u.function_ring().one(),), same_coordinates=True)
    sections = plane.tangent_bundle().sections()
    first = sections.section({"U": (u.function_ring().one(), u.function_ring().zero())})
    second = sections.section({
        "V": (v.function_ring().zero(), v.function_ring().one()),
        "W": (w.function_ring().zero(), w.function_ring().one()),
    })
    trivialization = sections.trivialized_by((first, second)).trivialization()
    a, b = plane.smooth_function({"U": x}), plane.smooth_function({"U": y})
    result = trivialization.forward((a, b))
    inverse = trivialization.inverse(result)
    for coords in ((0, 3), (1, 5), (2, 7)):
        point = plane(coords)
        expected = tuple(RR(c) for c in coords)
        assert tuple(result.components_at(point, "U")) == expected
        assert tuple(f(point) for f in inverse) == expected


def test_direct_pullback_section_on_independently_indexed_local_cover() -> None:
    r"""For the constant map to zero, the coefficient t is not pulled back from the target."""
    line = SmoothManifolds()(1, "constant-map base")
    chart = line.chart("U", "t")
    t = chart.coordinate(0)
    one = chart.function_ring().one()
    first = line.restricted_chart("U", (t,))
    second = line.restricted_chart("U", (t-one,))
    mapping = line.Mor(line)({("U", "U"): (chart.function_ring().zero(),)})
    sections = line.tangent_bundle().pullback_along(mapping).sections()
    section = sections.section(
        {"nonzero": (first.coordinate(0),), "notone": (second.coordinate(0),)},
        local_charts={"nonzero": first, "notone": second},
        fibre_frames={"nonzero": chart, "notone": chart},
        domains={"nonzero": (t,), "notone": (t-one,)},
        check=False,
    )


    for value in (0, 1, 2):
        assert tuple(section.components_at(line((value,)), "U")) == (RR(value),)


def test_derivation_recovery_with_a_redundant_open_chart() -> None:
    line = SmoothManifolds()(1, "noncompact line")
    full = line.chart("U", "x")
    x = full.coordinate(0)
    cut = line.chart_on_open_subset("V", "x", "U", (x,), same_coordinates=True)
    sections = line.tangent_bundle().sections()
    field = sections.section({"U": (full.function_ring().one() + x**2,)})

    recovered = sections.from_derivation(lambda f: field(f))

    p = line.point((17,), "U")
    q = cut.domain()(p)
    assert recovered.parent() is sections
    assert recovered.components()["U"][0](p) == RR(290)
    assert recovered.components()["V"][0](q) == RR(290)
    assert recovered(line.smooth_function({"U": x**2}))(p) == RR(9860)


def test_composition_and_derivative_of_real_line_germs() -> None:
    r"""For f(t)=1+t^2 and g(s)=s^3+s, at t=2, f=5, f'=4, f''=2.

    Thus g(f)=130, the first derivative is 76*4=304 and the second
    is 30*4^2+76*2=632, without symbolic formulas for either map.
    """
    line = SmoothManifolds()(1, "germ composition")
    chart = line.chart("U", "t")
    inner = line.smooth_functions()
    frame = line.tangent_bundle().sections().coordinate_vector_field(chart, 0)

    def outer_derivatives(chart, point, alpha):
        s = point.coordinates()[0]
        values = (s**3+s, RR(3)*s*s+RR(1), RR(6)*s, RR(6))
        return values[alpha[0]] if alpha[0] <= 3 else RR(0)

    def inner_derivatives(chart, point, alpha):
        t = point.coordinates()[0]
        values = (t*t+RR(1), RR(2)*t, RR(2))
        return values[alpha[0]] if alpha[0] <= 2 else RR(0)

    f = inner.from_local_derivatives(inner_derivatives)
    g = C(oo, RR, RR).from_local_derivatives(outer_derivatives)
    p = line((2,))
    h = g.compose(f)
    assert h.parent() is inner
    assert g(RR(5)) == RR(130)
    assert h(p) == RR(130)
    assert frame(h)(p) == RR(304)
    assert frame(frame(h))(p) == RR(632)
    assert g.derivative()(RR(5)) == RR(76)
    assert g.derivative().derivative()(RR(5)) == RR(30)


def test_exact_real_germ_at_a_cauchy_presented_point() -> None:
    r"""The regular Cauchy sequence 5+2^(-n) represents 5 exactly.

    The polynomial s^3+s and its derivative take values 130 and 76
    at its limit, and the section g d/ds recovered from its derivation
    acts on g with value 130*76=9880 there. Strict rational bounds test the exact real computations
    without requiring a decision of equality of two real presentations.
    """
    sequence = Sets().Mor(NN, QQ)(lambda n: QQ(5)+QQ(1)/QQ(2)**int(n))
    point = RR.of_cauchy(sequence)
    assert point.cauchy_sequence() is sequence

    def derivatives(chart, point, alpha):
        s = point.coordinates()[0]
        values = (s**3+s, RR(3)*s*s+RR(1), RR(6)*s, RR(6))
        return values[alpha[0]] if alpha[0] <= 3 else RR(0)

    g = C(oo, RR, RR).from_local_derivatives(derivatives)
    assert ask(g(point) > RR(129)) is True
    assert ask(g(point) < RR(131)) is True
    assert ask(g.derivative()(point) > RR(75)) is True
    assert ask(g.derivative()(point) < RR(77)) is True

    sections = RR.tangent_bundle().sections()
    frame = sections.coordinate_vector_field(RR.identity_chart(), 0)
    assert ask(frame(g)(point) > RR(75)) is True
    assert ask(frame(g)(point) < RR(77)) is True
    assert ask(frame(frame(g))(point) > RR(29)) is True
    assert ask(frame(frame(g))(point) < RR(31)) is True
    section = sections.scalar_multiple(g, frame)
    recovered = sections.from_derivation(lambda f: section(f))
    coefficient = tuple(recovered.components_at(point))[0]
    assert ask(coefficient > RR(129)) is True
    assert ask(coefficient < RR(131)) is True
    assert ask(recovered(g)(point) > RR(9879)) is True
    assert ask(recovered(g)(point) < RR(9881)) is True


def test_located_countable_cover_drives_scalar_section_and_pullback() -> None:
    r"""The open sets R minus {n}, n natural, cover R.

    At t choose n=0 unless t=0, in which case choose n=1.
    The sections t^2, t d/dt and map t |-> t+1 glue on this cover.
    The locator is defining cover data, not a finite search bound.
    """
    line = SmoothManifolds()(1, "countably covered line")
    home = line.chart("U", "t")
    t = home.coordinate(0)
    local = Sets().indexed_family(NN, lambda n: line.restricted_chart(
        "U", (t-home.function_ring()(RR(int(n))),)))
    def locate(point):
        return NN(1) if ask(point.coordinates()[0] == RR(0)) is True else NN(0)
    f = line.smooth_function(Sets().indexed_family(NN, lambda n: local[n].coordinate(0)**2),
        check=False, local_charts=local, locate=locate)
    sections = line.tangent_bundle().sections()
    v = sections.section(Sets().indexed_family(NN, lambda n: (local[n].coordinate(0),)),
        check=False, local_charts=local, locate=locate)
    frame = sections.section(Sets().indexed_family(NN, lambda n: (local[n].function_ring().one(),)),
        check=False, local_charts=local, locate=locate)
    mapping = line.Mor(line)(
        Sets().indexed_family(NN, lambda n: (local[n].coordinate(0)+local[n].function_ring().one(),)),
        local_charts=local, target_charts=Sets().indexed_family(NN, lambda n: home), locate=locate)
    trivialization = sections.trivialized_by(frame, check=False).trivialization()
    pulled = line.tangent_bundle().pullback_along(mapping).sections().pullback_of(v)
    for value in (0, 2):
        p = line((value,))
        assert f(p) == RR(value**2)
        assert v(f)(p) == RR(2*value**2)
        assert tuple((v + (-v)).components_at(p)) == (RR(0),)
        assert trivialization.inverse(trivialization.forward(f))(p) == f(p)
        assert tuple(mapping(p).coordinates()) == (RR(value+1),)
        assert tuple(pulled.components_at(p)) == (RR(value+1),)
        assert tuple((mapping*mapping)(p).coordinates()) == (RR(value+2),)


def test_nonsymbolic_smooth_change_of_coordinates():
    plane = SmoothManifolds()(2, "smooth shear plane")
    u = plane.chart("U", "x y")
    v = plane.chart("V", "s t")
    algebra = plane.smooth_functions()

    def derivatives(chart, point, alpha):
        x = point.coordinates()[0]
        if alpha[1] or ask(x <= RR(0)) is True:
            return RR(0)
        z = RR(1)/x
        coefficients = {0: 1}
        for _ in range(alpha[0]):
            next_coefficients = {}
            for power, c in coefficients.items():
                next_coefficients[power+2] = next_coefficients.get(power+2, 0) + c
                if power:
                    next_coefficients[power+1] = next_coefficients.get(power+1, 0) - power*c
            coefficients = next_coefficients
        return (-z).exp()*sum((RR(c)*z**power for power,c in coefficients.items()), RR(0))

    g = algebra.from_local_derivatives(derivatives)
    plane.transition_map("U", "V", (u.coordinate(0), u.coordinate(1)+g),
                         (v.coordinate(0), v.coordinate(1)-g),
                         source_local=u, target_local=v)
    p = plane.point((1, 2), "U")
    h = plane.smooth_function({"V": v.coordinate(1)}, check=False)
    assert h(p) == RR(2)+(-RR(1)).exp()
    sections = plane.tangent_bundle().sections()
    field = sections.section({"V": (v.function_ring().one(), v.function_ring().zero())}, check=False)
    assert tuple(field.components_at(p, "U")) == (RR(1), -(-RR(1)).exp())
    assert field(h)(p) == RR(0)


def test_restriction_to_nonsymbolic_open_locus():
    line = SmoothManifolds()(1, "open-locus line")
    home = line.chart("U", "x")
    algebra = line.smooth_functions()


    def flat_derivatives(chart, point, alpha):
        x = point.coordinates()[0]
        if ask(x <= RR(0)) is True:
            return RR(0)
        z = RR(1)/x
        coefficients = {0: 1}
        for _ in range(alpha[0]):
            next_coefficients = {}
            for power, c in coefficients.items():
                next_coefficients[power+2] = next_coefficients.get(power+2, 0) + c
                if power:
                    next_coefficients[power+1] = next_coefficients.get(power+1, 0) - power*c
            coefficients = next_coefficients
        return (-z).exp()*sum((RR(c)*z**power for power,c in coefficients.items()), RR(0))

    f = algebra.from_local_derivatives(flat_derivatives)
    def radius(coordinates):
        n = 1
        while ask(RR(2)/RR(n) < coordinates[0]) is not True:
            n *= 2
        return QQ(1)/QQ(n)
    cut = line.restricted_chart("U", (f,), local_radius=radius)
    domain = cut.domain()
    inclusion = line.open_submanifold_inclusion(domain)
    point = domain((1,))
    sections = line.tangent_bundle().sections()
    field = sections.section({"U": (home.coordinate(0),)})
    restricted = sections.restrict(field, inclusion)
    assert tuple(inclusion(point).coordinates()) == (RR(1),)
    assert tuple(restricted.components_at(point)) == (RR(1),)
    g = domain.smooth_function({"U": cut.coordinate(0)**2})
    assert restricted(g)(point) == RR(2)


def test_transition_retains_actual_nonsymbolic_overlap():
    line = SmoothManifolds()(1, "punctured transition")
    u = line.chart("U", "t")
    v = line.chart_on_open_subset("V", "t", "U", (u.coordinate(0),), same_coordinates=True)
    algebra = line.smooth_functions()

    def derivatives(chart, point, alpha):
        t = point.coordinates()[0]
        k = alpha[0]
        return t*t if k == 0 else RR(2)*t if k == 1 else RR(2) if k == 2 else RR(0)

    def radius(coordinates):
        n = 1
        t = coordinates[0]
        while ask(t*t > (RR(2)/RR(n))**2) is not True:
            n *= 2
        return QQ(1)/QQ(n)

    cut = line.restricted_chart("U", (algebra.from_local_derivatives(derivatives),), local_radius=radius)
    transition = line.transition_map("U", "V", (cut.coordinate(0),), (v.coordinate(0),),
                                     source_local=cut, target_local=v)
    assert transition(RR(2))[0] == RR(2)
    with pytest.raises(AssertionError):
        transition(RR(0))


def test_located_cover_without_finite_subcover():
    r"""The intervals (-n-1,n+1) cover R but no finite subfamily does."""
    line = SmoothManifolds()(1, "exhaustion by bounded intervals")
    home = line.chart("U", "t")
    algebra = line.smooth_functions()
    selected = {}

    def choose(k, i):
        c = 1
        for j in range(i):
            c = c*(k-j)//(j+1)
        return c

    def flat_jet(x, k):
        if ask(x <= RR(0)) is True:
            return RR(0)
        z = RR(1)/x
        coefficients = {0: 1}
        for _ in range(k):
            next_coefficients = {}
            for power, c in coefficients.items():
                next_coefficients[power+2] = next_coefficients.get(power+2, 0) + c
                if power:
                    next_coefficients[power+1] = next_coefficients.get(power+1, 0) - power*c
            coefficients = next_coefficients
        return (-z).exp()*sum((RR(c)*z**power for power,c in coefficients.items()), RR(0))

    def local(n):
        if n not in selected:
            bound = RR(int(n)+1)
            def derivatives(chart, point, alpha):
                t = point.coordinates()[0]
                k = alpha[0]
                return sum((RR((-1)**i*choose(k,i))*flat_jet(bound-t,i)*flat_jet(bound+t,k-i)
                            for i in range(k+1)), RR(0))
            def radius(coordinates):
                t = coordinates[0]
                d = 1
                while not (ask(t+RR(2)/RR(d) < bound) is True and
                           ask(-bound < t-RR(2)/RR(d)) is True):
                    d *= 2
                return QQ(1)/QQ(d)
            guard = algebra.from_local_derivatives(derivatives)
            selected[n] = line.restricted_chart("U", (guard,), local_radius=radius)
        return selected[n]

    def locate(point):
        t = point.coordinates()[0]
        n = 0
        while not (ask(-RR(n+1) < t) is True and ask(t < RR(n+1)) is True):
            n += 1
        return NN(n)

    charts = Sets().indexed_family(NN, local)
    expressions = Sets().indexed_family(NN, lambda n: charts[n].coordinate(0)**2)
    function = line.smooth_function(expressions, check=False, local_charts=charts, locate=locate)
    sections = line.tangent_bundle().sections()
    field = sections.coordinate_vector_field(home, 0)
    for t in (0, 7, -9):
        p = line((t,))
        assert function(p) == RR(t*t)
        assert field(function)(p) == RR(2*t)
    assert {int(n) for n in selected} == {0, 7, 9}
