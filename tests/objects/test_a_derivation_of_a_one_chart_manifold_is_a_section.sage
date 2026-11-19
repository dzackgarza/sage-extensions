r"""On a manifold presented by one chart, a derivation of $C^\infty(M)$ is the section it differentiates along.

A vector field is a derivation of the smooth functions, and every derivation of them is the
derivative along a unique vector field: $\Gamma(TM) \to \operatorname{Der} C^\infty(M)$,
$V \mapsto (f \mapsto Vf)$, is an isomorphism of $C^\infty(M)$-modules (Lee, *Introduction to
Smooth Manifolds*, 2nd ed., Prop. 8.15).  The section is recovered from the derivation by
evaluating it on the coordinates, which are functions on $M$ when one chart presents it.

The specimen is the plane's tangent bundle: the Euler field acts as a derivation, and
recovering the section from that derivation gives the field back.
"""

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its one chart, the two coordinates, and the Euler field."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    sections = plane.tangent_bundle().sections()
    return plane, chart, x, y, sections, sections.section({"U": (x, y)})


def test_a_derivation_of_the_one_chart_manifold_gives_back_the_section_it_came_from() -> None:
    r"""$V \mapsto (f \mapsto Vf) \mapsto W$ with $W = V$: the Euler field's components are its values on the coordinates.

    $Vx = x$ and $Vy = y$ for the Euler field, so the recovered section has components
    $(x, y)$ and is the field itself.
    """
    plane, _chart, x, y, sections, euler = _the_plane()

    recovered = sections.from_derivation(euler)

    at = plane((3, 4))
    assert recovered.components()["U"][0](at) == RR(3)
    assert recovered.components()["U"][1](at) == RR(4)
    assert recovered.components()["U"][0](at) == x(at)
    assert recovered.components()["U"][1](at) == y(at)
    assert recovered == euler


def test_a_derivation_is_read_on_the_coordinates_of_the_chart() -> None:
    r"""The field $\partial_x$ takes $x$ to $1$ and $y$ to $0$, and that is the section recovered from it."""
    plane, chart, _x, _y, sections, _euler = _the_plane()
    ring = chart.function_ring()
    partial_x = sections.section({"U": (ring.one(), ring.zero())})

    recovered = sections.from_derivation(partial_x)

    at = plane((5, 6))
    assert recovered.components()["U"][0](at) == RR(1)
    assert recovered.components()["U"][1](at) == RR(0)
    assert recovered == partial_x

