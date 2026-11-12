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

## #286, batch 3 (2026-11-10): the class machinery runs, neither card row is reproduced

Probes run inside the adopted image (`~/sage-image/run.sh` under `peakrss.py`, the port
bound at `/work` with `/work/src` ahead on `PYTHONPATH`, `/repos/sage-extensions` for the
library).  Every log is byte-for-byte the run's redirected output.

| log | result |
| --- | --- |
| `issue286c-genus-class-number.log` | genus of `E8(-1)^2 + <-2>`: `|Aut|` 1941728542064640000 in 0.3 s, mass in 1.1 s, then 4 classes from 10 random `p=3` neighbours in 19 s with `sum 1/|Aut|` equal to the mass **exactly** -- so `h(1) = 4`. `automorphism_group()` never returns (>90 s, killed) although `number_of_automorphisms()` is 0.3 s, which is why the `"orbits"` route never ran. For `<-4>` the traversal reaches 3 classes and then spends over 6 min inside one `qfisom` between two candidates with equal `|Aut|`; `h(2)` is not measured |
| `issue286c-plane-classes.log` | plane quotients from integer linear algebra (0.15 s each, no bridge): every quotient has determinant `+-2k` (one genus, as the fixture states). Bounded shape family of 1200 shapes: `k = 1` reaches **3 of 4** classes (`sum 1/|Aut| = 103651/555334363030487040000 < mass`), `k = 2` reaches **5 of 9** (`5903731/555334363030487040000 < mass`). The mass shortfall is the search's, reported as such; a partial family is never called complete |
| `issue286c-gamma-en-2.log` | `Involutions.I_En.polarized(h).coinvariant_extension_subgroup()` for `h = g_0 + g_1` (the `U(2) = S_dP` summand, `q(h) = 4`, primitive): builds in 24.0 s, `contains_character_kernel()` and `character_data_is_complete()` both `True`, `image_order()` **46998591897600** in 80.3 s (the issue's own number), `subgroup_image_order()` 696729600, index 67456. `isotropic_orbit_representatives(1)` then does not return in 1500 s (`launcher exit: 124`) |
| `issue286c-gate-029j-gated.log` | `tests/lattices/test_unpolarized_enriques_strata.sage` with the repository gate on (`each test call ceiling 20 s`): **2 passed in 61.61 s**, calls 38.75 s and 22.54 s, so the session is red on cost exactly as batch 1 recorded, not on a value mismatch |
| `issue286c-gate-029j-notime.log` | the same module with `--no-time-gates`: **2 passed in 66.14 s**, exit 0 |

Two setup facts cost a run each and are recorded in the batch record: without
`-b <port>:/work` the module fails at the port's `recursive.py:154` `TypeError`, and
binding the port without `/work/src` ahead on `PYTHONPATH` imports the image's port copy
and fails identically.  Both are the setup artefact already in `TRAPS.md`, not a finding
about card `029J`.

## #319 (2026-11-11): the card rows of the 87 numerical polarizations, and why they are undecided

`tests/enriques_polarization_rows_by_card.py` reads `tests/cards/lattice-database-enriques.json`
(database `dzackgarza/lattice-database` at `587d56fe`) and compares each row with the public
call.  Probes inside the adopted image, port at `/work`, `/repos/sage-extensions` for the
library.  Each log is byte-for-byte the run's redirected output.

| log | result |
| --- | --- |
| `p319-group-and-cardinality.log` | card `gamma-h-1` (`029J`, `S = overline{0}`): `Involutions.I_En.polarized(h).coinvariant_extension_subgroup()` builds in **38.0 s**, `contains_character_kernel()` and `character_data_is_complete()` `True`, and `finite_character_quotient().discriminant_image().order()` is **696729600** — the card's own `data.cardinality` — computed in 136.7 s.  Peak tree RSS 636 MiB |
| `p319-gamma-h-1-orbit-calls.log` | the same group, `group.isotropic_orbit_representatives(1)`, `(2)` and `(2, flag=True)` (the card's 5/9/18) each **did not return in 300 s** (SIGALRM stage abort); group rebuilt in 53.0 s, peak tree RSS 1174 MiB |
| `p319-gamma-h-1-runner.log` | the runner itself on `--tags gamma-h-1 --cap 120`: card citation printed, `S = overline{0}`, `|Gamma-bar_h| = 696729600`, then `UNDECIDED: lines: the public call did not return inside 120 s (after 185 s)`, `pass: 0, undecided: 1`, exit 1 |
| `p319-0128-h-unimodular.log` | `Lattices(ZZ)(W).Aut().vector_orbit_representatives(d)` on the card's own lattice: `d = 6` returns **2**, the card's `#h` at degree 6, in 111.8 s; `d = 2, 4, 8, 10, 12` did not return in 120 s each |
| `p319-0128-doubled-route.log` | the same `#h` asked of the doubled model `2W` at square 12 (the invariant lattice's own normalization): **did not return in 300 s**, which is why the runner reads `#h` on the card's lattice and transfers the coordinates |
| `p319-0128-runner-degree-6.log` | the runner on `--degrees 6 --cap 300`: `#h: expected 2, call 2 (285 s)`, then class 1 of 2 transfers to `q = 6`, the group builds, and the line call `UNDECIDED` at 300 s.  So the `#h` line is decided and equal; the `#Gamma-bar_h` line is not |
| `issue316-probe-orbit-counts.log` | `#316` | the finite-quotient counts: `Q`-orbits `527` and `23715` (`24242`), `rho(Gamma_En,2)`-orbits `9`, `|rho(Otilde+)| = 1`, one process, 163 s |
| `issue316-plain-pytest.log` | `#316` | `tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage`: **4 passed in 471.33 s**, exit 0, `addopts` blanked |
| `issue316-gate-setA.log` | `#316` | the same module plus three neighbours, repository `addopts` with `--no-time-gates --timeout=0`: **10 passed in 468.06 s**, exit 0 (rows 224.95 s and 100.31 s) |
| `issue316-gate-default-addopts.log` | `#316` | the same set under the untouched `addopts`: the `Gamma_En,2` row is killed by `pytest-timeout` at 60 s and the 20 s call gate reports it, so the session ends without a verdict |
| `issue321-probe-u-plus-u2.log` | `#321` | `U + U(2)`: `\|ρ(O(L))\| = 2`, class-set orbit 2; refusal without stabilizer data; 13 stabilizer generators (1.76 s) give 2 plane orbits |
| `issue321-module.log` | `#321` | `tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage`: **7 passed in 256.15 s**, exit 0 (`--no-time-gates --timeout=0`; rows 158.16 s and 68.91 s) |
| `issue321-gate-setA.log` | `#321` | the module plus `test_unpolarized_enriques_strata`, `test_enriques_anti_invariant_cusps`, `test_stable_isotropic_plane_orbits`, `test_line_stabilizer_image_requires_eichlers_hypothesis`: **16 passed in 420.13 s**, exit 0 |

## issue 317 — the genus of the Scattone summand `<-2k> + E8(-1)^2`

| log | commit | command | result |
| --- | --- | --- | --- |
| `issue317-genus-of-the-scattone-summands.log` | `HEAD` @ 317 | `pytest tests/lattices/test_genus_of_the_scattone_summands.sage` | 3 passed in 30.32 s, exit 0 |
| `issue317-genus-regression.log` | same | `pytest` over the seven genus-touching lattice modules | 2 failed, 21 passed in 577.11 s |
| `issue317-base-genus.log` | `git archive HEAD` tree | `pytest tests/lattices/test_genus.sage` at base | 1 failed, 9 passed — the same `spinor_genus_count() == 2` failure, so pre-existing |
| `issue317-base-embeddings.log` | base tree | `pytest tests/lattices/test_chosen_target_primitive_embeddings.sage` | 1 failed in 399.92 s inside the Julia bridge, so pre-existing |
| `issue317-k2-ninth-class.md` | — | probe logs quoted line by line | k = 2 reaches 8 of 9 classes; the ninth is `D_17(-1)` by the exact mass shortfall |

Exact command shape (the venv lacks `pytest-timeout`/`pytest-reportlog`, so
`addopts` is blanked and both repo plugins are named):

    PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src \
      /sage/.venv/bin/python -m pytest <paths> -q -o addopts="" \
        -p qc_sage_session -p sage_extensions.testing.suite_budget \
        --tb=short -rf -p no:cacheprovider --no-time-gates

The new module's class enumeration costs 29.62 s, above the 20 s per-call
ceiling, so a gated session reports it as a red cost (reported, not hidden).

Re-run on the rebased tree (main at `c31e90d`): `issue317-rebased-on-main.log`,
`pytest tests/lattices/test_genus_of_the_scattone_summands.sage` — **3 passed in
57.79 s**, exit 0 (enumeration call 56.48 s on the busier VM; the same four
classes and the same mass).

Follow-up on issue 317's ninth class, on the same tree: `issue317-probe24.log`
(sampled first generator, solved second generator — 7 u, 565 planes, 5 classes,
roots 204/224/264/480 against `D_17`'s 544), `issue317-probe22.log` (1400 splits,
17778 planes, 1 class), `issue317-probe23.log` (0 splits in 56 s).  All three logs
are byte-for-byte the launcher's redirected output.
| `issue295-red-module-not-found.log` | `#295` | the red failure at `7858c09d97`: `B.Aut().stabilizer(P, action="setwise")` raises `ModuleNotFoundError: No module named 'sage_indefinite_port.indefinite.pairing_slices'` at `lattice_morphisms.py:3723` |
| `issue295-t-en-identity-metadata.log` | `#295` | the second failure: the routing wrapper's `update_wrapper` doc copy runs `sageinspect` on a generated class → `TypeError`, reached from the port's `plane_automorphism_generators` via `one()` |
| `issue295-O-q-B2-engine-wall.log` | `#295` | `A.orthogonal_group()` for `A = (Z/2)^11`: `fqf_orthogonal._isom_fqf` → `orbits`, no return at 180 s |
| `issue295-image-order-in-O-q-B2.log` | `#295` | `order of the image in O(q_B(2)): 247726080` from the faithful action on the 2048 classes, 92 stabilizer generators, 220 s |
| `issue295-gate-setA.log` | `#295` | the new module plus four neighbours: **16 passed in 311.70 s**, exit 0 |

Second batch on issue 317 (cards by tag, spinor split, k = 2 diagnosis):
`issue317-summand-genus-from-card.log` — `tests/lattices/test_genus_of_the_scattone_summands.sage`
with the expected count read from card 6JRX plus the two-spinor-genus split test:
**4 passed in 83.24 s**, exit 0 (the enumeration call 82.52 s, gate red on cost);
`issue317-probe27.log` and `issue317-probe28.log` — the split on `diag(3,4,9)`,
`diag(1,16,17)` (4, 4) and `diag(1,16,20)` (3, 3); `issue317-probe29.log` — both
summand genera have one improper spinor genus and Sage uses p = 3;
`issue317-probe25d.log` — the repaired walk at p = 2, 3, 5, 7 reaches seven of the
nine k = 2 classes.

Re-run on the rebased tree (main at `d35c72c`): `issue317-rebased2.log`,
`test_genus_of_the_scattone_summands.sage` plus `test_genus.sage` — 13 passed,
1 failed in 30.92 s, and the failure is the pre-existing
`spinor_genus_count() == 2` on `diag(1,20,400)`.

Third batch on issue 317 (the k = 2 prime ladder and an exhaustive p = 2 sweep):
`issue317-probe30.log` — the mass-accounted walk at fifteen primes (2 … 47),
1440 lines, **8 of 9 classes**, mass ratio 0.99999937;
`issue317-probe31.log` — exhaustive enumeration of the seed's 2-divisible lines
(33296 of 131071 in 3223 s at 13 lines/s), **5 classes**, no 544-root class.
Neither reaches `D_17(-1)`.

Fourth batch on issue 317 (the correction and the real blocker):
`issue317-probe32.log` — `automorphism_group()` **returns** on the rank-17 k = 1
seed in **155.6 s** (repeat 186.8 s), and `orbits_lines_mod_p(3)` is killed at the
6144 MiB guard after 196 s building GF(3)^17;
`issue317-probe33.log` — the same walk with 5 mod-2 line orbits and no 2-neighbour
(corrected: the 2-neighbour lattice is not built this way);
`issue317-probe34.log` — k = 1 has 0 elements of order two in N^#/N and k = 2 has
exactly 1, so p = 2 cannot walk either genus.

Fifth batch on issue 317 (Nikulin's correspondence and the Vinberg chamber):
`issue317-nikulin-chamber.md` — the citation (Nikulin, Thm 1.14.2 p. 125, Prop.
1.15.1 with its proof p. 128-129), the chamber call, and the stop;
`issue317-probe35.log` — `fundamental_chamber()` on `U + E8(-1)^2` returns **19
wall roots in 76.9 s**, and the chamber vectors of square 2k reach 1 of 4 classes
for k = 1 and 1 of 9 for k = 2, with the right genus masses;
`issue317-probe35-walls-negative.log` — the same run with the wall sign reversed,
returning the same candidates, which is the diagnostic that the wall roots are
carried in a framing other than the coordinate basis.

Sixth batch on issue 317 (the frame, the bound, the classes):
`issue317-nikulin-chamber.md` — the frame resolved (wall roots are lattice
elements of square −2; model Gram = U ⊕ E8 ⊕ E8), the bound, and the class sets;
`issue317-probe37.log` — **k = 1: 4 classes, mass equal; k = 2: 9 classes
including the 544-root D₁₇(−1), mass equal**;
`issue317-chamber-test.log` — `tests/lattices/test_genus_of_the_scattone_summands.sage`:
**5 passed in 112.46 s**, exit 0 (the class enumeration 110.39 s).

Seventh batch on issue 317 (the truncations): `issue317-bound-full-buckets.log` —
the per-bucket `[:40]` slice removed, so every vector of both norm buckets is
tried and the nineteen wall tests run before the exact isometry test:
`tests/lattices/test_genus_of_the_scattone_summands.sage` **5 passed in 108.48 s**,
exit 0, the class enumeration 106.08 s against 110.39 s with the slice.
`coordinate_bound = 10` and the norm floor −40 remain; the note in
`issue317-nikulin-chamber.md` states exactly what the proof of them needs.

### #335: the Scattone plane rows of `6JRX` and `6JRY` (2026-11-11, base `7519715`, port `991b88b0`)

`isotropic_orbit_representatives(2)` on `Λ₂` and `Λ₄` does not return: the rank-2 branch
reaches `_planes_through_line`, whose candidate classification is the port's
`INDUCTION.isotropic_vector_classes` on the rank-19 Witt-index-one reduction
`⟨−2k⟩ ⊕ U ⊕ E8(−1)²`, and that call passes the 6144 MiB tree guard on `Λ₄` and does not
return on `Λ₁`'s reduction in 2400 s. The nine classes of `6JRY`'s `O` row are #334's,
mass-closed. The exact plane equivalence is not the defect: ten pairs of five distinct
classes all answer distinct.

| log | commit cited | result |
| --- | --- | --- |
| `issue335-probe2.log` | `7519715` (#335) | `Λ₄` by the public path: 1 line class in 23.1 s, split certified, then **STOPPED_AT_MEMORY_LIMIT tree RSS 6156 MiB** at 84 s in the port's rank-19 classification |
| `issue335-probe3.log` | `7519715` (#335) | the same in the card's own basis: 1 line class in 125.8 s, split certified, `K_v` rank 19 det 4 (1,18); the library's own line classification of `K_v` had not returned in fifteen minutes and was stopped |
| `issue335-probe1.log` | `7519715` (#335) | `Λ₂` under the public path: 1 `O(L)` line class in 30.6 s (the 4-plane row rests on the same rank-19 reduction) |
| `issue335-probe4.log` | `7519715` (#335) | planes built without the port: five of the nine classes in the box `|c|,|d| ≤ 3`, norm ≥ −24, mass short by exactly the four missing shares |
| `issue335-probe7.log` | `7519715` (#335) | the widened box `|c|,|d| ≤ 10`, norm ≥ −40: roots 244 and 304 added; **stopped at its 3000 s inner cap** (`launcher exit: 124`, peak tree RSS 1307 MiB) with nothing of roots 544 |
| `issue335-probe8.log` | `7519715` (#335) | `_isotropic_equivalence_witness` on ten pairs of five distinct plane classes: all ten distinct, 0.4–50.0 s per pair |
| `issue335-lint3.log` | `7519715` (#335) | `test_scattone_plane_orbits.sage -k test_the_card_inputs -p sage_extensions.testing.test_lint`: 1 passed, 4 deselected, no findings |
| `issue335-lint5.log` | rebased onto `900e866` (#335) | the same, after `#338` moved the card digest to database pin `d6a5393` and rewrote the reader: **1 passed, 4 deselected**, no findings, exit 0 |

## #354: the preimage's Schreier family (the stabilizer route)

`rho_L^-1(P)` for the decomposition stabilizer `P` of `A_{U(2)}` is the stabilizer of a point of
`O(L)`'s action on `A_L`, so Schreier's lemma (Seress, *Permutation Group Algorithms*, Cambridge
Tracts in Mathematics 152, CUP 2003, Lemma 4.2.1, p. 57) generates it from a transversal of that
orbit, with no generating set of `ker rho_L`.  `discriminant_point_orbit`,
`discriminant_point_stabilizer` and `discriminant_preimage(..., orbit_point=...)` are that route.
On card `0125` the orbit has 67456 points, `|O(q)| = 46998591897600`, and the family has
`15 * 67456 - 67455 = 944385` members; `2 * 348364800 * 67456 = |O(q)|` reads `|P|` from the two
summands' isometry groups, the other way to the same number.

| log | commit cited | result |
| --- | --- | --- |
| `issue354-preimage-test.log` | `f0003cd`, measured at its pre-rebase parent `15a3d13` (#354) | `tests/lattices/test_the_decomposition_preimage_returns_generators.sage`, `-p qc_sage_session -p sage_extensions.testing.suite_budget --no-time-gates`: **1 passed in 52.65 s**, no lint findings; the call takes 52.13 s, over the local 20 s call ceiling, which is reported and not enforced in this run |
| `issue354-preimage-test-head.log` | `f0003cd` on `f899ebd` (#354) | the same test at the pushed head: **1 passed in 54.30 s** (call 53.88 s), `--no-time-gates`, no lint findings |
| `issue354-subfamily-test.log` | `e514842` (#354) | the extended test: the nine-member subfamily's image order is `2 * 348364800` through `orthogonal.subgroup(...)`, every member preserves `A_{U(2)}`; **1 passed in 93.81 s** (call 93.35 s), `--no-time-gates`, no lint findings |

### #365: the radical's parameter lattice at `P₂`, decided class by class (2026-11-12, base `7ef38d5`)

Membership of a parameter `c` of the unipotent radical is not tabulated any more. The
translation `τ = −J⁻¹cᵗA_K` is linear in `c` and the plane block `Ja + aᵗJᵗ = −(Kc + cᵗKᵗ + cᵗA_Kc)`
is quadratic, so each depends on `c` modulo a modulus that `unipotent_parameter_modulus()`
derives from the equations and then verifies on their lcm: `2` at Sterk's `P₂` of `T_En`,
`1` at the splitting plane `P₁`. All `2¹⁶ = 65536` classes at it are decided, `4096` lift,
the lattice they generate has rank `16` and index `16`, and `4096 · 16 = 65536` is the
check that the admissible classes are a subgroup. The translations over that basis are a
`ℤ`-basis of `τ(U_I)` — rank `16`, covolume `1` — so `unipotent_radical_index()` is `1` at
`P₂`. The centre's generator is the generator of the lattice of integral `a` with `Ja`
skew: at `P₁`, with `J = diag(1,2)`, it is `((0,−2),(1,0))`, which the skew scalar `1` the
handed-over code passed cannot reach, so that code raised there and broke the splitting
plane's own test.

| log | commit cited | result |
| --- | --- | --- |
| `issue365-parameters.log` | `5b2c60c` (#365) | the probe, `P₂` then `P₁`: modulus, class counts, lattice rank and index, the translations' rank and covolume, the fourteen transvections' parameters, the centre's matrix `a` and its coordinate, `unipotent_radical_index()`, `is_parabolic_complete()` |
| `issue365-tests.log` | `5b2c60c` (#365) | the four test files, `test_lint` loaded: **15 passed in 118 s**, no findings |
| `issue365-lint.log` | `5b2c60c` (#365) | `test_lint` on the new test file and the two updated ones: **3 files, 0 findings** |
| `issue365-regression.log` | `5b2c60c` (#365) | the eight neighbouring files: **9 failed, 19 passed**, the nine pre-existing ones included |
| `issue365-base.log` | `7ef38d5` (main without #365) | the same three failing files on the base: **9 failed, 4 passed in 4.96 s**, the same nine ids |
| `issue365-regression-earlier-test.log` | `5b2c60c`'s code with the previous revision of `test_the_unipotent_radical_of_a_plane.sage` | the same eight files **before** that file was updated for the widened family: **10 failed, 18 passed in 340.58 s**, the tenth being the assertion that every radical generator is a transvection |

### #366: the setwise stabilizer's generators carry the radical, and `P₂`'s parabolic is generated (2026-11-12, base `75b048f`)

`L.Aut().stabilizer(P, action="setwise").group_generators()` at Sterk's `P₂` of `T_En` went
to the indefinite port and returned 23 elements carrying **one** of the radical's seventeen
block generators and the centre's generator.  The parabolic's completeness is now a
computation rather than the splitting hypothesis: `parabolic_completeness_decision()` computes
the radical's index, the plane actions of the members trivial on `P₂^⊥/P₂`, and the quotient
images of the members that fix `P₂` pointwise, and the family is the whole parabolic exactly
when all three are `1` — Milne, *Group Theory*, v4.01 of 6 November 2025, **Theorem 1.47
(Correspondence Theorem)**, printed **p. 22**, with **Corollary 1.48**, printed **p. 23**.
At `P₂` all three are `1`, so the predicate is `True`, `parabolic_obstruction()` is `None`,
and the public call returns the block family of 139 elements, which contains all seventeen
of the radical's generators and the centre's.  At `P₁`, which splits, the block equations
give the answer directly.  The radical's own generation is cited from the same theorem, and
the split-basis relations in `#353`'s docstrings were replaced by the equations the code
solves.

| log | commit cited | result |
| --- | --- | --- |
| `issue366-public-before.log` | `75b048f` (main without #366) | the public call before the change: **23 elements in 16.2 s**, 1 of the radical's 17 block generators and the centre's generator among them |
| `issue366-completeness.py`, `issue366-completeness.log` | `8430450` (#366) | the three factors at `P₂` (**1, 1, 1**), `parabolic_completeness_decision() = (True, None)`, `parabolic_obstruction() = None`, `|parabolic_stabilizer_generators()| = 139`; the same calls at the splitting plane `P₁`; and the public family at `P₂` |
| `issue366-tests.log` | `8430450` (#366) | the acceptance run of the five test files |
| `issue366-lint.log` | `8430450` (#366) | `test_lint` on the new and changed test files |
| `issue366-regression.log` | `8430450` (#366) | the neighbouring files with the change |
| `issue366-base.log` | `75b048f` (main without #366) | the same neighbouring file set without it |

### #360: the plane row of `T_Co` for `O(T_Co)`, and the parabolic at a `T_Co` plane (2026-11-11, base `2a43ce4`)

The plane-orbit call no longer reads its count off the finite divided-class set
where that set is not the orbit set: at a representative whose parabolic
`is_parabolic_complete()` establishes, it computes the double cosets
`ρ(Γ) \ ρ(O(L)) / ρ(G_x)` themselves and realizes each orbit by the splitting
isometry's transport (`_orbits_from_stabilizer`).  On `T_Co` that is what the
row needs, because the plane's stabilizer maps onto a subgroup of index **8** in
the stabilizer of its order-four isotropic subgroup — `1981808640 / 247726080`,
both orders computed — while its class set is one `ρ(O(L))`-orbit of `23715`
points, so the class-set count is short by exactly that factor.  The plane's
block basis was also repaired at its owner: completing it by keeping standard
basis vectors while they raise the rank leaves a sublattice of index `2` at that
plane, and the two completions are now the cokernels'
(`finite_free_trivialization`), which is the statement that a saturated
sublattice of a free `ZZ`-module is a direct summand.

| log | commit cited | result |
| --- | --- | --- |
| `issue360-parabolic-at-a-tco-plane.py`, `issue360-parabolic-at-a-tco-plane.log` | the tree of this push | at the `T_Co` plane of `test_the_tco_plane_orbit_and_its_composed_automorphisms.sage`: `is_parabolic_complete() = True` from its three factors (radical `1` in 6.4 s, plane actions `1` in 41.0 s, quotient images `1` in 4.9 s), `105` generators, `stabilizer_discriminant_image_orders() = (1981808640, 247726080)` and index `8` in 79.7 s; the block basis is `11` rows of determinant `1` (it was `2` before the repair, which now falls back on the cokernel completion); `T_En` at Sterk's `P₁`, `P₂` returns `±1` as before |
| `issue360-plane-orbit-by-stabilizer.py`, `issue360-plane-orbit-by-stabilizer.log` | the tree of this push | `ρ̄⁻¹(ρ(O(T_Co)))` has `[O(L) : Γ] = 1`, and `isotropic_plane_orbits([P])` returns **1** orbit in 82.6 s, its representative primitive and its divided class set the one handed in |
| `issue360-coble-plane-row.py`, `issue360-coble-plane-row.log` | the tree of this push | `Tco.Aut().isotropic_orbit_representatives(2)` stops after 9 min 6 s at `PariError: sorry, qfsolve, dim >= 10 is not yet implemented` (`lattice_engines.py:496` ← `lattices.py:4687` ← `isotropic_induction.py:84` ← `isotropic_orbits.py:1393`); the incidence stops with it |
| `issue360-regression.log` | the tree of this push | the neighbouring parabolic, plane-block, radical, divided-class and this issue's own rows with the change: **16 passed in 617.12 s** |
| `issue360-lint.log` | the tree of this push | `test_lint` on the new test module: **1 file, 0 findings** |

### #371: isotropy decided by theorem, and `T_Co`'s plane and incidence rows return (2026-11-12, base `40200e1`)

`is_isotropic` decided isotropy only by a witness search over the whole Gram
matrix, so it stopped where PARI's `qfsolve` does.  It is now decided by three
statements — definite forms represent no zero; an indefinite form of rank at
least five is isotropic by Meyer's theorem (Serre, *A Course in Arithmetic*,
Ch. IV, §3.2, Cor. 2, printed p. 43); rank at most four by Hasse–Minkowski and
the local invariants (Serre, Ch. IV, §3.2, Thm. 8, printed p. 41) — and the
witness of a rank-five-and-above form is built from five diagonal directions of
both signs, solved there with `qfsolve` (Denis Simon's code, as Sage's
`qfsolve` module states) and carried back; Hecke's `QuadForm/Quad/Spaces.jl`
`_isotropic_subspace` is the reference for answering rational isotropy by that
method, with Simon, *Quadratic equations in dimensions 4, 5 and more*.  The
reduction is stated for rank five, not rank ten, because the refusal is a
property of the solver's way and not of the dimension: a diagonal form of size
eleven answers and a nine-variable form of `T_Co` refuses.

| log | commit cited | result |
| --- | --- | --- |
| `issue371-test.log` | the tree of this push | `tests/lattices/test_the_isotropy_decisions_in_high_rank.sage`: **4 passed in 3.25 s** — `U + E8(-1)` (rank 10) and `T_Co` (rank 11) isotropic with a primitive witness of square zero, `E8(-1) + E8(-1)` (rank 16, definite) and `⟨1, -2⟩` (rank 2, indefinite) not isotropic and refusing a witness |
| `issue371-lint.log` | the tree of this push | `test_lint` on the new module: **1 file, 0 findings** |
| `issue371-qfsolve-bound.py`, `issue371-qfsolve-bound.log` | the tree of this push | `qfsolve` on `diag(-1, 1, …, 1)` for sizes 2 to 11: every size answers, so the `dim >= 10` refusal is not a size bound alone |
| `issue371-tco-plane-call.py`, `issue371-tco-plane-call.log` | the tree of this push | `T_Co.Aut().isotropic_orbit_representatives(2)` = **1** orbit in 1423.4 s, `cusps(2)` = 1, `isotropic_orbit_representatives(1)` = 1, `cusps(1)` = 1, `tits_building_incidence()` = **1** edge in 62.2 s; whole run 1495.3 s, peak 747 MiB |
## #358: the `Gamma_{Co,2}` line row on `T_Co`

The row is `isotropic_orbit_representatives(1)` on `Gamma_{Co,2} = rho^{-1}(P)`, `P` the
stabilizer in `O(q)` of `A_{U(2)} + A_{E8(-2)}` inside `A_{T_Co}`.  It returns **4 line orbits**.
`|O(q)| = 46998591897600` and `|P| = 696729600` (the two summands' isometry-group orders; the
engine's setwise stabilizer; and `|O(q)| / 67456`), `[O(T_Co) : Gamma_{Co,2}] = 67456`.  The stop
this unit repaired was the point stabilizer handed over as a bare predicate: a generator request on
a predicate subgroup of the *finite* group `O(A_{T_Co})` filtered an enumeration of all `4.7e13`
elements, killed at 4282 MiB.  `TorsionFormOrthogonalGroup.stabilizer_of_classes` gives `P` its
family (GAP's `Stabilizer` on the engine's own action) and `discriminant_point_stabilizer` keeps
its predicate with that family attached.  Two stages do **not** realize and are recorded, not
worked around: `Gamma_{Co,2}`'s Schreier family (`|S| * 67456 - 67455` members, ~2.3e7, killed at
5484 MiB) and `discriminant_lift` of one generator of `P` (killed at 6254 MiB).

| log | commit cited | result |
| --- | --- | --- |
| `issue358-reproduction-and-summands.log` | `7ef38d52cf` (pre-push base) | `O(A_{T_Co})`'s order **returns in 4.0 s** (`46 998 591 897 600`, GAP `HasSize` true, the `#323` half-integral odd-rank branch); the three summands of `A_{T_Co}` and `A_{U(2)}^\perp = A_{E8(-2)} + <[h/2]>` from the Gram data; `\|P\|` two ways = 696 729 600; orbit of `A_{U(2)}` = 67 456 |
| `issue358-the-predicate-stop.log` | `7ef38d52cf` | the stop: `orthogonal_quotients.py:706` -> `groups.py:5763` -> `groups.py:6755` -> `set_categories.py:4482`, **STOPPED at 4282 MiB** without returning in 2400 s; also the public `discriminant_point_orbit` at 67 456 in 318.9 s |
| `issue358-the-engine-stabilizer.log` | `7ef38d52cf` | the engine's setwise stabilizer of the four classes: order 696 729 600, three generators, every one fixing the point (307.7 s with the set-image function) |
| `issue358-the-action-comparison.log` | `7ef38d52cf` | GAP's own action against the set-image function on the same orbit: `Orbit` 67 456 in **2.89 s**, `Stabilizer` 696 729 600 in **86.85 s** |
| `issue358-schreier-family-stop.log` | `7ef38d52cf` | `preimage.group_generators()` on `T_Co`: **killed at 5484 MiB** (no stack; the process was reaped with `MemAvail` 764 MiB) after `index = 67456` and the image orders were computed |
| `issue358-the-lift-stop.log` | `7ef38d52cf` | `discriminant_lift` of one generator of `P`: **killed at 6254 MiB** |
| `issue358-row-idle.log` | `7ef38d52cf` | the row on an idle machine: `isotropic_orbit_representatives(1)` -> **4** in 265.8 s, with `image_order`, `subgroup_image_order = 696729600` and `index = 67456` |
| `issue358-row-and-representatives.log` | `7ef38d52cf` | the row's four representatives (vectors in the named basis, `div = 2`, `q = 0`) and their divided classes; the ambient stage costs 1917.5 s under contention |
| `issue358-index-per-class.log` | `7ef38d52cf` | the four divided classes rebuilt from those vectors reproduce the row's own printed lines; `[Stab_{O(q)}(c) : rho(Stab_Gamma(v))]` = 256, 17 280, 34 560, 15 360 and the class counts 2, 135, 270, 120 summing to the 527 nonzero isotropic classes |
| `issue358-card0125-regression.log` | `7ef38d52cf` | `tests/lattices/test_the_decomposition_preimage_returns_generators.sage` with the repair and the set-image function: 1 passed in 320.85 s |
| `issue358-tests.log` | pushed head | `tests/lattices/test_the_coble_gamma_co_2_line_row_returns_generators.sage` and the card-`0125` test with `-p qc_sage_session -p suite_budget -p test_lint --no-time-gates`: **2 passed in 541.79 s** (391.07 s and 150.14 s), no lint findings, peak tree RSS 4381 MiB |

## #370: the `Gamma_{Co,2}`-orbits of the admissible roots of `K_I` at a marked 0-cusp of `T_Co`

`IsotropicVectorReductionImage.root_class_orbits(roots, *, stabilizer_generators=None)` returns the
orbits of a finite family of **root classes** of `K_I = eta^perp/ZZ eta` under the certified action
of `Stab_{Gamma_{Co,2}}(ZZ eta)` on `K_I`, with a transporter (an isometry of `K_I` in `G_v`) per
class, checked by re-application; `root_class(vector)` reads the class of an ambient root.  Rank-one
difficulty: the acting family is not certified to generate `G_v` (#312), so an orbit of more than one
class proves equivalence and a singleton proves nothing.  Card `029J`'s `cusp_chambers` wall counts
(12, 10, 12) equal the computed number of distinct `K_J`-classes of the printed roots at cusps 1–3;
at `T_Co`'s cusp 3 the printed family meets `T_Co` in exactly one `(-2)`-class and the call returns
its orbit with the identity transporter.  Cusps 4–5 are blocked on the missing `T_En` transcription
of Sterk's diagrams 4.3.8 and 4.3.9.

| log | commit cited | result |
| --- | --- | --- |
| `issue370-tco-cusps-and-reductions.log` | `8e88c6a1c5` (pre-push base) | card `029J`'s cusp vectors read in `T_Co` at cusps 3–5: `q = 0`, primitive, `div = 2`; `K_I` rank 9, det 512, signature (1,8) at all three; `O(K_I)`'s chamber has 9 walls |
| `issue370-k-i-chambers.log` | `8e88c6a1c5` | the chamber's wall norms at cusps 3, 4, 5: eight `-4` and one `-2` each — the chamber is not the root family |
| `issue370-printed-roots-in-t-co.log` | `8e88c6a1c5` | `delta = e - f`; of the printed roots, 12/12 (`Sterk_1`, all `-4`), 8 of 10 (`Sterk_2`, all `-4`, the other two `±delta`) and 9 of 12 (`Sterk_3`, eight `-4` and one `-2`) are `delta`-orthogonal |
| `issue370-line-stabilizer-and-certification.log` | `8e88c6a1c5` | `T_Co` cusp 3: the line stabilizer returns **31** generators in 21.5 s, **16** of them certified in `G_v` in 159 s; `rho(K_v)` trivial; one `(-2)` printed root |
| `issue370-the-transcription-is-not-linear.log` | `8e88c6a1c5` | the 34 `TdP`↔`T_En` root pairs of the three transcribed cusps span rank 16 of 20 and impose an inconsistent linear system: no single linear map gives cusps 4–5's coordinates |
| `issue370-root-class-orbit-probe.log` | `8e88c6a1c5` | the orbit call on the printed roots: 12/10/12 distinct classes at cusps 1–3 and the refusal of a `-4` class |
| `issue370-tests.log` | pushed head | `tests/lattices/test_the_coble_root_orbits_at_a_marked_cusp.sage` with `-p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates`: **3 passed in 344.08 s**, no lint findings, peak tree RSS 1509 MiB |
## #369 — the stable orthogonal group generators call of card 0125 refuses

The owner's comment (2026-11-12) records that `5b75461d72` returned a family
under a generation claim that no published statement supports: the normal
closure of one Bertini involution in `W237` needs all its conjugates, not only
those by the simple reflections. The search this turn (Allcock's paper read in
full, the machine's research library, arXiv and the web) found no published
finite generating set of `Õ(L)`, so the call now refuses: it constructs and
certifies the family it could return (each member's discriminant image is
trivial) and then raises, stating that no published generation statement gives
a finite generating set of `Õ(L)` whose hypotheses this lattice meets.

| log | commit cited | result |
| --- | --- | --- |
| `issue369-refusal-test.log` | the tree of this push | the refusal test of `tests/lattices/test_the_stable_orthogonal_group_generators_refuse.sage`: **1 passed in 13.40 s** (the call certifies the Bertini family's membership in `ker ρ_L` inside `pytest.raises(ValueError)` and refuses; the index `|ρ_L(O(L))|` read by tag equals the card's own `46998591897600`) |
| `issue369-refusal-lint.log` | the tree of this push | `test_lint` on the new test module: **1 file, 0 findings** |
