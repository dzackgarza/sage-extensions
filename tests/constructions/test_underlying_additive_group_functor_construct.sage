r"""Forgetting module scalars retains exactly the underlying abelian group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_module_forgetful_functor_returns_its_underlying_additive_group() -> None:
    modules = Modules(ZZ)
    module = ZZ.free_module(2)
    forget = modules.underlying_additive_group_functor()

    assert forget.domain() is modules
    assert forget.codomain() is AdditiveGroups().AdditiveCommutative()
    assert forget(module) is module.underlying_additive_group()
