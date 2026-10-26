r"""Constructions on groups: products, centres, commutator subgroups, free products, subgroups, characters."""

from sage_extensions.all import *


def test_finite_group_product_retains_group_structure_and_order() -> None:
    product = Groups().product((Groups.C(2), Groups.C(3)))

    assert product in Groups()
    assert product.order() == 6
    assert product.is_isomorphic_to(Groups.C(6))


def test_finite_group_centers_are_owned_subgroups() -> None:
    symmetric = Groups.S(3)
    cyclic = Groups.C(2)

    assert symmetric.center().order() == 1
    assert symmetric.center().supergroup() is symmetric
    assert cyclic.center().order() == 2
    assert cyclic.center().supergroup() is cyclic


def test_finite_group_commutator_subgroups_are_owned() -> None:
    symmetric = Groups.S(3)
    cyclic = Groups.C(4)

    assert symmetric.commutator_subgroup().order() == 3
    assert symmetric.commutator_subgroup().supergroup() is symmetric
    assert cyclic.commutator_subgroup().order() == 1
    assert cyclic.commutator_subgroup().supergroup() is cyclic


def test_group_coproduct_is_the_owned_free_product() -> None:
    coproduct = Groups().coproduct((Groups.C(2), Groups.C(3)))

    assert coproduct in Groups()
    assert coproduct.cardinality() == aleph0
    assert coproduct.group_generators().cardinality() == 2


def test_group_coproduct_factorization_extends_the_factor_maps() -> None:
    two = Groups.C(2)
    three = Groups.C(3)
    target = Groups.S(3)
    construction = Groups().coproduct_construction((two, three))
    diagram = construction.diagram()
    first_index = diagram.domain()(0)
    second_index = diagram.domain()(1)
    two_generator = two.group_generators()[0]
    three_generator = three.group_generators()[0]
    first = two.Mor(target)({two_generator: target((1, 2))})
    second = three.Mor(target)({three_generator: target((1, 2, 3))})
    cocone = (diagram).CoproductCocones().cocone(
        target,
        lambda index: first if index is first_index else second,
    )

    factor = construction.factor(cocone).apex_map()
    first_injection = construction.costructure_morphism(first_index)
    second_injection = construction.costructure_morphism(second_index)
    assert factor(first_injection(two_generator)) == first(two_generator)
    assert factor(second_injection(three_generator)) == second(three_generator)


def test_finite_group_subgroups_are_owned_and_keep_the_ambient_group() -> None:
    cyclic = Groups.C(6)
    subgroups = cyclic.subgroups()

    assert subgroups in FiniteSets()
    assert subgroups.cardinality() == 4
    assert {int(subgroup.cardinality()) for subgroup in subgroups} == {1, 2, 3, 6}
    assert all(subgroup in Subgroups(cyclic) for subgroup in subgroups)
    assert all(subgroup.supergroup() is cyclic for subgroup in subgroups)
    assert all(subgroup.inclusion().codomain() is cyclic for subgroup in subgroups)
    assert all(subgroup.group_generators().cardinality().is_finite() for subgroup in subgroups)


def test_the_three_cycle_generates_the_index_two_subgroup_a3_of_s3() -> None:
    r"""$\langle (1\,2\,3) \rangle = A_3$ has order 3 and index 2 in $S_3$, so $S_3 / A_3 \cong C_2$."""
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2, 3)),))

    assert subgroup.order() == 3
    assert group((1, 3, 2)) in subgroup
    assert group((1, 2)) not in subgroup
    assert subgroup.inclusion().cokernel().is_isomorphic_to(Groups.C(2))


def test_conjugation_on_d4_has_the_centre_as_kernel_and_inner_group_v4() -> None:
    r"""$\ker(G \to \operatorname{Aut} G) = Z(G)$; for $D_4$ of order 8, $|Z| = 2$ and $\operatorname{Inn}(D_4) \cong V_4$, of index 2 in $\operatorname{Aut}(D_4)$ of order 8 (Dummit--Foote 4.4)."""
    group = Groups.D(4)
    conjugation = group.conjugation_morphism()

    assert conjugation.kernel().order() == 2
    assert conjugation.image().is_isomorphic_to(Groups.V4())
    assert group.Aut().order() == 8
    assert not conjugation.is_surjective()


def test_conjugation_on_s3_is_an_isomorphism_onto_its_automorphism_group() -> None:
    r"""$Z(S_3) = 1$ and every automorphism of $S_3$ is inner."""
    conjugation = Groups.S(3).conjugation_morphism()

    assert conjugation.is_injective()
    assert conjugation.is_surjective()


def test_the_endomorphism_ring_of_z_mod_3_is_the_field_f3() -> None:
    r"""$\operatorname{End}(\mathbb{Z}/3) \cong \mathbb{F}_3$: three elements, and $2 \cdot 2 = 4 = 1$."""
    group = Groups.Abelian([3])
    endomorphisms = group.endomorphism_ring()
    one = endomorphisms.one()
    twice = one + one

    assert endomorphisms.cardinality() == 3
    assert twice != one
    assert twice * twice == one
    assert twice + one == endomorphisms.zero()


def test_the_exponent_of_z2_times_z4_is_four() -> None:
    r"""$4x = 0$ for every $x \in \mathbb{Z}/2 \times \mathbb{Z}/4$, while $2x \neq 0$ for a generator of the $\mathbb{Z}/4$ factor."""
    group = Groups.Abelian([2, 4])

    assert all(group.scalar_multiple(ZZ(4), x) == group.one() for x in group)
    assert any(group.scalar_multiple(ZZ(2), x) != group.one() for x in group)


def test_the_discriminant_group_of_a2_is_cyclic_of_order_three() -> None:
    r"""$\det A_2 = 3$, so $A_2^\vee / A_2 \cong \mathbb{Z}/3$ (Conway--Sloane, SPLAG, 4.6.1)."""
    discriminant = Lattices(ZZ)("A2").discriminant_group()

    assert discriminant.cardinality() == 3
    assert all(discriminant.scalar_multiple(ZZ(3), x) == discriminant.zero() for x in discriminant)
    assert any(x.additive_order() == 3 for x in discriminant)


def test_archived_finite_group_character_surface_is_live_on_the_owned_group() -> None:
    group = Groups.S(3)
    representatives = group.conjugacy_classes_representatives()
    irreducibles = group.irreducible_characters()
    trivial = group.trivial_character()

    assert representatives.cardinality() == irreducibles.cardinality()
    assert trivial in irreducibles
    assert all(trivial(representative) == 1 for representative in representatives)
