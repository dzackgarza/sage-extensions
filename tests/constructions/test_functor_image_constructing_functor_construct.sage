r"""A chosen object in a functor image retains the functor that constructed it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_functor_image_object_retains_constructing_functor() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[1]
    presented = identity.Image()(points)

    assert presented.constructing_functor() is identity
    assert presented.underlying_image() is points
