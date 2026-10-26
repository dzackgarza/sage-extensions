r"""Plane curves: genus of the cuspidal cubic and reducibility of the coordinate cross."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_cuspidal_cubic_has_arithmetic_genus_one_and_geometric_genus_zero() -> None:
    r"""``V(y^2 z - x^3) ⊂ P^2`` has ``p_a = (3-1)(3-2)/2 = 1`` and ``g = 0``.

    Hartshorne, *Algebraic Geometry*, I Ex. 7.2(b) (plane curve of degree ``d`` has
    ``p_a = (d-1)(d-2)/2``); the cusp has ``delta = 1`` and normalization ``P^1``
    by ``t -> (t^2 : t^3 : 1)``.
    """
    P2 = Schemes(QQ).projective_space(2, names=("x", "y", "z"))
    x = P2.coordinate_ring().algebra_generator("x")
    y = P2.coordinate_ring().algebra_generator("y")
    z = P2.coordinate_ring().algebra_generator("z")
    cubic = P2.closed_subscheme(y**2 * z - x**3)

    assert cubic.dimension() == 1
    assert cubic.arithmetic_genus() == 1
    assert cubic.geometric_genus() == 0
    assert not cubic.is_smooth()


def test_the_coordinate_cross_xy_is_reducible_with_two_components() -> None:
    r"""``V(xy) ⊂ A^2_QQ`` is the union of the two axes: reduced, one-dimensional, not irreducible.

    Derivation: the minimal primes of ``(xy)`` in ``QQ[x, y]`` are ``(x)`` and ``(y)``.
    """
    R = QQ['x,y']
    x, y = R.algebra_generator("x"), R.algebra_generator("y")
    cross = R.affine_spectrum().closed_subscheme(x * y)

    assert cross.dimension() == 1
    assert cross.is_reduced()
    assert not cross.is_irreducible()
    assert cross.irreducible_components().cardinality() == 2
    assert R.ideal(x * y).minimal_associated_primes() == Set([R.ideal(x), R.ideal(y)])
