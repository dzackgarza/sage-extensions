r"""A cusp of a subgroup names its plane by the plane's span, and its relation is exact.

The cusp row of a kernel of the discriminant character holds one plane an orbit,
and a plane is a constructed parent.  What a cusp keeps is therefore the span of
its representative -- the exact name of the sublattice -- and the plane is built
from that span when a reader asks for it.  The relation between the rows is the
incidence of the quotient building: a certificate's line lies in its plane, and
each of its two transporters carries the term to the representative of its cusp.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_cusp_of_a_null_plane_builds_its_plane_from_its_span() -> None:
    r"""Two plane cusps of one span each, and three line cusps, on \(U \oplus U(2) \oplus \langle -2 \rangle\).

    The lattice has signature \((2,3)\), and the discriminant character cuts
    \(O(L)\) down to a subgroup whose plane row splits the one \(O(L)\)-orbit of
    isotropic planes into two orbits and whose line row splits the line orbit
    into three.  A cusp named by a span answers what it names without a
    transporter search, and the plane it builds is the same sublattice.
    """
    lattice = (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U").twist(2)
        + Lattices(ZZ)([[-2]])
    )
    subgroup = lattice.stable_orthogonal_group()
    line_cusps = subgroup.cusps(1)
    plane_cusps = subgroup.cusps(2)

    assert line_cusps.cardinality() == cardinal(3)
    assert plane_cusps.cardinality() == cardinal(2)
    for cusp in plane_cusps:
        first = cusp.representative()
        second = cusp.representative()
        assert first.module_rank() == 2
        assert first.is_primitive()
        assert first.is_totally_isotropic()
        assert second.is_primitive()
        assert second.is_totally_isotropic()
        assert first in cusp
        assert second in cusp
    plane_spans = tuple(cusp.span() for cusp in plane_cusps)
    assert plane_spans[0] != plane_spans[1]
    for cusp in line_cusps:
        representative = cusp.representative()
        assert representative.module_rank() == 1
        assert representative.is_totally_isotropic()


def test_each_incidence_certificate_carries_its_terms_to_its_cusps() -> None:
    r"""A certificate's line lies in its plane, and each transporter reaches its cusp.

    An incidence of the quotient building is a pair of orbits, one of lines and
    one of planes, witnessed by a flag.  The line is contained in the plane, so
    its inclusion factors through the plane's, and the certificate's own
    transporters are elements carrying the terms to the cusp representatives.
    """
    lattice = (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U").twist(2)
        + Lattices(ZZ)([[-2]])
    )
    subgroup = lattice.stable_orthogonal_group()

    for certificate in subgroup.tits_building_incidence():
        line = certificate.line()
        plane = certificate.plane()
        factored = line.inclusion().factor_through(plane.inclusion())
        for generator in line.module_generators():
            assert plane.inclusion()(factored(generator)) == line.inclusion()(generator)
        assert (
            certificate.line_transporter().transport_isotropic_object(line)
            in certificate.line_cusp()
        )
        assert (
            certificate.plane_transporter().transport_isotropic_object(plane)
            in certificate.plane_cusp()
        )
