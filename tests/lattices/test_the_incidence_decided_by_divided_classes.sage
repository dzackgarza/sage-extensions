r"""The building incidence decided by divided classes, on the lattices the gate can afford (#585).

``tits_building_incidence`` decides an edge of the Tits building's incidence by
carrying a covering of the plane's lines to the plane and reading each carried
line's key in the finite image.  The covering is a flag row, so the carry builds
an ``IsotropicFlag`` per line of every plane, and a constructed parent of this
library is retained for the process: that is the 350-400 KB a plane which the
kernel rows' 189720 planes cannot pay.

``tits_building_incidence_by_divided_classes`` decides the same edges from the
divided classes alone.  For a primitive isotropic line ``x = <v>`` with divided
class ``c = [v / div(v)]`` in ``A_L = L^\#/L``, an isometry ``g`` carries ``c``
to the divided class of ``g v`` -- an isometry preserves primitivity and
divisibility -- so the ``rho(Gamma)``-orbit of the class pair ``{c, -c}`` is an
invariant of the ``Gamma``-orbits of lines, and the class pair of a carried line
is the image of the class pair under the finite image, with no subobject built
(D. Dutour Sikiri\'c and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22,
is the reduction the row is split by).

**What is asserted.**  The relation is not compared with the other route's
implementation: both are compared with the relation the subgroup's *flag row*
states, through the public ``isotropic_orbit_representatives(2, flag=True)``.
A flag's line is carried to exactly one cusp of the line row and its plane to
exactly one cusp of the plane row, by the cusps' own transporter witnesses, so
the flag row is a third computation of the same relation and neither incidence
route can agree with it by sharing code with the other.

* the class route's edges, as pairs of cusp positions, equal the flag row's;
* they equal the certificate route's, so the two routes are one relation;
* every vertex of a record is a cusp of its own row, no two records share both
  endpoints, and two records with one line vertex carry one class datum -- the
  class data is the row's own index, not a per-edge choice;
* the records are points of a finite ordered set: each hashes and its hash
  agrees with its equality, so the returned set identifies repeated edges and
  nothing else (``FiniteOrderedSets``).

The counts are computed, not typed.  ``U + U(2) + <-2>`` and ``U + U + <-4>``
hold no row of the lattice database (lattice-database#13) and ``T_Co`` holds
none either (lattice-database#7), so nothing here is compared with a card value.
The ``T_Co`` rows are minutes of computation per row and are the dispatched
driver's, not this gate's; what is gated here is that the class route decides
the relation on the lattices whose rows the gate can afford.
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
    r"""``U + U + <-4>``: rank five, ``|A_L| = 4``, so ``A_L`` has a class of order four."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)(((-4,),))


def _kernel_rows(lattice):
    r"""``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, built as the drivers build them."""
    stable = lattice.stable_orthogonal_group()
    return (stable, stable.intersection(lattice.O_plus()))


def _position(cusps, cusp):
    r"""The position of ``cusp`` among ``cusps``, or ``None`` when it is not one of them.

    By identity, and only by identity.  Two distinct cusps of one row are equal
    when a transporter carries one representative to the other, and that search
    reads the quotient's retained transports -- which the incidence routes fill
    as they walk.  A position read through that comparison therefore depends on
    which route ran last in the same process, and both incidence routes hand back
    the very cusp objects of the row, so identity is the statement wanted.
    """
    for position, candidate in enumerate(cusps):
        if candidate is cusp:
            return position
    return None


def _edge_positions(incidences, lines, planes):
    r"""The relation an incidence returns, as pairs of line and plane cusp positions.

    A ``set()`` and not a set display: in a session file a ``{...}`` display is the
    library's own finite literal set, and its equality with a ``set()`` is a
    statement about two kinds of set, not about their points.
    """
    pairs = set()
    for incidence in tuple(incidences):
        pairs.add(
            (
                _position(lines, incidence.line_cusp()),
                _position(planes, incidence.plane_cusp()),
            )
        )
    return pairs


def _flag_positions(subgroup):
    r"""The relation the subgroup's own flag row states, as pairs of cusp positions.

    This is the third computation of the same relation: each flag's line lies in
    exactly one cusp of the line row and its plane in exactly one cusp of the
    plane row, so the flag row reads as endpoint pairs without either incidence
    route being involved.
    """
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    pairs = set()
    for flag in subgroup.isotropic_orbit_representatives(2, flag=True):
        line, plane = flag.terms()
        line_cusp = next(
            cusp for cusp in lines if cusp.transporter_witness(line) is not None
        )
        plane_cusp = next(
            cusp for cusp in planes if cusp.transporter_witness(plane) is not None
        )
        pairs.add((_position(lines, line_cusp), _position(planes, plane_cusp)))
    return pairs


def _assert_the_records_are_edges(subgroup, incidences) -> None:
    r"""Each record is one edge of this subgroup's relation, and the records are its points."""
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    records = tuple(incidences)
    assert records
    for record in records:
        assert record.subgroup() is subgroup
        assert record.lattice() is subgroup.supergroup().domain()
        assert record.line_cusp() in lines
        assert record.plane_cusp() in planes
    for position, first in enumerate(records):
        for second in records[position + 1:]:
            assert not (
                first.line_cusp() is second.line_cusp()
                and first.plane_cusp() is second.plane_cusp()
            )
            if first.line_cusp() is second.line_cusp():
                assert first.divided_classes() == second.divided_classes()
    positions = dict()
    for position, record in enumerate(records):
        positions[record] = position
    assert tuple(positions[record] for record in records) == tuple(
        range(incidences.cardinality().finite_value())
    )


def _assert_the_two_routes_are_one_relation(subgroup) -> None:
    r"""The class route, the certificate route and the flag row state one relation.

    The flag row is read **first**, before either incidence route registers the
    row's covering and the planes' lifts in the character quotient: its cusps are
    found by a transporter witness, which reads that state, so a row read after
    the routes is a row read through them.
    """
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    flags = _flag_positions(subgroup)
    decided = subgroup.tits_building_incidence_by_divided_classes()
    certified = subgroup.tits_building_incidence()
    assert flags
    assert _edge_positions(decided, lines, planes) == flags
    assert _edge_positions(certified, lines, planes) == flags
    _assert_the_records_are_edges(subgroup, decided)
    vertices = set()
    for pair in flags:
        for position in pair:
            vertices.add(position)
    assert None not in vertices


def test_the_class_route_and_the_flag_row_agree_for_the_otilde_row_of_u_u2_m2() -> None:
    r"""``ker rho`` on ``U + U(2) + <-2>``: three line cusps, and the class route decides them."""
    lattice = _u_u2_m2()
    stable = _kernel_rows(lattice)[0]
    assert stable.cusps(1).cardinality() == cardinal(3)
    _assert_the_two_routes_are_one_relation(stable)


def test_the_class_route_and_the_flag_row_agree_for_the_otilde_plus_row_of_u_u2_m2() -> None:
    r"""``ker(rho, sn_RR)`` on ``U + U(2) + <-2>``: the finer group's relation too."""
    lattice = _u_u2_m2()
    plus = _kernel_rows(lattice)[1]
    _assert_the_two_routes_are_one_relation(plus)


def test_the_class_route_decides_the_rows_of_u_u_m4() -> None:
    r"""``U + U + <-4>``: a class of order four, and both kernel rows agree with their flags."""
    lattice = _u_u_m4()
    for subgroup in _kernel_rows(lattice):
        _assert_the_two_routes_are_one_relation(subgroup)
