from sage_extensions.all import *


def s3():
    return Groups.S(3)


def test_the_automorphisms_of_a_three_element_set() -> None:
    r"""$S_3 = \operatorname{Aut}_{\mathbf{Set}}(\{0, 1, 2\})$."""
    assert Sets.Δ[2].Aut().is_isomorphic_to(s3())


def test_the_set_category_automorphism_group_agrees() -> None:
    assert Sets().Aut(Sets.Δ[2]) == Sets.Δ[2].Aut()


def test_the_dihedral_group_of_the_triangle() -> None:
    assert Groups.D(3).is_isomorphic_to(s3())


def test_the_weyl_group_of_a2() -> None:
    assert Groups.Weyl(["A", 2]).is_isomorphic_to(s3())


def test_the_coxeter_presentation() -> None:
    r"""$\langle a, b \mid a^2, b^3, (ab)^2\rangle \cong S_3$."""
    free = Groups.Free(2)
    a, b = free.group_generators()
    presented = free.quotient_by_relators([a ^ 2, b ^ 3, (a * b) ^ 2])
    assert presented.order() == 6
    assert presented.is_isomorphic_to(s3())


def test_the_categories_of_s3() -> None:
    group = s3()
    assert group in Groups()
    assert group in FiniteGroups()
    assert group in FinitelyGeneratedGroups()
    assert group in FinitelyPresentedGroups()
    assert group not in AbelianGroups()


def test_the_invariants_of_s3() -> None:
    group = s3()
    assert group.order() == 6
    assert group.cardinality() == 6
    assert not group.is_abelian()
    assert group.center().order() == 1
    assert group.commutator_subgroup().order() == 3
    assert group.conjugacy_classes_representatives().cardinality() == 3
    assert Groups().Subobjects(group).cardinality() == 6


def test_the_abelianization_of_s3() -> None:
    r"""$[S_3, S_3] = A_3$, so $S_3^{ab} = \mathbb Z/2$."""
    assert Groups().abelianization()(s3()).order() == 2


def test_the_group_law_is_composition() -> None:
    r"""$(1\,2)\circ(2\,3)$ sends $1 \mapsto 1 \mapsto 2$, $2 \mapsto 3 \mapsto 3$, $3 \mapsto 2 \mapsto 1$: it is $(1\,2\,3)$."""
    group = s3()
    transposition = group((1, 2))
    assert transposition.order() == 2
    assert group((1, 2, 3)).order() == 3
    assert transposition * group((2, 3)) == group((1, 2, 3))
    assert transposition * transposition == group.one()


def test_the_homomorphisms_out_of_and_into_s3() -> None:
    r"""$\operatorname{Hom}(S_3, C_2)$: the trivial map and the sign; $\operatorname{Hom}(C_2, S_3)$: the identity element and three transpositions;
    $|\operatorname{End}(S_3)| = 6 + 3 + 1 = 10$ (automorphisms, maps with image of order two, the trivial map); $\operatorname{Aut}(S_3) = \operatorname{Inn}(S_3) \cong S_3$."""
    group = s3()
    assert group.Mor(Groups.C(2)).cardinality() == 2
    assert Groups.C(2).Mor(group).cardinality() == 4
    assert group.End().cardinality() == 10
    assert group.Aut().order() == 6


def test_the_natural_action_on_three_points() -> None:
    r"""$S_3$ acts transitively on $\{1, 2, 3\}$; the stabilizer of a point is $S_2$."""
    group = s3()
    natural = FiniteGSets(group)((1, 2, 3), lambda g, x: g(x))
    assert natural.fixed_points().cardinality() == 0
    assert natural.stabilizer(1).order() == 2


def test_s3_has_one_endomorphism_category() -> None:
    group = s3()
    endomorphisms = group.Mor(group)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert group.Mor(group) is endomorphisms
    assert group.End() is endomorphisms
    assert identity * identity == identity
    assert identity.domain() is group
