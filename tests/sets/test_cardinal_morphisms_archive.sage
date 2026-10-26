r"""Cardinal exponentiation is not monotone in the exponent at base zero.

Derivation: `0^0 = |\{\emptyset \to \emptyset\}| = 1` while `0^1 = |\{1 \to \emptyset\}|
= 0`, so `0 \le 1` does not give `0^0 \le 0^1`; for a nonzero base, `\kappa \le \lambda`
gives `2^\kappa \le 2^\lambda`, e.g. `2^1 = 2 \le 4 = 2^2`.
"""

from sage_extensions.all import *


def test_zero_to_the_zero_is_one_and_zero_to_the_one_is_zero() -> None:
    cardinals = Cardinalities()

    assert cardinal(0) ** cardinal(0) == cardinal(1)
    assert cardinal(0) ** cardinal(1) == cardinal(0)
    assert cardinals.Mor(cardinal(0) ** cardinal(0), cardinal(0) ** cardinal(1)).is_empty()
    assert not cardinals.Mor(cardinal(2) ** cardinal(1), cardinal(2) ** cardinal(2)).is_empty()
