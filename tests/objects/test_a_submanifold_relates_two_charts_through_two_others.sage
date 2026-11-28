r"""Two charts of an open submanifold are related through a chain of charts, not only through one.

The coordinate changes of an atlas generate a relation between the charts it carries: two
charts are related by composing the changes along any chain that joins them,
$\varphi_t \circ \varphi_s^{-1} = (\varphi_t \circ \varphi_c^{-1}) \circ (\varphi_c \circ
\varphi_s^{-1})$ applied step by step (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
Ch. 1).  A chart cut on a subset of one ambient chart meets only that chart, so a chart cut
from the north chart and a chart cut from the south one are joined by *two* intermediate
charts; a relation that stops after one hop leaves that pair unrelated, and a family
stated on both cannot be checked.

The specimen is $S^2$ minus the north pole with a chart cut on each stereographic chart.
The change from the north-cut chart to the south-cut chart must be the composition through
the two stereographic charts: a point with north coordinates $(2, 3)$ has south coordinates
$(2/13, 3/13)$.
"""

from sage_extensions.all import *


def _the_submanifold_with_two_cut_charts(north_label, south_label):
    r"""$S^2$ minus the north pole, with a chart cut on the north chart and one cut on the south chart."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    sphere.chart_on_open_subset(
        north_label,
        "x1 x2",
        "U_N",
        (north.coordinate(0) ** 2 + north.coordinate(1) ** 2,), same_coordinates=True,
    )
    sphere.chart_on_open_subset(
        south_label,
        "y1 y2",
        "U_S",
        (south.coordinate(0) ** 2 + south.coordinate(1) ** 2,), same_coordinates=True,
    )
    domain = north.domain()
    return sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))


def test_the_change_between_two_cut_charts_composes_through_two_intermediate_charts() -> None:
    r"""A point with north coordinates $(2, 3)$ has south coordinates $(2/13, 3/13)$, and that is the change from one cut chart to the other.

    Neither cut chart meets the other: each is cut on a subset of one stereographic chart,
    and the ambient atlas states no change between them.  The change is the composition
    through the north chart and the south chart, and its value is what the stereographic
    change says.
    """
    submanifold = _the_submanifold_with_two_cut_charts("CN", "CS")

    transition = submanifold.transition("CN", "CS")
    coordinates = tuple(transition(RR(2), RR(3)))

    assert coordinates[0] == RR(2) / RR(13)
    assert coordinates[1] == RR(3) / RR(13)


def test_the_composed_change_agrees_with_going_through_the_stereographic_charts() -> None:
    r"""The two-hop change is the one-hop change read in sequence: $CS \leftarrow U_S \leftarrow U_N \leftarrow CN$.

    The value is checked against the chain the ambient atlas does state, so the
    composition is the atlas' own change and not a second guess at it.
    """
    submanifold = _the_submanifold_with_two_cut_charts("CN2", "CS2")
    at = (RR(1) / RR(2), RR(-1) / RR(3))

    through = tuple(
        submanifold.transition("U_S", "CS2")(
            *tuple(submanifold.transition("U_N", "U_S")(*tuple(submanifold.transition("CN2", "U_N")(*at))))
        )
    )
    direct = tuple(submanifold.transition("CN2", "CS2")(*at))

    assert direct[0] == through[0]
    assert direct[1] == through[1]
