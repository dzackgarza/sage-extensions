r"""The meet of two principal ideals is the ideal of their least common multiple.

In a principal ideal domain $(a) \cap (b) = (\operatorname{lcm}(a, b))$.  The
meet is supplied by the common module-subobject owner, which keeps the ideal's
inclusion and its ambient ring; the ideal owner supplies only the computation.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_meet_of_integer_ideals_is_the_ideal_of_the_lcm() -> None:
    meet = ZZ.ideal(2).intersection(ZZ.ideal(3))
    assert meet == ZZ.ideal(6)
    assert ZZ(6) in meet
    assert ZZ(2) not in meet and ZZ(3) not in meet
    assert meet.inclusion().codomain() is ZZ


def test_the_meet_of_integer_ideals_with_a_zero_generator_is_zero() -> None:
    assert ZZ.ideal(0).intersection(ZZ.ideal(5)) == ZZ.ideal(0)
    assert ZZ.ideal(0).intersection(ZZ.ideal(0)) == ZZ.ideal(0)


def test_the_meet_of_integer_ideals_composes_with_the_join() -> None:
    assert ZZ.ideal(4).intersection(ZZ.ideal(6)) == ZZ.ideal(12)
    assert ZZ.ideal(2).sum(ZZ.ideal(3)) == ZZ.ideal(1)
