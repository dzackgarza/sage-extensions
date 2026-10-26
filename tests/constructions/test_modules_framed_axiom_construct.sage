r"""The framed-module refinement records a selected generating map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_integer_plane_lies_in_the_framed_refinement() -> None:
    module = ZZ.free_module(2)
    category = Modules(ZZ).Framed()

    assert module in category
    assert module.module_generating_set().cardinality() == cardinal(2)
    assert module.module_generator(0) in module
