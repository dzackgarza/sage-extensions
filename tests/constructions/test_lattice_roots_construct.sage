r"""The rank-one root lattice has exactly its two signed roots."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_has_exactly_two_roots() -> None:
    lattice = NamedLattices.A1
    root = lattice.basis_vector(0)
    roots = lattice.roots()

    assert roots.cardinality() == cardinal(2)
    assert root in roots
    assert -root in roots


def test_a1_roots_of_minus_two_are_all_roots() -> None:
    lattice = NamedLattices.A1

    assert lattice.roots_of_square(-2) == lattice.roots()
