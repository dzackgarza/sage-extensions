r"""The singular locus of an affine algebra, from the Fitting ideals of Omega.

The d-th Fitting ideal of a finitely presented module cuts out the points where
its rank exceeds d.  For an algebra of finite type over a field and of relative
dimension d, the differentials have rank d exactly where it is smooth, so that
closed set is the singular locus.  The node ``y^2 = x^3 + x^2`` is a curve, so
d is one, and its singular locus is the origin alone.
"""

from sage_extensions.all import *


def test_the_node_is_singular_at_the_origin_and_nowhere_else() -> None:
    plane = QQ.polynomial_ring("x,y")
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    node = (plane).quotient_by_relations([y**2 - x**3 - x**2])
    differentials = node.kahler_differentials()

    singular = differentials.non_smooth_locus(1)
    origin = node.spectrum()(node.ideal(node(x), node(y)))
    # (3, 6) lies on the node: 36 = 27 + 9.
    smooth_point = node.spectrum()(
        node.ideal(node(x) - 3 * node.one(), node(y) - 6 * node.one())
    )

    assert origin in singular
    assert smooth_point not in singular


def test_the_affine_line_is_smooth_everywhere() -> None:
    line = QQ.polynomial_ring("t")
    t = line.algebra_generator("t")
    differentials = line.kahler_differentials()

    singular = differentials.non_smooth_locus(1)

    assert line.spectrum()(line.ideal(t)) not in singular
