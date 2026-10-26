"""Homogeneous section spaces pull back contravariantly by projective coordinates."""

from sage_extensions.all import *


def test_coordinate_swap_pulls_homogeneous_sections_by_substitution() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    sections = line.O(3).global_sections()
    ring = sections.homogeneous_coordinate_ring()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    swap = line.projective_morphism_from_coordinates(line, (y, x))
    pullback = sections.pullback_by_projective_automorphism(swap)
    source = sections.section_from_homogeneous_polynomial(x**2 * y)
    expected = sections.section_from_homogeneous_polynomial(y**2 * x)

    assert pullback.domain() is sections
    assert pullback.codomain() is sections
    assert pullback(source) == expected
