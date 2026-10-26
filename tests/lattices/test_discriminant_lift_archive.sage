r"""Lifting discriminant-form automorphisms to lattice isometries.

``rho_L: O(L) -> O(A_L)`` is the discriminant representation.  The lifts
along it and the factorization ``g = s l`` of an isometry through
``1 -> ker(rho_L) -> O(L) -> rho_L(O(L)) -> 1`` are operations of ``O(L)``
for every lattice ``L`` (owner ruling 2026-10-15).
"""

import pytest

from sage_extensions.all import *


def test_O_A2_surjects_onto_O_of_its_discriminant_form() -> None:
    r"""disc(A2) = Z/3 with q = +-2/3 mod 2, so O(q_{A2}) = {+-1} has order 2;
    the nontrivial element -1 is induced by the isometry -1 of A2, so
    O(A2) -> O(q_{A2}) is surjective."""
    lattice = Lattices(ZZ)("A2")
    form = lattice.discriminant_group()
    form_isometries = form.orthogonal_group()
    generator = form.module_generators()[0]

    assert form_isometries.cardinality() == 2
    assert lattice.O().discriminant_image().cardinality() == 2

    target = [g for g in form_isometries if g != form_isometries.one()][0]
    assert target(generator) == -generator

    lifted = lattice.O().discriminant_lift(target)
    assert lifted in lattice.O()
    assert lifted.discriminant_morphism() == target


def test_the_group_generators_of_O_q_A2_lift_to_O_A2() -> None:
    r"""O(q_{A2}) = {+-1} (above), and -1 is induced by the isometry -1 of A2, so
    each group generator of O(q_{A2}) has a lift, inducing that generator."""
    lattice = Lattices(ZZ)("A2")
    target = lattice.discriminant_group().orthogonal_group()
    lifts = lattice.O().discriminant_orthogonal_group_generator_lifts()

    group_generators = target.group_generators()
    assert lifts.index_set() == group_generators.index_set()
    for label in lifts.index_set():
        assert lifts.value(label) in lattice.O()
        assert lifts.value(label).discriminant_morphism() == group_generators.value(label)


def test_minus_one_on_A2_factors_through_the_stable_orthogonal_group() -> None:
    r"""-1 acts on A_{A2} = Z/3 as -1, which is not the identity, so -1 is not
    stable.  Its factorization g = s l has s in ker(rho), l inducing -1 on A_L,
    and s l = -1."""
    lattice = Lattices(ZZ)("A2")
    group = lattice.O()
    minus_one = group(tuple(-generator for generator in lattice.module_generators()))
    stable_factor, lift = group.discriminant_factorization(minus_one)

    assert minus_one.discriminant_morphism() != lattice.discriminant_group().orthogonal_group().one()
    assert stable_factor in lattice.stable_orthogonal_group()
    assert stable_factor.discriminant_morphism() == lattice.discriminant_group().orthogonal_group().one()
    assert lift.discriminant_morphism() == minus_one.discriminant_morphism()
    assert group(stable_factor) * lift == minus_one


def test_a_root_reflection_of_A2_factors_with_a_stable_factor() -> None:
    r"""For a root r of A2 and x in the dual lattice, s_r(x) - x = -b(x, r) r lies in
    A2 since b(x, r) is an integer, so s_r acts trivially on A_{A2}; its lift
    therefore induces the identity, and s l = s_r."""
    lattice = Lattices(ZZ)("A2")
    group = lattice.O()
    reflection = group(lattice.reflection(lattice.module_generator(0)))
    stable_factor, lift = group.discriminant_factorization(reflection)

    assert stable_factor in lattice.stable_orthogonal_group()
    assert lift.discriminant_morphism() == lattice.discriminant_group().orthogonal_group().one()
    assert group(stable_factor) * lift == reflection


def test_O_of_the_rank_one_lattice_30_is_not_onto_O_of_its_discriminant_form() -> None:
    r"""For L = <30>, A_L = Z/30 with q(x/30) = x^2/30 mod 2, and a unit u acts
    isometrically exactly when u^2 = 1 mod 60: u in {1, 11, 19, 29}, so
    O(A_L) = {1, 11, 19, 29}, of order 4 (7, 13, 17, 23 square to 49 mod 60).
    O(L) = {+-1} has image {1, 29}, a proper subgroup, so every generating set
    of O(A_L) has an element outside the image and the generator lifts assert;
    every isometry still factors, since its own image lies in the image."""
    lattice = Lattices(ZZ)([[30]])
    group = lattice.O()

    assert lattice.discriminant_group().orthogonal_group().cardinality() == 4
    assert group.discriminant_image().cardinality() == 2
    with pytest.raises(AssertionError):
        group.discriminant_orthogonal_group_generator_lifts()

    minus_one = group(tuple(-generator for generator in lattice.module_generators()))
    stable_factor, lift = group.discriminant_factorization(minus_one)
    assert stable_factor in lattice.stable_orthogonal_group()
    assert lift.discriminant_morphism() == minus_one.discriminant_morphism()
    assert group(stable_factor) * lift == minus_one
