r"""Projective space exposes its standard projective fan."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_has_the_standard_three_ray_fan() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    fan = plane.fan()

    assert fan.dimension() == 2
    assert fan.rays().cardinality() == cardinal(3)
    assert fan.maximal_cones().cardinality() == cardinal(3)
