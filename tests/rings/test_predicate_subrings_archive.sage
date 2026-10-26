r"""The integers as the subring of ``QQ`` cut out by a predicate."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_rationals_with_denominator_one_form_a_subring_whose_units_are_plus_minus_one() -> None:
    r"""``{q in QQ : den(q) = 1} = ZZ`` is closed under ``+`` and ``*`` and contains
    ``1``; its units are ``+-1`` (``ZZ^x = {+-1}``), although every nonzero element
    is a unit of ``QQ``."""
    integers = QQ.predicate_subring(lambda value: value.denominator() == 1, "the denominator is one")
    three = integers(3)
    four = integers(4)

    assert QQ(6) in integers
    assert QQ(1) / 2 not in integers
    assert three * four == integers(12)
    assert three + four == integers(7)
    assert integers.inclusion()(three * four) == QQ(12)
    assert integers.one().is_unit()
    assert integers(-1).is_unit()
    assert not three.is_unit()
    assert not integers(2).is_unit()
    assert QQ(3).is_unit()
