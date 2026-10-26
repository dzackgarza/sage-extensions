from sage_extensions.all import *


def plane():
    return ProjectiveSpaces(QQ)(2)


def test_the_projective_plane_is_glued_from_its_charts() -> None:
    assert plane().glued_from_standard_charts().is_isomorphic_to(plane())


def test_the_categories_of_the_projective_plane() -> None:
    scheme = plane()
    assert scheme in Schemes(QQ)
    assert scheme in ProjectiveSpaces(QQ)
    assert scheme in ProjectiveSchemes(QQ)
    assert scheme in SmoothSchemes(QQ)
    assert scheme in IntegralSchemes(QQ)
    assert scheme in Surfaces(QQ)
    assert scheme not in AffineSchemes(QQ)


def test_the_invariants_of_the_projective_plane() -> None:
    scheme = plane()
    assert scheme.relative_dimension() == 2
    assert scheme.dimension() == 2
    assert scheme.is_projective()


def test_the_standard_affine_charts() -> None:
    r"""$\mathbb P^2 = D_+(x_0) \cup D_+(x_1) \cup D_+(x_2)$, each chart an $\mathbb A^2$."""
    charts = plane().standard_affine_charts()
    assert charts.cardinality() == 3
    assert plane().standard_affine_chart(0).is_isomorphic_to(AffineSpaces(QQ)(2))


def test_the_picard_group_and_the_canonical_bundle() -> None:
    r"""$\operatorname{Pic}\mathbb P^n = \mathbb Z\,\mathcal O(1)$ and $\omega_{\mathbb P^n} = \mathcal O(-n-1)$ (Hartshorne II.6.17, II.8.13)."""
    scheme = plane()
    assert scheme.picard_group().is_isomorphic_to(Groups.Abelian([0]))
    assert scheme.canonical_bundle() == scheme.O(-3)
    assert scheme.anticanonical_bundle() == scheme.O(3)


def test_the_projective_plane_has_one_endomorphism_category() -> None:
    scheme = plane()
    endomorphisms = scheme.Mor(scheme)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert scheme.Mor(scheme) is endomorphisms
    assert identity * identity == identity
