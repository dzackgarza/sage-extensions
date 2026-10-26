r"""Rational polyhedral cones cut out by integral covectors in a lattice.

Every claim is read off the defining inequalities.

- The positive orthant \(\{x_0,x_1,x_2 \ge 0\}\) of \(\mathbf Z^3\) is a pointed cone of
  dimension 3 whose primitive rays are \(e_0,e_1,e_2\) and whose three facets are the
  coordinate quarter-planes; the face cut out by the covector \(x_0\) is the facet
  \(\{x_0 = 0\}\), of dimension 2.
- \(\{x_0,x_1\ge0\}\) in \(\mathbf Z^3\) contains the whole line \(\mathbf Z e_2\), so it
  is not pointed.
- Two orthants differing in the sign of one coordinate share a facet; the orthant and its
  negative meet only in the origin.
- The cone \(\{x \ge 0,\; -x+2y \ge 0\}\) in \(\mathbf Z^2\) has primitive rays \((0,1)\) and
  \((2,1)\); the parallelogram they span has area 2 and contains the lattice point
  \((1,1)\), so the Hilbert basis is \(\{(0,1),(1,1),(2,1)\}\).
- In \(U\) the basis vectors are isotropic, so both rays of the quadrant are ideal and
  none is timelike, while \(e_0+e_1\) has square 2.  In \(\langle2\rangle\oplus\langle-1\rangle\)
  the ray \(e_0\) is timelike and \(e_1\) is not.
"""

from sage_extensions.all import *


def test_the_positive_orthant_of_z3() -> None:
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    first, second, third = lattice.module_generators()
    orthant = lattice.reduction_cell(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    assert orthant.dimension() == 3
    assert orthant.ambient_dimension() == 3
    assert orthant.is_pointed()
    for ray in (first, second, third):
        assert ray in orthant.primitive_rays()
    for facet in orthant.facets().values():
        assert facet.dimension() == 2
    assert orthant.face_on_covector((1, 0, 0)).dimension() == 2
    assert orthant.contains(first + second)
    assert not orthant.contains(first - second)
    assert orthant.evaluate_covector((1, 2, 3), first + third) == 4


def test_the_positive_orthant_has_three_rays_three_facets_and_no_lineality() -> None:
    orthant = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).reduction_cell(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    assert orthant.primitive_rays().cardinality() == 3
    assert orthant.facet_covectors().cardinality() == 3
    assert orthant.facets().cardinality() == 3
    assert orthant.lineality_generators().cardinality() == 0


def test_a_wedge_containing_a_line_is_not_pointed() -> None:
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    _first, _second, third = lattice.module_generators()
    wedge = lattice.reduction_cell(((1, 0, 0), (0, 1, 0)))

    assert wedge.dimension() == 3
    assert not wedge.is_pointed()
    assert wedge.contains(third)
    assert wedge.contains(-third)


def test_orthants_sharing_a_facet_are_adjacent_and_opposite_orthants_are_not() -> None:
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    orthant = lattice.reduction_cell(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    reflected = lattice.reduction_cell(((-1, 0, 0), (0, 1, 0), (0, 0, 1)))
    opposite = lattice.reduction_cell(((-1, 0, 0), (0, -1, 0), (0, 0, -1)))

    assert orthant.is_adjacent_to(reflected)
    assert not orthant.is_adjacent_to(opposite)
    assert orthant.intersection(reflected).dimension() == 2
    assert orthant.intersection(opposite).dimension() == 0


def test_the_faces_of_the_positive_orthant_by_dimension() -> None:
    orthant = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).reduction_cell(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    assert orthant.faces(1).cardinality() == 3
    assert orthant.faces(2).cardinality() == 3
    for ray_face in orthant.faces(1):
        assert ray_face.is_face_of(orthant)


def test_the_primitive_rays_of_a_nonunimodular_plane_cone() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    first, second = lattice.module_generators()
    cone = lattice.reduction_cell(((1, 0), (-1, 2)))

    assert second in cone.primitive_rays()
    assert 2 * first + second in cone.primitive_rays()
    assert not (first + second in cone.primitive_rays())


def test_the_hilbert_basis_of_a_nonunimodular_plane_cone() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    first, second = lattice.module_generators()
    basis = lattice.reduction_cell(((1, 0), (-1, 2))).hilbert_basis()

    assert basis.cardinality() == 3
    assert first + second in basis


def test_the_rays_of_a_quadrant_in_the_hyperbolic_plane_are_ideal() -> None:
    plane = Lattices(ZZ)("U")
    first, second = plane.module_generators()
    quadrant = plane.reduction_cell(((1, 0), (0, 1)))

    assert first in quadrant.ideal_rays()
    assert second in quadrant.ideal_rays()
    assert not (first in quadrant.timelike_rays())
    assert quadrant.lies_in_closed_positive_cone(first + second)


def test_a_quadrant_with_one_timelike_ray() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -1]])
    timelike, spacelike = lattice.module_generators()
    quadrant = lattice.reduction_cell(((1, 0), (0, 1)))

    assert timelike in quadrant.timelike_rays()
    assert not (spacelike in quadrant.timelike_rays())
    assert not (timelike in quadrant.ideal_rays())


def test_the_lattice_of_rank_three_is_the_standard_cubic_lattice() -> None:
    cubic = Lattices(ZZ)(3)

    assert cubic.determinant() == 1
    assert cubic.is_positive_definite()
    assert cubic.is_isometric(Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
