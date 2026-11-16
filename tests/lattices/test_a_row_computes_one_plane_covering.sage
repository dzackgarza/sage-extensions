r"""One plane covering per row, carried to the row's other planes (#381).

A row's incidence covers the ``Stab_Gamma(P)``-orbits of the lines of a plane
``P`` by the plane's own parabolic: the double cosets ``K \ Pi / H``, reduced
to the finite character image (D. Dutour Sikiric and K. Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  That work -- the certified
parabolic family, its image in the character product, the word section and the
double cosets -- is one datum of the *row* and not of the plane.  Where the
subgroup is invariant under conjugation by an ambient isometry, an ambient
isometry carries the subgroup to itself, so the covering of one plane carried
to another by the composite of the two planes' registered lifts *is* the
covering of that other plane: same orbits, same count.  A row therefore
computes it once, and every other plane costs one transport.

This file reads that off ``U + U(2) + <-2>``, whose two kernel rows have two
plane cusps and two ambient flag orbits each, so "once per row" and "once per
plane" are different numbers there -- two and four -- and the difference is
read without a clock.  The registry the covering is retained in is the
quotient's: ``isotropic_covering_of`` answers at the plane the family was
computed at and at no other, and every other plane's family is that one carried
there.

What is asserted, for both kernel rows of that lattice:

* the row retains one covering per ambient flag orbit, so exactly one of its
  plane cusps is the plane that covering was computed at;
* at every plane cusp, the row's edges are the retained covering carried
  there: the line cusps of the edges over that plane are exactly the line
  cusps of the carried family.

Neither kernel row of ``U + U(2) + <-2>`` has a lattice-database card
(lattice-database#13), so no number here is a card value: the two plane cusps,
the two ambient flag orbits and the four edges are the row's own, and the two
premises the counts rest on are asserted rather than typed.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u_m2():
    r"""``U + U(2) + <-2>``: rank five, ``|A_L| = 2``, so neither kernel row is the ambient one."""
    return Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])


def _line_cusp_of(line_cusps, line):
    r"""The line cusp of the row that contains ``line``, read from its own transporter witness."""
    return next(
        cusp for cusp in line_cusps if cusp.transporter_witness(line) is not None
    )


def _retained_covering(quotient, source, plane_cusps):
    r"""The row's one covering of ``source``, at the exactly one plane that computed it."""
    coverings = [
        quotient.isotropic_covering_of(cusp.representative(), source)
        for cusp in plane_cusps
    ]
    # One plane of the row computed this family; the row's other planes are the
    # same family carried there, so they answer for it nowhere.
    assert sum(covering is not None for covering in coverings) == 1
    return next(covering for covering in coverings if covering is not None)


def _assert_one_covering_per_row(subgroup) -> None:
    r"""Assert that ``subgroup``'s incidence computes one covering per row and carries it there."""
    incidences = subgroup.tits_building_incidence()
    quotient = subgroup.finite_character_quotient()
    line_cusps = tuple(subgroup.cusps(1))
    plane_cusps = tuple(subgroup.cusps(2))
    source_row = subgroup.supergroup().isotropic_orbit_representatives(2, flag=True)
    # The premises: two plane cusps and two source families, so a covering
    # computed per plane is four and one computed per row is two.
    assert source_row.cardinality() == cardinal(2)
    assert subgroup.cusps(2).cardinality() == cardinal(2)
    retained = [
        _retained_covering(quotient, source, plane_cusps)
        for source, _flag in enumerate(source_row)
    ]
    for cusp in plane_cusps:
        lift = quotient.isotropic_lift_of(cusp.representative())
        carried = [
            flag
            for reference_lift, reference_flags in retained
            for flag in quotient.transport_covering(reference_lift, reference_flags, lift)
        ]
        assert set(
            incidence.line_cusp()
            for incidence in incidences
            if incidence.plane_cusp() == cusp
        ) == set(_line_cusp_of(line_cusps, flag.terms()[0]) for flag in carried)
    assert incidences.cardinality() == cardinal(4)


def test_the_otilde_row_computes_one_plane_covering() -> None:
    r"""``Otilde`` on ``U + U(2) + <-2>``: one covering per row, carried to the other plane."""
    lattice = _u_u_m2()
    _assert_one_covering_per_row(lattice.stable_orthogonal_group())


def test_the_otilde_plus_row_computes_one_plane_covering() -> None:
    r"""``Otilde+`` on ``U + U(2) + <-2>``: one covering per row, carried to the other plane."""
    lattice = _u_u_m2()
    stable = lattice.stable_orthogonal_group()
    _assert_one_covering_per_row(stable.intersection(lattice.O_plus()))
