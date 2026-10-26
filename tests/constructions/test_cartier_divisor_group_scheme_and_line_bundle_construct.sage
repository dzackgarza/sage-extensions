r"""A Cartier divisor group remembers its scheme and a divisor exposes its associated line bundle."""

from sage_extensions.all import *  # noqa: F401,F403


def test_zero_cartier_divisor_retains_scheme_and_line_bundle() -> None:
    line = ProjectiveSpaces(QQ)(1)
    atlas = line.standard_affine_atlas()
    group = line.cartier_divisor_group()
    equations = [
        (index, atlas.chart(index).coordinate_algebra().one())
        for index in atlas.chart_indices()
    ]
    divisor = group.finite_atlas_section(atlas, equations)

    assert group.divisor_scheme() is line
    assert divisor.line_bundle() == divisor.associated_invertible_sheaf()
