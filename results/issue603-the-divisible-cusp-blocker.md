# #603: why the pointed call is still the port's at a divisibility-2 cusp

Status: **the repair named in the last report is not delivered.** This note records
what it needs, what the tree already decides, and why neither route was taken in
the time available. Measurements are on the adopted runtime in a worktree of
`main = c3ff64d` (tree bound at `/repos/sage-extensions`, the port at `/work`).

## The two measurements

| lattice, vector | card | pointed call |
| --- | --- | --- |
| `N = U + U(2) + E8(-2)` at `L_1 = Ze_1` (div 1) | `029J` | returns, 36 generators, 11.9--52.1 s, stabilizer image index **1** |
| the same at `L_2 = Ze_3` (div 2) | `029J` | **does not return**: inside the call at 400 s in two runs |
| `U(2) + E8(-2)` at its two hyperbolic generators (div 2) | `0125` | returns, 531 members, **72.4 s** and **105.5 s** |

The card's discriminating index is `L_2`'s **527** (the `L_1` row's 1 is what any
family generating everything else gives). So the card comparison stays narrow
until a divisibility-2 cusp is answered by the construction.

## What the construction needs, and what is missing

`_isotropic_line_stabilizer_generators` builds `P_I = <one lift per generator of
O(K_I)> * <kernel>` and refuses when a generator of `O(K_I)` has no integral
lift, because a family built on the others generates only a subgroup. The missing
input is therefore **generators of `M_I = rho(P_I)`, the image of the parabolic in
`O(K_I)`**, which at a divisibility-2 cusp is a proper subgroup.

What the tree already decides: `IsotropicReductions._levi_image_contains`
(`lattices.py:13185`) decides membership in `M_I` elementwise, at rank one by the
emptiness of the two lift fibres over a complete residue system. So `M_I` is
*knowable*, but not *presented*: no finite set with `M_I` as a point stabilizer is
computed anywhere, which is what the non-isotropic construction and the isotropic
Schreier step both consume. The two routes to it are:

* **the degenerate glue.** `J = v^\perp` carries the radical `I`, `J/I = K_I`, and
  a complement `K' \cong K_I` lifting `K_I` into `J` gives a gluing subgroup
  `H_J = J/(I + K') \le A_I \oplus A_{K_I}` whose stabilizer in `O(K_I)` is
  `M_I` -- the same lemma as the non-isotropic case, applied to a *degenerate*
  lattice, where the class computation this repository's Smith-form bookkeeping
  uses (it inverts the Gram matrix) does not apply as written.  This is the route
  the previous report named, and it is one construction, not a patch: the
  degenerate case needs its own class model.
* **owning `O(K_I)`.** `L_2`'s `K_I` has rank 10 and its own generating family is
  the indefinite port's, which is where the 400 s goes.  Owning `O` of an
  indefinite rank-10 lattice is not #603's scope.

Neither was written and validated here. Nothing was changed to make a number
look better: the row script states `L_2`'s cost, and the tests that exist assert
what they can.
