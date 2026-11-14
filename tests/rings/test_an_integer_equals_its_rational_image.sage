r"""Equality of an integer and a rational follows the canonical map ``ZZ -> QQ``.

The map ``n |-> n/1`` is the structure map ``f: A -> S^{-1}A`` of the fraction
field, injective because ``ZZ`` is a domain (Atiyah--Macdonald, Ch. 3).  So
``3/1`` and ``3`` are one rational, and ``3/1`` and ``4`` are two.
Regression for sage-extensions#135.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_an_integer_equals_its_image_in_the_rationals() -> None:
    assert QQ(3) == ZZ(3)
    assert ZZ(3) == QQ(3)
    assert QQ(3) != ZZ(4)
    assert ZZ(4) != QQ(3)
