r"""A represented coverage is the selected subcategory of covering families."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coverage_retains_the_selected_covering_family_subcategory() -> None:
    site = Sets()
    families = TrivialCoveringFamilies(site)
    coverage = Coverage(site, families)
    points = site(("a", "b"))
    cover = coverage.family(points)

    assert coverage is families
    assert cover in coverage
    assert cover in CoveringFamilies(site)
    assert cover.coverage() is coverage
