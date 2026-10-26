r"""The Gaussian integers cut out of ``Q(i)`` by integrality, and the unit-group functor.

The elements of ``Q(i)`` integral over ``Z`` form the subring ``Z[i]``: it contains
``i`` and not ``(1 + i)/2`` (whose minimal polynomial ``x^2 - x + 1/2`` is not
integral).  An element of ``Z[i]`` is a unit exactly when its norm is ``1``, so
``i`` is a unit (``i * (-i) = 1``) while ``1 + i`` and ``2`` (norms ``2`` and ``4``)
are not, and ``(1 + i)(1 - i) = 2``.  The subring is countably infinite, as is
``Z^2``.

A ring map ``f: R -> S`` sends units to units, so ``(-)^x`` is a functor; applied to
``Z -> Z/6`` it sends ``-1`` to ``5``, and ``5^2 = 1`` in ``(Z/6)^x``.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_the_integral_elements_of_q_i_form_the_gaussian_integers() -> None:
    field = QuadraticField(-1)
    i = field.primitive_element()
    gaussian = field.predicate_subring(lambda z: z.is_integral(), "integral over Z")

    assert gaussian.ambient_ring() is field
    assert i in gaussian
    assert (1 + i) / 2 not in gaussian
    assert gaussian.inclusion()(gaussian(i)) == i
    assert gaussian(1 + i) * gaussian(1 - i) == gaussian(2)
    assert gaussian(i) * gaussian(i) == -gaussian.one()
    assert gaussian.zero().is_zero()
    assert not gaussian(i).is_one()


def test_an_element_outside_the_predicate_is_refused() -> None:
    field = QuadraticField(-1)
    i = field.primitive_element()
    gaussian = field.predicate_subring(lambda z: z.is_integral(), "integral over Z")

    with pytest.raises(ValueError):
        gaussian((1 + i) / 2)


def test_the_gaussian_units_are_the_elements_of_norm_one() -> None:
    field = QuadraticField(-1)
    i = field.primitive_element()
    gaussian = field.predicate_subring(lambda z: z.is_integral(), "integral over Z")

    assert gaussian(i).is_unit()
    assert gaussian(-1).is_unit()
    assert not gaussian(1 + i).is_unit()
    assert not gaussian(2).is_unit()


def test_the_gaussian_integers_are_countably_infinite() -> None:
    field = QuadraticField(-1)
    gaussian = field.predicate_subring(lambda z: z.is_integral(), "integral over Z")

    assert gaussian.cardinality() == aleph0


def test_reduction_modulo_six_sends_minus_one_to_five_on_units() -> None:
    residues = ZZ.ideal(ZZ(6)).quotient_ring()
    units = Rings().unit_group()
    on_units = units(residues.quotient_map())
    five = residues.unit_group()(residues(5))

    assert on_units(ZZ.unit_group()(-1)) == five
    assert on_units(ZZ.unit_group()(1)) == residues.unit_group().one()
    assert five * five == residues.unit_group().one()
