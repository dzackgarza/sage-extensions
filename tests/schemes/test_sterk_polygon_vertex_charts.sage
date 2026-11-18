r"""A selected polygon vertex, its normal cone and the affine chart of that cone.

Cox--Little--Schenck, *Toric Varieties*: a polytope's normal fan is the fan of
the normal cones of its faces, and the cone of a vertex is spanned by the inner
normals of the facets through it (Def. 2.3.2), the affine chart of a cone is
``Spec k[sigma-dual cap M]`` (Prop. 1.3.9), and the charts of the maximal cones
are the atlas (Thm. 3.1.5).  A vertex of a full-dimensional polytope therefore
indexes one chart of the atlas, and the small triangle and the stored Sterk2
polygon below are asked for it.
"""

from sage_extensions.all import *


def _plane_lattice():
    return ZZ.free_module(2)


def _character_monomial(cone, chart, character):
    r"""The monomial ``chi^m`` of one character in the chart's coordinate algebra.

    The cone states the character's nonnegative expansion over its Hilbert
    generators, and the chart's algebra has one generator per Hilbert generator.
    """
    algebra = chart.coordinate_algebra()
    labels = tuple(algebra.algebra_generating_set())
    exponents = tuple(int(value) for value in cone.semigroup_coefficients(character))
    monomial = algebra.one()
    for label, exponent in zip(labels, exponents, strict=True):
        if exponent:
            monomial *= algebra.algebra_generator(label) ** exponent
    return monomial


def test_the_vertex_cones_of_a_triangle_index_charts_of_its_atlas() -> None:
    r"""``conv{(0,0),(2,0),(0,1)}``: a smooth quadrant at ``(0,0)`` and an
    index-two cone at ``(0,1)``, whose chart is the quadric cone."""
    lattice = _plane_lattice()
    polygon = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 1)))
    variety = polygon.toric_variety(QQ)
    cocharacters = variety.fan().cocharacter_lattice()
    first, second = tuple(cocharacters.module_generating_set())
    horizontal = cocharacters.linear_combination({first: ZZ(1)})
    vertical = cocharacters.linear_combination({second: ZZ(1)})
    inner = cocharacters.linear_combination({first: ZZ(-1), second: ZZ(-2)})

    # The normal fan lives in the dual of the lattice the polygon lives in.
    assert cocharacters == lattice.dual_module()

    origin = lattice((0, 0))
    opposite = lattice((0, 1))
    corner = lattice((2, 0))
    smooth = variety.vertex_normal_cone(origin)
    singular = variety.vertex_normal_cone(opposite)
    other = variety.vertex_normal_cone(corner)

    # The facets through (0,0) are x >= 0 and y >= 0, whose inner normals are
    # the two coordinate vectors, so that cone is the smooth quadrant.
    assert smooth.dimension() == variety.dimension()
    assert smooth.rays().cardinality() == 2
    assert smooth.is_smooth()
    assert smooth.contains(horizontal) and smooth.contains(vertical)
    assert all(
        polygon.normal_supports_point(normal, origin) for normal in tuple(smooth.rays())
    )
    assert all(normal.parent() is cocharacters for normal in tuple(smooth.rays()))

    # The facets through (0,1) are x >= 0 and x + 2y <= 2, whose inner normals
    # span a cone of lattice index two.
    assert singular.dimension() == variety.dimension()
    assert singular.rays().cardinality() == 2
    assert not singular.is_smooth()
    assert singular.contains(horizontal) and singular.contains(inner)
    assert all(
        polygon.normal_supports_point(normal, opposite) for normal in tuple(singular.rays())
    )
    assert all(normal.parent() is cocharacters for normal in tuple(singular.rays()))
    assert all(
        polygon.normal_supports_point(normal, corner) for normal in tuple(other.rays())
    )
    assert smooth != singular and singular != other and smooth != other

    # The chart of the smooth vertex is the affine plane.
    plane_chart = variety.vertex_chart(origin)
    plane_algebra = plane_chart.coordinate_algebra()
    assert plane_chart in AffineSchemes(QQ)
    assert plane_algebra in SymmetricAlgebras(QQ)
    assert plane_algebra.algebra_generating_set().cardinality() == 2

    # The dual Hilbert basis of the index-two cone is (0,-1), (1,-1), (2,-1) in
    # the ray basis, and (0,-1) + (2,-1) = 2*(1,-1): the chart is the quadric
    # cone z0*z2 = z1^2, not a polynomial ring.
    characters = singular.character_lattice()
    ray_one, ray_two = tuple(characters.module_generating_set())
    lower = characters.linear_combination({ray_two: ZZ(-1)})
    middle = characters.linear_combination({ray_one: ZZ(1), ray_two: ZZ(-1)})
    upper = characters.linear_combination({ray_one: ZZ(2), ray_two: ZZ(-1)})
    hilbert = tuple(singular.semigroup_generators())
    assert all(singular.dual_cone_contains(character) for character in (lower, middle, upper))
    assert all(any(character == generator for generator in hilbert) for character in (lower, middle, upper))
    assert singular.semigroup_generators().cardinality() == 3
    assert lower + upper == 2 * middle

    singular_chart = variety.vertex_chart(opposite)
    singular_algebra = singular_chart.coordinate_algebra()
    assert singular_algebra.algebra_generating_set().cardinality() == 3
    assert singular_algebra not in SymmetricAlgebras(QQ)
    monomials = tuple(
        _character_monomial(singular, singular_chart, character)
        for character in (lower, middle, upper)
    )
    lower_monomial, middle_monomial, upper_monomial = monomials
    assert lower_monomial * upper_monomial == middle_monomial ** 2
    assert lower_monomial != middle_monomial

    # The chart of a vertex is the atlas entry at that vertex's cone.
    cover = variety.affine_cover()
    for vertex in (origin, opposite, corner):
        cone = variety.vertex_normal_cone(vertex)
        chart = variety.vertex_chart(vertex)
        assert cover.enumeration()(cone) is chart
        assert cover.enumeration_inverse()(chart) == cone


def test_a_stored_sterk2_polygon_vertex_indexes_its_chart() -> None:
    r"""The stored Sterk2 specimen's polygon, from its own lengths, and the chart
    of its apex ``p_8 = p_9 = (-12,26)``."""
    lengths = Sterk.sterk2_stored_lengths()
    coefficients = Sterk.sterk2_direction_coefficients(lengths)
    path = Sterk.sterk2_boundary_path(lengths)

    # The source's half weights, its two l_1/2 and l_19/2 offsets, and the two
    # surgery directions, which are not boundary-path steps.
    assert coefficients["v_4"] == lengths[3] + coefficients["v_1"]
    assert coefficients["v_16"] == lengths[15] + coefficients["v_19"]
    assert coefficients["v_3"] + coefficients["v_3"] == lengths[2]
    assert coefficients["v_6"] == lengths[5]
    assert coefficients["v_10"] == lengths[9]
    assert Sterk.sterk2_surgery_directions()["v_19"] == (1, 2)
    assert Sterk.sterk2_surgery_directions()["v_1"] == (-1, 2)

    # The path runs from the origin to (-24,0), and its zero tenth step repeats
    # a point; the hull closes the path with the side back to the origin.
    assert path["p_0"] == (0, 0)
    assert path["p_17"] == (-24, 0)
    assert path["p_8"] == path["p_9"] == (-12, 26)

    lattice = _plane_lattice()
    polygon = Sterk.sterk2_polygon(lattice, lengths)
    assert polygon.is_lattice_polytope()
    assert polygon.dimension() == 2
    assert polygon.normalized_volume() == 820

    # The path has eighteen labelled points and the hull seventeen vertices: the
    # repeated point is one point of the path that is not a vertex of its own,
    # so the hull, not the path, decides which points index charts.
    assert tuple(path) == tuple(f"p_{step}" for step in range(18))
    assert polygon.n_vertices() == 17

    end = lattice((-24, 0))
    apex = lattice((-12, 26))
    assert end in polygon.vertices()
    assert apex in polygon.vertices()

    variety = polygon.toric_variety(QQ)
    cocharacters = variety.fan().cocharacter_lattice()
    assert cocharacters == lattice.dual_module()

    end_cone = variety.vertex_normal_cone(end)
    assert end_cone.is_smooth()
    assert all(
        polygon.normal_supports_point(normal, end) for normal in tuple(end_cone.rays())
    )
    assert variety.vertex_chart(end).coordinate_algebra() in SymmetricAlgebras(QQ)

    apex_cone = variety.vertex_normal_cone(apex)
    assert not apex_cone.is_smooth()
    assert apex_cone.dimension() == variety.dimension()
    assert apex_cone.rays().cardinality() == 2
    assert all(
        polygon.normal_supports_point(normal, apex) for normal in tuple(apex_cone.rays())
    )
    assert all(normal.parent() is cocharacters for normal in tuple(apex_cone.rays()))
    apex_chart = variety.vertex_chart(apex)
    assert apex_chart in AffineSchemes(QQ)
    assert apex_chart.coordinate_algebra() not in SymmetricAlgebras(QQ)
    assert apex_chart.coordinate_algebra().algebra_generating_set().cardinality() == 5

    # The chart of a vertex is the atlas entry at that vertex's cone, on this
    # variety too: the cone the supporting normals span is a cone of this
    # variety's fan and its chart is the chart the atlas enumerates there.
    cover = variety.affine_cover()
    for vertex, cone in ((end, end_cone), (apex, apex_cone)):
        chart = variety.vertex_chart(vertex)
        assert cone in variety.fan()
        assert cover.enumeration()(cone) is chart
        assert cover.enumeration_inverse()(chart) == cone
