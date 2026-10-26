r"""The exact real field retains exact constants, relations, and transcendental operations."""

import operator

from sage_extensions.all import *  # noqa: F401,F403


def test_exact_real_field_has_exact_zero_one_pi_and_e() -> None:
    reals = ExactRealField()

    assert reals.characteristic() == 0
    assert reals.cardinality() == continuum
    assert reals.fraction_field() is reals
    assert reals.is_commutative()
    assert reals.is_exact()
    assert not reals.is_finite()
    assert reals.zero().is_zero()
    assert reals.one().is_one()
    assert reals.pi() > reals(3)
    assert reals.e() > reals(2)
    assert reals.relation(reals(1), reals(2), operator.lt)


def test_exact_real_number_operations_retain_exact_relations() -> None:
    reals = ExactRealField()
    two = reals(2)
    root_two = two.sqrt()
    zero = reals.zero()
    one = reals.one()

    assert root_two * root_two == two
    assert root_two.is_positive()
    assert (-root_two).is_negative()
    assert root_two.is_real()
    assert zero.is_zero()
    assert one.is_one()
    assert zero.exp() == one
    assert one.log() == zero
    assert zero.sin() == zero
    assert zero.tan() == zero
    assert zero.cos() == one
    assert root_two.expression() * root_two.expression() == two.expression()
    assert abs(float(root_two.n()) ** 2 - 2.0) < 1e-12
    assert abs(float(root_two.numerical_approx()) ** 2 - 2.0) < 1e-12

