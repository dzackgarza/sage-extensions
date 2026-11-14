# K_v from the integral lift locus: repairing #405 and deleting the parallel construction

`IsotropicVectorReductionImage.kernel_generators` no longer builds `K_v`.  The kernel of
the identity reduction's rational lift torsor at the line is `K_v`, and
`isotropic_lifts.IsotropicReductionLiftTorsors.integral_kernel_group_generators` is its
owner; that owner's integral lift locus was wrong (#405), so it is repaired here and the
consumer reads it.

## The defect in the locus (#405)

`integral_parameter_classes` decides the locus through one test per coset of
`P/mP` modulo `S = {a : s(a) ∈ L'}` and then presents the union of those cosets.  Two
errors in its class coordinates made that union a union of the wrong cosets:

* The section's coefficient matrix `A` — one *column* per parameter generator — was filled
  from the flat list of those columns row by row, which for a `(12, 10)` shape scrambles the
  entries.  Its Smith form read `(1,1,1,1,1,1,2,2,2,8)` with 64 representatives of `P/S`,
  where the matrix read by columns has ten ones and 1024.
* The Smith coordinate change was inverted: `N A = U⁻¹ D V⁻¹` puts the kernel condition on
  `(V⁻¹ a)ᵢ`, so the representatives are `a = V u`; the code enumerated `a = V⁻¹ u`.

The per-class lift test was also a hand-built coordinate product (`eichler_transvection_matrix
* base_images`) with the base point's images transposed, so a coset whose lift is not
integral could pass.  It is now the owned composition `eichler_transvection(f, s(a)) * base`
and that composition's own `integral_restriction`.

Smallest control that shows the old defect: `U(2) + U(2) + <2>`, rank 5, divisibility two —
all 64 classes of `P/mP` were reported as in the locus while 32 of them lift.  It is now a
test in `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`.

## K_v at Sterk's fourth cusp

At the line through Sterk's `2e' + f' + ᾱ₁` of `T_En = U ⊕ U(2) ⊕ E8(−2)` (card 029J row
4.3.8, Math. Z. 207 (1991), p. 23): period 4, denominator 2, ten Smith invariants one, 1024
representatives of `P/S`, 256 of them passing, `|K| = 1024`, locus `4⁹` classes.  The
identity marking's base point is itself integral here, so the locus is the subgroup of index
4 the count exhibits: a passing class plus a kernel generator stays integral and a refused
class plus the same generator does not.

The family `integral_kernel_group_generators` returns has 275 members (the locus'
representatives, the transvection kernel's generators, the period's generators); every one
has an integral restriction, and their images under `ρ` generate a group of order **256** —
the order the removed parallel construction reached, from a different construction.
`.tmp/qc-evidence/issue452-locus-cosets.log`.

## What the consumer lost

Deleted from `kernel_generators` with the parallel construction: the Gram matrix by a double
comprehension over `lattice.b`, the hand-written transvection matrix, the private
`_isometry_from_column_matrix` call, the enumeration of all `d^rank` residue classes and the
matrix integrality test.  What replaced them is one call to the owner plus the two
assertions that state `K_v` (fixes `v`, acts trivially on `N`); the second *is* the Levi
map's statement, so the removed cross-check is not re-added.

The coset reduction of `_kernel_coset_representatives` translates by left multiplication,
which is a coset decomposition because `ρ(K_v)` is abelian; that is now stated with
equation (5) of Gritsenko–Hulek–Sankaran (arXiv:0810.1614, §3.1, printed p. 9) instead of
being relied on silently.  `DiscriminantImageMembership.engine_elements` and
`meets_translates` were left as they are: both are declared operations of the membership
object with their purpose and invariants documented, and the reviewer's concern is about the
declaration rather than about a use the code makes of an undocumented one.

The class docstring's sign was wrong and is corrected: `s_{a+v}s_a = E(v, a/2)`, not
`E(v, −a/2)` (equation (4), printed p. 8, at `q(a) = −4`).

## Evidence

* `.tmp/qc-evidence/issue452-controls.{py,log}` — the control search on `eb07c43`; the
  `U(2) + U(2) + <2>` disagreement.
* `.tmp/qc-evidence/issue452-locus-cosets.{py,log}` — the corrected reading: 256/1024,
  `|K| = 1024`, the family integral, `ρ(K_v)` of order 256, coset constancy sampled.
* `.tmp/qc-evidence/issue452-locus-tests.log` — the lift-locus file, 4 passed.
* `.tmp/qc-evidence/issue452-reduction-image-tests.log` — the reduction-image file.

## Not verified here

* No `T_Co` row was run.  The family's size is the index of `K` in the locus (275 at this
  line), so that index, not the locus' size, is what a `T_Co` measurement has to bound.
* The repository's CI diagnostics have never run on this repository (ai-review-ci#491), and
  `just tensor-boundary`, `just test-ci` and the mypy tier were not run here.
* `Lattices.ParentMethods.eichler_transvection_matrix` and `rational_gram_matrix` now have no
  caller: the locus was their only consumer and it composes isometries instead.  They were
  left in place rather than deleted inside this repair, but they state equation (4) a second
  time in coordinate form, and the module layer has no owned lowering of a morphism to its
  coefficient matrix for a consumer that would want one.
