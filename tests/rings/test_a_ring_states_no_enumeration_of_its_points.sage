r"""A ring's points are iterated only where a level states their enumeration.

$\mathbf{Z}[x]$ is countable -- its points are $0, 1, -1, x, -x, \ldots$ -- so
nothing is missing when a ring states no enumeration of them: an iterator need
not be finite, but a ring's points are not a sequence either, and no level
supplies this ring an enumeration.

Two levels do supply one.  A ring whose points are a finite set is enumerated by
the engine that realizes it (:class:`OwnedRings.Finite`, stated for
$\mathbf{Z}/8$ in
``tests/categories/test_the_refined_category_answers_with_its_own_operation.sage``),
and a ring that is a finitely generated framed free module over its base ring is
enumerated through the framing's coordinates -- the bounded integral box
exhausts such a module, so the coordinates enumerate its points -- which
``tests/rings/test_a_framed_ring_enumerates_its_points_through_its_framing.sage``
states for $\mathbf{Z}$ and $\mathbf{Q}(i)$.  $\mathbf{Z}[x]$ is in neither: its
monomial framing has no finite basis, so no coordinate box exists to exhaust it
and the general ring's stated absence answers.

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

The assertions below state both halves of what the language then says about
$\mathbf{Z}[x]$: ``__iter__`` is ``None``, and ``iter`` and ``tuple`` refuse.
The language draws one further consequence, which this file records rather than
asserts: an object whose ``__iter__`` is ``None`` is not an instance of
``collections.abc.Iterable``, where one whose ``__iter__`` raised would still be
(measured: ``True`` with the method ``7b23fc3`` replaced, ``False`` with the
slot set to ``None``, the two agreeing on ``iter`` and ``tuple``).  The test
lint bars the spelling --- ``TL01`` refuses ``import collections.abc`` and
``TL03`` refuses ``isinstance`` --- so the assertion would have to be admitted
by the standard before it can be written here.
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
