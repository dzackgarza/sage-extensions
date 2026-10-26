r"""The additive and multiplicative group schemes are internal groups in schemes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_additive_group_scheme_has_addition_unit_and_negation_as_group_laws() -> None:
    groups = Grp(Schemes(QQ))
    additive = groups.additive_group()
    x = additive.coordinate_ring().gen()
    multiplication = additive.multiplication()
    left = multiplication.domain().projection(0)
    right = multiplication.domain().projection(1)

    assert additive in groups
    assert multiplication.pullback(x) == left.pullback(x) + right.pullback(x)
    assert additive.unit_morphism().pullback(x) == 0
    assert additive.inverse_morphism().pullback(x) == -x


def test_multiplicative_group_scheme_has_multiplication_unit_and_inverse_as_group_laws() -> None:
    groups = Grp(Schemes(QQ))
    multiplicative = groups.multiplicative_group()
    u = multiplicative.coordinate_ring().gen()
    multiplication = multiplicative.multiplication()
    left = multiplication.domain().projection(0)
    right = multiplication.domain().projection(1)

    assert multiplicative in groups
    assert multiplication.pullback(u) == left.pullback(u) * right.pullback(u)
    assert multiplicative.unit_morphism().pullback(u) == 1
    assert multiplicative.inverse_morphism().pullback(u) == u**-1


def test_mu_two_changes_from_etale_to_nonreduced_in_characteristic_two() -> None:
    over_qq = Grp(Schemes(QQ)).roots_of_unity(2)
    over_f2 = Grp(Schemes(GF(2))).roots_of_unity(2)

    assert over_qq.degree() == 2
    assert over_qq.is_reduced()
    assert over_qq.structure_morphism().is_etale()
    assert over_f2.degree() == 2
    assert not over_f2.is_reduced()
    assert not over_f2.structure_morphism().is_etale()
