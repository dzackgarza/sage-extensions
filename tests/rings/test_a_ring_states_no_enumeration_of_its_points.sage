r"""A ring's points are iterated only where they are a finite set.

$\mathbf{Z}[x]$ is countable -- its points are $0, 1, -1, x, -x, \ldots$ -- so
nothing is missing when it states no enumeration of them: an iterator need not
be finite, but a ring's points are not a sequence either, and the general ring
category states no ``__iter__`` at all rather than an operation whose only
behavior is to refuse.

The language states the refusal.  ``__getitem__`` on a ring is the adjunction
syntax $R[x_1, \ldots, x_n]$ and not an index into a sequence, so with
``__iter__`` merely absent Python's sequence fallback would read
$\mathbf{Z}[x][0]$ -- a ring -- as the first point, and ``tuple(ZZ['x'])`` would
hand rings back forever.  Setting the special method to ``None`` states that the
operation is not available: ``iter()`` then raises ``TypeError`` without falling
back to ``__getitem__`` (Python Language Reference, Data Model, §3.3, "Special
method names").

A ring whose points are a finite set does state their enumeration, and
``tests/categories/test_the_refined_category_answers_with_its_own_operation.sage``
states it for $\mathbf{Z}/8$.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_polynomial_ring_states_no_enumeration_of_its_points() -> None:
    r"""$\mathbf{Z}[x]$ is countable, and its points are not a finite iteration.

    The ring states the data model's ``__iter__ = None``, so ``iter`` and
    ``tuple`` raise the language's ``TypeError`` instead of reading the
    adjunction ``ZZ['x'][n]`` as the $n$-th point of the ring.
    """
    ring = ZZ["x"]

    assert ring in CountablyInfiniteSets()
    assert ring.__iter__ is None
    with pytest.raises(TypeError):
        iter(ring)
    with pytest.raises(TypeError):
        tuple(ring)
