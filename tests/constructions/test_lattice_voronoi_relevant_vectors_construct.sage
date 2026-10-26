r"""The integer line has exactly the two signed unit Voronoi vectors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_line_voronoi_relevant_vectors_are_signed_units() -> None:
    lattice = Lattices(ZZ)(ZZ^1)
    unit = lattice.basis_vector(0)
    relevant = lattice.voronoi_relevant_vectors()

    assert relevant.cardinality() == cardinal(2)
    assert unit in relevant
    assert -unit in relevant
