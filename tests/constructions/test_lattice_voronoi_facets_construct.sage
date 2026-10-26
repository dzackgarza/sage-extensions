r"""The two facets of the integer-line Voronoi interval are points."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_line_voronoi_facets_are_two_points() -> None:
    lattice = Lattices(ZZ)(ZZ^1)
    facets = lattice.voronoi_facets()

    assert facets.cardinality() == cardinal(2)
    for facet in facets.values():
        assert facet.n_vertices() == 1
