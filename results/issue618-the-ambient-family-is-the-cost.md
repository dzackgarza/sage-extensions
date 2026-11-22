# The line rows of the Scattone lattices cost the ambient generating family, not the orbit

Diagnosis of #618, measured 2026-11-21 against `main` `e366ec5`.  The row
`6JRY:Otilde+:lines` reaches 6312 MiB in 90 s because the acceptance row asks for
the **selected generating family of the ambient orthogonal group** `O(Lambda_4)`,
whose computation runs the indefinite port's Lorentzian cell traversal with a
recursive backtracking search.  The orbit walk, the class enumeration and the
group construction are not the cost: each is measured below at under a second.

## The stages, with time and peak resident memory

SageMath 11.0.beta5, Python 3.14, the port as the image provides it at
`/repos/sage-indefinite-port`, 4 CPUs, one process.  Peak resident set from
`resource.getrusage(RUSAGE_SELF).ru_maxrss` after each stage:

| stage | time | peak RSS |
| --- | ---: | ---: |
| `Lambda_4 = U + U + E8(-1) + E8(-1) + <-4>` from its summands (rank 21, det -4) | 0.07 s | 297 MiB |
| `L.Aut()` | 0.01 s | 298 MiB |
| `L.O_plus()` | 0.10 s | 301 MiB |
| `L.stable_orthogonal_group()` | 0.11 s | 306 MiB |
| `stable.intersection(O_plus)` | 0.01 s | 306 MiB |
| `G.finite_character_quotient()` | 0.00 s | 284 MiB |
| `L.Aut().isotropic_orbit_representatives(1)` (the ambient row) | 25.20 s | 422 MiB |
| `G.isotropic_orbit_representatives(1)` | not returned at 80 s | 1236 MiB, rising |

So the ambient classification of the same lattice costs 25 s and 422 MiB, and the
subgroup row costs unbounded memory.  The difference is one datum: the ambient
*generating family*.

## The stack, at the moment of the growth

`faulthandler` at 60 s of the subgroup row, from
`G.isotropic_orbit_representatives(1)`, deepest frame last:

```
predicate_subgroups.py:604       isotropic_orbit_representatives
orthogonal_quotients.py:4878     _subgroup_isotropic_orbit_representatives
orthogonal_quotients.py:4809     _yield_subgroup_isotropic_orbit_representatives
orthogonal_quotients.py:1766     isotropic_line_stabilizer_image
orthogonal_quotients.py:1445     _sign_descent_rank
orthogonal_quotients.py:1388     _im_rho_engine_and_section
orthogonal_quotients.py:655      _ambient_generators          -> tuple(ambient.group_generators())
groups.py:6352                   has_selected_finite_group_generating_set
groups.py:6363                   selected_group_resolution
lattices.py:2834                 _core_automorphism_generators
lattice_morphisms.py:4793        _computed_group_generators
marked_lattices.py:176           automorphism_group_generators        (port)
recursive.py:1105/1123/1891      orthogonal_group_generators, _generation_step, pointed_automorphism_generators
recursive.py:1206                _lattice_action
recursive.py:1103                orthogonal_group_generators  (the Lorentzian branch)
lorentzian_cells.py:459          lorentzian_orthogonal_group_generators
lorentzian_cells.py:2845         full_orthogonal_group_generators
lorentzian_cells.py:2837         component_preserving_generators
lorentzian_cells.py:2829         quotient_cells        (cached)
lorentzian_cells.py:2825         _traversal
lorentzian_cells.py:2735         _expand_traversal_once
lorentzian_cells.py:1719         _facet_mask_orbits_via_walk
lorentzian_cells.py:1297/1316    cell_stabilizer_permutations, point_permutations_from_rows
lorentzian_cells.py:1287         cell_stabilizer
lorentzian_cells.py:2667         cell_transporter
lorentzian_cells.py:2485/2488    backtrack     (recursive, ~20 frames deep)
```

## The mechanism

`isotropic_line_stabilizer_image` must decide the double cosets
`chi(Gamma) \\ chi(O(L)) / chi(Stab(x))` of the joint character `chi = (rho, sn)`,
so `_sign_descent_rank` asks which sign patterns are realized on `ker rho`, and it
evaluates `chi` on the **ambient generating family** to answer.  That family is not
a datum the row has: `_ambient_generators` calls `ambient.group_generators()`, which
runs the port's `automorphism_group_generators`, and on `Lambda_4` that is the
Lorentzian cell traversal above.

Two properties of that traversal are what the slow-run rule names:

* **A constructor computes.**  `has_selected_finite_group_generating_set()` is a
  *predicate* and it realizes the resolution: asking whether a family is selected
  computes the family.  The row pays for a construction it does not need to
  complete -- it needs `chi` on a generating family, and `chi` takes values in the
  finite group `O(A_L) x C2`, of order 4 here.
* **The cost rises with the work already done.**  `_expand_traversal_once` expands
  the traversal one cell at a time, and for each facet mask it runs
  `cell_stabilizer_permutations` -> `cell_transporter` -> `backtrack`, whose frames
  hold a GAP permutation-group stabilizer chain (`permgroup.py:1979 stabilizer`
  inside `GAP_Enter`) per assigned point.  The stored stabilizers accumulate as the
  walk proceeds, so the allocation is a function of the cells already processed,
  not of the input's size.

It is also more than ten times what the mathematics owes: the count owed is one
orbit, the ambient row that already classifies this lattice's isotropic lines takes
25 s and 422 MiB, and the family the row asks for has at most `|O(A_L) x C2| = 4`
images under `chi`.

## The price is visible in the finite data

Measured on the same lattice, each of these returns without the family:

| call | answer | time |
| --- | --- | ---: |
| `L.discriminant_group()` | invariant factor 4 | 0.75 s |
| `L.discriminant_group().orthogonal_group().cardinality()` | 2 | 2.67 s |
| `L.eichler_criterion_applies()` | `True` | 0.90 s |
| `L.splits_two_hyperbolic_planes()` | `True` | 0.00 s |
| `L.odd_spinor_norm_isometry()` | an isometry of `L` | 0.55 s |
| `L.discriminant_representation()` on that isometry | a form automorphism | 0.11 s |
| `L.discriminant_representation_is_surjective()` | not returned in 60 s | -- |

The last line is the same defect at a second entry point: the surjectivity decision
also reaches for the family, while `|O(A_L)| = 2` and an exhibited isometry with a
nontrivial image certify the same statement without it.

## What the row needs, and the two routes to it

The row needs `chi(O(L))` and `chi(Stab(x))` as subgroups of the finite group
`O(A_L) x C2`, exactly -- a smaller image over-splits the ambient orbit, which is
why the code refuses to guess.

**Route A, the Eichler criterion.**  `Lambda_4` contains `U + U`
(`eichler_criterion_applies()` is `True`), so Gritsenko--Hulek--Sankaran,
arXiv:0810.1614v1, Proposition 3.3(i) (after Eichler, Satz 10.4) applies: the orbit
of a primitive vector under the group generated by the Eichler transvections is
determined by its square and by its class `v/div(v)` in the discriminant group.  If
that group is the kernel of the discriminant character on this lattice, then
`Otilde(Lambda_4)`'s line orbits are the divided classes, which the library already
enumerates without any generating family
(`ParentMethods.primitive_isotropic_vector_of_divided_class`,
`_line_orbit_from_divided_classes`), and the row is decided by the finite datum of
`A_L`.  What is owed before this route is used is the identification: that the
Eichler group is `ker rho`, and that the spinor norm is trivial on it (else
`Otilde^+` is the index-two subgroup of `ker rho` and the split must still be
decided).  Neither is proved here.

**Route B, a certified finite image.**  Compute `chi(O(L))` inside the finite group:
above by `O(A_L) x C2` (order 4, 2.67 s), below by `chi` of exhibited isometries
(`odd_spinor_norm_isometry` is one, with its image computed in 0.11 s), and close the
two by the same upper-bound/lower-bound loop `exact_isotropic_stabilizer_generators`
already uses for the stabilizer's image.  If the exhibited images generate the upper
bound the answer is certified with no lattice generating family; if they do not, the
call must say so and keep its exact route rather than guess.

Neither route is landed in this commit.  What is landed is the measurement above:
the stage, the file and function that own it, the growth law, and the two entry
points (`isotropic_line_stabilizer_image` and
`discriminant_representation_is_surjective`) that reach for the same family.
