r"""Coextension along the identity ring map realizes Hom_R(R,-)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_coextension_of_scalars_preserves_free_module_rank() -> None:
    modules = Modules(ZZ)
    identity = ZZ.Mor(ZZ).identity()
    coextension = modules.coextension_of_scalars(identity)
    plane = ZZ.free_module(2)
    coextended = coextension(plane)

    assert coextension.domain() is modules
    assert coextension.codomain() is modules
    assert coextended.module_rank() == cardinal(2)
