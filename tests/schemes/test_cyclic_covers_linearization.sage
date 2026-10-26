r"""The deck linearization of a cyclic cover and its fibres over the base.

For a cyclic cover ``pi: Y -> X`` of degree ``n`` given by ``z^n = f``, the
pushforward ``pi_* O_Y = ⊕_{i<n} O_X z^i`` is the eigen-decomposition of the deck
action.  The degree-three cover ``z^3 = x`` over ``GF(7)`` separates pullback
along a deck transformation from the left action on sections, which is pullback
along the inverse; for ``n = 2`` the two agree.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_deck_involution_acts_by_plus_one_on_o_and_minus_one_on_o_z() -> None:
    r"""On ``pi_* O_Y = O ⊕ O z`` for ``z^2 = x^4 - 1`` the involution acts by ``+1`` and ``-1``.

    Derivation: the deck involution sends ``z -> -z`` and fixes ``QQ[x]``.
    """
    R = QQ['x']
    x = R.gen()
    Y = R.affine_spectrum().cyclic_cover(2, x**4 - 1)
    B = Y.coordinate_ring()
    z = B.algebra_generator("z")
    G = Y.deck_group()
    sigma = G.gen()
    sections = Y.global_sections()

    assert sections.act(sigma, B.one()) == B.one()
    assert sections.act(sigma, B(x**3)) == B(x**3)
    assert sections.act(sigma, z) == -z
    assert sections.act(sigma, x * z) == -(x * z)
    assert sections.act(sigma, sections.act(sigma, z)) == z


def test_the_left_action_on_sections_of_z3_equals_x_is_pullback_along_the_inverse() -> None:
    r"""For ``z^3 = x`` over ``GF(7)``, ``g . s = (g^{-1})^* s``; ``g^* z = zeta z`` and ``g . z = zeta^2 z``.

    ``GF(7)`` contains the primitive cube roots of unity 2 and 4 (``2^3 = 8 = 1``),
    and ``zeta^2 = zeta^{-1}``.  Derivation: a left action on functions must
    satisfy ``(gh) . s = g . (h . s)``, which forces pullback along the inverse.
    """
    R = GF(7)['x']
    x = R.gen()
    Y = R.affine_spectrum().cyclic_cover(3, x)
    B = Y.coordinate_ring()
    z = B.algebra_generator("z")
    g = Y.deck_group().gen()
    pulled = Y.deck_transformation(g).pullback(z)
    acted = Y.global_sections().act(g, z)

    assert Y.deck_group().cardinality() == 3
    assert pulled in (2 * z, 4 * z)
    assert acted in (2 * z, 4 * z)
    assert acted != pulled
    assert acted == Y.deck_transformation(g**-1).pullback(z)


def test_the_fibre_of_z2_equals_x4_minus_1_over_a_branch_point_is_nonreduced() -> None:
    r"""Over ``x = 1`` the fibre is ``Spec QQ[z]/(z^2)``; over ``x = 0`` it is ``Spec QQ[z]/(z^2 + 1)``.

    Derivation: substitute ``x = 1`` and ``x = 0`` into ``z^2 = x^4 - 1``.  The first
    fibre is a double point (the two sheets collide); the second is the reduced
    point ``Spec QQ(i)`` of degree 2.
    """
    R = QQ['x']
    x = R.gen()
    Y = R.affine_spectrum().cyclic_cover(2, x**4 - 1)
    over_one = Y.fiber(R.ideal(x - 1))
    over_zero = Y.fiber(R.ideal(x))

    assert over_one.degree() == 2
    assert not over_one.is_reduced()
    assert over_one.coordinate_ring().nilradical() != over_one.coordinate_ring().zero_ideal()
    assert over_zero.degree() == 2
    assert over_zero.is_reduced()
    assert over_zero.coordinate_ring().is_field()
