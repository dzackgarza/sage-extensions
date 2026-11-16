r"""The one sweep a set is built from is the orbit of the seed that started it.

``from_finite_orbits`` evaluates every ``(point, letter)`` pair of one
breadth-first search, and the transversal words it assigns on the way are the
section of the orbit of its seed: the word that carries the seed to a point is
that point's transversal.  A set built from a single seed is therefore exactly
that orbit, so the words the set is built from are the answer to the first
question about the orbit, and no second search over the same points is run to
find them again.
"""

from sage_extensions.all import *


def test_the_orbit_of_the_seed_is_the_set_the_sweep_reached() -> None:
    r"""``C(3)`` in its regular action: the orbit of the identity is the whole set.

    The sweep started at the identity reaches all three elements, so the orbit of
    the identity is this ``G``-set itself, and the section it answers with is the
    sweep's own words: each carries the base point to the point it belongs to,
    which is what makes it a transversal of that orbit.
    """
    group = Groups.C(3)
    one = group.one()
    g_set = FiniteGSets(group).from_finite_orbits(
        (one,), lambda element, point: element * point
    )
    assert g_set.cardinality() == cardinal(3)

    augmentation = group.selected_group_resolution().augmentation()
    orbit, section = g_set.orbit_transversal_words(one)
    assert orbit is g_set
    assert all(
        g_set.act(augmentation(section(point)), one) == point for point in orbit
    )
