r"""The divided-class relation is decided one plane at a time, and a plane's lift is spent by its edges (#381).

A kernel plane row of ``T_Co`` is 189720 planes and the split that produces them
registers a lift a plane: that registry is the row's largest per-plane term.  So
the relation is asked for a plane at a time (``divided_class_incidence_of_planes``),
and a caller streaming a walk's planes hands that call the walk itself: the
covering is seeded at the first plane the call reaches, the plane's edges are
decided there, and the plane's lift is released on the way past the yield.

**What is asserted.**  On ``U + U(2) + <-2>``, whose kernel rows this gate can
afford:

* the call yields the row's own plane cusps, one for each cusp of the row;
* every edge it yields at a plane names that plane, no two edges share both
  vertices, and every line cusp of the row is the vertex of some edge;
* a plane's registered lift is no longer registered once that plane's edges are
  yielded, and the planes after it still decide theirs -- which is what lets a
  row release as it walks instead of holding every lift it walked;
* the whole relation, which is this call composed over the subgroup's own cusps,
  returns as many edges as the streamed planes do.

The counts are the specimen's recorded value -- four edges over three line cusps
and two plane cusps -- and each is reached by its own route over the row.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2():
    r"""``U + U(2) + <-2>``: rank five, and its kernel rows have three line cusps."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
    )


def _u2_u_m2():
    r"""The same lattice presented the other way round: ``U(2) + U + <-2>``."""
    return (
        Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)("U")
        + Lattices(ZZ)(((-2,),))
    )


def _kernel_rows(lattice):
    r"""``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, built as the drivers build them."""
    stable = lattice.stable_orthogonal_group()
    return (stable, stable.intersection(lattice.O_plus()))


def _span_rows(cusp):
    r"""The rows of the span a cusp is named by: the cusp's own canonical name."""
    return cusp.span()[1]


def _assert_the_row_is_decided_one_plane_at_a_time(subgroup) -> None:
    r"""The streamed planes are the row's, each plane's edges name it, and its lift is spent."""
    quotient = subgroup.finite_character_quotient()
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    line_spans = tuple(_span_rows(cusp) for cusp in lines)
    planes_decided = 0
    edges_decided = 0
    endpoints = {}
    line_vertices = {}
    for cusp, edges in subgroup.divided_class_incidence_of_planes(planes):
        assert cusp in planes
        planes_decided += 1
        # The plane is spent by its own edges: the registry no longer answers for
        # its span, and the planes after it are decided without it.
        assert quotient.registered_isotropic_discriminant_of_span(cusp.span()) is None
        for incidence in edges:
            assert incidence.plane_cusp() is cusp
            assert _span_rows(incidence.plane_cusp()) == _span_rows(cusp)
            assert _span_rows(incidence.line_cusp()) in line_spans
            edges_decided += 1
            endpoints[(_span_rows(incidence.line_cusp()), _span_rows(incidence.plane_cusp()))] = True
            line_vertices[_span_rows(incidence.line_cusp())] = True
    distinct_endpoints = 0
    for _pair in endpoints:
        distinct_endpoints += 1
    distinct_lines = 0
    for _vertex in line_vertices:
        distinct_lines += 1
    assert cardinal(planes_decided) == cardinal(2)
    assert cardinal(edges_decided) == cardinal(4)
    assert cardinal(distinct_endpoints) == cardinal(4)
    assert cardinal(distinct_lines) == cardinal(3)
    assert subgroup.cusps(1).cardinality() == cardinal(3)
    assert subgroup.cusps(2).cardinality() == cardinal(2)


def test_the_otilde_row_of_u_u2_m2_is_decided_one_plane_at_a_time() -> None:
    r"""``ker rho`` on ``U + U(2) + <-2>``: four edges, decided plane by plane."""
    _assert_the_row_is_decided_one_plane_at_a_time(_kernel_rows(_u_u2_m2())[0])


def test_the_otilde_plus_row_of_u_u2_m2_is_decided_one_plane_at_a_time() -> None:
    r"""``ker(rho, sn_RR)`` on the same specimen: the finer group's row holds too."""
    _assert_the_row_is_decided_one_plane_at_a_time(_kernel_rows(_u_u2_m2())[1])


def test_the_whole_relation_is_the_composition_of_the_planes() -> None:
    r"""A row composed from its cusps and a row streamed plane by plane agree.

    The relation spends the row's registered lifts -- that is what makes it
    streamable -- so the two routes are taken on the other presentation of the
    lattice, whose rows are still registered: the two numbers are then one
    relation read by two routes, and not one route read twice.
    """
    composed = _kernel_rows(_u2_u_m2())[0].tits_building_incidence_by_divided_classes()
    streamed = 0
    finer = _kernel_rows(_u2_u_m2())[1]
    for _cusp, edges in finer.divided_class_incidence_of_planes(tuple(finer.cusps(2))):
        for _incidence in edges:
            streamed += 1
    assert composed.cardinality() == cardinal(streamed)
    assert composed.cardinality() == cardinal(4)
