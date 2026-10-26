r"""The zero Cartier divisor on P^1 has unit local equations and trivial transition units."""

from sage_extensions.all import *  # noqa: F401,F403


def test_zero_cartier_divisor_on_standard_projective_line_atlas() -> None:
    line = ProjectiveSpaces(QQ)(1)
    atlas = line.standard_affine_atlas()
    group = line.cartier_divisor_group()
    equations = [
        (index, atlas.chart(index).coordinate_algebra().one())
        for index in atlas.chart_indices()
    ]
    divisor = group.finite_atlas_section(atlas, equations)

    assert divisor.gluing_datum() is atlas
    for index in atlas.chart_indices():
        assert divisor.local_equation(index).is_one()
    for source, target in atlas.transition_index_set():
        assert divisor.transition_unit(source, target).is_one()
    assert divisor.associated_invertible_sheaf().associated_divisor() is divisor
