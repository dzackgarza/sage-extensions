r"""A lattice vector exposes the rank-one lattice subobject that it spans."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_basis_vector_spans_rank_one_lattice_subobject() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    line = e.sublattice()

    assert line.ambient_lattice() is lattice
    assert line.module_rank() == cardinal(1)
    assert line.inclusion()(line.module_generator(0)) == e


def test_vector_sublattice_matches_lattice_subobject_constructor() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert e.sublattice() == lattice.subobject_on((e,))
