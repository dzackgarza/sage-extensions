r"""A hyperbolic-plane root reflection has trivial default rational spinor norm."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_root_reflection_has_trivial_spinor_norm() -> None:
    lattice = NamedLattices.U
    first = lattice.basis_vector(0)
    second = lattice.basis_vector(1)
    reflection = lattice.reflection(first - second)

    assert lattice.spinor_norm()(reflection) == QQ.square_class_group().one()
