from sage_extensions.all import *


def coordinates():
    return QQ.polynomial_ring(("x", "y"))


def plane():
    return AffineSpaces(QQ)(2, names=("x", "y"))


def test_the_affine_plane_is_the_spectrum_of_its_coordinate_ring() -> None:
    r"""$\mathbb A^2_{\mathbb Q} = \operatorname{Spec}\mathbb Q[x, y]$."""
    assert plane() == coordinates().affine_spectrum()


def test_the_spectrum_functor_agrees() -> None:
    spectrum = Algebras(QQ).Associative().Unital().Commutative().spectrum()
    assert spectrum(coordinates()) is coordinates().affine_spectrum()


def test_the_unnamed_construction_has_the_same_dimension() -> None:
    assert AffineSpaces(QQ)(2).relative_dimension() == plane().relative_dimension()


def test_the_categories_of_the_affine_plane() -> None:
    scheme = plane()
    assert scheme in Schemes(QQ)
    assert scheme in AffineSchemes(QQ)
    assert scheme in AffineSpaces(QQ)
    assert scheme in SmoothSchemes(QQ)
    assert scheme in IntegralSchemes(QQ)
    assert scheme in Varieties(QQ)
    assert scheme in Surfaces(QQ)


def test_the_invariants_of_the_affine_plane() -> None:
    scheme = plane()
    assert scheme.relative_dimension() == 2
    assert scheme.dimension() == 2
    assert scheme.scheme_base_ring() is QQ
    assert scheme.coordinate_ring() == coordinates()
    assert scheme.coordinate_ring().krull_dimension() == 2


def test_the_picard_and_class_groups_are_trivial() -> None:
    r"""$\mathbb Q[x, y]$ is a unique factorization domain, so $\operatorname{Cl} = \operatorname{Pic} = 0$."""
    scheme = plane()
    assert scheme.picard_group().cardinality() == 1
    assert scheme.class_group().cardinality() == 1


def test_the_affine_plane_has_one_endomorphism_category() -> None:
    scheme = plane()
    endomorphisms = scheme.Mor(scheme)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert scheme.Mor(scheme) is endomorphisms
    assert identity * identity == identity
