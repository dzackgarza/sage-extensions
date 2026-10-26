r"""The free-module refinement records existence of a basis."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_integer_plane_lies_in_the_free_refinement() -> None:
    module = ZZ.free_module(2)
    category = Modules(ZZ).Free()

    assert module in category
    assert module.is_free()
    assert module.module_rank() == 2
