r"""The rational parametrization of the nodal cubic `y^2 z = x^2 (x + z)`.

Derivation: with `(x, y, z) = ((s^2 - t^2) t, s (s^2 - t^2), t^3)` both sides of
the equation equal `s^2 (s^2 - t^2)^2 t^3`; `(1:0) \mapsto (0:1:0)`, and the two
points `(1:\pm 1)` both map to the node `(0:0:1)`.
"""

from sage_extensions.all import *


def _parametrization():
    line = ProjectiveSpaces(QQ)(1, names=("s", "t"))
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    s, t = line.homogeneous_coordinate_generators()
    x, y, z = plane.homogeneous_coordinate_generators()
    curve = plane.closed_subscheme(y**2 * z - x**2 * (x + z))
    ambient = line.projective_morphism_from_coordinates(
        plane,
        ((s**2 - t**2) * t, s * (s**2 - t**2), t**3),
    )
    return line, curve, curve.corestriction(ambient)


def test_cubic_parametrization_factors_through_the_nodal_cubic_birationally() -> None:
    line, curve, parametrization = _parametrization()

    assert parametrization.domain() is line
    assert parametrization.codomain() is curve
    assert parametrization.degree() == 1


def test_parametrization_sends_the_two_points_s_equals_plus_minus_t_to_the_node() -> None:
    line, curve, parametrization = _parametrization()
    node = curve.point((0, 0, 1))

    assert parametrization(line.point((1, 0))) == curve.point((0, 1, 0))
    assert parametrization(line.point((1, 1))) == node
    assert parametrization(line.point((1, -1))) == node
    assert curve.singular_locus().point_count() == 1
