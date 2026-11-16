r"""A line vertex of the building incidence is named by the finite image (#381).

The incidence of a subgroup ``Gamma`` of ``O(L)`` joins a line cusp to a plane
cusp when one element of ``Gamma`` carries a line of the first into a plane of
the second.  The line term of a flag is a line of a plane, which is no chosen
representative of the line row, so its cusp cannot be read off a span.  What
names it is the finite image: for a primitive isotropic line ``x = <v>`` with
divided class ``c = [v / div(v)]`` in ``A_L``, an isometry ``g`` carries
``c`` to the divided class of ``g v``, so a subgroup element carrying one line
onto another maps the class pair ``{c, -c}`` of the first onto that of the
second, and the ``rho(Gamma)``-orbit of the pair is an invariant of the
``Gamma``-orbits of lines: two lines of one orbit share it, and a cusp whose
orbit differs from a line's cannot contain the line.  The cusp rows are exactly
the double cosets the finite image splits the ambient orbit by (D. Dutour
Sikiri\'c and K. Hulek, *Moduli of polarised Enriques surfaces -- computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6,
printed p. 22), so the row's cusps carry pairwise different orbits.

What is asserted, on the specimens the per-test gate can afford:

* the line cusps of a kernel row are pairwise separated by the finite image --
  the row's own reduction, read as a statement about the cusps it returned;
* a line of a plane is separated from every cusp but one, and the cusp it is
  not separated from is the one whose transporter witness carries the line:
  the finite image names the vertex the witness search finds, so an index by it
  loses no line and adds none;
* an edge of the incidence joins a line term to a line cusp its finite image
  does not separate it from.

``Otilde(T_Co) = ker rho`` and ``Otilde+ = ker(rho, sn_RR)`` are the groups
#381 owes the incidence of, whose Coble rows are the dispatched job; on
``U + U(2) + <-2>`` their line rows have three cusps each, and on
``U + U + <-4>`` one, which is the case the key adds nothing to and which is
asserted to agree all the same.  Neither lattice's row is a card value
(lattice-database#13), so nothing here is compared with a printed count.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2():
    r"""``U + U(2) + <-2>``: the kernel rows have three line cusps of their own."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
    )


def _u_u_m4():
    r"""``U + U + <-4>``: the kernel rows have one line cusp of their own."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)(((-4,),))


def _kernel_rows(lattice):
    r"""``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, built as the drivers build them."""
    stable = lattice.stable_orthogonal_group()
    return (stable, stable.intersection(lattice.O_plus()))


def _lines_of_a_plane(lattice, plane):
    r"""Two lines of one plane, taken from the plane's own generators.

    A plane is totally isotropic and primitive, so every primitive vector of it
    spans an isotropic line of the lattice; the generators of the plane and
    their sum are primitive, and the sum is a line that is no generator.
    """
    domain = plane.inclusion().domain()
    labels = tuple(domain.module_generating_set())
    first = plane.inclusion()(domain.module_generator(labels[0]))
    second = plane.inclusion()(domain.module_generator(labels[1]))
    return (
        lattice.primitive_isotropic_subobject(first),
        lattice.primitive_isotropic_subobject(first + second),
    )


def _assert_the_row_is_separated_by_its_image(subgroup) -> None:
    r"""The kernel row's line cusps lie in different orbits of the finite image."""
    quotient = subgroup.finite_character_quotient()
    lines = tuple(subgroup.cusps(1))
    assert lines
    for position, first in enumerate(lines):
        for second in lines[position + 1:]:
            assert quotient.invariant_separates_isotropic_orbits(
                first.representative(), second.representative()
            )


def _assert_a_plane_s_lines_are_named(subgroup) -> None:
    r"""A line of a plane has one cusp its image does not separate it from, and it is the carried one."""
    lattice = subgroup.supergroup().domain()
    quotient = subgroup.finite_character_quotient()
    lines = tuple(subgroup.cusps(1))
    plane = next(iter(subgroup.cusps(2))).representative()
    for line in _lines_of_a_plane(lattice, plane):
        named = [
            cusp
            for cusp in lines
            if not quotient.invariant_separates_isotropic_orbits(
                line, cusp.representative()
            )
        ]
        carried = [
            cusp for cusp in lines if cusp.transporter_witness(line) is not None
        ]
        assert named
        assert named == carried


def test_the_otilde_line_row_of_u_u2_m2_is_separated_by_the_finite_image() -> None:
    r"""``ker rho`` on ``U + U(2) + <-2>``: three line cusps, three finite images."""
    subgroup = _kernel_rows(_u_u2_m2())[0]
    _assert_the_row_is_separated_by_its_image(subgroup)
    _assert_a_plane_s_lines_are_named(subgroup)


def test_the_otilde_plus_line_row_of_u_u2_m2_is_separated_by_the_finite_image() -> None:
    r"""``ker(rho, sn_RR)`` on ``U + U(2) + <-2>``: the finer group's row too."""
    subgroup = _kernel_rows(_u_u2_m2())[1]
    _assert_the_row_is_separated_by_its_image(subgroup)
    _assert_a_plane_s_lines_are_named(subgroup)


def test_the_incidence_line_vertex_of_u_u_m4_lies_in_its_finite_image_orbit() -> None:
    r"""``U + U + <-4>``: each edge's line term shares its vertex's finite image."""
    lattice = _u_u_m4()
    for subgroup in _kernel_rows(lattice):
        quotient = subgroup.finite_character_quotient()
        incidences = tuple(subgroup.tits_building_incidence())
        assert incidences
        for incidence in incidences:
            assert not quotient.invariant_separates_isotropic_orbits(
                incidence.line(), incidence.line_cusp().representative()
            )
