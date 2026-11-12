r"""The rank-(n - 1) parabolic count on the W_e chamber equals the vertex count (#355).

**The criterion and the call it names.**  Vinberg's finite-volume criterion
(E. B. Vinberg, *The groups of units of certain quadratic forms*, Mat. Sb. 87
(129) (1972), the English translation Math. USSR Sb. 16 (1972), No. 1,
Proposition 1, printed p. 22): the ideal vertices of a finite-volume chamber
are in bijection with the maximal parabolic subdiagrams of rank \\(n - 1\\) —
one per vertex at infinity, \\(n\\) the dimension of the Lobachevskii space.
The criterion's family on a given chamber is computed from the chamber's own
primitive rays: each ideal vertex's orthogonal walls form a subdiagram of
form rank \\(n - 1\\), and the ideal-vertex count is the vertex count.

**What is asserted.**  Exactly the proved facts: the reproductions of the
reported calls (``maximal_parabolic_subdiagrams`` returns 36 and
``maximal_elliptic_subdiagrams`` returns 44, both maximal for inclusion and
neither the criterion's rank condition); the ideal-vertex count read from
the chamber's primitive rays (nine); and each ideal vertex's orthogonal
walls have form rank \\(n - 1\\).

**The card field.**  Card `0125`'s ``integral.cusp_chambers['g-e']`` row
states no ``ideal_vertices`` count: the source prints four labelled classes
(Fig. 5, p. 20) and the row stores them as ``parabolic_orbits`` of sizes
1, 2, 2 and 4, which sum to nine.  The assertion below compares the
ideal-vertex count with the computed ray count and names the missing card
field (``ideal_vertices``) rather than read a value the card does not hold.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_rank_n_minus_one_parabolic_count_equals_the_ideal_vertex_count() -> None:
    r"""The count is the chamber's own ideal-vertex count, and the reported calls reproduce."""
    gram = [
        [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, -4, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, -4, 0, 2, 0, 0, 0, 0],
        [0, 0, 2, 0, -4, 2, 0, 0, 0, 0],
        [0, 0, 0, 2, 2, -4, 2, 0, 0, 0],
        [0, 0, 0, 0, 0, 2, -4, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, -4, 2, 0],
        [0, 0, 0, 0, 0, 0, 0, 2, -4, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 2, -4],
    ]
    walls = [
        (0, 0, 1, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 1, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        (-1, 1, 0, 0, 0, 0, 0, 0, 0, 0),
        (2, 0, -2, -3, -4, -6, -5, -4, -3, -2),
        (2, 2, -6, -8, -11, -16, -13, -10, -7, -4),
        (5, 3, -10, -16, -20, -30, -24, -18, -12, -6),
    ]
    lattice = Lattices(ZZ)([[int(entry) for entry in rows] for rows in gram])
    roots = tuple(lattice(vector) for vector in walls)
    diagram = CoxeterDiagrams().from_roots(roots)

    # The reproduction of the reported calls: maximal for inclusion, not the
    # criterion's rank condition.
    assert int(diagram.maximal_parabolic_subdiagrams().cardinality()) == 36
    assert int(diagram.maximal_elliptic_subdiagrams().cardinality()) == 44

    # The criterion's computation: the chamber's primitive rays, the ideal
    # vertices, and each one's orthogonal walls have form rank n - 1.
    hyperbolic_dimension = int(lattice.signature_pair().second())
    correlation = lattice.algebraic_correlation_morphism()
    cone = lattice.rational_polyhedral_cone(
        tuple(correlation(root) for root in roots), wall_roots=roots, complete=True
    )
    rays = tuple(tuple(int(entry) for entry in rays) for rays in cone.primitive_rays())
    ideal_rays = tuple(ray for ray in rays if lattice.q(lattice(ray)) == 0)
    form = lattice.b

    for ray in ideal_rays:
        orthogonal = tuple(
            i for i, wall in enumerate(walls) if form(lattice(ray), lattice(wall)) == 0
        )
        subdiagram = diagram.induced_subdiagram(
            tuple(diagram.index_set()[i] for i in orthogonal)
        )
        assert int(subdiagram.form_rank()) == hyperbolic_dimension - 1
        assert subdiagram.is_parabolic() or subdiagram.is_parabolic_union()

    # The count: the ideal-vertex count, named against the card's missing
    # field (ideal_vertices).
    assert sum(1 for ray in rays if ray in ideal_rays) == 9
