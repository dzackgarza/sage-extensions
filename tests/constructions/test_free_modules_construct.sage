r"""Free modules are precisely modules carrying a basis.

The standard rank-two integer module is free and its identity preserves the
chosen basis.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_integer_plane_is_free() -> None:
    module = ZZ.free_module(2)

    assert module in FreeModules(ZZ)
    assert module.is_free()


def test_free_module_morphisms_have_identity() -> None:
    module = ZZ.free_module(2)
    identity = module.Mor(module).identity()

    assert identity(module.module_generator(0)) == module.module_generator(0)
    assert identity * identity == identity
