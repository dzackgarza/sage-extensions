r"""Connected elliptic subdiagrams of Sterk's five Coxeter diagrams.

The committed artifacts under ``computations/enriques-paper-artifacts/Sterk``
draw one picture per connected elliptic induced subdiagram of each diagram,
together with the empty diagram; the counts and types below are read from
them.  A type is recorded as \((\text{rank}, \text{Cartan letter}, \text{scale})\):
a subdiagram of roots of square \(-4\) is a scale-\(2\) copy of a simply laced
type, and a subdiagram mixing roots of square \(-2\) and \(-4\) is of type
\(B_n = C_n\) at scale \(1\).
"""

from sage_extensions.all import *

_ARCHIVED_TOTALS = {
    "Sterk_1": 121,
    "Sterk_2": 65,
    "Sterk_3": 67,
    "Sterk_4": 78,
    "Sterk_5": 119,
}

_CONNECTED_ELLIPTIC_TYPES = {
    "Sterk_1": {
        (1, "A", 2): 12,
        (2, "A", 2): 10,
        (3, "A", 2): 12,
        (4, "A", 2): 12,
        (4, "D", 2): 2,
        (5, "A", 2): 12,
        (5, "D", 2): 4,
        (6, "A", 2): 12,
        (6, "D", 2): 4,
        (6, "E", 2): 2,
        (7, "A", 2): 14,
        (7, "D", 2): 4,
        (7, "E", 2): 4,
        (8, "A", 2): 4,
        (8, "D", 2): 8,
        (8, "E", 2): 4,
    },
    "Sterk_2": {
        (1, "A", 1): 1,
        (1, "A", 2): 9,
        (2, "A", 2): 8,
        (2, "C", 1): 1,
        (3, "A", 2): 8,
        (3, "B", 1): 1,
        (4, "A", 2): 7,
        (4, "B", 1): 1,
        (4, "D", 2): 1,
        (5, "A", 2): 5,
        (5, "B", 1): 1,
        (5, "D", 2): 2,
        (6, "A", 2): 4,
        (6, "B", 1): 1,
        (6, "D", 2): 1,
        (6, "E", 2): 1,
        (7, "A", 2): 3,
        (7, "B", 1): 1,
        (7, "D", 2): 1,
        (7, "E", 2): 1,
        (8, "A", 2): 1,
        (8, "B", 1): 2,
        (8, "D", 2): 1,
        (8, "E", 2): 1,
        (9, "B", 1): 1,
    },
    "Sterk_3": {
        (1, "A", 1): 2,
        (1, "A", 2): 10,
        (2, "A", 2): 7,
        (2, "C", 1): 4,
        (3, "A", 2): 7,
        (3, "B", 1): 2,
        (4, "A", 2): 6,
        (4, "B", 1): 2,
        (4, "D", 2): 1,
        (5, "A", 2): 5,
        (5, "B", 1): 2,
        (5, "D", 2): 2,
        (6, "A", 2): 2,
        (6, "B", 1): 4,
        (6, "D", 2): 2,
        (6, "E", 2): 1,
        (7, "A", 2): 1,
        (7, "B", 1): 2,
        (7, "E", 2): 2,
        (8, "B", 1): 2,
    },
    "Sterk_4": {
        (1, "A", 1): 2,
        (1, "A", 2): 9,
        (2, "A", 2): 8,
        (2, "C", 1): 2,
        (3, "A", 2): 9,
        (3, "B", 1): 2,
        (4, "A", 2): 6,
        (4, "B", 1): 4,
        (4, "D", 2): 2,
        (5, "A", 2): 5,
        (5, "B", 1): 2,
        (5, "D", 2): 2,
        (6, "A", 2): 4,
        (6, "B", 1): 2,
        (6, "D", 2): 2,
        (7, "A", 2): 4,
        (7, "B", 1): 2,
        (7, "D", 2): 2,
        (8, "B", 1): 4,
        (8, "D", 2): 4,
    },
    "Sterk_5": {
        (1, "A", 1): 4,
        (1, "A", 2): 10,
        (2, "A", 2): 8,
        (2, "C", 1): 8,
        (3, "A", 2): 8,
        (3, "B", 1): 8,
        (4, "A", 2): 8,
        (4, "B", 1): 8,
        (5, "A", 2): 8,
        (5, "B", 1): 8,
        (6, "A", 2): 8,
        (6, "B", 1): 8,
        (7, "A", 2): 8,
        (7, "B", 1): 8,
        (8, "B", 1): 8,
    },
}


def test_sterk_connected_elliptic_populations_match_the_committed_archive() -> None:
    diagrams = Sterk.diagrams()
    assert Set(diagrams) == Set(_ARCHIVED_TOTALS)

    for name, expected_total in _ARCHIVED_TOTALS.items():
        diagram = diagrams[name]
        empty = diagram.induced_subdiagram(())
        connected = diagram.elliptic_subdiagrams(connected=True)

        assert empty.is_elliptic()
        assert not empty.is_connected()
        assert connected.cardinality() + 1 == expected_total
        assert all(subdiagram.is_elliptic() for subdiagram in connected)
        assert all(subdiagram.is_connected() for subdiagram in connected)


def test_sterk_diagram_vertices_keep_the_zero_based_root_labels() -> None:
    r"""The five published diagrams use the literal root indices ``r0,...,r(n-1)``."""
    layouts = Sterk.diagram_layouts()
    diagrams = Sterk.diagrams()
    for name, layout in layouts.items():
        expected = {f"r{index}" for index in range(len(layout))}
        assert Set(diagrams[name].index_set()) == Set(expected)
        assert Set(layout) == Set(range(len(layout)))
        assert Set(diagrams[name].preferred_positions()) == Set(expected)
        assert dict(diagrams[name].preferred_positions()) == {
            f"r{index}": position for index, position in layout.items()
        }


def test_sterk_connected_elliptic_subdiagrams_have_the_recorded_types() -> None:
    r"""Each Sterk diagram's connected elliptic subdiagrams, counted by rank, Cartan
    letter and scale, form the multiset drawn in the committed artifacts."""
    diagrams = Sterk.diagrams()

    def scaled_type(subdiagram):
        # B_n and C_n have one Coxeter diagram, which the archive records as B;
        # in rank two, however, the archived canonical Cartan label is C2.
        # Preserve that rank-two convention while identifying B_n/C_n for n>2.
        # root_scale() keeps the sign of the negative-definite Sterk roots.
        letter = subdiagram.label()[0]
        rank = int(subdiagram.cardinality())
        if letter == "C" and rank != 2:
            letter = "B"
        return (rank, letter, -subdiagram.root_scale())

    for name, expected in _CONNECTED_ELLIPTIC_TYPES.items():
        connected = diagrams[name].elliptic_subdiagrams(connected=True)
        types = [scaled_type(subdiagram) for subdiagram in connected]

        assert connected.cardinality() == sum(expected.values())
        assert Set(types) == Set(expected)
        for key, count in expected.items():
            assert types.count(key) == count
