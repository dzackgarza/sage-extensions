r"""A carried line is read and released, so the row retains its coverings and not its planes (#381).

The incidence covers the ``Stab_Gamma(P)``-orbits of the lines of a plane ``P``
by the plane's own parabolic, reduced to the finite character image (D. Dutour
Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  Where the
subgroup is invariant under conjugation by an ambient isometry, one covering is
the covering of every plane, carried there by the composite of the two planes'
registered lifts, and the row computes it once
(``test_a_row_computes_one_plane_covering``).

A carried line's transport datum is a datum of *that plane's* edges and of
nothing else: the isometry that placed the line is read while the plane's edge
certificates are made, and the certificate retains its own transporter.  A row
that kept the datum beside the line would retain one isometry, one subobject and
one span key for every line of every plane -- on ``T_Co`` three data for each of
189720 planes, on top of the relation the call returns -- which is state the row
never reads again.  So the quotient retains the transport data of the coverings
it computed (they are the chain every carried line is read from) and releases
the carried lines' own.

This file asserts that on the two kernel rows of ``U + U(2) + <-2>``, whose two
plane cusps and two ambient flag orbits make "the covering's lines" and "the
carried lines" different sets -- two and four.  What is asserted, for both of
the lattice's kernel rows:

* a line of an edge standing over a plane that computed no covering keeps no
  transport datum;
* the edges that keep one are at most as many as the flags of the retained
  coverings, which is a number the row's coverings supply and the plane count
  does not enter.

Neither kernel row of ``U + U(2) + <-2>`` has a lattice-database card
(lattice-database#13), and nothing here reads a count off one: the two plane
cusps, the two ambient flag orbits and the four edges are the row's own, and the
premises are asserted rather than typed.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u_m2():
    r"""``U + U(2) + <-2>``: rank five, ``|A_L| = 2``, so neither kernel row is the ambient one."""
    return Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])


def _count(things) -> cardinal:
    r"""The cardinality of a finite family, read without assuming a length."""
    return cardinal(sum(1 for _ in things))


def _covering_cusps(quotient, source_row, plane_cusps):
    r"""The plane cusps whose planes computed a covering, one plane per source family."""
    covering_planes = [
        record[0]
        for record in (
            quotient.isotropic_covering_reference(source)
            for source in range(int(_count(source_row)))
        )
        if record is not None
    ]
    return tuple(
        cusp
        for cusp in plane_cusps
        if any(cusp.representative() is plane for plane in covering_planes)
    )


def _assert_no_carried_line_is_retained(subgroup) -> None:
    r"""Assert that ``subgroup``'s incidence retains no transport of a carried line."""
    plane_cusps = tuple(subgroup.cusps(2))
    subgroup.cusps(1)
    source_row = tuple(subgroup.supergroup().isotropic_orbit_representatives(2, flag=True))
    incidences = tuple(subgroup.tits_building_incidence())
    quotient = subgroup.finite_character_quotient()
    covering_cusps = _covering_cusps(quotient, source_row, plane_cusps)
    # The premises: the row carries its covering to planes that computed none, so
    # "the covering's lines" and "the carried lines" are different sets.
    assert _count(plane_cusps) > _count(covering_cusps)
    assert _count(covering_cusps) > cardinal(0)
    covering_flags = cardinal(
        sum(
            sum(1 for _ in quotient.isotropic_covering_reference(source)[2])
            for source in range(int(_count(source_row)))
        )
    )
    kept = [
        incidence
        for incidence in incidences
        if quotient.isotropic_transport_of(incidence.line()) is not None
    ]
    carried = [
        incidence
        for incidence in kept
        if not any(cusp is incidence.plane_cusp() for cusp in covering_cusps)
    ]
    assert carried == [], (
        f"{_count(carried)} of the {_count(incidences)} edges of {subgroup} stand over a plane "
        f"that computed no covering and keep the transport datum of their line: the row retains "
        f"one datum per carried line instead of releasing it once its plane's certificates exist"
    )
    assert _count(kept) <= covering_flags


def test_the_otilde_row_retains_only_its_coverings() -> None:
    r"""``Otilde`` on ``U + U(2) + <-2>``: the carried plane's lines keep no datum."""
    _assert_no_carried_line_is_retained(_u_u_m2().stable_orthogonal_group())


def test_the_otilde_plus_row_retains_only_its_coverings() -> None:
    r"""``Otilde+`` on ``U + U(2) + <-2>``: the carried plane's lines keep no datum."""
    lattice = _u_u_m2()
    stable = lattice.stable_orthogonal_group()
    _assert_no_carried_line_is_retained(stable.intersection(lattice.O_plus()))
