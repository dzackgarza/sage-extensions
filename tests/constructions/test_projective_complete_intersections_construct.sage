r"""A hyperplane in P^1 over F_5 is a projective complete intersection."""

from sage_extensions.all import *  # noqa: F401,F403


def test_linear_complete_intersection_over_five_constructs() -> None:
    complete_intersections = ProjectiveCompleteIntersections(GF(5))
    point = complete_intersections.an_object()

    assert point in complete_intersections
    assert point.is_complete_intersection()
    assert point.complete_intersection_codimension() == cardinal(1)
    assert point.expected_dimension() == 0
