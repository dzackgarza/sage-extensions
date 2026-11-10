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

## Issue #286, the small indefinite lattices L_d = U + U + <-2d> (2026-11-06)

| log | result |
| --- | --- |
| `issue286-ld-classes-and-timings.log` | the derivation checked on the lattice: isotropic classes of `A_{L_d}` by order give totals **1, 1, 2, 3, 6** (= `sum phi(e)`) and orders **1, 1, 2, 2, 4** (= `#{e : e^2|d}`) for d = 1, 2, 4, 9, 36; `O(L).group_generators()` **28/60.5 s, 26/6.3 s, 27/7.0 s, 33/11.1 s, 37/16.8 s** |
| `issue286-ld-orbits-pinned-port.log` | under the pinned port the splitting runs; `O(L)` counts **1, 1, 2, 2, 4** match the derivation, Õ gives **1, 1, 2, 2** — at **d = 9 the Õ count is 2 where the derivation gives 3** |
| `issue286-ld-test-draft.sage` | the drafted test (class-order derivation passes; red on the d = 9 Õ assertion), not committed |

## Issue #296, the isotropic subobject orbit and setwise stabilizer (2026-11-07)

Delivered at the commit that carries this entry: `A.isotropic_subobject` unchanged from
`14a506a`, and `O(q).subobject_orbit_action(J)` / `orbit(J)` / `orbit_points(J)` /
`stabilizer(J)` computed from one owned walk. Commands are the same shape as above
(`-q -o addopts= -p qc_sage_session`, run inside the adopted image with this checkout
bound at `/repos/sage-extensions`), plus `-s` where a log carries the test's own
printed phase timings.

| log | result |
| --- | --- |
| `issue296-sigsegv-record.log` | **the crash the brief names**, captured before the repair: SIGSEGV in `abelian_group_gap.exponents:154` <- `abelian_aut.matrix:203` <- `fqf_orthogonal._act_:484` <- `_normalized_map` <- `_transported_map` <- `_from_engine` <- `TorsionFormAutomorphism.__mul__` <- the plane-orbit walk, at 560 s, tree RSS 3076 MiB, no pytest line (inner cap 600 s) |
| `issue296-stabilizer-order-defect.log` | the second failing regression, captured before its repair: the walk and the orbit were right and `stabilizer(J)` returned a generator that does **not** fix `J` (`assert [3] == [1]`), because the engine product is the reverse of owned composition |
| `issue296-full-run.log` | `tests/lattices/test_isotropic_subobjects_of_finite_quadratic_modules.sage`: **2 passed in 220.32 s** (T_Co 164.67 s, small specimen 52.90 s), `|orbit(J)| = 23715`, `|Stab(J)| = 1981808640` from 8 generators, `23715 * 1981808640 = 46 998 591 897 600 = |O(q)|`; the earlier identical run was **2 passed in 283.95 s** (walk 55.8 s, stabilizer 149.0 s) |
| `issue296-test-lint.log` | the repository test lint on the delivered test module and on the #275 Schreier-family test: `4 tests collected`, exit 0, no findings |
| `issue296-schreier-factors-regression.log` | `tests/lattices/test_schreier_factors_rebuild_the_stabilizer_family.sage` + `tests/lattices/test_integral_stabilizers.sage` with the lint plugin: **4 passed in 7.61 s** (the `orbit_schreier_factors` refactor does not move #275) |
| `issue296-costs.log` | warm micro-costs on `A_{T_Co}`: `hash(element)` 0.0001 ms, `element == element` 0.12 ms, one owned application 0.50 ms, engine product 0.114 ms, engine membership 0.07 ms |
| `issue296-crossing-costs.log` | the enumeration and crossing costs: `tuple(elements())` 0.011 s warm, `ranking(element)` 23 us, `ranking.inverse(rank)` 53 us, **`_from_engine` 51.7 ms** |
| `issue296-crashpath.log` | the crash path isolated: 20 engine products in 0.002 s, an owned product 0.06-0.07 s, 200 image applications in 1.1 s, **no crash at that scale** — the recorded SIGSEGV needs the sustained walk, which is why the record above is the failing regression |
| `issue296-costs-probe.py`, `issue296-crossing-probe.py`, `issue296-crashpath-probe.py` | the three probes, bound at `/probe.py` |

### The element orbit was shadowed by the submodule orbit (2026-11-07, fixed in the #296 commit)

`14a506a` gave `O(q)` an `orbit(J)` on *submodules* while the class already had an
`orbit(element)` on *elements of the form*, defined earlier in the body; the later
definition wins, so `O(q).orbit(element)` and `form.orbit(element)` (through
`_finite_form_orbit`) called the submodule operation. Two call sites were live:
`form_modules._finite_form_orbit` and `tests/forms/test_torsion_forms.sage`.

| run | file | result |
| --- | --- | --- |
| `7540ceb` (clean export) | `tests/forms/test_torsion_forms.sage` | **3 failed, 7 passed in 92.43 s**, `test_u2_bilinear_orthogonal_group_element_orbit` among the failures |
| the #296 commit | same file, same command | **2 failed, 8 passed**, that test green; its two other failures (`Lattices(ZZ)([[2,0],[0,1]])` is odd and has no `discriminant_quadratic_form`, and an `orbits_on_isotropic_subobjects` cache `KeyError`) are unchanged |

The repair is a rename of the older operation to `orbit_of_element`, matching
`stabilizer_of_element` beside it, and the two call sites follow it; `orbit` is the
submodule orbit the issue names (`#296`). Evidence:
`issue296-element-orbit-head.log` and `issue296-element-orbit-base.log`.

## #286, batch 1 (2026-11-09): the rank-2 branch and card `029J`

The runs use the port-bound harness `.scratch/sage-python-port` (the port checkout at
`991b88b0` bound at `/repos/sage-indefinite-port`) with the repository `addopts` intact and
only the ceilings lifted (`--no-time-gates`, `--timeout=…`), because every call here is over
the 20 s per-call gate on this host.  The probes run under `peakrss` (6144 MiB) via
`.scratch/issue275e_launch.sh`.

| log | result |
| --- | --- |
| `p286-stage0.log` | `T_En` before the branch: 2 line orbits in 43.9 s; the first line's reduction `K_v` rank 10, signature (1,9), `det -1024`, `1` `O(K)`-class of isotropic vectors in 2.1 s |
| `p286-stage1.log` | the rank-2 branch by hand on `T_En`: 3 candidates over the two line orbits, one identified with an earlier one by an explicit isometry (16.6 s), **2 plane orbits in 62 s**; the plane stabilizer generators were still running when the probe was stopped at 7 min |
| `p286-stage3.log` | the split check: `U + U(2)` both lines, `U + E8`, and `T_En` both lines (`v = -e_e, f = e_f`, dets `-1`/`-1024`; `v = e_fp, f = e_ep`, dets `-4`/`-256`) |
| `p286-stage4.log` | the public calls: `029J` `O` **2 planes in 62.8 s** and 2 lines; `6JRX` 1 line orbit in 20.5 s, then `INDUCTION.isotropic_vector_classes` on the rank-19 reduction did not return — the probe was killed by its 2400 s inner cap (`launcher exit: 124`, peak tree RSS 1086 MiB) |
| `p286-enriques-runB.log` | `tests/lattices/test_unpolarized_enriques_strata.sage`: **2 passed in 202.55 s**, exit 0; the gate report lists the two calls at 116.95 s and 84.37 s (host at load 10.6) |
| `p286-milestones-runB.log` | `tests/lattices/test_orbit_milestones.sage`: **2 passed in 246.54 s**, exit 0, with the Enriques plane count corrected from 9 to the card's 2 |
| `p286-so-run.log` | `tests/lattices/test_special_orthogonal_split_building.sage`: **1 passed in 33.31 s**, exit 0 — `SO(2U)` still splits the single `O`-plane class into its two |
| `p286-stable-planes-run.log` | `tests/lattices/test_stable_isotropic_plane_orbits.sage`: **3 passed in 50.57 s**, exit 0 — the `Otilde`/`Otilde+` plane fibres of `L_1` are unchanged |
| `p286-touched-modules-run.log` | the two touched modules together on a quiet host under `--no-time-gates`: **4 passed in 90.36 s**, exit 0; call phases 66.45 s (`test_orbit_milestones`), 13.95 s (`test_unpolarized_enriques_strata` planes, lines warm), 9.33 s (the E10 milestone) |
| `p286-enriques-gated-run.log` | the same card-reading module with the repository `addopts` intact (`time gates on … each test call ceiling 20 s`, `--timeout=60`): **2 passed in 65.22 s**, both calls listed over the ceiling (41.80 s and 23.02 s), so the session is the cost finding for #306 and not a value mismatch |
| `p286-rebased-run.log` | the same four modules re-run after the rebase onto `b2a1a49`, so the evidence names the pushed base: **8 passed in 114.43 s**, exit 0; call phases 68.58 s (`test_orbit_milestones`), 12.62 s (`test_unpolarized_enriques_strata` planes), 9.82 s (`SO(2U)` building), 8.68 s + 5.15 s + 0.04 s (the three `L_1` plane tests), 8.43 s (the E10 milestone) |
| `p286-pushed-base-run.log` | the same four modules at the pushed base `34d198e`: **8 passed in 111.69 s**, exit 0; call phases 62.97 s (`test_orbit_milestones`), 14.34 s (`test_unpolarized_enriques_strata` planes), 10.68 s (`SO(2U)` building), 8.56 s + 5.34 s + 0.04 s (the three `L_1` plane tests), 8.59 s (the E10 milestone) |
| `p286-head-run.log` | the four modules at the pushed commit `ead5f07`: **8 passed in 106.21 s**, exit 0; call phases 62.50 s (`test_orbit_milestones`), 11.90 s (`test_unpolarized_enriques_strata` planes), 9.11 s (`SO(2U)` building), 8.23 s + 5.04 s + 0.04 s (the three `L_1` plane tests), 8.34 s (the E10 milestone) |

## #286, batch 2 (2026-11-09): the definite route and `Gamma_{En,2}` -- both stopped

| log | result |
| --- | --- |
| `p286b-stageA.log` | genus of `E8(-1)^2 + <-2>`: mass `2499347/9440684171518279680000` in 1.1 s, then `genus_class_number()` exceeded 6 GiB in 38 s and was killed at 6324 MiB |
| `p286b-stageB.log` | 17 candidate shapes on `Lambda_2`; the dedupe used `is_isometric`, which reported every one isometric to the first -- the invalid test, kept because it is the measurement behind the `TRAPS.md` row |
| `p286b-stageD.log` | the same shapes with PARI's `is_globally_equivalent_to`: `qfisom` overflowed at 1 GiB, then at 3 GiB after `pari.allocatemem` |
| `p286b-stageE.log` | `neighbor_iteration(algorithm="orbits")` dies inside `p_divisible_vectors -> automorphism_group -> qfauto` (PARI stack overflow); `algorithm="fast"` is not a spelling this image accepts |
| `p286b-stageF.log` | `Gamma_{En,2} = O.stabilizer(h)`, `h = e_ep + e_fp`: builds in 0.0 s, `contains_character_kernel()` and `character_data_is_complete()` both `False`, `finite_character_quotient()` raises `ValueError`, and `isotropic_orbit_representatives(1)` raises the `AssertionError` naming the missing generating set |
| `p286b-stageG.log`, `p286b-stageG2.log` | repeated `K_E` builds on one rank-19 lattice: tree RSS 6544 and 6681 MiB, julia 5112 and 4907 MiB, both killed by the 6144 MiB guard |
| `p286b-stageI.log` | `algorithm="fast"` raises `ValueError: unknown algorithm` in 0.0 s |
