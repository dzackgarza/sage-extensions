r"""Localized modules as fractions with a retained localization map.

Localizing ``ZZ^2`` at the prime ``(5)`` produces ``ZZ_(5)^2``.  Its elements
are fractions ``m/s`` with ``s`` outside ``(5)``, and the canonical unit sends a
numerator to the same fraction with denominator one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _localized_plane_at_five():
    module = ZZ.free_module(2)
    point = ZZ.spectrum()(ZZ.ideal(5))
    return module, point, module.localize_at_prime(point)


def test_localized_module_retains_source_ring_module_and_prime() -> None:
    module, point, localized = _localized_plane_at_five()

    assert localized in LocalizedModules(point.local_ring())
    assert localized.base_ring() is point.local_ring()
    assert localized.localization_ring() is point.local_ring()
    assert localized.base() is point.local_ring()
    assert localized.source_ring() is ZZ
    assert localized.numerator_module() is module
    assert localized.localization_prime_point() is point
    submonoid = localized.localization_submonoid()
    assert ZZ(2) in submonoid
    assert ZZ(5) not in submonoid
    assert all(scalar in submonoid for scalar in localized.inverted_elements())


def test_localized_module_fractions_retain_numerator_denominator_and_equality() -> None:
    module, _point, localized = _localized_plane_at_five()
    generator = module.module_generator(0)
    fraction = localized.fraction(generator, ZZ(2))
    unit_fraction = localized.fraction(generator)

    assert isinstance(fraction, localized.ElementType)
    assert fraction.numerator() == generator
    assert fraction.denominator() == ZZ(2)
    assert unit_fraction == localized.localization_unit()(generator)
    assert fraction.equality_status(fraction) is True
    assert localized.zero() == localized.fraction(module.zero())


def test_localized_module_functor_and_identity_restriction_have_the_expected_endpoints() -> None:
    module, point, localized = _localized_plane_at_five()
    functor = localized.localization_functor()
    away_two = ZZ.free_module(1).localize(2)
    away_six = ZZ.free_module(1).localize(2, 3)
    restriction = away_two.restriction_to(away_six.base_ring())

    assert functor(module) is localized
    assert restriction.domain() is away_two
    assert restriction.codomain() is away_six
    assert not localized.is_zero()
    assert not localized.is_finite()


def test_localized_module_morphisms_have_identity() -> None:
    _module, _point, localized = _localized_plane_at_five()
    identity = localized.Mor(localized).identity()

    assert identity(localized.zero()) == localized.zero()
    assert identity * identity == identity
