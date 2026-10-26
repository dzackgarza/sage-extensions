r"""Restriction of a diagram retains the original diagram and indexing functor."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_restriction_retains_both_defining_functors() -> None:
    identity = Sets().identity_functor()
    restricted = identity.restrict(identity)
    points = Sets.Δ[1]

    assert restricted.original_diagram() is identity
    assert restricted.indexing_functor() is identity
    assert restricted(points) is points
