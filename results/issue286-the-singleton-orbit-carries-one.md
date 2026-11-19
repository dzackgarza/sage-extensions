# The fixed class carries exactly one orbit, and the other five carry six

**Lemma.** Keep the hypotheses of `results/issue286-the-fibre-formula.md`: `L`
even, indefinite, nondegenerate `2`-elementary, `rho` onto `O(A_L, q)` (Nikulin,
*Integral symmetric bilinear forms and some of their applications*, Math.
USSR-Izv. 14 (1980), pp. 103--167, Theorem 3.6.3; the article's page range, the
theorem's printed page not in front of me), `J_0` order-four totally isotropic,
`P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`.  Let `𝒪` be a `P_0`-orbit of
liftable classes and `m(𝒪) = |P_0 cap rho(Pi_P)|` for `P` with `J_P in 𝒪`.  Then
the fibre over `𝒪` is `|𝒪|·m(𝒪)/|P_0|`, and:

* on a **singleton** orbit (`|𝒪| = 1`) the fibre is exactly `1`, and `m(𝒪) =
  |P_0|`, i.e. the class is fixed by all of `P_0` and its stabilizer contains
  `P_0`;
* consequently, for `T_Co`, `7 = 1 + sum_{i = 1..5} |𝒪_i|·m_i/|P_0|`: the five
  other orbits contribute exactly **six**, and each contributes a positive
  integer `k_i = |𝒪_i| m_i / |P_0|` with `sum k_i = 6`.

## Proof

`m(𝒪) = |P_0 cap Stab(J)|` for `J in 𝒪` is an intersection of two subgroups of
`O(q)`, so it divides `|P_0|` (Lagrange).  On a singleton orbit the fibre
`|𝒪|·m/|P_0| = m/|P_0|` is an integer at least `1` -- it counts orbits of a
nonempty set -- so `m = |P_0|` and the fibre is `1`.  The `T_Co` identity is
`results/issue286-the-fibre-formula.md`'s formula summed over the six measured
orbits with the row's seven total (`results/issue286-the-gamma-co-2-distribution-
measured.md`).

## The arithmetic it leaves

With `|P_0| = 1981808640` and the measured sizes `13440, 8192, 1680, 210, 192`:

| `|𝒪|` | smallest `k` | smallest `m` | `m` divides `|P_0|` |
| ---: | ---: | ---: | --- |
| 13440 | 1 | 147456 | yes |
| 8192 | 1 | 241920 | yes |
| 1680 | 1 | 1179648 | yes |
| 210 | 1 | 9437184 | yes |
| 192 | 1 | 10321920 | yes |

and `sum k_i = 6` over those five, with `k_i >= 1` each.  So every `m_i` is at
least the tabulated bound and divides `|P_0|`, and the five `k_i` are positive
integers summing to six -- in particular **no orbit carries more than two**, and
at most one of them carries two (`k_i` summing to 6 over five terms forces four
ones and one two, or five ones with one orbit of the six unaccounted... precisely:
exactly one `k_i = 2` and four `k_i = 1`).

That last reading is the answer to "which class-orbit carries two": **there is at
most one, and the arithmetic says the five non-fixed orbits carry six in total**,
so the doubling is among them and the fixed class never doubles.

## Status

Proved; no computation beyond the arithmetic above, and no code changed, so no red
test this turn.  What is still owed is the five `m_i` themselves -- each a
`|P_0 cap rho(Pi_P)|` at a representative plane of its orbit -- which the identity
`sum |𝒪_i| m_i = 7 |P_0|` now checks without the row.
