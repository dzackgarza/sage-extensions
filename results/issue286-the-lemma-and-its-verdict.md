# The lemma that would close the first open item, and its verdict

**Lemma.** Let `L` be even, indefinite and nondegenerate `2`-elementary, so that
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3 -- the article's page range is what this repository cites, and the
theorem's own printed page is not in front of me); let `J_0` be an order-four
totally isotropic subgroup of `A_L`, `P_0 = Stab_{O(q)}(J_0)` and
`Gamma = rho^{-1}(P_0)`; and let `P` be a primitive isotropic plane of `L`.
Then the `Gamma`-orbits of primitive isotropic planes inside the `O(L)`-orbit of
`P` are the double cosets `P_0 \ O(q) / rho(Stab_{O(L)}(P))`, **and their number
is the number of `P_0`-orbits on the liftable classes `J = [P/2]`**.  The
smallest case that tests both halves is `U + U(2) + <-4>`, where `|O(q)| = 12`,
`|P_0| = 4`, three liftable classes and two planes in the row.

## The first half: proved

`Gamma` acts on the set of planes through `rho`, and `Gamma = ker rho` is
normal, so `Gamma \ O(L)` is `rho(O(L)) = O(q)` by the surjectivity above.  Hence
the `Gamma`-orbits inside the `O(L)`-orbit `O(L)/Stab_{O(L)}(P)` are
`P_0 \ O(q) / rho(Stab_{O(L)}(P))`: this is the double-coset correspondence of
Dutour Sikirić--Hulek, arXiv:2302.01679v2, **Lemma 3.6, printed p. 22**, applied
with `Pi = Stab_{O(L)}(P)` and `U = Pi cap ker rho`, normal in `Pi` because `rho`
is a homomorphism.

Measured on the smallest case (`.scratch/w286-probes/probe-lemma.log`):

```
|O(q)| = 12, |P_0| = 4
class orbit 3, P_0-orbits on it: [1, 2]
Gamma_{Co,2} plane orbits: 2
```

## The second half: refuted

`U + U(2) + <-4>` has **two** `P_0`-orbits on the three classes (sizes `1` and
`2`) and **two** `Gamma`-orbits of planes, so the two counts agree there.  On
`T_Co` they do not: `P_0 = Stab_{O(q)}([P/2])` splits the 23715 liftable classes
into **six** orbits, `13440 + 8192 + 1680 + 210 + 192 + 1`, while the
`Gamma_{Co,2}` plane row has **seven** orbits
(`results/issue286-the-gamma-co-2-distribution-measured.md`).  A bijection cannot
have 7 on one side and 6 on the other, so the lemma's second half is **false** as
stated: the plane orbits are not in bijection with the `P_0`-orbits on the
classes, and one class-orbit carries two of them.

What survives is the double-coset half, which is the part the code computes:
`isotropic_line_stabilizer_image` and its plane analogue read the double cosets,
not the classes, which is why the row returns 7 where the classes give 6.

## What that means for the item

The first open item's remaining datum -- *which* class-orbit carries two orbits
-- cannot be derived from the classes: the lemma that would have derived it is
refuted above on `T_Co` and confirmed on the smallest case.  The datum is a
property of the double-coset space, so it is read off the row's seven
representatives (the `#391` plane computation) and from nothing cheaper.  That is
the item's exact status: the fibre statement is false, the double-coset statement
is proved and is what the library computes, and the last datum is a row's output.

No code changed, so there is no red test this turn; the run above is the
deciding probe, and its two numbers are the refutation.
