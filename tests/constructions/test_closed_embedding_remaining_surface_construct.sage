r"""Closed embeddings expose restriction, factorization, intersection, and emptiness."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_hyperplane_restricts_standard_line_bundles() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    hyperplane = plane.hyperplane(0)

    assert hyperplane.O(2) == plane.O(2).restrict_to(hyperplane)


def test_closed_embedding_corestricts_its_inclusion_to_identity() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_algebra().algebra_generator("x")
    axis = plane.closed_subscheme(x)

    assert axis.corestriction(axis.inclusion()) == axis.categorical_identity_morphism()


def test_affine_axes_intersect_in_the_origin_and_disjoint_lines_are_empty() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    origin = plane.closed_subscheme(x).intersection(plane.closed_subscheme(y))
    empty = plane.closed_subscheme(x).intersection(plane.closed_subscheme(x - ring.one()))

    assert origin.codimension() == 2
    assert not origin.is_empty()
    assert empty.is_empty()
