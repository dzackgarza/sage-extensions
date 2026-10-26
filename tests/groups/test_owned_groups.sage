r"""Standard finite groups, their subgroups and their isomorphism types."""

from sage_extensions.all import *


def test_sl2_f3_is_sp2_f3_and_modulo_its_centre_is_a4() -> None:
    r"""$|\operatorname{GL}_2(\mathbb{F}_3)| = (9-1)(9-3) = 48$, $\operatorname{SL}_2 = \operatorname{Sp}_2$, $Z(\operatorname{SL}_2(\mathbb{F}_3)) = \{\pm 1\}$ and $\operatorname{PSL}_2(\mathbb{F}_3) \cong A_4$ (Dummit--Foote 4.5, Exercise)."""
    special = Groups.SL(2, GF(3))
    centre = special.center()

    assert Groups.GL(2, GF(3)).order() == 48
    assert special.order() == 24
    assert special.is_isomorphic_to(Groups.Sp(2, GF(3)))
    assert not special.is_isomorphic_to(Groups.S(4))
    assert centre.order() == 2
    assert centre.inclusion().cokernel().is_isomorphic_to(Groups.A(4))


def test_groups_of_the_same_order_that_are_not_isomorphic() -> None:
    r"""$V_4 \not\cong C_4$; $Q_8 \not\cong D_4$ ($Q_8$ has one element of order 2, $D_4$ has five); $C_6 \not\cong S_3$."""
    assert not Groups.V4().is_isomorphic_to(Groups.C(4))
    assert not Groups.Q().is_isomorphic_to(Groups.D(4))
    assert Groups.Q().order() == Groups.D(4).order() == 8
    assert not Groups.C(6).is_isomorphic_to(Groups.S(3))
    assert Groups.D(5).order() == 10


def test_the_abelianization_of_the_free_product_of_c2_and_c3_is_c6() -> None:
    r"""$\langle a, b \mid a^2, b^3 \rangle = C_2 * C_3 \cong \operatorname{PSL}_2(\mathbb{Z})$ has abelianization $C_2 \times C_3 \cong C_6$."""
    free = Groups.Free(2)
    a, b = free.group_generators()
    presented = free.quotient_by_relators((a**2, b**3))

    assert presented.abelianization().is_isomorphic_to(Groups.C(6))


def test_the_four_cycle_generates_a_cyclic_subgroup_of_s4_of_order_four() -> None:
    r"""$\langle (1\,2\,3\,4) \rangle \cong C_4$ contains $(1\,2\,3\,4)^2 = (1\,3)(2\,4)$ and no transposition."""
    group = Groups.S(4)
    cycle = group((1, 2, 3, 4))
    subgroup = group.subgroup((cycle,))

    assert subgroup.order() == 4
    assert subgroup.is_isomorphic_to(Groups.C(4))
    assert cycle**2 in subgroup
    assert group((1, 2)) not in subgroup


def test_centralizers_of_a_transposition_and_a_four_cycle_in_s4() -> None:
    r"""$C_{S_4}((1\,2)) = \langle (1\,2), (3\,4) \rangle \cong V_4$, so $(1\,2)$ has $24/4 = 6$ conjugates; $C_{S_4}((1\,2\,3\,4)) = \langle (1\,2\,3\,4) \rangle \cong C_4$."""
    group = Groups.S(4)
    transposition_centralizer = group.centralizer(group((1, 2)))
    cycle_centralizer = group.centralizer(group((1, 2, 3, 4)))

    assert transposition_centralizer.order() == 4
    assert transposition_centralizer.inclusion().codomain() is group
    assert transposition_centralizer.group_generators().cardinality().is_finite()
    assert transposition_centralizer.is_isomorphic_to(Groups.V4())
    assert group((3, 4)) in transposition_centralizer
    assert group((1, 3)) not in transposition_centralizer
    assert cycle_centralizer.is_isomorphic_to(Groups.C(4))
