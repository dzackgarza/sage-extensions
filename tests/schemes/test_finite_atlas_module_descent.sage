r"""Line bundles on ``P^1`` glued from a transition function.

Cover ``P^1`` by ``U_0 = Spec QQ[t]`` and ``U_1 = Spec QQ[s]`` with ``s = 1/t`` on
``U_0 ∩ U_1``.  Gluing ``O_{U_0} e_0`` and ``O_{U_1} e_1`` by ``e_0 = t^{-d} e_1``
gives a line bundle whose global sections are the pairs ``(f(t), g(s))`` with
``f(t) t^{-d} = g(1/t)``, that is ``f`` a polynomial of degree at most ``d``:
``h^0 = d + 1`` for ``d >= 0`` and ``h^0 = 0`` for ``d < 0``.  This is ``O(d)``
(Hartshorne III.5.1 gives ``h^0(O(d)) = d + 1``).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _projective_line():
    L = QQ['t']
    t = L.gen()
    M = QQ['s']
    s = M.gen()
    U0 = L.affine_spectrum()
    U1 = M.affine_spectrum()
    overlap = U0.basic_open(t)
    transition = overlap.Mor(U1.basic_open(s))({s: overlap.coordinate_ring()(t) ** -1})
    P1 = Schemes(QQ).glue((U0, U1), {(0, 1): transition})
    return P1, overlap.coordinate_ring()(t)


def test_the_line_bundle_with_transition_t_to_the_minus_d_has_d_plus_one_sections() -> None:
    r"""``h^0`` of the bundle glued by ``e_0 = t^{-d} e_1`` is ``1, 2, 3, 4`` for ``d = 0, 1, 2, 3``."""
    P1, t = _projective_line()

    for d in (0, 1, 2, 3):
        bundle = P1.line_bundle({(0, 1): t ** (-d)})
        assert bundle.global_sections().dimension() == d + 1


def test_the_line_bundle_with_transition_t_to_the_d_has_no_sections_for_positive_d() -> None:
    r"""``e_0 = t^d e_1`` with ``d > 0`` forces ``f(t) t^d = g(1/t)``, so ``f = g = 0``: ``h^0 = 0``."""
    P1, t = _projective_line()

    for d in (1, 2):
        assert P1.line_bundle({(0, 1): t**d}).global_sections().dimension() == 0


def test_the_trivial_transition_glues_the_structure_sheaf_and_opposite_transitions_are_dual() -> None:
    r"""Transition ``1`` gives ``O_{P^1}``; ``t^{-1}`` and ``t`` give ``O(1)`` and ``O(-1)``, whose tensor product is ``O``.

    Derivation: the transition function of a tensor product of line bundles is the product of theirs.
    """
    P1, t = _projective_line()
    trivial = P1.line_bundle({(0, 1): t**0})
    positive = P1.line_bundle({(0, 1): t**-1})
    negative = P1.line_bundle({(0, 1): t})

    assert trivial.is_isomorphic(P1.structure_sheaf())
    assert positive.tensor_product(negative).is_isomorphic(P1.structure_sheaf())
    assert not positive.is_isomorphic(P1.structure_sheaf())
    assert not positive.is_isomorphic(negative)
