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


def test_a_plane_cusp_answers_the_lift_its_row_registered_for_it() -> None:
    r"""The registry is keyed by the span, and a cusp holds that span.

    A plane row registers one lift per plane, keyed by the plane's span
    (:meth:`...OrthogonalCharacterQuotient.register_isotropic_lift`), and a cusp
    of the row keeps the representative's span and nothing else.  So the lift a
    cusp names is the registry's answer to the span the cusp holds, and asking
    the same registry with the plane rebuilt from that span is asking the same
    question: the two reads are one datum, the lift and the finite element it
    acts on the discriminant group by.

    The lattice is \\(U \\oplus U(2) \\oplus \\langle -2 \\rangle\\), whose
    \\(\\tilde O\\) row splits the one \\(O(L)\\)-orbit of primitive isotropic
    planes into two, so the statement is asked of two cusps and not of one.

    What the relation transports with that datum is stated too: the composite
    \\(s_2 s_1^{-1}\\) of two planes' registered lifts carries the first plane
    onto the second, which is the move the incidence carries a covering's line
    classes by.
    """
    lattice = (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U").twist(2)
        + Lattices(ZZ)([[-2]])
    )
    subgroup = lattice.stable_orthogonal_group()
    quotient = subgroup.finite_character_quotient()
    plane_cusps = subgroup.cusps(2)
    assert plane_cusps.cardinality() == cardinal(2)

    registered = []
    for cusp in plane_cusps:
        by_plane = quotient.registered_isotropic_lift(cusp.representative())
        lift, finite_element = by_plane
        # The lift is an isometry of the row's lattice, and the finite element
        # beside it is its own character image: the two halves of one datum.
        assert lift.domain() is lattice
        assert lift.codomain() is lattice
        assert quotient.image(lift)["discriminant"] == finite_element
        assert cusp.representative().module_rank() == 2
        registered.append((cusp, lift))

    first_cusp, first_lift = registered[0]
    second_cusp, second_lift = registered[1]
    move = second_lift * ~first_lift
    assert move.transport_isotropic_object(first_cusp.representative()) in second_cusp
