r"""One sweep per construction: no seed of it is searched a second time.

``from_finite_orbits`` runs one breadth-first sweep from the seeds it is handed, and
the sweep it leaves is closed under every selected letter.  Each seed's own orbit
therefore lies inside that sweep, and the words composed along it carry that seed to
each of its points: the first question about a seed's orbit is answered by the work
the construction already did, and running the sweep again is one orbit searched
twice.

The count is the contract, and it is the only witness of it.  A set built from a
sweep holds that sweep's answer, so a question that sweeps again has repeated the
derivation, and no value-level assertion would show it: the second sweep reaches the
same points in the same order with the same words, so the answer is right either
way.

The boundary is where a section copied out of the sweep would be wrong.  The sweep
writes the identity at every seed it started from, so it is a section from a lone
seed and from no other, and a block of the sweep is one seed's orbit only when the
sweep reached one orbit.  Every section here is therefore also asserted as a
transversal from the seed it is asked about: on a repeated seed, on two seeds of one
orbit, and on two seeds of different orbits.
"""

from sage_extensions.all import *


def _regular_action(element, point):
    r"""``C(3)`` acting on its own elements."""
    return element * point


def _regular_beside_a_fixed_point(element, point):
    r"""``C(3)`` acting on its own elements, with ``5`` fixed."""
    return point if point == 5 else element * point


def _is_sectioned_from(group, g_set, seed, answer):
    r"""Whether the answer's section carries ``seed`` to each point of its orbit."""
    orbit, section = answer
    augmentation = group.selected_group_resolution().augmentation()
    return all(g_set.act(augmentation(section(point)), seed) == point for point in orbit)


def test_the_only_seed_of_a_sweep_is_not_searched_again() -> None:
    r"""``C(3)`` in its regular action: the construction's own sweep answers the seed.

    The sweep started at the identity reaches all three elements, so the orbit of the
    identity is this ``G``-set itself and its section is the sweep's own words.  The
    construction ran one sweep; the question runs none, and each word carries the
    identity to the point it belongs to.
    """
    group = Groups.C(3)
    one = group.one()
    g_set, answer, swept, asked = orbit_sweeps_of(
        lambda: FiniteGSets(group).from_finite_orbits((one,), _regular_action),
        lambda built: built.orbit_transversal_words(one),
    )
    assert swept == 1
    assert asked == 0
    orbit, _section = answer
    assert orbit is g_set
    assert _is_sectioned_from(group, g_set, one, answer)


def test_a_seed_listed_twice_is_one_seed_and_one_sweep() -> None:
    r"""``(one, one)`` names one point, so its orbit is the set the sweep built.

    Both seeds are the identity, and the sweep deduplicates them: the three elements
    of ``C(3)`` are reached once, by the one sweep the construction ran.  The orbit of
    the identity is then this ``G``-set itself, not a second set built over the same
    points.
    """
    group = Groups.C(3)
    one = group.one()
    g_set, answer, swept, asked = orbit_sweeps_of(
        lambda: FiniteGSets(group).from_finite_orbits((one, one), _regular_action),
        lambda built: built.orbit_transversal_words(one),
    )
    assert swept == 1
    assert asked == 0
    assert g_set.cardinality() == cardinal(3)
    orbit, _section = answer
    assert orbit is g_set
    assert _is_sectioned_from(group, g_set, one, answer)


def test_the_second_seed_of_one_sweep_is_sectioned_from_itself() -> None:
    r"""Two seeds of the regular orbit: one orbit, one sweep, a section for each.

    ``1`` and the generator ``g`` lie in the same orbit, so the sweep reaches the
    three elements once.  The orbit of ``g`` is that same block of points, and its
    section carries ``g`` to them -- not the identity the sweep wrote at ``g`` as a
    seed, and not ``1``'s section.
    """
    group = Groups.C(3)
    one = group.one()
    (generator,) = group.group_generators()
    g_set, answer, swept, asked = orbit_sweeps_of(
        lambda: FiniteGSets(group).from_finite_orbits((one, generator), _regular_action),
        lambda built: built.orbit_transversal_words(generator),
    )
    assert swept == 1
    assert asked == 0
    orbit, _section = answer
    assert orbit.cardinality() == cardinal(3)
    assert _is_sectioned_from(group, g_set, generator, answer)


def test_the_seeds_of_two_orbits_are_each_answered_from_the_sweep() -> None:
    r"""``1`` and ``5``: the regular orbit and the fixed point, one sweep between them.

    The sweep reaches the three elements of the regular orbit and the fixed point
    ``5``.  Each seed's own orbit is inside it, and each is answered without a second
    sweep: the orbit of ``5`` is the one-point set on it, and the orbit of ``1`` is the
    three elements of its own, which does not hold ``5``.
    """
    group = Groups.C(3)
    one = group.one()
    for seed in (one, 5):
        g_set, answer, swept, asked = orbit_sweeps_of(
            lambda: FiniteGSets(group).from_finite_orbits(
                (one, 5), _regular_beside_a_fixed_point
            ),
            lambda built: built.orbit_transversal_words(seed),
        )
        assert swept == 1
        assert asked == 0
        assert _is_sectioned_from(group, g_set, seed, answer)

    g_set = FiniteGSets(group).from_finite_orbits((one, 5), _regular_beside_a_fixed_point)
    assert g_set.cardinality() == cardinal(4)
    fixed_orbit, _fixed_section = g_set.orbit_transversal_words(5)
    assert tuple(fixed_orbit) == (5,)
    regular_orbit, _regular_section = g_set.orbit_transversal_words(one)
    assert regular_orbit.cardinality() == cardinal(3)
    assert 5 not in tuple(regular_orbit)
