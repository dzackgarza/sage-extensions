r"""A selected finite algebra presentation retains its relation source in the resolution."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_axes_resolution_has_one_relation_source_generator() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    resolution = axes.selected_algebra_resolution()

    assert resolution.relation_source().algebra_generating_set().cardinality() == cardinal(1)
    assert resolution.relations().cardinality() == cardinal(1)
