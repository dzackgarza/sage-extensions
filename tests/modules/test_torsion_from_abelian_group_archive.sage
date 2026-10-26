r"""Cyclic groups of order six."""

from sage_extensions.all import *  # noqa: F401,F403


def test_g2_and_g3_generate_the_cyclic_group_of_order_6() -> None:
    r"""$\gcd(2, 3) = 1$, so $\langle g^2, g^3 \rangle = \langle g \rangle = C_6$; as a $\mathbb Z$-module,
    $\langle 2, 3 \rangle = \mathbb Z/6$ with invariant factor $6$.

    Source: by hand (Bezout: 1 = 3 - 2).
    """
    G = Groups.C(6)
    g = G.group_generators()[0]
    assert G.subgroup([g**2, g**3]).order() == 6
    assert G.subgroup([g**2]).order() == 3

    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    e = M.module_generator(0)
    generated = M.submodule([2 * e, 3 * e])
    assert generated.cardinality() == 6
    assert tuple(generated.invariant_factors()) == (6,)


def test_z_mod_2_plus_z_mod_3_is_cyclic_of_order_6() -> None:
    r"""$\mathbb Z/2 \oplus \mathbb Z/3 \cong \mathbb Z/6$ by the Chinese remainder theorem; its invariant factors
    are $(6)$ and its elementary divisors $2, 3$.

    Source: Lang, Algebra, I.8 and III.7.
    """
    F = ZZ**2
    M = F / F.submodule([2 * F.module_generator(0), 3 * F.module_generator(1)])
    assert M.cardinality() == 6
    assert tuple(M.invariant_factors()) == (6,)
    assert M.is_isomorphic(Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6))))
