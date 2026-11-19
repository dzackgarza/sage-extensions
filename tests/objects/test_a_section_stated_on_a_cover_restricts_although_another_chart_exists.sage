r"""A section stated on a cover restricts to an open submanifold that carries one more chart.

A section is fixed by its components on a cover of the manifold, and its restriction to an
open submanifold is fixed by the components it has there (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 8).  The open submanifold carries the ambient charts read on it,
and a chart another construction registered on the ambient manifold is one of them; the
restriction must be read off the charts the section states, not off every chart the
submanifold happens to carry, or a section the library admits cannot be restricted at all
because an unrelated chart exists.

The specimen is the sphere: a vector field stated on the two stereographic charts -- which
cover it -- restricted to the complement of the north pole, whose atlas also carries a
chart cut on the north chart.
"""

from sage_extensions.all import *


def _the_sphere_with_a_cut_chart(label):
    r"""$S^2$, its two stereographic charts, a chart cut on the north one, and the complement of the pole."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    sphere.chart_on_open_subset(
        label, "x1 x2", "U_N", (north.coordinate(0) ** 2 + north.coordinate(1) ** 2,)
    )
    domain = north.domain()
    return sphere, sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))


def test_a_section_stated_on_a_cover_restricts_though_the_submanifold_carries_more_charts() -> None:
    r"""The restriction takes the components the section has on the charts it is stated on, and its values are the section's.

    The field is the Euler field: $(x_1, x_2)$ on the north chart and $(-y_1, -y_2)$ on the
    south one, since $a_S(y(x)) = a_N(x)\,dy/dx$ for $y = x/\lvert x\rvert^2$ gives
    $-y_j$.  The section is stated on the north and south charts, which cover the sphere; the
    submanifold's atlas also carries a chart cut on the north chart, which lies inside the
    north chart and so adds no point the section leaves undecided.
    """
    sphere, submanifold = _the_sphere_with_a_cut_chart("RESTRICT_A")
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    section = sphere.tangent_bundle().sections().section(
        {
            "U_N": (north.coordinate(0), north.coordinate(1)),
            "U_S": (-south.coordinate(0), -south.coordinate(1)),
        }
    )
    inclusion = sphere.open_submanifold_inclusion(submanifold)
    restricted = sphere.tangent_bundle().sections().restrict(section, inclusion)
    at_south = submanifold.atlas()["U_S"].domain()((RR(2) / RR(13), RR(3) / RR(13)))

    assert restricted.parent().vector_bundle().base_manifold() is submanifold
    at_north = submanifold.atlas()["U_N"].domain()((2, 3))
    assert restricted.components()["U_N"][0](at_north) == RR(2)
    assert restricted.components()["U_N"][1](at_north) == RR(3)
    assert section.components()["U_N"][0](at_north) == RR(2)
    assert restricted.components()["U_S"][0](at_south) == RR(-2) / RR(13)
    assert restricted.components()["U_S"][1](at_south) == RR(-3) / RR(13)


def test_the_chart_that_adds_nothing_is_not_required_of_the_section() -> None:
    r"""The cut chart lies inside the north chart, so the section says nothing about it and the restriction does not ask it to."""
    sphere, submanifold = _the_sphere_with_a_cut_chart("RESTRICT_B")
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    section = sphere.tangent_bundle().sections().section(
        {
            "U_N": (north.coordinate(0), north.coordinate(1)),
            "U_S": (-south.coordinate(0), -south.coordinate(1)),
        }
    )

    restricted = sphere.tangent_bundle().sections().restrict(
        section, sphere.open_submanifold_inclusion(submanifold)
    )

    assert "RESTRICT_B" in submanifold.chart_labels()
    assert tuple(restricted.components()) == ("U_N", "U_S")
