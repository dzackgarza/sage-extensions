r"""The identity of a presented module lifts to a chain endomorphism of its selected free resolution."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_morphism_lifts_to_selected_free_resolution() -> None:
    generators = ZZ.free_module(2)
    relations = ZZ.free_module(1)
    presentation = relations.Mor(generators)(
        {0: 6 * generators.module_generator(0)}
    )
    module = presentation.cokernel()
    resolution = module.free_resolution()
    identity = module.Mor(module).identity()
    lift = resolution.lift_morphism(identity, resolution)

    assert lift.domain() is resolution
    assert lift.codomain() is resolution
    assert lift.module_morphism() == identity
    assert lift.component(0).domain() is resolution.term(0)
    assert lift.component(0).codomain() is resolution.term(0)
