r"""An affine spectrum is integral exactly when its coordinate ring is a domain."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_spectrum_is_integral_exactly_for_domains(commutative_ring) -> None:
    ring = commutative_ring
    spectrum = ring.affine_spectrum()

    assert (spectrum in IntegralSchemes(ring)) == (ring in IntegralDomains())
