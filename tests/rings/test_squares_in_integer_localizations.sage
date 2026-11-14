r"""Squareness belongs to the selected integer localization, including the rational field."""

from sage_extensions.all import *


def test_rational_squares_are_decided_independently_of_fraction_presentation():
    for numerator, denominator, expected in ((0, 1, True), (4, 9, True), (8, 18, True), (-4, 9, False), (2, 9, False), (2**160, 3**80, True)):
        value = QQ(numerator) / QQ(denominator)
        assert value.is_square() is expected


def test_squares_in_z_one_half_use_admitted_root_denominators():
    ring = ZZ.localization(ZZ(2))
    for numerator, denominator, expected in ((9, 4, True), (18, 8, True), (3, 4, False), (-1, 4, False), (0, 8, True)):
        value = ring.fraction(ZZ(numerator), ZZ(denominator))
        assert value.is_square() is expected


def test_squares_in_the_local_ring_at_three_use_its_selected_denominators():
    ring = ZZ.spectrum()(3).local_ring()
    assert ring.fraction(ZZ(4), ZZ(25)).is_square() is True
    assert ring.fraction(ZZ(3), ZZ(4)).is_square() is False
    assert ring.fraction(ZZ(-1), ZZ(4)).is_square() is False
