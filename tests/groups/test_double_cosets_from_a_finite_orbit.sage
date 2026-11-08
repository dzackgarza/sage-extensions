r"""Double cosets in S3 from its three-point action.

For H = Stab(1) = <(2 3)>, H has two orbits on S3/H, while A3 has
one. The complete Schreier family generates H. Adding a fixed point
to the supplied finite action does not change the orbit S3.1.
"""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("union", (False, True), ids=("transitive", "with_fixed_point"))
def test_the_orbit_cosets_have_their_exact_actions_and_double_cosets(union):
    group = Groups.S(3)
    subgroup = group.subgroup((group((2, 3)),))
    alternating = group.subgroup((group((1, 2, 3)),))

    def action(element, point):
        return point if point == 4 else element(point)

    seeds = (ZZ(1), ZZ(4)) if union else (ZZ(1),)
    acted = FiniteGSets(group).from_finite_orbits(seeds, action)
    cosets = acted.coset_space_for(ZZ(1), subgroup)

    assert cosets.cardinality() == cardinal(3)
    for element in group:
        for point in cosets:
            assert cosets.act(element, point) == element(point)
    assert cosets.double_cosets(subgroup).cardinality() == cardinal(2)
    assert cosets.double_cosets(alternating).cardinality() == cardinal(1)
    schreier = cosets.schreier_generating_morphism()
    image = tuple(schreier(letter) for letter in schreier.domain().group_generators())
    assert group.subgroup(image).cardinality() == cardinal(2)
    assert all(element(ZZ(1)) == ZZ(1) for element in image)


@pytest.mark.parametrize("reverse", (False, True), ids=("cycle_first", "transposition_first"))
def test_pointed_cosets_generate_the_full_stabilizer_with_the_supplied_cover(reverse):
    group = Groups.S(3)
    subgroup = group.subgroup((group((2, 3)),))
    group_generators = (group((1, 2, 3)), group((1, 2)))
    if reverse:
        group_generators = tuple(reversed(group_generators))
    cover = group.free_cover(group_generators)
    cosets = FiniteGSets(group).pointed_orbit(
        subgroup, ZZ(1), lambda element, point: element(point), cover,
    )
    schreier = cosets.schreier_generating_morphism()
    image = tuple(schreier(letter) for letter in schreier.domain().group_generators())
    assert group.subgroup(image).cardinality() == cardinal(2)
    assert all(element(ZZ(1)) == ZZ(1) for element in image)
    section = cosets.representative_map()
    assert all(section(point)(ZZ(1)) == point for point in cosets)

