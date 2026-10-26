r"""Subgroups of the symmetric group on three letters cut out by predicates."""

from sage_extensions.all import *  # noqa: F401,F403


def test_even_permutations_of_s3_form_the_normal_subgroup_of_order_three() -> None:
    r"""$A_3 = \{g \in S_3 : \operatorname{sgn} g = 1\}$ has order 3 and index 2."""
    group = Groups.S(3)
    alternating = group.predicate_subgroup(lambda g: g.sign() == 1, "sgn(g) = 1")

    assert alternating.cardinality() == 3
    assert group.cardinality() / alternating.cardinality() == 2
    assert all(g.order() in (1, 3) for g in alternating)
    assert alternating.is_normal()


def test_centralizers_in_s3_have_orders_given_by_the_class_equation() -> None:
    r"""$|C_{S_3}(g)| = 6/|\mathrm{cl}(g)|$: 2 for a transposition, 3 for a 3-cycle.

    The class equation of $S_3$ is $6 = 1 + 3 + 2$.
    """
    group = Groups.S(3)
    transposition = next(g for g in group if g.order() == 2)
    three_cycle = next(g for g in group if g.order() == 3)

    assert group.centralizer(transposition).cardinality() == 2
    assert group.centralizer(three_cycle).cardinality() == 3
    assert group.centralizer(group.one()).cardinality() == 6
