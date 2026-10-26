r"""Schemes expose slice/diagonal maps, fibres, selected atlases, and finite-field point counts."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_slice_and_diagonal_data() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    product = Schemes(QQ).product((plane, plane))
    diagonal = plane.diagonal_morphism()
    diagonal_subscheme = plane.diagonal_subscheme()
    identity = plane.categorical_identity_morphism()

    assert plane.scheme_category() is Schemes(QQ)
    assert plane.as_slice_object().arrow() is plane.structure_morphism()
    assert product.projection(0) * diagonal == identity
    assert product.projection(1) * diagonal == identity
    assert diagonal_subscheme.codimension() == 2


def test_local_family_generic_special_and_ideal_fibres() -> None:
    polynomial = QQ["t"]
    t = polynomial.algebra_generator("t")
    base = polynomial.localize_at_prime(polynomial.ideal(t))
    algebra = base["x,y"]
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    family = algebra.quotient(algebra.ideal(x * y - t)).affine_spectrum()
    generic = SchemesOverIntegralDomains(base)(family).generic_fiber()
    special = SchemesOverLocalRings(base)(family).special_fiber()
    by_ideal = family.fiber_over_ideal(base.maximal_ideal())
    comparison = SchemesOverLocalRings(base)(family).special_fiber_comparison()
    forward = comparison.forward()
    inverse = comparison.inverse()

    assert generic.dimension() == 1
    assert generic.is_smooth()
    assert special.dimension() == 1
    assert not special.is_smooth()
    assert by_ideal.is_isomorphic(special)
    assert forward * inverse == forward.codomain().categorical_identity_morphism()
    assert inverse * forward == forward.domain().categorical_identity_morphism()


def test_projective_line_selected_atlas_glues_identity_map() -> None:
    line = ProjectiveSpaces(QQ)(1)
    atlas = line.selected_finite_affine_atlas()
    reconstructed = line.morphism_from_finite_atlas(
        line,
        atlas.embeddings(),
        atlas=atlas,
    )
    glued = line.glued_from_standard_charts()

    assert line.has_selected_finite_affine_atlas()
    assert atlas is line.standard_affine_atlas()
    assert reconstructed == line.categorical_identity_morphism()
    assert glued.finite_affine_atlas().charts().cardinality() == cardinal(2)


def test_affine_line_point_counts_over_two_extensions() -> None:
    line = AffineSpaces(GF(5))(1)
    counts = line.point_counts(2)

    assert tuple(counts) == (ZZ(5), ZZ(25))
