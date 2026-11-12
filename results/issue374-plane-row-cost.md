# #374: where the T_En plane-orbit row and the plane parabola spend their time

Partial: one real defect is repaired and measured, and the two files the issue
names are **still above the 20 s call gate**.  What follows is the profile with
the step, its file and line, the repair, and the numbers before and after.  At
`7761145d` (main): the plane-orbit call is 75.7 s alone, and
`test_the_parabolic_completeness_of_an_enriques_plane.sage` is 131.46 s for its
four tests (93.98 s on the slowest, `4.2 s` on the fastest).

## 1. The step that takes the time

One process, pinned runtime, worktree `.scratch/wt374` at `7761145d`, each
number a single cold call.

### The plane-orbit call — `Lattices.isotropic_orbit_representatives(2)`

`lattice_morphisms.py:4905` -> `isotropic_orbits.py:1574`
(`_isotropic_orbit_representatives`) -> `isotropic_orbits.py:1397`
(`_isotropic_plane_orbit_representatives`):

| step | code | time |
| --- | --- | --- |
| the two line classes | `isotropic_orbits.py:1412` -> port `marked_lattices.primitive_marking_classes` -> `recursive.py:1754 primitive_vector_classes` | **46.03 s** |
| planes through line 0 | `isotropic_orbits.py:1367 _planes_through_line` -> port `isotropic_induction.py:68 isotropic_vector_classes` | 3.20 s |
| planes through line 1 | same | 6.20 s |
| identification, candidate 1 vs candidate 0 | `isotropic_orbits.py:1419` -> `_isotropic_equivalence_witness` `isotropic_orbits.py:1633` -> port `isotropic_induction.py:288 plane_isometry` -> `recursive.py:1644 _isotropic_correction` -> `rational_integral_stabilizers.py:770 transporter` (`g_sets.py:213 _orbit_words`) | **19.62 s** |
| identification, candidate 2 | same | 0.38 s |

So 46.03 of 75.7 s is the line-class enumeration, 9.40 s the planes through the
two lines, and 20.00 s the identification of three candidates down to the two
classes the card records.  The line step's covering set is 18 vectors
(`eichler.py:980 primitive_covering_vectors`, 7 s of the 46) and the rest is 16
`recursive.py:1572 pointed_isometry` decisions, of which the two that need an
integral correction (`recursive.py:1644`) carry about 25 s between them.

### The completeness module

`test_the_plane_that_does_not_split_is_complete_by_its_three_factors` calls
`isotropic_parabolics.py`'s three factors at `P_2`; measured one at a time:

| call | time |
| --- | --- |
| `parabolic_stabilizer_generators()` — 139 generators, of which | 32.34 s |
|  — `half_vector_transvection_generators` (19 generators) | **31.94 s** |
|  — `quotient_reflection_generators` (64) | 30.98 s |
|  — `unipotent_radical_generators` (31) | 5.76 s |
|  — `levi_lift_generators` (18) | 4.09 s |
| `unipotent_radical_index()` (with `unipotent_parameter_lattice`) | 17.49 s |
| `levi_plane_action_index(trivial_on_quotient=True)` | 92.33 s |
| `levi_quotient_image_index(trivial_on_plane=True)` | 8.45 s |

and at `P_1`, `parabolic_stabilizer_generators()` is 42.52 s for 181 generators,
which is what `test_the_split_plane_action_has_index_three` (33.28 s) waits for.

## 2. The defect repaired here

`lattices.py:8479 eichler_transvection_half_vector` asserted its hypotheses by
asking whether the parameter is a member of
`half_vector_transvection_parameters(isotropic)` — which **recomputes that whole
family**, scanning every generator of the metric dual and building the Gram
matrix, once per parameter.  `half_vector_transvection_generators`
(`isotropic_parabolics.py`) iterates exactly over that family and calls this
method once per element, so the scan was paid `1 + 2 x 19` times.

The conditions are the ones the method's own docstring states, and they are all
read on the `w` coordinates the method already holds: `b(e, w) = 0`,
`2w` in `L`, `q(w)` in `ZZ`, and `e` of divisibility two.  They are the
integrality conditions of the transvection formula

    t(e, w)(x) = x - b(w, x) e + b(e, x) w - (1/2) q(w) b(e, x) e,

whose sources the method already cites: Dawes, *Orbits in lattices*, section 2
equation (7); Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1 equations
(4)--(5); and Scattone, Mem. AMS 374 (1987), section 3.7, Proposition 3.7.3,
whose criterion generates the radical of the parabolic at an isotropic
sublattice by these transvections.  The three coefficients of the formula are
`b(w, x)`, `q(w)/2` and `b(e, x)`: on an integral lattice the first is integral
because `2w` in `L`, and the remaining two are exactly the conditions now
checked per parameter.

Every returned generator is still checked entry by entry to be an integral
isometry before it is constructed, and no generator is dropped or added: the
same 19 are returned, in the same order (the family is built from the same
`half_vector_transvection_parameters` list, whose own filter is unchanged).

Measured, one cold call at `P_2`:

```
half_vector_transvection_generators   31.94 s  ->  9.16 s   (19 generators, both)
test_the_parabolic_completeness_of_an_enriques_plane.sage
                                     131.46 s  -> 100.75 s
  test_the_plane_that_does_not_split_is_complete_by_its_three_factors
                                      93.98 s  -> 78.49 s
```

## 3. Docstring pages

Every docstring that cited Dutour Sikirić--Hulek's Theorem 4.9 as "printed p. 22"
now cites `arXiv:2302.01679v2, printed pp. 33--34`, which is where the theorem
and its proof stand (the sentence "the second equation determines `P_1` ..." and
the denominator `d_3 = |det A|` are on printed p. 34): `predicate_subgroups.py`,
`isotropic_parabolics.py` (11 places), `lattices.py`, `isotropic_orbits.py` (2),
and the module docstrings of `test_the_unipotent_radical_of_the_plane_is_measured`,
`test_the_isotropic_reduction_image`,
`test_the_parameter_lattice_of_the_unipotent_radical`,
`test_the_stabilizer_of_a_non_split_enriques_plane` (2),
`test_the_parabolic_completeness_of_an_enriques_plane` (2),
`test_the_plane_block_lift_coset`.  Pages that belong to other statements are
left alone: Dutour Sikirić--Hulek's Lemma 3.6 in §3.6 (`isotropic_orbits.py`,
printed p. 22 is correct there), Milne's Theorem 1.47 and Vinberg's
Proposition 1.

## 4. What is not done, and where the rest of the time is

* **The plane-orbit call is unchanged at 75.7 s.**  Its 46.03 s line step and
  its 19.62 s identification are inside the pinned indefinite port
  (`primitive_vector_classes`, `pointed_isometry`, `_isotropic_correction`); the
  port is readable and not pushable, so the repair has to replace the call, not
  patch it.  The two owned levers measured here are
  `rational_integral_stabilizers.py:770 transporter`, whose orbit-word search
  (`g_sets.py:213`) costs 3.5 s of the identification and is the same search the
  port's two expensive corrections use, and the fact that our library asks the
  port for the line classes through the marking category rather than by any
  cheaper certified route — `INDUCTION.isotropic_vector_classes(L)` directly is
  56.37 s, no better.
* **The completeness module is still at 100.75 s.**  After this repair the
  largest single items are `quotient_reflection_generators` (32.08 s, of which
  37 s of the profiled time is 8 engine reads in the shell enumeration of
  `P^perp/P`), `unipotent_parameter_lattice`'s class enumeration (14 s of the
  17.49 s `unipotent_radical_index`), `levi_quotient_image_index`
  (9.27 s), `half_vector_transvection_generators` (9.16 s, the two family scans
  that remain), `unipotent_radical_generators` (7.52 s) and
  `levi_lift_generators` (4.70 s).
* The three other test modules that are over the gate at `7761145d`
  (`test_the_stabilizer_of_a_non_split_enriques_plane` 117.48 s,
  `test_the_unipotent_radical_of_the_plane_is_measured` 65.50 s,
  `test_the_plane_block_lift_coset` 71.59 s) are the same generator families and
  are not addressed here.
