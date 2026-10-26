r"""Closed embeddings expose homogeneous equations in projective space and ideal sheaves on affine space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_hyperplane_has_its_homogeneous_equation() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    hyperplane = plane.hyperplane(0)
    coordinate_ring = plane.O(1).global_sections().homogeneous_coordinate_ring()
    equations = hyperplane.homogeneous_defining_equations(coordinate_ring)

    assert equations.cardinality() == cardinal(1)
    assert equations[0] == coordinate_ring.algebra_generator("x")


def test_affine_parabola_ideal_sheaf_has_defining_ideal_as_global_sections() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola.ideal_sheaf().global_sections() == parabola.defining_ideal_owned()
