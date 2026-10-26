r"""Homogeneous section spaces convert between basis sections and homogeneous polynomials."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_basis_section_round_trips_through_its_polynomial() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    sections = plane.O(2).homogeneous_polynomial_sections()
    monomial = next(iter(sections.module_generating_set()))
    basis_section = sections.module_generator(monomial)

    assert sum(sections.monomial_exponents(monomial)) == 2
    assert sections.homogeneous_polynomial(basis_section) == monomial
    assert sections.section_from_homogeneous_polynomial(monomial) == basis_section


def test_coordinate_swap_pulls_sections_by_substitution() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    sections = line.O(3).homogeneous_polynomial_sections()
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
