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
