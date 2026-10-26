r"""Open subgroups of $G_{\mathbb{F}_5}$ correspond to finite extensions of $\mathbb{F}_5$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_subgroup_fixing_f25_is_normal_of_index_two() -> None:
    r"""$G_{\mathbb{F}_{25}} \trianglelefteq G_{\mathbb{F}_5}$ has index $2$, excludes $\mathrm{Frob}_5$, and its own Frobenius is $\mathrm{Frob}_5^2$."""
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()
    subgroup = group.open_subgroup(group.finite_extension(2))

    assert subgroup.index() == 2
    assert subgroup.is_normal()
    assert frobenius not in subgroup
    assert frobenius**2 in subgroup
    assert subgroup.inclusion()(subgroup.frobenius()) == frobenius**2
    assert subgroup.fixed_field().cardinality() == 25


def test_the_subgroups_fixing_f25_and_f125_meet_in_index_six() -> None:
    r"""$G_{\mathbb{F}_{25}} \cap G_{\mathbb{F}_{125}} = G_{\mathbb{F}_{5^6}}$ has index $\operatorname{lcm}(2, 3) = 6$."""
    group = GF(5).absolute_galois_group()
    index_two = group.open_subgroup(group.finite_extension(2))
    index_three = group.open_subgroup(group.finite_extension(3))
    intersection = index_two.intersection(index_three)

    assert intersection.index() == 6
    assert intersection <= index_two
    assert intersection <= index_three
    assert intersection.fixed_field().cardinality() == 5**6
