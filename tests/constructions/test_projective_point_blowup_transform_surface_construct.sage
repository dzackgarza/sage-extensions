r"""The blowup of (mathbf P^2) at a rational point exposes its center and curve transforms."""

from sage_extensions.all import *  # noqa: F401,F403


def _point_blowup_and_cusp():
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    point = plane.point_morphism((1, 1, 1))
    blowup = ProjectivePointBlowups(QQ)(point)
    x, y, z = plane.homogeneous_coordinate_generators()
    cusp = plane.closed_subscheme((y - z) ** 2 * z - (x - z) ** 3)
    return plane, point, blowup, cusp


def test_projective_point_blowup_retains_center_in_graph_coordinates() -> None:
    plane, point, blowup, _cusp = _point_blowup_and_cusp()
    center = blowup.blowup_center()
    embedding = blowup.source_coordinate_embedding()
    equations = blowup.center_equations_in_graph_ring()

    assert center.inclusion().codomain() is plane
    assert point.codomain() is plane
    assert embedding.domain() is plane.homogeneous_coordinate_ring()
    assert len(equations) == 2
    assert all(equation.parent() is blowup.graph_relation().parent() for equation in equations)


def test_cuspidal_cubic_total_and_strict_transforms_have_expected_classes() -> None:
    _plane, _point, blowup, cusp = _point_blowup_and_cusp()
    hyperplane = blowup.hyperplane_picard_class()
    exceptional = blowup.exceptional_picard_class()
    inverse_image = blowup.scheme_theoretic_inverse_image(cusp)
    total = blowup.total_transform(cusp)
    strict = blowup.strict_transform(cusp)

    assert blowup.curve_degree(cusp) == 3
    assert blowup.curve_multiplicity_at_center(cusp) == 2
    assert inverse_image.defining_equations() == total.defining_equations()
    assert blowup.total_transform_picard_class(cusp) == 3 * hyperplane
    assert blowup.strict_transform_picard_class(cusp) == 3 * hyperplane - 2 * exceptional
    assert total.divisor_class() == 3 * hyperplane
    assert strict.divisor_class() == 3 * hyperplane - 2 * exceptional
