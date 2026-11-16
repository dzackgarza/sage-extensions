r"""Modules over group rings: invariants, coinvariants, splitting fields and base change."""

from sage_extensions.all import *  # noqa: F401,F403


def _trivial_and_sign_lines(ring):
    group = Groups.C(2)
    line = Modules(ring)(Sets()(("e",)))
    trivial = Modules(ring[group])(line, lambda g, v: v)
    sign = Modules(ring[group])(line, lambda g, v: v if g == group.one() else -v)
    return group, trivial, sign


def test_the_integral_sign_representation_has_no_invariants_and_coinvariants_z_mod_2() -> None:
    r"""For $\mathbb{Z}_-$ with $g \cdot v = -v$: $H^0 = \{v : v = -v\} = 0$ and $H_0 = \mathbb{Z}/(g - 1)\mathbb{Z} = \mathbb{Z}/2$.

    Over $\mathbb{Q}$ both vanish, since $2$ is invertible.  Source: Brown,
    *Cohomology of Groups*, II.2.
    """
    _, _, integral_sign = _trivial_and_sign_lines(ZZ)
    _, _, rational_sign = _trivial_and_sign_lines(QQ)

    assert integral_sign.module_invariants().module_rank() == 0
    assert integral_sign.module_coinvariants().cardinality() == 2
    assert rational_sign.module_invariants().module_rank() == 0
    assert rational_sign.module_coinvariants().module_rank() == 0


def test_the_invariants_of_the_regular_representation_of_s3_are_one_dimensional() -> None:
    r"""$\mathbb{Q}[S_3]^{S_3}$ is spanned by $\sum_{g} g$, so it has dimension $1$, while the regular representation has dimension $6$."""
    group = Groups.S(3)
    regular = QQ[group].regular_representation()

    assert regular.module_rank() == 6
    assert regular.module_invariants().module_rank() == 1


def test_q_splits_c2_but_the_splitting_field_of_c3_is_quadratic() -> None:
    r"""$\mathbb{Q}[C_2] \cong \mathbb{Q} \times \mathbb{Q}$ is split; $\mathbb{Q}[C_3] \cong \mathbb{Q} \times \mathbb{Q}(\zeta_3)$ needs $\mathbb{Q}(\zeta_3)$, of degree $2$.

    Source: Serre, *Linear Representations of Finite Groups*, §12.3.
    """
    group, _, sign = _trivial_and_sign_lines(QQ)

    assert sign.action_of(group.group_generators()[0])[0, 0] == QQ(-1)
    assert Modules(QQ[group]).splitting_field() is QQ
    assert Modules(QQ[group]).is_split()
    assert Modules(QQ[Groups.C(3)]).splitting_field().degree() == 2
    assert not Modules(QQ[Groups.C(3)]).is_split()


def test_sign_and_trivial_actions_coincide_after_base_change_to_characteristic_two() -> None:
    r"""$\mathbb{Z}_-$ and $\mathbb{Z}$ are non-isomorphic $\mathbb{Z}[C_2]$-modules, but $-1 = 1$ in $\mathbb{F}_2$, so $\mathbb{F}_2 \otimes \mathbb{Z}_- = \mathbb{F}_2 \otimes \mathbb{Z}$ is trivial."""
    group, trivial, sign = _trivial_and_sign_lines(ZZ)
    generator = group.group_generators()[0]
    field = GF(2)
    extension = Modules(ZZ[group]).coefficient_base_change_adjunction(
        ZZ.Mor(field)(lambda integer: field(integer))
    ).left_adjoint()
    changed_trivial = extension(trivial)
    changed_sign = extension(sign)

    assert trivial.action_of(generator) != sign.action_of(generator)
    assert not trivial.is_isomorphic(sign)
    assert changed_trivial.action_of(generator) == changed_sign.action_of(generator)
    assert changed_sign.is_trivial_action()
    assert changed_trivial.is_isomorphic(changed_sign)


def _permutation_module_of_s3():
    r"""The permutation representation $\mathbb{Q}^3$ of $S_3$ on the three basis vectors."""
    group = Groups.S(3)
    vectors = Modules(QQ).free_module(3)

    def act(g, vector):
        return vectors.Mor(vectors)(
            {label: vectors.module_generator(int(g(label + 1)) - 1) for label in range(3)}
        )(vector)

    return group, Modules(QQ[group])(vectors, act)


def test_a_coefficient_scalar_acts_on_a_group_module_element() -> None:
    r"""$\tfrac13\sum_i e_i$ is the invariant line of the permutation representation.

    A module over $R[G]$ is a module over $R$ through the morphism
    $R\to R[G]$, $r\mapsto r\cdot 1$, so a coefficient scalar multiplies a
    module element: the average of the basis is fixed by every group element,
    and three copies of it give the sum of the basis back.
    """
    group, representation = _permutation_module_of_s3()
    total = sum(
        representation.module_generator(label)
        for label in representation.module_generating_set()
    )
    averaged = (QQ(1) / QQ(3)) * total
    transposition = next(g for g in group if g.order() == 2)
    three_cycle = next(g for g in group if g.order() == 3)

    assert representation.act(transposition, averaged) == averaged
    assert representation.act(three_cycle, averaged) == averaged
    assert averaged + averaged + averaged == total


def test_the_character_of_a_finite_free_representation_is_the_trace_of_its_action() -> None:
    r"""The character of $\mathbb{Q}^3$ is the permutation character $3,1,0$.

    Over a characteristic-zero field the character of a finite free
    representation is the trace of each group element (Serre, *Linear
    Representations of Finite Groups*, §2.1 and §6.1): the identity gives the
    rank, a transposition fixes one basis vector, and a three-cycle fixes none.
    """
    group, representation = _permutation_module_of_s3()
    transposition = next(g for g in group if g.order() == 2)
    three_cycle = next(g for g in group if g.order() == 3)
    character = representation.character()

    assert character(group.one()) == 3
    assert character(transposition) == 1
    assert character(three_cycle) == 0
