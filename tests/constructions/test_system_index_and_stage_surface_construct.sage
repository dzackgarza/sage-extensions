r"""Directed and inverse systems expose their base index and diagram stages."""

from sage_extensions.all import *  # noqa: F401,F403


def test_directed_system_base_index_and_stage_are_the_defining_diagram_data() -> None:
    index = PosetCategory(
        Sets.Δ[1],
        le=lambda left, right: int(left) <= int(right),
    )
    systems = DirectedSystem(index, Sets())
    diagram = Cat().Mor(index, Sets()).constant_functor(Sets.Δ[0])
    system = systems.object(diagram)

    assert systems.base_index_category() is index
    assert system.base_index_category() is index
    assert system.stage(index(0)) is Sets.Δ[0]


def test_inverse_system_remembers_the_unopposed_base_index() -> None:
    index = PosetCategory(
        Sets.Δ[1],
        le=lambda left, right: int(left) <= int(right),
    )
    systems = InverseSystem(index, Sets())
    opposite = systems.index_category()
    diagram = Cat().Mor(opposite, Sets()).constant_functor(Sets.Δ[0])
    system = systems.object(diagram)

    assert systems.base_index_category() is index
    assert system.base_index_category() is index
    assert system.stage(opposite(index(0))) is Sets.Δ[0]
