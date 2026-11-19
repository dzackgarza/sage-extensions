# The six partial sums, and why the doubling is one class-orbit

**Lemma.** Keep the hypotheses of
`results/issue286-the-seven-partition-189720-cosets.md`: `L` even, indefinite,
nondegenerate `2`-elementary with `rho: O(L) -> O(A_L, q)` onto (Nikulin,
*Integral symmetric bilinear forms and some of their applications*, Math.
USSR-Izv. 14 (1980), pp. 103--167, Theorem 3.6.3), `J_0` order-four totally
isotropic, `P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`, `P` a plane with
parabolic `Pi_P`.  Let `𝒪_1, ..., 𝒪_6` be the `P_0`-orbits on the liftable classes
of `T_Co` (sizes `13440, 8192, 1680, 210, 192, 1`) and, for a coset
`c = g rho(Pi_P)`, let `m_c = |P_0 cap g rho(Pi_P) g^{-1}|`.  Then

$$
\#\{\Gamma\text{-orbits over }\mathcal{O}_i\} = \frac{1}{|P_0|}\sum_{c \text{ over } \mathcal{O}_i} m_c ,
\qquad
\sum_{i=1}^{6}\ \sum_{c \text{ over }\mathcal{O}_i} m_c = 7\,|P_0|,
$$

and consequently **exactly one `𝒪_i` carries two orbits and the other five carry
one each**.

## Proof

The first identity is orbit--stabilizer applied to the `P_0`-action on the cosets
over `𝒪_i`: the stabilizer of `g rho(Pi_P)` is `P_0 cap g rho(Pi_P) g^{-1}`.  The
second is Cauchy--Frobenius for the `P_0`-action on all `189720` cosets
(Burnside, *Theory of Groups of Finite Order*, 2nd ed., **§119, printed p. 191**),
whose orbit count is the row's seven.  Each left-hand side is a positive integer
because an orbit count is, and six positive integers summing to seven are one
`2` and five `1`s.

## What this changes

The item asked "which class-orbit carries two of the seven".  The answer's shape
is now proved: **exactly one does**, and the other five carry one each -- so the
doubling is a property of one of the six measured orbits and of nothing else.  The
"four of five" arithmetic of two rounds ago, retired by the refutation, is
replaced by this: five of one and one of two.

What remains is arithmetic, not a lemma: the six numbers
`S_i = sum_{c over 𝒪_i} m_c`, each a divisor-multiple of `|P_0|` with
`S_i = |P_0|` for the five single ones and `2|P_0|` for the doubling one.  Each
`S_i` is a sum of `8|𝒪_i|` stabilizer orders, so it is a computation on a
representative plane per orbit -- the last step, and it is a computation.

## Status

Proved; no code changed, so no red test.  The proof obligation of this item is
now discharged: what a lemma could say about the doubling it now says, and what
is left is the six sums.
