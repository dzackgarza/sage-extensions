r"""Identity functors are neutral for functor composition and restriction."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_functor_then_identity_is_identity_on_objects_and_arrows() -> None:
    identity = Sets().identity_functor()
    composite = identity.then(identity)
    points = Sets.Δ[2]
    arrow = Sets().Mor(points, points).identity()

    assert composite(points) is points
    assert composite(arrow) == arrow


def test_identity_functor_restricted_along_identity_is_identity() -> None:
    identity = Sets().identity_functor()
    restricted = identity.restrict(identity)
    points = Sets.Δ[2]
    arrow = Sets().Mor(points, points).identity()

    assert restricted(points) is points
    assert restricted(arrow) == arrow
