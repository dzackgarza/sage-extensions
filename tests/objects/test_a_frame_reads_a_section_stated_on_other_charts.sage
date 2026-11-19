r"""The inverse of a trivialization reads every section, including one stated on charts the frame is not.

A frame $E$ of a rank-one bundle states $C^\infty(M) \to \Gamma(E)$, $a \mapsto aE$, and its
inverse sends $V$ to the function $a$ with $V = aE$ (Lee, *Introduction to Smooth Manifolds*,
2nd ed., Ch. 10, local frames and local trivializations).  A section is fixed by its
components on any cover, and its components on another chart are the transported ones
(Lee, Ch. 3, the change of coordinates for tangent vectors), so where a
section is stated does not limit which sections the inverse reads.

The specimen is the circle with one more chart $W = U_N \setminus \{x = 1\}$, coordinate
$x$, and the frame $E_N = (1 + x^2)\partial_x$, $E_S = -(1 + y^2)\partial_y$.  The section
$V = hE$ with $h = 2x/(1 + x^2)$ on $U_N$, $2y/(1 + y^2)$ on $U_S$, has components $2x$ on
$U_N$ and on $W$ and $-2y$ on $U_S$ (since $\partial_x = -y^2\partial_y$ under $y = 1/x$), and
its coordinate is $h$: $4/5$ at $x = 2$ and at $y = 1/2$.
"""

from sage_extensions.all import *


def _the_circle_with_a_third_chart(label):
    r"""$S^1$ with the chart $W$, labelled ``label``, cut on $U_N$, and its three charts."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    circle.chart_on_open_subset(
        label, "x1", "U_N", (north.coordinate(0) - north.function_ring().one(),)
    )
    return circle, north, circle.atlas()["U_S"], circle.atlas()[label]


def _the_frame(sections, north, south, *extra):
    components = {
        "U_N": (north.function_ring().one() + north.coordinate(0) ** 2,),
        "U_S": (-(south.function_ring().one() + south.coordinate(0) ** 2),),
    }
    for chart in extra:
        components[chart.label()] = (
            chart.function_ring().one() + chart.coordinate(0) ** 2,
        )
    return sections.section(components)


def test_a_section_stated_on_a_chart_outside_the_frame_is_read_in_the_frame() -> None:
    r"""The frame is stated on $U_N, U_S$ and $V$ also on $W$; its coordinate is $h$, $4/5$ at $x = 2$."""
    circle, north, south, cut = _the_circle_with_a_third_chart("W_A")
    sections = circle.tangent_bundle().sections()
    frame = _the_frame(sections, north, south)
    section = sections.section(
        {
            "U_N": (2 * north.coordinate(0),),
            "U_S": (-2 * south.coordinate(0),),
            cut.label(): (2 * cut.coordinate(0),),
        }
    )

    coordinate = sections.trivialized_by(frame).trivialization().inverse(section)

    assert coordinate.parent() is circle.smooth_functions()
    assert coordinate(circle.point((2,), "U_N")) == RR(4) / RR(5)
    assert coordinate(circle.point((RR(1) / RR(2),), "U_S")) == RR(4) / RR(5)


def test_a_frame_on_three_charts_reads_a_section_stated_on_two() -> None:
    r"""The frame is stated on $U_N, U_S, W$ and $V$ on $U_N, U_S$; at the point $x = 3$ of $W$ the coordinate is $h(3) = 3/5$."""
    circle, north, south, cut = _the_circle_with_a_third_chart("W_B")
    sections = circle.tangent_bundle().sections()
    frame = _the_frame(sections, north, south, cut)
    section = sections.section(
        {
            "U_N": (2 * north.coordinate(0),),
            "U_S": (-2 * south.coordinate(0),),
        }
    )

    trivialization = sections.trivialized_by(frame).trivialization()
    coordinate = trivialization.inverse(section)

    assert coordinate(circle.point((3,), cut.label())) == RR(3) / RR(5)
    assert trivialization.forward(coordinate) == section
