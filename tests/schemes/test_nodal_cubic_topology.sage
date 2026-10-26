r"""The nodal cubic `y^2 z = x^2 (x + z)` over QQ and its normalization.

Derivation: the complex points of the nodal cubic are `\mathbb{P}^1` with two
points identified, homotopy equivalent to `S^2 \vee S^1`, so
`H^0 = H^1 = H^2 = \mathbb{Z}`; the normalization `\mathbb{P}^1 \to C` has
degree 1, so it is an isomorphism on `H^2` and it kills the loop through the node.
"""

from sage_extensions.all import *


def _nodal_cubic():
    plane = ProjectiveSpaces(QQ)(2)
    x, y, z = plane.homogeneous_coordinate_generators()
    return plane.closed_subscheme(y**2 * z - x**2 * (x + z))


def test_nodal_cubic_has_first_betti_number_one_and_its_normalization_zero() -> None:
    curve = _nodal_cubic()
    normalization = curve.normalization()

    assert curve.arithmetic_genus() == 1
    assert curve.integral_cohomology(0).module_rank() == 1
    assert curve.integral_cohomology(1).module_rank() == 1
    assert curve.integral_cohomology(2).module_rank() == 1
    assert normalization.domain().genus() == 0
    assert normalization.domain().integral_cohomology(1).module_rank() == 0


def test_normalization_pullback_kills_h1_and_is_an_isomorphism_on_h2() -> None:
    normalization = _nodal_cubic().normalization()
    on_h1 = normalization.cohomology_pullback(1)
    on_h2 = normalization.cohomology_pullback(2)

    assert on_h1.is_zero()
    assert on_h2.is_isomorphism()
