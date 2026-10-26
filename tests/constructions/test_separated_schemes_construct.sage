r"""Affine and projective spaces are separated over their base rings."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_spaces_are_separated(commutative_ring) -> None:
    ring = commutative_ring

    assert AffineSpaces(ring)(2) in Schemes(ring).Separated()
    assert ProjectiveSpaces(ring)(2) in Schemes(ring).Separated()
