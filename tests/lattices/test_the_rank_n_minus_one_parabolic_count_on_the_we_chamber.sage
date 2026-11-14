r"""The rank-(n - 1) parabolic count on the W_e chamber equals the vertex count (#355).

**The criterion and the call it names.**  Vinberg's finite-volume criterion
(E. B. Vinberg, *The groups of units of certain quadratic forms*, Mat. Sb. 87
(129) (1972), the English translation Math. USSR Sb. 16 (1972), No. 1,
Proposition 1, printed p. 22): the ideal vertices of a finite-volume chamber
are in bijection with the parabolic subdiagrams of rank \\(n - 1\\) — one per
vertex at infinity, \\(n\\) the dimension of the Lobachevskii space.  In
Vinberg's sense a parabolic subdiagram is a disjoint union of connected affine
diagrams, and its rank is its vertex count less its component count, which is
the rank of its Gram matrix; the call the criterion names is
``parabolic_subdiagrams_of_rank``, and it returns that family — connected or
not — for the rank asked for.

**What is asserted.**  Exactly the proved facts: the call's count on the
chamber equals the sum of the card's ``parabolic_orbits`` sizes; and each
returned subdiagram is the orthogonal-wall subdiagram of one of the chamber's
own ideal rays, so the family the call returns is the chamber's ideal vertices.

**The card field.**  Card `0125`'s ``integral.cusp_chambers['g-e']`` row states
no ``ideal_vertices`` count: the source prints four labelled classes
(Fig. 5, p. 20) and the row stores them as ``parabolic_orbits`` of sizes
1, 2, 2 and 4, which sum to nine.  The count is read from the card by tag and
never typed here, and the lattice and the walls are read from the same row.
"""

from sage_extensions.all import *


def card_0125():
    r"""Return card ``0125``'s row, read by tag from the digest."""
    return card("parabolic_subdiagrams", "0125")


def test_the_rank_n_minus_one_parabolic_count_equals_the_ideal_vertex_count() -> None:
    r"""The count is the sum of the card's orbit sizes, and each member is an ideal vertex's walls."""
    stated = card_0125()
    lattice = Lattices(ZZ)(stated["gram"])
    row = stated["rows"]["g-e"][0]
    roots = tuple(lattice(entry) for entry in row["walls"])
    diagram = CoxeterDiagrams().from_roots(roots)

    # The criterion's rank: the Lobachevskii dimension less one.
    hyperbolic_dimension = int(lattice.signature_pair().second())
    family = diagram.parabolic_subdiagrams_of_rank(hyperbolic_dimension - 1)

    # The count: the sum of the card's parabolic_orbits sizes.
    assert int(family.cardinality()) == sum(
        1 for orbit in row["parabolic_orbits"] for subdiagram in orbit
    )

    # Each returned subdiagram is the orthogonal-wall subdiagram of an ideal ray.
    correlation = lattice.algebraic_correlation_morphism()
    cone = lattice.rational_polyhedral_cone(
        tuple(correlation(root) for root in roots), wall_roots=roots, complete=True
    )
    rays = tuple(tuple(int(entry) for entry in ray) for ray in cone.primitive_rays())
    form = lattice.b
    ideal_rays = tuple(ray for ray in rays if lattice.q(lattice(ray)) == 0)
    orthogonal_sets = {
        frozenset(
            index
            for index, wall in enumerate(row["walls"])
            if form(lattice(ray), lattice(wall)) == 0
        )
        for ray in ideal_rays
    }
    labels = tuple(diagram.index_set())
    for subdiagram in family:
        positions = frozenset(
            labels.index(vertex) for vertex in subdiagram.index_set()
        )
        assert positions in orthogonal_sets
