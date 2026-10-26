r"""Inverse systems as functors from the opposite of an indexing category.

For the chain ``0 <= 1``, the constant one-point diagram on its opposite is the
smallest inverse system.  Its variance is visible in the represented functor's
domain and its natural identity remains inside the inverse-system category.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_term_inverse_system():
    labels = Sets.Δ[1]
    index = PosetCategory(labels, le=lambda left, right: int(left) <= int(right))
    opposite = index.opposite()
    systems = InverseSystem(index, Sets())
    diagram = Cat().Mor(opposite, Sets()).constant_functor(Sets.Δ[0])
    return index, opposite, systems, systems.object(diagram)


def test_constant_diagram_on_the_opposite_chain_is_an_inverse_system() -> None:
    index, opposite, systems, system = _two_term_inverse_system()

    assert systems in Cat()
    assert system in systems
    assert system.domain() is opposite
    assert system.codomain() is Sets()
    for obj in opposite.objects():
        assert system(obj) is Sets.Δ[0]


def test_inverse_system_morphisms_have_identity() -> None:
    _index, _opposite, systems, system = _two_term_inverse_system()
    identity = systems.Mor(system, system).identity()

    assert identity.domain() is system
    assert identity.codomain() is system
    assert identity * identity == identity
