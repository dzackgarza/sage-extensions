r"""A root reflection of the hyperbolic plane can have trivial rational spinor norm."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_root_reflection_lies_in_spinor_kernel() -> None:
    lattice = NamedLattices.U
    first = lattice.basis_vector(0)
    second = lattice.basis_vector(1)
    reflection = lattice.reflection(first - second)

    assert reflection in lattice.spinor_kernel()
