r"""Fractional ideals are projective rank-one modules inside a fraction field.

The principal Gaussian ideal ``(1+i)`` and its inverse are inverse fractional
ideals.  Their sum is the larger inverse ideal and their intersection is the
smaller principal ideal.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _gaussian_principal_fractional_ideal():
    ring = QuadraticField(-1, "i").ring_of_integers()
    i = ring.fraction_field().primitive_element()
    generator = ring(1 + i)
    return ring, generator, ring.fractional_ideal(generator)


def test_fractional_ideal_retains_ring_field_and_selected_generators() -> None:
    ring, generator, ideal = _gaussian_principal_fractional_ideal()
    generators = ideal.ideal_generators()

    assert ideal in FractionalIdeals(ring)
    assert ideal.ring() is ring
    assert ideal.fraction_field() is ring.fraction_field()
    assert generators.cardinality() == cardinal(1)
    assert ideal.is_principal()
    assert ideal.is_projective()
    assert ideal == ring.fractional_ideal(ideal.principal_generator())
    assert isinstance(ideal.an_element(), ideal.ElementType)
    assert ideal.zero() in ideal
    assert ideal.scalar_multiple(ring(2), ideal.an_element()) in ideal


def test_fractional_ideal_sum_intersection_and_inverse_have_expected_order() -> None:
    _ring, _generator, ideal = _gaussian_principal_fractional_ideal()
    inverse = ideal.inverse()

    assert inverse.inverse() == ideal
    assert ideal.sum(inverse) == inverse
    assert ideal.intersection(inverse) == ideal


def test_fractional_ideal_morphisms_have_identity() -> None:
    _ring, _generator, ideal = _gaussian_principal_fractional_ideal()
    identity = ideal.Mor(ideal).identity()

    assert identity(ideal.zero()) == ideal.zero()
    assert identity * identity == identity
