r"""Open subgroups of the absolute Galois group of a finite field."""

from sage_extensions.all import *


def test_the_open_subgroup_of_the_galois_group_of_f5_fixing_f25_has_index_two() -> None:
    r"""$G_{\mathbb{F}_5} \cong \hat{\mathbb{Z}}$; the open subgroup fixing $\mathbb{F}_{5^n}$ is $n\hat{\mathbb{Z}}$, of index $n$."""
    group = GF(5).absolute_galois_group()
    subgroup = group.open_subgroup(group.finite_extension(2))

    assert subgroup.index() == 2
    assert subgroup.fixed_field().cardinality() == 25


def test_open_subgroups_of_the_abelian_galois_group_of_f5_are_their_own_conjugacy_classes() -> None:
    r"""$G_{\mathbb{F}_5} \cong \hat{\mathbb{Z}}$ is abelian, so the conjugacy class of the index-3 open subgroup is a singleton."""
    group = GF(5).absolute_galois_group()
    conjugacy_class = group.open_subgroup_class(group.finite_extension(3))

    assert conjugacy_class.cardinality() == 1
    assert conjugacy_class.representative().index() == 3
    assert conjugacy_class.representative().fixed_field().cardinality() == 125
