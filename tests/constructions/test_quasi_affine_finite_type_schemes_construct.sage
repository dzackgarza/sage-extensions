r"""Affine space is quasi-affine of finite type and therefore quasi-projective."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_is_quasi_affine_of_finite_type(commutative_ring) -> None:
    ring = commutative_ring
    plane = AffineSpaces(ring)(2)
    category = Schemes(ring).QuasiAffine().FiniteType()

    assert plane in category
    assert plane in Schemes(ring).QuasiAffine()
    assert plane in Schemes(ring).FiniteType()
    assert plane in Schemes(ring).QuasiProjective()
    assert plane.is_quasi_affine()
    assert plane.is_quasi_projective()
