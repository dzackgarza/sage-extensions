r"""The Schreier family of a pointed finite G-set is read from the set's own action.

``orbit_schreier_morphism`` emits ``t_(s.p)^-1 s t_p`` over the orbit's points
``p`` and the selected free cover's letters ``s``.  Every image ``s.p`` in that
family is the letter's action at the point, so the family is a function of the
``G``-set -- its point set and its permutation representation -- and not of the
search that happened to reach the set.

These tests pin that mathematics at the ``G``-set layer: the composites fix the
base point and generate its stabilizer, the returned letters and transversals
rebuild the family element for element, the generators that
``drop_trivial`` omits are exactly the identity images, and a point outside the
sweep that built the family answers as the orbit it lies on.
"""

from sage_extensions.all import *


def _transpositions():
    r"""The three transpositions of S(3), which conjugation permutes transitively."""
    group = Groups.S(3)
    return group((1, 2)), group((1, 3)), group((2, 3))


def _conjugation_action(element, point):
    r"""S(3) acting on its three transpositions by conjugation."""
    return element * point * ~element


def test_the_schreier_family_of_a_point_is_its_stabilizer() -> None:
    r"""The family of ``(1 2)`` under conjugation is its centralizer, of order two.

    The three transpositions of $S_3$ are one orbit under conjugation, so the
    stabilizer of one is its centralizer $\langle(1\,2)\rangle$.  Every
    Schreier composite fixes the point, and the composites together generate
    exactly that stabilizer.
    """
    group = Groups.S(3)
    point = _transpositions()[0]
    g_set = FiniteGSets(group).from_finite_orbits((point,), _conjugation_action)
    assert g_set.cardinality() == cardinal(3)

    morphism = g_set.orbit_schreier_morphism(point)
    family = tuple(morphism(letter) for letter in morphism.domain().group_generators())
    assert all(g_set.act(image, point) == point for image in family)
    assert group.subgroup(family).cardinality() == g_set.stabilizer(point).cardinality()
    assert g_set.stabilizer(point).cardinality() == cardinal(2)


def test_the_factors_rebuild_the_family_element_for_element() -> None:
    r"""``~t_(s.p) s t_p`` over the returned letters and transversals is the family.

    The transversals are the augmentation of the section's words, and the
    composite law the docstring states rebuilds every member of the family in
    the order the orbit's own points and the cover's own letters present them.
    """
    group = Groups.S(3)
    point = _transpositions()[0]
    g_set = FiniteGSets(group).from_finite_orbits((point,), _conjugation_action)
    augmentation = group.selected_group_resolution().augmentation()

    letters, transversals = g_set.orbit_schreier_factors(point)
    orbit, section = g_set.orbit_transversal_words(point)
    assert tuple(transversals) == tuple(augmentation(section(candidate)) for candidate in orbit)

    positions = orbit.ranking_map()
    rebuilt = tuple(
        (~transversals[int(positions(orbit.act(letter, candidate)))])
        * letter
        * transversals[int(positions(candidate))]
        for candidate in orbit
        for letter in letters
    )
    morphism = g_set.orbit_schreier_morphism(point)
    assert rebuilt == tuple(morphism(letter) for letter in morphism.domain().group_generators())


def test_the_dropped_generators_are_the_identity_images() -> None:
    r"""A coset space's family with its trivial generators dropped names no identity.

    $S_3/\langle(1\,2)\rangle$ has three points, so the family over the two
    selected letters has six members.  The trivial generators are the members
    whose image is the identity, dropping them leaves exactly the non-identity
    ones, and the subgroup they present is unchanged.
    """
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    cosets = group.left_cosets(subgroup)
    assert cosets.cardinality() == cardinal(3)

    full = cosets.schreier_generating_morphism()
    trimmed = cosets.schreier_generating_morphism(drop_trivial=True)
    full_family = tuple(full(letter) for letter in full.domain().group_generators())
    trimmed_family = tuple(trimmed(letter) for letter in trimmed.domain().group_generators())

    assert group.subgroup(full_family).cardinality() == subgroup.cardinality()
    assert group.subgroup(trimmed_family).cardinality() == subgroup.cardinality()
    assert group.one() not in trimmed_family
    assert trimmed_family == tuple(image for image in full_family if image != group.one())


def test_a_point_outside_the_familys_sweep_answers_from_its_own_orbit() -> None:
    r"""The fixed point ``5`` of a C(3)-set: a one-point orbit whose family is all of C(3).

    The set is the union of the regular orbit of ``1`` and the fixed point
    ``5``.  The orbit of ``5`` is the one-point set, and a fixed point's
    stabilizer is the whole group, so the Schreier family of ``5`` generates
    C(3) -- the same answer the one-point ``G``-set on its own gives.
    """
    group = Groups.C(3)
    one = group.one()
    g_set = FiniteGSets(group).from_finite_orbits(
        (one, 5), lambda element, point: point if point == 5 else element * point
    )
    assert g_set.cardinality() == cardinal(4)

    orbit, _section = g_set.orbit_transversal_words(5)
    assert orbit.cardinality() == cardinal(1)
    assert tuple(orbit) == (5,)
    _letters, transversals = g_set.orbit_schreier_factors(5)
    assert tuple(transversals) == (one,)

    morphism = g_set.orbit_schreier_morphism(5)
    family = tuple(morphism(letter) for letter in morphism.domain().group_generators())
    assert all(g_set.act(image, 5) == 5 for image in family)
    assert group.subgroup(family).cardinality() == cardinal(3)

    alone = FiniteGSets(group)(orbit.point_set(), lambda element, point: point)
    assert alone.cardinality() == cardinal(1)
    alone_morphism = alone.orbit_schreier_morphism(5)
    assert tuple(alone_morphism(letter) for letter in alone_morphism.domain().group_generators()) == family


def test_the_same_action_presented_two_ways_presents_the_same_family() -> None:
    r"""A set reached by a sweep and the set handed its action answer identically.

    ``from_finite_orbits`` reaches the point set by a breadth-first sweep;
    ``from_permutation_representation`` is handed the action that sweep
    computed.  The family of a point is the action's, so both present the same
    images in the same order.
    """
    group = Groups.S(3)
    swept = FiniteGSets(group).from_finite_orbits((_transpositions()[0],), _conjugation_action)
    presented = FiniteGSets(group).from_permutation_representation(swept.permutation_representation())

    for base in swept:
        swept_morphism = swept.orbit_schreier_morphism(base)
        presented_morphism = presented.orbit_schreier_morphism(base)
        assert tuple(swept_morphism(letter) for letter in swept_morphism.domain().group_generators()) == tuple(
            presented_morphism(letter) for letter in presented_morphism.domain().group_generators()
        )


def test_a_one_shot_seed_iterable_presents_the_whole_orbit() -> None:
    r"""A generator of seeds is materialized before the sweep, not consumed by it.

    The regular action of C(3) started from the identity reaches all three
    elements, so a one-shot iterable of seeds still presents the whole orbit.
    """
    group = Groups.C(3)
    one = group.one()
    g_set = FiniteGSets(group).from_finite_orbits(
        (seed for seed in (one,)), lambda element, point: element * point
    )
    assert g_set.cardinality() == cardinal(3)

    morphism = g_set.orbit_schreier_morphism(one)
    family = tuple(morphism(letter) for letter in morphism.domain().group_generators())
    assert all(image == one for image in family)
