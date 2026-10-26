r"""Metric invariants of the square lattice and the hexagonal lattice A2.

Values: Conway--Sloane, *Sphere Packings, Lattices and Groups*, 1.2 and 4.6.1.
"""

from sage_extensions.all import *


def test_square_lattice_metric_invariants_are_exact() -> None:
    r"""\(\mathbf Z^2\): kissing number 4, packing radius 1/2, covering radius \(1/\sqrt2\),
    Hermite invariant 1, center density 1/4, packing density \(\pi/4\)."""
    lattice = Lattices(ZZ)(2)
    e1, _e2 = lattice.module_generators()
    target = (QQ(3) / 4, QQ(1) / 4)

    assert lattice.closest_vector(target) == e1
    minima = lattice.successive_minima()
    assert minima.cardinality() == 2
    assert minima[0] == 1
    assert minima[1] == 1

    theta = lattice.theta_series(5)
    assert theta[0] == 1
    assert theta[1] == 4
    assert lattice.kissing_number() == 4

    assert lattice.packing_radius() == QQ(1) / 2
    assert lattice.covering_radius() ** 2 == QQ(1) / 2
    assert lattice.hadamard_ratio() == 1
    assert lattice.hermite_invariant() == 1
    assert lattice.center_density() == QQ(1) / 4
    assert lattice.packing_density() == RR.pi() / 4
    assert lattice.contact_polytope().n_vertices() == 4


def test_a2_invariants_see_the_nonorthogonal_hexagonal_geometry() -> None:
    r"""\(A_2\): kissing number 6, six Voronoi-relevant vectors, successive minima
    \(\sqrt2,\sqrt2\), \(\gamma^2=\min^2/\det=4/3\)."""
    lattice = Lattices(ZZ)("A2")

    assert lattice.minimum() == -2
    assert lattice.kissing_number() == 6
    assert lattice.contact_polytope().n_vertices() == 6
    assert lattice.voronoi_relevant_vectors().cardinality() == 6

    minima = lattice.successive_minima()
    assert minima.cardinality() == 2
    assert minima[0] ** 2 == 2
    assert minima[1] ** 2 == 2

    assert lattice.hermite_invariant() ** 2 == QQ(4) / 3
    assert lattice.packing_radius() ** 2 == QQ(1) / 2
