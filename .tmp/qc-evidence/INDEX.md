# Test evidence for the published commits, 2026-11-05/06

The Development diagnostics QC has never run on this repository (0 of 200 since 2026-11-01,
ai-review-ci#491: the shared workflow drops the Sage container when a caller passes a setup
recipe, and this repository passes `_ci-tensor-tools`). Until that is fixed, the pasted runs
below are the only test evidence for the pushes that cite them, so the raw logs are kept here
with their digests in `SHA256SUMS`. Each file is byte-for-byte the run's redirected output.

Every command is the same shape, with the repository's `addopts` blanked because this venv
lacks `pytest-timeout` and `pytest-reportlog`:

```
cd /repos/sage-extensions
PYTHONPATH=/root/ai-review-ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src \
  /sage/.venv/bin/python -m pytest <paths> -q -o addopts="" -p qc_sage_session --tb=no -rf -p no:cacheprovider
```
inside the adopted image via `.scratch/proot-run` (this project's checkout bound at
`/repos/sage-extensions`, the port at `/work` only where a test imports it).

| log | commit cited | result |
| --- | --- | --- |
| `inverse_test_prefix_final.log` | `cdc589b` (#17) | pre-fix worktree `354231d^`: **3 failed in 12.89 s** |
| `inverse_test_final.log` | `cdc589b` (#17) | at `354231d`: **3 passed** (test lint loaded, exit 0) |
| `test_run.log` | `15db925` (#272) | the regression: **4 passed in 45.24 s** (test lint loaded) |
| `forms-fail.log` | `6548aae` (#272 repair) | the three failures my #272 change introduced, with tracebacks |
| `forms-recheck.log` | `6548aae` (#272 repair) | **19 passed in 54.33 s** after the repair |
| `sweep-head.log` | `6548aae` (#272 repair) | `tests/forms tests/sets` at `3903e1c`: **86 failed, 200 passed in 438.90 s** |
| `sweep-base.log` | `6548aae` (#272 repair) | same command, clean worktree `cd52427`: **83 failed, 200 passed in 446.45 s** |
| `sweep-head2.log` | `6548aae` (#272 repair) | after the repair: **83 failed, 203 passed in 439.52 s** |
| `iso-carriers.log` | `e7efac9` (#17) | Iso-cardinality carriers at `6548aae`: **5 failed, 31 passed in 84.24 s** |
| `iso-carriers-base.log` | `e7efac9` (#17) | same command at `cd52427`: **5 failed, 31 passed in 84.67 s** |

The comparison rule these support is the repository's own: diff the FAILED **ids** against a
clean worktree at the same base commit, never compare absolute counts. `sweep-head.log` versus
`sweep-base.log` is what found the regression in `6548aae`; `sweep-head2.log` versus
`sweep-base.log` is 0 new and 0 fixed, with 3 extra passes that are exactly the new
`tests/sets/test_isomorphisms_between_finite_sets_are_counted.sage`.

Not included here, because they are measurements rather than pytest runs and are already
tracked: the #17 and #19 probe logs under `.tmp/` (`enriques_family_cpu.log`,
`enriques_t1t2.log`, `issue18_sign_witness.log`, `issue18_apex_stabilizer.log`,
`issue19_order_probe.log`, `issue19_final_probe.log`, `issue19_control.log`,
`issue19_det.log`), each cited with its own figures in `TRAPS.md`.

## Issue #273 (added 2026-11-06)

| log | commit cited | result |
| --- | --- | --- |
| `issue273-certificates.log` | `stabilizer_generators` | the certificates printed on `A_{T_Co}`, `c = [½ h̃_Co]`: orbit 496, predicted and measured stabilizer order `94 755 225 600`, six generators |
| `issue273-owner-test.log` | the owner test | **2 passed in 64.26 s** with the test-lint plugin loaded |
| `issue273-durations.log` | the owner test | per test: **39.86 s** and **8.45 s**, both inside the 60 s gate |

## Issue #16 consumer rerun on the new runtime (2026-11-06)

Runtime: rootfs checkout `281da26ffd`, image `sha256:220293469c53…`, GAP 4.16.1, sage-categories pin `de31eec` with all 26 packages under `.gap/pkg`.

| log | result |
| --- | --- |
| `consumer_newruntime.log` | `tests/algebra/test_modules_general_complete.sage`: the GAP-package collection error is gone and the colimit **constructs**; fails at `presented_modules.py:160` with **2 retained coequalizer presentations** (1 error in 35.52 s) |
| `general_presentations.log` | `tests/algebra/test_general_module_presentations.sage`: the **same** assertion, same line (1 error in 30.98 s) |

## Issue #17 on the adopted runtime (2026-11-06)

| log | result |
| --- | --- |
| `enriques_family_cpu_newruntime.log` | case_3: G_h built at **184.0 s wall / 114.0 s CPU**; `group_generators()` **exceeded its 600 CPU-second budget, fired at 714.0 s**, peak tree 4373 MiB of 6144 → `FAMILY_OVER_BUDGET` |
| `enriques_index_cpu_newruntime.log` | G_h built at **171.6 s wall / 105.0 s CPU**; `has_finite_coset_space()` **True in 0.0 s**; `coset_space()` then ran **43 minutes of wall without returning**, stopped by its owner — the wall is upstream of the family enumeration |

## Issue #275, the certificate at both layers (2026-11-06)

Runtime: rootfs checkout `281da26ffd`, image `sha256:220293469c53…`; the pytest run has `addopts` blanked because this venv carries `pytest` alone.

| log | result |
| --- | --- |
| `issue275-certificate-gset.log` | `tests/lattices/test_schreier_factors_rebuild_the_stabilizer_family.sage` + `tests/lattices/test_integral_stabilizers.sage`: **4 passed in 2.60 s** (was 3 passed in 2.94 s) — the composite law now asserted at the integral action **and** at the G-set owner (`Groups.S(3)`'s natural action, `|letters| = 2`, `|orbit| = 3`, family 6) |
| `issue275-coble-496.log` | earlier run: Coble element action, `|letters| = 4`, `|orbit| = 496`, family 1984, realized word by word **capped at 1800 s** |

### Coble factor route, measured (2026-11-06)

Probes are published beside their logs; the pytest run has `addopts` blanked (this venv carries `pytest` alone).

| log | result |
| --- | --- |
| `issue275-coble-factors.log` | `.tmp/qc-evidence/issue275-coble-factors-probe.py` on `A_{T_Co}`, `c` a `q = 1` class: factors **299.5 s**, 1984 composites **221.8 s**, **all fix `c`**, form preserved on 64, 8-of-1984 sampled family words **equal**, subgroup order **94 755 225 600** = `|O|/496` in 2.1 s; total **692.6 s**, exit 0, peak tree 2891 MiB — where the word-by-word realization of the same family did not finish in 1800 s |
| `issue275-natural-g-set-probe.py` | `Groups.S(3)`'s natural action: `|letters| = 2`, `|orbit| = 3`, family 6, `rebuilt == family` True, `composites == morphism images == group_generators` True — the specimen the suite now asserts |

## Issue #20's five acceptance specimens, measured (2026-11-06)

Probes are published beside their logs.

| log | result |
| --- | --- |
| `issue20-five-specimens.log` | `ZZ` **825 B**, number-field order `O(a)` **3946 B**, lattice **2134 B** — each equal with the same parent; `QQ`, an owned isometry and a genuine stabilizer-family element all raise `PicklingError: __reduce__ must return a string or tuple, not NoneType` |
| `issue20-gen.log` | `field.gen()` / `order.gen()` raise `AttributeError` on the owned algebra/ring parent, while `field.module_generator(...)` names the primitive element: the `.gen` gap does **not** block the order specimen |
| `issue20-chain.log` | `QQ`'s parent state: `_localization_submonoid` is a `SubobjectCategory.parent_class[_SubmonoidEngine].ObjectType`; that class reduces through `SubobjectCategory.parent_class` / `element_class`, which reduce through the parameterized category |
| `issue20-class.log` | those two classes carry `_reduction = (_parent_class_of, (Subobjects of Integer Ring,))` and `(_element_class_of, …)` — a real reduction whose datum is the category — and **both raise** when pickled |
| `issue20-category.log` | the blocker itself: `Subobjects of Integer Ring` does not pickle — instance, class, `parent_class`, `element_class`, `subcategory_class` all raise the same `PicklingError` |

## Issue #276, the gluing anti-isometry (2026-11-06)

| log | result |
| --- | --- |
| `issue276-certificate.log` | `tests/lattices/test_gluing_anti_isometry.sage` + `tests/lattices/test_centralizer_gluing.sage`: **11 passed in 100.21 s**, the two new tests at **0.77 s** and **25.47 s** per `--durations=0` |
| `issue276-glue-map-probe.py` | the probe that established `Lattices.glue_map` already returns the requested witness on both specimens (`(Z/2)^2` for the index-2 overlattice in `U`, 1024 = `\|A_{S_En}\|` for the Enriques gluing), so the new method delegates instead of duplicating |
| `issue276-enumeration-blocked.log` | `even_overlattice_inclusions()` on `S_En ⊥ T_En`: `_isotropic_subgroups` asks numpy for a `(1048576, 1048576)` int64 array — 8 TiB — and raises `_ArrayMemoryError` |

## Issue #279, scoped on the consumer specimen (2026-11-06, not implemented)

| log | result |
| --- | --- |
| `issue279-scope.log` | `T_En`: rank 12, `(2,10)`, `\|A_T\| = 1024`; `T_Co`: rank 11, `(2,9)`, `\|A_C\| = 2048`; `TCo_into_TEn` primitive with a **rank-1** complement spanned by a square `-2` primitive vector, so `⟨δ⟩ ⊕ T_Co` has index `sqrt(2048·2/1024) = 2`; `covering_discriminant_classes(-2)` = **one** class in 4.7 s; `vectors_of_square_and_divisibility(-2,1)` = a lazy infinite subset |

## Issue #279, the gluing route (2026-11-06)

| log | result |
| --- | --- |
| `issue279-certificate.log` | `tests/lattices/test_vectors_of_square_with_complement.sage`: **2 passed in 147.91 s** with the test-lint plugin loaded — the `A2` definite control against the enumerated six roots reduced by the two simple reflections, and the consumer `T_En`/`-2`/`T_Co` yielding one vector of square `-2` whose complement is `T_Co` and whose realizing isometry carries the `<-2>` generator to it |
| `issue279-gluing-route-probe.py` | the probe that fixed the route: 528 classes of `q = 1/2` in `A_{T_Co}`, 496 of them of order 2, `O(q_{T_Co})` with 4 generators giving one orbit, and the resulting overlattice of index 2 isometric to `T_En` |

## Issue #286, the port pin and the obstruction (2026-11-06)

Port `991b88b095a42a1e3679569ea42328c900c120f6` cloned into `.scratch/port-991b88b0` and bound at `/work`; `sage_indefinite_port` imported from `/work/src/sage_indefinite_port/__init__.py`.

| log | result |
| --- | --- |
| `issue286-vector-denominator-obstruction.log` | `T_Co.Aut().group_generators()` returns **444 in 338.7 s** (372/368.8 s and 442/375.2 s on reruns — the count is not a function of the input), then `isotropic_orbit_representatives(1)` raises in `isotropic_lifts.py:27 _vector_denominator`: `ValueError: a semilinear map into Lattice of rank 11 ... lies over a ring map into its base ring QQ, but Generic endomorphism of Integer Ring ends at Integer Ring` |
| `issue286-port-and-orbit-probe.py` | the probe, and | 
| `issue286-launcher.sh` | the launcher that binds the pinned clone at `/work` with `/sage/.venv/bin` on `PATH` |

| `issue286-after-vector-denominator-fix.log` | with the `_vector_denominator` patch: the `ValueError` is gone and the chain proceeds, then `STOPPED_AT_MEMORY_LIMIT` at **6209 / 6144 MiB**, 452 s (319 s for 438 generators) |
| `issue286-isotropic-suite.log` | the isotropic-orbit suites at this tree: `10 failed, 19 passed in 239.49 s`, **no traceback entering `isotropic_lifts.py`** — the failures are `component_character`'s `Cardinalities...one`, a `tuple` where a cardinality was expected, and the **image's** un-pinned port at `eichler.py:999` |

## Issue #286 items 1-3 (2026-11-06)

| log | result |
| --- | --- |
| `issue286-guard-at-sandbox-headroom.log` | guard at 12288 MiB: killed at **12305 MiB, 528 s**, python **9730 MiB**, julia 3136 MiB, generators 360 in 352.8 s — the search grows ~55 MiB/s and does not terminate at any cap tried |
| `issue286-tracemalloc-top-sites.log` | top ten allocation sites by size difference over 90 s are **all 0.0 MiB** (4–39 blocks): the retention is C-level, below tracemalloc's hook |
| `issue286-old-line-small-lattices.log` | with the pre-fix line restored, `isotropic_orbit_representatives(1)` returns in ≤1.4 s on `U(2)+A1`, `U+<2>`, `U`, `U+U` — none raises |
| `issue286-vector-denominator-call-counter.log` | `_vector_denominator` call counter: **0 calls** on ranks 3, 5, 6 and 10; the only call that reaches the line is `T_Co`'s, which cannot finish |
