r"""Chosen resolutions retain their truncation, levels, simplicial maps, and selected generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_constant_truncation_one_resolution_retains_level_and_simplicial_data() -> None:
    resolutions = Resolutions(Sets(), Sets(), 1)
    points = Sets.Δ[1]
    resolution = resolutions.constant(points)
    identity = Sets().Mor(points, points).identity()

    assert resolution in resolutions
    assert resolution.resolution_category() is resolutions
    assert resolution.base_category() is Sets()
    assert resolution.projective_class() is Sets()
    assert resolution.level_category() is Sets()
    assert resolution.truncation() == 1
    assert resolution.target() is resolution.resolved_object() is points
    assert resolution.level(0) is resolution.term(0) is points
    assert resolution.level(1) is resolution.term(1) is points
    assert resolution.augmentation() == identity
    assert resolution.face(1, 0) == identity
    assert resolution.face(1, 1) == identity
    assert resolution.degeneracy(0, 0) == identity
    assert resolution.length() == resolution.resolution_length() == 0
    assert resolution.model() == "constant"
    assert resolution.is_acyclic_through_truncation()


def test_selected_degree_zero_resolution_retains_generator_data() -> None:
    resolutions = Resolutions(Sets(), Sets(), 0)
    points = Sets.Δ[1]
    identity = Sets().Mor(points, points).identity()
    resolution = resolutions.selected_degree_zero(
        points,
        points,
        identity,
        generating_set=points,
        generator_morphism=identity,
    )

    assert resolution.generating_set() is points
    assert resolution.generator_morphism() == identity
    assert resolution.generator_count() == cardinal(2)
    assert resolution.generator(points(1)) == points(1)
    assert resolution.generators(name="selected generators")[points(0)] == points(0)
