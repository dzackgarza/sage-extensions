r"""The genus formula ``p_a = g + sum_P [k(P):k] delta_P`` on two rational plane quintics.

A plane quintic has ``p_a = (5-1)(5-2)/2 = 6`` (Hartshorne I Ex. 7.2(b)); the
genus formula is Hartshorne IV Ex. 1.8.  Both specimens are rational, since
``y^2 = x h(x)^2`` is birational to ``y'^2 = x`` by ``y' = y / h(x)``.

* ``Y^2 Z^3 = X (X - Z)^2 (X - 4Z)^2``: nodes at ``(1, 0)`` and ``(4, 0)``
  (tangent cones ``y = ±3(x - 1)`` and ``y = ±6(x - 4)``) with ``delta = 1``, and
  at ``[0:1:0]`` the local equation ``z^3 = x^5 + ...`` with
  ``delta = (3-1)(5-1)/2 = 4``.
* ``Y^2 Z^3 = X (X^2 + Z^2)^2``: one closed point ``(x^2 + 1, y)`` of residue
  degree 2, a node at each of its two geometric points, and the same ``delta = 4``
  point at infinity.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_quintic_with_two_rational_nodes_and_an_e8_point_has_genus_zero_and_arithmetic_genus_six() -> None:
    r"""``p_a = 6 = 0 + 1 + 1 + 4`` for ``Y^2 Z^3 = X (X - Z)^2 (X - 4Z)^2``."""
    P2 = Schemes(QQ).projective_space(2, names=("X", "Y", "Z"))
    X = P2.coordinate_ring().algebra_generator("X")
    Y = P2.coordinate_ring().algebra_generator("Y")
    Z = P2.coordinate_ring().algebra_generator("Z")
    C = P2.closed_subscheme(Y**2 * Z**3 - X * (X - Z) ** 2 * (X - 4 * Z) ** 2)
    singular = C.singular_locus().closed_points()

    assert C.arithmetic_genus() == 6
    assert C.geometric_genus() == 0
    assert C.normalization().arithmetic_genus() == 0
    assert singular.cardinality() == 3
    assert sorted(C.delta_invariant(p) for p in singular) == [1, 1, 4]
    assert all(p.residue_degree() == 1 for p in singular)


def test_a_node_at_a_degree_two_closed_point_contributes_two_to_the_delta_sum() -> None:
    r"""``p_a = 6 = 0 + 2 * 1 + 4`` for ``Y^2 Z^3 = X (X^2 + Z^2)^2`` over ``QQ``."""
    P2 = Schemes(QQ).projective_space(2, names=("X", "Y", "Z"))
    X = P2.coordinate_ring().algebra_generator("X")
    Y = P2.coordinate_ring().algebra_generator("Y")
    Z = P2.coordinate_ring().algebra_generator("Z")
    C = P2.closed_subscheme(Y**2 * Z**3 - X * (X**2 + Z**2) ** 2)
    singular = C.singular_locus().closed_points()

    assert C.arithmetic_genus() == 6
    assert C.geometric_genus() == 0
    assert singular.cardinality() == 2
    assert sorted((p.residue_degree(), C.delta_invariant(p)) for p in singular) == [(1, 4), (2, 1)]
    assert sum(p.residue_degree() * C.delta_invariant(p) for p in singular) == 6
