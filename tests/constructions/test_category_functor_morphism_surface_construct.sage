r"""A functor regarded as an arrow in ``Cat`` acts and composes as that functor."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_functor_arrow():
    identity = Sets().identity_functor()
    return identity, identity.arrow()


def test_category_functor_arrow_acts_on_objects_and_morphisms() -> None:
    _identity, arrow = _identity_functor_arrow()
    points = Sets.Δ[2]
    identity_map = Sets().Mor(points, points).identity()

    assert arrow(points) is points
    assert arrow(identity_map) == identity_map


def test_category_functor_arrow_composition_is_functor_composition() -> None:
    identity, arrow = _identity_functor_arrow()
    composite = arrow * arrow
    points = Sets.Δ[2]
    identity_map = Sets().Mor(points, points).identity()

    assert composite.domain() is Sets()
    assert composite.codomain() is Sets()
    assert composite(points) is points
    assert composite(identity_map) == identity_map
    assert composite.functor().domain() is identity.domain()
    assert composite.functor().codomain() is identity.codomain()
