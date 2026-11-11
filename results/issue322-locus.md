# #322: the lift locus is a union of transvection cosets

`integral_parameter_classes` (`isotropic_lifts.py`) used to decide its residue locus by
listing the parameter module's elements and building a rational isometry per class. On
`T_Co` that module has 262144 classes and one class test costs 0.39 s, so the public call
never returned. `b9e8cfa` replaced the listing with the kernel of one map of finite groups.
That kernel is **not** the locus: the criterion it rests on fails as soon as the marked
isotropic vector has divisibility greater than one. It is now computed as the union of the
kernel's cosets whose representative passes the lift test.

## The defect in `b9e8cfa`'s proof

Eichler's transvection formula (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
(4)--(5); the owner of the formula here is `Lattices.ParentMethods.eichler_transvection`)
writes, for a primitive isotropic `f` of an even lattice `L'` and `x` in its rational span,

    E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x .

The forward direction needs no hypothesis beyond evenness: if `x` is in `L'` every term is
integral. The **converse** needs a `y` with `b(y,f) = 1`, and a primitive isotropic `f` does
not supply one. It gives only `b(f, L') = d Z` for the divisibility `d = div(f)`, and
`d > 1` is common: on `T_Co` every basis pairing is even, so `b(f, T_Co) = 2 Z` for **every**
basis vector (`.tmp/p322-probe26.log`).

At `d = 2` the parameter `x = f/2` has `b(y,x) = b(y,f)/2` and `q(x) = q(f)/4 = 0`, so the
formula gives `E_{f,f/2} = id`: an integral isometry whose parameter is not a lattice vector.
The locus therefore contains the kernel properly, and a locus computed as `{a : s(a) in L'}`
loses lifts. Measured on the controls (`.tmp/p322-cosets-RED2.log`), with the kernel of
`b9e8cfa` on the left and the classes that actually lift on the right:

| control | `div(f)` | `|P/mP|` | `b9e8cfa` locus | integral classes |
| --- | ---: | ---: | ---: | ---: |
| `U + <2>` | 1 | 2 | 2 | 2 |
| `U + U + <2>` | 1 | 8 | 8 | 8 |
| `U(2) + <2>` | 2 | 4 | 2 | 2 |
| `U(2) + U(2)` | 2 | 16 | **4** | **16** |
| `U(4) + <2>` | 4 | 8 | **2** | **4** |

The controls that agree are the ones where `d = 1`, exactly as the divisibility analysis
predicts. No control can detect the defect by testing only that the returned classes lift,
because every returned class does lift; the excluded classes are what fails.

## The criterion that does hold

For every base point and every divisibility the locus is a union of cosets of

    K = {a in P/mP : s(a) in L'},

the kernel of `a + mP |-> s(a) + L'` in `L'^vee/L' = A_{L'}`. The section lands in the
perpendicular of the marked isotropic vector, so `E_{f,s(a)}` and `E_{f,s(k)}` commute and
compose to the transvection of the sum; `phi(a) = E_{f,s(a)} phi(0)` is how
`parameterization` defines the coordinates. Hence

    phi(a + k) = E_{f,s(k)} phi(a)

(`.tmp/p322-probe14.log`: verified against the code's own `parameterization` on `U(2) + U(2)`,
`U(4) + <2>` and `U(2) + <2>`, `4/4` samples each). For `k` in `K`, `s(k)` and `-s(k)` lie in
`L'`, so `E_{f,s(k)}` and its inverse are integral on an even `L'`, and multiplying by an
integral isometry with integral inverse preserves integrality. So integrality is constant on
each `K`-coset -- integral base point or not, and independently of `d`. The
`integrality is constant on (a, k) pairs` check on the controls found no exception
(`.tmp/p322-probe14.log`: `0` pairs).

The method therefore: `K` from one integer Smith form; one representative of each coset of
`P/mP` modulo `K` (`|P/mP| / |K| = prod_i gcd(step_i, m)` of them); each representative's own
lift asked for its integral restriction -- the lift test itself, not a criterion for it; and
the union of the cosets that pass. The base-point refusal and the "`E_{f,x}` is integral
exactly when `x` is in `L'`" statement are gone, because the coset argument needs neither.
`integral_base_point_or_none` now searches the locus instead of listing `P/mP`, which was the
same listing defect one call away.

## Measured

`T_Co = <2> + E(2)`, `E = U + E8(-1)` (Dolgachev--Kondo, Izv. Math. 77:3 (2013), §3, eq.
(3.6), printed p. 513), marked `U(2)` line `<e_1>`, identity reduction
(`.tmp/p322-probe14.log`, `.tmp/p322-probe23.log`, `.tmp/p322-probe26.log`):

| quantity | value |
| --- | --- |
| `b(f, L')` | `2 Z` (divisibility 2; every basis pairing is even) |
| parameter rank, `|P/mP|`, period | 9, 262144 = 4^9, `m = 4` |
| Smith diagonal of the section's coordinate matrix | `(1,1,1,1,1,1,1,1,0)` |
| coset index `prod_i gcd(step_i, m)` | 256 |
| `|K|` (`b9e8cfa`'s locus) | 1024 |
| cosets whose representative lifts | 128 |
| **`|integral locus|`** | **131072 = 2^17**, in 86.5 s |

The cost of one locus: 256 lift tests at 0.141 s (`36.2 s`) plus `finite_ordered_set` over the
131072 classes (`46.6 s`, `.tmp/p322-probe24.log`: the additions themselves are 0.2 s; the
hash pass in the ordered-set constructor is the rest). `_integral_lift_locus`,
`integral_members()`, its `is_empty()` and `integral_base_point()` then cost 0.0 s each.

## The two consumer rows

| row | result | log |
| --- | --- | --- |
| `L.Aut().isotropic_orbit_representatives(1)` (`O(T_Co)`) | **1 orbit**, representative `-e_1`, `[v/2] = -[2]`, `div = 2`; row 424.5 s in the run that armed its profiler only afterwards, 676.7 s while two other jobs of the same 4-CPU machine ran, 1651.8 s under heavier contention | `.tmp/p322-otilde-step.log`, `.tmp/p322-probe26.log` |
| `L.stable_orthogonal_group().intersection(L.O_plus()).isotropic_orbit_representatives(1)` (`Õ⁺(T_Co)`) | **does not return**; see below | `.tmp/p322-otilde-step.log` |

Compared with research's `computations/reports/coble_isotropic_orbits.py` (runs of
2026-11-05): `|A_{T_Co}| = 2048` with 528 isotropic classes, 527 of them nonzero, and
`|Orth(A_{T_Co}, q)| = 2^21*3^5*5^2*7*17*31`. The measurement reproduces the first two
(`.tmp/p322-probe26.log`). The page's `thm:unpolarized-cusps` (transitivity on isotropic
lines) is what the `O(T_Co)` row's single orbit says; the `Õ⁺(T_Co)` row is
`sec-cusp-lifting`'s 527. No test asserts any of these counts: they are page proofs and
lattice-database card values (lattice-database#7), not card rows.

## Where the `Õ⁺(T_Co)` row stops (open)

The stack is the probe's own, kept by `sys.setprofile`, because `faulthandler` loses the
caller of a Cython frame (`<invalid frame>`, the earlier `.tmp/p322-otilde-stack.log`).
`_subgroup_isotropic_orbit_representatives` has two routes to one lift per double coset, and
on `T_Co` both are closed (`.tmp/p322-otilde-step.log`):

1. **The class route, refused.** `isotropic_line_stabilizer_image` returns `None` in 0.1 s.
   Its criterion (Eichler's, Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503) needs two
   orthogonal *unimodular* hyperbolic planes in the lattice itself, and `T_Co` exhibits none:
   every pairing of its basis vectors is even, so `_two_hyperbolic_planes(T_Co)` is `False`.
   That refusal is #315's ruling, not a defect to route around.
2. **The generator route, not returning.** With no line image, the caller asks for the
   ambient stabilizer's generators (about 60 s) and then `splitting_isometries(stabilizer)`,
   which reaches `OrthogonalCharacterQuotient._image_section` ->
   `_ambient_generators`, and there demands `O(T_Co)`'s *selected finite generating set*:

        splitting_isometries -> _image_section -> _ambient_generators
          -> has_selected_finite_group_generating_set -> selected_group_resolution
          -> _core_automorphism_generators -> _computed_group_generators
          -> marked_lattices.automorphism_group_generators
          -> recursive.orthogonal_group_generators -> eichler covering vectors

   That computation ran from 488 s to the 2100 s cap without returning, on top of the 424 s
   ambient row. It is the cost #18 already records for
   `INDUCTION.line_automorphism_generators` (1643 s stabilizer plus the port conversion), so
   the row cannot reach 2400 s by this route either.

So the owner of the step is the generator-driven character image
(`OrthogonalCharacterQuotient._ambient_generators`, with the predicate
`has_selected_finite_group_generating_set()` computing the resolution it is asked to report
on), and the unit that repairs it is #17's replacement of that image by the finite
character quotient's regular model -- not a locus question. No repair is claimed here.

## Tests

`tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` compares
the returned locus with the classes that lift integrally, over every class of `P/mP`, on
`U + <2>`, `U + U + <2>`, `U(2) + <2>`, `U(2) + U(2)` and `U(4) + <2>`; it also pins each
specimen's divisibility, so a specimen cannot silently become a divisibility-one one.

| run | tree | result | log |
| --- | --- | --- | --- |
| the new file | `b9e8cfa` (kernel) | **2 failed** (the two divisibility > 1 specimens), 1 passed, in 5.46 s | `.tmp/p322-cosets-RED2.log` |
| the new file | this tree | 3 passed in 10.31 s | `.tmp/p322-cosets-GREEN2.log` |
| gate: new file, `test_rational_coordinates_of_a_lattice_vector`, `test_integral_reduction_lift_witness`, `test_the_coble_lattice_line_orbit_call_returns` | this tree | **8 passed in 1679.54 s**, exit 0, test lint clean; the `T_Co` row itself 1673.33 s under two other jobs on the same 4 CPUs | `.tmp/p322-gate-cosets.log` |
| gate: the seven Levi/parabolic consumers | this tree | 10 failed, 14 passed in 73.36 s | `.tmp/p322-gate-levi.log` |
| the same seven | `b9e8cfa` | 15 failed, 9 passed in 36.82 s | `.tmp/p322-gate-levi-base.log` |

The 10 remaining Levi failures are a subset of the 15 that fail without this change (the
`EichlerRecursion` has no `isotropic_quotient_lift` mismatch and the port's rank-3 refusal, not
this locus); the change fixes five of them
(`test_an_eichler_transvection_lies_in_the_unipotent_radical_of_its_parabolic`,
`test_the_reflection_in_a_root_is_parabolic_but_not_unipotent`,
`test_lifting_minus_one_splits_the_lattice_along_the_chosen_lifts`,
`test_null_plane_parabolic_restriction_is_the_actual_gl_action`,
`test_special_orthogonal_null_line_has_its_proper_quotient_image[setwise]`). They were run
with `--no-test-lint` because `test_radical_quotient_integral.sage` and
`test_isotropic_routes_small_examples.sage` carry lint findings of their own (TL10, TL01,
TL02, TL03) that stop collection; those are pre-existing and untouched here.
