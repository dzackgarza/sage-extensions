r"""Vinberg invariants of mirrors, and the two hyperbolic families they decide.

The invariant of a pair of mirrors is the projective point
\([4b(r,s)^2 : q(r)q(s)]\), dehomogenized \(t = 4\cos^2(\pi/m)\).  These tests
state what the invariant knows that the Coxeter matrix does not, and check the
Lannér and quasi-Lannér conditions on the rank-three triangles where the
literature names the answer.

Sources: Vinberg, *Hyperbolic reflection groups*, Russian Math. Surveys 40
(1985), sections 1 and 4; Lannér, *On complexes with transitive groups of
automorphisms* (1950); Bourbaki, *Groupes et algèbres de Lie* VI.1.1 for the
crystallographic restriction.
"""

from sage_extensions.all import *


def rooted_diagram(gram_rows):
    r"""Return the Coxeter diagram of the roots forming the basis of this Gram."""
    return CoxeterDiagrams()(Lattices(ZZ)(gram_rows).module_generators())


def test_cos_pi_over_n_are_the_reflection_cosines_and_one_third_is_not() -> None:
    r"""\(1/2 = \cos(\pi/3)\), \((1+\sqrt5)/4 = \cos(\pi/5)\), \(0 = \cos(\pi/2)\);
    \(1/3\) is not \(\cos(\pi/n)\) since \(1/3 + i\sqrt{8}/3\) is not a root of unity
    (its minimal polynomial \(3x^2 - 2x + 3\) is not monic over \(\mathbb Z\))."""
    cosines = reflection_cosines()

    assert AA(1) / 2 in cosines
    assert (1 + AA(5).sqrt()) / 4 in cosines
    assert AA(0) in cosines
    assert AA(1) / 3 not in cosines


def test_the_invariant_of_a_root_pair_gives_back_the_coxeter_bond() -> None:
    r"""\(t = 1, 2, 3\) are the bonds \(3, 4, 6\).

    Two roots of square \(-2\) pairing to \(1\) give \([4:4]\) and the bond \(3\);
    squares \(-2, -4\) pairing to \(2\) give \([16:8]\) and the bond \(4\);
    squares \(-2, -6\) pairing to \(3\) give \([36:12]\) and the bond \(6\).
    """
    single = rooted_diagram([[-2, 1], [1, -2]]).vinberg_invariant_matrix()
    double = rooted_diagram([[-2, 2], [2, -4]]).vinberg_invariant_matrix()
    triple = rooted_diagram([[-2, 3], [3, -6]]).vinberg_invariant_matrix()

    assert single.vinberg_ratio(0, 1) == 1
    assert single.coxeter_entry(0, 1) == 3
    assert double.vinberg_ratio(0, 1) == 2
    assert double.coxeter_entry(0, 1) == 4
    assert triple.vinberg_ratio(0, 1) == 3
    assert triple.coxeter_entry(0, 1) == 6


def test_the_invariant_separates_parallel_mirrors_from_divergent_ones() -> None:
    r"""Both bonds are \(\infty\); the invariants are \(16/4 = 4\) and \(36/4 = 9\).

    The Coxeter matrix records only that the mirrors fail to meet; the invariant
    is exactly \(4\) when they meet at the boundary and larger when they have a
    common perpendicular.
    """
    parallel_diagram = rooted_diagram([[-2, 2], [2, -2]])
    divergent_diagram = rooted_diagram([[-2, 3], [3, -2]])
    parallel = parallel_diagram.vinberg_invariant_matrix()
    divergent = divergent_diagram.vinberg_invariant_matrix()

    assert parallel_diagram.mirrors_are_parallel(0, 1)
    assert not parallel_diagram.mirrors_are_divergent(0, 1)
    assert divergent_diagram.mirrors_are_divergent(0, 1)
    assert not divergent_diagram.mirrors_are_parallel(0, 1)
    assert parallel.coxeter_matrix() == divergent.coxeter_matrix()

    assert parallel.vinberg_ratio(0, 1) == 4
    assert divergent.vinberg_ratio(0, 1) == 9
    assert parallel.vinberg_invariant(0, 1) != divergent.vinberg_invariant(0, 1)


def test_the_invariant_does_not_move_when_the_mirrors_normals_are_rescaled() -> None:
    r"""\(A_2\) and \(A_2(4)\): \([4\cdot 1 : 4] = [4 \cdot 16 : 64]\) in \(\mathbb P^1\)."""
    plain = rooted_diagram([[-2, 1], [1, -2]]).vinberg_invariant_matrix()
    scaled = rooted_diagram([[-8, 4], [4, -8]]).vinberg_invariant_matrix()

    assert plain.vinberg_invariant(0, 1) == scaled.vinberg_invariant(0, 1)
    assert plain.coxeter_entry(0, 1) == scaled.coxeter_entry(0, 1) == 3


def test_the_crystallographic_and_simply_laced_conditions_read_the_bonds() -> None:
    r"""Crystallographic is \(m\in\{2,3,4,6,\infty\}\); simply laced is \(m\in\{2,3\}\).

    \(A_2\) is both, \(B_2\) (bond \(4\)) is crystallographic and not simply laced,
    \(H_3\) (bond \(5\), \(4\cos^2(\pi/5)\notin\mathbb Q\)) is neither.
    """
    a2 = CoxeterDiagrams()(["A", 2]).vinberg_invariant_matrix()
    b2 = CoxeterDiagrams()(["B", 2]).vinberg_invariant_matrix()
    h3 = CoxeterDiagrams()(["H", 3]).vinberg_invariant_matrix()

    assert a2.is_crystallographic()
    assert a2.is_simply_laced()

    assert b2.is_crystallographic()
    assert not b2.is_simply_laced()

    assert not h3.is_crystallographic()
    assert not h3.is_simply_laced()


def test_the_two_three_seven_triangle_is_a_lanner_diagram() -> None:
    r"""\(\Delta(2,3,7)\) is compact hyperbolic and not paracompact.

    \(1/2 + 1/3 + 1/7 < 1\), and the vertex-deleted subdiagrams \(A_2\),
    \(A_1\times A_1\), \(I_2(7)\) are all finite (Lannér's condition).
    """
    diagram = CoxeterDiagrams()([[1, 7, 2], [7, 1, 3], [2, 3, 1]])
    invariants = diagram.vinberg_invariant_matrix()

    assert diagram.is_hyperbolic()
    assert invariants.is_hyperbolic()
    assert invariants.is_compact_hyperbolic()
    assert not invariants.is_paracompact_hyperbolic()


def test_the_two_three_infinity_triangle_is_a_quasi_lanner_diagram() -> None:
    r"""\(\Delta(2,3,\infty)\) is paracompact hyperbolic and not compact.

    Roots \(r_0, r_1, r_2\) with Gram \(\begin{pmatrix}-2&1&0\\1&-2&2\\0&2&-2\end{pmatrix}\)
    (determinant \(2\), signature \((1,2)\)) have bonds \(3, 2\) and, on \(r_1 r_2\),
    \(t = 16/4 = 4\): the affine \(\tilde A_1\), so the triangle has an ideal
    vertex and finite volume (Vinberg, §4).
    """
    diagram = rooted_diagram([[-2, 1, 0], [1, -2, 2], [0, 2, -2]])
    invariants = diagram.vinberg_invariant_matrix()

    assert diagram.is_hyperbolic()
    assert diagram.mirrors_are_parallel(1, 2)
    assert invariants.coxeter_entry(0, 1) == 3
    assert invariants.coxeter_entry(0, 2) == 2
    assert invariants.vinberg_ratio(1, 2) == 4
    assert invariants.is_paracompact_hyperbolic()
    assert not invariants.is_compact_hyperbolic()


def test_the_invariant_matrix_with_t_equal_one_everywhere_is_the_affine_A2_triangle() -> None:
    r"""\(t = 1\) off the diagonal makes every bond \(3\): the cycle \(\tilde A_2\),
    whose Schläfli matrix \(2I - (J - I)\) has the all-ones vector in its kernel."""
    invariants = VinbergInvariantMatrices().from_invariants(
        ZZ, [[4, 1, 1], [1, 4, 1], [1, 1, 4]]
    )

    assert invariants.cardinality() == 3
    assert invariants.coxeter_entry(0, 1) == 3
    assert invariants.is_crystallographic()
    assert invariants.is_simply_laced()
    assert invariants.is_parabolic()
    assert not invariants.is_hyperbolic()
    assert invariants.coxeter_diagram().schlaflian() == 0
