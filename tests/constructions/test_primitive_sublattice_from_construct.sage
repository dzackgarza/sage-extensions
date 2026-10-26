r"""Primitive sublattice construction saturates the generated lattice span."""

from sage_extensions.all import *  # noqa: F401,F403


def test_primitive_sublattice_generated_by_twice_a_basis_vector_is_the_basis_line() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    e = lattice.basis_vector(0)
    primitive = lattice.primitive_sublattice_from((2 * e,))

    assert primitive.ambient_lattice() is lattice
    assert primitive.module_rank() == cardinal(1)
    assert primitive.inclusion()(primitive.module_generator(0)) == e


def test_primitive_sublattice_from_matches_saturated_sublattice_construction() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    e = lattice.basis_vector(0)

    assert lattice.primitive_sublattice_from((2 * e,)) == lattice.sublattice_from(
        (2 * e,),
        saturate=True,
    )
