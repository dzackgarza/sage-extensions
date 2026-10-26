r"""Affine and projective spaces are quasi-projective over their base."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_spaces_are_quasi_projective(commutative_ring) -> None:
    ring = commutative_ring

    assert AffineSpaces(ring)(2) in Schemes(ring).QuasiProjective()
    assert ProjectiveSpaces(ring)(2) in Schemes(ring).QuasiProjective()
