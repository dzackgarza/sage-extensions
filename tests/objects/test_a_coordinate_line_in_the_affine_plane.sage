from sage_extensions.all import *


def plane():
    return AffineSpaces(QQ)(2, names=("x", "y"))


def axis():
    r"""$V(x) \subset \mathbb A^2_{\mathbb Q}$."""
    ambient = plane()
    return ambient.closed_subscheme(ambient.coordinate_ring().algebra_generator("x"))


def test_the_axis_is_an_affine_line() -> None:
    r"""$\mathbb Q[x, y]/(x) \cong \mathbb Q[y]$."""
    assert axis().is_isomorphic_to(AffineSpaces(QQ)(1))


def test_the_categories_of_the_axis() -> None:
    line = axis()
    assert line in Schemes(QQ)
    assert line in ClosedSubschemes(QQ)
    assert line in SmoothSchemes(QQ)
    assert line in IntegralSchemes(QQ)
    assert line in Curves(QQ)


def test_the_axis_is_a_closed_subscheme_of_codimension_one() -> None:
    line = axis()
    assert line.relative_dimension() == 1
    assert line.dimension() == 1
    assert line.codimension() == 1
    assert line.ambient_scheme() == plane()
    assert line.inclusion().codomain() == plane()
    assert line.coordinate_ring().krull_dimension() == 1


def test_the_axis_has_one_endomorphism_category() -> None:
    line = axis()
    endomorphisms = line.Mor(line)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert line.Mor(line) is endomorphisms
    assert identity * identity == identity
