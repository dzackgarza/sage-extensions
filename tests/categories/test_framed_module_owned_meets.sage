r"""A finitely presented module computed from its presentation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cokernel_of_twice_a_basis_vector_is_Z_mod_2_plus_Z() -> None:
    r"""``coker(Z -> Z^2, r |-> 2 e1) = Z/2 + Z``: torsion of order 2, rank 1."""
    line = Modules(ZZ)(ZZ**1)
    plane = Modules(ZZ)(ZZ**2)
    (r,) = line.basis()
    e1, e2 = plane.basis()

    module = line.Mor(plane)({r: 2 * e1}).cokernel()

    assert module.torsion_submodule().cardinality() == 2
    assert module.vector_space().dimension() == 1
    assert not module.is_free()
    assert module.minimal_number_of_generators() == 2
