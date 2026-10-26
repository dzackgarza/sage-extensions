r"""The coordinate isotropic line of the hyperbolic plane lies in its rank-one isotropic locus."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_coordinate_line_lies_in_isotropic_sublattice_locus() -> None:
    lattice = NamedLattices.U
    line = lattice.subobject_on((lattice.basis_vector(0),))

    assert line in lattice.isotropic_sublattice_locus(1)
