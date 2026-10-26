r"""A finitely presented group computed from its presentation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_commuting_generators_of_orders_two_and_three_present_c6() -> None:
    r"""$\langle a, b \mid a^2, b^3, aba^{-1}b^{-1}\rangle \cong C_2 \times C_3 \cong C_6$; $S_3$ needs the relation $(ab)^2$ instead."""
    free = Groups.Free(2)
    a, b = free.group_generators()[0], free.group_generators()[1]
    commuting = free.quotient_by_relators((a**2, b**3, a * b * ~a * ~b))
    dihedral = free.quotient_by_relators((a**2, b**3, (a * b) ** 2))

    assert commuting.order() == 6
    assert commuting.is_abelian()
    assert commuting.is_isomorphic_to(Groups.C(6))
    assert dihedral.order() == 6
    assert not dihedral.is_abelian()
    assert dihedral.is_isomorphic_to(Groups.S(3))
