r"""Primitive lattice vectors expose their primitive dual and discriminant class."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_basis_vector_primitive_dual_delegates_to_lattice_owner() -> None:
    lattice = Lattices(ZZ)("A2")
    vector = lattice.basis_vector(0)

    assert vector.primitive_dual() == lattice.primitive_dual(vector)


def test_a2_basis_vector_discriminant_class_delegates_to_lattice_owner() -> None:
    lattice = Lattices(ZZ)("A2")
    vector = lattice.basis_vector(0)

    assert vector.divided_discriminant_class() == lattice.divided_discriminant_class(vector)
    assert vector.discriminant_class() == vector.divided_discriminant_class()
