r"""The exported trivial coverage is the singleton identity coverage."""

from sage_extensions.all import *  # noqa: F401,F403


def test_trivial_coverage_function_returns_the_identity_singleton_coverage() -> None:
    site = Sets()
    points = site(("a", "b"))
    coverage = trivial_coverage(site)
    cover = coverage.family(points)
    index = cover.index_set().an_element()

    assert coverage is TrivialCoveringFamilies(site)
    assert cover.covered_object() is points
    assert cover.index_set().cardinality() == cardinal(1)
    assert cover.member(index) == site.Mor(points, points).identity()
