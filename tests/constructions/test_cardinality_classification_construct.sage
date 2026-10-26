r"""Cardinals classify finite, countable, aleph, and continuum cases."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cardinal_classification_and_initial_ordinals() -> None:
    assert cardinal(3).is_infinite() is False
    assert aleph0.is_infinite()
    assert aleph0.is_aleph()
    assert aleph0.is_countably_infinite()
    assert aleph0.aleph_index() == ordinal(0)
    assert aleph0.initial_ordinal() == omega(0)
    assert continuum.is_continuum()
    assert continuum.is_uncountably_infinite()
    assert cardinal(3).sort_key() < aleph0.sort_key()
