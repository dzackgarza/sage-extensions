r"""Affine space is quasi-affine over its base."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_space_is_quasi_affine(commutative_ring) -> None:
    ring = commutative_ring

    assert AffineSpaces(ring)(2) in Schemes(ring).QuasiAffine()
