from sage_extensions.all import *


def l2():
    return Lp(2, RR, RR)


def test_l2_is_its_own_holder_conjugate() -> None:
    r"""$1/2 + 1/2 = 1$."""
    assert l2().conjugate_lebesgue_space() is l2()
    assert l2().integrability_exponent() == 2


def test_the_holder_conjugate_of_l1() -> None:
    assert Lp(1, RR, RR).conjugate_lebesgue_space() is Lp(Infinity, RR, RR)


def test_the_categories_of_l2() -> None:
    space = l2()
    assert space in VectorSpaces(RR)
    assert space in SymmetricBilinearFormModules(RR)
    assert space in FormModules(RR)
    assert Lp(1, RR, RR) not in FormModules(RR)


def test_the_form_on_a_gaussian() -> None:
    r"""$\int_{\mathbb R} e^{-2t^2}\,dt = \sqrt{\pi/2}$, and $b(f, f) = 2q(f)$."""
    space = l2()
    maps = C(Infinity, RR, RR)
    g(t) = exp(-t^2)
    gaussian = space(maps(g))
    assert space.b(gaussian, gaussian) == sqrt(pi / 2)
    assert space.b(gaussian, gaussian) == 2 * space.q(gaussian)


def test_l2_has_one_endomorphism_category() -> None:
    space = l2()
    endomorphisms = space.Mor(space)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert space.Mor(space) is endomorphisms
    assert identity * identity == identity
