from sage_extensions.all import *


def smooth():
    return C(Infinity, RR, RR)


def test_the_constructions_of_smooth_functions_agree() -> None:
    r"""$C^\infty(\mathbb R) = C^\infty(\mathbb R, \mathbb R)$."""
    assert C(Infinity, RR, RR) is smooth()


def test_the_categories_of_smooth_functions() -> None:
    assert smooth() in VectorSpaces(RR)
    assert smooth() in Algebras(RR)


def test_there_are_continuum_many_smooth_functions() -> None:
    r"""A continuous function is fixed by its values on $\mathbb Q$: at most $|\mathbb R|^{\aleph_0} = 2^{\aleph_0}$; the constants give at least that many."""
    assert smooth().cardinality() == continuum


def test_evaluating_a_gaussian() -> None:
    r"""$g(t) = e^{-t^2}$ has $g(0) = 1$, so $(g^2)(0) = 1$ and $(g + g)(0) = 2$."""
    maps = smooth()
    g(t) = exp(-t^2)
    gaussian = maps(g)
    assert gaussian(0) == 1
    assert (gaussian * gaussian)(0) == 1
    assert (gaussian + gaussian)(0) == 2


def test_smooth_functions_have_one_endomorphism_category() -> None:
    maps = smooth()
    endomorphisms = maps.Mor(maps)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert maps.Mor(maps) is endomorphisms
    assert identity * identity == identity
