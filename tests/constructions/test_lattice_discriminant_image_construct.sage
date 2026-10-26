r"""A unimodular lattice has trivial discriminant image."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_discriminant_image_is_trivial() -> None:
    lattice = NamedLattices.U

    assert lattice.discriminant_image().cardinality() == cardinal(1)
