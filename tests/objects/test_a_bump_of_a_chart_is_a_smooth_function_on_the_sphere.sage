r"""The bump of a stereographic chart is a smooth function on $S^1$ and $S^2$, and sections act on it.

$f(t) = e^{-1/t}$ for $t > 0$ and $0$ otherwise is smooth (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Lemma 2.20); $h(t) = f(t)/(f(t) + f(1-t))$ is $0$ for $t \le 0$ and
$1$ for $t \ge 1$ (Lemma 2.21).  The bump of $U_N$ with radii $2 < 3$ is
$H = h((9 - |x|^2)/5)$ on $U_N$, extended by $0$ (Lemma 2.22): $H = 1$ where $|x| \le 2$,
$H = 0$ where $|x| \ge 3$.  On $U_S$, $|x|^2 = 1/|y|^2$, so $H = 0$ where $|y| \le 1/3$,
the north pole $y = 0$ included, and $H = 1$ where $|y| \ge 1/2$.

On $S^1$ the frame $E = (1+x^2)\partial_x = -(1+y^2)\partial_y$ gives $E(H) = 0$ wherever
$H$ is locally constant, and $E(xH) = E(x) = 1 + x^2$ where $|x| < 2$: $2$ at $x = 1$.
The section $HE$ has component $1 + x^2 = 2$ at $x = 1$ and $0$ at $y = 1/4$.
"""

from sage_extensions.all import *


def _the_circle_and_its_frame():
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    frame = circle.tangent_bundle().sections().section(
        {
            "U_N": (north.function_ring().one() + north.coordinate(0) ** 2,),
            "U_S": (-(south.function_ring().one() + south.coordinate(0) ** 2),),
        }
    )
    return circle, north, south, frame


def test_the_bump_of_the_north_chart_is_one_inside_and_zero_outside() -> None:
    r"""$H(x = 1) = 1$, $H(y = 1/4) = 0$, $H(y = 0) = 0$ and $H(y = 1) = 1$ on $S^1$."""
    circle, north, south, _frame = _the_circle_and_its_frame()

    bump = circle.chart_bump("U_N", 2, 3)

    assert bump.parent() is circle.smooth_functions()
    assert bump(circle.point((1,), "U_N")) == RR(1)
    assert bump(circle.point((RR(1) / RR(4),), "U_S")) == RR(0)
    assert bump(circle.point((0,), "U_S")) == RR(0)
    assert bump(circle.point((1,), "U_S")) == RR(1)


def test_a_section_differentiates_the_bump_and_its_product_with_a_coordinate() -> None:
    r"""$E(H) = 0$ at $x = 1$ and at $y = 0$; $E(xH) = 1 + x^2 = 2$ at $x = 1$."""
    circle, north, south, frame = _the_circle_and_its_frame()
    bump = circle.chart_bump("U_N", 2, 3)

    derivative = frame(bump)

    assert derivative(circle.point((1,), "U_N")) == RR(0)
    assert derivative(circle.point((0,), "U_S")) == RR(0)


def test_the_bump_times_the_frame_is_a_section_with_its_values() -> None:
    r"""$HE$ is $2$ at $x = 1$ and $0$ at $y = 1/4$; the trivialization reads back $H$."""
    circle, north, south, frame = _the_circle_and_its_frame()
    bump = circle.chart_bump("U_N", 2, 3)
    sections = circle.tangent_bundle().sections()
    trivialization = sections.trivialized_by(frame).trivialization()

    scaled = trivialization.forward(bump)
    read = trivialization.inverse(scaled)

    assert scaled.components()["U_N"][0](north.domain()((1,))) == RR(2)
    assert read(circle.point((1,), "U_N")) == RR(1)
    assert read(circle.point((RR(1) / RR(4),), "U_S")) == RR(0)


def test_the_bump_of_the_north_chart_of_the_two_sphere() -> None:
    r"""On $S^2$: $H = 1$ at $x = (1, 1)$, $|x|^2 = 2 \le 4$; $H = 0$ at $y = (1/8, 1/8)$, where $|x|^2 = 1/|y|^2 = 32 \ge 9$, and at $y = 0$."""
    sphere = SmoothManifolds().sphere(2)

    bump = sphere.chart_bump("U_N", 2, 3)

    assert bump(sphere.point((1, 1), "U_N")) == RR(1)
    assert bump(sphere.point((RR(1) / RR(8), RR(1) / RR(8)), "U_S")) == RR(0)
    assert bump(sphere.point((0, 0), "U_S")) == RR(0)



def test_the_chart_bump_reads_cauchy_presented_support_boundaries_and_pole() -> None:
    r"""H is one at x=2, zero at x=3 and at the reciprocal chart's pole.

    Each input is a regular Cauchy presentation of the stated real.
    The comparisons test certified exact-real bounds, not symbolic
    substitution of a representative or a floating-point approximation.
    """
    circle, _, _, _ = _the_circle_and_its_frame()
    bump = circle.chart_bump("U_N", 2, 3)
    epsilon = RR(QQ(1)/QQ(2)**20)
    for limit, label, expected in ((2,"U_N",1), (3,"U_N",0), (0,"U_S",0)):
        point = RR.of_cauchy(Sets().Mor(NN, QQ)(
            lambda n: QQ(limit)+QQ(1)/QQ(2)**int(n)))
        value = bump(circle.point((point,), label))
        assert value.parent() is RR
        assert ask(value > RR(expected)-epsilon) is True
        assert ask(value < RR(expected)+epsilon) is True


def test_the_chart_bump_differentiates_at_an_exact_cauchy_point_in_its_transition_region() -> None:
    r"""At x=5/2, t=(9-x^2)/5=11/20 and t'=-1.

    For h(t)=f(t)/(f(t)+f(1-t)), f(t)=exp(-1/t), differentiation
    gives h'=h(1-h)(1/t^2+1/(1-t)^2). The frame acts by
    (1+x^2)d/dx, so its derivative is -29/4 times h'.
    """
    circle, _, _, frame = _the_circle_and_its_frame()
    bump = circle.chart_bump("U_N", 2, 3)
    a = RR.of_cauchy(Sets().Mor(NN, QQ)(
        lambda n: QQ(5)/QQ(2)+QQ(1)/QQ(2)**int(n)))
    p = circle.point((a,), "U_N")
    t = RR(11)/RR(20)
    rising = (-RR.one()/t).exp()
    falling = (-RR.one()/(RR.one()-t)).exp()
    h = rising/(rising+falling)
    derivative = -RR(29)/RR(4)*h*(RR.one()-h)*(t**(-2)+(RR.one()-t)**(-2))
    epsilon = RR(QQ(1)/QQ(2)**20)
    for value, expected in ((bump(p),h), (frame(bump)(p),derivative)):
        assert value.parent() is RR
        assert ask(value > expected-epsilon) is True
        assert ask(value < expected+epsilon) is True
