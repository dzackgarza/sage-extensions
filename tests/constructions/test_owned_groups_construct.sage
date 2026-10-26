r"""The owned group API recovers standard invariants and subgroup constructions of S3."""

from sage_extensions.all import *  # noqa: F401,F403


def test_symmetric_three_exposes_owned_group_invariants() -> None:
    group = Groups.S(3)
    transposition = next(g for g in group.group_generators() if g.order() == 2)
    identity = group.Mor(group).identity()
    endomorphisms = group.End()

    assert group in OwnedGroups()
    assert group.cardinality() == cardinal(6)
    assert group.order() == 6
    assert group.center().order() == 1
    assert group.centralizer(transposition).order() == 2
    assert group.commutator_subgroup().order() == 3
    assert group.derived_subgroup() == group.commutator_subgroup()
    assert group.Aut().order() == 6
    assert endomorphisms.identity() == identity
    assert group.inclusion().domain() is group
    assert group.inclusion().codomain() is group
    assert not group.is_abelian()
    assert group.is_finite()
    assert group.is_finitely_generated()
    assert group.is_finitely_presented()
    assert group.is_isomorphic_to(Groups.D(3))
    assert group.order_is_invertible_in(QQ)
    assert not group.order_is_invertible_in(GF(3))
    assert group.subgroups().cardinality() == cardinal(6)
    assert group.supergroup() is group
    assert transposition.cyclic_subgroup().order() == 2
    assert transposition * transposition.inverse() == group.one()


def test_symmetric_three_constructs_subgroups_by_generators_and_predicates() -> None:
    group = Groups.S(3)
    transposition = next(g for g in group.group_generators() if g.order() == 2)
    generated = group.subgroup((transposition,))
    three_torsion = group.predicate_subgroup(
        lambda g: g**3 == group.one(),
        "elements whose cube is the identity",
    )

    assert generated.order() == 2
    assert three_torsion.order() == 3
    assert three_torsion.is_abelian()


def test_group_classifying_category_has_one_object() -> None:
    classifying = Groups.S(3).classifying_category()

    assert classifying in Cat()
    assert classifying.object_set().cardinality() == cardinal(1)


def test_integral_special_linear_group_is_arithmetic() -> None:
    assert Groups.SL(2, ZZ).is_arithmetic_group()
