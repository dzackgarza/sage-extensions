r"""A section of $TS^2$ pulls back along a constant map $S^1 \to S^2$ to a rank-two section over the circle.

The pullback of a section $s$ of $E \to M$ along $f: N \to M$ is $q \mapsto s(f(q))$, a
section of $f^*E$ (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10, the pullback
bundle).  Its rank is the rank of $E$, two for $TS^2$, while the circle has dimension one:
a section of $f^*TS^2$ is no vector field on the circle.

The specimen is the constant map at the point with north coordinates $(1, 0)$, stated on
both charts of the circle, and the Euler field $s$ of $S^2$: $(x_1, x_2)$ on $U_N$ and
$(-y_1, -y_2)$ on $U_S$.  The pulled-back section is the constant $(1, 0)$ on both charts
of the circle, read in the frame of the sphere's north chart.
"""

from sage_extensions.all import *


def _the_constant_map_and_the_euler_field():
    r"""$S^1$, $S^2$, the constant map at $(1, 0)$ in the north chart, and the Euler field."""
    circle = SmoothManifolds().sphere(1)
    sphere = SmoothManifolds().sphere(2)
    sphere_north = sphere.atlas()["U_N"]
    sphere_south = sphere.atlas()["U_S"]

    def at_the_point(label):
        ring = circle.atlas()[label].function_ring()
        return (ring.one(), ring.zero())

    mapping = circle.Mor(sphere)(
        {
            ("U_N", "U_N"): at_the_point("U_N"),
            ("U_S", "U_N"): at_the_point("U_S"),
        }
    )
    euler = sphere.tangent_bundle().sections().section(
        {
            "U_N": (sphere_north.coordinate(0), sphere_north.coordinate(1)),
            "U_S": (-sphere_south.coordinate(0), -sphere_south.coordinate(1)),
        }
    )
    return circle, sphere.tangent_bundle().pullback_along(mapping), euler


def test_the_pullback_of_the_euler_field_is_its_value_at_the_point() -> None:
    r"""$f^*s$ is the constant $(1, 0)$ on both charts: the Euler field's value at $(1, 0)$."""
    circle, pulled, euler = _the_constant_map_and_the_euler_field()

    section = pulled.sections().pullback_of(euler)

    assert section.parent() is pulled.sections()
    at_north = circle.atlas()["U_N"].domain()((3,))
    at_south = circle.atlas()["U_S"].domain()((RR(1) / RR(3),))
    assert section.components()["U_N"][0](at_north) == RR(1)
    assert section.components()["U_N"][1](at_north) == RR(0)
    assert section.components()["U_S"][0](at_south) == RR(1)
    assert section.components()["U_S"][1](at_south) == RR(0)


def test_the_sum_of_two_pulled_back_sections_is_a_rank_two_section() -> None:
    r"""$f^*s + f^*s$ is the constant $(2, 0)$ on the circle."""
    circle, pulled, euler = _the_constant_map_and_the_euler_field()
    section = pulled.sections().pullback_of(euler)

    doubled = section + section

    at_north = circle.atlas()["U_N"].domain()((3,))
    assert doubled.components()["U_N"][0](at_north) == RR(2)
    assert doubled.components()["U_N"][1](at_north) == RR(0)
