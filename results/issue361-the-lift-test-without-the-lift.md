# #361: the lift locus asks its lift test without building the lift

**Result: at `main` `7761145`, the profiled row `NamedLattices.Tco.Aut()
.isotropic_orbit_representatives(1)` spent 92.8% of its 636.82 s inside
`isotropic_lifts.integral_parameter_classes`, 85.0% in the per-coset lift test
`lifts_integrally` that `9fa28c1f51` introduced — 78.1% of the row inside
`parameterization`'s forward map, split into the transvection (35.3%), the torsor's
membership check of the composed lift (39.0%) and `integral_restriction` (7.4%).  The
lift test now forms the lift's coordinate matrix from the owner's transvection matrix
and reads integrality from it, and the parameter of a class is read off its own
coordinates instead of solved for; the row returns its one representative in
100.06 s against the 636.82 s it took on the same machine before.**

## The step, and the commit that made it slow

The row, one profiled run on `7761145` (5 ms sampler, `sys._current_frames`, load
average 3.6-5.5 on 4 CPUs with foreign jobs): 636.82 s, 57895 samples, 1
representative.

| inclusive | time | share | frame |
| --- | ---: | ---: | --- |
| row | 636.8 s | 100% | `LatticeIsomorphisms.isotropic_orbit_representatives` (`lattice_morphisms.py:4907`) |
| `integral_members` | 591.2 s | 92.8% | `isotropic_lifts.py:278` |
| `_integral_lift_locus` | 586.7 s | 92.1% | `isotropic_lifts.py:234` |
| `integral_parameter_classes` | 581.1 s | 91.3% | `isotropic_lifts.py:586` |
| **`lifts_integrally`** | **541.1 s** | **85.0%** | **`isotropic_lifts.py:584`** |
| `parameterization`'s forward map | 497.5 s | 78.1% | `isotropic_lifts.py:193` |
| the torsor's membership check | 248.3 s | 39.0% | `set_categories.py:4437 __contains__` via `g_sets.py:2008`, `framed_free_modules.py:103`, `module_morphisms.py:1126` |
| `eichler_transvection` | 224.6 s | 35.3% | `lattices.py:8332` |
| `integral_restriction` | 46.9 s | 7.4% | `lattice_morphisms.py:1643` |
| module `preimage` | 33.2 s | 5.2% | inside `lifts_integrally` |

Leaf time is 51.5% in `ring_foundation.py` (owned ring element construction,
conversion and equality) and 15.3% in `sage/categories/category.py` (category
membership), which is what "build two isometries and check one belongs to the
torsor" costs when it is done once per class.  One `T_Co` locus (131072 classes,
256 tested cosets) was ~53 s of the row.

`9fa28c1f51^` has **no** `lifts_integrally` at all — it is the commit that
introduced the per-coset lift test, because the kernel it used before was wrong at
divisibility 2.  `c32f8c1` then replaced the locus's listed union with the image of
its factors but kept the lift test.  So the step this row pays for is
`9fa28c1f51`'s, at `isotropic_lifts.py`.

## The repair

At the transvection's owner, `Lattices.ParentMethods`, next to
:meth:`eichler_transvection`:

- `eichler_transvection_matrix(isotropic, orthogonal)` — the same formula as a single
  matrix `T = 1 - E(A^t G) + A(E^t G) - ½q(a) E(E^t G)` in the selected basis, whose
  columns are the images of that basis;
- `rational_gram_matrix()` — the Gram matrix the coordinate form needs, cached as a
  datum of the lattice.

In `integral_parameter_classes`, the lift test (`lifts_integrally`) now forms
`T(f, s(a)) · B` — the transvection's matrix times the base point's coordinate matrix
`B`, computed once per locus — and decides integrality exactly as
`integral_restriction` does on its integral branch: every coordinate in the base ring,
and unit determinant.  The parameter of a class is read off the class's own
coordinates (`parameter_at`) instead of being solved for by `quotient.preimage`.

The statements it uses, with their sources:

- the transvection formula `t(e,a)(x) = x - b(a,x)e + b(e,x)a - ½q(a)b(e,x)e`:
  Dawes, section 2 equation (7), as transcribed in
  `notes/topics/coble-enriques-lattice-theory/reflective-two-elementary-lattices.md`
  and as stated in Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, (4)--(5)
  — the citation `eichler_transvection` and the module docstring already carry;
- the lift at a parameter is `phi(a) = t(f, s(a)) · base`: `parameterization`'s own
  definition (`isotropic_lifts.py:182`), which is where the formula is applied today;
- a square integral matrix has an integral two-sided inverse exactly when its
  determinant is `±1`, and both directions must preserve the lattices:
  `integral_restriction`'s docstring, whose integral branch is the predicate copied
  here;
- the class's coordinates name a parameter of it: `parameter_class`'s own
  construction (`V^-1 indices` in `P/mP`), so `linear_combination` of those
  coefficients is a parameter of that class, and `mP ⊆ K` is what makes any
  representative answer integrality alike (the method's own divisibility argument).

## Measured

One `T_Co` locus (`integral_parameter_classes` of the identity-marking torsor at the
primitive isotropic vector `e_ep`, 131072 classes, 256 tested cosets), the same
machine:

| version | one locus |
| --- | ---: |
| `7761145`, from the row profile | ~53 s |
| after the transvection matrix, `preimage` still solved per class | 13.89 s |
| after the parameter read off its coordinates | 3.58 s |

The controls of the locus test (`U + <2>`, `U + U + <2>`, `U(2) + <2>`,
`U(2) + U(2)`, `U(4) + <2>`) keep their cardinalities 2, 8, 2, 16, 4 and take
0.146 s, 0.185 s, 0.197 s, 0.159 s, 0.372 s; at these ranks the per-locus fixed cost
(the base point's coordinates, the Gram matrix) is larger than the per-class cost it
replaces, which is why the win appears only at `T_Co`'s rank and class count.

The row after the repair: **100.06 s**, returning the same one representative.

The exactness ground truth is the committed test, which decides the locus class by
class against the definitional lift on all five controls:
`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`
— 6 passed in 177.94 s with the row test among them.

## What this unit does not claim

- No count or representative changed: the row still returns one orbit whose
  representative is a primitive isotropic line, which is what
  `test_the_coble_lattice_line_orbit_call_returns.sage` asserts.
- The remaining per-locus time is diffuse preamble plumbing (category membership
  checks 5.8%, ring element construction 4.0%, `class_of`'s class arithmetic 10.0%
  of one locus); no single step dominates it any more.
