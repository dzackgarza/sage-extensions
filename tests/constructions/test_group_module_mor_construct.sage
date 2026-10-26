r"""Equivariant module Mor objects contain identities, zero maps, and equivariant maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _swap_module():
    group = Groups.C(2)
    module = Modules(ZZ).free_module(("e", "f"))
    e, f = module.module_generator("e"), module.module_generator("f")
    swap = module.Mor(module)({e: f, f: e})
    action = group.Mor(module.Aut())({group.group_generators()[0]: swap})
    return Modules(ZZ[group])(module, action)


def test_identity_and_zero_are_equivariant_endomorphisms() -> None:
    module = _swap_module()
    morphisms = module.Mor(module)
    e, f = module.module_generator("e"), module.module_generator("f")
    identity = morphisms.identity()
    zero = morphisms.zero()

    assert identity.parent() is morphisms
    assert identity(e) == e
    assert identity(f) == f
    assert zero(e) == module.zero()
    assert zero(f) == module.zero()


def test_sum_projection_is_equivariant_to_the_trivial_line() -> None:
    module = _swap_module()
    group = module.acting_group()
    target = Modules(ZZ).trivial_action(group)(Modules(ZZ).free_module(("n",)))
    e, f = module.module_generator("e"), module.module_generator("f")
    n = target.module_generator("n")
    quotient = module.Mor(target)({e: n, f: n})

    assert quotient.parent() is module.Mor(target)
    assert quotient(e + f) == 2 * n
