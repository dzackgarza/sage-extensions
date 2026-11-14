r"""Division and inversion in the exact real field.

``RR`` is a field, hence a one-dimensional free module over itself, so its
element class carries the module's scalar division ``v / r = r^{-1} v`` beside
the field's own division.  Written as the quotient ``v / r = (1/r) v`` that
identity asks the same method for ``1/r`` and never terminates, which made
``1 / (RR(sqrt(2)) - 1)`` a ``RecursionError`` and left
``tests/functions/test_young_convolution.sage`` uncollectable (#398).
"""

from sage_extensions.all import *


def test_the_reciprocal_identity_keeps_the_radical_quotient_exact() -> None:
    r"""``1/(sqrt2 - 1) = sqrt2 + 1``, since ``(sqrt2 - 1)(sqrt2 + 1) = 1``."""
    root = RR(2).sqrt()
    inverse = 1 / (root - 1)

    assert inverse == root + 1
    assert (root - 1) * inverse == RR(1)


def test_a_real_divides_by_a_real_and_inverts() -> None:
    assert RR(3) / RR(4) * RR(4) == RR(3)
    assert ~RR(4) * RR(4) == RR(1)
