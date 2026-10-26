r"""The quotient of the non-affine scheme ``P^1`` by a finite group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_swap_on_p1_has_two_fixed_points_and_quotient_p1_by_a_degree_two_map() -> None:
    r"""``[x : y] -> [y : x]`` on ``P^1_QQ`` fixes ``[1 : 1]`` and ``[1 : -1]``, and ``P^1/C_2 ≅ P^1``.

    Derivation: the fixed locus is ``V(x^2 - y^2)``; the invariant map
    ``[x : y] -> [x^2 + y^2 : xy]`` is base-point free of degree 2, so it is the
    quotient map.  The swap exchanges the standard charts, so the quotient is
    glued from the affine quotients of the invariant opens ``D_+(xy)`` and
    ``D_+(x^2 + y^2)``, which cover ``P^1``.
    """
    P1 = Schemes(QQ).projective_space(1, names=("x", "y"))
    x, y = P1.coordinate_ring().algebra_generator("x"), P1.coordinate_ring().algebra_generator("y")
    swap = P1.projective_morphism_from_coordinates(P1, (y, x))
    G = Groups.C(2)
    acted = GObjects(G, Schemes(QQ))(P1, G.Mor(P1.automorphism_group())({G.gen(): swap}))
    quotient_map = P1.projective_morphism_from_coordinates(P1, (x**2 + y**2, x * y))

    assert swap * swap == P1.identity_morphism()
    assert P1.fixed_locus(swap).degree() == 2
    assert P1.fixed_locus(swap).defining_ideal() == P1.coordinate_ring().ideal(x**2 - y**2)
    assert not acted.is_free()
    assert acted.quotient().is_isomorphic(P1)
    assert quotient_map * swap == quotient_map
    assert quotient_map.degree() == 2
