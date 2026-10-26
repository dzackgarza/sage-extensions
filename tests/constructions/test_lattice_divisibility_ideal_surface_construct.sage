r"""A lattice computes the divisibility ideal from pairings with its generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_diagonal_lattice_owner_computes_divisibility_ideal() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -6]])
    e0 = lattice.basis_vector(0)
    e1 = lattice.basis_vector(1)

    assert lattice.divisibility_ideal(e0) == ZZ.ideal(2)
    assert lattice.divisibility_ideal(e1) == ZZ.ideal(6)


def test_lattice_divisibility_ideal_is_generated_by_generator_pairings() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -6]])
    vector = lattice.basis_vector(0) + lattice.basis_vector(1)
    pairings = lattice.generator_pairings(vector)

    assert lattice.divisibility_ideal(vector) == ZZ.ideal(*pairings.values())
