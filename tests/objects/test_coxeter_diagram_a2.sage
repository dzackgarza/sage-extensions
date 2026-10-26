from sage_extensions.all import *


def diagram():
    return CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)


def test_the_category_applied_to_the_cartan_type_agrees() -> None:
    r"""The unrooted diagram of the label, compared with the unrooted diagram of its own Coxeter matrix."""
    unrooted = CoxeterDiagrams()(["A", 2])
    assert unrooted == CoxeterDiagrams()(unrooted.coxeter_matrix())
    assert unrooted != diagram()


def test_the_category_applied_to_the_roots_agrees() -> None:
    r"""$A_2$: two nodes with $m_{12} = 3$; the rooted diagram of its simple roots."""
    roots = Lattices(ZZ)("A2").module_generators()
    assert CoxeterDiagrams()(roots) == CoxeterDiagrams().from_roots(roots)


def test_the_categories_of_the_diagram() -> None:
    assert diagram() in CoxeterDiagrams()
    assert diagram() in Sets()


def test_the_shape_of_the_diagram() -> None:
    graph = diagram()
    assert graph.num_vertices() == 2
    first, second = graph.vertices()
    assert graph.coxeter_entry(first, first) == 1
    assert graph.coxeter_entry(first, second) == 3
    assert graph.is_connected()
    assert graph.is_rooted()


def test_a2_is_spherical() -> None:
    r"""The cosine matrix $\begin{pmatrix}1&-1/2\\-1/2&1\end{pmatrix}$ is positive definite."""
    graph = diagram()
    assert graph.is_elliptic()
    assert not graph.is_parabolic()
    assert not graph.is_hyperbolic()
    assert graph.positive_inertia_index() == 2
    assert graph.negative_inertia_index() == 0
    assert graph.zero_inertia_index() == 0


def test_the_coxeter_group_of_a2_is_s3() -> None:
    group = diagram().coxeter_group()
    assert group.order() == 6
    assert group.is_isomorphic_to(Groups.S(3))


def test_the_diagram_automorphisms_of_a2() -> None:
    r"""The only nontrivial symmetry exchanges the two nodes."""
    assert diagram().Aut().order() == 2


def test_the_root_lattice_of_a2() -> None:
    assert diagram().root_lattice().is_isometric(Lattices(ZZ)("A2"))
