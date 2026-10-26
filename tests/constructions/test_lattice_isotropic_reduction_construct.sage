r"""The isotropic coordinate line in (U) has zero isotropic reduction."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_coordinate_line_isotropic_reduction_is_zero() -> None:
    lattice = NamedLattices.U
    line = lattice.subobject_on((lattice.basis_vector(0),))
    reduction = line.isotropic_reduction()

    assert reduction.module_rank() == cardinal(0)
    assert reduction.isotropic_sublattice() is line
