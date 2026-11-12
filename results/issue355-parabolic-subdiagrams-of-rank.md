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

`parabolic_subdiagrams_of_rank` is added to `CoxeterDiagrams`: it returns the
parabolic subdiagrams, connected or not, of the form rank asked for — the
criterion's family for rank \\(n - 1\\).  In Vinberg's sense a parabolic
subdiagram is a disjoint union of connected affine diagrams, and its rank is
its vertex count less its component count, which is the rank of its Gram
matrix; the call's docstring states the criterion with its citation and page.
The existing maximality calls are unchanged: they are correct for their own
stated meaning (maximal for inclusion), and the criterion's rank condition
is now answered by the new call.

The digest gains a `parabolic_subdiagrams` section: card `0125`'s
`integral.cusp_chambers['g-e']` row holds the twelve walls and the
parabolic-subdiagram orbits of the chamber of `W_e ⊂ G_e` (Sterk, Fig. 5,
p. 20: four labelled classes, of sizes 1, 2, 2 and 4).  The digest was
regenerated at the pinned database ref `1e1cadcf`, not edited, and every
other section is unchanged from the previous pin `dbc9fc6a`.

## The test

`tests/lattices/test_the_rank_n_minus_one_parabolic_count_on_the_we_chamber.sage`
asserts exactly the proved facts: the call's count on the `g-e` chamber
equals the sum of the card's `parabolic_orbits` sizes — nine — and each
returned subdiagram is the orthogonal-wall subdiagram of one of the chamber's
own ideal rays.  The lattice and the walls are built from the card, read by
tag, so the Gram matrix and the twelve wall vectors are never typed in the
test; the reproductions of the reported calls (36 and 44) are deleted, and
the ideal-vertex count is read from the card's orbits rather than computed
and compared with the ray count.

## The run

`1 passed in 22.37 s` (`.tmp/qc-evidence/issue355-parabolic-test.log`); the
test lint on the file: `1 files, 0 findings`
(`.tmp/qc-evidence/issue355-parabolic-lint.log`).
