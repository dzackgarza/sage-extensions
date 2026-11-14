r"""Disjoint unions of affine components, and maximal subdiagrams with a rank cap.

A connected diagram is classified by the inertia of its Schlaefli form:
elliptic, parabolic (affine), or indefinite.  The nullity of a disjoint union is
the sum of its components' nullities, so ``is_parabolic()`` -- total nullity one
-- does not name a boundary ray of Type II, which contributes several affine
components.  ``is_parabolic_union()`` states that union explicitly and leaves
``is_parabolic()`` alone; these cases pin both, the exclusions, and the
maximal-subdiagram queries built on them.
"""

from sage_extensions.all import CoxeterDiagrams, Sterk

_TYPE_TWO_INVENTORY = {"Sterk_1": 3, "Sterk_2": 0, "Sterk_3": 3, "Sterk_4": 1, "Sterk_5": 9}


def union(*labels):
    r"""The disjoint union of the diagrams of the Cartan type labels."""
    blocks = [CoxeterDiagrams()(list(label)) for label in labels]
    rows = []
    for index, block in enumerate(blocks):
        for left in block.index_set():
            row = []
            for other_index, other in enumerate(blocks):
                for right in other.index_set():
                    if other_index != index:
                        row.append(2)
                    elif left == right:
                        row.append(1)
                    else:
                        row.append(block.coxeter_entry(left, right))
            rows.append(row)
    return CoxeterDiagrams()(rows)


def test_a_union_of_affine_components_is_a_different_predicate_from_nullity_one() -> None:
    r"""``E_7^{(1)} + A_1^{(1)}`` and ``B_4^{(1)} + B_4^{(1)}`` are unions, not parabolic diagrams."""
    for name, diagram in {
        "affine E7 + affine A1": union(["E", 7, 1], ["A", 1, 1]),
        "affine B4 + affine B4": union(["B", 4, 1], ["B", 4, 1]),
    }.items():
        assert diagram.is_parabolic() is False, name
        assert diagram.is_parabolic_union() is True, name

        components = tuple(diagram.connected_component_vertex_sets())
        assert len(components) == 2, name
        assert all(diagram.induced_subdiagram(tuple(component)).is_parabolic() for component in components), name


def test_a_single_affine_component_keeps_the_nullity_one_predicate() -> None:
    r"""The connected affine family is not reinterpreted: one component is not a union."""
    for label in (["E", 7, 1], ["A", 1, 1], ["B", 4, 1]):
        diagram = CoxeterDiagrams()(list(label))
        assert diagram.is_parabolic() is True, label
        assert diagram.is_parabolic_union() is False, label


def test_finite_components_are_excluded_from_the_affine_union_contract() -> None:
    r"""Every component must be affine; finite ones are elliptic, not parabolic."""
    for name, diagram in {
        "finite E7 + finite A1": union(["E", 7], ["A", 1]),
        "affine E7 + finite A1": union(["E", 7, 1], ["A", 1]),
        "finite E7 + affine A1": union(["E", 7], ["A", 1, 1]),
    }.items():
        assert diagram.is_parabolic_union() is False, name
        assert len(tuple(diagram.connected_component_vertex_sets())) == 2, name


def test_the_maximal_affine_union_of_a_pure_union_is_the_diagram_itself() -> None:
    diagram = union(["E", 7, 1], ["A", 1, 1])

    maximal = tuple(diagram.maximal_parabolic_union_subdiagrams())
    assert len(maximal) == 1
    assert maximal[0].arrow().codomain() is diagram
    assert frozenset(maximal[0].index_set()) == frozenset(diagram.index_set())
    assert maximal[0].is_parabolic_union()


def test_maximality_is_decided_before_the_rank_cap() -> None:
    r"""A cap removes maximal members; it never promotes a contained subdiagram."""
    diagram = union(["E", 7, 1], ["A", 1, 1])
    assert int(diagram.cardinality()) == 10

    capped_below = tuple(diagram.maximal_parabolic_union_subdiagrams(max_rank=9))
    assert capped_below == ()
    assert len(tuple(diagram.maximal_parabolic_union_subdiagrams(max_rank=10))) == 1

    # Over the whole Sterk inventory the capped query is exactly the uncapped
    # one filtered by rank, which is what deciding maximality first means.
    diagram = Sterk.diagrams()["Sterk_5"]
    uncapped = tuple(diagram.maximal_parabolic_union_subdiagrams())
    capped = tuple(diagram.maximal_parabolic_union_subdiagrams(max_rank=10))
    assert capped == tuple(entry for entry in uncapped if int(entry.cardinality()) <= 10)
    assert 0 < len(capped) < len(uncapped)


def test_the_generic_maximal_subdiagram_query_takes_a_vertex_decision() -> None:
    r"""Any condition stated on vertex sets gets the same enumeration and cap."""
    diagram = CoxeterDiagrams()(["A", 3])
    assert int(diagram.cardinality()) == 3

    maximal = tuple(diagram.maximal_subdiagrams(lambda vertices: len(vertices) <= 2))
    assert len(maximal) == 3
    assert all(int(entry.cardinality()) == 2 for entry in maximal)
    assert tuple(diagram.maximal_subdiagrams(lambda vertices: len(vertices) <= 2, max_rank=1)) == ()


def test_the_five_sterk_diagrams_have_their_type_two_inventory() -> None:
    r"""The maximal affine unions of each Sterk diagram, with their retained data."""
    diagrams = Sterk.diagrams()

    for name, expected in _TYPE_TWO_INVENTORY.items():
        diagram = diagrams[name]
        parent_gram = diagram.root_gram_tensor()
        ranking = diagram.index_set().ranking_map()
        maximal = tuple(diagram.maximal_parabolic_union_subdiagrams())

        assert len(maximal) == expected, (name, [entry.index_set() for entry in maximal])
        vertex_sets = tuple(frozenset(entry.index_set()) for entry in maximal)
        assert not any(left < right for left in vertex_sets for right in vertex_sets), name

        for entry in maximal:
            assert entry.is_parabolic_union(), name
            assert entry.is_connected() is False, name
            assert entry.arrow().codomain() is diagram, name

            selected = tuple(entry.index_set())
            positions = tuple(int(ranking(label)) for label in selected)
            assert all(label in diagram.index_set() for label in selected), name
            assert tuple(entry.vertex_names()) == tuple(
                diagram.vertex_names()[position] for position in positions
            ), name
            entry_gram = entry.root_gram_tensor()
            for row, left in enumerate(selected):
                for column, right in enumerate(selected):
                    assert entry.coxeter_entry(left, right) == diagram.coxeter_entry(left, right), name
                    assert entry_gram[row, column] == parent_gram[positions[row], positions[column]], name

            # Every connected component of the union is affine, read through
            # the maintained connected classification.
            components = tuple(entry.connected_component_vertex_sets())
            assert len(components) >= 2, name
            assert all(
                entry.induced_subdiagram(tuple(component)).is_parabolic()
                for component in components
            ), name


def test_a_single_affine_component_satisfies_the_componentwise_contract() -> None:
    r"""``is_componentwise_affine()`` is the complete contract; the union predicate stays as documented."""
    for label in (["E", 7, 1], ["A", 1, 1], ["B", 4, 1]):
        diagram = CoxeterDiagrams()(list(label))
        assert diagram.is_componentwise_affine() is True, label
        assert diagram.is_parabolic_union() is False, label
        assert int(diagram.form_rank()) == int(diagram.cardinality()) - 1, label


def test_componentwise_affine_excludes_finite_components() -> None:
    for name, diagram in {
        "finite A2": CoxeterDiagrams()(["A", 2]),
        "finite E7 + finite A1": union(["E", 7], ["A", 1]),
        "affine E7 + finite A1": union(["E", 7, 1], ["A", 1]),
    }.items():
        assert diagram.is_componentwise_affine() is False, name


def test_maximality_is_global_across_the_componentwise_affine_family() -> None:
    r"""An affine component inside a larger affine union is not maximal."""
    diagram = union(["E", 7, 1], ["A", 1, 1], ["A", 2])

    maximal = tuple(diagram.maximal_componentwise_affine_subdiagrams())
    assert len(maximal) == 1
    assert int(maximal[0].cardinality()) == 10
    assert int(maximal[0].form_rank()) == 8
    assert maximal[0].is_componentwise_affine()
    assert maximal[0].is_parabolic_union()
    assert maximal[0].arrow().codomain() is diagram


def test_the_form_rank_cap_is_geometric_not_the_vertex_count() -> None:
    r"""A union of three affine components has two more vertices than form rank."""
    diagram = union(["E", 7, 1], ["A", 1, 1], ["A", 1, 1])
    assert int(diagram.cardinality()) == 12
    assert int(diagram.form_rank()) == 9

    # Selecting by vertex count truncates the geometric rank by two here: the
    # rank-nine form is twelve vertices wide, so a vertex cap of eleven loses it.
    assert tuple(diagram.maximal_componentwise_affine_subdiagrams(max_rank=11)) == ()
    capped = tuple(diagram.maximal_componentwise_affine_subdiagrams(max_form_rank=9))
    assert len(capped) == 1 and int(capped[0].form_rank()) == 9
    assert tuple(diagram.maximal_componentwise_affine_subdiagrams(max_form_rank=8)) == ()

    union_of_two = union(["E", 7, 1], ["A", 1, 1])
    assert int(union_of_two.cardinality()) == 10
    assert int(union_of_two.form_rank()) == 8


def test_the_generic_query_passes_labels_not_positions() -> None:
    r"""The documented boundary is the vertex labels, which need not be integers."""
    from sage_extensions.categories.coxeter_diagrams import _owned_coxeter_matrix
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

    vertices = finite_ordered_set(("x", "y", "z"))
    entries = {
        (left, right): 1 if left == right else 3 for left in vertices for right in vertices
    }
    diagram = CoxeterDiagrams().from_coxeter_matrix(_owned_coxeter_matrix(vertices, entries))
    assert tuple(diagram.index_set()) == ("x", "y", "z")

    received = []

    def predicate(labels):
        received.append(tuple(labels))
        return len(labels) == 2

    maximal = tuple(diagram.maximal_subdiagrams(predicate))
    assert all(all(isinstance(label, str) for label in labels) for labels in received)
    assert tuple(diagram.index_set()) in received
    assert len(maximal) == 3
    assert {tuple(entry.index_set()) for entry in maximal} == {("x", "y"), ("x", "z"), ("y", "z")}
