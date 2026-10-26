r"""The swap involution of (U) is reconstructed from its invariant and coinvariant gluing data."""

from sage_extensions.all import *  # noqa: F401,F403


def _hyperbolic_swap_extension():
    lattice = NamedLattices.U
    labels = tuple(lattice.module_generating_set())
    first, second = lattice.module_generators()
    swap = lattice.Aut()({labels[0]: second, labels[1]: first})
    return lattice, swap, swap.primitive_extension()


def test_hyperbolic_swap_extension_retains_inclusions_glue_and_negation() -> None:
    lattice, _swap, extension = _hyperbolic_swap_extension()
    invariant = extension.invariant_inclusion()
    coinvariant = extension.orthogonal_complement_inclusion()
    sum_inclusion = extension.orthogonal_sum_inclusion()

    assert extension.acts_as_negation_on_coinvariants()
    assert invariant.codomain() is lattice
    assert coinvariant.codomain() is lattice
    assert sum_inclusion.codomain() is lattice
    assert sum_inclusion.index() == 2
    assert extension.invariant_gluing_subgroup().cardinality() == cardinal(2)
    assert extension.glue().domain() is extension.invariant_gluing_subgroup()
    assert extension.glue_graph().cardinality() == cardinal(2)


def test_hyperbolic_swap_restrictions_preserve_glue_and_reassemble_centralizer() -> None:
    lattice, swap, extension = _hyperbolic_swap_extension()
    invariant_part = extension.invariant_restriction(swap)
    coinvariant_part = extension.coinvariant_restriction(swap)

    assert extension.pair_preserves_glue_graph(invariant_part, coinvariant_part)
    assert extension.centralizer_element(invariant_part, coinvariant_part) == swap
    invariant_lattice = extension.invariant.inclusion().domain()
    coinvariant_lattice = extension.orthogonal_complement.inclusion().domain()
    assert extension.centralizer_element(
        invariant_lattice.O().one(),
        coinvariant_lattice.O().one(),
    ) == lattice.O().one()
