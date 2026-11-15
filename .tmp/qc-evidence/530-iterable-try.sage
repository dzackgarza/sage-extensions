"""Try: the language's iterable class, written the way the review asks."""

import collections.abc

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_polynomial_ring_states_no_enumeration_of_its_points() -> None:
    r"""$\mathbf{Z}[x]$ is countable, and its points are not a finite iteration."""
    ring = ZZ["x"]

    assert ring in CountablyInfiniteSets()
    assert not isinstance(ring, collections.abc.Iterable)
    with pytest.raises(TypeError):
        iter(ring)
