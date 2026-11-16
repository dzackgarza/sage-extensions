r"""An orbit is the G-set on its own points, with the action restricted to them.

An orbit of a finite ``G``-set is the ``G``-set whose points are the points
reachable from a seed and whose action is the set's action restricted to them; the
search that reaches those points is a route to the set, not part of it.  So the
orbit a question answers with is the ``G``-set its own point set and action
describe: the same points in the same order, and the same image under every group
element.

The specimen is the one the issue names: ``C(3)`` acting on its regular orbit beside
the fixed point ``5``.  The family's sweep reaches four points; the orbit of ``5`` is
the one-point ``G``-set on it, and it is compared with that ``G``-set built directly
on the same point set with the trivial action.
"""

from sage_extensions.all import *


def _regular_beside_a_fixed_point(element, point):
    r"""``C(3)`` acting on its own elements, with ``5`` fixed."""
    return point if point == 5 else element * point


def test_the_orbit_of_the_fixed_point_is_the_g_set_it_is() -> None:
    r"""The orbit of ``5`` is the one-point ``G``-set, action and all.

    The family's sweep reaches four points, three of them in the regular orbit.  The
    orbit of ``5`` is the one-point ``G``-set on it: it presents the point ``5``, and
    every element of ``C(3)`` acts on it as that element acts on the ``G``-set built
    directly on the same point set with the trivial action.
    """
    group = Groups.C(3)
    g_set = FiniteGSets(group).from_finite_orbits(
        (group.one(), 5), _regular_beside_a_fixed_point
    )
    assert g_set.cardinality() == cardinal(4)

    searched, _section = g_set.orbit_transversal_words(5)
    assert tuple(searched) == (5,)

    direct = FiniteGSets(group)(searched.point_set(), lambda element, point: point)
    assert direct.cardinality() == cardinal(1)
    assert tuple(searched) == tuple(direct)
    assert all(
        searched.act(element, point) == direct.act(element, point)
        for element in group
        for point in searched
    )
