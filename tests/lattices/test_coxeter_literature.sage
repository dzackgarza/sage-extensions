r"""Literature values for Coxeter diagrams, their groups and their Schlaeflians.

Sources:

* Humphreys, *Reflection Groups and Coxeter Groups* (1990): Table 2.4 (orders
  and degrees of the finite irreducible groups), 2.10 (the classification),
  3.19 (\(\ell(w_0)\) is the number of positive roots), 4.7 (the affine
  diagrams), 6.4 (a Coxeter group is finite exactly when its Schlaefli form
  is positive definite).
* Bourbaki, *Lie Groups and Lie Algebras* Ch. VI, Plates I--IX: determinants
  of the Cartan matrices (\(A_n\): \(n+1\); \(B_n\), \(C_n\): \(2\); \(D_n\): \(4\);
  \(E_n\): \(9-n\); \(F_4\), \(G_2\): \(1\)) and the root counts.

The Schlaefli matrix is \(C_{vv}=2\), \(C_{vw}=-2\cos(\pi/m_{vw})\), and the
Schlaeflian is \(\det C\).  Diagrams are given by their Coxeter matrices; a
bracket symbol \([p_1,\dots,p_k]\) names the path whose consecutive bonds are
the \(p_i\).  Two corrections the archived specification recorded are kept:
\(\operatorname{Aut}\) of the \(A_4\) diagram is \(\mathbb Z/2\) (path
reversal), and \([4,3]\), \([3,4]\) are two labellings of one Coxeter graph.
"""

import pytest

from sage_extensions.all import *


def coxeter_matrix(rank: int, bonds: dict) -> list[list[int]]:
    r"""The Coxeter matrix on ``rank`` nodes with the given bonds and \(2\) elsewhere."""
    return [
        [1 if i == j else bonds.get((min(i, j), max(i, j)), 2) for j in range(rank)]
        for i in range(rank)
    ]


def bracket(*bonds: int):
    r"""The diagram of the bracket symbol \([p_1,\dots,p_k]\): the path on the nodes \(0,\dots,k\)."""
    path = {(i, i + 1): bond for i, bond in enumerate(bonds)}
    last_node = max(right for _left, right in path)
    return CoxeterDiagrams()(coxeter_matrix(last_node + 1, path))


def type_d(rank: int):
    r"""\(D_n\): the path on nodes \(0,\dots,n-2\) with node \(n-1\) joined to node \(n-3\)."""
    bonds = {(i, i + 1): 3 for i in range(rank - 2)}
    bonds[(rank - 3, rank - 1)] = 3
    return CoxeterDiagrams()(coxeter_matrix(rank, bonds))


def type_e(rank: int):
    r"""\(E_n\): the path on nodes \(0,\dots,n-2\) with node \(n-1\) joined to node \(2\)."""
    bonds = {(i, i + 1): 3 for i in range(rank - 2)}
    bonds[(2, rank - 1)] = 3
    return CoxeterDiagrams()(coxeter_matrix(rank, bonds))


FINITE = {
    "A2": lambda: bracket(3),
    "B2": lambda: bracket(4),
    "H2": lambda: bracket(5),
    "G2": lambda: bracket(6),
    "A3": lambda: bracket(3, 3),
    "A4": lambda: bracket(3, 3, 3),
    "B3": lambda: bracket(4, 3),
    "H3": lambda: bracket(5, 3),
    "D4": lambda: type_d(4),
    "F4": lambda: bracket(3, 4, 3),
    "H4": lambda: bracket(5, 3, 3),
    "E6": lambda: type_e(6),
    "E7": lambda: type_e(7),
    "E8": lambda: type_e(8),
}

AFFINE = {
    "A2~": coxeter_matrix(3, {(0, 1): 3, (1, 2): 3, (0, 2): 3}),
    "B3~": coxeter_matrix(4, {(0, 2): 3, (1, 2): 3, (2, 3): 4}),
    "C3~": coxeter_matrix(4, {(0, 1): 4, (1, 2): 3, (2, 3): 4}),
    "D4~": coxeter_matrix(5, {(0, 1): 3, (0, 2): 3, (0, 3): 3, (0, 4): 3}),
    "E6~": coxeter_matrix(
        7, {(0, 1): 3, (1, 2): 3, (0, 3): 3, (3, 4): 3, (0, 5): 3, (5, 6): 3}
    ),
    "E7~": coxeter_matrix(8, {**{(i, i + 1): 3 for i in range(6)}, (3, 7): 3}),
    "E8~": coxeter_matrix(9, {**{(i, i + 1): 3 for i in range(7)}, (2, 8): 3}),
    "F4~": coxeter_matrix(5, {(0, 1): 3, (1, 2): 3, (2, 3): 4, (3, 4): 3}),
    "G2~": coxeter_matrix(3, {(0, 1): 3, (1, 2): 6}),
}


def type_b_root_gram(rank: int) -> list[list[int]]:
    r"""\(B_n\) simple roots: \(n-1\) long roots of square \(-4\), then one short root of square \(-2\)."""
    return [
        [
            (-2 if i == rank - 1 else -4) if i == j else (2 if abs(i - j) == 1 else 0)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def type_c_root_gram(rank: int) -> list[list[int]]:
    r"""\(C_n\) simple roots: \(n-1\) short roots of square \(-2\), then one long root of square \(-4\)."""
    return [
        [
            (-4 if i == rank - 1 else -2)
            if i == j
            else ((2 if max(i, j) == rank - 1 else 1) if abs(i - j) == 1 else 0)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


@pytest.mark.parametrize(
    "bonds,order",
    [((3,), 6), ((4,), 8), ((5,), 10), ((6,), 12), ((3, 3), 24), ((4, 3), 48), ((5, 3), 120)],
)
def test_a_bracket_symbol_names_an_elliptic_diagram_of_the_tabulated_order(bonds, order) -> None:
    r"""\([3],[4],[5],[6],[3,3],[4,3],[5,3]\) have groups of orders \(6,8,10,12,24,48,120\) (Humphreys 2.4)."""
    diagram = bracket(*bonds)

    assert diagram.is_connected()
    assert diagram.is_elliptic()
    assert diagram.coxeter_group().cardinality() == order


def test_the_two_labellings_of_the_rank_three_double_bond_present_one_group() -> None:
    r"""\([4,3]\) and \([3,4]\) differ as labelled diagrams and present one group of order \(48\), Schlaeflian \(2\)."""
    first = bracket(4, 3)
    second = bracket(3, 4)

    assert first.coxeter_matrix() != second.coxeter_matrix()
    assert first.coxeter_group().cardinality() == 48
    assert first.coxeter_group().is_isomorphic(second.coxeter_group())
    assert first.schlaflian() == second.schlaflian() == 2


@pytest.mark.parametrize(
    "name,rank,order", [("A2", 2, 6), ("B2", 2, 8), ("G2", 2, 12), ("H3", 3, 120)]
)
def test_the_coxeter_presentation_has_one_generator_per_mirror(name, rank, order) -> None:
    r"""\(\langle s_v \mid s_v^2,\ (s_vs_w)^{m_{vw}}\rangle\) presents \(W\): \(A_2,B_2,G_2,H_3\) of orders \(6,8,12,120\)."""
    group = FINITE[name]().coxeter_group()

    assert group.group_generators().cardinality() == rank
    assert group.cardinality() == order


@pytest.mark.parametrize("rank", [1, 2, 3, 4])
def test_the_coxeter_group_of_type_a_is_the_symmetric_group(rank) -> None:
    r"""\(W(A_n)\cong S_{n+1}\), of order \((n+1)!\) (Humphreys 1.1)."""
    group = CoxeterDiagrams()(
        coxeter_matrix(rank, {(i, i + 1): 3 for i in range(rank - 1)})
    ).coxeter_group()

    assert group.cardinality() == factorial(rank + 1)
    assert group.is_isomorphic(Groups.S(rank + 1))


@pytest.mark.parametrize("rank", [2, 3, 4])
def test_the_weyl_groups_of_types_b_and_c_coincide(rank) -> None:
    r"""\(W(B_n)\cong W(C_n)\), of order \(2^n n!\) (Humphreys 1.1, 2.4).

    The root systems differ -- \(B_n\) has one short simple root, \(C_n\) one
    long one -- but their mirrors generate isomorphic reflection groups.
    """
    b_group = CoxeterDiagrams()(Lattices(ZZ)(type_b_root_gram(rank)).module_generators()).coxeter_group()
    c_group = CoxeterDiagrams()(Lattices(ZZ)(type_c_root_gram(rank)).module_generators()).coxeter_group()

    assert b_group.cardinality() == 2**rank * factorial(rank)
    assert b_group.is_isomorphic(c_group)


def classical(family: str, rank: int):
    r"""The classical diagram \(A_n\), \(B_n\) (\([4,3,\dots,3]\)) or \(D_n\)."""
    if family == "D":
        return type_d(rank)
    head = [4] if family == "B" else [3]
    return CoxeterDiagrams()(
        coxeter_matrix(rank, {(i, i + 1): (head + [3] * rank)[i] for i in range(rank - 1)})
    )


@pytest.mark.parametrize(
    "family,rank,schlaeflian",
    [("A", n, n + 1) for n in range(1, 7)]
    + [("B", n, 2) for n in range(2, 7)]
    + [("D", n, 4) for n in range(4, 7)],
)
def test_a_classical_finite_type_is_elliptic_of_the_tabulated_schlaeflian(family, rank, schlaeflian) -> None:
    r"""\(A_n\), \(B_n\), \(D_n\) are positive definite with Schlaeflians \(n+1\), \(2\), \(4\) (Bourbaki VI, Plates I--IV)."""
    diagram = classical(family, rank)

    assert diagram.cardinality() == rank
    assert diagram.is_elliptic()
    assert diagram.negative_inertia_index() == 0
    assert diagram.zero_inertia_index() == 0
    assert diagram.schlaflian() == schlaeflian


@pytest.mark.parametrize(
    "name,schlaeflian",
    [("E6", 3), ("E7", 2), ("E8", 1), ("F4", 1), ("G2", 1), ("H3", None), ("H4", None)],
)
def test_an_exceptional_finite_type_is_elliptic_of_the_tabulated_schlaeflian(name, schlaeflian) -> None:
    r"""\(E_6,E_7,E_8,F_4,G_2\) have Schlaeflians \(3,2,1,1,1\); \(H_3,H_4\) are elliptic (Bourbaki VI, Plates V--IX)."""
    diagram = FINITE[name]()

    assert diagram.is_elliptic()
    if schlaeflian is not None:
        assert diagram.schlaflian() == schlaeflian


@pytest.mark.parametrize("bond,schlaeflian", [(3, 3), (4, 2), (6, 1)])
def test_the_rank_two_schlaeflian_is_four_sine_squared(bond, schlaeflian) -> None:
    r"""\(\det C = 4 - 4\cos^2(\pi/p) = 4\sin^2(\pi/p)\): \(3, 2, 1\) for \(p = 3, 4, 6\)."""
    assert bracket(bond).schlaflian() == schlaeflian


def test_the_rank_two_schlaeflian_of_the_pentagon_is_five_minus_root_five_over_two() -> None:
    r"""\(4\sin^2(\pi/5) = (5-\sqrt5)/2\), the smaller root of \(s^2-5s+5\)."""
    s = bracket(5).schlaflian()

    assert s.parent() is AA
    assert s**2 - 5 * s + 5 == 0
    assert 1 < s < 2


@pytest.mark.parametrize("name,order", [("F4", 1152), ("G2", 12), ("H3", 120)])
def test_an_exceptional_finite_group_has_the_tabulated_order(name, order) -> None:
    r"""\(|W(F_4)| = 1152\), \(|W(G_2)| = 12\), \(|W(H_3)| = 120\) (Humphreys 2.4)."""
    assert FINITE[name]().coxeter_group().cardinality() == order


@pytest.mark.parametrize(
    "name,vertices,edges,automorphisms",
    [("A4", 4, 3, 2), ("D4", 4, 3, 6), ("E8", 8, 7, 1)],
)
def test_diagram_automorphism_groups_match_the_literature(name, vertices, edges, automorphisms) -> None:
    r"""\(\operatorname{Aut}\) of \(A_4\), \(D_4\), \(E_8\): path reversal \(\mathbb Z/2\), triality \(S_3\), trivial."""
    diagram = FINITE[name]()
    assert diagram.cardinality() == vertices
    assert diagram.graph().edges().cardinality() == edges
    assert diagram.Aut().cardinality() == automorphisms


@pytest.mark.parametrize("name", AFFINE)
def test_an_affine_diagram_is_parabolic_with_vanishing_schlaeflian(name) -> None:
    r"""Each affine diagram (Humphreys 4.7) is positive semidefinite with a one-dimensional radical."""
    diagram = CoxeterDiagrams()(AFFINE[name])

    assert diagram.is_connected()
    assert diagram.is_parabolic()
    assert not diagram.is_elliptic()
    assert diagram.schlaflian() == 0
    assert diagram.zero_inertia_index() == 1
    assert diagram.negative_inertia_index() == 0


def test_icosahedral_root_lattices_live_over_the_golden_integer_ring() -> None:
    r"""The \(H_3\), \(H_4\) root systems have \(30\), \(120\) roots and Coxeter numbers \(10\), \(30\) (Humphreys 2.4).

    Their roots lie over \(\mathbb Z[(1+\sqrt5)/2]\), whose fraction field
    \(\mathbb Q(\sqrt5)\) has discriminant \(5\).
    """
    h3 = Lattices.root_lattice("H", 3)
    h4 = Lattices.root_lattice("H", 4)

    assert h3.base_ring().fraction_field().degree() == 2
    assert h3.base_ring().fraction_field().discriminant() == 5
    assert h3.module_rank() == 3
    assert h4.module_rank() == 4
    assert h3.roots().cardinality() == 30
    assert h4.roots().cardinality() == 120
    assert h3.coxeter_number() == 10
    assert h4.coxeter_number() == 30


@pytest.mark.parametrize(
    "name,order,coxeter_number",
    [("E6", 51840, 12), ("E7", 2903040, 18), ("E8", 696729600, 30), ("F4", 1152, 12), ("H4", 14400, 30)],
)
def test_the_group_order_is_the_product_of_the_invariant_degrees(name, order, coxeter_number) -> None:
    r"""\(|W| = \prod d_i\) and \(h = \max d_i\) (Humphreys 3.9, 3.19, Table 3.1)."""
    degrees = FINITE[name]().coxeter_group().degrees()
    product = 1
    for degree in degrees:
        product *= degree

    assert product == order
    assert max(degrees) == coxeter_number


@pytest.mark.parametrize(
    "name,length",
    [("A3", 6), ("B3", 9), ("D4", 12), ("G2", 6), ("H3", 15), ("H2", 5)],
)
def test_the_longest_element_has_one_step_per_positive_root(name, length) -> None:
    r"""\(\ell(w_0) = |\Phi^+|\): \(A_3\) \(6\), \(B_3\) \(9\), \(D_4\) \(12\), \(G_2\) \(6\), \(H_3\) \(15\), \(I_2(5)\) \(5\) (Humphreys 1.8)."""
    assert FINITE[name]().coxeter_group().long_element().length() == length


@pytest.mark.parametrize(
    "name,root_count,coxeter_number", [("A3", 12, 4), ("D4", 24, 6), ("E6", 72, 12)]
)
def test_root_counts_positive_roots_and_highest_root_heights(name, root_count, coxeter_number) -> None:
    r"""\(|\Phi| = nh\), half of it positive, and the highest root has height \(h-1\) (Bourbaki VI, 1.11)."""
    lattice = Lattices(ZZ)(name)
    roots = lattice.roots()
    positive = roots.condition_set(lambda root: root.is_positive_root())

    assert roots.cardinality() == root_count
    assert positive.cardinality() == root_count // 2
    assert lattice.coxeter_number() == coxeter_number
    assert lattice.highest_root().height() == coxeter_number - 1
