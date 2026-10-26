r"""A finitely framed module can inject its named generators into an explicit namespace."""

from sage_extensions.all import *  # noqa: F401,F403


def test_named_free_module_injects_generators_into_supplied_scope() -> None:
    module = ZZ.free_module(("e", "f"))
    scope = {}

    module.inject_variables(scope=scope, verbose=False)

    assert scope["e"] == module.module_generator("e")
    assert scope["f"] == module.module_generator("f")
