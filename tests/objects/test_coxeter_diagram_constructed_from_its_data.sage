from sage_extensions.all import *


def a2_rows():
    r"""The Coxeter matrix of $A_2$ written as its rows."""
    return CoxeterDiagrams()([[1, 3], [3, 1]])


def test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_rows() -> None:
    r"""An object of a category is that category applied to its defining data.

    A label names a Coxeter matrix up to the numbering of its simple roots, so
    the diagram of the label and the diagram of the rows of that matrix are one
    diagram: $m$ is $@[ext]$ (Mathlib, ``Mathlib/GroupTheory/Coxeter/Matrix.lean``,
    ``structure CoxeterMatrix``), equal exactly when the entries are.
    """
    assert CoxeterDiagrams()(["A", 2]) == a2_rows()
    assert a2_rows() == CoxeterDiagrams()(["A", 2])
    assert CoxeterDiagrams()(["E", 6]) == CoxeterDiagrams()(
        CoxeterDiagrams()(["E", 6]).coxeter_matrix()
    )
    assert a2_rows() != CoxeterDiagrams()([[1, 4], [4, 1]])


def test_the_affine_a2_triangle_is_the_three_by_three_matrix() -> None:
    r"""Every pair of the three mirrors meets at $\pi/3$: the affine $A_2$ triangle.

    Its Schlaefli form is positive semidefinite of radical one, so the diagram
    is parabolic rather than elliptic (Humphreys, 2.5), and it is the diagram
    of the affine label ``["A", 2, 1]``.
    """
    triangle = CoxeterDiagrams()([[1, 3, 3], [3, 1, 3], [3, 3, 1]])
    assert triangle.is_connected()
    assert triangle.is_parabolic()
    assert triangle.form_rank() == 2
    assert triangle.zero_inertia_index() == 1
    assert CoxeterDiagrams()(["A", 2, 1]) == triangle


def test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_simple_roots() -> None:
    r"""$A_2$: the label, its rows and its simple roots place the mirrors on one vertex set.

    The pairings of the simple roots of the root lattice of $A_2$ determine
    $m_{12}=3$ (Humphreys, *Reflection Groups and Coxeter Groups*, 2.1), which
    is what the label names.
    """
    unrooted = CoxeterDiagrams()(["A", 2])
    rooted = CoxeterDiagrams().from_roots(Lattices(ZZ)("A2").module_generators())
    assert unrooted.index_set() == rooted.index_set()
    assert unrooted.coxeter_entry(0, 1) == rooted.coxeter_entry(0, 1) == 3
    assert unrooted != rooted


def test_the_retained_datum_is_the_family_of_entries() -> None:
    r"""The stored datum is $m\colon V\times V\to\mathrm{Card}$, read back entry by entry."""
    diagram = a2_rows()
    matrix = diagram.coxeter_matrix()
    assert matrix.value((0, 0)) == 1
    assert matrix.value((0, 1)) == 3
    assert matrix.value((1, 0)) == 3
    assert diagram.coxeter_entry(0, 1) in Cardinalities()
    assert CoxeterDiagrams()(matrix) == diagram


def test_the_diagram_is_a_labelled_graph_on_its_vertices() -> None:
    r"""The underlying graph joins exactly the pairs with $m_{vw}\neq 2$, labelled $m_{vw}$.

    This is the graph of the definition (Bourbaki, *Groupes et algebres de Lie*
    IV.1.9): the vertices are the mirrors and the bond is the order of the
    product of the two reflections.
    """
    diagram = CoxeterDiagrams()([[1, 3, 2], [3, 1, 2], [2, 2, 1]])
    assert diagram in LabelledGraphs()
    assert diagram.vertices() == diagram.index_set()
    assert diagram.edges().cardinality() == 1
    assert diagram.edge_label(0, 1) == 3
    assert all(
        diagram.coxeter_entry(left, right) != 2
        for left, right in diagram.edges()
    )
    assert diagram.graph() in LabelledGraphs()


def test_a_rooted_diagram_is_its_roots() -> None:
    r"""Two realizations by roots with one matrix are distinct diagrams.

    Twisting the root lattice by 2 multiplies every root square by 2, which
    leaves $4b^2/(q_1q_2)$ and so $m$ unchanged; the roots are a chosen datum
    on the diagram, not a property of it (``CAT-17``).
    """
    short = CoxeterDiagrams().from_roots(Lattices(ZZ)("A2").module_generators())
    tall = CoxeterDiagrams().from_roots(
        Lattices(ZZ)("A2").twist(2).module_generators()
    )
    assert short.coxeter_matrix() == tall.coxeter_matrix()
    assert short.root(0) != tall.root(0)
    assert short != tall


def test_the_rooted_diagrams_are_a_data_subcategory() -> None:
    r"""A rooted diagram is constructed with its roots and retains them."""
    rooted = CoxeterDiagrams().Rooted()
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)
    assert diagram in rooted
    assert diagram.roots().cardinality() == 2
    assert diagram.root(0) == Lattices(ZZ)("A2").module_generators().value(0)
    assert diagram.coxeter_matrix() == a2_rows().coxeter_matrix()
    assert a2_rows() not in rooted
    assert rooted.an_object() in rooted
