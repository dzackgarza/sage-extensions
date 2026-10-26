r"""Owned rings form adic formal spectra from ideals of definition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_adic_formal_spectrum_remembers_ring_and_ideal() -> None:
    formal = ZZ.formal_spectrum(ZZ.ideal(3))

    assert formal.source_ring() is ZZ
    assert formal.ideal_of_definition() == ZZ.ideal(3)
    assert formal.thickening_ring(2).cardinality() == 9
