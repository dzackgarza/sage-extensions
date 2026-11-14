r"""The quotient building for SO(2U) has one line, two planes and two flags.

The maximal null parabolic has determinant one, so exchanging one
hyperbolic pair splits its O orbit into two SO orbits. The line parabolic
contains the exchange of the other hyperbolic pair, so its O orbit stays
one SO orbit. Each maximal parabolic contains GL2(Z), transitive on
primitive lines in its plane; thus each plane vertex has one incident flag.
"""

from sage_extensions.all import *


def test_special_orthogonal_split_building_retains_exact_flag_incidence_and_transporters():
    hyperbolic = Lattices(ZZ)("U")
    lattice = hyperbolic + hyperbolic
    group = lattice.SO()
    lines, planes = group.cusps(1), group.cusps(2)
    incidences = group.tits_building_incidence()
    assert lines.cardinality() == cardinal(1)
    assert planes.cardinality() == cardinal(2)
    assert incidences.cardinality() == cardinal(2)
    assert all(any(edge.plane_cusp() == plane for edge in incidences) for plane in planes)
    basis = tuple(lattice.module_generators())
    for edge in incidences:
        assert edge.line_cusp() in lines
        assert edge.plane_cusp() in planes
        assert edge.subgroup() is group
        for term, cusp, witness in (
            (edge.line(), edge.line_cusp(), edge.line_transporter()),
            (edge.plane(), edge.plane_cusp(), edge.plane_transporter()),
        ):
            assert witness in group
            representative = cusp.representative()
            assert all(
                representative.inclusion().is_in_image(witness(term.inclusion()(point)))
                for point in term.module_generators()
            )
            assert all(
                term.inclusion().is_in_image((~witness)(representative.inclusion()(point)))
                for point in representative.module_generators()
            )
            assert all((~witness)(witness(point)) == point for point in basis)
            assert all(lattice.b(witness(x), witness(y)) == lattice.b(x, y) for x in basis for y in basis)
