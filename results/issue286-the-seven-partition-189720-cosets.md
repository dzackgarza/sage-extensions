# The seven orbits partition 189720 cosets, and the partition is not uniform

**Lemma.** Let `L` be even, indefinite, nondegenerate `2`-elementary, so
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3; the article's page range is what this repository cites), `J_0` order-four
totally isotropic, `P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`, and `P` a
primitive isotropic plane with parabolic `Pi_P`.  Then:

1. the cosets `O(q)/rho(Pi_P)` number `[O(q) : rho(Pi_P)] = 23715 * 8 = 189720`
   on `T_Co`, and the `Gamma`-orbits of planes are a partition of them into
   `P_0`-orbits;
2. each of the seven orbit sizes divides `|P_0| = 1981808640`;
3. the seven sizes therefore sum to `189720`, and since `7` does not divide
   `189720` (`189720 = 2^3 * 3^2 * 5 * 17 * 31`) **the seven are not all equal**;
   `189720 / 7 = 27102 + 6/7`.

## Proof

(1) is the double-coset correspondence (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, **Lemma 3.6, printed p. 22**) with `rho` onto as cited, plus
`[O(q) : rho(Pi_P)] = 46998591897600 / 247726080 = 189720`, the two orders `#360`
measures at a `T_Co` plane, factorised as the 23715 liftable classes times the
eight cosets over each (`[Stab(J) : rho(Pi_P)] = 1981808640 / 247726080 = 8`).
(2) is Lagrange: an orbit of `P_0` has size `[P_0 : P_0 cap g rho(Pi_P) g^{-1}]`,
a divisor of `|P_0|`.  (3) is arithmetic.

## What it adds, and what it does not

It does not give the fibre.  It gives a check every partition must pass: seven
divisors of `1981808640`, summing to `189720`, not all equal, each at least
`189720/|P_0| < 1` and at most `|P_0|`.  Any future computation of the seven --
from the row or otherwise -- is now falsifiable on its sum and its divisibility
alone, which the previous rounds' attempts were not.

It also corrects a habit of the last two rounds: the per-orbit quantities are
coset counts (`189720` in total, eight per class), not class counts (`23715`),
and every fibre formula that summed over the classes missed the factor eight that
the earlier refutation exposed.

## Status

Proved, by the cited page and index arithmetic; no code changed, so no red test.
The item itself is unchanged: the fibre over the one class-orbit that carries two
of the seven is read from the row's representatives, and the partition identity
above is the check to run on them.
