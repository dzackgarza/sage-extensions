r"""P^1 x P^1 has its standard four-chart cover and canonical bundle O(-2,-2)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_product_of_projective_lines_standard_geometry() -> None:
    line = ProjectiveSpaces(QQ)(1)
    surface = Schemes(QQ).product((line, line))
    atlas = surface.standard_affine_atlas()

    assert surface in ProductProjectiveSpaces(QQ)
    assert surface.canonical_bundle() == surface.O(-2, -2)
    assert surface.anticanonical_bundle() == surface.O(2, 2)
    assert atlas.charts().cardinality() == cardinal(4)
    assert surface.is_covered_by_open_immersions(atlas.embeddings())
