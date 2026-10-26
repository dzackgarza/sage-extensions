r"""A submodule's selected generators map into its ambient module by the subframing."""

from sage_extensions.all import *  # noqa: F401,F403


def test_index_two_submodule_subframing_is_its_selected_inclusion_on_generators() -> None:
    module = ZZ.free_module(2)
    e0, e1 = module.module_generators()
    submodule = module.subobject_on((2 * e0, e1))
    subframing = submodule.sub_framing_morphism(module)

    assert subframing.domain() is submodule
    assert subframing.codomain() is module
    assert subframing(submodule.module_generator(0)) == submodule.inclusion()(
        submodule.module_generator(0)
    )
    assert subframing(submodule.module_generator(1)) == submodule.inclusion()(
        submodule.module_generator(1)
    )
