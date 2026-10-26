r"""A finite free module carries its selected Dold--Kan chain resolution."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_free_module_selected_chain_resolution_surface() -> None:
    module = ZZ.free_module(2)
    resolution = module.selected_module_resolution()
    category = resolution.resolution_category()

    assert category in Cat()
    assert resolution in category
    assert category.base_category() is Modules(ZZ)
    assert category.ring() is ZZ
    assert resolution.target() is resolution.resolved_object() is module
    assert resolution.level(0) is resolution.term(0) is module
    assert resolution.truncation() == 1
    assert resolution.length() == resolution.resolution_length() == 0
    assert resolution.model() == "chain"
    assert resolution.generator_count() == cardinal(2)
    assert resolution.differential(1).is_zero()
    assert resolution.is_acyclic_through_truncation()
