r"""Finite presentations and the groups they present."""

from sage_extensions.all import *


def test_the_coxeter_presentation_of_s3_presents_a_group_of_order_six() -> None:
    r"""$\langle a, b \mid a^2, b^2, (ab)^3 \rangle \cong S_3$ (Humphreys, *Reflection groups and Coxeter groups*, 1.9)."""
    free = Groups.Free(2)
    a, b = free.group_generators()
    presented = free.quotient_by_relators((a**2, b**2, (a * b) ** 3))

    assert presented.order() == 6
    assert presented.is_isomorphic_to(Groups.S(3))
    assert not presented.is_isomorphic_to(Groups.C(6))


def test_one_generator_and_one_square_relator_present_the_group_of_order_two() -> None:
    r"""$\langle x \mid x^2 \rangle \cong C_2 \cong S_2 \cong \mathbb{Z}/2$."""
    free = Groups.Free(1)
    (x,) = free.group_generators()
    presented = free.quotient_by_relators((x**2,))

    assert presented.order() == 2
    for group in (Groups.C(2), Groups.S(2), Groups.Abelian([2])):
        assert presented.is_isomorphic_to(group)
        assert group.presentation().is_isomorphic_to(group)
