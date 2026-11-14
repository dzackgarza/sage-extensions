# The Vinberg call returns the facets of \(P\) (#401)

Vinberg's algorithm writes down a sequence of normals (38) and E. B. Vinberg,
*On the groups of unit elements of certain quadratic forms*, Math. USSR Sb. 16
(1972), Proposition 4 (p. 28) states of it that the polyhedron \(P\) is the
intersection of the half-spaces of *all* the roots of that sequence.  The
proposition does not state that each root of the sequence is a facet, so the
chamber call now decides that question instead of assuming it:
`HyperbolicLattices._facet_roots` intersects the half-spaces in the owned cone
and keeps only the roots whose half-space is one of the cone's
`facet_covectors`, that is, one its H-representation needs.  Both public doors
onto the accepted sequence read the pruned family: `fundamental_chamber` — and
through it `subgroup_fundamental_chamber` and
`isotropic_vector_reduction_image.cusp_chamber` — and `vinberg_simple_roots`,
and through that `vinberg_algorithm`, `reflection_group` and
`reflection_coxeter_diagram`.

The pruning is a no-op on the polyhedron: a redundant half-space cuts nothing,
so the cone, its vertices, its completion flag and its Coxeter diagram are the
same as before.  What changes is only the root family the call reports.

## What the sequences in this suite are

Every completed Vinberg search the tests run was measured on this tree: the
number of roots the algorithm accepts, against the number of facets of the
polyhedron they cut out.

| lattice | accepted | facets | where the test builds it |
| --- | --- | --- | --- |
| \(U\oplus A_1\) | 3 | 3 | `test_reflection_hyperbolic.sage`, `test_hyperbolic_archive_reconciliation.sage` |
| \(U\oplus E_8\) | 10 | 10 | `test_hyperbolic_root_lengths_and_vinberg.sage` |
| \(U\oplus E_8(-2)\) | 10 | 10 | `test_the_subgroup_cusp_chamber.sage`, `test_the_chamber_vertex_squares_and_cocompactness.sage` |
| \(U(2)\oplus E_8(-2)\) | 10 | 10 | `test_the_chamber_vertex_squares_and_cocompactness.sage` |
| \(U\oplus E_8\oplus E_8\) | 19 | 19 | `test_genus_of_the_scattone_summands.sage` |
| \(U\oplus A_1\), \(U\oplus A_1^{\oplus2}\), \(U\oplus A_1^{\oplus3}\), \(U\oplus A_2\), \(U\oplus A_2\oplus A_1\), \(U\oplus A_3\), \(U\oplus D_4\), \(U\oplus A_1\oplus E_8\) | 3, 4, 5, 4, 6, 5, 6, 12 | same | not in the suite; surveyed for this issue |
| \(U\oplus E_8(-2)\) at `max_roots` 1..12 and `max_decompositions` 2..20 | 9 or 10 | same | the bounded prefixes the suite passes |

No completed sequence carries a root that is not a facet, so no chamber changes
in this suite.

## The Sterk rows

At the three printed Enriques cusps whose rows are green, the *public*
`cusp_chamber` call returns the same walls before and after this change: 12, 10
and 12 roots, with identical coordinates, matching card `029J`'s `gamma-en-2`
rows 4.3.5, 4.3.6 and 4.3.7 (H. Sterk, *Compactifications of the period space of
Enriques surfaces, Part I*, Math. Z. 207 (1991), pp. 19, 21, 22).

Cusp 5's sequence has fourteen facets, while card row 4.3.9 publishes thirteen
and `Sterk_5` holds fourteen roots.  The facet test does not explain that
disagreement away: all fourteen are irredundant, so the extra wall is not
redundancy, and the row stays as #387 left it.  Cusp 4 was not measured to
completion; that is the walk #400's registration is about.

## The one row where a root is not a facet

No Vinberg sequence in this suite carries one, so the criterion is pinned on a
family supplied by hand, on a lattice the suite already builds.
`test_nondegenerate_marking_stabilizers.sage`'s \(U\oplus A_1\oplus A_1\) has
\(a_1^2=a_2^2=-2\) and \(b(a_1,a_2)=0\), so \(a_1+a_2\) is a primitive root of
square \(-4\).  Its half-space is implied by the chamber's four walls: the wall
\(a_1\) gives \(b(a_1,x)\ge 0\) and the wall \(a_2-a_1\) gives
\(b(a_2,x)\ge b(a_1,x)\), so \(b(a_1+a_2,x)\ge 2b(a_1,x)\ge 0\).  The cone cut
by the four walls and by that root has four facets, and the face on the extra
root is two-dimensional in a four-dimensional cone.

`tests/lattices/test_the_vinberg_call_returns_the_facets.sage` pins both halves
of the statement: on \(U\oplus A_1\), \(U\oplus E_8\), \(U\oplus E_8(-2)\) and
\(U(2)\oplus E_8(-2)\) every returned wall cuts a facet (root count equals facet
count, and each wall's face has codimension one), and a half-space the other
walls imply is not one.
