from sage_extensions.all import *


def first():
    return omega(0)


def test_omega_is_the_initial_ordinal_of_aleph0() -> None:
    assert aleph0.initial_ordinal() == first()


def test_the_categories_of_omega() -> None:
    assert first() in Ordinals()


def test_the_cardinality_of_omega() -> None:
    assert first().cardinality() == aleph0
    assert omega(1).cardinality() == aleph(1)


def test_ordinal_addition_is_not_commutative() -> None:
    r"""$1 + \omega = \omega$ but $\omega + 1 \ne \omega$; on finite ordinals it is addition, $2 + 3 = 5$."""
    assert ordinal(1).ordinal_sum(first()) == first()
    assert first().ordinal_sum(1) != first()
    assert Ordinals()(2).ordinal_sum(3) == 5
