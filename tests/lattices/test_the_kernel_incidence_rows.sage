r"""The kernel incidence rows of ``T_Co`` on the lattices the per-test gate can afford (#381).

``Otilde(T_Co) = ker rho`` and ``Otilde+(T_Co) = ker(rho, sn_RR)`` are the two
kernel groups whose plane rows #390 returns, 189720 planes each, and #381 owes
their incidence with the line rows of #357.  The rows themselves are the CI job
``tests/coble_gamma_co_2_incidence_rows.py --rows Otilde,Otilde+ --lattice Tco``:
each realizes one plane per double coset, so they are dispatched, never
repeated in this gate.  This file gates, on the lattices whose rows the gate
can afford, what the construction guarantees for **every** output of a kernel
incidence row, and the two counts that are forced.

**The guarantees.**  The edge set of the incidence at a subgroup ``Gamma`` is
the set of ``(Stab_Gamma(P), line)`` orbit pairs, one per ``Gamma``-orbit of
flags whose line lies in its plane, read as pairs of cusps; so for every
output of ``tits_building_incidence()``:

* each edge joins a line that lies in its plane -- the edge's line term is in
  its plane term, and one element of ``Gamma`` carries the selected line cusp
  representative into the selected plane cusp representative;
* the edges are a relation: no two of them share their line and plane cusp
  endpoints, and each edge's two cusps are cusps of the row;
* every line cusp and every plane cusp is a vertex of some edge -- a primitive
  isotropic line lies in a primitive isotropic plane in an indefinite lattice
  of these ranks, so no vertex is isolated;
* the relation is the subgroup's own flag row read as endpoint pairs, through
  ``isotropic_orbit_representatives(2, flag=True)`` -- a different public call
  than ``tits_building_incidence()``, so the two routes check each other;
* the records are points of a finite ordered set: each hashes, its hash agrees
  with its equality, and two edges are equal exactly when they have the same
  endpoints, so the returned set identifies repeated edges and nothing else
  (``FiniteOrderedSets``).

**The forced counts, both computed and neither typed.**  ``Otilde`` is the
kernel of the discriminant representation, so on a lattice with
``|O(A_L)| = 1`` it *is* ``O(L)``, and ``Otilde+ = ker(rho, sn_RR)`` is
``O^+(L)``; both kernel rows and both incidences are then the ambient ones, and
that is the first check.  On a lattice with a non-trivial discriminant image
the rows split -- on ``U + U(2) + <-2>`` each kernel row has three line cusps
and two plane cusps of its own, and the flag row's four endpoint pairs are a
strict subset of the six pairs of the two rows -- and the comparison that still
holds is ``Otilde+ <= Otilde``: a subgroup has at least as many cusps of each
kind as its supergroup.

**The lattices.**  ``6JRS = U + U + <-2>``, the card-named ``U + U + <-2>`` of
the kernel plane rows' gate (``test_the_stable_plane_rows_...``), and
``U + U(2) + <-4>``, the same shape with a non-trivial discriminant image and a
relation that is not complete.  No lattice-database card holds a row of either
(lattice-database#13), and none holds a ``T_Co`` row (lattice-database#7), so
no number here is a card value: each is computed.  The specimens are split per
lattice and per group so one costly row cannot hide another's result.

``U + U(2) + <-2>`` is not the second specimen although the driver runs it:
in this session's ring its ambient flag row cannot be built at all --
``ModuleAutomorphismGroup.flag_stabilizer`` inverts its basis change at the
rank-two zero-form reduction lattice, and that change has determinant ``-2``,
so it is no basis change and has no inverse in the integer ring (``Generic
endomorphism of Integral lattice of rank 2 and signature (0, 0) has no
inverse ...: its determinant -2 is not a unit of Integer Ring``).  That is a defect of that route and not of this
row, and it is not repaired here; the driver's own run of the same lattice, in
the image's plain interpreter, decides its two rows.

The counts these rows return are recorded in the commit body of the push that
lands this file -- six edges over four line and three plane cusps for each
kernel row of ``U + U(2) + <-4>``, and one edge over one line and one plane
cusp for each kernel row of ``6JRS``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _6jrs():
    r"""``6JRS = U + U + <-2>``: rank five, ``|A_L| = 2`` and ``|O(A_L)| = 1``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def _u_plus_u2_plus_m4():
    r"""``U + U(2) + <-4>``: rank five, ``|A_L| = 16`` and a non-trivial image."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-4]])
    )


def _kernel_rows(lattice):
    r"""``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, built as the drivers build them."""
    stable = lattice.stable_orthogonal_group()
    return (
        ("Otilde", stable),
        ("Otilde+", stable.intersection(lattice.O_plus())),
    )


def _contained(line, plane) -> bool:
    r"""Whether the retained generator of the line term lies in the plane term."""
    inclusion = line.inclusion()
    domain = inclusion.domain()
    label = next(iter(domain.module_generating_set()))
    return bool(plane.inclusion().is_in_image(inclusion(domain.module_generator(label))))


def _position(cusps, cusp):
    r"""The position of ``cusp`` among ``cusps``, or ``None`` when it is not one of them."""
    for position, candidate in enumerate(cusps):
        if candidate is cusp or candidate == cusp:
            return position
    return None


def _flag_pairs(subgroup):
    r"""The subgroup's flag row read as (line cusp, plane cusp) positions.

    The route is ``isotropic_orbit_representatives(2, flag=True)``, the
    subgroup's own orbits of flags: each flag's line is carried to exactly one
    of the line row's cusps and its plane to exactly one of the plane row's,
    by the cusp's own transporter witness, so the pair of positions is the
    incidence pair the flag witnesses.  This is the relation the incidence call
    must return, computed through a different public call.
    """
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    pairs = set()
    for flag in subgroup.isotropic_orbit_representatives(2, flag=True):
        line, plane = flag.terms()
        line_cusp = next(cusp for cusp in lines if cusp.transporter_witness(line) is not None)
        plane_cusp = next(cusp for cusp in planes if cusp.transporter_witness(plane) is not None)
        pairs.add((_position(lines, line_cusp), _position(planes, plane_cusp)))
    return pairs


def _assert_records_are_points(incidences) -> None:
    r"""The incidence records hash, with a hash that agrees with their equality.

    ``FiniteOrderedSets`` states the rule and relies on it: each point of a
    finite ordered set hashes, and the hash agrees with the equality, because
    the set's inverse enumeration is a hash table of its points.  Two records
    are one edge exactly when they have the same line and plane cusps -- the
    relation, not the flag certificate -- so the table holds one key per edge
    and no edge is lost.
    """
    records = tuple(incidences)
    for first in records:
        for second in records:
            assert (first == second) == (
                first is second
                or (
                    first.line_cusp() is second.line_cusp()
                    and first.plane_cusp() is second.plane_cusp()
                )
            )
    positions = dict()
    for position, record in enumerate(records):
        positions[record] = position
    assert tuple(positions[record] for record in records) == tuple(
        range(incidences.cardinality().finite_value())
    )


def _assert_kernel_incidence_contract(subgroup):
    r"""Assert every guarantee of a kernel incidence row and return its edge set."""
    incidences = subgroup.tits_building_incidence()
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    line_vertices = set()
    plane_vertices = set()
    retained = []
    for incidence in tuple(incidences):
        assert incidence.subgroup() is subgroup
        assert _contained(incidence.line(), incidence.plane())
        witness = incidence.plane_transporter() * ~incidence.line_transporter()
        assert witness in subgroup
        assert _contained(
            witness.transport_isotropic_object(incidence.line_cusp().representative()),
            incidence.plane_cusp().representative(),
        )
        assert incidence.line_cusp() in lines
        assert incidence.plane_cusp() in planes
        retained.append((incidence.line_cusp(), incidence.plane_cusp()))
        line_vertices.add(incidence.line_cusp())
        plane_vertices.add(incidence.plane_cusp())
    for position, first in enumerate(retained):
        for second in retained[position + 1:]:
            assert not (first[0] is second[0] and first[1] is second[1])
    for cusp in lines:
        assert cusp in line_vertices
    for cusp in planes:
        assert cusp in plane_vertices
    _assert_records_are_points(incidences)
    assert set([
        (_position(lines, incidence.line_cusp()), _position(planes, incidence.plane_cusp()))
        for incidence in tuple(incidences)
    ]) == _flag_pairs(subgroup)
    return incidences


def test_6jrs_kernel_rows_are_the_ambient_rows() -> None:
    r"""``|O(A_L)| = 1``: ``Otilde = O(L)`` and ``Otilde+ = O^+(L)``, rows and incidences alike."""
    lattice = _6jrs()
    assert lattice.discriminant_group().orthogonal_group().cardinality() == cardinal(1)
    for label, subgroup in _kernel_rows(lattice):
        ambient = lattice.Aut() if label == "Otilde" else lattice.O_plus()
        incidences = _assert_kernel_incidence_contract(subgroup)
        assert subgroup.cusps(1).cardinality() == ambient.cusps(1).cardinality()
        assert subgroup.cusps(2).cardinality() == ambient.cusps(2).cardinality()
        assert incidences.cardinality() == ambient.tits_building_incidence().cardinality()
        assert incidences.cardinality() == cardinal(1)


def test_u_plus_u2_plus_m4_otilde_incidence_is_its_flag_row() -> None:
    r"""``U + U(2) + <-4>``: every edge of ``Otilde`` joins a line to the plane it lies in."""
    lattice = _u_plus_u2_plus_m4()
    stable = lattice.stable_orthogonal_group()

    incidences = _assert_kernel_incidence_contract(stable)

    assert stable.cusps(1).cardinality() == cardinal(4)
    assert stable.cusps(2).cardinality() == cardinal(3)
    assert incidences.cardinality() == cardinal(6)


def test_u_plus_u2_plus_m4_otilde_plus_incidence_is_its_flag_row() -> None:
    r"""``U + U(2) + <-4>``: the same for ``Otilde+``, whose vertex rows cannot be smaller."""
    lattice = _u_plus_u2_plus_m4()
    stable = lattice.stable_orthogonal_group()
    plus = stable.intersection(lattice.O_plus())

    incidences = _assert_kernel_incidence_contract(plus)

    assert plus.cusps(1).cardinality() >= stable.cusps(1).cardinality()
    assert plus.cusps(2).cardinality() >= stable.cusps(2).cardinality()
    assert incidences.cardinality() == cardinal(6)
