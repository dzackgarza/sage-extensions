r"""The Coxeter diagram of a configuration of roots, and the Schläfli form it retains.

For roots \(r_1,\dots,r_n\) of square \(-2\) the Schläfli matrix \(2\,\delta_{ij} - 2\cos(\pi/m_{ij})\)
is \(-b(r_i,r_j)\), so its determinant is \((-1)^n\det b\) and its inertia is that of \(-b\).

- The simple roots of \(D_4\) (\(\det = 4\), Conway--Sloane, SPLAG, Ch. 1, section 1.4)
  give Schläflian \(4\) and inertia \((4,0,0)\); the diagram is connected, and two
  adjacent vertices induce \(A_2\), which is elliptic.  Its automorphisms permute the three
  outer nodes, a group of order 6.
- The roots \(r_0,r_1,r_2\) with pairwise products \(1\) give the triangle \(\tilde A_2\):
  \(-b\) has eigenvalues \(3,3,0\), so the Schläflian is \(0\) and the inertia \((2,0,1)\);
  each edge is \(A_2\), of Schläflian 3.
- The simple roots of \(B_3\) in \(\mathbb{Z}^3\) have root scale \(1/2\), and their reference
  diagram is the \(B_3\) root basis at that scale.
- Two roots with \(b(r,s)=3\) have \(b^2 > q(r)q(s)\): their mirrors diverge, the bond is
  \(\infty\), and \(-b\) has one positive and one negative eigenvalue.
"""

from sage_extensions.all import *


def test_the_diagram_of_the_simple_roots_of_d4() -> None:
    lattice = Lattices(ZZ)("D4")
    diagram = CoxeterDiagrams().from_roots(lattice.module_generators())

    assert diagram.is_elliptic()
    assert not diagram.is_parabolic()
    assert not diagram.is_hyperbolic()
    assert diagram.is_connected()
    for root in diagram.roots():
        assert root.q() == -2
    for left in diagram.vertices():
        for right in diagram.vertices():
            if diagram.coxeter_entry(left, right) == 3:
                assert diagram.induced_subdiagram((left, right)).is_elliptic()


def test_the_schlaeflian_and_inertia_of_the_d4_diagram() -> None:
    diagram = CoxeterDiagrams().from_roots(Lattices(ZZ)("D4").module_generators())

    assert diagram.schlaflian() == 4
    assert diagram.positive_inertia_index() == 4
    assert diagram.negative_inertia_index() == 0
    assert diagram.zero_inertia_index() == 0


def test_the_automorphisms_of_the_d4_diagram_permute_its_three_outer_nodes() -> None:
    diagram = CoxeterDiagrams().from_roots(Lattices(ZZ)("D4").module_generators())

    assert diagram.Aut().order() == 6


def test_three_mutually_bonded_roots_give_the_affine_triangle() -> None:
    lattice = Lattices(ZZ)([[-2, 1, 1], [1, -2, 1], [1, 1, -2]])
    diagram = CoxeterDiagrams().from_roots(lattice.module_generators())

    assert diagram.is_parabolic()
    assert not diagram.is_elliptic()
    for edge in diagram.maximal_elliptic_subdiagrams():
        assert edge.is_elliptic()
        assert not edge.is_parabolic()


def test_the_schlaeflian_and_inertia_of_the_affine_triangle() -> None:
    lattice = Lattices(ZZ)([[-2, 1, 1], [1, -2, 1], [1, 1, -2]])
    diagram = CoxeterDiagrams().from_roots(lattice.module_generators())

    assert diagram.schlaflian() == 0
    assert diagram.positive_inertia_index() == 2
    assert diagram.zero_inertia_index() == 1
    for edge in diagram.maximal_elliptic_subdiagrams():
        assert edge.schlaflian() == 3


def test_two_roots_with_divergent_mirrors_give_a_hyperbolic_bond() -> None:
    lattice = Lattices(ZZ)([[-2, 3], [3, -2]])
    diagram = CoxeterDiagrams().from_roots(lattice.module_generators())

    assert diagram.is_hyperbolic()
    assert not diagram.is_elliptic()
    for left in diagram.vertices():
        for right in diagram.vertices():
            if left != right:
                assert diagram.coxeter_entry(left, right) == Infinity


def test_the_inertia_of_two_roots_with_divergent_mirrors() -> None:
    diagram = CoxeterDiagrams().from_roots(Lattices(ZZ)([[-2, 3], [3, -2]]).module_generators())

    assert diagram.positive_inertia_index() == 1
    assert diagram.negative_inertia_index() == 1


def test_a_b3_root_basis_of_scale_one_half_has_the_b3_type_diagram() -> None:
    # The simple roots e1 - e2, e2 - e3, e3 of B3 in the standard lattice ZZ^3
    # (Humphreys, Introduction to Lie Algebras and Representation Theory, 12.1)
    # have squares 2, 2, 1, so the root scale is 1/2 and the diagram of the type
    # is the B3 root basis twisted to shortest square 1.
    lattice = Lattices(ZZ)([[2, -1, 0], [-1, 2, -1], [0, -1, 1]])
    diagram = CoxeterDiagrams().from_roots(lattice.module_generators())

    assert diagram.root_scale().parent() is QQ
    assert diagram.root_scale() == QQ(1) / QQ(2)
    assert diagram.label() == "B3"
    reference = diagram.scaled_cartan_type()
    assert reference.root_scale().parent() is QQ
    assert reference.root_scale() == QQ(1) / QQ(2)
    assert reference.coxeter_matrix() == diagram.coxeter_matrix()
