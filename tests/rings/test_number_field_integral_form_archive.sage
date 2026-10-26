r"""``ZZ[sqrt 5]`` and ``ZZ[(1 + sqrt 5)/2]``: two orders with one fraction field."""

from sage_extensions.all import *  # noqa: F401,F403


def test_root_five_order_is_not_maximal_and_has_fraction_field_the_number_field() -> None:
    r"""``(1 + sqrt 5)/2`` is a root of ``x^2 - x - 1``, integral over ``ZZ`` and not
    in ``ZZ[sqrt 5]``, so ``ZZ[sqrt 5]`` is not integrally closed; its fraction
    field is ``QQ(sqrt 5)`` (Neukirch, *Algebraic Number Theory*, I.2)."""
    field = QuadraticField(5, "a")
    a = field.primitive_element()
    selected = field.order_generated_by(a)
    golden = (field.one() + a) / 2

    assert not selected.is_maximal()
    assert selected.fraction_field() is field
    assert golden.minimal_polynomial()(golden) == field.zero()
    assert golden.is_integral()
    assert golden not in selected


def test_the_maximal_order_of_root_five_contains_the_root_five_order_with_index_two() -> None:
    r"""``O_{QQ(sqrt 5)} = ZZ[(1 + sqrt 5)/2]`` (``5 = 1 mod 4``), and
    ``ZZ[sqrt 5] = ZZ + 2 ZZ[(1 + sqrt 5)/2]`` has index ``2`` in it, while both
    have fraction field ``QQ(sqrt 5)`` (Neukirch, I.2)."""
    field = QuadraticField(5, "a")
    a = field.primitive_element()
    selected = field.order_generated_by(a)
    maximal = field.ring_of_integers()

    assert maximal.is_maximal()
    assert maximal.fraction_field() is field
    assert selected.fraction_field() is field
    assert a in maximal
    assert (field.one() + a) / 2 in maximal
    assert selected.index_in(maximal) == 2
