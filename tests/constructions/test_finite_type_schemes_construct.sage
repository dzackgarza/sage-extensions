r"""Affine and projective spaces are finite type over their base rings."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_spaces_are_finite_type(commutative_ring) -> None:
    ring = commutative_ring

    assert AffineSpaces(ring)(2) in Schemes(ring).FiniteType()
    assert ProjectiveSpaces(ring)(2) in Schemes(ring).FiniteType()
