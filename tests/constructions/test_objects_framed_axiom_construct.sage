r"""A framed module is, in particular, a framed represented object."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_integer_plane_is_a_framed_object() -> None:
    module = ZZ.free_module(2)

    assert module in Objects().Framed()
    assert module in Modules(ZZ).Framed()
