# The fixed class carries one orbit exactly when the plane's image sits in `P_0`

**Lemma.** Let `L` be even, indefinite and nondegenerate `2`-elementary, so
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3; the article's page range is what this repository cites), `J_0` order-four
totally isotropic, `P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`, and `P` a
plane with `J_P = [P/2]` and `H = rho(Pi_P) <= Stab_{O(q)}(J_P)`.  Then:

* on the `P_0`-**fixed** class (`J_P` fixed by `P_0`, so `P_0 <= Stab(J_P)`), the
  `Gamma`-orbits of planes are the `P_0`-orbits on `Stab(J_P)/H`, and their number
  is `[Stab(J_P) : H] / [P_0 : P_0 cap H]`; that is `1` **iff** `H <= P_0`;
* on `T_Co` the fixed class therefore carries exactly one `Gamma`-orbit iff
  `rho(Pi_P) <= P_0` there, and the doubling of the seven is over one of the five
  non-fixed orbits in either case.

## Proof

The cosets over a fixed class are `Stab(J_P)/H`, of order
`[Stab(J_P) : H] = 1981808640 / 247726080 = 8` on `T_Co` (the index `#360`
measures).  `P_0 <= Stab(J_P)` acts on them by left multiplication, and its orbits
there are the `Gamma`-orbits over that class -- the double-coset correspondence,
Dutour Sikirić--Hulek, arXiv:2302.01679v2, **Lemma 3.6, printed p. 22**.  The
action is transitive iff `Stab(J_P) = P_0·H`, i.e. iff
`[Stab(J_P) : H] = [P_0 : P_0 cap H]`, i.e. iff `|P_0 cap H| = |H|`.  So the
fixed class carries one orbit exactly when `H <= P_0`; otherwise more, and the
number is the quotient above.

The last sentence is the previous round's conclusion: six positive integers
summing to seven force one orbit of size two, and if the fixed class carries
exactly one then the doubling is among the five non-fixed -- while if the fixed
class itself carried two, the five others would carry five and the doubling would
be there.  Either way the datum is confined to the five non-fixed orbits **or**
to the fixed one, and the criterion `H <= P_0` decides which, a subgroup inclusion
of two subgroups of `O(q)`.

## What was verified, and what was not

Verified: the index arithmetic above, from the two orders `#360` measures at a
`T_Co` plane.  Not verified this turn: the inclusion `rho(Pi_P) <= P_0` itself at
a plane over the fixed class, which is one `IsSubgroup` call on `T_Co`'s `O(q)`
engine -- cheap, and the exact next check.

On the small specimen the analogue holds: `U + U(2) + <-4>` has a fixed class,
`|P_0 cap Stab(J)| = |P_0| = 4` there (measured,
`.scratch/w286-probes/probe-fibrelem.log`), and its fibre is `1`, consistent with
the criterion.

No code changed; no red test.
