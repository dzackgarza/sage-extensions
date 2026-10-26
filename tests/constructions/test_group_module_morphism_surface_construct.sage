r"""An equivariant identity retains its linear and natural-transformation views."""

from sage_extensions.all import *  # noqa: F401,F403


def _trivial_group_module_identity():
    group = Groups.C(2)
    module = ZZ.free_module(1)
    acted = Modules(ZZ).trivial_action(group)(module)
    return group, module, acted, acted.Mor(acted).identity()


def test_group_module_identity_retains_its_underlying_module_map() -> None:
    _group, module, _acted, identity = _trivial_group_module_identity()
    generator = module.module_generator(0)

    assert identity.underlying_arrow()(generator) == generator
    assert identity.underlying_module_morphism()(generator) == generator


def test_group_module_identity_is_its_own_inverse_and_automorphism() -> None:
    _group, module, _acted, identity = _trivial_group_module_identity()
    generator = module.module_generator(0)

    assert identity.inverse()(generator) == generator
    assert identity.as_automorphism()(generator) == generator


def test_group_module_identity_gives_the_identity_natural_transformation() -> None:
    group, module, acted, identity = _trivial_group_module_identity()
    transformation = identity.natural_transformation()
    object_of_bg = next(iter(group.classifying_category().object_set()))
    generator = module.module_generator(0)

    assert transformation.source() == acted.action_functor()
    assert transformation.target() == acted.action_functor()
    assert transformation.component(object_of_bg)(generator) == generator
