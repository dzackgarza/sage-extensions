r"""Identity functor object and morphism action accessors agree with the identity action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_functor_object_action_accessors_fix_objects() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[2]

    assert identity.object_image(points) is points
    assert identity.on_object(points) is points


def test_identity_functor_morphism_action_accessors_fix_arrows() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[2]
    arrow = Sets().Mor(points, points).identity()

    assert identity.morphism_image(arrow) == arrow
    assert identity.on_morphism(arrow) == arrow
