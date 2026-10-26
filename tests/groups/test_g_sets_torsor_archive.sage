r"""Finite $G$-sets and torsors."""

from sage_extensions.all import *


def test_the_equivariant_self_maps_of_the_regular_c3_set_are_its_three_translations() -> None:
    r"""$\operatorname{Hom}_G(G, X) \cong X$ (Yoneda), so $|\operatorname{End}_{C_3}(C_3)| = 3$; on the trivial $C_3$-set of 3 points every one of the $3^3 = 27$ maps is equivariant."""
    group = Groups.C(3)
    regular = FiniteGSets(group)(tuple(group), lambda g, x: g * x)
    trivial = FiniteGSets(group).trivial((1, 2, 3))

    assert regular.Mor(regular).cardinality() == 3
    assert trivial.Mor(trivial).cardinality() == 27
    assert trivial.Mor(regular).cardinality() == 0


def test_the_transporter_of_the_regular_c3_torsor_from_x_to_gx_is_g() -> None:
    r"""In a torsor the element carrying $x$ to $y$ exists and is unique."""
    group = Groups.C(3)
    torsor = Torsors(group)(FiniteGSets(group)(tuple(group), lambda g, x: g * x))
    (g,) = group.group_generators()
    x = torsor.an_element()

    assert torsor.cardinality() == 3
    assert torsor.transporter(x, torsor.act(g, x)) == g
    assert torsor.transporter(x, torsor.act(g**2, x)) == g**2
    assert torsor.transporter(x, x) == group.one()
