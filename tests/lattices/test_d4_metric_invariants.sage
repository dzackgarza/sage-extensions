r"""Metric invariants of the negative definite root lattice \(D_4\) and of \(A_2\).

Here \(D_4\) is \(\{x \in \mathbf Z^4 : \sum x_i \equiv 0 \bmod 2\}\) with the negated
standard form, presented on its simple roots.  Every value below is derived from that
model; no table is quoted.

- Roots: \(\pm e_i \pm e_j\), \(i<j\), so \(2 \cdot 4 \cdot 3 = 24\) vectors of square
  \(-2\).  Vectors of square \(-4\): \((\pm2,0,0,0)\) and \((\pm1,\pm1,\pm1,\pm1)\),
  \(8+16=24\).  Vectors of square \(-6\): \((\pm2,\pm1,\pm1,0)\) up to position,
  \(4\cdot3\cdot8=96\).
- \(\det = 4\), so the Hermite invariant \(\gamma = |\min|/\det^{1/4} = \sqrt2\), and the
  Gaussian heuristic \((\det^{1/2}/V_4)^{1/4}\) with \(V_4=\pi^2/2\) has fourth power
  \(4/\pi^2\).
- The simple roots have square norm 2, so the Hadamard ratio
  \((\det/\prod|b_i|^2)^{1/(2n)}\) has eighth power \(4/16\).
- The points \((1,0,0,0)\) and \((\tfrac12,\tfrac12,\tfrac12,\tfrac12)\) lie at distance 1
  from \(D_4\) and no point is further, so the covering radius is 1; the packing radius is
  half the minimal length, \(\sqrt2/2\), and the center density
  \(\rho^4/\sqrt{\det}\) is \(1/8\).
- The Voronoi cell is the 24-cell: 24 facets, one per root, each an octahedron.
"""

from sage_extensions.all import *


def test_the_roots_of_d4_are_its_shortest_vectors_and_its_kissing_configuration() -> None:
    lattice = Lattices(ZZ)("D4")

    assert lattice.is_negative_definite()
    assert lattice.determinant() == 4
    assert lattice.minimum() == -2
    assert lattice.kissing_number() == 24
    assert lattice.contact_polytope().n_vertices() == 24
    for root in lattice.roots_of_square(-2):
        assert root.q() == -2
        assert root.is_root()


def test_the_numbers_of_vectors_of_squares_minus_two_four_and_six_in_d4() -> None:
    lattice = Lattices(ZZ)("D4")

    assert lattice.roots_of_square(-2).cardinality() == 24
    assert lattice.vectors_of_square(-4).cardinality() == 24
    assert lattice.vectors_of_square(-6).cardinality() == 96


def test_d4_successive_minima_hermite_invariant_and_gaussian_heuristic() -> None:
    lattice = Lattices(ZZ)("D4")
    minima = lattice.successive_minima()

    for index in range(4):
        assert minima[index] ** 2 == 2
    assert lattice.hermite_invariant() ** 2 == 2
    assert lattice.gaussian_heuristic() ** 4 == 4 / pi ** 2
    assert lattice.hadamard_ratio() ** 8 == QQ(1) / 4


def test_d4_has_four_successive_minima() -> None:
    assert Lattices(ZZ)("D4").successive_minima().cardinality() == 4


def test_the_voronoi_cell_of_d4_is_the_24_cell() -> None:
    lattice = Lattices(ZZ)("D4")

    for vector in lattice.voronoi_relevant_vectors():
        assert vector.q() == -2
    assert lattice.voronoi_cell().n_vertices() == 24
    for facet in lattice.voronoi_facets().values():
        assert facet.n_vertices() == 6


def test_d4_has_24_voronoi_relevant_vectors_and_24_voronoi_facets() -> None:
    lattice = Lattices(ZZ)("D4")

    assert lattice.voronoi_relevant_vectors().cardinality() == 24
    assert lattice.voronoi_facets().cardinality() == 24


def test_the_covering_radius_of_d4_is_one() -> None:
    assert Lattices(ZZ)("D4").covering_radius() == 1


def test_the_packing_radius_and_center_density_of_d4() -> None:
    lattice = Lattices(ZZ)("D4")

    assert lattice.packing_radius() ** 2 == QQ(1) / 2
    assert lattice.center_density() == QQ(1) / 8
    assert lattice.packing_density() == pi ** 2 / 16


def test_the_root_sublattice_of_d4_is_all_of_d4() -> None:
    r"""A sublattice of full rank and equal determinant has index one."""
    root_sublattice = Lattices(ZZ)("D4").root_sublattice()

    assert root_sublattice.determinant() == 4
    assert root_sublattice.signature_pair() == signature_pair(0, 4)


def test_the_closest_point_of_a2_to_a_point_near_a_simple_root() -> None:
    r"""With form \(-\begin{pmatrix}2&-1\\-1&2\end{pmatrix}\) in the simple roots, the
    point \(\tfrac34 e_0 + \tfrac14 e_1\) has distance squared \(14/16\) to \(0\) and to
    \(e_0+e_1\), and \(6/16\) to \(e_0\); \(e_0\) is the unique closest lattice point."""
    lattice = Lattices(ZZ)("A2")
    first, _second = lattice.module_generators()

    assert lattice.closest_vector((QQ(3) / 4, QQ(1) / 4)) == first
