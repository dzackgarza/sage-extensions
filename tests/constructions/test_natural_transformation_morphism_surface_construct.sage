r"""A functor-category morphism exposes the natural transformation it represents."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_transformation_arrow():
    identity = Sets().identity_functor()
    transformation = NaturalTransformation(
        identity,
        identity,
        lambda obj: Sets().Mor(obj, obj).identity(),
    )
    return identity, transformation, transformation.morphism()


def test_natural_transformation_morphism_retains_transformation_and_components() -> None:
    _identity, transformation, arrow = _identity_transformation_arrow()
    points = Sets.Δ[2]

    assert arrow.transformation() is transformation
    assert arrow.component(points) == Sets().Mor(points, points).identity()


def test_natural_transformation_morphism_exposes_the_naturality_square() -> None:
    _identity, _transformation, arrow = _identity_transformation_arrow()
    points = Sets.Δ[2]
    morphism = Sets().Mor(points, points).identity()
    target_path = arrow.naturality_target_composite(morphism)
    source_path = arrow.naturality_source_composite(morphism)
    square = arrow.naturality_square(morphism)

    assert target_path == source_path
    assert square.parent().projection(0)(square) == target_path
    assert square.parent().projection(1)(square) == source_path
