# #355 — the rank-(n − 1) parabolic subdiagrams of the W_e chamber of card 0125

Card `0125`, `L = U(2) ⊕ E8(−2)`, the twelve-wall chamber of `W_e ⊂ G_e`
(`integral.cusp_chambers['g-e']`, Sterk, Math. Z. 207 (1991), (4.3.5), p. 19,
Fig. 4).

## The reproduction

On the card's own twelve walls, read from the row and rebuilt through the
owner's calls:

| call | value |
| --- | --- |
| `CoxeterDiagrams().from_roots(walls).maximal_parabolic_subdiagrams()` | 36 |
| `CoxeterDiagrams().from_roots(walls).maximal_elliptic_subdiagrams()` | 44 |
| the chamber's primitive rays | 23, of which 9 have square zero |

Both calls are maximal **for inclusion** — their docstrings say so — and
neither is the criterion's rank condition.

## The meaning of each call

The owner's `maximal_parabolic_subdiagrams` returns the parabolic induced
subdiagrams maximal for inclusion, of every rank; `maximal_elliptic_subdiagrams`
is its elliptic counterpart.  Vinberg's criterion
(E. B. Vinberg, *The groups of units of certain quadratic forms*, Mat. Sb. 87
(129) (1972), the English translation Math. USSR Sb. 16 (1972), No. 1,
Proposition 1, printed p. 22) states that the ideal vertices of a
finite-volume chamber are in bijection with the parabolic subdiagrams of
rank \\(n - 1\\) — one per vertex at infinity, \\(n\\) the dimension of the
Lobachevskii space.  The two notions differ: maximality for inclusion is a
property of vertex sets, and the criterion's rank condition is a property of
the Schlaefli form.

## The change

No new method is added to `CoxeterDiagrams`: the criterion's computation
needs the chamber's own primitive rays (a lattice-level computation, not a
diagram-level one), so it is asserted in the test with Vinberg's citation.
The existing maximality calls are unchanged: they are correct for their own
stated meaning (maximal for inclusion), and the criterion's rank condition
is documented beside them in the test's docstring.

## The test

`tests/lattices/test_the_rank_n_minus_one_parabolic_count_on_the_we_chamber.sage`
asserts exactly the proved facts: the reproductions of the reported calls
(36 and 44), and the count of the parabolic subdiagrams of rank \\(n - 1\\)
equals the chamber's own ideal-vertex count — nine, read from the primitive
rays of the chamber.  Card `0125`'s `integral.cusp_chambers['g-e']` row
states no `ideal_vertices` count, so the assertion compares the call's count
with the computed ray count and names the missing card field
(`ideal_vertices`) rather than read a value the card does not hold.

## The run

`1 passed` (`.tmp/qc-evidence/issue355-parabolic-test.log`); the test lint on
the file: `1 files, 0 findings`
(`.tmp/qc-evidence/issue355-parabolic-lint.log`).
