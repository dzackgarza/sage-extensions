r"""Blowing up a rational point of P^2 gives the graph closure in P^2 x P^1."""

from sage_extensions.all import *  # noqa: F401,F403


def test_blowup_of_projective_plane_at_a_rational_point() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 1, 1))
    blowup = ProjectivePointBlowups(QQ)(point)

    assert blowup in ProjectivePointBlowups(QQ)
    assert blowup in ProjectiveSchemes(QQ)
    assert blowup in SmoothSchemes(QQ)
    assert blowup.blowup_point() is point
    assert blowup.blowup_source() is plane
    assert blowup.blowup_morphism().codomain() is plane
    assert blowup.graph_ambient_product() in ProductProjectiveSpaces(QQ)
    assert blowup.graph_relation() in blowup.graph_section_space()
