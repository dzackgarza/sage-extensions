from sage_extensions.all import *


def two():
    return Sets.Δ[1]


def isomorphisms():
    return Sets().Iso(two(), two())


def swap():
    points = two()
    return Sets().Mor(points, points)(lambda point: points(1) if point == points(0) else points(0))


def test_the_isomorphisms_are_the_core_morphisms() -> None:
    assert Sets().Core().Mor(two(), two()).cardinality() == isomorphisms().cardinality()


def test_the_isomorphisms_are_the_automorphism_group() -> None:
    r"""$\operatorname{Iso}(X, X) = \operatorname{Aut}(X) \cong C_2$ for $|X| = 2$."""
    assert Sets().Aut(two()).order() == 2
    assert Sets().Aut(two()).is_isomorphic_to(Groups.C(2))


def test_the_categories_of_the_isomorphisms() -> None:
    assert isomorphisms() in Cat()


def test_there_are_two_isomorphisms() -> None:
    r"""$|\operatorname{Iso}| = 2! = 2$ among $|\operatorname{End}| = 2^2 = 4$."""
    assert isomorphisms().cardinality() == 2
    assert Sets().Mor(two(), two()).cardinality() == 4
    assert Sets().Iso(two(), Sets.Δ[2]).cardinality() == 0


def test_the_swap_is_an_involution() -> None:
    identity = isomorphisms().identity()
    assert swap() != Sets().Mor(two(), two()).identity()
    assert swap() * swap() == Sets().Mor(two(), two()).identity()
    assert identity * identity == identity
