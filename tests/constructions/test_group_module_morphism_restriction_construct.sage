r"""An equivariant endomorphism restricts along an equivariant inclusion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_group_module_identity_restricts_along_identity_inclusion() -> None:
    group = Groups.C(2)
    module = ZZ.free_module(1)
    acted = Modules(ZZ).trivial_action(group)(module)
    identity = acted.Mor(acted).identity()
    inclusion = acted.Mor(acted).identity()
    restricted = identity.restrict_to(inclusion)
    generator = acted.module_generator(0)

    assert restricted.domain() is acted
    assert restricted.codomain() is acted
    assert restricted(generator) == generator
    assert restricted.underlying_module_morphism()(module.module_generator(0)) == (
        module.module_generator(0)
    )
