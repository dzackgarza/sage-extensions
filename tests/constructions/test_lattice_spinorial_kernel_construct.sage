r"""The spinorial kernel is the determinant-one part of the rational spinor kernel."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_root_reflection_is_not_spinorial() -> None:
    lattice = NamedLattices.U
    first = lattice.basis_vector(0)
    second = lattice.basis_vector(1)
    reflection = lattice.reflection(first - second)

    assert reflection in lattice.spinor_kernel()
    assert reflection not in lattice.spinorial_kernel()
    assert lattice.identity_morphism() in lattice.spinorial_kernel()
