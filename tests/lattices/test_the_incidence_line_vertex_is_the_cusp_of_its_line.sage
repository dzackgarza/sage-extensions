r"""The line vertex of an incidence edge is the one cusp that contains the edge's line.

An edge of the building is a pair of cusp orbits, a line's and a plane's, and
the line term of its flag certificate is a line of the plane.  A row records,
per cusp, the divided class pair of its own representative's generator; for a
subgroup whose finite image is trivial that pair is an invariant of the cusp,
and the row's pairs are distinct, so a line's pair names its cusp.

The statement asserted here does not mention that pair: of the row's cusps
exactly one contains the edge's line, and it is the cusp the edge names, and
the same holds for the plane.  A vertex read off any invariant has to give
that, so an answer naming another cusp fails here.

The specimen is ``U + U(2) + <-2>``, whose kernel rows split the ambient rows
into three line cusps and two plane cusps of their own and have four edges
each.  No lattice-database card holds this row, so the numbers are computed
here.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2():
    r"""``U + U(2) + <-2>``: the smallest specimen whose kernel rows split off their own cusps."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
    )


def _kernel_rows(lattice):
    r"""``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, built as the driver builds them."""
    stable = lattice.stable_orthogonal_group()
    return (stable, stable.intersection(lattice.O_plus()))


def _contained(line, plane) -> bool:
    r"""Whether the retained generator of the line term lies in the plane term."""
    inclusion = line.inclusion()
    domain = inclusion.domain()
    label = next(iter(domain.module_generating_set()))
    return bool(plane.inclusion().is_in_image(inclusion(domain.module_generator(label))))


def _only_cusp_containing(cusps, term):
    r"""The one cusp of the row that contains ``term``, by the cusp's own witness.

    Every primitive isotropic subobject of the row's rank lies in exactly one
    cusp of the row: the cusps are its orbits.  So the tuple of containing
    cusps has one term, and which one it is is the statement.
    """
    return tuple(cusp for cusp in cusps if cusp.transporter_witness(term) is not None)


def test_a_kernel_row_incidence_names_its_line_and_plane_vertices() -> None:
    r"""Four edges over three line and two plane cusps, each edge naming the cusps that contain its terms."""
    lattice = _u_u2_m2()
    assert lattice.discriminant_group().orthogonal_group().cardinality() == cardinal(2)
    for subgroup in _kernel_rows(lattice):
        row = subgroup.tits_building_incidence()
        assert row.cardinality() == cardinal(4)
        assert subgroup.cusps(1).cardinality() == cardinal(3)
        assert subgroup.cusps(2).cardinality() == cardinal(2)
        lines = tuple(subgroup.cusps(1))
        planes = tuple(subgroup.cusps(2))
        line_vertices = set()
        plane_vertices = set()
        for incidence in tuple(row):
            assert incidence.line_cusp() in lines
            assert incidence.plane_cusp() in planes
            assert _contained(incidence.line(), incidence.plane())
            witness = incidence.plane_transporter() * ~incidence.line_transporter()
            assert witness in subgroup
            assert _contained(
                witness.transport_isotropic_object(incidence.line_cusp().representative()),
                incidence.plane_cusp().representative(),
            )
            assert _only_cusp_containing(lines, incidence.line()) == (
                incidence.line_cusp(),
            )
            assert _only_cusp_containing(planes, incidence.plane()) == (
                incidence.plane_cusp(),
            )
            line_vertices.add(incidence.line_cusp())
            plane_vertices.add(incidence.plane_cusp())
        for cusp in lines:
            assert cusp in line_vertices
        for cusp in planes:
            assert cusp in plane_vertices
