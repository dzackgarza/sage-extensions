r"""Projective space exposes coordinate restrictions, jets, coordinate swap, and point blowup."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_coordinate_restriction_and_jets() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    restriction = plane.coordinate_hyperplane_section_restriction(2, 0)
    jets = plane.coordinate_point_jet_evaluation(3, 0, 2)
    singular = plane.sections_vanishing_to_order(3, 0, 2)

    assert restriction.domain().dimension() == 6
    assert restriction.codomain().dimension() == 3
    assert restriction.kernel().dimension() == 3
    assert jets.domain().dimension() == 10
    assert jets.codomain().dimension() == 3
    assert singular.dimension() == 7


def test_projective_line_coordinate_swap_is_an_involution() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    action = ProjectiveLines(QQ)(line).coordinate_swap_action()
    group = action.acting_group()
    generator = group.group_generators()[0]
    swap = action.action_of(generator)

    assert group.order() == 2
    assert swap * swap == line.categorical_identity_morphism()


def test_projective_plane_point_blowup_remembers_source_and_center() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 1, 1))
    blowup = plane.point_blowup(point)

    assert blowup.blowup_source() is plane
    assert blowup.blowup_point() is point
