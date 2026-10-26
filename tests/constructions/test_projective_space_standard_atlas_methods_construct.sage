r"""Projective space exposes its chosen homogeneous coordinates and standard affine gluing."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_line_standard_atlas_and_transition() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    coordinates = line.homogeneous_coordinate_generators()
    charts = line.standard_affine_charts()
    first_embedding = line.standard_affine_chart_embedding(0)
    overlap = line.standard_chart_overlap(0, 1)
    transition = line.standard_chart_transition(0, 1)

    assert line.variable_names() == ("x", "y")
    assert coordinates.cardinality() == cardinal(2)
    assert charts.cardinality() == cardinal(2)
    assert first_embedding.domain() is charts[0]
    assert first_embedding.codomain() is line
    assert overlap.inclusion().codomain() is charts[0]
    assert transition.forward().domain() is overlap
    assert transition.backward().codomain() is overlap


def test_projective_plane_glues_from_three_standard_charts() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    glued = plane.glued_from_standard_charts()

    assert plane.standard_affine_charts().cardinality() == cardinal(3)
    assert glued.gluing_datum().transition_index_set().cardinality() == cardinal(3)
    assert glued.is_isomorphic(plane)
