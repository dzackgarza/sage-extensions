# `Gamma_{Co,2}` is the discriminant preimage the driver builds

The reviewer's first item: the incidence driver builds `Gamma_{Co,2}` as
`rho^{-1}` of the stabilizer of `A_{U(2)}` in `O(q_{T_Co})`
(`tests/coble_gamma_co_2_incidence_rows.py:669-670`,
`lattice.Aut().discriminant_point_stabilizer(_decomposition(lattice))`), where
the issue defines `Gamma_{Co,2} = R_{Gamma_{En,2}}`, the image in `O(T_Co)` of
`Stab_{Gamma_{En,2}}(delta)`.  This note proves the two are the same group, so
the driver's construction *is* the issue's, and states what the proof rests on.
No image run decides it.

## The statement

$$
\Gamma_{Co,2} \;=\; R_{\Gamma_{En,2}} \;=\; \bar\rho^{-1}\bigl(\mathrm{Stab}_{O(q_{T_{Co}})}(A_{U(2)})\bigr),
$$

with `bar rho: O(T_Co) -> O(A_{T_Co}, q)` the discriminant representation of
`T_Co` and `A_{U(2)} = <[ep/2], [fp/2]>` the order-four subgroup of
`A_{T_Co}`.  The right-hand group is exactly the driver's
`discriminant_point_stabilizer` of the span of the two dual classes.

## The proof

Write `N = T_Co perp Z delta` for the rank-twelve lattice and `T_En = N_H` for
the overlattice glued along `H = <(h/2, delta/2)>` (def:gamma-co-groups;
`delta^perp = eta(T_Co)`, `q(delta) = -2`, `T_Co = <h> perp E_10(2)`,
`E_10(2) = U(2) perp E_8(2)`).

**Step 1 (the restricted stabilizer is a preimage).**  By
def:gamma-co-groups(5), `Gamma_{Co,2} = R_{Gent}` with
`Gent = rho_{T_En}^{-1}(M)`, `M <= O(A_{T_En}, q)` the summand-preserving
subgroup [AEGS25, Def. 2.6; Ste91, Prop. 2.7].  Restriction carries
`Stab_{O(T_En)}(delta)` bijectively onto `O(T_Co)` -- an element stabilizing
`delta` preserves `delta^perp = eta(T_Co)` and so is `phi + id`, and conversely
-- and by the action formula `phi + id` acts on `A_{T_En} = H^perp/H` by
`[(x,0)] -> [(bar rho(phi) x, 0)]` under the isomorphism
`kappa: A_{E_10(2)} -> A_{T_En}` (prop:gamma-co-images, first paragraph of the
proof).  So `rho_{T_En}(phi + id) = kappa bar rho(phi) kappa^{-1}`, and

$$
R_{Gent} = \{\phi in O(T_Co) : \bar\rho(\phi) \in \kappa^{-1} M \kappa\}.
$$

**Step 2 (the page's `P`).**  prop:gamma-co-images(3) evaluates that set:
`R_{Gent} = bar rho^{-1}(P)` where `P` is the subgroup of `O(q_{T_Co})` the
proof describes as preserving `A_{U(2)}` **and** `A_{E_8(2)}`, the summands of

$$
w^{\perp} = A_{U(2)} \oplus A_{E_8(2)}, \qquad w = [h/2],
$$

the orthogonal decomposition of the perpendicicular of the characteristic class
`w` inside `A_{T_Co} = <w> perp A_{E_10(2)}`.  Its proof runs: every
`sigma in O(q_{T_Co})` fixes `w` (part 2: `w` is the characteristic class,
`b(w,x) = q(x)`), hence preserves `w^perp`; and `phi + id` lies in `Gent` exactly
when `bar rho(phi)` preserves the two summands.

**Step 3 (the two descriptions of `P` coincide -- the step the driver needs).**
Preserving both summands is the same as preserving `A_{U(2)}` alone, because
`A_{E_8(2)}` is the orthogonal complement of `A_{U(2)}` *inside* `w^perp`: for
`sigma` preserving `w^perp` and `A_{U(2)}` setwise,
`sigma(A_{U(2)}^{perp} cap w^{perp}) = sigma(A_{U(2)})^{perp} cap w^{perp} = A_{E_8(2)}`.
So `P = Stab_{O(q)}(A_{U(2)})`, which is the driver's point stabilizer.

*The one thing this could fail on.*  An isometry of `w^perp` could in principle
**swap** the two summands, and then the stabilizer of the decomposition would be
strictly larger than the stabilizer of the summand -- but an isometry of `A` is a
bijection of the class set, so it cannot carry a subgroup of order `4` onto one
of order `|A_{E_8(2)}| = det E_8(2) = 2^8 = 256`.  Hence no swap exists, the two
stabilizers coincide, and `P` is the driver's group under either reading of
"the stabilizer of the decomposition" (ordered, or unordered as a set of
subgroups).  That is the only hypothesis, and it is arithmetic:
`4 != 256`.

**Conclusion.**  Composing, `Gamma_{Co,2} = R_{Gamma_{En,2}} = bar rho^{-1}(P) =
bar rho^{-1}(Stab_{O(q)}(A_{U(2)}))`, which is the driver's group.  The inclusion
that holds unconditionally is `R_{Gamma_{En,2}} subseteq bar rho^{-1}(P')` for
`P'` the full stabilizer of the unordered decomposition, with equality exactly
when the summands are not isometric; here they are not (`4 != 256`), so equality
holds.

## What the proof rests on, and what it does not

* def:gamma-co-groups(4),(5) -- the definition of `R_Gamma` and of
  `Gamma_{Co,2}`; read at research `writing/coble/lattices-and-moduli/lattices.md`.
* prop:gamma-co-images(3) and its proof -- `R_{Gent} = bar rho^{-1}(P)`, the
  bijection `phi + id <-> phi`, and the action formula on `A_{T_En}`.
* AEGS25 Def. 2.6 / Ste91 Prop. 2.7 for `Gent = rho^{-1}(M)`, which is the one
  step taken by citation rather than recomputed: the library's
  `coinvariant_extension_subgroup` builds `Gamma_{En,2}` as
  `rho^{-1}(gamma rho_I(Stab_{O(I)}(h)) gamma^{-1})` and its own docstring
  states that this is the finite-character preimage the gluing criterion gives.
  Nothing in this note's two equalities depends on that beyond it being
  `rho^{-1}(M)` of *some* subgroup `M` carried by `kappa` to the
  summand-preserving one.
* **Not used:** any count, any orbit row, any image run.  In particular the
  `T_En`/`T_Co` restricted-stabilizer row is a reproduction with its own cost
  (`results/issue286-the-restricted-stabilizer-cost.md`); it can confirm the
  computation but cannot decide the statement, and nothing here waits on it.

## The small case, as the check

`--lattice small` on `L = U + U(2) + <-2>`, `delta` the `(-2)` generator,
`delta^perp = U + U(2)`: the restriction of `Stab_Gamma(delta)` to
`delta^perp` has `|rho(R)| = 2`, equal to the stabilizer of the class set the
driver indexes by, with spinor signs `40` of `+1` and `21` of `-1`
(`.scratch/w286-probes/fixed-restricted-five.log`, 24.4 s).  That is the
construction reproducing the driver's group at a size one command reaches; it is
the green of the test below, and it is a reproduction of the computation, not
the proof.

`tests/lattices/test_the_coble_point_is_a_summand_no_isometry_swaps.sage`
asserts the two steps above that a computer can be asked: on `T_Co`,
`|A_{U(2)}| = 4`, `|A_{E_8(2)}| = 2^8 = 256`, `|[h/2]^perp| = 4 * 256 = 1024`
and `2 * 1024 = |A_{T_Co}| = 2048`, with the three summands pairwise orthogonal;
and on `A1 + A1`, where the two summands have equal order, the lattice isometry
exchanging the two `A1`s swaps their classes, so there the stabilizer of one
summand is a proper subgroup of `O(q)`.  Two tests, 2.88 s and 2.36 s.  Neither
is red on an earlier commit: this round's repair is a proof, and the file is the
part of it a computer can check.
