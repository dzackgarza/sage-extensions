# #603: the divisibility-2 cusp — what is established, and the corrected route

Status: **the construction is still not delivered.** This note corrects the
route the previous note claimed and records the measurements taken; it does not
claim an item met.  Everything is on the adopted runtime in a worktree of
`main = 25d2190` (tree bound at `/repos/sage-extensions`, the port at `/work`).

## Retraction: the rank-two fixed part is not the repair

The previous note said the repair was "one generalization" of the non-isotropic
construction — its fixed part from rank one to rank two over `L_0 = <v, w> + K~`.
That is wrong, and here is where it breaks.  An isometry `g` with `g(v) = v`
sends `w` to `w + z` with `z in J = v^\perp`, because `b(v, .)` is preserved and
`J` is exactly the kernel of `b(v, .)`.  So `g(L_0)` is not `L_0`, and
"`(1 + sigma)(H) = H` for `H = L/L_0`" is neither necessary nor sufficient for
`sigma` to lie in `M_I = rho(P_I)`.  The argument of the non-isotropic case needs
`g` to fix the *whole* reference lattice pointwise; at an isotropic vector it does
not, and the shift is precisely the unipotent radical that the rank-one
construction carries as its kernel factor.

The splitting itself stands (it was verified: `K~` is isometric to `K_I`, and
`(v, w, K~)` has full rank with nonzero determinant on both `0125` and `026E`),
but it gives a nondegenerate `L_0`, not the criterion.

## What the membership needs

`M_I = rho(P_I)` is *decided* elementwise by
`IsotropicReductions._levi_image_contains` (`lattices.py:13185`), at rank one by
the emptiness of the two lift fibres over a complete residue system, and the
exactly-sequenced statement is
`P_I^1 = <lifts of M_I> * <unipotent_kernel>` (`RankOneParabolicLeviExactSequence`).
What is missing is a *presentation* of `M_I` as the stabilizer of a point in a
finite set, which is the input the Schreier step consumes.  A fibre is a torsor
over a finite residue set, so the presentation is available in principle — as the
action of `P_I` on the finite set of transport residues — and that is the piece
still to be written.

## Measurements this turn

`N = U + U(2) + E8(-2)`, card `029J`:

| call | result |
| --- | --- |
| `N.discriminant_representation_is_surjective_by_theorem()` | `True`: `rho(O(N)) = O(A_N)`, so an index in `O(A_N)` is an index in the image |
| `A_N` | `(Z/2)^10`, `|A_N| = 1024` |
| `|O(A_N)|` | `46998591897600 = 2^21 * 3^5 * 5^2 * 7 * 17 * 31` |
| setwise line family at `L_1 = Ze_1` (the #459 construction) | 26 members in **16.0 s**; image with `-id` has order `|O(A_N)|`, **index 1** — the card's `L_1` value, by an owned route and not by the pointed family |
| setwise line family at `L_2 = Ze_3` | **not returned** in 4 min (stopped) |
| `stabilizer_discriminant_image()` at `L_1` (the #312 route) | **not returned** in 5 min (stopped) |
| pointed call at `L_2` (earlier rounds) | **not returned** in 400 s, twice |
| pointed call at `0125`'s two hyperbolic generators (earlier) | 72.4 s and 105.5 s |

So the card's `L_1` index is reproduced by `rho` of #459's own family with
`rho` surjective by theorem — the cheap and owned half — and the discriminating
`L_2` index, 527, is blocked at the same place from three different directions:
the parabolic's `O(K_I)`, its setwise family, and its #312 image all stall at a
divisibility-2 cusp with `K_I` of rank 10.  That is one blocker, not three, and
it is `O(K_I)`'s own generating family.

Nothing here was changed to make a number look better; no test asserts a value
that was not measured.
