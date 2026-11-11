# #286: the integral lift locus is indexed, not listed

The chain record of 2026-11-11 names the regression this repairs: before `9fa28c1f51` the
`O(T_Co)` row of `L.Aut().isotropic_orbit_representatives(1)` returned in 66.0 s (#329);
from that commit each `integral_parameter_classes` call materializes the union of the
passing cosets and the transvection kernel as one `finite_ordered_set` — 131072 classes on
`T_Co` — once per candidate the port's `_isotropic_pointed_isometry` tests
(`recursive.py:1720`), and `900e866b09` counted ten such loci before 2000 s.

`9fa28c1f51` was needed: the locus it replaced was **wrong**, not merely slow.  It reported
the kernel of `a + mP |-> s(a) + L'` as the locus, and that converse fails at divisibility
`d > 1` — at `d = 2` the parameter `f/2` gives `E_{f,f/2} = id`, an integral isometry whose
parameter is not a lattice vector — so the kernel is a proper subset of the locus
(`U(2) + U(2)`: 4 classes reported, 16 integral; `U(4) + <2>`: 2 reported, 4 integral;
`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`,
committed red at `305f779`).  `T_Co` has `d = 2` for every basis vector.  The 66 s route is
therefore not restorable, exactly as `results/issue310-basis-independence.md`'s follow-up
states: owner-level fix (1) there is this change.

## The repair

`integral_parameter_classes` returns the same set — the union of the transvection-kernel
cosets whose representative lifts — presented as the image of the passing representatives
and the kernel under the coset addition:

```python
cosets = finite_ordered_set(passing).product_with(finite_ordered_set(transvection_kernel))
...
locus = Sets().image_set(Sets().Mor(cosets, classes_module)(sum_of), cosets, inverse=pair_of)
```

the indexed image-set shape `_integral_lift_locus` already uses for the lift locus itself
(`classes.product_with`, `Sets().image_set`).  The inverse `pair_of` names both components
of the pair: the unique passing residue `r` with `value - r` in the kernel, and the kernel
class `value - r`, returning `None` off the image, which is the decision extension
`_enumerated_image_set` documents.  The union is never listed: cardinality and emptiness
are decided from the factors (`|passing| * |K|`), iteration runs through the product's own
index, and membership runs the inverse.  Nothing else in the method changes: the quotient,
the Smith form, the kernel enumeration and the per-coset lift tests are the same code.

## Measured, before and after, one machine, one load window

The same phase probe on two worktrees at the same base commit `fd625409d5`, pristine and
with this change, on `T_Co`'s identity-marking torsor, under a 4-CPU VM carrying three
foreign heavy jobs (load average 14-19 during the window; every wall time below is
load-inflated, which is why the two runs are compared in one window rather than against
the quiet-machine record):

| phase | pristine `fd625409d5` | indexed |
| --- | ---: | ---: |
| quotient, coordinates, Smith form | 2.61 s | 1.78 s |
| transvection-kernel enumeration (1024 classes) | 1.72 s | 1.85 s |
| representative lift tests (256, 128 pass) | 213.92 s | 235.79 s |
| **returned-set construction** | **213.19 s** | **1.26 s** |
| `cardinality()`, first element | 0.00 s | 0.00 s |

Logs: `.tmp/p286-phases-base.log` (pristine, old union tail), `.tmp/p286-phases.log`
(indexed).  On the quiet machine of the `9fa28c1f51` record the same split was 36.2 s of
lift tests and 46.6 s of ordered-set hash pass per locus (86.5 s), so the indexed shape
takes one locus to the lift tests alone.  The 256 per-coset representative lift tests
are the remaining per-locus cost, and they
are the same code as before (`900e866b09` §4 names the coordinate evaluation it needs);
they are not touched here.  Correctness on the controls is pinned by the committed test
`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`
(16 = 16 and 4 = 4 on the divisibility-two and -four controls) and on `T_Co` by the
verify probe (`.tmp/p286-verify.log`: 131072 = 131072, first element the zero class,
inverse round trip checked, `is_empty()` decided).

## The gate

`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`,
`test_rational_coordinates_of_a_lattice_vector.sage`,
`test_integral_reduction_lift_witness.sage`,
`test_the_coble_lattice_line_orbit_call_returns.sage`: **8 passed in 783.30 s**
(the `O(T_Co)` row itself 770.73 s, the machine's load falling from 7.5 to 2.5 during the
run), test lint clean.  Log `.tmp/p286-gate2.log`.  A first gate attempt at a 3900 s cap
was killed by a load spike of 14-24 (`launcher exit: 124`, `.tmp/p286-gate.log`); the
re-run at a 7200 s cap passed.

The group rows on `T_Co` are recorded in `results/issue286-tco-rows.md`.
