r"""On the two-chart circle, a derivation of $C^\infty(S^1)$ is the section it differentiates along.

$\Gamma(TM) \to \operatorname{Der} C^\infty(M)$, $V \mapsto (f \mapsto Vf)$, is an isomorphism
(Lee, *Introduction to Smooth Manifolds*, 2nd ed., Prop. 8.15).  The section is read on the
functions $H_N x$ and $H_S y$, $H$ the bumps of the two stereographic charts (Lee,
Lemma 2.22 and Prop. 2.25): $H_N = 1$ on $|x| < 2$ and $H_S = 1$ on $|y| < 2$, and these
balls cover $S^1$, so in each chart some $d(H x)$ is $dx$ and the Jacobian has rank one.

The specimen is the frame $E$ with $E_N = (1+x^2)\partial_x$, $E_S = -(1+y^2)\partial_y$
(these agree, since $\partial_x = -y^2 \partial_y$ under $y = 1/x$), and the derivation
$f \mapsto E(f)$: the recovered section has the components $1 + x^2$ and $-(1 + y^2)$, so
$5$ at $x = 2$ and $-5/4$ at $y = 1/2$.
"""

from sage_extensions.all import *


def _the_circle_and_its_frame():
    r"""$S^1$, its sections, and the frame $E$ stated on both stereographic charts."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    sections = circle.tangent_bundle().sections()
    frame = sections.section(
        {
            "U_N": (north.function_ring().one() + north.coordinate(0) ** 2,),
            "U_S": (-(south.function_ring().one() + south.coordinate(0) ** 2),),
        }
    )
    return circle, north, south, sections, frame


def test_the_derivation_along_the_frame_of_the_circle_gives_back_the_frame() -> None:
    r"""$f \mapsto E(f)$ is read back as $E$: $1 + x^2$ on $U_N$ and $-(1 + y^2)$ on $U_S$."""
    _circle, north, south, sections, frame = _the_circle_and_its_frame()

    recovered = sections.from_derivation(lambda function: frame(function))

    assert recovered.parent() is sections
    assert recovered.components()["U_N"][0](north.domain()((2,))) == RR(5)
    assert recovered.components()["U_S"][0](south.domain()((RR(1) / RR(2),))) == RR(-5) / RR(4)
    assert recovered == frame


def test_a_derivation_that_is_twice_the_frame_is_read_as_twice_the_frame() -> None:
    r"""$f \mapsto 2E(f)$ is the section $2E$: $2(1 + x^2)$, which is $10$ at $x = 2$."""
    _circle, north, _south, sections, frame = _the_circle_and_its_frame()

    recovered = sections.from_derivation(lambda function: frame(function) + frame(function))

    assert recovered.components()["U_N"][0](north.domain()((2,))) == RR(10)
    assert recovered == frame + frame


def test_the_bracket_of_two_sections_is_read_as_the_section_it_is() -> None:
    r"""$D f = E(gEf) - gE(Ef)$ is a derivation not presented as a section; it is the section $E(g)E$.

    $[E, gE] = E(g)E$ (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Prop. 8.28 (d)
    reads $[X, gY] = g[X,Y] + (Xg)Y$, with $[E, E] = 0$).  With $g = u_1 = 2x/(1+x^2)$,
    $E(g) = 2(1-x^2)/(1+x^2)$ on $U_N$, so the component is $2(1-x^2)$: $-6$ at $x = 2$.
    On $U_S$ it is $2(1-y^2)$, $3/2$ at $y = 1/2$, which is $-6 \cdot (-y^2)$ at $y = 1/2$.
    """
    circle, north, south, sections, frame = _the_circle_and_its_frame()
    x = north.coordinate(0)
    y = south.coordinate(0)
    g = circle.smooth_function(
        {
            "U_N": north.section_ratio(2 * x, north.function_ring().one() + x**2),
            "U_S": south.section_ratio(2 * y, south.function_ring().one() + y**2),
        }
    )
    scaled = g * frame

    recovered = sections.from_derivation(
        lambda function: frame(scaled(function)) - g * frame(frame(function))
    )

    assert recovered.components()["U_N"][0](north.domain()((2,))) == RR(-6)
    assert recovered.components()["U_S"][0](south.domain()((RR(1) / RR(2),))) == RR(3) / RR(2)
