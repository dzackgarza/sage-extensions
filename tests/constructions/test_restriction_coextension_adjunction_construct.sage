r"""Restriction of scalars is left adjoint to coextension of scalars."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_restriction_coextension_adjunction_has_identity_endpoints() -> None:
    modules = Modules(ZZ)
    identity = ZZ.Mor(ZZ).identity()
    adjunction = modules.restriction_coextension_adjunction(identity)
    line = ZZ.free_module(1)

    assert adjunction.left_adjoint().domain() is modules
    assert adjunction.left_adjoint().codomain() is modules
    assert adjunction.right_adjoint().domain() is modules
    assert adjunction.right_adjoint().codomain() is modules
    assert adjunction.unit(line).domain() is line
    assert adjunction.counit(line).codomain() is line
