r"""A natural transformation retains its source, target, and functor-category arrow."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_natural_transformation():
    identity = Sets().identity_functor()
    return identity, NaturalTransformation(
        identity,
        identity,
        lambda obj: Sets().Mor(obj, obj).identity(),
    )


def test_identity_natural_transformation_retains_source_and_target() -> None:
    identity, transformation = _identity_natural_transformation()

    assert transformation.source() is identity
    assert transformation.target() is identity


def test_identity_natural_transformation_morphism_has_identity_functor_endpoints() -> None:
    identity, transformation = _identity_natural_transformation()
    arrow = transformation.morphism()

    assert arrow.domain() is identity.object()
    assert arrow.codomain() is identity.object()
