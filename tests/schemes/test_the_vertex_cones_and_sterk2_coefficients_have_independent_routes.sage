r"""The vertex cones and the Sterk2 coefficients, each by a route the library does not take.

Cox--Little--Schenck, *Toric Varieties*, Def. 2.3.2: the normal cone of a face is
spanned by the inner normals of the facets containing it, and the inner normal of
a facet is the primitive lattice vector minimized on that facet.  For a vertex of
a full-dimensional polytope the facets through it are the edges through it, so
the cone is decided by the polytope's own pairings alone.  This file enumerates
those normals from the pairing and asks the vertex operation for the cone, which
is a different route from reading the fan.

The Sterk2 coefficients are recomputed from the plotting source's own rule --
`M_18_0_0` -- in code that does not read the library's weight table, and the
boundary walk is re-run from the boundary directions alone, so the two surgery
directions are shown not to be steps of the path.
"""

import pytest

from sage_extensions.all import *


def _plane_lattice():
    return ZZ.free_module(2)


def _sterk2_source_coefficient_parts(lengths):
    r"""`M_18_0_0` applied to `lengths`, one `(label, numerator, denominator)` per direction.

    The source's rule: the coefficient of `v_2, v_6, v_8, v_10, v_12, v_14, v_18`
    is the length of the same index, that of `v_3, v_5, v_7, v_9, v_11, v_13,
    v_15, v_17` is half of it, that of `v_4` is `l_4 + l_1/2` and that of `v_16`
    is `l_16 + l_19/2`, and the two surgery directions carry `l_1/2` and
    `l_19/2`.  Each coefficient is written as a numerator over a denominator so
    that the comparison needs no arithmetic in the session's fraction field.
    """
    plain = ("v_2", "v_6", "v_8", "v_10", "v_12", "v_14", "v_18")
    halved = ("v_3", "v_5", "v_7", "v_9", "v_11", "v_13", "v_15", "v_17")
    result = []
    for index in range(1, 20):
        label = f"v_{index}"
        length = lengths[index - 1]
        if label in plain:
            numerator, denominator = length, 1
        elif label in halved or label in ("v_1", "v_19"):
            numerator, denominator = length, 2
        elif label == "v_4":
            numerator, denominator = 2 * length + lengths[0], 2
        elif label == "v_16":
            numerator, denominator = 2 * length + lengths[18], 2
        result.append((label, numerator, denominator))
    return tuple(result)


def test_the_vertex_cone_rays_are_the_inner_normals_the_pairing_finds() -> None:
    r"""`conv{(0,0),(2,0),(0,1)}`: two smooth vertex cones and one of index two.

    The three inner normals are `(1,0)`, `(0,1)` and `(-1,-2)`: the cone at
    `(0,0)` is spanned by the first two, and the cones at `(2,0)` and `(0,1)`
    each carry `(-1,-2)` with one of them.
    """
    lattice = _plane_lattice()
    polygon = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 1)))
    variety = polygon.toric_variety(QQ)
    cocharacters = variety.fan().cocharacter_lattice()
    assert cocharacters == lattice.dual_module()
    first, second = tuple(cocharacters.module_generating_set())

    def normal(a, b):
        return cocharacters.linear_combination({first: ZZ(a), second: ZZ(b)})

    vertices = tuple(polygon.vertices())
    # A normal whose coordinates are at most three in modulus is primitive
    # exactly when it is neither twice a normal nor three times one.
    candidates = tuple(
        normal(a, b)
        for a in range(-3, 4)
        for b in range(-3, 4)
        if (a, b) != (0, 0)
        and (a % 2, b % 2) != (0, 0)
        and (a % 3, b % 3) != (0, 0)
    )
    cover = variety.affine_cover()
    known = (
        (lattice((0, 0)), (normal(1, 0), normal(0, 1))),
        (lattice((2, 0)), (normal(0, 1), normal(-1, -2))),
        (lattice((0, 1)), (normal(1, 0), normal(-1, -2))),
    )
    for vertex, expected in known:
        # A primitive normal is the inner normal of a facet exactly when its
        # minimum over the vertices is attained on that facet's two vertices.
        supporting = []
        for candidate in candidates:
            values = tuple(polygon.normal_value(candidate, other) for other in vertices)
            smallest = min(values)
            if values.count(smallest) == 2 and any(
                other == vertex and value == smallest
                for other, value in zip(vertices, values, strict=True)
            ):
                supporting.append(candidate)
        cone = variety.vertex_normal_cone(vertex)
        rays = tuple(cone.rays())
        assert cone.rays().cardinality() == 2
        assert all(any(candidate == ray for ray in rays) for candidate in supporting)
        assert all(any(ray == candidate for candidate in supporting) for ray in rays)
        assert all(
            any(candidate == known_normal for known_normal in expected)
            for candidate in supporting
        )
        assert all(
            any(known_normal == candidate for candidate in supporting)
            for known_normal in expected
        )
        assert cone.dimension() == variety.dimension()
        assert cover.enumeration()(cone) is variety.vertex_chart(vertex)
    assert variety.vertex_normal_cone(lattice((0, 0))).is_smooth()
    assert variety.vertex_normal_cone(lattice((2, 0))).is_smooth()
    assert not variety.vertex_normal_cone(lattice((0, 1))).is_smooth()

    # The cone is asked at a vertex of the retained polytope: the midpoint of
    # the closing edge is a point of the polygon and is not one of its vertices.
    with pytest.raises(AssertionError):
        variety.vertex_normal_cone(lattice((1, 0)))
    # And it is asked of a variety built from a polytope: the same fan built
    # without one retains no polytope, so it has no vertex cones of its own.
    fan_variety = variety.fan().toric_variety(QQ)
    assert not fan_variety.is_polarized()
    with pytest.raises(AssertionError):
        fan_variety.vertex_normal_cone(lattice((0, 0)))


def test_every_sterk2_direction_carries_the_coefficient_the_source_gives_it() -> None:
    r"""All nineteen coefficients, the two roles, and the boundary walk."""
    lengths = Sterk.sterk2_stored_lengths()
    produced = Sterk.sterk2_direction_coefficients(lengths)
    for label, numerator, denominator in _sterk2_source_coefficient_parts(lengths):
        assert produced[label] * denominator == numerator

    unit = (1,) * 19
    at_unit = Sterk.sterk2_direction_coefficients(unit)
    for label, numerator, denominator in _sterk2_source_coefficient_parts(unit):
        assert at_unit[label] * denominator == numerator
    # At unit lengths the half weights are visible as halves.
    assert at_unit["v_1"] * 2 == 1
    assert at_unit["v_19"] * 2 == 1
    assert at_unit["v_3"] * 2 == 1
    assert at_unit["v_16"] * 2 == 3

    boundary = Sterk.sterk2_boundary_directions()
    surgery = Sterk.sterk2_surgery_directions()
    assert all(label not in boundary for label in surgery)
    assert surgery["v_1"] == boundary["v_6"] == (-1, 2)

    path = Sterk.sterk2_boundary_path(lengths)
    reached = (0, 0)
    for label, direction in boundary.items():
        coefficient = produced[label]
        reached = (
            reached[0] + coefficient * direction[0],
            reached[1] + coefficient * direction[1],
        )
    assert reached == path["p_17"]
    assert tuple(path) == tuple(f"p_{step}" for step in range(18))
    assert path["p_0"] == (0, 0) and path["p_17"] == (-24, 0)
    assert path["p_8"] == path["p_9"] == (-12, 26)

    polygon = Sterk.sterk2_polygon(_plane_lattice(), lengths)
    assert polygon.is_lattice_polytope()
    assert polygon.n_vertices() == 17
    assert polygon.normalized_volume() == 820
    points = tuple(path.values())
    closed = points + points[:1]
    doubled_area = 0
    for first_point, second_point in zip(closed, closed[1:], strict=False):
        doubled_area += first_point[0] * second_point[1] - second_point[0] * first_point[1]
    assert doubled_area == 820
    assert _plane_lattice()((0, 0)) in polygon.vertices()
    assert _plane_lattice()((-24, 0)) in polygon.vertices()
