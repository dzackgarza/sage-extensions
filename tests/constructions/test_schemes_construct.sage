r"""Scheme constructions a mathematician expects, over every named ring.

Spectra, affine and projective spaces, closed subschemes, products and fiber
products, over every commutative ring in the catalogue, with the dimensions,
point counts and placements the definitions determine.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_point_counts_of_a_hypersurface_over_a_finite_field() -> None:
    field = GF(5)
    plane = AffineSpaces(field)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    parabola = plane.closed_subscheme(y - x**2)
    assert parabola.point_count() == 5
    assert parabola.point_count(2) == 25


def test_spec_is_a_contravariant_functor(field) -> None:
    spec = Algebras(field).Associative().Unital().Commutative().spectrum()
    polynomials = field.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    squaring = polynomials.Mor(polynomials)({"x": x**2})
    morphism = spec(squaring)

    assert spec(polynomials) is (polynomials).affine_spectrum()
    assert morphism.domain() is (polynomials).affine_spectrum()
    assert morphism.codomain() is (polynomials).affine_spectrum()
    assert spec(squaring * squaring) == spec(squaring) * spec(squaring)
    assert spec(polynomials.Mor(polynomials).identity()) == (polynomials).affine_spectrum().Mor((polynomials).affine_spectrum()).identity()


def test_the_stalk_of_the_structure_sheaf_is_the_local_ring() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_ring()
    x = ring.algebra_generator("x")
    origin = line.underlying_space()(ring.ideal(x))
    stalk = line.stalk(origin)

    assert stalk in LocalRings()
    assert stalk.residue_field() in Fields()
    assert stalk.residue_field().characteristic() == 0
    assert stalk.krull_dimension() == 1
    assert line.structure_sheaf().global_sections() is ring


def test_spec_of_a_field_is_a_point_and_spec_of_the_integers_is_not(build) -> None:
    for name in ("QQ", "GF(5)", "QQ(i)"):
        assert (build(name)).affine_spectrum().relative_dimension() == 0
        assert (build(name)).affine_spectrum() in IntegralSchemes(build(name))
    integers = (ZZ).affine_spectrum()
    assert integers.relative_dimension() == 0
    assert integers.underlying_space().generic_point().residue_field() is QQ
    assert (ZZ).affine_spectrum().Mor((QQ).affine_spectrum()).cardinality() == cardinal(0)
    assert (QQ).affine_spectrum().Mor((ZZ).affine_spectrum()).cardinality() == cardinal(1)
