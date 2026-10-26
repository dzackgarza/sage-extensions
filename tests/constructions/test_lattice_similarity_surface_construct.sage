r"""Lattice similarities are isometries out of the corresponding twist."""

from sage_extensions.all import *  # noqa: F401,F403


def test_scale_one_similarity_mor_is_isometry_from_the_unit_twist() -> None:
    lattice = NamedLattices.U
    mor = lattice.similarity_mor(lattice, ZZ.one())

    assert mor.domain() == lattice.twist(ZZ.one())
    assert mor.codomain() is lattice
    assert mor == lattice.twist(ZZ.one()).Isom(lattice)


def test_lattice_is_similar_to_itself_at_scale_one() -> None:
    lattice = NamedLattices.U

    assert lattice.is_similar(lattice, ZZ.one()) is True
