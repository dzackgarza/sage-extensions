r"""A framed free module exposes its selected module-resolution data coherently."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_free_module_selected_resolution_controls_generators_and_framing() -> None:
    module = ZZ.free_module(2)
    resolution = module.selected_module_resolution()
    generator_map = module.module_generator_morphism()
    framing = module.framing_object()

    assert module.has_selected_module_resolution()
    assert resolution.target() is module
    assert module.number_of_module_generators() == cardinal(2)
    assert generator_map.codomain() is module
    assert framing.arrow() is module.framing_morphism()
