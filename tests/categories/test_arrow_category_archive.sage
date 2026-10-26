r"""Morphisms in the arrow category of finite sets, and its wide subcategories."""

from sage_extensions.all import *  # noqa: F401,F403


def test_commuting_squares_between_identity_arrows_are_endomorphisms() -> None:
    r"""A morphism ``id_X -> id_X`` in ``Arr(Sets)`` is a pair ``(a, b)`` with
    ``b ∘ id = id ∘ a``, so ``a = b`` and ``|Mor(id_X, id_X)| = |End(X)| = 4`` for a
    two-element ``X``; for ``p : {*} -> X`` the squares ``p -> id_X`` are pairs
    ``(v ∘ p, v)``, again 4."""
    two, one = Sets.Δ[1], Sets.Δ[0]
    arrows = Sets().ArrowCategory()
    identity = arrows(Sets().Mor(two, two).identity())
    point = arrows(Sets().Mor(one, two)(lambda _x: two[0]))

    assert arrows.Mor(identity, identity).cardinality() == 4
    assert arrows.Mor(point, identity).cardinality() == 4
    assert Sets().Mor(two, two).cardinality() == 4


def test_injections_and_isomorphisms_of_a_two_element_set() -> None:
    r"""Of the 4 self-maps of a two-element set, 2 are injective (the identity and
    the swap) and the same 2 are bijections; the swap is an involution."""
    points = Sets.Δ[1]
    maps = Sets().Mor(points, points)
    swap = maps(lambda point: points[1 - int(point)])
    collapse = maps(lambda _point: points[0])
    injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())

    assert injections.admits(swap)
    assert not injections.admits(collapse)
    assert injections.Mor(points, points).cardinality() == 2
    assert Sets().Core().Mor(points, points).cardinality() == 2
    assert swap * swap == maps.identity()


def test_the_bijections_of_a_three_element_set_number_six() -> None:
    r"""``Aut_Set(X) = Sym(X)`` has ``3! = 6`` elements for a three-element ``X``,
    and no bijection joins sets of two and three elements.  The vertex group
    ``Aut_Set(X)`` is a group, so its cardinality is asked through the group and
    set placements and reaches the core Mor's count of bijections."""
    three, two = Sets.Δ[2], Sets.Δ[1]

    assert Sets().Core().Mor(three, three).cardinality() == 6
    assert Sets().Core().Mor(two, three).cardinality() == 0


def test_the_identity_two_arrow_of_an_automorphism_of_a_two_element_set() -> None:
    r"""``Aut_Set(X)`` is also the discrete category whose objects are the
    bijections ``X -> X``; the identity 2-arrow of the swap composes to itself."""
    points = Sets.Δ[1]
    maps = Sets().Mor(points, points)
    swap = maps(lambda point: points[1 - int(point)])
    automorphisms = Sets().Core().Mor(points, points)
    two_identity = automorphisms.identity_2(automorphisms(swap, swap))

    assert two_identity * two_identity == two_identity
