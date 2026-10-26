r"""The hyperbolic plane has two primitive isotropic coordinate lines."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_has_two_primitive_isotropic_lines() -> None:
    lattice = NamedLattices.U
    first = lattice.subobject_on((lattice.basis_vector(0),))
    second = lattice.subobject_on((lattice.basis_vector(1),))
    lines = lattice.primitive_isotropic_sublattices(rank=1)

    assert first in lines
    assert second in lines
