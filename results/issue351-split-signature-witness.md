# #351: the split-signature witness at the divisor-1 line, and the row it serves

## The candidate witness, and its four computed checks

The owner named the candidate: at a primitive isotropic line ``L = ZZ v`` of an even
lattice ``N``, write the orthogonal decomposition ``N = U \\oplus \\Lambda`` with
``v = e_1 \\in U`` exhibited in the selected basis, and let

``w = 1_U \\oplus (-1_\\Lambda.``

By Zemel's Proposition 1.10 (*The Structure of Integral Parabolic Subgroups of
Orthogonal Groups*, J. Algebra 559 (2020) 95--128, arXiv:1902.08264v2, p. 13) this is
the Levi part ``(1, -1)``: for an element of the parabolic with Levi part
`(M, gamma)`, the determinant is `det gamma` and the real spinor norm is the class of
`det M` times the spinor norm of `gamma`, so for the pointwise stabilizer of `v` the
sign is carried by the `O(v^perp/v)`-part alone.  The four checks are computed by the
library, never asserted:

| representative | w is an isometry | w fixes the vector | `rho(w) = 1` | real spinor norm `-1` |
| --- | --- | --- | --- | --- |
| `N` divisor-1 (`L1 = ZZ f`, own label `f`, partner `e`) | yes (the `Aut` constructor verifies form preservation) | True | True | True |
| `N` divisor-2 (`L2 = ZZ ep`, own label `ep`, partner `fp`) | yes | True | True | True |
| `T_Co` divisor-2 (`ep` of the `U(2)`-summand, complement `<2> + E8(-2)` of signature (1, 8)) | yes | True | True | True |

The measurements are `.tmp/351-witness2.log` and `.tmp/351-diag2.log` (the pinned
image, the port at `991b88b0`, the #351 worktree as the provider): the witness at the
divisor-1 line in 8.4 s and at the divisor-2 line in 0.1 s, the fix, the trivial image
and the negative spinor norm computed and printed element by element.

## The complement's discriminant image, and the class-stabilizer equality

The isometries `1_plane + gamma` with `gamma` in the orthogonal group of the
complement fix the representative's plane pointwise, so they lie in the line
stabilizer, and their discriminant image is the discriminant action of `gamma` on the
complement's own discriminant group.  The stabilizer's image therefore contains the
complement's image; at a divisor-1 line -- where the complement's discriminant group
is the ambient one, the plane contributing nothing -- the class-stabilizer equality
`rho(Stab(v) = O(A_L)` therefore holds exactly when that image is surjective:

| representative | complement | image order | target order | surjective | time |
| --- | --- | ---: | ---: | --- | ---: |
| `N` divisor-1 | `U(2) + E8(-2)` | 46 998 591 897 600 | 46 998 591 897 600 | True | 6.8 s |
| `N` divisor-2 | `U + E8(-2)` | 348 364 800 | 348 364 800 | True | 10.6 s |
| `T_Co` divisor-2 | `<2> + E8(-2)` | 348 364 800 | 348 364 800 | True | 8.9 s |

## The code site, and what is wired

The owner is `OrthogonalCharacterQuotient.isotropic_line_stabilizer_image`
(`src/sage_extensions/categories/orthogonal_quotients.py`, the Eichler gate at the
`_two_hyperbolic_planes` check.  Three changes are wired there:

* `_split_signature_witness` (module level, after `_two_hyperbolic_planes`) builds
  `w` from the Gram matrix -- the fixed plane is the representative's own basis
  direction together with the basis vectors pairing nontrivially with it, the
  complement is the rest -- and computes the four checks; a witness that fails any
  check is not a witness, and `None` is returned.
* `_complement_discriminant_surjective` (module level) reads the complement off the
  same split, forms its Gram matrix as the pairing matrix of the complement's basis
  vectors, and compares the complement's discriminant image with its target.
* The Eichler gate keeps its refusal for lattices that exhibit two hyperbolic planes
  and now routes through the two computed certificates where it does not: the
  witness and the complement's surjectivity.  The zero-class branch and the flip
  search try the witness FIRST, the reflection enumerations only as the fallback --
  the enumerations are a slow route for an indefinite lattice, and the witness
  certifies the same conclusion.

## What is blocked

The row itself -- `test_the_stable_plus_line_row_is_the_card_otilde_plus_row` at
`9a2097f16d` -- does not return inside the budget.  Four runs (1500 s, 2400 s, 3300 s
and 3000 s inner timeouts, `.tmp/351-testrow.log` through `.tmp/351-testrow4.log`)
were each killed at the timeout; the last at 6.1 GiB peak, the memory signature of
the port's marked-lattice enumeration, which is the exact integral route the
certificates were to replace.  The gate passes when its two certificates are called
directly on the row's own representatives (`.tmp/351-diag2.log`, both lines, the
witness in 8.4 s and 0.1 s, the complement in 6.8 s and 10.6 s), and the ambient
side of the row is measured and affordable (the two `O(N)`-line orbits in 60.6 s
and 124.7 s, the ambient discriminant image of order 46 998 591 897 600 in 246.8 s,
surjective).  The discrepancy -- the certificates pass directly and the row still
falls through -- is not diagnosed here, and no count is asserted anywhere.  The VM
was shared with four other heavy jobs for most of these runs, which is why even the
affordable steps were measured under load.

## What is not claimed

The `Otilde+` row is not green and the count `528 = 1 + 527` is not asserted.  The
witness and the complement's surjectivity are measured, the wiring is in the tree,
and the row's blocker is documented rather than papered over.  Nothing here weakens
a test or adds a guard, a timeout or a profile as a deliverable.

## The row's gate, repaired from the vector itself

The discrepancy is diagnosed and repaired: the certificates pass on the basis
vectors but the row's own representatives are computed vectors, and both gates
fail at the same lookup.  The instrumentation (`.tmp/351c-instrument.log`, the
pinned image, the port at `991b88b0`, the #351c worktree as the provider, 45.2 s
total): the two ambient `O(N)`-orbit representatives of `N = T_En` are computed
vectors, and at each the Eichler gate returns `None` through both of its
certificates for the same reason -- `_split_signature_witness` looks the
representative up among the basis labels (`own = [label ... if
generators[label] == vector]`) and returns `None` when the vector is not a basis
vector, and `_complement_discriminant_surjective` repeats the lookup and returns
`False`.  Both gates fail at the label lookup for both representatives (the
witness in 0.0 s, the complement likewise), so the row keeps its exact integral
route and is killed inside it.

The repair builds the decomposition from the vector itself
(`_bezout_partner`, module level after `_two_hyperbolic_planes`): the pairing
row `b(e, g_j)` is read from the Gram matrix, the divisor is its positive
generator, and the partner `f = sum(m_j g_j)` is the Bezout combination with
`b(e, f) = divisor` -- for a divisor-1 vector this is the hyperbolic partner
with `b(e, f) = 1`, and for a divisor-2 vector the partner with `b(e, f) = 2`,
the divisor itself (S. Zemel, *The Structure of Integral Parabolic Subgroups of
Orthogonal Groups*, J. Algebra 559 (2020) 95-128, arXiv:1902.08264v2,
proposition 1.10, p. 13).  The plane is `<e, f>`, the complement is the kernel
of the two pairing constraints computed from the Gram matrix, and the witness
`w = 1_plane + (-1)_complement` is read on the module generators as the matrix
`2*Proj_plane - 1` whose `j`-th column holds the coordinates of the image of the
`j`-th generator.  The four computed checks are kept: the matrix identity
`W^t G W = G` and the integrality of `W` are computed before the `Aut`
constructor's column-matrix route, and the fix of the representative's
generating vector, the trivial discriminant image and the negative real spinor
norm are computed after it.

Validated on fixed test vectors (`.tmp/351c-diag2.log`, `.tmp/351c-diag3.log`,
`.tmp/351c-validate.log`, the same runtime): for every divisor-1 and divisor-2
primitive isotropic vector of `N` -- computed or basis -- the repaired witness
returns a witness and the repaired complement returns True, with the complement's
own orders 46 998 591 897 600 at divisor 1 and 348 364 800 at divisor 2.  The row
is green: `test_the_stable_plus_line_row_is_the_card_otilde_plus_row` returns
528 lines against card 029J's `Otilde+` row by tag, in 427.32 s (0:07:07), the
test call measured at 426.63 s and the peak tree RSS at 956 MiB.
