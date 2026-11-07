r"""The selected generator permutations on each orbit are its original action."""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("union", (False, True), ids=("single_orbit", "union_of_orbits"))
def test_orbit_generator_permutations_equal_the_given_action(union):
    r"""S3 permutes {1,2,3} and fixes 4; every orbit retains its true action."""
    group = Groups.S(3)

    def action(element, point):
        return element(point) if point != 4 else point

    seeds = (ZZ(1), ZZ(4)) if union else (ZZ(1),)
    g_set = FiniteGSets(group).from_finite_orbits(seeds, action)
    for point in seeds:
        orbit, section = g_set.orbit_transversal_words(point)
        letters, transversals = g_set.orbit_schreier_factors(point)
        permutations = g_set.orbit_generator_permutations(point)

        assert orbit.cardinality() == cardinal(1 if point == 4 else 3)
        assert tuple(tuple(permutation(candidate) for candidate in orbit) for permutation in permutations) == tuple(
            tuple(g_set.act(letter, candidate) for candidate in orbit) for letter in letters
        )
        assert all(g_set.act(transversal, point) == candidate for candidate, transversal in zip(orbit, transversals, strict=True))
