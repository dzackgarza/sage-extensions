r"""A hyperbolic-plane root reflection can preserve the real spinor component."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_root_reflection_lies_in_o_plus() -> None:
    lattice = NamedLattices.U
    first = lattice.basis_vector(0)
    second = lattice.basis_vector(1)
    reflection = lattice.reflection(first - second)

    assert reflection in lattice.O_plus()
