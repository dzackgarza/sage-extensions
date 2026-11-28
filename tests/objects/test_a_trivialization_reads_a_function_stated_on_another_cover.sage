r"""The trivialization multiplies a function by the frame whatever cover the function is stated on.

$\Gamma(E)$ is a module over $C^\infty(M)$, so $a \mapsto aE$ is defined for every smooth
function, and a function is fixed by its expression on any cover of $M$ (Lee, *Introduction
to Smooth Manifolds*, 2nd ed., Ch. 2 and Ch. 10).  A frame is stated on the charts it is
stated on, and the product needs the function's expression *there*: when the function is
written on another cover, its expression is read on the frame's charts through the
coordinate change the atlas states.

The specimen is the plane with a chart cut by $x^2+1$, which vanishes nowhere: the frame is
stated on the plane's own chart, and the function on the cut chart, which is the same open
set.
"""

from sage_extensions.all import *


def _the_plane_with_a_redundant_cut():
    r"""The plane, its chart, a chart cut by $x^2+1$, and the tangent bundle's sections."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    cut = plane.chart_on_open_subset("V1", "x y", "U", (x**2 + 1,), same_coordinates=True)
    return plane, chart, cut


def test_the_frame_multiplies_a_function_stated_on_the_cut_chart() -> None:
    r"""$aE$ for $a$ stated on the cut chart and $E$ the coordinate frame of the plane's chart.

    The function's expression on the cut chart is the one the product needs, read on the
    frame's chart through the identity coordinate change; the section's component is that
    function times the frame's component.
    """
    plane, chart, cut = _the_plane_with_a_redundant_cut()
    sections = plane.tangent_bundle().sections()
    frame = (
        sections.coordinate_vector_field(chart, 0),
        sections.coordinate_vector_field(chart, 1),
    )
    trivialization = sections.trivialized_by(frame).trivialization()
    a = plane.smooth_function({"V1": cut.coordinate(0) + cut.coordinate(1)})
    b = plane.smooth_function({"V1": cut.coordinate(0) + (-cut.coordinate(1))})

    section = trivialization.forward((a, b))

    at = plane((2, 3))
    assert section.components()["U"][0](at) == RR(5)
    assert section.components()["U"][1](at) == RR(-1)


def test_the_inverse_reads_the_section_back_into_the_same_functions() -> None:
    r"""$a \mapsto aE \mapsto a$ on the functions stated on the cut chart.

    The inverse reads the section's components against the frame's, on the charts both are
    stated on, and the pair it returns takes at a point the values the pair had there.
    """
    plane, chart, cut = _the_plane_with_a_redundant_cut()
    sections = plane.tangent_bundle().sections()
    frame = (
        sections.coordinate_vector_field(chart, 0),
        sections.coordinate_vector_field(chart, 1),
    )
    trivialization = sections.trivialized_by(frame).trivialization()
    a = plane.smooth_function({"V1": cut.coordinate(0) + cut.coordinate(1)})
    b = plane.smooth_function({"V1": cut.coordinate(0) + (-cut.coordinate(1))})
    at = plane((2, 3))

    back = trivialization.inverse(trivialization.forward((a, b)))

    assert back[0](at) == a(at)
    assert back[1](at) == b(at)
