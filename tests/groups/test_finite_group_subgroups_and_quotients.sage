r"""Centres, commutator subgroups, cosets, centralizers and products of small finite groups.

Every value is a hand computation from the multiplication law of the group:
$Z(Q_8) = [Q_8, Q_8] = \{\pm 1\}$; in $D_4$ (order $8$) the centre and the
commutator subgroup are both $\{1, r^2\}$; $[A_4, A_4] = V_4$ and
$Z(A_4) = 1$; a transposition of $S_3$ has index $3$, so three left and three
right cosets; the centralizer of a $3$-cycle in $S_3$ is $A_3$.  The product
claims are the universal property of $C_2 \times C_3$ in $\mathbf{Grp}$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_quaternion_group_has_centre_and_commutator_subgroup_plus_minus_one() -> None:
    group = Groups.Q()

    assert group.order() == 8
    assert not group.is_abelian()
    assert group.center().order() == 2
    assert group.commutator_subgroup().order() == 2


def test_the_dihedral_group_of_order_eight_has_centre_and_derived_subgroup_of_order_two() -> None:
    group = Groups.D(4)

    assert group.order() == 8
    assert group.center().order() == 2
    assert group.derived_subgroup().order() == 2


def test_the_derived_subgroup_of_a4_is_the_klein_four_group_and_its_centre_is_trivial() -> None:
    group = Groups.A(4)

    assert group.order() == 12
    assert group.commutator_subgroup().order() == 4
    assert group.commutator_subgroup().is_isomorphic_to(Groups.V4())
    assert group.center().order() == 1


def test_a_transposition_of_s3_has_three_left_and_three_right_cosets() -> None:
    r"""$[S_3 : \langle (1\,2) \rangle] = 3$."""
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    left = group.left_cosets(subgroup)

    assert left.cardinality() == cardinal(3)
    assert left in FiniteGSets(group)
    assert group.one() in left.base_point()
    assert left.projection().codomain() is left
    assert left.is_transitive_action()
    assert group.right_cosets(subgroup).cardinality() == cardinal(3)


def test_centralizers_in_s3_and_the_invertibility_of_its_order() -> None:
    r"""$C_{S_3}((1\,2\,3)) = A_3$, $C_{S_3}((1\,2)) = \langle (1\,2) \rangle$; $6$ is a unit in $\mathbb{Q}$ and not in $\mathbb{Z}$."""
    group = Groups.S(3)

    assert group.centralizer(group((1, 2, 3))).order() == 3
    assert group.centralizer(group((1, 2))).order() == 2
    assert group.order_is_invertible_in(QQ)
    assert not group.order_is_invertible_in(ZZ)


def test_the_product_of_c2_and_c3_is_c6_and_factors_the_two_reductions_of_c6() -> None:
    r"""$C_2 \times C_3 \cong C_6$ with kernels of the projections of orders $3$ and $2$.

    The reductions $C_6 \to C_2$ and $C_6 \to C_3$ factor through the product
    by a map $u$ with $p_i \circ u$ the given reductions; $u$ is the
    isomorphism of the Chinese remainder theorem.
    """
    two = Groups.C(2)
    three = Groups.C(3)
    six = Groups.C(6)
    construction = Groups().product_construction((two, three))
    diagram = construction.diagram()
    first = diagram.domain()(0)
    second = diagram.domain()(1)
    first_projection = construction.structure_morphism(first)
    second_projection = construction.structure_morphism(second)
    generator = six.group_generators()[0]
    to_two = six.Mor(two)({generator: two.group_generators()[0]})
    to_three = six.Mor(three)({generator: three.group_generators()[0]})
    cone = diagram.ProductCones().cone(six, lambda index: to_two if index is first else to_three)
    factor = construction.factor(cone).apex_map()

    assert construction.object().order() == 6
    assert construction.object().is_isomorphic_to(six)
    assert first_projection.kernel().order() == 3
    assert second_projection.kernel().order() == 2
    assert first_projection(factor(generator)) == to_two(generator)
    assert second_projection(factor(generator)) == to_three(generator)
    assert factor.is_injective()
    assert factor.is_surjective()


def test_reduction_from_c4_to_c2_has_kernel_image_preimages_and_lifts() -> None:
    r"""$C_4 \to C_2$, $g \mapsto h$: kernel $\langle g^2 \rangle$ of order $2$, onto, the preimage of $C_2$ is $C_4$.

    Every element of $C_2$ has a lift, and the lift maps back to it.
    """
    four = Groups.C(4)
    two = Groups.C(2)
    generator = four.group_generators()[0]
    target = two.group_generators()[0]
    reduction = four.Mor(two)({generator: target})
    lifts = four.finite_image_lifts(reduction)

    assert reduction.kernel().order() == 2
    assert reduction.image().order() == 2
    assert reduction.is_surjective()
    assert not reduction.is_injective()
    assert reduction.preimage_subgroup(two).order() == 4
    assert reduction.preimage_subgroup(two.subgroup((two.one(),))).order() == 2
    assert reduction(reduction.lift(target)) == target
    assert set(lifts) == set(two)
    assert all(reduction(witness) == image for image, witness in lifts.items())


def test_the_conjugacy_class_of_a_transposition_in_s3_has_three_elements() -> None:
    r"""$|\mathrm{cl}((1\,2))| = [S_3 : C_{S_3}((1\,2))] = 6 / 2 = 3$; $S_3$ has three classes."""
    group = Groups.S(3)

    assert group.conjugacy_classes_representatives().cardinality() == cardinal(3)
    assert group.conjugacy_class(group((1, 2))).cardinality() == cardinal(3)


def test_the_cokernel_of_the_inclusion_of_a3_in_s3_is_c2() -> None:
    r"""$A_3 \trianglelefteq S_3$ has index $2$, so $S_3 / A_3 \cong C_2$."""
    group = Groups.S(3)
    alternating = group.subgroup((group((1, 2, 3)),))
    cosets = group.left_cosets(alternating)
    comparison = cosets.normal_quotient_comparison()

    assert alternating.inclusion().cokernel().order() == 2
    assert comparison.codomain().order() == 2
    assert comparison(cosets.base_point()) == comparison.codomain().one()


def test_a_finite_group_morphism_has_its_image_coset_cokernel_as_a_pointed_set() -> None:
    r"""For $C_2 \to S_3$ with image a transposition, $S_3/f(C_2)$ has three points."""
    source = Groups.C(2)
    target = Groups.S(3)
    morphism = source.Mor(target)(
        {source.group_generators()[0]: target((1, 2))}
    )
    cosets = morphism.coset_cokernel()

    assert cosets.cardinality() == cardinal(3)
    assert morphism.coset_cokernel_projection().codomain() is cosets
    assert target.one() in cosets.base_point()


def test_the_abelianization_of_s3_is_c2() -> None:
    r"""$[S_3, S_3] = A_3$, so $S_3^{\mathrm{ab}} = S_3 / A_3 \cong C_2$."""
    assert Groups().abelianization()(Groups.S(3)).order() == 2
