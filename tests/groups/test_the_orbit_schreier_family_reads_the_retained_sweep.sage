r"""The orbit Schreier construction consumes the retained sweep; the words are the same words.

``from_finite_orbits`` evaluates every ``(letter, point)`` pair of the orbit
search exactly once.  The Schreier family used to evaluate them all twice
more (a second traversal in ``_orbit_of`` and one per comprehension row in
``_orbit_schreier_morphism``); the retained transition table answers every
``s.p`` from the single sweep.  These tests pin that the family is word-for-
word the family's old construction produces, on specimens with a nontrivial
stabilizer, and that the -- now unique -- sweep's table and words agree with
an explicit private sweep.
"""

from sage_extensions.all import *
from sage_extensions.categories.group.g_sets import (
    FiniteGSets,
    _orbit_schreier_morphism,
)
from sage_extensions.categories.sets.set_categories import Sets


def _direct_schreier(gset, point):
    r"""The comprehension construction of the Schreier morphism, with no retained table."""
    orbit, words, augmentation = gset._orbit_of(point)
    ranking = orbit.ranking_map()
    word_section = Sets().Mor(orbit, augmentation.domain())(
        lambda image: words[int(ranking(image))]
    )
    return _orbit_schreier_morphism(orbit, word_section, augmentation)


def test_the_retained_sweep_and_the_explicit_sweep_agree() -> None:
    r"""C(3) in its regular action: the retained table and words are the explicit sweep's."""
    group = Groups.C(3)
    one = group.one()
    gset = FiniteGSets(group).from_finite_orbits((one,), lambda g, x: g * x)
    (generator,) = group.group_generators()

    retained = gset.__dict__.get("_retained_orbit_bfs")
    assert retained is not None
    table = retained["transitions"]
    assert len(table) == 3 * retained["letter_count"] == 3
    # g.1 = g, g.g = g^2, g.g^2 = 1, read at point positions 0, 1, 2 of the sweep
    assert table[(0, 0)] == 1 and table[(1, 0)] == 2 and table[(2, 0)] == 0

    augmentation = group.selected_group_resolution().augmentation()
    points, words = FiniteGSets(group)._orbit_words(
        (one,), gset.act, augmentation, point_key=gset.ranking_map()
    )
    assert tuple(retained["points"]) == tuple(points)
    assert tuple(retained["words"]) == tuple(words)

    orbit_set, retained_words, retained_aug = gset._orbit_of(one)
    assert retained_aug is augmentation
    assert tuple(retained_words) == tuple(words)


def test_the_schreier_morphism_from_the_table_is_the_comprehension_morphism() -> None:
    r"""Word-for-word, on every letter of the Schreier domain, for both constructed paths."""
    group = Groups.C(3)
    one = group.one()
    gset = FiniteGSets(group).from_finite_orbits((one,), lambda g, x: g * x)

    via_table = gset.orbit_schreier_morphism(one)
    via_comprehension = _direct_schreier(gset, one)

    table = tuple(via_table(letter) for letter in via_table.domain().group_generators())
    swept = tuple(via_comprehension(letter) for letter in via_comprehension.domain().group_generators())
    assert table == swept
    # the regular action has a trivial point stabilizer: every Schreier image is the identity
    assert all(image == group.one() for image in table)


def test_the_stabilizer_of_a_transposition_under_conjugation_is_its_centralizer() -> None:
    r"""A genuinely nontrivial stabilizer through the retained path.

    S(3) conjugates its three transpositions transitively; the stabilizer of
    (1 2) under that action is its centralizer <(1 2)>, of order 2, and every
    delivered generator must fix its coset point, not a different point.
    """
    group = Groups.S(3)
    transpositions = (group((1, 2)), group((1, 3)), group((2, 3)))
    gset = FiniteGSets(group).from_finite_orbits(
        (transpositions[0],), lambda g, x: g * x * ~g
    )
    assert int(gset.point_set().cardinality()) == 3

    sch = gset.orbit_schreier_morphism(transpositions[0])
    images = tuple(sch(letter) for letter in sch.domain().group_generators())
    # every image fixes the base point under the same action
    for image in images:
        assert image * transpositions[0] * ~image == transpositions[0]
    # the generated subgroup is the stabilizer: order 2
    assert int(group.subgroup(images).cardinality()) == 2

    direct = _direct_schreier(gset, transpositions[0])
    via_table = tuple(sch(letter) for letter in sch.domain().group_generators())
    swept = tuple(direct(letter) for letter in direct.domain().group_generators())
    assert via_table == swept


def test_a_point_not_covered_by_the_retained_sweep_searches_as_before() -> None:
    r"""The general fallback is intact: a point outside the first seed's BFS start searches."""
    group = Groups.C(3)
    one = group.one()
    # the seed 'one' has a 3-point orbit and '5' is fixed, so the set holds 4 points
    gset = FiniteGSets(group).from_finite_orbits(
        (one, 5), lambda g, x: x if x == 5 else g * x
    )
    assert int(gset.point_set().cardinality()) == 4
    orbit, words, augmentation = gset._orbit_of(5)
    assert "_retained_transitions" not in orbit.__dict__
    sch = gset.orbit_schreier_morphism(5)
    images = tuple(sch(letter) for letter in sch.domain().group_generators())
    # 5 is a fixed point: its stabilizer is the whole C(3), generated by the image
    assert int(group.subgroup(images).cardinality()) == 3


def test_a_one_shot_seed_iterable_gets_the_same_retained_sweep() -> None:
    r"""A generator expression as seeds is materialized once, before the sweep."""
    group = Groups.C(3)
    one = group.one()
    gset = FiniteGSets(group).from_finite_orbits((s for s in (one,)), lambda g, x: g * x)

    retained = gset.__dict__.get("_retained_orbit_bfs")
    assert retained is not None
    assert retained["seeds"] == (one,)
    augmentation = group.selected_group_resolution().augmentation()
    orbit, words, returned_augmentation = gset._orbit_of(one)
    assert "_retained_transitions" in orbit.__dict__
    assert returned_augmentation is retained["augmentation"]
    sch = gset.orbit_schreier_morphism(one)
    images = tuple(sch(letter) for letter in sch.domain().group_generators())
    assert all(image == group.one() for image in images)


def test_the_deduped_generating_morphism_presents_the_same_subgroup_once_each() -> None:
    r"""First-occurrence order, no duplicate image, same subgroup as the full Schreier family."""
    from sage_extensions.categories.rational_integral_stabilizers import (
        _deduplicated_generating_morphism,
    )

    group = Groups.S(3)
    transpositions = (group((1, 2)), group((1, 3)), group((2, 3)))
    gset = FiniteGSets(group).from_finite_orbits(
        (transpositions[0],), lambda g, x: g * x * ~g
    )
    sch = gset.orbit_schreier_morphism(transpositions[0])
    deduped = _deduplicated_generating_morphism(group, sch)

    full = list(tuple(sch(letter) for letter in sch.domain().group_generators()))
    reduced = list(tuple(deduped(letter) for letter in deduped.domain().group_generators()))
    # every image of the full family appears in the reduced one, and vice versa
    assert set(full) == set(reduced)
    # the reduced family reads each distinct image exactly once
    assert len(set(reduced)) == len(reduced)
    assert len(reduced) <= len(full)
    # first-occurrence order: the reduced family begins with the first image,
    # and each later one is the first not yet seen
    assert reduced[0] == full[0]
    first_positions = [full.index(image) for image in reduced]
    assert first_positions == sorted(first_positions)
    # the presented subgroup is unchanged, and it is the order-2 centralizer here
    assert int(group.subgroup(reduced).cardinality()) == 2
    assert int(group.subgroup(full).cardinality()) == 2
