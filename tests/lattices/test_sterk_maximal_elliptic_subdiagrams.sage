r"""Maximal elliptic subdiagrams of Sterk's five diagrams, disconnected allowed.

A cusp computation asks each of the five Sterk diagrams for its elliptic induced
subdiagrams maximal for inclusion of vertices, with ``connected=False``: the
elliptic subdiagram belonging to a cusp can be a disjoint union of finite-type
components, so the connected family is not enough, and a Type III ray needs one
of rank nine.  The counts below are the enumeration this file holds the owner
to; the assertions beside them are the contract -- ellipticity, maximality
against every single added vertex, retained vertex labels, retained roots and
root Gram, the inclusion arrow, and the disconnected components.
"""

from collections import Counter

from sage_extensions.all import Sterk

_MAXIMAL_TOTALS = {"Sterk_1": 44, "Sterk_2": 9, "Sterk_3": 34, "Sterk_4": 29, "Sterk_5": 132}

_MAXIMAL_RANKS = {
    "Sterk_1": Counter({8: 30, 9: 14}),
    "Sterk_2": Counter({8: 1, 9: 8}),
    "Sterk_3": Counter({8: 5, 9: 29}),
    "Sterk_4": Counter({8: 8, 9: 21}),
    "Sterk_5": Counter({8: 30, 9: 102}),
}


def _maximal(diagram):
    return tuple(diagram.maximal_elliptic_subdiagrams(connected=False))


def test_the_five_sterk_diagrams_have_their_maximal_elliptic_subdiagrams() -> None:
    for name, diagram in Sterk.diagrams().items():
        maximal = _maximal(diagram)

        assert len(maximal) == _MAXIMAL_TOTALS[name], name
        assert Counter(len(entry.index_set()) for entry in maximal) == _MAXIMAL_RANKS[name], name
        # A Type III ray needs an elliptic subdiagram of rank nine.
        assert any(len(entry.index_set()) == 9 for entry in maximal), name


def test_a_maximal_elliptic_subdiagram_retains_labels_roots_gram_and_inclusion() -> None:
    for name, diagram in Sterk.diagrams().items():
        parent_gram = diagram.root_gram_tensor()
        ranking = diagram.index_set().ranking_map()
        for entry in _maximal(diagram):
            assert entry.is_elliptic(), name
            assert entry.arrow().codomain() is diagram, name

            selected = tuple(entry.index_set())
            positions = tuple(int(ranking(label)) for label in selected)
            assert all(label in diagram.index_set() for label in selected), name
            assert tuple(entry.vertex_names()) == tuple(
                diagram.vertex_names()[position] for position in positions
            ), name
            assert tuple(entry.root(label) for label in selected) == tuple(
                diagram.root(diagram.index_set()[position]) for position in positions
            ), name

            entry_gram = entry.root_gram_tensor()
            for row, left in enumerate(selected):
                for column, right in enumerate(selected):
                    assert entry.coxeter_entry(left, right) == diagram.coxeter_entry(left, right), name
                    assert entry_gram[row, column] == parent_gram[positions[row], positions[column]], name


def test_each_maximal_elliptic_subdiagram_admits_no_further_vertex() -> None:
    r"""Maximality is checked against the public subdiagram elliptic decision."""
    for name, diagram in Sterk.diagrams().items():
        maximal = _maximal(diagram)
        vertex_sets = tuple(frozenset(entry.index_set()) for entry in maximal)
        assert not any(left < right for left in vertex_sets for right in vertex_sets), name

        # Every returned maximal member is closed against adding any single
        # vertex it omits, decided by the public subdiagram contract.
        for entry in maximal:
            selected = tuple(entry.index_set())
            for vertex in diagram.index_set():
                if vertex in selected:
                    continue
                enlarged = diagram.induced_subdiagram(selected + (vertex,))
                assert enlarged.is_elliptic() is False, (name, selected, vertex)


def test_a_disconnected_maximal_elliptic_subdiagram_retains_its_components() -> None:
    r"""A disconnected member is the disjoint union of elliptic components."""
    for name, diagram in Sterk.diagrams().items():
        disconnected = tuple(entry for entry in _maximal(diagram) if not entry.is_connected())
        assert disconnected, name

        entry = disconnected[0]
        components = tuple(entry.connected_component_vertex_sets())
        assert len(components) > 1, name
        union = frozenset().union(*components)
        assert union == frozenset(entry.index_set()), name
        for component in components:
            induced = entry.induced_subdiagram(tuple(component))
            assert induced.is_connected(), name
            assert induced.is_elliptic(), name
