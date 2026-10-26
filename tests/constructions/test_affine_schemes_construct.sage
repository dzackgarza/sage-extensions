r"""Spectra are affine schemes over their represented base rings."""

from sage_extensions.all import *  # noqa: F401,F403


def test_spec_of_every_commutative_ring_is_affine(commutative_ring) -> None:
    ring = commutative_ring
    spectrum = ring.affine_spectrum()

    assert spectrum in AffineSchemes(ring)
    assert spectrum in Schemes(ring)
    assert spectrum in Schemes(ZZ)
    assert spectrum.is_affine()
    assert spectrum.coordinate_ring() is ring
    assert spectrum.relative_dimension() == 0


def test_basic_open_spelling_belongs_to_affine_schemes_not_only_affine_spaces() -> None:
    scheme = Zmod(6).as_algebra_over(ZZ).affine_spectrum()
    two = scheme.coordinate_algebra()(2)

    assert scheme in AffineSchemes(ZZ)
    assert scheme not in AffineSpaces(ZZ)
    assert scheme.basic_open(two) == scheme.distinguished_open(two)
