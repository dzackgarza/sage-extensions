r"""Spec Z has its generic point and one closed point for every rational prime."""

from sage_extensions.all import *  # noqa: F401,F403


def test_spec_z_exposes_closed_and_distinguished_open_sets() -> None:
    spectrum = ZZ.spectrum()
    generic = spectrum.generic_point()
    five = spectrum(ZZ.ideal(5))

    assert spectrum in PrimeSpectra()
    assert spectrum.ring() is ZZ
    assert spectrum.coordinate_ring() is ZZ
    assert spectrum.V(ZZ.ideal(10)) == spectrum.closed_set(ZZ.ideal(10))
    assert spectrum.D(ZZ(5)) == spectrum.distinguished_open(ZZ(5))
    assert five in spectrum.V(ZZ.ideal(10))
    assert five not in spectrum.D(ZZ(5))
    assert generic in spectrum.D(ZZ(5))
    assert spectrum.le(generic, five)
    assert not spectrum.le(five, generic)
    assert spectrum.ringed_space() == ZZ.affine_spectrum()


def test_closed_point_five_of_spec_z_has_the_expected_local_invariants() -> None:
    spectrum = ZZ.spectrum()
    five = spectrum(ZZ.ideal(5))
    generic = spectrum.generic_point()
    residue = five.residue_field()
    residue_map = five.residue_map()

    assert five.ideal() == ZZ.ideal(5)
    assert five.prime_ideal() == ZZ.ideal(5)
    assert five.height() == 1
    assert five.closure_dimension() == 0
    assert five.embedding_dimension() == 1
    assert five.is_regular()
    assert five.is_locally_factorial()
    assert five.local_ring() in LocalRings()
    assert five.stalk() == five.local_ring()
    assert residue.cardinality() == cardinal(5)
    assert residue_map(ZZ(7)) == residue(2)
    assert five.residue_degree() == 1
    assert five.order_of_vanishing(ZZ(25)) == 2
    assert five.local_length(ZZ.ideal(25)) == 2
    assert five.generic_local_length(ZZ.ideal(5)) == 1
    assert generic.specializes_to(five)


def test_spectrum_of_z_mod_six_has_two_points() -> None:
    assert Zmod(6).spectrum().cardinality() == cardinal(2)

