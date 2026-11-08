r"""The stable component subgroup of O(A1 cubed) has three norm -2 axis orbits.

Even sign changes take each root to its negative. They fix all three
basis half-classes in the discriminant, so they cannot exchange axes.
"""

from sage_extensions.all import *


def test_stable_component_norm_minus_two_orbits_retain_every_axis_class():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    basis = tuple(lattice.module_generators())
    subgroup = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    representatives = subgroup.vector_orbit_representatives(ZZ(-2))
    assert representatives.cardinality() == cardinal(3)
    assert all(point.q() == ZZ(-2) and point.is_primitive() for point in representatives)
    assert {lattice.divided_discriminant_class(point) for point in representatives} == {
        lattice.divided_discriminant_class(point) for point in basis
    }


def test_supplied_root_stabilizers_split_every_axis_into_the_same_three_classes():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    basis = tuple(lattice.module_generators())
    group = lattice.O()
    subgroup = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    quotient = subgroup.finite_character_quotient()
    expected = {lattice.divided_discriminant_class(point) for point in basis}
    for fixed in range(3):
        moving = tuple(position for position in range(3) if position != fixed)
        first, second = moving
        flip_first = tuple(-point if position == first else point for position, point in enumerate(basis))
        flip_second = tuple(-point if position == second else point for position, point in enumerate(basis))
        exchange = list(basis)
        exchange[first], exchange[second] = exchange[second], exchange[first]
        stabilizer = tuple(group(images) for images in (flip_first, flip_second, tuple(exchange)))
        assert all(element(basis[fixed]) == basis[fixed] for element in stabilizer)
        lifts = quotient.splitting_isometries(stabilizer)
        assert lifts.cardinality() == cardinal(3)
        assert {lattice.divided_discriminant_class(lift(basis[fixed])) for lift in lifts} == expected


def test_stable_component_norm_minus_four_orbits_retain_every_pair_of_axes():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root + root
    basis = tuple(lattice.module_generators())
    subgroup = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    representatives = subgroup.vector_orbit_representatives(ZZ(-4))
    assert representatives.cardinality() == cardinal(6)
    assert all(point.q() == ZZ(-4) and point.is_primitive() for point in representatives)
    assert {lattice.divided_discriminant_class(point) for point in representatives} == {
        lattice.divided_discriminant_class(basis[i] + basis[j]) for i in range(4) for j in range(i + 1, 4)
    }


def test_nonnormal_joint_conditions_split_a_based_pair_into_exactly_three_orbits():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    e, f, h = basis = tuple(lattice.module_generators())
    group = lattice.O()
    rho = lattice.discriminant_representation()
    target = rho.codomain().subgroup((rho(group((e, h, f))),))
    subgroup = lattice.SO().intersection(group.discriminant_preimage(target))
    exchange = group((f, e, h))
    assert exchange(e + f) == e + f and exchange(h) == h
    known = group((-e, h, f))
    assert known in subgroup
    quotient = subgroup.finite_character_quotient()
    lifts = quotient.splitting_isometries((exchange,))
    assert lifts.cardinality() == cardinal(3)
    character = quotient.character_representation()
    identity = character(group.one())
    left = (identity, character(known))
    right = (identity, character(exchange))

    def double_coset(element):
        image = character(element)
        return frozenset(a * image * b for a in left for b in right)

    group_elements = []
    for order in Permutations(3):
        images = tuple(basis[int(position) - 1] for position in order)
        group_elements.extend((group(images), group((-images[0], images[1], images[2]))))
    assert {double_coset(lift) for lift in lifts} == {double_coset(element) for element in group_elements}
    assert all((~lift)(lift(point)) == point for lift in lifts for point in basis)
    assert all(lattice.b(lift(x), lift(y)) == lattice.b(x, y) for lift in lifts for x in basis for y in basis)
