r"""Quadrics on P^2 form the six-dimensional degree-two homogeneous section space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_homogeneous_sections_on_projective_plane() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    sections = plane.O(2).homogeneous_polynomial_sections()

    assert sections in HomogeneousPolynomialSectionSpaces(QQ)
    assert sections.section_scheme() is plane
    assert sections.homogeneous_degree() == 2
    assert sections.dimension() == 6
    assert sections.homogeneous_coordinate_ring().algebra_generating_set().cardinality() == cardinal(3)
