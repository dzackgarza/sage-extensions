r"""The group law of a permutation group is composition, and its permutation modules are left modules."""

from sage_extensions.all import *


def test_the_product_of_two_transpositions_in_s3_is_their_composite_three_cycle() -> None:
    r"""$(1\,2)\circ(2\,3) = (1\,2\,3)$: $1 \mapsto 1 \mapsto 2$, $2 \mapsto 3 \mapsto 3$, $3 \mapsto 2 \mapsto 1$."""
    group = Groups.S(3)

    assert group((1, 2)) * group((2, 3)) == group((1, 2, 3))
    assert group((2, 3)) * group((1, 2)) == group((1, 3, 2))


def test_the_natural_permutation_module_of_s3_has_character_3_1_0() -> None:
    r"""$\chi(g)$ counts the fixed points of $g$ on $\{1,2,3\}$, and $\mathbb{Q}^3$ has invariants $\mathbb{Q}(1,1,1)$ (Serre, *Linear representations of finite groups*, 2.3)."""
    group = Groups.S(3)
    module = Modules(QQ)(QQ**3)

    def act(g, vector):
        return module.Mor(module)(
            {i: module.module_generator(int(g(i + 1)) - 1) for i in range(3)}
        )(vector)

    permutation = Modules(QQ[group])(module, act)
    character = permutation.character()

    assert character(group.one()) == 3
    assert character(group((1, 2))) == 1
    assert character(group((1, 2, 3))) == 0
    left, right = group((1, 2)), group((2, 3))
    assert permutation.action_of(left * right) == (
        permutation.action_of(left) * permutation.action_of(right)
    )
    assert permutation.module_invariants().module_rank() == 1


def test_the_standard_presentations_of_s3_d4_a4_present_groups_of_orders_6_8_12() -> None:
    r"""A group's chosen finite presentation presents a group isomorphic to it."""
    for group, order in ((Groups.S(3), 6), (Groups.D(4), 8), (Groups.A(4), 12)):
        presented = group.presentation()
        assert presented.order() == order
        assert presented.is_isomorphic_to(group)


def test_a4_acts_transitively_on_four_points_with_cyclic_point_stabilizers_of_order_three() -> None:
    r"""Orbit-stabilizer: $|A_4| = 12 = 4 \cdot 3$, and $\operatorname{Stab}(1) = \langle (2\,3\,4) \rangle \cong C_3$."""
    group = Groups.A(4)
    stabilizer = group.stabilizer(1)

    assert group.orbit(1).cardinality() == 4
    assert stabilizer.order() == 3
    assert stabilizer.is_isomorphic_to(Groups.C(3))
    assert group((2, 3, 4)) in stabilizer
    assert group((1, 2, 3)) not in stabilizer
