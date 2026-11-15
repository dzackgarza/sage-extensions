# The lift locus' kernel is read through the Smith change of basis

`isotropic_lifts.IsotropicReductionLiftTorsors._integral_parameter_cosets` presents the
integral lift locus of a marked-line reduction as a union of cosets of the transvection
kernel.  Three things it said or did assumed the saturation was a coordinate cube; it is
not, and on a section whose Smith steps differ the locus came out too small.

## The statement that was wrong

Write `s` for the target section, `A` for the matrix of its coordinates on the parameter
lattice's selected generators, `N` for the integer clearing their denominators, and
`U (N A) V = D` for one Smith form.  Then `N A a = U^{-1} D (V^{-1} a)` is integral exactly
when `(V^{-1} a)_i` is a multiple of `step_i = N / gcd(D_ii, N)`, so

    S = {a : s(a) in L'} = V(prod_i step_i Z).

The docstring wrote `S = prod_i step_i Z` and justified it by `V` being unimodular.
Unimodularity preserves the index of the cube, not the cube: the swap carries `Z x 2Z` to
`2Z x Z`.  The two agree as *sets* exactly when the steps are all equal, and the kernel's
classes and generators were read in the same `u`-coordinates while `shifted` adds them to
the representatives in the parameter lattice's own `a`-coordinates.

## Why the earlier evidence could not show it

Every specimen measured so far has all steps equal: card 029J's (4.3.8) line has ten steps
`2`, and the `U(2)`-based controls have steps equal to the marked vector's divisibility.  A
sweep of 140 (lattice, marked vector) pairs over `U(k)`, `U(2)`, `U(4)`, `U(8)` summed with
`<2>+<2>`, `<2>+<4>`, `<4>+<4>`, `A2`, `A2(2)`, `A3(2)`, `D4(2)` and small-coefficient
marked vectors found the section's Smith invariants all one in the sweep's specimens whose
marked vector is a basis vector.  Unequal steps need a non-basis marked vector *and* a definite
part of large determinant; the first controls that have them are:

| lattice | marked vector | `div` | period `m` | `N` | Smith invariants | steps |
| --- | --- | --- | --- | --- | --- | --- |
| `U + A3(2)` | `-2e0 + 2e1 - e2 + 2e3 - e4` | 2 | 8 | 4 | `(1, 2, 2)` | `(4, 2, 2)` |
| `U + <4> + <4>` | `-2e0 + 2e1 - e2 - e3` | 2 | 8 | 4 | `(1, 2)` | `(4, 2)` |
| `U(4) + <2> + <2>` | `-e0 + e1 + 2e3` | 4 | 64 | 32 | `(1, 2)` | `(32, 16)` |
| `U(4) + A2(2)` | `-2e0 + e1 + 2e3` | 4 | 32 | 16 | `(1, 2)` | `(16, 8)` |

## What the reading cost

On `U + A3(2)` at that marked line — period eight, `|P/mP| = 512`, `|P/S| = 16`,
`|K| = 32` — reading the saturation as the cube returned **256 of the 512 classes**, while
every class of the control lifts integrally; the returned kernel was a different subgroup
of `P/mP` of the same order.  With the readings taken through `V` the locus is all 512, and
the kernel classes it returns are the classes of `K` by its own definition.

`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` carries
that control and compares the reported locus with every class of `P/mP` decided by the lift
itself, as its four older controls do.  It cost 20.17 s failing on the pre-repair tree and
21.56 s passing on the repaired one, which is the price of the 512-class enumeration; the
four older controls cost the file about five seconds in total.

## Also done in the same pass

* `Lattices.ParentMethods.rational_gram_matrix` and `eichler_transvection_matrix` deleted
  with their doctests: no caller, and they restate equation (4) of Gritsenko–Hulek–Sankaran
  (arXiv:0810.1614, §3.1, printed p. 8) in coordinates beside `eichler_transvection`
  (`CONTRIBUTING` OWN-24).
* `DiscriminantImageMembership.engine_elements` deleted and `meets_translates` made to take
  and be handed owned `O(A_L)` elements only, with the conversion kept in a private cache
  (`OWN-04`); the unused `image` accessor went the same way.
* The `kernel_generators` docstring no longer says equation (10) is "coprime with" the
  fractional-parameter transvections — it is a route to integrality, not a criterion for it
  — and the issue numbers `(#452)`, `(#361)` left the source for the commit bodies.
* `integral_parameter_period()` is read through `NN` rather than lowered by a bare `int()`.

## Not verified here

* No `T_Co` row was run.  The count of lift tests the repair costs there is unchanged, since
  the enumeration of representatives is untouched.
* The reduction-image file (`tests/lattices/test_the_isotropic_reduction_image.sage`) passes
  on the repaired tree: 11 passed in 1168.99 s, the two-lifts test at 239.08 s and the
  five-row chamber test at 547.53 s.  So `K_v` read from the repaired locus and the sifting
  membership give the same answers as before on every row that file covers.
* `tests/lattices/test_two_u_eichler_model.sage::test_approximate_generating_family_uses_exact_two_u_perpendicular_frames`
  fails on the parent tree as well, before any change here; it is not a regression of this
  repair.
