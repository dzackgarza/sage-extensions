r"""Scheme morphisms retain selected point, cone, and slice-adjunction data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_point_morphism_retains_its_selected_coordinates() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 2, 3))

    assert tuple(point.point_coordinates()) == (QQ(1), QQ(2), QQ(3))


def test_diagonal_morphism_retains_its_universal_cone_construction() -> None:
    plane = AffineSpaces(QQ)(2)
    diagonal = plane.diagonal_morphism()
    construction = diagonal.cone_construction()
    retained = diagonal.with_cone_construction(construction)

    assert construction is not None
    assert retained == diagonal
    assert retained.cone_construction() is construction


def test_identity_scheme_slice_base_change_adjunction_is_an_endoadjunction() -> None:
    line = AffineSpaces(QQ)(1)
    slices = Schemes(QQ).SliceOver(line)
    adjunction = line.categorical_identity_morphism().slice_base_change_adjunction()

    assert adjunction.left_adjoint().domain() is slices
    assert adjunction.left_adjoint().codomain() is slices
    assert adjunction.right_adjoint().domain() is slices
    assert adjunction.right_adjoint().codomain() is slices
