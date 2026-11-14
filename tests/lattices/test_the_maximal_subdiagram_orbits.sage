r"""Aut-orbits of the maximal elliptic and maximal parabolic subdiagrams (#254).

The stage-2 pages classify the subdiagrams of a cusp diagram up to diagram
automorphism, and the library had no orbit set of the *maximal* elliptic or
parabolic ones.  Maximality is a relation of a subdiagram to the ambient diagram
and not a predicate of the subdiagram alone, so the queries that filter by a
predicate (``elliptic_subdiagram_orbits`` and its parabolic variant) do not
serve: no predicate on a subdiagram knows what contains it.

Three properties are checked here for both families and both values of
``connected``:

* the orbit set's points are exactly the maximal family — the ranks name the
  subdiagrams ``maximal_elliptic_subdiagrams`` and
  ``maximal_parabolic_subdiagrams`` return, every member is named, and no rank
  is named twice, so the orbits partition the family;
* each orbit is one orbit of ``Aut`` — the images of its representative under
  every element of the group are exactly its points, and orbit-stabilizer holds
  for it there;
* ``subdiagram_orbit_poset`` accepts the orbit set, one member per orbit, and two
  distinct maximal members are incomparable in the order inclusion induces.

The specimens are `E_6`, whose diagram automorphism group has order two, and
Sterk's five 0-cusp diagrams of the Enriques period lattice
`T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)` (H. Sterk, *Compactifications of
the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991),
§4.3.5--4.3.9, pp. 19--24).  Those five are read by tag from card `029J`'s
``integral.cusp_chambers`` rows, through the digest
``tests/cards/refresh_lattice_database_enriques.py`` writes: the walls are the
vertices and the card's ``diagram`` bonds are the Coxeter entries, so no edge and
no count is typed here.

No card states how many orbits a cusp diagram's maximal subdiagrams fall into,
so no orbit count is asserted: the counts this run meets are recorded in
``results/issue254-maximal-subdiagram-orbits.md``.
"""

from sage_extensions.all import *


def _count(values) -> int:
    r"""The number of entries of ``values``."""
    return sum(1 for _value in values)


def _cusp_diagram(row):
    r"""The Coxeter diagram one card 029J cusp row states, its walls as vertices in the card's order."""
    walls = tuple(row["vertices"])
    position = {wall: place for place, wall in enumerate(walls)}
    total = _count(walls)
    rows = [[1 if left == right else 2 for right in range(total)] for left in range(total)]
    for bond in row["edges"]:
        entry = aleph0 if bond["order"] is None else bond["order"]
        rows[position[bond["left"]]][position[bond["right"]]] = entry
        rows[position[bond["right"]]][position[bond["left"]]] = entry
    return CoxeterDiagrams()(rows)


def specimens():
    r"""`E_6` and Sterk's five cusp diagrams, each under the label it is reported by."""
    cusps = card("cusp_diagrams", "029J")["rows"]["gamma-en-2"]
    return (("E6", CoxeterDiagrams().from_cartan_type(["E", 6])),) + tuple(
        (f"cusp {row['statement']}", _cusp_diagram(row)) for row in cusps
    )


SPECIMENS = specimens()
KEYS = tuple(
    (family, connected) for family in ("elliptic", "parabolic") for connected in (False, True)
)
MAXIMAL = {}
ORBITS = {}
POSETS = {}


def maximal_families(label, diagram):
    r"""The four families of maximal subdiagrams of one specimen, computed once for the run."""
    if label not in MAXIMAL:
        MAXIMAL[label] = {
            ("elliptic", False): diagram.maximal_elliptic_subdiagrams(connected=False),
            ("elliptic", True): diagram.maximal_elliptic_subdiagrams(connected=True),
            ("parabolic", False): diagram.maximal_parabolic_subdiagrams(connected=False),
            ("parabolic", True): diagram.maximal_parabolic_subdiagrams(connected=True),
        }
    return MAXIMAL[label]


def orbit_sets(label, diagram):
    r"""The four maximal orbit sets of one specimen, computed once for the run."""
    if label not in ORBITS:
        ORBITS[label] = {
            ("elliptic", False): diagram.maximal_elliptic_subdiagram_orbits(connected=False),
            ("elliptic", True): diagram.maximal_elliptic_subdiagram_orbits(connected=True),
            ("parabolic", False): diagram.maximal_parabolic_subdiagram_orbits(connected=False),
            ("parabolic", True): diagram.maximal_parabolic_subdiagram_orbits(connected=True),
        }
    return ORBITS[label]


def orbit_poset(label, diagram, key):
    r"""``subdiagram_orbit_poset`` applied to one maximal orbit set, computed once for the run."""
    if (label, key) not in POSETS:
        POSETS[(label, key)] = diagram.subdiagram_orbit_poset(orbit_sets(label, diagram)[key])
    return POSETS[(label, key)]


def stated_ranks(diagram, family):
    r"""The ranks of the members of ``family``, read from their vertex sets."""
    return sorted(int(diagram.subdiagram_rank(entry.index_set())) for entry in family)


def reached_ranks(orbits):
    r"""The ranks of the orbit set's points, one entry per point."""
    return sorted(int(rank) for orbit in orbits for rank in orbit.points())


def test_the_orbits_partition_the_maximal_elliptic_subdiagrams() -> None:
    r"""The maximal elliptic family is nonempty on every specimen, and its orbits cover it.

    The public query is the authority on the family and the orbit set is built on
    ranks, so the two are compared through ``subdiagram_rank``: the ranks of the
    members and the ranks of the points are the same list, which also says no rank
    is named twice.  The nonemptiness guard keeps the equality from holding of two
    empty families.
    """
    for label, diagram in SPECIMENS:
        for connected in (False, True):
            family = maximal_families(label, diagram)[("elliptic", connected)]
            orbits = orbit_sets(label, diagram)[("elliptic", connected)]

            assert int(family.cardinality()) > 0
            assert stated_ranks(diagram, family) == reached_ranks(orbits)


def test_the_orbits_partition_the_maximal_parabolic_subdiagrams() -> None:
    r"""The parabolic counterpart, with the emptiness of `E_6`'s family stated rather than skipped.

    `E_6` is elliptic, so it has no parabolic induced subdiagram at all; the cusp
    diagrams are hyperbolic, and each of them does have one — which is the
    hypothesis the nonemptiness guard records for the family that carries the
    check.
    """
    families = {}
    for label, diagram in SPECIMENS:
        for connected in (False, True):
            family = maximal_families(label, diagram)[("parabolic", connected)]
            orbits = orbit_sets(label, diagram)[("parabolic", connected)]
            families[(label, connected)] = int(family.cardinality())

            assert stated_ranks(diagram, family) == reached_ranks(orbits)

    assert all(
        families[(label, connected)] > 0
        for label, _diagram in SPECIMENS
        if label != "E6"
        for connected in (False, True)
    )
    assert families[("E6", False)] == 0


def test_each_maximal_elliptic_orbit_is_one_automorphism_orbit() -> None:
    r"""An orbit is the full image of its representative, and orbit-stabilizer holds there.

    The action is the one the orbit set carries, evaluated at every element of
    ``Aut``; the image of the representative therefore has to be the orbit's own
    point set, which is stronger than being contained in it.
    """
    for label, diagram in SPECIMENS:
        for key in KEYS:
            if key[0] != "elliptic":
                continue
            orbits = orbit_sets(label, diagram)[key]
            action = orbits.g_set()

            for orbit in orbits:
                images = frozenset(
                    action.action_of(automorphism)(orbit.representative())
                    for automorphism in diagram.Aut()
                )
                assert images == frozenset(orbit.points())
                assert int(orbit.cardinality()) * int(orbit.stabilizer().cardinality()) == int(
                    diagram.Aut().cardinality()
                )


def test_each_maximal_parabolic_orbit_is_one_automorphism_orbit() -> None:
    r"""The parabolic counterpart of the elliptic orbit check, on the same action."""
    for label, diagram in SPECIMENS:
        for key in KEYS:
            if key[0] != "parabolic":
                continue
            orbits = orbit_sets(label, diagram)[key]
            action = orbits.g_set()

            for orbit in orbits:
                images = frozenset(
                    action.action_of(automorphism)(orbit.representative())
                    for automorphism in diagram.Aut()
                )
                assert images == frozenset(orbit.points())
                assert int(orbit.cardinality()) * int(orbit.stabilizer().cardinality()) == int(
                    diagram.Aut().cardinality()
                )


def test_the_maximal_orbit_sets_feed_the_subdiagram_orbit_poset() -> None:
    r"""``subdiagram_orbit_poset`` accepts each of them, and distinct maximal orbits are incomparable.

    Two distinct maximal members are incomparable as vertex sets, and ``Aut``
    carries an inclusion to an inclusion, so no member of one orbit sits inside a
    member of the other: the order has one member per orbit and no relation
    between distinct ones.  Reflexivity is asserted alongside, so the negative
    reading is not an empty relation.
    """
    for label, diagram in SPECIMENS:
        for key in KEYS:
            orbits = orbit_sets(label, diagram)[key]
            poset = orbit_poset(label, diagram, key)
            elements = {int(element.representative()): element for element in poset}

            assert int(poset.cardinality()) == int(orbits.cardinality())
            for orbit in orbits:
                element = elements[int(orbit.representative())]
                assert poset.le(element, element)
                for other in orbits:
                    if other != orbit:
                        assert not poset.le(element, elements[int(other.representative())])


def test_the_rank_of_a_subdiagram_is_its_rank_in_the_induced_enumeration() -> None:
    r"""``subdiagram_rank`` agrees with the enumeration on the diagrams cheap to enumerate.

    The orbit sets are built on ranks computed from subsets rather than looked up
    in ``induced_subdiagrams``, so the two readings of a rank are compared here on
    every induced subdiagram of the specimens whose enumeration is small: `E_6`,
    the smallest cusp diagram, affine `\tilde A_2` and `D_4`.
    """
    small = (
        ("affine A2", CoxeterDiagrams()([[1, 3, 3], [3, 1, 3], [3, 3, 1]])),
        ("D4", CoxeterDiagrams()([[1, 3, 3, 3], [3, 1, 2, 2], [3, 2, 1, 2], [3, 2, 2, 1]])),
        SPECIMENS[0],
        min(SPECIMENS[1:], key=lambda specimen: int(specimen[1].cardinality())),
    )
    for label, diagram in small:
        enumerated = diagram.induced_subdiagrams()
        ranking = enumerated.ranking_map()
        assert int(diagram.subdiagram_rank(diagram.index_set())) == int(
            ranking(diagram.induced_subdiagram(diagram.index_set()))
        )
        for subdiagram in enumerated:
            assert int(diagram.subdiagram_rank(subdiagram.index_set())) == int(ranking(subdiagram))


def test_a_vertex_relabelling_leaves_the_orbit_counts_unchanged() -> None:
    r"""Reversing and cyclically shifting the vertex order permute the subdiagrams and their orbits.

    The relabelled diagram is this one's Coxeter matrix with its vertices in a
    different order, so the two are equal as labelled graphs up to that order and
    the automorphism groups have equal order; the orbit counts of both maximal
    families are compared, since a relabelling that preserved nothing would still
    leave the group order alone.
    """
    for label, diagram in SPECIMENS:
        total = int(diagram.cardinality())
        matrix = tuple(
            tuple(diagram.coxeter_entry(left, right) for right in diagram.index_set())
            for left in diagram.index_set()
        )
        reversal = tuple(
            tuple(matrix[total - 1 - left][total - 1 - right] for right in range(total))
            for left in range(total)
        )
        shifted = tuple(
            tuple(matrix[(left + 1) % total][(right + 1) % total] for right in range(total))
            for left in range(total)
        )
        for relabelled in (CoxeterDiagrams()(reversal), CoxeterDiagrams()(shifted)):
            assert int(relabelled.Aut().cardinality()) == int(diagram.Aut().cardinality())
            assert int(relabelled.maximal_elliptic_subdiagram_orbits().cardinality()) == int(
                diagram.maximal_elliptic_subdiagram_orbits().cardinality()
            )
            assert int(relabelled.maximal_parabolic_subdiagram_orbits().cardinality()) == int(
                diagram.maximal_parabolic_subdiagram_orbits().cardinality()
            )
