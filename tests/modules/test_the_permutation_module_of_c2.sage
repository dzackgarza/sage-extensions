r"""The permutation module $\mathbb Z[C_2]$: invariants, coinvariants and character.

$C_2 = \langle g \rangle$ acts on $\mathbb Z^2 = \mathbb Z a \oplus \mathbb Z b$ by swapping $a$ and
$b$; this is the regular module $\mathbb Z[C_2]$.  Its invariants are $\mathbb Z(a + b)$, of rank one;
its coinvariants are $\mathbb Z^2 / (a - b) \cong \mathbb Z$, free of rank one; its character is
$\chi(1) = 2$, $\chi(g) = \operatorname{tr}\begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} = 0$.
Values by hand from the definitions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def permutation_module():
    group = Groups.C(2)
    plane = ZZ ^ 2
    a, b = plane.module_generator(0), plane.module_generator(1)
    swap = plane.Mor(plane)({0: b, 1: a})
    action = group.Mor(plane.Aut())({group.group_generators()[0]: swap})
    return Modules(ZZ[group])(plane, action)


def test_the_swap_moves_a_to_b_and_fixes_a_plus_b() -> None:
    r"""$g a = b$, and $a + b$ is invariant while $a$ is not."""
    module = permutation_module()
    g = module.acting_group().group_generators()[0]
    a, b = module.module_generator(0), module.module_generator(1)

    assert module.act(g, a) == b
    assert module.is_invariant(a + b)
    assert not module.is_invariant(a)
    assert not module.is_trivial_action()


def test_the_invariants_of_the_permutation_module_have_rank_one() -> None:
    r"""$\mathbb Z[C_2]^{C_2} = \mathbb Z(a + b)$."""
    assert permutation_module().module_invariants().module_rank() == 1


def test_the_coinvariants_of_the_permutation_module_are_free_of_rank_one() -> None:
    r"""$\mathbb Z[C_2]_{C_2} = \mathbb Z^2/(a - b) \cong \mathbb Z$."""
    coinvariants = permutation_module().module_coinvariants()

    assert coinvariants.module_rank() == 1
    assert coinvariants.is_free()


def test_the_character_of_the_permutation_module() -> None:
    r"""$\chi(1) = 2$ and $\chi(g) = 0$."""
    module = permutation_module()
    group = module.acting_group()

    representation = OrdinaryCharacterRepresentations(module.group_algebra())(module)
    assert representation.character()(group.one()) == 2
    assert representation.character()(group.group_generators()[0]) == 0
