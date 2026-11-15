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


def test_distinct_cones_of_one_shape_hash_apart_and_equal_cones_hash_alike() -> None:
    r"""Three two-dimensional cones on two rays in ``Z^2`` have three hashes; one cone cut out twice has one.

    The quadrant, the cone on ``(0, 1), (2, 1)`` and the cone on ``(1, 1), (1, -1)``
    are distinct sets with the same numbers of rays, facets and dimensions.  The
    quadrant cut out by ``x, y >= 0`` and by ``2x, y >= 0`` is one set.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    quadrant = lattice.reduction_cell(((1, 0), (0, 1)))
    narrow = lattice.reduction_cell(((1, 0), (-1, 2)))
    diagonal = lattice.reduction_cell(((1, 1), (1, -1)))
    doubled = lattice.reduction_cell(((2, 0), (0, 1)))

    assert quadrant != narrow
    assert quadrant != diagonal
    assert narrow != diagonal
    assert cardinal(sum(1 for _ in {hash(quadrant), hash(narrow), hash(diagonal)})) == cardinal(3)
    assert quadrant == doubled
    assert hash(quadrant) == hash(doubled)


def test_three_half_planes_of_one_dimension_and_one_lineality_space_are_three_sets() -> None:
    r"""Three half-planes of one dimension and one lineality dimension are three sets.

    ``y >= 0``, ``y <= x`` and ``x + y <= 0`` each have dimension two and a
    lineality space of dimension one, so the dimension and the lineality
    dimension do not separate them.  They are three sets: the lineality
    lattices they meet are ``<(1, 0)>``, ``<(1, 1)>`` and ``<(1, -1)>``, and
    the cone modulo its lineality space is a ray, on ``(0, 1)`` for
    ``y >= 0`` and on the class of ``(0, -1)`` for ``y <= x`` and for
    ``x + y <= 0``, the latter's extreme ray ``(-1, 0)`` being
    ``(0, -1) - (1, -1)``.
    The half-planes are the sets ``{(x, y) : y >= 0}``,
    ``{(x, y) : y - x <= 0}`` and ``{(x, y) : x + y <= 0}``.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    upper = lattice.reduction_cell(((0, 1),))
    steeper = lattice.reduction_cell(((1, -1),))
    mirror = lattice.reduction_cell(((-1, -1),))

    for cone in (upper, steeper, mirror):
        assert not cone.is_pointed()
        assert cone.dimension() == 2
        assert cone.lineality_generators().cardinality() == 1

    assert upper != steeper
    assert steeper != mirror
    assert cardinal(sum(1 for _ in {hash(upper), hash(steeper), hash(mirror)})) == cardinal(3)


def test_two_half_planes_of_one_lineality_lattice_are_two_sets() -> None:
    r"""``y >= 0`` and ``y <= 0`` meet one lineality lattice and differ on its two sides.

    Each has dimension two and one lineality generator, on ``(1, 0)``, so the
    two cones share their lineality lattice; their extreme rays are ``(0, 1)``
    and ``(0, -1)``, the two images of the plane modulo that line.  The two
    sets are the two sides of the line, and the ray they meet it on is what
    separates them.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    upper = lattice.reduction_cell(((0, 1),))
    lower = lattice.reduction_cell(((0, -1),))

    assert upper.lineality_generators() == lower.lineality_generators()
    assert upper.primitive_rays() != lower.primitive_rays()
    assert upper != lower
    assert hash(upper) != hash(lower)


def test_two_quarter_spaces_of_one_dimension_and_one_lineality_line_are_two_sets() -> None:
    r"""Two quarter-spaces of ``Z^3`` with one lineality line are two sets.

    ``{y >= 0, z >= 0}`` and ``{y <= 0, z >= 0}`` both have dimension three,
    one lineality generator on ``(1, 0, 0)`` and two extreme rays, so neither
    the dimension nor the number of rays separates them.  Their images modulo
    the lineality are the quadrants of the ``(y, z)`` plane cut out by the
    signs ``(+, +)`` and ``(-, +)``.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    upper = lattice.reduction_cell(((0, 1, 0), (0, 0, 1)))
    lower = lattice.reduction_cell(((0, -1, 0), (0, 0, 1)))

    for cone in (upper, lower):
        assert not cone.is_pointed()
        assert cone.dimension() == 3
        assert cone.lineality_generators().cardinality() == 1
        assert cone.primitive_rays().cardinality() == 2

    assert upper.lineality_generators() == lower.lineality_generators()
    assert hash(upper) != hash(lower)


def test_one_cone_with_a_lineality_of_non_unit_pivot_is_one_hash() -> None:
    r"""Two presentations of one 3-dimensional wedge around a line are one cone and one hash.

    The cone ``{<(-1, 3, 0), x> >= 0, <(3, -11, 1), x> >= 0}`` has dimension
    three, the lineality line ``<(3, 1, 2)>``, whose Hermite basis has the
    pivot ``3`` in its first coordinate and so is not a coordinate line, and
    the extreme rays ``(-3, -1, 0)`` and ``(-11, -3, 0)``.  The third covector
    ``(0, -2, 1)`` is ``(3, -11, 1) + 3(-1, 3, 0)``, a positive combination of
    the first two, so it cuts out the same cone.  The private exact polyhedron
    states an extreme ray only up to a lineality vector, and here it states
    ``(-11, -3, 0)`` for the first presentation and ``(-1, 0, 3)`` for the
    second: twice ``(-1, 0, 3)`` is ``(-11, -3, 0) + 3(3, 1, 2)``, so the two
    are one class modulo the lineality up to a positive rational, and one ray
    of the image.  The two presentations are one set and one hash.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    short = lattice.reduction_cell(((-1, 3, 0), (3, -11, 1)))
    longer = lattice.reduction_cell(((-1, 3, 0), (3, -11, 1), (0, -2, 1)))

    assert short == longer
    assert hash(short) == hash(longer)
    assert cardinal(sum(1 for _ in {short, longer})) == cardinal(1)
    assert short.lineality_generators() == longer.lineality_generators()
