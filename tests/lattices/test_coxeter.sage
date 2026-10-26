r"""Coxeter bonds read from root pairings.

Two roots \(r,s\) with \(q(r),q(s)<0\) span mirrors meeting at angle
\(\pi/m\) where \(\cos^2(\pi/m) = b(r,s)^2/(q(r)q(s))\); the value \(1\) is
the bond \(m=\infty\) with parallel mirrors, and a value above \(1\) is
\(m=\infty\) with ultraparallel mirrors (Vinberg, *Hyperbolic reflection
groups*, Russian Math. Surveys 40 (1985), §1).
"""

from sage_extensions.all import *


def test_the_simple_roots_of_a2_give_a_single_bond_and_the_symmetric_group_on_three_letters() -> None:
    r"""Gram \([[-2,1],[1,-2]]\): \(\cos^2 = 1/4\), so \(\cos(\pi/m)=1/2\) and \(m=3\); \(W\cong S_3\)."""
    lattice = Lattices(ZZ)([[-2, 1], [1, -2]])
    diagram = CoxeterDiagrams()(lattice.module_generators())
    vertices = diagram.index_set()

    assert diagram.coxeter_entry(vertices[0], vertices[1]) == 3
    assert diagram.is_elliptic()
    assert diagram.coxeter_group().cardinality() == 6


def test_a_double_bond_and_a_parallel_pair_are_read_from_the_root_pairing() -> None:
    r"""Gram \([[-2,2],[2,-4]]\) gives \(\cos^2 = 4/8\), \(m=4\); Gram \([[-2,2],[2,-2]]\) gives \(m=\infty\).

    The first pair generates the dihedral group of order \(8\); the second
    generates the infinite dihedral group, and its diagram is parabolic.
    """
    double = CoxeterDiagrams()(Lattices(ZZ)([[-2, 2], [2, -4]]).module_generators())
    parallel = CoxeterDiagrams()(Lattices(ZZ)([[-2, 2], [2, -2]]).module_generators())

    assert double.coxeter_entry(0, 1) == 4
    assert double.coxeter_group().cardinality() == 8
    assert not parallel.coxeter_group().is_finite()
    assert parallel.is_parabolic()


def test_the_bond_six_is_realized_by_roots_of_squares_minus_two_and_minus_six() -> None:
    r"""\(I_2(6)=G_2\) is elliptic of order \(12\), and Gram \([[-2,3],[3,-6]]\) gives \(\cos^2 = 9/12\), \(m=6\)."""
    abstract = CoxeterDiagrams()([[1, 6], [6, 1]])
    rooted = CoxeterDiagrams()(Lattices(ZZ)([[-2, 3], [3, -6]]).module_generators())

    assert abstract.is_elliptic()
    assert abstract.coxeter_group().cardinality() == 12
    assert rooted.coxeter_entry(0, 1) == 6


def test_parallel_and_ultraparallel_pairs_share_the_bond_infinity_but_differ_in_type() -> None:
    r"""\([[-2,2],[2,-2]]\) is parabolic (determinant \(0\)); \([[-2,3],[3,-2]]\) is hyperbolic (determinant \(-5\)).

    Both have \(m=\infty\), so their Coxeter matrices agree; the roots
    distinguish a common ideal point from a common perpendicular.
    """
    parallel = CoxeterDiagrams()(Lattices(ZZ)([[-2, 2], [2, -2]]).module_generators())
    divergent = CoxeterDiagrams()(Lattices(ZZ)([[-2, 3], [3, -2]]).module_generators())

    assert parallel.coxeter_matrix() == divergent.coxeter_matrix()
    assert parallel.mirrors_are_parallel(0, 1)
    assert parallel.is_parabolic()
    assert divergent.mirrors_are_divergent(0, 1)
    assert divergent.is_hyperbolic()
