# The definite-lattice slice on main: 11 red tests in eight causes

The slice is the five files the issue names, and it was run once on `main` in the adopted image with
the repository's own invocation, one pytest process per file, before anything was bisected or
repaired. Two of the eight causes are repaired on `main`; the other six are filed with their
paste-ready issue bodies under `.tmp/qc-evidence/triage/410-cause-*.md`.

## The file set, and the count

At `c8a3cedb` (the current `main`) the five files collect **37** tests:

| file | tests |
| --- | --- |
| `tests/lattices/test_definite.sage` | 25 |
| `tests/lattices/test_definite_genus_mass_archive.sage` | 2 |
| `tests/lattices/test_definite_isometry_witnesses.sage` | 5 |
| `tests/lattices/test_definite_metric_invariants_archive.sage` | 2 |
| `tests/lattices/test_full_definite_root_lattice_groups.sage` | 3 |

The issue body's "18 of 76" cannot be reproduced from this file set on any `main` of this workstream:
the three further `definite`-named files (`test_rational_definite_minimum`,
`test_rational_definite_orthogonal_groups`,
`test_reflective_root_system_components_of_definite_lattices`) add 17, and the eleven
`indefinite`-named files in `tests/lattices/` add 23, so 54 and 77 are the neighbouring readings and
neither is 76. The file list in the body is unambiguous, so the slice is those five files and the
count is 37.

## The run

```
cd /repos/sage-extensions
/sage/.venv/bin/python -m pytest -p qc_sage_session -o addopts= \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates --no-test-lint <one file>
```

`-o addopts=` is forced by the runtime: this venv has no `pytest-timeout` and no
`pytest-reportlog`, so `pyproject.toml`'s `addopts` is rejected with
`unrecognized arguments: --timeout=60 --timeout-method=signal --report-log=…`. `--no-time-gates
--no-test-lint` are the flags the issue's own observation used. Logs and their digests are in
`.tmp/qc-evidence/` with the `410-` prefix, indexed there under `## #410`.

At `9b29712` the five files gave **11 failed, 26 passed**: 9 failed of 25 in `test_definite.sage`,
2 failed of 2 in `test_definite_metric_invariants_archive.sage`, and 2 + 5 + 3 passed in the other
three files. At `c8a3cedb` the same 11 ids fail, and at `5f5fc25` — the `main` this triage is
rebased onto, five commits further on from the #408 slice — they still fail, so nothing that landed
between those commits changed the slice. The repaired tree is rebased onto `5f5fc25` and its gate
re-run there.

## The 11 failures, by cause

| cause | tests | error | introduced by |
| --- | --- | --- | --- |
| A | `test_definite`: `test_square_lattice_minimum_theta_and_packing_radius`, `test_exact_cvp_babai_minima_and_voronoi_geometry_on_square_lattice`; `metric_invariants_archive`: both tests | `RecursionError` in `Modules.ElementMethods.__truediv__` | `e4bd95d` Zack Garza 2026-11-06 |
| B | `test_definite`: `test_norm_one_vectors_of_x2_minus_2y2_form_one_orbit` | `IndexError: index out of range` in `_named_stabilizer` | `bbb6608` D. Zack Garza 2026-11-14 |
| C | `test_definite`: `test_definite_target_embedding_mor_enumerates_all_a1_into_a2_roots` | cardinality of `Emb(A1, A2)` undecided | never implemented; assertion landed `14b9cc1` Zack Garza 2026-10-26 |
| D | `test_definite`: `test_a2_discriminant_representation_is_onto_order_two_and_so_a2_has_order_6` | cardinality of a predicate `Subset` of `O(A2)` undecided | `d26db5d7` Zack Garza 2026-10-27 (no observable flip, see below) |
| E | `test_definite`: `test_discriminant_group_of_a1_plus_a2_is_cyclic_of_order_6` | `AttributeError: … has no attribute 'is_cyclic'` | no such operation ever; assertion landed `14b9cc1` |
| F | `test_definite`: `test_a_hyperbolic_isometry_of_x2_minus_2y2_has_infinite_order` | cyclic subgroup cardinality: "no order algorithm or finite ambient enumeration is supplied" | refusal from the initial import `c731175` Zack Garza 2026-10-26 |
| G | `test_definite`: `test_definite_complement_extensions_exhaust_the_u_vector_cosets` | `'tuple' object has no attribute 'cardinality'` | `_definite_complement_extensions` tuple from `c731175` |
| H | `test_definite`: `test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so` | `ArithmeticError`: the index-2 character image is not certified | `6a93efe` D. Zack Garza 2026-11-12 |

Each row is one defect of one call, not one test: A is the module element's division, B the GAP
stabilizer's empty generator family, C the `Emb` cardinality decision that `Isom` has and `Emb`
lacks, D the predicate subset's missing decision, E the absent `is_cyclic` operation, F the absent
element-order decision for a lattice isometry, G the helper returning a Python tuple, H the
certification refusal in the special orthogonal isotropic route.

### Masking, which the triage had to unpick

Three of the eight are visible only after another is repaired, so "the failing test" and "the
cause" are not in bijection at a single commit:

* `test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so` was red on H's refusal at
  `6a93efe`, then red on B's `IndexError` after `bbb6608`; the `IndexError` is what `main` shows.
  Repairing B exposes H again.
* The two metric-archive ids were already red at `e4bd95d^` on an older
  `'>' not supported between instances of 'OwnedJoinCategory.element_class'`, so A's recursion
  masks them; the two `test_definite.sage` ids of A are the clean flip.
* Cause D's guard (`Sets().condition_set` requiring the universe to be in `EnumeratedSets()`) has no
  observable pass-to-fail flip: at `d26db5d7^` and at `d26db5d7` the id fails earlier, on
  `TypeError: CategoricalIsomorphism.__init__() missing 1 required positional argument:
  'inverse_computation'`. The commit is named from the code history and the refusal it produces is
  verified at `c8a3cedb`.

## Repaired on main

Two commits, each with the failing ids as its regression:

* **A** — `src/sage_extensions/categories/modules/pure/modules.py`: an element whose parent *is* its
  base ring divides by the ring's own `_div_`; the `scalar_multiple` route is kept for a genuine
  scalar action. Four ids green.
* **B** — `src/sage_extensions/categories/group/g_sets.py`: `_named_stabilizer` returns the trivial
  subgroup when the acting group has an empty generating family. One id green.

The gate on the repaired tree at `5f5fc25` — the four cause-A ids, the cause-B id and the #150
division contract `tests/lattices/test_rational_scalars_on_a_base_changed_lattice.sage` — is
**6 passed in 3.88 s**. The full five-file slice on the repaired tree leaves the six filed causes
red, and one extra: `test_nikulin_even_unimodular_embedding_existence_controls_embedding_mor`,
which passed at 319.62 s in the baseline run and in the repaired run died with
`sage_julia_bridge.errors.JuliaWorkerError: Julia bridge process exited unexpectedly` while two
other Julia processes held 5 GiB each of this 15 GiB VM. That is the Julia bridge under memory
pressure, not a defect of the tree, and it is not assigned a cause.

## Filed, not repaired

Six causes, each with its own paste-ready body under `.tmp/qc-evidence/triage/`:
`410-cause-c-embedding-mor-cardinality.md`, `410-cause-d-predicate-subset-cardinality.md`,
`410-cause-e-module-cyclicity.md`, `410-cause-f-infinite-order-isometry.md`,
`410-cause-g-definite-complement-tuple.md`, `410-cause-h-index-two-character-image.md`. Two of them
(C, E) need an owner that is broader than this slice — the `Emb` cardinality decision and the
module cyclicity operation — and D's repair is in the `Sets` owner, so their bodies state that
scope. This connection cannot create issues, so the bodies are committed for the orchestrator to
file rather than filed.
