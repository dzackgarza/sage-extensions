r"""The action restricted to invariant and isotypic pieces of a group module.

The permutation module of the symmetric group on three letters splits over
the rationals into the trivial line and the two-dimensional standard
representation (Serre, *Linear Representations of Finite Groups*, 2.3, 5.8).
Both pieces are stable, so each carries the restricted action, and the
restricted characters identify which piece is which: the trivial character is
one everywhere, while the standard character takes the values two, zero and
minus one on the identity, a transposition and a three-cycle.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _permutation_module():
    group = Groups.S(3)
    module = Modules(QQ).free_module(3)

    def act(g, vector):
        return module.Mor(module)(
            {label: module.module_generator(int(g(label + 1)) - 1) for label in range(3)}
        )(vector)

    return group, Modules(QQ[group])(module, act)


def _transposition_and_three_cycle(group):
    transposition = next(g for g in group if g.order() == 2)
    three_cycle = next(g for g in group if g.order() == 3)
    return transposition, three_cycle


def test_the_standard_isotypic_component_is_the_standard_representation() -> None:
    group, representation = _permutation_module()
    transposition, three_cycle = _transposition_and_three_cycle(group)
    standard = representation.isotypic_decomposition().nontrivial_components()[0]

    restricted = representation.restrict_action_to(standard.inclusion()).domain()
    character = restricted.character()

    assert restricted.module_rank() == 2
    assert character(group.one()) == 2
    assert character(transposition) == 0
    assert character(three_cycle) == -1
    assert restricted.module_invariants().module_rank() == 0


def test_the_invariants_of_the_permutation_module_are_the_trivial_representation() -> None:
    group, representation = _permutation_module()
    transposition, three_cycle = _transposition_and_three_cycle(group)
    invariants = representation.module_invariants()

    restricted = representation.restrict_action_to(invariants.inclusion()).domain()
    character = restricted.character()

    assert restricted.module_rank() == 1
    assert character(group.one()) == 1
    assert character(transposition) == 1
    assert character(three_cycle) == 1


def test_reflection_in_the_trivial_line_is_plus_one_on_standard_and_minus_one_on_invariants() -> None:
    r"""$r = 1 - 2P_{\mathrm{triv}}$, $P_{\mathrm{triv}}(v) = \tfrac13(\textstyle\sum v_i)(1,1,1)$.

    $r$ commutes with $S_3$; it fixes the sum-zero plane and negates $(1,1,1)$.
    """
    _, representation = _permutation_module()
    labels = representation.module_generating_set()
    total = sum(representation.module_generator(label) for label in labels)
    reflection = representation.Mor(representation)(
        {label: representation.module_generator(label) - QQ(2) / QQ(3) * total for label in labels}
    )
    automorphism = reflection.as_automorphism()

    standard = representation.isotypic_decomposition().nontrivial_components()[0]
    on_standard = representation.restrict_automorphism_to(automorphism, standard.inclusion())
    standard_module = on_standard.domain()
    assert all(
        on_standard(standard_module.module_generator(label))
        == standard_module.module_generator(label)
        for label in standard_module.module_generating_set()
    )

    invariants = representation.module_invariants()
    on_invariants = representation.restrict_automorphism_to(automorphism, invariants.inclusion())
    invariant_module = on_invariants.domain()
    assert all(
        on_invariants(invariant_module.module_generator(label))
        == -invariant_module.module_generator(label)
        for label in invariant_module.module_generating_set()
    )
