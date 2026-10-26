r"""Reflection in a root is the orthogonal involution negating that root."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_root_reflection_negates_the_root() -> None:
    lattice = NamedLattices.A1
    root = lattice.basis_vector(0)
    reflection = lattice.reflection(root)

    assert reflection(root) == -root


def test_a1_root_reflection_is_an_involution() -> None:
    lattice = NamedLattices.A1
    root = lattice.basis_vector(0)
    reflection = lattice.reflection(root)

    assert reflection(reflection(root)) == root
