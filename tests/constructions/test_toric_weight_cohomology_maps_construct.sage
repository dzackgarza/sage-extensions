r"""Toric weight cohomology exposes its comparison and weight summand maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_weight_complex_records_simplicial_comparison() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    complex_ = plane.weight_cohomology_complex(
        plane.hyperplane_divisor(),
        plane.character_lattice().zero(),
    )

    assert "shifted reduced simplicial cohomology" in complex_.comparison_description()


def test_weight_piece_inclusion_and_projection_split() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cohomology = plane.line_bundle_cohomology(plane.hyperplane_divisor(), 0)

    for weight in cohomology.cohomology_weight_support():
        piece = cohomology.cohomology_weight_piece(weight)
        inclusion = cohomology.cohomology_weight_inclusion(weight)
        projection = cohomology.cohomology_weight_projection(weight)
        assert inclusion.domain() is piece
        assert inclusion.codomain() is cohomology
        assert projection.domain() is cohomology
        assert projection.codomain() is piece
        assert projection * inclusion == piece.Mor(piece).identity()
