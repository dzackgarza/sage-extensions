r"""Cotangent and tangent spaces at a point of an affine spectrum.

The cotangent space is the fibre of the module of Kähler differentials, and the
tangent space is its dual over the residue field.  For the affine plane both
have dimension two at every point; for the node ``y^2 = x^3 + x^2`` the
cotangent space at the origin still has dimension two while the curve has
dimension one, which is what makes the origin singular.
"""

from sage_extensions.all import *


def test_the_affine_plane_has_a_two_dimensional_cotangent_space() -> None:
    plane = QQ.polynomial_ring("x,y")
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    differentials = plane.kahler_differentials()
    origin = plane.spectrum()(plane.ideal(x, y))

    assert differentials.cotangent_space(origin).dimension() == 2
    assert differentials.tangent_space(origin).base_ring() is origin.residue_field()


def test_the_node_has_a_two_dimensional_cotangent_space_at_its_singular_point() -> None:
    plane = QQ.polynomial_ring("x,y")
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    node = (plane).quotient_by_relations([y**2 - x**3 - x**2])
    differentials = node.kahler_differentials()
    origin = node.spectrum()(node.ideal(node(x), node(y)))

    assert differentials.cotangent_space(origin).dimension() == 2
