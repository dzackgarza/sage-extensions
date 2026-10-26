r"""Scheme-theoretic fixed loci of involutions of ``A^2`` and ``P^1 x P^1``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_fixed_locus_of_the_coordinate_swap_on_a2_is_the_diagonal() -> None:
    r"""The swap ``x <-> y`` on ``A^2_QQ`` has fixed ideal ``(x - y, y - x) = (x - y)``: the diagonal line."""
    A = QQ['x,y']
    x, y = A.algebra_generator("x"), A.algebra_generator("y")
    X = A.affine_spectrum()
    swap = X.Mor(X)(A.Mor(A)({x: y, y: x}))
    G = Groups.C(2)
    acted = GObjects(G, Schemes(QQ))(X, G.Mor(X.automorphism_group())({G.gen(): swap}))
    fixed = acted.fixed_locus()

    assert fixed.defining_ideal() == A.ideal(x - y)
    assert fixed.dimension() == 1
    assert fixed.is_smooth()
    assert swap * fixed.inclusion() == fixed.inclusion()


def test_on_p1_times_p1_the_diagonal_sign_has_four_fixed_points_and_the_factor_swap_fixes_the_diagonal() -> None:
    r"""``s = [x_0 : -x_1]`` fixes ``[1:0]`` and ``[0:1]`` on ``P^1``, so ``s x s`` fixes ``2 x 2 = 4`` points;
    the factor swap ``(p, q) -> (q, p)`` fixes the diagonal ``Δ ≅ P^1``, a curve.

    Derivation: ``[x_0 : x_1] = [x_0 : -x_1]`` iff ``x_0 x_1 = 0`` (characteristic 0).
    """
    P1 = Schemes(QQ).projective_space(1, names=("x0", "x1"))
    x0 = P1.coordinate_ring().algebra_generator("x0")
    x1 = P1.coordinate_ring().algebra_generator("x1")
    s = P1.projective_morphism_from_coordinates(P1, (x0, -x1))
    Q = P1.product(P1)
    p, q = Q.projection(0), Q.projection(1)
    diagonal_sign = Q.morphism_from_components((s * p, s * q))
    factor_swap = Q.morphism_from_components((q, p))

    assert P1.fixed_locus(s).rational_points().cardinality() == 2
    assert Q.fixed_locus(diagonal_sign).dimension() == 0
    assert Q.fixed_locus(diagonal_sign).rational_points().cardinality() == 4
    assert factor_swap * factor_swap == Q.identity_morphism()
    assert Q.fixed_locus(factor_swap).dimension() == 1
    assert Q.fixed_locus(factor_swap).is_isomorphic(P1)
