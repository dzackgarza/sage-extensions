r"""Set invariants of a slice object are those of its retained source."""

from sage_extensions.all import *


def test_a_subset_retains_its_source_points_and_cardinality() -> None:
    points = Sets.Δ[2]
    pair = points.power_set()((points(0), points(1)))

    assert pair.is_finite() is True
    assert pair.cardinality() == 2
    assert tuple(pair) == (points(0), points(1))
    assert points(0) in pair
    assert points(2) not in pair


def test_a_finite_lattice_square_fibre_counts_as_its_source_set() -> None:
    lattice = Lattices(ZZ)([[-1, 0, 0], [0, -1, 0], [0, 0, -1]])

    assert lattice.vectors_of_square(-6).cardinality() == 24
