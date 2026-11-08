r"""The selected generator permutations on each orbit are its original action."""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("union", (False, True), ids=("single_orbit", "union_of_orbits"))
@pytest.mark.parametrize("relabeled", (False, True), ids=("ordinal_points", "relabeled_points"))
def test_orbit_generator_permutations_equal_the_given_action(union, relabeled):
    r"""The standard S3 action and its conjugate by a point bijection retain their actual action."""
    group = Groups.S(3)
    labels = tuple(ZZ(value) for value in ((29, -11, 17, 83) if relabeled else (1, 2, 3, 4)))
    fixed = labels[3]

    def action(element, point):
        if point == fixed:
            return point
        position = labels.index(point) + 1
        return labels[int(element(ZZ(position))) - 1]

    seeds = (labels[0], fixed) if union else (labels[0],)
    g_set = FiniteGSets(group).from_finite_orbits(seeds, action)
    for point in (*seeds, labels[1]):
        orbit, section = g_set.orbit_transversal_words(point)
        letters, transversals = g_set.orbit_schreier_factors(point)
        permutations = g_set.orbit_generator_permutations(point)

        assert orbit.cardinality() == cardinal(1 if point == fixed else 3)
        assert tuple(tuple(permutation(candidate) for candidate in orbit) for permutation in permutations) == tuple(
            tuple(action(letter, candidate) for candidate in orbit) for letter in letters
        )
        assert all(action(transversal, point) == candidate for candidate, transversal in zip(orbit, transversals, strict=True))
        augmentation = group.selected_group_resolution().augmentation()
        assert all(transversal == augmentation(section(candidate)) for candidate, transversal in zip(orbit, transversals, strict=True))
