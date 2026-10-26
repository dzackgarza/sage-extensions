r"""A morphism of chosen resolutions retains its base map and degree maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _constant_set_resolution_identity():
    resolutions = Resolutions(Sets(), Sets(), 0)
    points = Sets.Δ[2]
    resolution = resolutions.constant(points)
    identity = resolutions.Mor(resolution, resolution).identity()
    return resolutions, points, resolution, identity


def test_resolution_identity_retains_target_and_degree_zero_maps() -> None:
    _resolutions, points, _resolution, identity = (
        _constant_set_resolution_identity()
    )
    base_identity = Sets().Mor(points, points).identity()

    assert identity.target_morphism() == base_identity
    assert identity.base_morphism() == base_identity
    assert identity.component(0) == base_identity


def test_resolution_target_functor_sends_identity_to_the_base_identity() -> None:
    resolutions, points, resolution, identity = (
        _constant_set_resolution_identity()
    )
    target = resolutions.target_functor()

    assert target(resolution) is points
    assert target(identity) == Sets().Mor(points, points).identity()


def test_resolution_morphism_composition_is_degreewise_and_on_targets() -> None:
    _resolutions, points, _resolution, identity = (
        _constant_set_resolution_identity()
    )
    composite = identity * identity
    base_identity = Sets().Mor(points, points).identity()

    assert composite.target_morphism() == base_identity
    assert composite.component(0) == base_identity
