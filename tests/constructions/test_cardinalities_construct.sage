r"""Finite and infinite cardinal arithmetic lives in the cardinality category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_basic_cardinal_arithmetic() -> None:
    cardinals = Cardinalities()

    assert cardinal(3) in cardinals
    assert aleph0 in cardinals
    assert continuum in cardinals
    assert cardinal(3) + cardinal(4) == cardinal(7)
    assert cardinal(2) ** cardinal(3) == cardinal(8)
    assert cardinal(2) ** aleph0 == continuum
    assert cardinals.lt(aleph0, continuum)
