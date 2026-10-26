r"""Fraction fields as localizations at the nonzero elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_fraction_field_of_the_integers_is_the_rationals() -> None:
    r"""Frac(Z) = (Z - 0)^{-1} Z = Q, and the canonical map Z -> Q sends n to n
    (Atiyah-Macdonald ch. 3); in (Z - 0)^{-1} Z, 6/4 = 3/2 because 6*2 = 3*4."""
    to_rationals = ZZ.fraction_field_map()
    localization = ZZ.fraction_field_localization()

    assert ZZ.fraction_field() is QQ
    assert to_rationals.domain() is ZZ
    assert to_rationals.codomain() is QQ
    assert to_rationals(ZZ(6)) / to_rationals(ZZ(4)) == QQ(3) / 2
    assert localization.fraction(ZZ(6), ZZ(4)) == localization.fraction(ZZ(3), ZZ(2))
    assert localization.fraction(ZZ(1), ZZ(2)) != localization.fraction(ZZ(1), ZZ(3))


def test_the_fraction_field_of_a_prime_localization_of_the_integers_is_the_rationals() -> None:
    r"""Z_(3) = (Z - 3Z)^{-1} Z is a domain whose fraction field is Q, and the
    canonical map Z_(3) -> Q sends the fraction 1/2 to 1/2 (Mathlib
    IsFractionRing.isFractionRing_of_isDomain_of_isLocalization)."""
    at_three = ZZ.spectrum()(3).local_ring()
    to_rationals = at_three.fraction_field_map()

    assert at_three.fraction_field() is QQ
    assert to_rationals.domain() is at_three
    assert to_rationals.codomain() is QQ
    assert to_rationals(at_three.fraction(ZZ(1), ZZ(2))) == QQ(1) / 2
    assert to_rationals(at_three.fraction(ZZ(6), ZZ(4))) == QQ(3) / 2


def test_fraction_fields_of_countable_polynomial_domains_remain_countable() -> None:
    domains = (
        GF(5).polynomial_ring("t"),
        QQ.polynomial_ring("x"),
    )

    for domain in domains:
        field = domain.fraction_field()
        assert field.cardinality() == aleph0
        assert field.regular_module().cardinality() == aleph0

    polynomial_ring = domains[1]
    field = polynomial_ring.fraction_field()
    inclusion = polynomial_ring.fraction_field_map()
    x = polynomial_ring.algebra_generator("x")
    assert inclusion.domain() is polynomial_ring
    assert inclusion.codomain() is field
    assert field in OwnedRings().Division().Commutative()
    assert inclusion(x) / inclusion(x) == field.one()
    assert field.regular_module().base_ring() is field


def test_localizing_a_free_module_then_passing_to_q_is_the_base_change_to_q() -> None:
    r"""For M = Z^2 and S = Z - 0, S^{-1}M = M (x)_Z S^{-1}Z = M (x)_Z Q = Q^2
    (Atiyah-Macdonald 3.5)."""
    module = ZZ.free_module(2)
    localized = ZZ.fraction_field_localization().localization_functor()(module)
    direct = Modules(ZZ).scalar_extension(ZZ.fraction_field_map())(module)

    assert ZZ.fraction_field() is QQ
    assert localized.module_rank() == 2
    assert direct in VectorSpaces(QQ)
    assert direct.module_rank() == 2
    half_e = direct.scalar_multiple(QQ(1) / 2, direct.module_generator(0))
    assert 2 * half_e == direct.module_generator(0)


def test_selected_and_prime_localizations_do_not_collapse_to_the_fraction_field() -> None:
    at_two = ZZ.localization(ZZ(2))
    at_three = ZZ.spectrum()(3).local_ring()
    fractions = ZZ.fraction_field_localization()

    assert at_two is not fractions
    assert at_three is not fractions
    assert at_two(ZZ(2)).is_unit()
    assert not at_two(ZZ(3)).is_unit()
    assert at_three(ZZ(2)).is_unit()
    assert not at_three(ZZ(3)).is_unit()
    assert fractions(ZZ(2)).is_unit()
    assert fractions(ZZ(3)).is_unit()
