r"""Distinguished-cover refinements expose their chart and geometric comparison maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _refinement_of_affine_line_covers():
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_algebra()
    x = ring.algebra_generator("x")
    covers = DistinguishedAffineCovers(line)
    two_chart = line.distinguished_open_cover(x, ring.one() - x)
    identity_cover = covers.an_object()
    refinement = two_chart.common_refinement(identity_cover).left_leg()
    return line, refinement


def test_refinement_chart_map_has_the_underlying_geometric_inclusion() -> None:
    _line, refinement = _refinement_of_affine_line_covers()
    chart = refinement.fine_cover().atlas()[0]

    assert refinement.chart_map(chart).factor_morphism() == refinement.inclusion(chart)


def test_refinement_geometric_cohomology_comparison_is_induced_between_cochain_cohomologies() -> None:
    line, refinement = _refinement_of_affine_line_covers()
    sheaf = line.structure_sheaf()
    cochain_map = refinement.geometric_cochain_map(sheaf)
    comparison = refinement.geometric_cohomology_comparison(sheaf, 0)

    assert comparison.domain() is cochain_map.domain().cohomology(0)
    assert comparison.codomain() is cochain_map.codomain().cohomology(0)
