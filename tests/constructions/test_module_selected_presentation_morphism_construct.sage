r"""A morphism of finitely presented modules lifts to their selected presentations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_lifts_to_an_endomorphism_of_the_selected_presentation() -> None:
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.free_module(1)
    module = line.End()({0: x**2 * line.module_generator(0)}).cokernel()
    identity = module.Mor(module).identity()
    lifted = identity.selected_presentation_morphism()

    assert lifted.domain() is module.presentation_object()
    assert lifted.codomain() is module.presentation_object()
