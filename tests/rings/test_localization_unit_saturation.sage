from sage_extensions.all import *


def test_localization_units_use_ideal_saturation_over_multivariate_polynomials() -> None:
    ring = QQ.polynomial_ring(("x", "y"))
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    localized = ring.localization(x)
    localization = localized.localization_map()

    inverted = localization(x)
    uninverted = localization(y)

    assert inverted.is_unit()
    assert inverted * inverted.inverse_of_unit() == localized.one()
    assert not uninverted.is_unit()


def test_localizing_at_a_product_makes_each_factor_a_unit() -> None:
    ring = QQ.polynomial_ring(("s0", "s1"))
    s0 = ring.algebra_generator("s0")
    s1 = ring.algebra_generator("s1")
    localized = ring.localization(s0 * s1)
    localization = localized.localization_map()

    for numerator in (s0, s1, s0**2, s0 * s1):
        unit = localization(numerator)
        assert unit.is_unit()
        assert unit * unit.inverse_of_unit() == localized.one()

    assert not localization(s0 + s1).is_unit()



def test_pid_localization_units_use_owned_principal_saturation_fallback() -> None:
    localized = ZZ.localization(ZZ(6))
    localization = localized.localization_map()

    for numerator in (ZZ(2), ZZ(3), ZZ(6), ZZ(12), ZZ(18)):
        assert localization(numerator).is_unit()

    for numerator in (ZZ(5), ZZ(10), ZZ(15)):
        assert not localization(numerator).is_unit()

    assert ZZ.ideal(72).ideal_saturation(ZZ.ideal(6)) == ZZ.ideal(1)
    assert ZZ.ideal(20).ideal_saturation(ZZ.ideal(6)) == ZZ.ideal(5)
    assert ZZ.ideal(10).colon(ZZ.ideal(5)) == ZZ.ideal(2)
    assert ZZ.ideal(0).colon(ZZ.ideal(5)) == ZZ.ideal(0)
    assert ZZ.ideal(0).colon(ZZ.ideal(0)) == ZZ.ideal(1)
