r"""Directed systems as functors from directed posets.

The chain ``0 <= 1`` is directed.  A constant one-point set diagram on that
chain is therefore the smallest directed system, and its natural identity is
the identity morphism in the directed-system category.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_term_directed_system():
    labels = Sets.Δ[1]
    index = PosetCategory(labels, le=lambda left, right: int(left) <= int(right))
    systems = DirectedSystem(index, Sets())
    diagram = Cat().Mor(index, Sets()).constant_functor(Sets.Δ[0])
    return index, systems, systems.object(diagram)


def test_constant_diagram_on_a_two_term_chain_is_a_directed_system() -> None:
    index, systems, system = _two_term_directed_system()

    assert systems in Cat()
    assert system in systems
    assert system.domain() is index
    assert system.codomain() is Sets()
    assert system(index(0)) is Sets.Δ[0]
    assert system(index(1)) is Sets.Δ[0]


def test_directed_system_morphisms_have_identity() -> None:
    _index, systems, system = _two_term_directed_system()
    identity = systems.Mor(system, system).identity()

    assert identity.domain() is system
    assert identity.codomain() is system
    assert identity * identity == identity
