r"""Adjunctions between sets, $G$-sets, groups and $G$-modules, measured by counting morphisms."""

from sage_extensions.all import *  # noqa: F401,F403


def _swap_two_of_three():
    r"""$C_2$ acting on $X = \{0, 1, 2\}$ by swapping $0$ and $1$: two orbits, one fixed point."""
    group = Groups.C(2)
    swapped = {ZZ(0): ZZ(1), ZZ(1): ZZ(0), ZZ(2): ZZ(2)}
    acted = Sets(group)(Sets()((ZZ(0), ZZ(1), ZZ(2))), lambda g, p: p if g == group.one() else swapped[p])
    return group, acted


def test_orbits_and_fixed_points_are_adjoint_to_the_trivial_action() -> None:
    r"""$\operatorname{Hom}_G(X, T_{\mathrm{triv}}) = \operatorname{Hom}(X/G, T)$ and $\operatorname{Hom}_G(S_{\mathrm{triv}}, X) = \operatorname{Hom}(S, X^G)$.

    With $|X/G| = 2$, $|X^G| = 1$ and $|S| = |T| = 2$ these have $2^2 = 4$ and
    $1^2 = 1$ elements.
    """
    group, acted = _swap_two_of_three()
    two_points = Sets()((ZZ(10), ZZ(20)))
    orbits = Sets(group).orbits_trivial_adjunction()
    fixed = Sets().trivial_fixed_adjunction(group)

    assert orbits.left_adjoint()(acted).cardinality() == 2
    assert fixed.right_adjoint()(acted).cardinality() == 1
    assert acted.Mor(orbits.right_adjoint()(two_points)).cardinality() == 4
    assert Sets().Mor(orbits.left_adjoint()(acted), two_points).cardinality() == 4
    assert fixed.left_adjoint()(two_points).Mor(acted).cardinality() == 1


def test_the_free_and_cofree_g_sets_are_adjoint_to_the_underlying_set() -> None:
    r"""$\operatorname{Hom}_G(G \times S, X) = X^S$ has $3^2 = 9$ elements; $\operatorname{Hom}_G(X, T^G) = T^X$ has $2^3 = 8$."""
    group, acted = _swap_two_of_three()
    two_points = Sets()((ZZ(10), ZZ(20)))
    free = Sets().free_underlying_adjunction(group).left_adjoint()(two_points)
    cofree = Sets(group).underlying_cofree_adjunction().right_adjoint()(two_points)

    assert free.cardinality() == 4
    assert cofree.cardinality() == 4
    assert free.Mor(acted).cardinality() == 9
    assert acted.Mor(cofree).cardinality() == 8


def test_a_set_map_to_c3_extends_to_the_free_group_by_evaluating_words() -> None:
    r"""$x_2 \mapsto g$, $x_3 \mapsto g^2$ gives $x_2 x_3^{-1} \mapsto g^{-1}$; on $F(\mathbb{Z})$ with $n \mapsto g^{n \bmod 3}$, $x_2 x_{-1}^{-2} x_7 \mapsto g^{2 - 4 + 1} = g^{-1}$."""
    adjunction = Sets().free_group_adjunction()
    target = Groups.C(3)
    g = target.group_generators()[0]

    source = Sets()((ZZ(2), ZZ(3)))
    free = adjunction.left_adjoint()(source)
    extension = adjunction.mor_set_isomorphism_inverse(
        Sets().Mor(source, target)(lambda point: g if point == 2 else g**2), target
    )
    assert extension(free.free_generator(2) * free.free_generator(3) ** -1) == g**-1
    assert free.Mor(target).cardinality() == 9

    free_on_integers = adjunction.left_adjoint()(ZZ)
    word = free_on_integers.free_generator(2) * free_on_integers.free_generator(-1) ** -2 * free_on_integers.free_generator(7)
    infinite_extension = adjunction.mor_set_isomorphism_inverse(
        Sets().Mor(ZZ, target)(lambda n: g ** (n % 3)), target
    )
    assert infinite_extension(word) == g**-1


def test_inducing_the_z4_sign_module_from_c2_to_s3_gives_three_copies_of_z4() -> None:
    r"""$\operatorname{Ind}_{C_2}^{S_3}$ and $\operatorname{CoInd}_{C_2}^{S_3}$ of $\mathbb{Z}/4$ are $(\mathbb{Z}/4)^{[S_3 : C_2]} = (\mathbb{Z}/4)^3$, and they agree because the index is finite.

    Source: Brown, *Cohomology of Groups*, III.5.9.
    """
    supergroup = Groups.S(3)
    transposition = next(g for g in supergroup.group_generators() if g.order() == 2)
    subgroup = supergroup.subgroup([transposition])
    sign = Modules(ZZ[subgroup])(
        Modules(ZZ).direct_sum_of_cyclics((4,)),
        lambda h, v: v if h == subgroup.one() else -v,
    )
    induced = Modules(ZZ[subgroup]).induction_restriction_adjunction(supergroup).left_adjoint()(sign)
    coinduced = Modules(ZZ[supergroup]).restriction_coinduction_adjunction(subgroup).right_adjoint()(sign)

    assert tuple(induced.invariant_factors()) == (4, 4, 4)
    assert tuple(coinduced.invariant_factors()) == (4, 4, 4)
    assert induced.cardinality() == 64
    assert induced.is_isomorphic(coinduced)
