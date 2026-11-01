r"""Exhaustive audit of the maximal-subdiagram queries on small fixtures.

The Sterk cases check the owner's maximal elliptic family against itself (each
returned member admits no further vertex).  These fixtures check it against an
independent enumeration on diagrams small enough to enumerate every subset and
build every induced subdiagram, and they pin the two contracts the larger
cases cannot show: the caps are applied after maximality, and the generic
predicate receives vertex labels rather than positions.
"""

from itertools import combinations

from sage_extensions.all import CoxeterDiagrams
from sage_extensions.categories.coxeter_diagrams import _owned_coxeter_matrix
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

_FIXTURES = {
    "affine A2": ["A", 2, 1],
    "affine A1": ["A", 1, 1],
    "B2": ["B", 2],
    "affine B2": ["B", 2, 1],
}


def _fixture(label):
    return CoxeterDiagrams()(list(label))


def test_the_maximal_elliptic_family_agrees_with_an_exhaustive_enumeration() -> None:
    r"""Every subset is decided by the public predicate, then filtered by inclusion."""
    for name, label in _FIXTURES.items():
        diagram = _fixture(label)
        vertices = tuple(diagram.index_set())

        elliptic = []
        for size in range(len(vertices) + 1):
            for subset in combinations(vertices, size):
                if diagram.induced_subdiagram(subset).is_elliptic():
                    elliptic.append(frozenset(subset))
        expected = {
            candidate
            for candidate in elliptic
            if not any(candidate < other for other in elliptic)
        }

        produced = {frozenset(entry.index_set()) for entry in diagram.maximal_elliptic_subdiagrams()}
        assert produced == expected, (name, produced, expected)


def test_every_maximal_elliptic_survivor_admits_no_further_vertex() -> None:
    r"""Checked for every survivor of every fixture, through the public decision."""
    for name, label in _FIXTURES.items():
        diagram = _fixture(label)
        maximal = tuple(diagram.maximal_elliptic_subdiagrams())
        assert maximal

        for entry in maximal:
            selected = tuple(entry.index_set())
            assert entry.is_elliptic(), (name, selected)
            assert entry.arrow().codomain() is diagram, (name, selected)
            for vertex in diagram.index_set():
                if vertex in selected:
                    continue
                enlarged = diagram.induced_subdiagram(selected + (vertex,))
                assert enlarged.is_elliptic() is False, (name, selected, vertex)


def test_both_caps_are_applied_after_maximality_for_the_elliptic_query() -> None:
    r"""For every cap the answer is the uncapped family filtered, never a smaller re-maximalisation."""
    for name, label in _FIXTURES.items():
        diagram = _fixture(label)
        uncapped = tuple(diagram.maximal_elliptic_subdiagrams())
        width = int(diagram.cardinality())

        for cap in range(width + 1):
            by_vertices = tuple(diagram.maximal_elliptic_subdiagrams(max_rank=cap))
            assert by_vertices == tuple(
                entry for entry in uncapped if int(entry.cardinality()) <= cap
            ), (name, cap)

            by_form = tuple(diagram.maximal_elliptic_subdiagrams(max_form_rank=cap))
            assert by_form == tuple(
                entry for entry in uncapped if int(entry.form_rank()) <= cap
            ), (name, cap)

        # An elliptic diagram has zero nullity, so on this family the geometric
        # cap and the vertex cap select the same members at every threshold.
        for cap in range(width + 1):
            assert tuple(
                diagram.maximal_elliptic_subdiagrams(max_rank=cap)
            ) == tuple(diagram.maximal_elliptic_subdiagrams(max_form_rank=cap)), (name, cap)


def test_the_generic_predicate_receives_every_subset_as_labels() -> None:
    r"""Not one representative subset: all of them, and as labels."""
    vertices = finite_ordered_set(("u", "v", "w"))
    entries = {(left, right): 1 if left == right else 3 for left in vertices for right in vertices}
    diagram = CoxeterDiagrams().from_coxeter_matrix(_owned_coxeter_matrix(vertices, entries))

    received = []

    def predicate(labels):
        received.append(tuple(labels))
        return len(labels) <= 1

    maximal = tuple(diagram.maximal_subdiagrams(predicate))

    offered = set()
    for size in range(len(tuple(diagram.index_set())) + 1):
        for subset in combinations(tuple(diagram.index_set()), size):
            offered.add(subset)
    assert len(received) == len(offered)
    assert set(received) == offered
    assert all(isinstance(label, str) for labels in received for label in labels)
    assert {tuple(entry.index_set()) for entry in maximal} == {("u",), ("v",), ("w",)}
