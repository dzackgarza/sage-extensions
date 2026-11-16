r"""A search leaves nothing on the orbit it reached.

An orbit is the ``G``-set on its own point set with the action restricted to it,
so the state of a searched orbit is the state of that ``G``-set built directly
from the same point set and action, and nothing else.  The breadth-first sweep
that reaches the points is a route to the set, not a datum of it: the table it
evaluates belongs to the search, and a set that carried it would answer a later
question from a route rather than from its own action.

The specimen is the one the issue names: ``C(3)`` acting on its regular orbit
beside the fixed point ``5``.  The orbit of ``5`` is a one-point ``G``-set, and
it must carry exactly what that one-point ``G``-set carries.
"""

from sage_extensions.all import *


def _regular_beside_a_fixed_point(element, point):
    r"""``C(3)`` acting on its own elements, with ``5`` fixed."""
    return point if point == 5 else element * point


def test_a_searched_orbit_carries_only_the_state_of_the_g_set_it_is() -> None:
    r"""The orbit of the fixed point ``5`` is the one-point ``G``-set, state and all.

    The family's sweep reaches four points, three of them in the regular orbit;
    the orbit of ``5`` is ``{5}``.  Both it and the ``G``-set built directly on
    that point set with the trivial action are asked the one question each owns,
    the enumeration of its points, so that what remains is what a search left:
    nothing.  A sweep retained on the orbit would be one more name than the
    construction establishes, and it is the name a later question would read.
    """
    group = Groups.C(3)
    g_set = FiniteGSets(group).from_finite_orbits(
        (group.one(), 5), _regular_beside_a_fixed_point
    )
    assert g_set.cardinality() == cardinal(4)

    searched, _section = g_set.orbit_transversal_words(5)
    assert tuple(searched) == (5,)

    direct = FiniteGSets(group)(searched.point_set(), lambda element, point: point)
    searched.ranking_map()
    direct.ranking_map()

    assert names_beyond(direct, searched) == frozenset()
    assert tuple(searched) == tuple(direct)
    assert all(
        searched.act(element, point) == direct.act(element, point)
        for element in group
        for point in searched
    )
