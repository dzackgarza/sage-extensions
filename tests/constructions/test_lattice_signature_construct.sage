r"""The hyperbolic plane has inertia pair ((1,1))."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_signature_is_one_one() -> None:
    lattice = NamedLattices.U

    assert lattice.signature() == signature_pair(1, 1)
