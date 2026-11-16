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
| `391-incidence-route-smoke.log` | this push (#391) | the new incidence route vs the flag row on `U + U(2) + <2>`: **both routes 2 edges, agreeing, exit 0**, peak tree RSS 2800 MiB |
| `391-incidence-test-lint.log` | this push (#391) | `python -m sage_extensions.testing.test_lint` on the new test: **1 file, 0 findings** |
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
| `issue369-refusal-test.log` | the tree of this push | the refusal test of `tests/lattices/test_the_stable_orthogonal_group_generators_refuse.sage`: **1 passed in 14.43 s** (the call certifies the Bertini family's membership in `ker ρ_L` inside `pytest.raises(ValueError)` and refuses; the index `|ρ_L(O(L))|` read by tag equals the card's own `46998591897600`) |
| `issue369-refusal-lint.log` | the tree of this push | `test_lint` on the new test module: **1 file, 0 findings** |
| `issue370-tests-at-the-pushed-head.log` | `6664495b7c` (#370) | the same test file at the pushed head, after the cherry-pick onto `72c40a2` (#363): **3 passed in 311.40 s** (26.88 s and 280.60 s), no lint findings, peak tree RSS 1477 MiB |

## #355 — the rank-(n - 1) parabolic count on the W_e chamber of card 0125

The reported calls on the twelve-wall chamber of `W_e ⊂ G_e`
(`integral.cusp_chambers['g-e']`, Sterk, Math. Z. 207 (1991), (4.3.5), p. 19,
Fig. 4) are maximal for inclusion, not the criterion's rank condition, so the
criterion's computation is asserted from the chamber's own rays, with Vinberg's
citation (E. B. Vinberg, *The groups of units of certain quadratic forms*,
Mat. Sb. 87 (129) (1972), the English translation Math. USSR Sb. 16 (1972),
No. 1, Proposition 1, printed p. 22).

| log | commit cited | result |
| --- | --- | --- |
| `issue355-criterion-test.log` | the tree of this push | the criterion test of `tests/lattices/test_the_rank_n_minus_one_parabolic_count_on_the_we_chamber.sage`: **1 passed in 11.54 s** (the reproductions 36 and 44; the ideal-vertex count nine, read from the primitive rays; each ideal vertex's orthogonal walls have form rank \\(n - 1\\), the subdiagram parabolic or a parabolic union) |
| `issue355-criterion-lint.log` | the tree of this push | `test_lint` on the test module: **1 file, 0 findings** |

## #298 and #370 — the lattice isometry matrix, and the printed cusps carried into `T_En`

`results/issue298-the-lattice-isometry-matrix.md` and `results/issue370-the-coble-root-orbits.md`
state the calls and the counts; these are the runs behind them, at the trees of the two pushes this
batch made (`28422f9` + `f7eaa5d` for #298, `73d02b7` for #370).

| log | commit cited | result |
| --- | --- | --- |
| `issue298-isometry-matrix-tests.log` | `f7eaa5d` (#298) | `tests/lattices/test_the_isometry_matrix_between_isometric_lattices.sage`: **3 passed in 28.42 s**, the rank-eleven indefinite pair 26.64 s over the 20 s call ceiling; no lint findings |
| `issue298-isometry-matrix-probe.log` | the tree of the #298 push | the decision, the witness and the Gram equation of both test pairs and of a non-isometric control, pair by pair |
| `issue370-tests-at-the-fixed-head.log` | `73d02b7` (#370) | both files: **8 passed in 906.94 s** — the five-cusp card comparison 213.60 s, the `T_Co` cusp 3 run 359.16 s, the `T_En` cusps 4 and 5 orbits 243.86 s, the `T_Co` cusp 5 orbits 61.73 s, the #298 rank-eleven call 23.91 s; no lint findings |
| `issue370-cusp-transport-probe.log` | the tree of this push | the model `U + E8(-2)` against `K_J` at cusp 5 (pairings preserved, `is_isometric_to` `True`, transport determinant `2` for cusp 4 and `1` for cusp 5 by the matrix) and the lifted classes at both cusps |
| `issue370-cusp-lines-probe.log` | the tree of this push | the library's cusp vector against card `029J`'s row at all five cusps, and the eleven printed roots of 4.3.8 paired with each line: `[-6, 14, -8, 14, 6, 8, 12, 0, -6, -6, -12]` against the card's, all zeros against the library's |
| `issue370-t-co-cusp-orbits-probe.log` | the tree of this push | `T_Co`'s cusps 4 and 5: `K_I`, the classes in `T_Co`, the root classes, the line stabilizer's generator count and `root_class_orbits`' orbit count |
| `issue370-ten-cusps-orbits-probe.log` | the tree of this push | `T_En`'s cusps 4 and 5: eleven and fourteen distinct classes of `K_J`, two and four of them roots, and two and four orbits of one class each |
| `issue370-chambers-at-the-library-cusps-probe.log` | the tree of this push | the fundamental chamber of `K_I` at `T_Co`'s cusps 3, 4 and 5 read at the library's cusp vectors: nine walls each, eight of square `-4` and one of `-2` |

The probe scripts sit beside their logs under the same names with `.py`.
| `issue355-parabolic-test.log` | the tree of this push | the rewritten criterion test of `tests/lattices/test_the_rank_n_minus_one_parabolic_count_on_the_we_chamber.sage`: **1 passed in 22.37 s** (the call's count on the `g-e` chamber against the sum of the card's `parabolic_orbits` sizes — nine; each returned subdiagram the orthogonal-wall subdiagram of an ideal ray) |
| `issue355-parabolic-lint.log` | the tree of this push | `test_lint` on the rewritten test module: **1 file, 0 findings** |

## #376 — the sign in the two `2U + K` models

`results/issue376-two-u-signatures.md` states the four signatures, the wrong sign and the repair;
these are the runs behind it, at the tree of this push.  No log here shows a green module: the
third assertion of `tests/lattices/test_two_u_recursive_isometry.sage` asks for the port's isometry
witness, which does not return (see the last two rows).

| log | commit cited | result |
| --- | --- | --- |
| `issue376-signatures-probe.log` | the tree of this push | the four signatures and the two models' from their Gram matrices: `E8` (0, 8), `E8.twist(-1)` (8, 0), `_d16_plus_gram()` (16, 0), `D16+(-1)` (0, 16), the models (18, 2) and (2, 18); both decisions on that pair `False` in 0.0 s |
| `issue376-decision-probe.log` | the tree of this push | with the repair: `source.is_isometric_to(target)` **`True` in 126.1 s** (68.0 s and 56.6 s of it the two `discriminant_module().invariant_factors()` calls), and the complements' decision `False` in 43.3 s |
| `issue376-module-run-postrepair-2400s.log` | the tree of this push | the module: the first two tests pass, the third killed at the 2400 s inner cap (`shell_code=124`) inside the port's witness |
| `issue376-other-two-tests.log` | the tree of this push | the same module with the third test deselected: **2 passed, 1 deselected in 1.30 s**, no lint findings |
| `issue376-witness-cost-probe.log` | the tree of this push | the port's per-level costs on the rank-20 target: `OrbitCoverModel` 0.08 s, `source_easy_generators` 4.3 s for 8 generators, `covering_vectors(0, 1)` 37.2 s for one vector |
| `issue376-rank18-witness-probe.log` | the tree of this push | one Witt cancellation down: `(U + E8^2).is_isometric_to(U + D16^+)` `True` in 28.4 s, and its `isometry_to` killed at 300 s in `lorentzian_cells.py` `_expand_traversal_once` |

## #370 — the cusp-4 chamber anchored at the vector its figure is drawn at

`results/issue370-the-coble-root-orbits.md` states the map and the counts; these are the runs behind
them, at the tree of the push `1df83be`.

| log | commit cited | result |
| --- | --- | --- |
| `issue370-cusp-four-tests.log` | `1df83be` (#370) | the whole file: **4 passed in 3429.24 s** — the five-cusp card comparison 154.07 s, the two `T_En` cusps 698.21 s, the three `T_Co` cusps 2557.82 s; no lint findings |
| `issue370-cusp-four-test-alone.log` | the tree of this push | `-k cusps_four_and_five`: **1 passed in 580.35 s**, the card's `wall_vectors` against Sterk's transcription, wall for wall, and the `K_J` orbits |
| `issue370-t-co-cusps-test-alone.log` | the tree of this push | `-k coble_cusps_three_four_and_five`: **1 passed in 408.73 s**, the three `K_I` runs with their transporters |
| `issue370-cusp-lattice-consumer.log` | the tree of this push | `tests/lattices/test_cusp_lattices.sage`: **11 passed in 72.81 s** — where the two vectors of the fourth cusp are checked to be one cusp (their reductions are isometric) |
| `issue370-card-row-consumer.log` | the tree of this push | `test_the_five_cusps_are_the_chamber_rows_of_card_029j`: **1 passed in 98.65 s** — the card comparison still finding four agreements, `Sterk_4` being (4.2.3)'s vector, not the chamber's |

## #370 — the cusp-4 run at the card's vector, twice, for determinism

`results/issue370-the-coble-root-orbits.md` §4 states that the cusp-4 classes no longer depend on an
engine choice.  These are the two runs of that probe, in separate processes, at the tree of `8a21290`.

| log | commit cited | result |
| --- | --- | --- |
| `issue370-cusp-four-determinism-run1.log` | `8a21290` (#370) | the eleven walls of Fig. 10, the card's cusp vector `(0,0,2,1,-4,...)` beside (4.2.3)'s `(0,0,1,2,-4,...)`, nine classes of `K_I`, one root class `[-2,4,8,12,16,20,14,-5,1]`, 37 stabilizer generators and **one orbit with its transporter**, in 2140.6 s |
| `issue370-cusp-four-determinism-run2.log` | the tree of this push | the same probe again: the same eleven walls, the same nine classes, the same root class and the same one orbit |

The probe is `issue370-cusp-four-determinism-probe.py`.

## #380 — the Kneser 2-neighbour route and its runs

The route behind `isometry_to` for `2U ⊕ E8(−1)² → 2U ⊕ D16⁺(−1)` is
`LatticeIsometryMor._kneser_neighbour_isometry` (`lattice_morphisms.py`),
cited to Conway–Sloane 3rd ed. (Preface "Neighbours" p. lv; Ch. 26 §1 p. 525;
Ch. 17 §1 pp. 421–422).  These are its runs at the tree of this push.

| log | commit cited | result |
| --- | --- | --- |
| `issue380-kneser-neighbour.log` | the tree of this push | the neighbour search: the first candidate of the norm-(−4) shell of one `E8(−1)` summand, `v = [3, 6, 9, 8, 6, 4, 2, 4]`, gives `w = v + v` with `w·w = −8 ∈ 8ℤ`, `½w ∉ K`, and the neighbour `K′ = K_w + ℤ(½w)` of `|O(K′)| = 685597979049984000` — the order of `D16⁺(−1)` — in 10.9 s |
| `issue380-assembly.log` | the tree of this push | the assembly: `u = 2e + 2f + w` isotropic of divisibility one; `z = z₀ − (z₀²/2)u` with `z₀² = −2`; `M₁ = u^⊥ ∩ z^⊥` of the `D16⁺(−1)` order; the definite isometry `T₁₆` of determinant `−1` verified exactly; the placed column matrix verified exactly (`placed^⊤ G′ placed = G`); `M^⊤ G M = G′` **True** |
| `issue380-route.log` | the tree of this push | the public API: `source.is_isometric_to(target)` `True` in 308 s; `isometry_to` returned the witness, the inverse's row matrix of determinant `−1`, and the acceptance equation `M^⊤ G M = G′` **True** in 450 s |
| `issue380-test.log` | the tree of this push | the module: **3 passed in 423.56 s**, the target test 422.68 s under `--no-time-gates`, at 611 MiB peak, no lint findings |

## #391 — the transported plane retains its parabolic structure

`tests/lattices/test_isotropic_transport_retains_parabolic_structure.sage` exercises
`transport_isotropic_object` at the split plane of `2U`.  Its repair is issue #397,
needed by the Γ_{Co,2} plane row of #391.

| log | commit cited | result |
| --- | --- | --- |
| `issue397-transport-regression.log` | the tree of this push | **1 passed in 1.90 s**, transported primitive isotropic plane retains `is_parabolic_complete` and its exact inclusion in both directions |
| `issue397-transport-lint.log` | the tree of this push | **1 test collected, no lint findings** |

## #391 — the two T_Co incidence rows through the plane's parabolic

The command is the image Python with `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src` and the 6144 MiB `peakrss.py` guard.  No number is an expected oracle: the test checks containment of each edge's line in its plane and incidence of every line and plane cusp.

| log | commit cited | result |
| --- | --- | --- |
| `issue391-gamma-co2-staged.log` | the tree of this push | Γ_{Co,2}: subgroup 96.1 s; **4 line cusps at 328.4 s; 7 plane cusps at 391.8 s; 13 edges at 1382.6 s; assertions passed at 1388.1 s**; peak tree RSS 3710 MiB |
| `issue391-incidence-rows.log` | the tree of this push | unchanged `tests/coble_gamma_co_2_incidence_rows.py --cap 2400 --budget 2500`: **O(T_Co) 1 edge over 1/1 cusps in 112.9 s; Γ_{Co,2} 13 edges over 4/7 cusps in 1374.2 s; exit 0, peak tree RSS 3718 MiB** |

## #391 — test gate, the inherited collection blocker, and the branch/base comparison

The exact `just test` command first fails usage because the image's Python does not have the `--timeout` or `--report-log` plugins.  `-o addopts=` is therefore used with `--durations=0`; measurements name every override.  `--no-time-gates` lifts only per-call performance ceilings, and `--no-test-lint` is used for the old modules with their recorded findings.  The newly added #397 module has its own clean lint log.

| log | commit cited | result |
| --- | --- | --- |
| `issue391-just-test.log` | `a226af6af2` (#391) | 3915 items, **1 collection error in 198.20 s**: `tests/functions/test_young_convolution.sage`, integer-one divided by a real element recursively calls `modules.py:1704`; global lint adds 1514 pre-existing findings |
| `issue391-just-test-base.log` | `118a910bcf` | **same collection error in 190.27 s** on the unmodified base |
| `issue391-focused-runtime.log` | the tree of this push | 22 route-related modules: **78 passed, 10 failed in 1853.78 s**, including the Γ_{Co,2} incidence test **passed in 1071.52 s**; the time ceilings were disabled for these minutes-long rows |
| `issue391-failing-modules-base.log` | `118a910bcf` | exactly the same failing modules: **15 passed, 10 failed in 28.89 s** |
| `issue391-failure-comparison.log` | the tree of this push | **zero new failing test IDs**; all ten baseline failures are identical |
| `issue391-push-gate.log` | `a226af6af2` | `just test-push`: **7 files checked, no errors** (syntax only, not the suite) |
## #387 — the group of the card's chamber, and the exactness of contains_lift

The group question of the rewritten issue, with the walk diagnosis.  The
probes are `issue387-probe-*.py` under the session's `.scratch` (not tracked;
the commands are recorded in the results document and the logs carry the
launcher's peakrss footer).

| log | commit cited | result |
| --- | --- | --- |
| `issue387-probe-h.log` | `118a910` | the card's eleven walls and the walk's sixteen at the figure's cusp vector, in `T_En` coordinates: the walk's eight distance-zero walls are the card's `a8..a2` and `α9`; the eight additions pair positively (library convention) with the card's closing walls; the three true closing walls of the chamber containing `v0` pass the trusted filter `contains_root_reflection` |
| `issue387-probe-i.log` | `118a910` | the `T_En` coordinates of the controlling vector's lift and of all sixteen walk walls, for the local chamber computations |
| `issue387-probe-j2.log` | `118a910` | the repaired walk's acceptance log at Sterk_4 over 40 minutes: the three true closers all pass `contains_root_reflection`; the walk accepts eight additions at heights `√2..4√2` and gains none for thirty minutes — the stall inside one whole-layer `qsolve` |
| `issue387-probe-k.log` | `118a910` | `|A_{T_En}| = 1024`; the `H(2)`-summand `A_B = <[e'*], [f']*]` of order 4 with q-values `0,0,0,1`; its annihilator of order 256; `|ρ(Γ_library)| = 696729600` |
| `issue387-probe-l.log` | `118a910` | the robust annihilator-based membership data: the action of `O(A)` generators returns elements of an equal copy of `A` (parent-identity noise, not a group fact); the sanity checks `in_B` pass on `A_B` and fail on `[a1*]` |
| `issue387-probe-m.log` | `118a910` | **the equality**: `|D| = 696729600` from the block isometries in 9.7 s; `|ρ(Γ_library)| = 696729600`; `|join(D, ρ(Γ_library))| = 696729600` — the library's group is Sterk's group; `|O(A_{U(2)})| = 2`, `|O(A_{E8(2)})| = 348364800`; `|ρ(K_v)| = 1` at Sterk_4 |

| log | commit cited | result |
| --- | --- | --- |
| `issue400-probe-a.log` | `1a59869` | the cell at the Sterk_4 cusp-4 controlling vector: eight distance-zero normals of rank nine, their Gram Stieltjes with determinant 256 = det M1; the primitive lineality vector `m = (1, -1, -2, -3, -4, -5, -4, 1, 0, 0)` of square 4; the frame `(normals, m)` has index two in `v0^\perp`; the nonzero `W` representative has negative normal coordinates `[0, -1, -1, -2, -2, -3, -2, 0]` — the orthant of the candidate's coordinates needs the shift by them |
| `issue400-probe-b.log` | `1a59869` + #400 | **the agreement**: at Sterk_4 the restricted enumeration returns exactly the whole-lattice solutions with nonpositive normal coordinates, on every layer both searches reach (layers 1-13; the whole-lattice search dies at layer 14 with ~3.4M solutions, out of memory); per-layer times whole to restricted: 0.75 to 0.03, 0.29 to 0.01, 0.11 to 0.00, 2.31 to 0.05, 1.00 to 0.02, 9.72 to 0.30, 0.59 to 0.02, 36.71 to 1.33, 4.84 to 0.21, 112.72 to 4.53, 20.73 to 0.56, 3.38 to 0.05, 291.11 to 10.54 s |
| `issue400-probe-c.log` | `1a59869` + #400 | the walk at the Sterk_4 controlling vector, bounded to twenty decompositions: eighteen walls in 486.3 s, the first sixteen the documented stall state of `issue387-probe-j2.log` and the last two at height `6 sqrt(2)`, past the stall height `4 sqrt(2)` |
| `issue400-probe-d.log` | `1a59869` + #400 | the basis branch of the same enumeration at Sterk_1 (the class of `x = e' + f'`): ten layers, zero failures — the restricted set equals the whole-lattice solutions with nonpositive normal coordinates there too |
| `issue400-tests-focused.log` | #400 | `tests/lattices/test_the_isotropic_reduction_image.sage` with `-k "not every_cusp_chamber"`: **8 passed, 1 deselected in 623.89 s** with `--no-time-gates`; the new regression 464.40 s, the #285 first-cusp regression 38.24 s, both over the 20 s ceiling (recorded, not hidden) |
| `issue400-just-test.log` | #400 | the whole-suite substituting invocation on the #400 tree: 3916 items, 1 error, 1514 lint findings — dies at collection exactly as on base |
| `issue400-just-test-base.log` | `1a59869` | the same command on the base tree: 3915 items, 1 error, 1514 lint findings — the whole suite cannot run past collection on base either (pre-existing since #391); the +1 item and no new failure is the whole of #400's difference |
## #391 — the incidence relation, not the finer flag-record count

The two historical process summaries returning 13 and 15 records counted candidates before the incidence relation was formed.  Let `Pi = Stab(P)`, `K = Gamma cap Pi`, `H = Pi cap Stab(ell)`, and `R <= H` be the group generated by the retained line-fixing parabolic generators.  The natural map `K g R -> K g H` is well-defined and surjective.  DSH, arXiv:2302.01679v2, Lemma 3.6, printed p. 22, descends it to the finite discriminant image; the printed statement calls the correspondence many-to-one.  Retaining one actual flag per line/plane cusp pair therefore decides exactly the incidence, independent of the double-coset representatives.

For one edge, if `a(ell) = L` and `b(P) = Q` are the retained cusp transporters, `g = b a^(-1)` belongs to Gamma and `gL = b(ell) <= bP = Q`.  The acceptance test checks that containment on the selected cusp representatives, endpoint uniqueness and full vertex coverage.  Across the pinned and Actions-port outputs, the sorted line/plane degrees also agree: `(1, 3, 3, 6)` and `(1, 1, 2, 2, 2, 2, 3)`.

The source-registry diagnostic also established why a mismatched source reached the old generic isometry search: the single ambient flag's plane was not the registered ambient plane representative, while every target lift was present.  The repaired call normalizes this source once against the small registered representative and composes with each retained target lift.

| log | commit cited | result |
| --- | --- | --- |
| `issue391-pinned-port-baseline.log` | base `1a59869ba6`, port `991b88b0` | **13 flag records and 13 distinct endpoint pairs in 1599.3 s**; every line and plane cusp covered; peak tree RSS 3531 MiB |
| `issue391-actions-source-registry.log` | base `1a59869ba6`, Actions port `54d12c2e` and categories `01d1219c` | 1 ambient flag and 7 target lifts, but the source lift is **missing at every target**; the diagnostic returns without the generic search in 464.6 s |
| `issue391-ambient-source-witness.log` | the tree of this push | the small ambient-source search returns a witness in 8.62 s; its transported plane has the exact registered source coordinates |
| `issue391-incidence-actions-repaired.log` | the tree of this push, the Actions port and categories revisions (.scratch `pycddlib=3.0.2` supplies the published image's `cdd.gmp`) | public acceptance: **O(T_Co) 1 edge over 1/1 cusps in 95.1 s; Gamma_{Co,2} 13 edges over 4/7 cusps in 1449.3 s**, every direct orbit-incidence witness asserted; peak tree RSS 3064 MiB |
| `issue391-incidence-focused.log` | the tree of this push, port `991b88b0` | **2 passed in 2367.28 s**: 13 Gamma edges over 4/7 cusps and the ambient one-edge row, with all containment and endpoint-uniqueness assertions |
| `issue391-incidence-route-smoke-repair.log` | the tree of this push | small rank-five comparison: **2 edges by the repaired public call and 2 by the flag row**, all cusps covered; peak tree RSS 2375 MiB |
| `issue391-incidence-lint-repair.log` | the tree of this push | changed incidence test: **1 file, 0 findings** |
| `issue391-special-building-repair.log` | the tree of this push | inherited SO(2U) stabilizer-certification error in 8.26 s; the incidence return is not reached |
| `issue391-special-building-base.log` | base `1a59869ba6` | **identical failure ID and identical certification error** in 8.14 s |

## #391 — literal repository gate and same-base comparison

The literal `just test` stops at pytest usage because this image lacks the configured timeout and report-log plugins.  The `-o addopts=` override reaches collection.  Repair and clean base collect the same 3915 items and fail identically on the unrelated Young-convolution recursion; neither suite completes.

| log | commit cited | result |
| --- | --- | --- |
| `issue391-just-test-literal-repair.log` | the tree of this push | **exit 4 before collection**: unrecognized `--timeout=60 --timeout-method=signal --report-log=tests/.report/run.jsonl` |
| `issue391-just-test-repair.log` | the tree of this push | `just test -o addopts= --durations=0`: 3915 collected, **1 inherited collection error in 281.61 s** at `tests/functions/test_young_convolution.sage` |
| `issue391-just-test-final-resource-kill.log` | tree of this push, repeated after the source repair | the additional final-tree run was killed by host memory pressure, exit 137 after 275 s; no collection result; MemAvail reached 918 MiB alongside other projects' jobs |
| `issue391-just-test-base-1a59869.log` | clean base `1a59869ba6` | same 3915 collected, **same collection error in 298.04 s** |
| `issue391-push-repair.log` | the tree of this push | `just test-push`: **7 files checked, no errors** (syntax check, not a suite claim) |
| `issue400-tests-agreement.log` | #400 | the per-layer agreement regression on the #400 tree: `tests/lattices/test_the_isotropic_reduction_image.sage` with `-k "not every_cusp_chamber"` — **9 passed, 1 deselected in 780.56 s** with `--no-time-gates`; the new layer-agreement test 57.73 s (initial cone plus four layers, duals verified then both enumerations compared), the walk-progress regression 542.26 s, both over the 20 s ceiling (recorded, not hidden) |
## #401 — the Vinberg call returns the facets of the polyhedron it cuts out

The gate pair runs at the base `1edc223` and on this tree, in two worktrees of the same checkout.  The probes and the wall dumps ran at `cf656f8` and on an intermediate rebase; they depend on `hyperbolic_lattices.py` alone, and `issue401-failed-sets.txt` records that file's sha256 on each tree so the correspondence is checkable.  The probes run under `peakrss.py` with the 6144 MiB guard; the pytest runs use `just test -o addopts= -p sage_extensions.testing.suite_budget --no-time-gates` with `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src` from `/repos/sage-extensions` and the port bound at `/work`.  The literal recipe does not run here at all — its addopts name `--timeout` and `--report-log`, and pytest-timeout and pytest-reportlog are absent from the image's venv — so every run names `-o addopts=` and its plugins.

| log | commit cited | result |
| --- | --- | --- |
| `issue401-facets-survey.log` | the tree of this push | accepted roots against facets of the intersection: \(U\oplus A_1\) **3/3**, \(U\oplus E_8\) **10/10**, \(U\oplus E_8\oplus E_8\) **19/19**, \(U\oplus E_8(-2)\) **10/10**; no completed chamber carries a non-facet root |
| `issue401-bounded-prefixes.log` | the tree of this push | the same on bounded prefixes, `max_roots` 1..12 and `max_decompositions` 2..20: **accepted = facets** at every bound, including the two truncations that return 9 roots |
| `issue401-small-lattices.log` | the tree of this push | eight small hyperbolic lattices (3, 4, 5, 4, 6, 5, 6 and 12 accepted): **accepted = facets** in each |
| `issue401-redundant-root-specimen.log` | the tree of this push | \(U\oplus A_1\oplus A_1\): four walls, each cutting a face of dimension 3; \(a_1+a_2\) primitive of square \(-4\); the cone with it as a fifth wall has **4 facets** and cuts a dimension-**2** face on it |
| `issue401-cusp-walls-base.log` | `cf656f8` | the public `cusp_chamber` wall sets at Sterk's cusps 1, 2 and 3: **12, 10, 12**, with coordinates |
| `issue401-cusp-walls-mine.log` | `c15b432`, same `hyperbolic_lattices.py` as this push | the same three, **byte-identical** to the base dump |
| `issue401-cusp-5-walls.log` | `c15b432`, same file as this push | cusp 5's public chamber: **complete, 14 walls** — against card `029J` row 4.3.9's thirteen, so the extra wall is irredundant and not a redundancy artefact; cusp 4 does not return (a 19-minute run stopped inside it), which is #400's walk and not this call |
| `issue401-facet-tests.log` | `1edc223` + this commit | the new module alone: **5 passed in 11.68 s** |
| `issue401-gate-base.log` | `1edc223` | the 25 suite files that name a changed operation, `--continue-on-collection-errors -q --deselect ...test_every_cusp_chamber_has_the_wall_count_of_its_card_row`: **41 failed, 149 passed, 1 deselected in 3329.47 s** |
| `issue401-gate-mine.log` | the tree of this push | the same 25 files: **41 failed, 149 passed, 1 deselected in 3386.93 s** |
| `issue401-failed-sets.txt` | both trees | **the FAILED id sets are identical, 41 ids: nothing new, nothing repaired**; the full command; why the one test is deselected; the source checksums of the two trees |
| `issue401-whole-suite-base.log` | `cf656f8` | the whole suite over `tests`: `collected 3916 items / 1 error`, killed by the OOM killer at 15% (exit 137) |
| `issue401-whole-suite-mine.log` | `c15b432`, same file as this push | `collected 3921 items` — the five new tests — killed by the OOM killer at 15% (exit 137); the suite's 4 GiB-per-process rows do not fit beside the other sessions' runs on this VM, at either tree |
| `issue387-cusp4-layers.py` | the tree of this push | the probe: the public `cusp_chamber` at Sterk_4 with the walk's own layer enumeration instrumented — a subclass substituted for the module attribute `_filtered_vinal_class`, so the run is that call and not a re-implementation — recording per layer its distance, its `k`, its time, the peak RSS and the number of candidates, and after each acceptance the finite-volume test (`is_FundPoly`) and whether the accepted root's half-space is one of the eleven printed walls of Sterk (4.3.8), Fig. 10, p. 23 |
| `issue387-cusp4-filter.py` | the tree of this push | the probe: every wall the same walk accepts, decided by both public membership doors — `admits_root` (the walk's own filter) and `contains_root_reflection` (through the Levi image `reduction_image`) — and each of the eleven printed walls asked of the filter |
| `issue387-cusp4-layers-figure.log` | the tree of this push | the record at the cusp **of the printed chamber**, `2e' + f' + alpha-bar_1` = `(0,0,2,1,-4,-5,-7,-10,-8,-6,-4,-2)` — the vector card `029J`'s 4.3.8 row stores — bounded at `max_decompositions=40`: **all eleven printed walls lie in that cusp's perpendicular**, the walk accepts **eighteen** roots of which the first sixteen are eight of square `-4` and eight of square `-2`, `is_FundPoly` false after every acceptance, and the layer enumeration growing `252 → 1184 → 5796 → 25315 → 84922 → 269218 → 659684` candidates. **The record's printed-wall column is superseded**: it lifted a class through `class_lift`, whose `to_vector` is in the perpendicular subobject's frame and not in `T_En`'s, so its "no" for every wall is not a measurement — the corrected comparison is `issue387-cusp4-facets.log` | 
| `issue387-cusp4-layers-row.log` | the tree of this push | the same record through the row's own call, at `Sterk.selected_isotropic_vectors()["Sterk_4"]` = (4.2.3)'s `e' + 2f' + gamma` = `(0,0,1,2,-4,-5,-7,-10,-8,-6,-4,-2)`, bounded at `max_decompositions=12`: the same sixteen accepted walls, the same growth, `is_FundPoly` false throughout; its printed-wall column has the same defect and is superseded by `issue387-cusp4-facets.log` |
| `issue387-cusp4-filter.log` | the tree of this push | the sixteen walls the walk accepts at the printed chamber's cusp, decided by both public membership doors: **16 agreements, 0 disagreements** — `admits_root` (the walk's filter) and `contains_root_reflection` (through the Levi image) say the same thing of every one, so the accepted set is the honest chamber of the group the filter defines and the membership stage is not where a spurious reflection enters; the printed-wall column of the layer record is not decided by this log (it is superseded below) |
| `issue387-cusp4-facets.py` | the tree of this push | the probe: the facets of the polyhedron the sixteen accepted normals cut out, decided by the library's `_facet_roots`, each compared with the eleven printed walls of (4.3.8) by a class lift built from the reduction's own `coordinate_frame` in `T_En` coordinates |
| `issue387-cusp4-facets.log` | the tree of this push | at the printed chamber's cusp, bounded at `max_decompositions=12`: the sixteen accepted normals are **sixteen facets** — none is redundant — so the prefix's polyhedron is neither the card's chamber nor a superset of it, and `is_FundPoly`'s silence is the silence of a prefix. **The row's printed-wall column is retracted**: the lift it compares against was built from `coordinate_frame()`'s elements, which carry eleven coordinates in the *perpendicular's* frame, while the printed walls carry twelve in `T_En`'s, so the zip silently misaligned and its "seven of sixteen" is an artefact — see `issue387-cusp4-liftshape.log`, and the verified route is `class_lift`, which returns twelve |
| `issue387-cusp4-liftshape.py` / `issue387-cusp4-liftshape.log` | the tree of this push | what a class lift's coordinates are: `coordinate_frame()` has ten entries, each an element of the perpendicular with **eleven** coordinates; `perpendicular.inclusion()` of one, and `image.class_lift()` of a reduction vector, are elements of `T_En` with **twelve**. So a comparison against Sterk's printed walls must use `class_lift`, and any lift summed from the frame by hand is misaligned by one coordinate |
| `issue387-cusp4-redundancy.log` | the tree of this push | the decisive one: the cone of the eleven printed covectors (dimension 10, 11 extreme rays) against the sixteen accepted walls' covectors, lifted through `class_lift`. **Seven** of the sixteen half-spaces are implied by the card's eleven — the six `E8(-2)` simple roots and `f - e` — and **nine are not**: one of square `-4` and eight of square `-2` cut strictly more than card `029J`'s chamber. So the walk's polyhedron is strictly *smaller* than the card's, and no enumeration speed makes eleven printed walls come out of it |
| `issue387-cusp4-nine-lifts.py` | the tree of this push | the probe the owner asked for: for each of the sixteen accepted walls, the lifts `class_lift(r) + k v` of the class into `v^perp` (`k` in `[-2,2]`; `b(a,v)=0` and the square is coset-invariant, both measured), the reflection `s_a` where it is integral, and three conditions tested on `s_a` itself, never through `contains_lift` or `admits_root`: integrality against the lattice's own generators and form, the real spinor norm `sn_R(s_a) = -q(a)/2` (Gritsenko--Hulek--Sankaran Sec. 1), and `rho(s_a)` against the subgroup the library builds as `Gamma_{En,2}` through `coinvariant_extension_subgroup` (AEGS Definition 2.6). Sterk's Proposition 2.7 (source lines 225--240) states that group *precisely* as the set of `g` whose induced map on the discriminant respects the decomposition in two summands -- a condition on `rho(g)` alone, with no spinor-norm clause -- so the three are recorded separately rather than fused |
| `issue387-cusp4-nine-lifts.log` | the tree of this push | the record per lift, 111 s. Every one of the sixteen reflections is an **integral** isometry of `T_En` fixing `v` (no integrality failure at any `k`, `b(lift,v)=0` throughout), so integrality excludes nothing. All sixteen have `rho(s_a)` in the library's discriminant image at `k = 0`. The split is by square: the reflections in square `-2` classes have `sn_R = 1` and pass all three conditions at every `k` -- this includes **all seven** square `-2` walls among the nine that card `029J`'s eleven do not imply -- while the reflections in square `-4` classes have `sn_R = 2` at every `k` (coset-invariant) and pass the discriminant condition only at even `k`. So **seven of the nine non-implied walls** have a `g` in the group fixing `v` and inducing `s_r` on `v^perp/Zv` with all three conditions met; the two square `-4` ones (the walls whose covectors are `(2,-5,-10,-15,-20,-25,-18,6,0,2)` and `(-30,72,145,218,291,364,257,-90,-16,-16)`) meet the integrality and discriminant conditions and fail only the spinor one |
| `issue387-cusp4-nine-lifts.log` (**corrected** by `issue387-cusp4-mirrors.log`) | the tree of this push | the spinor column of that log is struck: the real spinor norm takes values in `RR^x/(RR^x)^2` and `2` is a square in `RR`, so `sn_R(s_a) = -q(a)/2` is `1` for `q(a) = -4` exactly as for `q(a) = -2`. **The spinor condition excludes none of the sixteen**, the split that log reported between the square `-2` and square `-4` walls was over `QQ` and not over `RR`, and at `k = 0` all nine unprinted walls have a lift in Sterk's group fixing `v` and inducing the reflection |
| `issue387-cusp4-mirrors.py` | the tree of this push | the two questions the corrected reading forces: (1) whether each of the sixteen walls' mirrors meets the interior of the polyhedron `P` that card `029J`'s eleven cut out -- decided as cone membership, `b(r,x) >= 0` being implied by the eleven exactly when the covector of `r` is in their cone, so the mirror meets the *interior* exactly when neither `r` nor `-r` is in it; (2) card `029J` row 4.3.8 against Sterk's (4.3.8) with Fig. 10, p. 23 -- the cusp vector, the eleven wall vectors, and the diagram's ten edges against the computed Gram matrix by `cos(pi/k) = b_ij/sqrt(q_i q_j)`, the relation for vectors of unequal square |
| `issue387-cusp4-mirrors.log` | the tree of this push | 24 s, exit 0. **All nine** unprinted walls -- indices 0, 8, 9, 10, 11, 12, 13, 14, 15 of that log's list -- have `r` and `-r` both outside the cone, so each mirror meets the interior of `P`, and for each an interior point on the mirror is recorded and certified exactly: the least pairing with the eleven is `1` and the mirror pairing is `0`. The seven implied walls have `r` in the cone and are facets. So no chamber of the group of Proposition 2.7 has eleven walls at this cusp. The card agrees with the figure in every respect: the cusp vector is `(0,0,2,1,-4,-5,-7,-10,-8,-6,-4,2)`... exactly the library's, all eleven wall vectors are identical, and **all ten** of the row's edge orders are confirmed by the computed Gram -- the two order-4 edges `alpha_3--alpha_11` and `alpha_9--alpha_12` are precisely the two that join a square `(-2)` vector to a square `(-4)` one |
| `issue387-cusp4-lifts.py` | the tree of this push | the three checks, on the lattice's own pairing and with no discriminant image anywhere: (1) each of the seven square `(-2)` walls of the walk lifts to an integral vector with square `-2` and zero pairing with `v`; (2) each of the nine witnesses is spacelike and lies on the chamber's side of the positive cone; (3) the card's eleven pass the same checks in the same coordinates. It also records the pairing of every one of those vectors with the polarization `h = e' + f' = (0,0,1,1,0,...)` (`h^2 = 4`, `b(h,v) = 6`) -- the datum AEGS Definition 2.6 turns on, and the one a *class* of `v^perp/Zv` does not carry |
| `issue387-cusp4-lifts.log` | the tree of this push | 24 s, exit 0. **Step 1 holds outright**: all seven square `(-2)` walls lift integrally with square `-2` and `b(lift,v) = 0`, so the premise `r` lifts to a `(-2)`-vector orthogonal to `v` is true. **Step 2 holds**: every witness has `x^2 = 44 > 0` and `b(x,v) < 0`, the chamber's side of the positive cone -- they are in the hyperbolic space, not outside it. **Step 3 holds**: the card's eleven are integral, square `-4` and `-2`, with `b(w,v) = 0`. What fails is the step between 1 and the conclusion: `s_rt` fixes `h` only when `h` is orthogonal to `rt`, and `b(lift,h)` is `-42, -46, -104, -162, -166, -220, -228` for the seven. Since the lifts of a class are `rt + k v` and `b(v,h) = 6`, an integral `h`-orthogonal lift exists exactly when `6` divides that value: it does for walls **8, 12, 15** (`k = 7, 27, 38`) and for no `k` for walls **9, 10, 13, 14** (residues `4, 2, 4, 4`). So the argument that a `(-2)`-mirror cannot meet a chamber covers three of the seven and not the other four. It also cannot be a necessary condition: the card's own `alpha_10, alpha_11, alpha_12` have `b(w,h) = 4, -2, -4` with no integral clearing lift either, yet they are walls of the printed chamber |
| `issue387-cusp4-span-attempt.py` / `issue387-cusp4-span-attempt.log` | the tree of this push | **step 1 of the span batch, not completed — the blocker, so the next chat does not retrace it.** Two facts it established before stopping: `algebraic_correlation_morphism()` returns **twelve**-coordinate covectors (the ambient dual), not the ten of `v^perp/Zv`, so a span computed there is not the span's index in the quotient; and `reduction.projection()`'s **source is the rank-11 lattice `v^perp`**, not rank-12 `T_En`, while `class_lift` goes the other way (`v^perp/Zv` -> `v^perp`) and the library exposes no section back, so a card wall given in `T_En` coordinates cannot be handed to it (`TypeError: ... does not describe an element of Integral lattice of rank 11 and signature (1, 9)`). The route that avoids both: work in `Z^12` with the Gram built from the ambient pairing, take `{v} + {class_lift(g)}` over the reduction's generators as a basis of `v^perp`, and compute `[v^perp : M + Zv]` as the square root of the ratio of the two Gram determinants, membership by Smith form of the generating matrix |
| `issue387-cusp4-span.py` / `issue387-cusp4-span.log` | the tree of this push | **step 1 of the span batch, measured, and it refutes the premise of step 2.** In `Z^12` with the ambient Gram, a basis of `v^perp` is `{v}` together with the class lifts of the reduction's module generators; the card's eleven have **rank 10** there, so they are of full rank in `v^perp/Zv`; and since a lattice index needs no quadratic form, the index is the ratio of coordinate covolumes: `det Gram(M + Zv) = 96` against `det Gram(v^perp) = 6`, so **[v^perp : M + Zv] = 4** (exact: `96/6 = 16`, square root `4`). **Every one of the sixteen walk walls lies in M + Zv** -- decided by the Smith form of the eleven together with `v` -- so the seven unprinted walls are Z-combinations of the card's eleven and no wall lies outside their span. The index-2-sublattice reading of (4.3.10) therefore does not explain the eleven-versus-sixteen discrepancy in the library's coordinates. The Smith diagonal `(1,1,1,1,1,1,1,1,1,1,2,0)` is an elementary-divisor statement relative to `Z^12` and is *not* the index above; both numbers are printed so they are not confused later |
## #390 — the coset-walk realization of the kernel plane rows

The realization of each double coset as a plane of `T_Co`, through one
breadth-first walk over the right-coset action of `rho(O(L))` on
`rho(O(L)) / rho(Stab P)` (GAP's `FactorCosetAction`), each reached coset
carrying the ambient generator image that carried its parent there.

| log | commit cited | result |
| --- | --- | --- |
| `issue390-main-percoset-profile.log` | main `118a910` | the per-coset cost the walk replaces: 154 ms per double coset over 60 cosets (102 ms `PreImagesRepresentative` word problem, 48 ms spelling, 1.7 ms permutation preimage; transport 1.5 ms), so 189720 cosets are 8.1 h per row |
| `issue390-small-lattice-rows.log` | the tree of this push | the order-based expected-count formula equals the rows on `6JRS` and `U+U(2)+<-2>` (both kernel rows of both lattices) |
| `issue390-coset-walk-validation.log` | the tree of this push | the walk on `6JRS`, `U+U`, `U+U(2)+<-2>`, `U(2)+U(2)+<-2>`: both kernel rows and a point-stabilizer row each equal their independently enumerated double-coset counts, and no two row planes are `Gamma`-equivalent (the subgroup's own equivalence witness); the run was cut by the caller during the last pairwise check with every completed row green |
| `issue390-gate.log` | the tree of this push | the gate on the touched files: **10 passed in 599.17 s** (`--no-time-gates`; the four calls over the 20 s gate: the new kernel-plane gate rows 24.9 s and 33.3 s, the line-orbit row 25.4 s, the `Gamma_{Co,2}` plane row 508.2 s), the line-orbit row green after the point-branch `return` repair |
| `issue390-tco-rows.log` | the tree of this push | on `T_Co` itself: the order-formula expected counts `Otilde` 189720 (`|im rho| = 46998591897600`, `|rho(H)| = 247726080`), `Otilde+` 189720 (`|chi(G)| = 93997183795200`, `s = 2`), `Gamma_{Co,2}` 7 by `DoubleCosets`; the `Gamma_{Co,2}` plane row through the public call: **7 planes in 127.7 s**, count matching, sample planes primitive isotropic, peak tree 3860 MiB; the two kernel rows did not return inside a 4200 s probe cap (each needs about 75 min on this VM -- 189720 owned products and transports -- with memory stable at 2.0 GiB python after the streaming repair), so they are the `coble-kernel-plane-rows` CI job's to decide against its 10800 s per-row cap |

| `issue390-stage-slice.py` | main `484e4c52` | the probe: the public `stable.isotropic_orbit_representatives(2)` on `T_Co` under `Otilde`, sliced by stage from outside the library -- a timing proxy on the module's `libgap` (so the row's own GAP primitives are timed), wrappers that keep the caches in force on the quotient's methods, a wrapper on the lift iterator that separates the block before its first yield from the work of each lift after it, the lift's own `transport_isotropic_object` and the quotient's `register_isotropic_lift`, and a two-second `/proc/self/status` sample tagged with the stage the row is in; `smoke`, `cap=<seconds>` and `no-shim` are the three modes the logs below use |
| `issue390-stage-slice.log` | main `484e4c52` | the 5400 s row, `T_Co` under `Otilde`: **7456 of 189720 lifts (3.9%) in 5400 s**, and the time is the **transport: 4749.9 s (88.0 %)**, 637 ms per plane, its per-call quarters 221, 578, 766, 983 ms, so the cost grows with the row; the walk's own setup 207.8 s, of which GAP's `FactorCosetAction` on the 189720 cosets 191.2 s and the breadth-first walk itself 8.1 s; `quotient.image_order` 182.0 s (with the ambient `rho` sweep 32.8 s), the ambient `O(L)` plane row 138.5 s, the parabolic family 48.8 s, its completeness decision 18.1 s; lift spelling 1.53 ms and registration 1.4 ms per plane; residual 0.2 s; peak python RSS 2256 MiB, about 0.24 MiB retained per lift. The probe's `primitive_isotropic_subobject` wrap was added after this run, and the row it adds to the table is `plane admission  1 call  0.0 s`. The row this measures is still main's: between `484e4c52` and main `a8b7eb8f` `lattices.py` and `orthogonal_quotients.py` are untouched and `transport_isotropic_object`'s text is untouched (`lattice_morphisms.py` gains 197 lines elsewhere) |
| `issue390-stage-slice-prefix.log` | main `484e4c52` | the same row truncated to 1200 s with that admission wrap in place: **2674 lifts**, transport **718.1 s (59.8 %)** at quarters 94, 220, 384, 376 ms, walk setup 221.8 s (`FactorCosetAction` 205.7 s), ambient row 98.5 s, `image_order` 78.9 s, registration 3.1 s, peak 1533 MiB -- the second independent sample of the same table, and the record that the admission wrap answers **one** call, so the subobject the transport builds is not built through `Lattices.ParentMethods.primitive_isotropic_subobject` and the transport's interior is not split here |
| `issue390-stage-slice-main-blocked.log` | main `484e4c52` | the same probe with `no-shim` on `T_Co`: the row **raises at 215 s**, `IndexError: index out of range` at `g_sets.py:913 _named_stabilizer`, `libgap.Identity(engine_generators[0])` on the empty generating family of the trivial group (`Symmetric group on 1 points` on `{0}`; the shim prints the same identification in the prefix log), reached from `quotient.image_order` -- the defect of `bbb6608` that stops this row before the walk, and the reason the probe carries a shim |
| `issue390-stage-slice-smoke.log` | main `484e4c52` | the instrumentation's own check on `U + U(2) + <-2>`, whose `Otilde` row walks two cosets: **2 planes return** and the slice names every stage it must -- 2 cosets, 2 lifts, 2 transports, 3 registrations; not a measurement of anything |

| `issue390-transport-split.py` | main `a71272add9` | the probe: `transport_isotropic_object`'s subobject branch re-expressed as the same four steps under a clock each (`product`, `image`, `basis`, `admission`), their mean per call in fixed windows of transported planes, and at each window close a snapshot of the live objects by type, of every `_cache__*` table on the lattice and on the instances the steps build, and of the `__classcall__.cache` of the classes those instances construct through. The admission's and the image step's interiors are timed from wrappers on the methods they call, with `CachedMethod`'s instance shortcut dropped, so the cache stays in force and every call is still timed -- which is why the previous probe's single patch answered one call. The reproduced branch is checked against the unmodified one on the first three calls. Modes: `smoke`, `cap=`, `window=`, `detail=image`, `detail=span` |
| `issue390-transport-split.log` | main `a71272add9` | the 2700 s row on `T_Co` under `Otilde`: **4672 of 189720 planes (2.5 %) in 2700 s**, transport 2158.3 s (79.9 %) at 462 ms per plane. The rise is in two of the four steps and in nothing else: `image` 19.65 -> 435.91 ms (x22.2) and the admission 22.83 -> 228.25 ms (x10.0), of which `subobject_on` 8.88 -> 217.41 (x24.5), while `is_primitive` 10.31 -> 6.97 and `refine` 0.39 -> 0.36 stay flat; `product` 0.22 -> 0.23 ms and `basis` 1.22 -> 1.44 ms are flat throughout, and the four steps are the whole call (framing 0.02 ms). Not the collector: 6615 collections for 20.0 s in the 2700 s, at most 2.8 % of any window. Not a `UniqueRepresentation` table: `OwnedJoinCategory_with_category.__classcall__.cache` 1746 -> 1718, flat. The one cache that grows is the admission's own `_cache__primitive_isotropic_subobject`, 267 -> 4689 entries (one per plane), a dict lookup and not a scan. Live objects 2.98 M -> 8.42 M (+1160 per plane: `list`, `tuple`, `dict`, the element class, `MonoDict`), RSS 1425 -> 2158 MiB at 0.165 MiB per plane, peak python VmHWM 2222 MiB; at this run's own mean the row is 24.3 h and rising, so that is a lower bound. (The tree's peak 3616 MiB includes a julia process that is not this probe's: python 2221 MiB.) |
| `issue390-transport-image-detail.log` | main `a71272add9` | the same row, 1000 s, windows of 50 planes, `detail=image`: **2868 planes**; `image` 9.31 -> 239.41 ms and the `subobject_on` call *inside* it 8.86 -> 239.31 ms, i.e. the image step is its own span construction to 0.1 ms, and the admission's `subobject_on` is the same growth one call later (3.41 -> 119.05 ms); `product` x1.04, `basis` x1.18, `is_primitive` x1.08, `refine` x1.19 over the run. The `img all` column is the label the image wrapper would book and it books nothing -- the step's total is already the `image` column |
| `issue390-transport-span-detail.log` | main `a71272add9` | the same row, 700 s, windows of 50 planes, `detail=span`: **2005 planes**; inside `subobject_on` the span-basis computation `_span_basis_elements` is **flat**, 2.45 -> 2.68 ms per call (x1.09), while the sublattice construction `_lattice_subobject_spanning` is 3.93 -> 126.82 ms per call (x32.3) and is called twice per plane; `admission.subobject_on` 3.46 -> 85.09, `image` 9.33 -> 174.01, the call 22.25 -> 269.07. The linear algebra of the span is not the cost; building the sublattice object on it is |
| `issue390-transport-split-smoke.log`, `issue390-transport-split-smoke-span.log` | main `a71272add9` | the probe's own check on `U + U(2) + <-2>`, whose `Otilde` row returns 2 planes: the split sees the transports, the reproduced branch agrees with the unmodified one on the first calls (generator coordinates equal), the admission step equals the method it times to 0.01 ms, the span rows fire twice per plane, and each window closes with its snapshot; not a measurement of anything. The first two logs carry the earlier prefix `in admission` on the interior rows; it is a line prefix, not a number |

| `issue390-transport-split.py` | main `cef9c5d` | the probe of the two earlier findings of this turn, extended: `detail=basis` splits the sublattice construction into `_module_subobject_constructor_data`, `ring._fresh_free_module_on`, the Gram tensor, the inclusion, `_module_with_structure` and `_lattice_object` -> `_form_module_from_bilinear_computation`; `coercion` censuses `_coerce_from_list`, `_convert_from_list`, `_action_list`, `_coerce_from_hash`, `_convert_from_hash` and `_embedding` on the ambient lattice, its free module, the base ring and the last plane, counts every registration call on those three, and counts live `MonoDict` objects; `profile` profiles two windows and prints the callers of the growing function, and counts the set comparison's call sites by file:line of the asking frame. On `T_Co` this tree spends 1144 s in setup before the first plane |
| `issue390-subobject-construction.log` | main `cef9c5d` | the 1800 s `T_Co` row under `Otilde`, 2943 planes, windows of 100: every part of the sublattice construction is flat -- `_module_subobject_constructor_data` 0.92 -> 0.95 ms, `_fresh_free_module_on` 0.18 -> 0.21, the Gram tensor 1.96 -> 1.90, `_lattice_object` 1.17 -> 1.20, the form module 0.51 -> 0.54, `_module_with_structure` 0.45 -> 0.48, the inclusion 1.02-1.16 (11.57 in the cold first window) -- while `_lattice_subobject_spanning` goes 5.56 -> 176.76 ms (x31.8) and its own time, children removed, 3.46 -> 174.62 (x50.5), so the cost is the one statement those five do not cover. The coercion census is flat in all 30 windows (`_coerce_from_list`, `_convert_from_list`, `_coerce_from_hash`, `_convert_from_hash` 0; `_action_list` 2; the last plane 0/0/2/0/0) and **no** coercion, embedding, action or conversion was registered on the ambient lattice, its free module or the base ring, so the coercion candidate is refuted. What grows is the heap: `MonoDict` +91 per plane (82 k -> 269.7 k), `TripleDict` +33, the ring's element class +198 |
| `issue390-subobject-scan.py` | main `cef9c5d` | the probe that answers the question on a small input: `L = U + U + <-2>` (rank 5, signature (2, 3)), `v_k = (1, e^2 - c d, c, d, e)` primitive isotropic, `base_k = L.primitive_isotropic_subobject(v_k)`, `g_k` one of 40 length-three generator words, and the timed call `g_k.transport_isotropic_object(base_k)` -- the library method the row calls, so the same `subobject_on` and `_lattice_subobject_spanning`. A fixed base is not used: this lattice's isotropic line orbit holds only about 120 lines under the isometries its generators reach, so a walk over one base stops making new subobjects within a hundred calls. Per window of 100 calls: mean and median time, the comparison count and cost by class and call site, live objects, the machine's load; at the end the two caches' sizes with the number of distinct hash values among their keys. Setup 1-7 s. `profile` adds two profiled windows and the callers of the growing function |
| `issue390-subobject-scan.log` | main `cef9c5d` | **the answer, on rank 5 in 105 s**: 600 transports, 600 distinct subobjects. Per transport 32.95 -> 180.25 ms (x5.47 over 500 transports), and the growth is a **count** of comparisons, not their cost: `FiniteOrderedSets.ParentMethods.__eq__` (`finite_ordered_sets.py:578`) goes 525.3 -> 5415.4 comparisons per call (x10.31) while each costs a flat 42.7-53.1 us, and every one of them is called from `subobject_on`'s return line, `lattices.py:3976`. The accumulation is the cache of `_lattice_subobject_spanning`, a `@cached_function` (`lattices.py:407`) whose key holds the span basis, a `FiniteOrderedSets` whose `__hash__` is `hash(int(self.cardinality()))` (`finite_ordered_sets.py:615`): 1197 entries, 5 distinct hash values, so a lookup scans its bucket and compares the stored bases with `__eq__` |
| `issue390-subobject-scan-profile.log` | main `cef9c5d` | the same probe with `profile`, 420 transports, windows of 100 at calls 101 and 301: `subobject_on` 21.000 -> 47.615 s of cumulative time in a window, `FiniteOrderedSets.__eq__` 19.235 -> 46.107 s, its calls 145596 -> 338790; the profile's caller records put `__eq__` under `subobject_on (lattices.py:3972)`, which is the frame the `cached_function`'s Cython `__call__` leaves visible. The profiled windows' wall times and per-comparison costs carry cProfile's overhead (135 and 290 ms per transport against 22-114 ms in `issue390-subobject-scan.log`; 131 us per comparison against 43); the counts do not. Not to be read for timing |

## #402 — the chamber at Sterk's fourth cusp

| log | commit cited | result |
| --- | --- | --- |
| `issue402-lift-dependence.py` / `issue402-lift-dependence.log` | `6d8ed19` | at card `029J` row 4.3.8's cusp, for each of the eleven printed walls: the frame lift `class_lift` of its class minus the printed vector is `k v` with `k = 1` for `alpha_2` and `alpha_10`, `0` for `alpha_3..alpha_9`, `-2` for `alpha_11, alpha_12`; `contains_lift` of the reflection in the printed vector is **True for all eleven**, and `admits_root` of the class is **False for `alpha_2` and `alpha_10`** -- the two odd `k`. `g = s_(alpha_2+v) s_(alpha_2)` fixes `v` and acts trivially on `N`, so it lies in `K_v`, and `rho(g)` is **not the identity**, while `kernel_discriminant_image()` built from the basis transvections has order 1. So the criterion's `rho(K_v)` omits elements of `K_v`, and the filter's answer on a class depends on the lift |
| `issue402-cusp4-polyhedron.py` / `issue402-cusp4-polyhedron.log` | `c4300a9` | card `029J` row 4.3.8's polyhedron `P` computed **in `N = v^perp/Zv`**, each printed wall read as its class: `P` has 26 extreme rays and no lines, every ray of square `0, 2, ..., 12`, so `P` lies in the closed positive cone and has finite volume. Each of the sixteen walls of `issue387-cusp4-facets.log` paired with every ray: the seven printed ones and the square `-4` wall `(2,-5,...,0,2)` are **implied**, the other eight are **opposite** (nonpositive on all of `P`); **none crosses**. So no mirror of the walk meets the interior of `P`, and **`issue387-cusp4-mirrors.log`'s conclusion is retracted**: its witnesses pair `-10` and `-14` with `v` (`issue387-cusp4-lifts.log`), so they are not points of `v^perp`, and its cone test read twelve-coordinate lifts of classes, whose pairing with such a point depends on the lift |
| `issue402-kernel-repair.py` / `issue402-kernel-repair.log` | the tree of this push | `kernel_generators()` at card `029J` row 4.3.8's cusp: **20 generators** (the transvections of a basis of `v^perp` and of nine generators of the parameter classes `B / v^perp`), `rho(K_v)` of **order 256**, and `admits_root` **True for all eleven** printed walls' classes |
| `issue402-kernel-tests.log` | the tree of this push | `tests/lattices/test_the_isotropic_reduction_image.sage -k "every_wall_of_the_fourth or two_lifts or one_sift_per_root or agrees_with_the_levi or reduces_to"`: **5 passed in 1054.96 s** -- the red test of `a33dae4` is green, and `rho(K_v)` is still trivial at `Sterk_1` |
| `issue402-locus-classes.py` / `issue402-locus-classes.log` | `b77de81` | the owner of the integral lift locus, unchanged: for the identity marking of the reduction at the same line, class 64 of `integral_parameter_classes()` is in the locus and the lift at its `residue.preimage` is **not integral**, so the locus is not the set of residues of integral lifts there |
| `issue402-cusp4-chamber-at-vertex.py` / `issue402-cusp4-chamber-at-vertex.log` | the tree of this push | the public `cusp_chamber(p_0)` at card `029J` row 4.3.8's cusp, `p_0` the vertex of square 2 of the card's polyhedron (nine printed walls through it): **complete, 11 walls**, the nine through `p_0` printed, two more of squares `-4` and `-2`; 245 filter questions, 116 admitted |
| `issue402-cusp4-chamber-gram.py` / `issue402-cusp4-chamber-gram.log` | the tree of this push | the eleven walls of that chamber and card `029J`'s eleven printed walls, in `N`: **the two Gram matrices are equal entry by entry**, and both polyhedra have 26 rays of squares `0..12`. The returned chamber contains `p_0` on the side where the two closing walls pair `-2` with it, the card's on the side where they pair `+2` |
| `issue402-reduction-image-file.log` | `484e4c5` | the whole `tests/lattices/test_the_isotropic_reduction_image.sage`: **10 passed, 1 failed in 5143.46 s**. `test_every_cusp_chamber_has_the_wall_count_of_its_card_row` **passed**: the public `cusp_chamber()`, with no bound and no point, returns complete chambers with card `029J`'s wall counts at all five cusps, Sterk_4 included. The failure is `test_the_fourth_cusps_layers_are_enumerated_in_the_coordinates_of_its_cell`, which asserted the stalled walk (`is_complete_wall_set() is False`, more than sixteen walls); with the repaired filter the bounded walk completes |
| `issue402-cusp4-walk-test.log` | the tree of this push | that test, rewritten as `test_the_fourth_cusps_walk_stops_within_twenty_decompositions_at_the_card_chamber`: **1 passed in 982.48 s** -- complete, every wall admitted, the card's 4.3.8 wall count |

## #404 — the kernel plane rows driver's row step, restored

`488f06f` deleted `run_row` and `_is_a_primitive_isotropic_plane` from
`tests/coble_kernel_plane_rows.py` when it added the expected-count
machinery, and left `main` calling the deleted `run_row`, so image run
43610158124 stopped 7 s in with `NameError: name 'run_row' is not defined` and
never reached the first row of either kernel plane. Both functions are
restored: the row step is the public call
`subgroup.isotropic_orbit_representatives(2)` under the per-row cap (the
alarm's `RowUndecided` makes a row undecided, never failed), each returned
representative checked for rank two, primitivity and total isotropy, and its
count handed to `check_row_count`.

| log | commit cited | result |
| --- | --- | --- |
| `issue404-row-step-probe.py` | the tree of this push | the probe: `tests/coble_kernel_plane_rows.py` loaded as a module (not run as a script) and its own `run_row` and `check_row_count` called on the gate lattice `U + U(2) + <-2>`, so the restored row step is exercised without running the Coble rows on the VM |
| `issue404-row-step-probe.log` | the tree of this push | on `U + U(2) + <-2>` (rank 5, 1 ambient `O(L)`-class): `Otilde` **2 planes in 36.6 s**, `check_row_count` true against 2 double cosets; `Otilde+` **2 planes in 10.2 s**, true against 2; `Otilde+ >= Otilde`; peak tree 2570 MiB, exit 0 (`PROBE404 OK`) |
| `issue404-gate.log` | the tree of this push | the gate on the file that gates the same contract, `tests/lattices/test_the_stable_plane_rows_equal_their_double_coset_counts.sage`: **3 passed in 61.06 s**, `--no-time-gates`, two calls over the 20 s gate (25.51 s on `6JRS`, 31.16 s on `U + U(2) + <-2>`) |

## #409 — the finite-coset slice's only red is the file's own session standard

`tests/test_finite_cosets.py` holds four tests. Under the flags the issue's
observation used, `--no-time-gates --no-test-lint`, all four pass on `main` at
`9b29712`, alone and in session behind sibling files that drive the same
coset, transport and stabiliser machinery, and they pass at `bbb6608`,
`484e4c5` and `0ee5ad5`; the slice contributes no failing test id to the 238
of 633, and the three paths still collect exactly 633 tests here. Its one red
is the collection the repository's own invocation performs: the file imported
`sage.all` and five `sage_extensions` modules directly, imported the private
`_owned_integers` and called `len()` twice, so with the session-standard lint
on, `pytest` exited 1 with `no tests ran` and nine findings before any of the
four tests ran. The file entered that way at `178bec4` (2026-10-26, added with
the coset machinery) and never ran under `just test` since. `fba2e71` repairs
it: the names come from `from sage_extensions.all import *`, and the two length
assertions are replaced by the statement they were numbering, the coset
section carrying the cosets onto the orbit of the distinguished vector, whose
9 and 4 are derived (72/8 and 8/2, printed with `|G|` and `|Stab|` beside
`|orbit|`) rather than typed.

Two limits of this host are recorded, not worked around. The image's Sage
environment has neither `pytest-timeout` nor `pytest-reportlog`, so `just test`
verbatim dies on its own `addopts` (`unrecognized arguments: --timeout=60
--timeout-method=signal --report-log=...`) and the observation's 60 s cap
cannot be reproduced as failures; per-test durations are recorded instead, and
the slowest of the four is 11.7 s. And the three-path run cannot be bounded
here: `tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage::
test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup` ran
past eleven minutes with nothing to stop it, which the observation's
`--timeout=60` would have turned into a failure; the run was stopped after the
first four tests of `tests/groups`, so the split by file for the other two
paths is not in these logs.

Paste-ready body for the one cause this slice owns (this connection reads and
pushes, it cannot create issues):

```
tests/test_finite_cosets.py runs under no invocation of just test

Under the repository's own invocation the session-standard lint ends the run
red at collection, so the file's four tests have never run:

  $ just test tests/test_finite_cosets.py -o addopts= -p \
      sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint
  no tests ran in 2.26s
  ! _pytest.outcomes.Exit: test lint: 9 findings (run just test-lint for all)
  tests/test_finite_cosets.py:3: TL01 import sage.all
  ... five TL01, one TL02 (_owned_integers), two TL10 (len at :63, :85)
  exit 1

Introduced by 178bec4 ("Carry exact coset transversals and pairing-map graph
construction", 2026-10-26), which added the file outside the session standard;
D. Zack Garza. The eight top-level .py tests share the finding pattern (41
findings over five of them, `python -m sage_extensions.testing.test_lint
tests/test_*.py`), so the repair of the others belongs to whoever owns them.

When this closes a user of the library gets `tests/test_finite_cosets.py` as a
suite that actually runs: the four coset, section and Schreier assertions are
executed by `just test` instead of being skipped by a collection error.

Repaired on main in fba2e71.
```

| log | commit cited | result |
| --- | --- | --- |
| `issue409-just-test-addopts-unavailable.log` | `9b29712` | the repository's `addopts` under this host's image: `unrecognized arguments: --timeout=60 --timeout-method=signal --report-log=tests/.report/run.jsonl`, exit 4, nothing collected — the reason the runs below pass `-o addopts=` with the two gate plugins named explicitly |
| `issue409-slice-collection-count.log` | `9b29712` | `tests/groups tests/objects tests/test_finite_cosets.py` collect **633** tests (302 / 327 / 4), the issue's denominator |
| `issue409-slice-main-run.log` | `9b29712` | `tests/test_finite_cosets.py` under `--no-time-gates --no-test-lint`: **4 passed in 3.81 s**, slowest call 3.07 s |
| `issue409-slice-earlier-commits.log` | `bbb6608`, `484e4c5`, `0ee5ad5` | the same four tests at each commit: **4 passed** in 7.51 s, 7.87 s, 7.91 s — no commit of that day carries a red here |
| `issue409-slice-three-path-run-stopped.log` | `9b29712` | the three-path run, stopped by me after 11 min: four tests done, no failure, blocked in `test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup` |
| `issue409-slice-default-invocation-red.log` | `9b29712` | the red: gates and lint on, `tests/test_finite_cosets.py` alone — **no tests ran**, `Exit: test lint: 9 findings`, exit 1 |
| `issue409-slice-after-fix-default.log` | `fba2e71` | the same invocation on the repaired tree: **4 passed in 9.11 s**, 0 findings |
| `issue409-slice-after-fix-context.log` | `fba2e71` | the repaired file behind seven sibling files (four `tests/groups` coset tests, `test_symmetric_group_s3.sage`, `test_orthogonal_group_of_a2.sage`): **36 passed, 9 failed**, all nine in the two sibling files, none here |
| `issue409-slice-orbit-counts.py` / `.log` | `fba2e71` | the numbers the replaced `len()` calls carried: split four-dimensional form `|orbit| = 9`, `|G| = 72`, `|Stab| = 8`; anisotropic ternary plane `|orbit| = 4`, `|G| = 8`, `|Stab| = 2` |

## Triage of the failing tests of `tests/objects` (#408)

`triage/408-*.md` are the paste-ready issue bodies for the causes the #408 triage found
in its slice (the 26 files of `tests/objects` up to
`test_isomorphisms_of_a_two_element_set.sage`; the rest of the directory is #412). Each
file is one cause: the first line is the issue title, the rest is the body, which names
the failing tests with the error each reports, the defective call, the commit that
introduced the cause and the scope. They are not logs. The run that produced them is
recorded in `results/issue408-triage.md`, whose cause ids these bodies carry.

## #410 — the definite-lattice slice triaged, two causes repaired

The slice is the five files the issue names. At `c8a3cedb` they collect **37** tests
(25 + 2 + 5 + 2 + 3), not the 76 the issue body quotes; the neighbouring `definite`-named files
add 17 and the `indefinite`-named ones 23, so no reading of "the definite-lattice test files"
gives 76 either. **11 of the 37 fail**, in eight causes; each cause's paste-ready issue body is
under `triage/410-cause-*.md`. Two of the eight are repaired on `main` in this push (causes A and
B) and the other six are filed for the orchestrator.

Every command is `python -m pytest -p qc_sage_session -o addopts=` inside the adopted image with
this project's checkout bound at `/repos/sage-extensions` and the port at `/work`, because this
venv has no `pytest-timeout` and no `pytest-reportlog`, so the repository's own `addopts` cannot
be used; `-p sage_extensions.testing.suite_budget --no-time-gates` where the count is the point.
One pytest process per file and per probe, never the suite.

| log | commit cited | result |
| --- | --- | --- |
| `410-baseline-11-ids-at-c8a3cedb.log` | `c8a3cedb` (current `main`) | the 11 red ids, `-v --tb=line`: **11 failed in 9.82 s**, one error line each |
| `410-baseline-slice-driver-at-9b29712.log` | `9b29712` (the `main` the triage started on) | the five-file slice one process per file: **9 failed, 16 passed** in `test_definite`, **2 failed** in the metric archive, and the other three files green (2, 5, 3 passed) |
| `410-repaired-slice-driver.log` | the tree of this push | the same five files after causes A and B: **2 passed** metric archive, 5 passed isometry witnesses, 3 passed root groups, and `test_definite` with 7 red left; its 593 s is contention with the other triage chats on this VM |
| `410-repaired-slice-test_definite.log` | the tree of this push | the residual: the six filed causes plus `test_nikulin_even_unimodular_embedding_existence_controls_embedding_mor`, which passed at 319.62 s in the baseline run of the same command and here died with `sage_julia_bridge.errors.JuliaWorkerError: Julia bridge process exited unexpectedly` — the Julia bridge under two 5 GiB Julia processes on a 15 GiB VM, not a code failure |
| `410-repair-a-and-b-targeted-at-c8a3cedb.log` | the tree of this push | the four cause-A ids, the cause-B id and the #150 division contract at `c8a3cedb`: **6 passed in 2.85 s** |
| `410-flip-e4bd95d-parent.log`, `410-flip-e4bd95d.log` | cause A | `test_square_lattice_minimum_theta_and_packing_radius`: **passed** at `e4bd95d^`, **RecursionError** at `e4bd95d` |
| `410-flip-bbb6608-parent.log`, `410-flip-bbb6608.log`, `410-flip-bbb6608-isotropic-id.log` | cause B | `test_norm_one_vectors_of_x2_minus_2y2_form_one_orbit`: **passed** at `bbb6608^`, **IndexError** at `bbb6608`; the isotropic-lines id went from its own `ArithmeticError` at `bbb6608^` to the same **IndexError** at `bbb6608` |
| `410-flip-6a93efe-parent.log`, `410-flip-6a93efe.log` | cause H | `test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so`: **passed** at `6a93efe^`, **ArithmeticError** at `6a93efe` |
| `410-masked-d26db5d-parent.log`, `410-masked-d26db5d.log` | cause D | the `condition_set` guard's commit `d26db5d7` and its parent: the id **fails at both** with `TypeError: CategoricalIsomorphism.__init__() missing 1 required positional argument: 'inverse_computation'`, so the guard has no observable pass-to-fail flip |
| `410-sample-02d9657.log`, `410-sample-441519c.log` | causes C, E, F, G | the four "never implemented" causes show the same error at both commits: the `Emb` cardinality assertion, `is_cyclic`, the `cyclic_subgroup` refusal (masked at `02d9657` by `_form_module_morphism`) and the bare tuple |
| `410-baseline-11-ids-at-5f5fc25.log` | `5f5fc25` (the `main` this push is rebased onto) | the same 11 ids, `-v --tb=line`: **11 failed in 11.17 s** — the #408 push that moved `main` under this triage changed no definite-lattice test |
| `410-repair-a-and-b-targeted-on-the-push-tree.log` | `3cb0d5e` (the tree of this push, rebased) | the four cause-A ids, the cause-B id and test_rational_scalars_on_a_base_changed_lattice.sage on the rebased tree: **6 passed in 3.88 s** |
| `issue402-cusp4-chamber-at-vertex.py` / `issue402-cusp4-chamber-at-vertex.log` | the tree of this push | the public `cusp_chamber(p_0)` at card `029J` row 4.3.8's cusp, `p_0` the vertex of square 2 of the card's polyhedron (nine printed walls through it): **complete, 11 walls**, the nine through `p_0` printed, two more of squares `-4` and `-2`; 245 filter questions, 116 admitted |
| `issue402-cusp4-chamber-gram.py` / `issue402-cusp4-chamber-gram.log` | the tree of this push | the eleven walls of that chamber and card `029J`'s eleven printed walls, in `N`: **the two Gram matrices are equal entry by entry**, and both polyhedra have 26 rays of squares `0..12`. The returned chamber contains `p_0` on the side where the two closing walls pair `-2` with it, the card's on the side where they pair `+2` |

## #407 — the triage of `tests/groups`, and three repairs

The triage of the slice `tests/groups` up to `test_group_adjunctions.sage` on `main` at
`9b29712`: 39 files, 156 tests, 62 of them red, each in exactly one of the 17 causes whose
paste-ready issue bodies are `triage/407-*.md`; `triage/407-triage-index.md` is the table.
Two of the 62 are #399's; #384 owns none of them.

Every log is the redirected output of the command that produced it, one file at a time
with the repository's own invocation and its addopts blanked for the two plugins this venv
lacks (`pytest-timeout`, `pytest-reportlog`):

```
just test -o addopts= -p sage_extensions.testing.suite_budget \
    -p sage_extensions.testing.test_lint --no-time-gates --no-test-lint <file>
```

| log | commit cited | result |
| --- | --- | --- |
| `issue407-sweep-tests-groups.log` | `9b29712` | the 77-file sweep of the whole directory: exit status, file, wall time for each |
| `issue407-failing-tests-slice.log` | `9b29712` | the 60 failing tests of the 38 finished files with the last error line of each, derived from that run's per-file junit xml |
| `issue407-legacy-14b9cc1.log` | `14b9cc1` | the same files at the commit that brought them: 83 of 83 tests red, which is why no bisect on `main` has a green boundary |
| `issue407-stabilizer-file.log` | `9b29712` | the file that does not finish: 1 of 3 passed, the second `Killed` at 2400 s, peak tree 1304 MiB, exit 137 |
| `issue407-probe-stabilizer-steps.py` / `.log` | `fa7553e`'s tree | the file's own steps timed: `O()` 1.9 s, the isotropic subobject 2.2 s, the stabilizer 2.2 s, then `group_generators()` with no return |
| `issue407-probe-stabilizer-section.py` / `.log` | `fa7553e`'s tree | `_GapWordSection.__init__`, `.permutation_group` and `.gap_group` instrumented: the section is never constructed before the hang, so the hang is not #384's `permutation_group` cost |
| `issue407-lint-names-before.log` | `14b9cc1` | `sage_extensions.testing.test_lint` on three group tests: `TL13 Subgroups`, `TL13 Torsors`, `TL13 SymmetricGroups` (17), `TL13 GeneralLinearGroups` (17), `TL13 FreeGroupQuotients` (14), `TL13 OwnedGroups` (45), `TL13 FiniteGSets` (3) |
| `issue407-lint-names-after.log` | this push's tree | the same three files: 0 `TL13` findings, their other findings unchanged |
| `issue407-repair-namespace.log` | `eb203aa` | 10 files re-run on that commit's tree: 8 tests green, none new red |
| `issue407-repair-closure.log` | `4706e99` | 11 files re-run: `AlgebraicClosureFiniteField() missing` gone from all of them, no test flipping |
| `issue407-repair-engine-identity.log` | `fa7553e` | 12 files re-run: 3 tests green, none new red, two green-on-main guards held |
| `issue407-probe-closure.py` / `.log` | `525dd1b`'s tree | `AlgebraicClosureFiniteField(Zmod(3), "z3")` raises `NotImplementedError: ... only implemented for prime fields`; the same call on `GF(3)` answers -- the reason the closure's base is `GF(p)` |
| `issue407-repair6.log` | `c17910a` | 12 files re-run on the pushed tree: the same 3 tests green, nothing new red, and no `AlgebraicClosureFiniteField() missing` in the 11 closure files |

`issue407-repair1.log` and `issue407-repair2.log` were superseded by
`issue407-repair6.log` and the two replacement commits and are not kept.
## #406: the suite stopped before its first test (2026-11-14, `main` `9b297125`)

The repository's own `addopts` in force (`suite_budget`, `test_lint`,
`--timeout=60 --timeout-method=signal`, junit, report log), with
`pytest-timeout` and `pytest-reportlog` supplied at `.scratch/wt406/.pydeps`
because this venv carries `pytest` only.  Every run is
`/sage/.venv/bin/python -m pytest -p qc_sage_session` inside the adopted image
with the tree bound at `/repos/sage-extensions`, `PYTHONPATH` carrying
`/ci/tool-artifacts/pytest_plugins`, the port's `src`, the tree's `src` and the
`.pydeps` path.

| log | tree | command shape | result |
| --- | --- | --- | --- |
| `issue406-suite-collection-stop.log` | `9b297125` | `--collect-only` | 3930 collected, **0 run**; `! _pytest.outcomes.Exit: collection took 232.90 s; the measured ceiling is 6 s !`; exit 1; peak RSS 3763 MiB |
| `issue406-suite-lint-stop.log` | `9b297125` | `--collect-only -q --no-time-gates` | 3930 collected, **0 run**; `! _pytest.outcomes.Exit: test lint: 1514 findings (run just test-lint for all) !`; exit 1; collection 471.88 s |
| `issue406-bisect-good-fca190e.log` | `fca190e` (`14b9cc16^`) | `--collect-only` | collection completed with no ceiling message: the good side of the bisect |
| `issue406-red-tests-on-main.log` | `9b297125` | `tests/engineering/test_the_suite_plugins_report_what_they_measured.py -q` | **2 failed in 18.03 s**, exit 1 |
| `issue406-green-tests-on-repair.log` | the #406 repair | same | **2 passed in 22.44 s**, exit 0; calls 11.63 s and 10.72 s, `setup` 0.00 s |
| `issue406-repair-full-run.log` | the #406 repair | `-q -k plugins_report_what_they_measured` | the whole tree collected, the collection ceiling reported, the two selected tests ran |

The bad side of the bisect is measured at the tip in the first row only:
collecting `14b9cc16`'s 1437-file tree held 6.4 GiB after nine minutes and the
run was stopped to keep the shared VM's memory.  That measurement is unrun, not
passing; `14b9cc16` is the commit that introduced the three `pytest.exit` calls
(`git blame`), and it has no earlier history for
`src/sage_extensions/testing/suite_budget.py`.

Follow-up in the same session, after the two repairs:

| log | tree | command shape | result |
| --- | --- | --- | --- |
| `issue406-run-before-issue398-repair.log` | `9b297125` plus this slice's plugin repair, before #398's repair (which #410 landed as `e9b6c2c`) | `-q -k plugins_report_what_they_measured` | the gate is reported (`collection took 625.38 s; the measured ceiling is 6 s`) and the run then ends at `Interrupted: 1 error during collection` — #398's RecursionError, 0 tests run |
| `issue406-final-full-run.log` | `main` with this slice's repairs, #410's included | same | the gate is reported (`collection took 224.19 s; the measured ceiling is 6 s`), the two selected tests **run and pass**: `2 passed, 3939 deselected in 241.97 s`, exit 1 on the gate report, peak RSS 3945 MiB |
| `issue398-red-rational-exact-reals.log` | `9b297125` | `tests/rings/test_rational_exact_reals.sage` | **1 failed in 5.32 s** (`RecursionError`) |
| `issue398-green-three-files.log` | `main` with this slice's one-formula division and its test | `tests/rings/test_exact_real_division.sage`, `test_rational_exact_reals.sage`, `tests/functions/test_young_convolution.sage` and `tests/lattices/test_rational_scalars_on_a_base_changed_lattice.sage` (#150's contract) | **3 failed, 8 passed in 6.24 s**: both #150's contract and the new file pass, the rational exact reals pass, and the convolution file collects and runs, reporting three defects of its own |
| `issue398-regression-base.log` | `9b297125` | 8 files over rings, lattices and modules | **8 failed, 22 passed in 5.57 s** |
| `issue398-regression-fixed.log` | this slice's one-formula division | same | **7 failed, 23 passed in 4.51 s**; the one difference is `test_a_product_of_distinct_square_roots_that_is_rational_converts_to_qq`, the other seven FAILED ids identical |
| `issue398-division-before.log` | `9b297125` | division probe with the session imported | `RR(1)/RR(2)`, `RR(1)/(sqrt2-1)` and `~RR(2)` are `RecursionError`; `ZZ(1)/ZZ(2)` is `1/2` |
| `issue398-division-after.log` | this slice's one-formula division | the division probe of the same shape as the before-row | `RR(1)/RR(2)` = `1/2`, `RR(1)/(sqrt2-1)` and `~x` = `1/(sqrt(2) - 1)`; `ZZ(1)/ZZ(2)` = `1/2`, `~ZZ(2)` and `e/2` still refuse |

| `issue406-plugins-after-rewrite.log` | the plugin repairs, with the finding grouping rewritten as `itertools.groupby` | `tests/engineering/test_the_suite_plugins_report_what_they_measured.py -q` under the repository addopts | **2 passed in 13.30 s**, exit 0 |

The `tests/groups` side of #408's namespace cause and of its closure cause are recorded in
this triage's index, not filed twice: three cause bodies that this triage first wrote
(`407-session-namespace-*`, `407-owned-algebraic-closure-*`,
`407-cardinality-of-a-finitely-presented-group`) were folded into #408's filed causes
`408-the-session-namespace-does-not-publish-the-constructors-the-suite`,
`408-the-algebraic-closure-of-a-finite-field-is-raised-with-the-wrong` and
`408-cardinality-refuses-for-a-group-whose-finiteness-is-a-predicate`, and their digests are
removed from `SHA256SUMS`.  `issue407-repair7-merged-tree.log` is the run on the merged tree
that is pushed: the identity repair's three greens hold there, nothing new is red, and the
closure's `TypeError` is absent from all eleven files.
## #409, reopened — the counts the length assertions carried are stated again

`fba2e71` replaced the two `len(...)` assertions with the section's images
equalling the orbit of the distinguished vector, and the review of it reads
correctly: nothing on the page pinned the orbit's order, so an action returning
a smaller orbit would satisfy that equality with two cosets sharing an image,
and the nine (four) distinct vectors the length carried would be gone. Each
test now asserts the orbit-stabilizer count as a stated cardinality of the
orbit against the coset space, with the values derived in the test rather than
typed: `|G| = 72` beside `|Stab| = 8` gives `[G : Stab(v)] = 72/8 = 9` for the
split four-dimensional form, and `|G| = 8` beside `|Stab| = 2` gives `8/2 = 4`
for the anisotropic ternary plane. Together with the image-set equality, "one
coset per vector" now means nine and four distinct vectors.

The gate is measured in `b6b63d0`'s tree with this commit's change to
`tests/test_finite_cosets.py` applied: the pushed tree's source is the same,
its parent `5d1b66f` adding only that slice's evidence, and the four tests are
the file's whole selection. So the plug-ins it measures are the ones `fd7260d`
and the #406 review left behind. An earlier attempt
of the same gate on the pre-rebase tree also had four tests pass but exited 1 on
`session star import took 3.11 s; the measured ceiling is 3 s`, the
shared-preamble ceiling that `suite_budget.pytest_sessionfinish` turns into
`TESTS_FAILED` for any workload over it, under the other triage runs on the
VM; no test of this file causes it.

| log | commit cited | result |
| --- | --- | --- |
| `issue409-slice-orbit-count-gate.log` | `b6b63d0`'s tree with this commit's change to `tests/test_finite_cosets.py` | gates and lint on, `tests/test_finite_cosets.py`: **4 passed in 22.18 s**, slowest call 13.02 s under the 20 s ceiling, star import under its 3 s ceiling, exit 0 |

`issue407-repair8-second-merge.log` is the same check on the tree that is pushed after the
second move of `main` (to `eb07c43`, #409): `test_galois_extension_coset_archive.sage` green,
the normalizer and quotient files at one and two reds, `test_absolute_galois.sage` at five --
the state the identity repair leaves behind, unchanged by the merge.

# The tests/objects triage slices, 2026-11-14 (#408, #412)

The second half of `tests/objects` (#412) is recorded under `triage/`: the slice run on
`c8a3ced`, every failing test of it again at the suite's import commit `14b9cc1`, the
bisect of each cause whose failure is not that import failure, the slice re-run on the
rebased main with the workstream's one repair, and that repair's red test, its neighbours
and the neighbour run without it. The 37 paste-ready cause bodies are beside them, one per
defect, each stating its failing tests with the error each reports.

| log | commit cited | result |
| --- | --- | --- |
| `triage/412-run-c8a3ced/` (25 files) | `c8a3ced` | the slice, one file per process: **75 failed, 99 passed** in 24 of the 25 files |
| `triage/412-base-14b9cc1.txt` | `14b9cc1` | each failing test again at the import: 73 of the 75 fail there, 2 passed |
| `triage/412-bisect.txt` | `14b9cc1..c8a3ced` | one bisect per cause whose signature is absent at the import |
| `triage/412-run-415c2b4/` (25 files) | `415c2b4` | the slice re-run on the rebased main with the repair: **69 failed, 105 passed** |
| `triage/412-c11-red-at-415c2b4.log` | `415c2b4` | the repair's red test: **1 failed, 9 passed** (the one red is C10) |
| `triage/412-c11-neighbours-at-415c2b4.log` | `415c2b4` | `tests/sets` neighbours: **4 failed, 15 passed** |
| `triage/412-c11-neighbours-clean.log` | `7817e87` | the same without the repair: **4 failed, 15 passed**, the same four ids |
| `triage/412-c33-closed-7817e87.log` | `7817e87` | C33's five tests: **6 passed** (green on main via `d38845a`) |
| `triage/412-c37-clean-7817e87.log` | `7817e87` | C37's two tests on a clean main: **2 failed**, the base-ring refusal |

`triage/412-index.md` is the record #412 is accepted against: the cause table, the state of
each repair, the acceptance count (75 failing tests, 75 assigned, none twice) and what the
triage does not do.

### #409, third review — every expected value in the file is counted from its construction

`eb07c43` met the orbit-order finding but left the expected values themselves
(72, 9, 8, and 8, 2, 4) typed, which `AGENTS.md:1405` does not allow: each is
cited from a source or proved, independently of the implementation. Each is now
counted in the test's own docstring from the two constructions the test builds.
The split four-dimensional form: determinant $-4$ per copy gives four vectors a
copy and $4 \cdot 4 = 16$ in all; $q = x_1x_2 + x_3x_4$ vanishes on
$3 \cdot 3 + 1 \cdot 1 = 10$ vectors, leaving nine nonzero singular; the images
of a hyperbolic basis number $9 \cdot 4 \cdot 2 \cdot 1 = 72$ (four because
$v \mapsto v + u$ pairs the eight $v$ with $B(u,v) = 1$, exchanging $q = 0$ with
$q = 1$; two because the orthogonal complement of a hyperbolic pair is
hyperbolic, both Arf invariants being $0$; one because the fourth is then
forced); and orbit-stabilizer gives $72/9 = 8$. The anisotropic ternary plane:
determinant $9$ gives the nine vectors of $(Z/3)^2$; $q$ takes $1/3$ on the four
vectors $\pm e_1, \pm e_2$ and $2/3$ on the other four, so an isometry carries
those four among themselves ($4$ choices), and the image of $e_2$ must be
orthogonal to that image, which $B(x,y) = (x_1y_1+x_2y_2)/3$ leaves to the
other pair ($2$), so $|G| = 8$, the orbit is the four unit vectors, and the
stabilizer is the sign change of the second coordinate, of order $2$, with
$8/2 = 4$ cosets. Both tests also assert the form's own cardinality ($16$ and
$9$), so the first clause of each count is a checked statement rather than
prose. The ternary form is bilinear, which is why that proof uses $B$ directly
and not $q(x+y) - q(x) - q(y)$, the doubled pairing there.

| log | commit cited | result |
| --- | --- | --- |
| `issue409-slice-derived-values-gate.log` | `4a94605`'s tree with this commit's change to `tests/test_finite_cosets.py` | gates and lint on: **4 passed in 8.81 s**, slowest call 7.22 s under the 20 s ceiling, exit 0 |

### #410 — the two repairs replaced by their principled forms

`e9b6c2c` (division) and `6e85b07` (the GAP stabilizer) did not meet the repository's standard on
re-reading them: the first dispatched on `self.parent() is ring`, the second guarded the empty
generating family. Both are replaced, in `4b958ef`'s lineage and `852a901` as pushed: one formula
at the module owner, with the reciprocal stated at the two fields' owner, and one GAP path that is
given the group's own identity.

The two spellings of the reciprocal differ exactly where a scalar is not a unit, which is why the
replacement is not cosmetic. Measured, same probe, clean base and the tree of the push:

| row | clean `8755b95` (`** -1`) | the tree of the push (`inverse_of_unit`) |
| --- | --- | --- |
| `ZZ(3) ** -1` / `ZZ(3).inverse_of_unit()` | `(1)/(3)` | `ZeroDivisionError: 3 is not a unit` |
| a ZZ-module vector `/ ZZ(2)` | `TypeError: no conversion of this rational to integer` | `ZeroDivisionError: 2 is not a unit` |
| `QQ[x].gen() ** -1` / `.inverse_of_unit()` | `1/x`, the fraction field | `ArithmeticError: x is not a unit in ...` |
| `RR(1)/RR(2)`, `~RR(2)` | `1/2`, `1/2` | `1/2`, `1/2` |

| log | commit cited | result |
| --- | --- | --- |
| `410-probe-units.log`, `410-probe-units-on-clean-8755b95.log` | the tree of this push / clean `8755b95` | the unit-inverse and `** -1` columns above, on QQ, ZZ, QQ[x], Zmod(6), RR and CC |
| `410-probe-zz.log`, `410-probe-zz-on-clean-8755b95.log` | the tree of this push / clean `8755b95` | the ZZ-module division: `ZeroDivisionError: 2 is not a unit` here, `TypeError` there |
| `410-probe-design2.log` | the tree of this push | `RR(1)/RR(2) = 1/2`, `RR(3)/RR(2) = 3/2`, `RR(3)/ZZ(3) = 1`, `~RR(2) = 1/2`, `RR(2) * ~RR(2) = 1`, `~RR(0)` and `RR(1)/RR(0)` refused, `CC(1)/CC(2) = 1/2`, a QQ-module vector `/ 2 = (1)/(2)*e_0` and `/ ZZ(3) = (1)/(3)*e_0`, `packing_radius() = 1/2`, `center_density() = 1/4` |
| `410-replacement-repairs-gate-at-1e0546d.log` | the tree of this push (`852a901`) | the four cause-A ids, the cause-B id and the #150 contract on the rebased tree: **6 passed in 5.61 s** |
| `410-replacement-repairs-gate-at-8755b95.log` | `4b958ef` before the rebase | the same six ids: **6 passed in 10.79 s** |
| `410-promoted-repairs-b-alone-at-8755b95.log` | repair B alone, on `8755b95` | the same six ids with only the GAP stabilizer changed: **6 passed in 6.23 s** |
| `410-regression-set-comparison.log` | the tree of this push against clean `8755b95` | fourteen files, one pytest process per file per tree, FAILED-id sets compared: every row has an empty only-on-this-tree set, and the counts agree row by row (`tests/sets` 33 failed / 123 passed on both; `test_exact_real_division` 2 passed; `test_rational_exact_reals` 1 passed; `test_young_convolution` 3 failed / 4 passed; `test_lebesgue_spaces_on_the_line` 9 failed / 5 passed; `test_fraction_field_base_change_archive` 2 failed; `test_finite_cokernel_constructor` 1 failed; `test_predicate_kernel_and_stabilizer_subgroups_of_s4` 1 failed / 4 passed; `test_structured_subgroups` 1 passed; `test_group_law` 1 failed / 3 passed; `test_integral_stabilizers` 4 passed; `test_vector_family_stabilizers` 10 passed; `test_rational_scalars_on_a_base_changed_lattice` 1 passed; `test_definite_metric_invariants_archive` 2 passed). `test_a_stabilizers_generators_generate_a_subgroup` reached the 600 s cap on **both** trees (`exit=124`), so it is not claimed either way |

## #411 — the second half of `tests/groups`

The slice is the 38 files #411 lists (every `tests/groups` file from
`test_group_automorphisms_archive.sage` on, plus `test_g_sets_torsor_archive.sage`):
148 tests, run one file per pytest process in the published image with the
repository's own `just test` and its `addopts` blanked, as in the commands above.
Triage record: `results/issue411-triage.md`. The 22 open causes are staged as
paste-ready issue bodies in `.tmp/qc-evidence/triage/411-*.md`.

| log | commit cited | result |
| --- | --- | --- |
| `issue411-slice-red.log` | `36e5eac` | the sweep: 38 files, **42 failed / 106 passed**, 19 files with failures; each section is one file's run with its own pytest summary |
| `issue411-slice-final.log` | `d0cfd20`, `dcfe72c` (on `8971654`) | the same 38 files on the repaired tree: **41 failed / 107 passed**, the same 41 ids that fail on `36e5eac` with the two repairs; the one green is the degree test of C02 |
| `issue411-probes.log` | `d0cfd20`, `dcfe72c` | the three decisions the two repairs rest on, printed from the image: which values `_integral_rank` admits (`QQ(2)` yes, `2.5` no, a string no, an engine `ZZ(2)` no), `GL/SL/Sp/GU` of `GF(3)` at each, and `Z(QQ[S_3])`/`Z(ZZ[S_3])` of rank 3 through `Modules.linear_combination` |
| `issue411-candidates.log` | `c8a3ced` (two dropped attempts) | the two candidate repairs measured and NOT landed: C05's engine crossing, which moves the five conjugation tests to `'...ArrowType' object has no attribute 'gap'` and leaves M12's file unfinished at 360 s where it failed in 0.87 s; and C20's ring-first `matrix`, whose result `Groups.SL(2, ZZ)` refuses as a Sage object |

Two limits of this host, recorded rather than hidden: the image's venv has no
`pytest-timeout` and no `pytest-reportlog`, so the repository's `addopts` are blanked
and the two gate plugins named by hand (`--no-time-gates --no-test-lint` for the
sweeps), and every run is a single file in its own process because other chats use the
same VM.
### #410 — the ring's division placed at the ring, the module formula left to modules

The placement of `4b958ef`/`852a901` still sent a ring element's `/` through `Modules.ElementMethods`,
the module's scalar action; that is the ring quotient only for a commutative ring. The two owned
fields now state their division beside their `_div_`, and the module formula is left to modules
whose elements are not ring elements.

| row | before | the tree of this push |
| --- | --- | --- |
| `RR`'s `__truediv__` resolves from | `Modules.ElementMethods` (index 13 of the element class) | `sage_extensions.rings.real.ExactRealNumber` (index 0) |
| `CC`'s `__truediv__` resolves from | `Modules.ElementMethods` (index 12) | `sage_extensions.rings.complex.ExactComplexNumber` (index 0) |
| an engine-backed owned ring's | `_OwnedRingElement.__truediv__`, index 2, unchanged | the same |
| `RR(3)/2`, `RR(3)/ZZ(3)`, `CC(3)/2` | by the module formula | `3/2`, `1`, `3/2` |
| a QQ-module vector `/ 2`, `/ ZZ(3)`, `/ (1/2)` | the module formula | `(1)/(2)*e_0`, `(1)/(3)*e_0`, `2*e_0` |
| a ZZ-module vector `/ ZZ(2)` | refused | `ZeroDivisionError: 2 is not a unit` |

| log | commit cited | result |
| --- | --- | --- |
| `410-ringdiv.log` | the tree of this push | the two resolution rows above and every statement in the table, including `RR(2) * ~RR(2) = 1`, `~RR(0)`, `CC(3)/2`, and `packing_radius() = 1/2` with `center_density() = 1/4` |
| `410-ring-division-gate.log` | the tree of this push | the four cause-A ids, the cause-B id and #150's contract: **6 passed in 2.43 s** |
| `410-ring-division-regression.log` | the tree of this push against clean `8755b95` | thirteen files, one pytest process per file per tree, FAILED ids not counts: an empty only-on-this-tree set and an empty fixed set row by row; `tests/rings` **77 failed, 251 passed on both**; `test_a_stabilizers_generators_generate_a_subgroup` reached its cap on both trees and is not claimed |

### #410 — the slice closed out on the main it lands on

The five files hold 37 tests; six were red at the base and are red on `51310d6`, each with a named
owner in `triage/410-triage-index.md`. Causes A (division, four ids) and B (the GAP stabilizer, one
id) are repaired on main; the division's further work is #500.

| log | commit cited | result |
| --- | --- | --- |
| `410-final-slice-driver.log` | `51310d6` | the five files, one pytest process per file: `test_definite.sage` **6 failed, 19 passed in 302.22 s**, the metric archive **2 passed**, genus mass 2 passed, isometry witnesses 5 passed, root groups 3 passed |
| `410-final-slice-test_definite.log` | `51310d6` | the six red ids, which are C, D, E, F, G and H and nothing else: the `Emb` cardinality, the predicate subset, `is_cyclic`, the infinite-order isometry, the bare tuple and the index-2 character image |

## #468 — the session publishes the area packages' declarations, one authority per name

Two triage repairs had contradicted each other on `main`: `b3747a0` reverted the
six names `eb203aa` added to `sage_extensions/all.py` because that file restated
the areas' declarations, and `c099996` added eighteen more to the same
hand-written list 61 seconds later. The file is now derived: `all.py` names the
22 packages that declare an `__all__` and binds each one's whole declaration, so
no member name of an area is written by hand anywhere in it (`_AREA_PACKAGES`
is the list of *packages*, not of names). 310 hand-written lines became 37, and
the session publishes 599 names over those areas, 524 of them distinct.

The six names of #407's namespace cause, and the eighteen of #408's, are now
session names because their owners declare them —
`sage_extensions/groups/__init__.py` has declared `Subgroups`,
`SymmetricGroups`, `GeneralLinearGroups`, `FreeGroupQuotients`, `Torsors` and
`CoxeterGroups` all along, and `all.py` imported that area nowhere. Each of the
23 names of the two causes resolves to the preamble's object: the probe prints
`CoxeterGroups` as the preamble's constructor and Sage's namesake shadowed, and
the other 22 with no Sage namesake at all. `GeneratedSubgroups` and
`AdditiveMonoids` remain `TL13` findings because no area declares them — an
owner gap, not a namespace one, and the same defect `#411`'s `C01` files.

Measured on the tree of this push against a clean worktree at the same base
commit, one pytest process per file, `-o addopts= -p
sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint
--no-time-gates --no-test-lint`: 16 files of the two namespace causes, 15 test
ids red before and green after, 0 ids green before and red after. The tree-wide
`test_lint` reports `TL13` 86 findings over 86 names before and 10 over 10 after
(1475 findings in all before, 1424 after), which is the signal #408's `C36`
names. `import sage_extensions.all` is 2.34 s against 3.24 s before, under the
suite's 3.0 s ceiling for that workload.

Five names stay hand-written because their own area does not declare them:
`MatrixAlgebras` (algebras), `LieGroups` and `TopologicalGroups` (groups),
`MatrixSpaces` and `MatrixEndomorphismSpaces` (modules). They are the areas'
surfaces to close, and the session publishes them in the meantime.

| log | commit cited | result |
| --- | --- | --- |
| `issue468-allpy-rewrite.py` | — | the rewrite, re-runnable: reads each area's `__all__`, drops every hand-written binding of a declared name, and inserts `_AREA_PACKAGES` and the publication loop |
| `issue468-session-names.py` / `.log` | the tree of this push | the 23 names of the two causes, their owner, and whether Sage has a namesake: `CoxeterGroups` `SHADOWS-SAGE`, the other 22 `no-sage-namesake`; 599 area names published, no loop variable leaked |
| `issue468-baseline-outcomes.log` / `issue468-after-outcomes.log` | base `51310d6` / the tree of this push | the 16 files' pytest summaries side by side, e.g. `test_free_and_catalogued_groups.sage` 18 failed / 10 passed before, 10 failed / 18 passed after |
| `issue468-flipped.txt` | the tree of this push | the 15 test ids that went red to green |
| `issue468-runs/*.log` | the tree of this push | the 16 whole runs, one per file |
| `issue468-lint-tl13-before.log` / `-after.log` | base `51310d6` / the tree of this push | every `TL13` line of the tree-wide `test_lint`, with the run's totals |
| `issue468-star-import.log` | both trees | `import sage_extensions.all`: 3.24 s → 2.34 s |

## #471 — the kernel-plane-rows driver reads the plane's Gram tensor

`tests/coble_kernel_plane_rows.py` decided a returned plane's total isotropy by
a double loop of `lattice.b(...)` over the plane's retained generators --
`OWN-24`'s own violation example and the shape `STY-102` names -- and returned
`(None, False)` both for a representative that breaks that contract and for a
row that did not return inside its per-call cap, so a red CI job could not be
read. The check is now the plane's induced Gram tensor against the zero tensor
of the plane's own framing, and the two outcomes are separate reports and
separate exit statuses (`decided` / `undecided` / `contract violation`, 0 / 1 /
2 / 3).

| log | commit cited | result |
| --- | --- | --- |
| `issue471-row-step-probe.py` / `.log` | the tree of this push | the induced Gram tensor of a plane the row returns is the zero `(2,2)` tensor and equals `lattice.gram_tensor().pullback(plane.inclusion())`; a rank-two primitive *non-isotropic* subobject's is `[[0,1],[1,0]]` and the check reports "its induced Gram tensor is not zero", a rank-one subobject "its rank is 1, not two"; the old pairing loop says `True` / `False` on the same two, so the reading changed and the verdicts did not; warm cost per representative 0.262 ms against the old loop's 1.055 ms (x189720 planes = 49.8 s against 200.1 s) |
| same | the tree of this push | the driver's own `main`, its `_coble_lattice` pointed at the gate lattice `U + U(2) + <-2>`: `[Otilde] 2 planes in 15.3 s` against 2 double cosets over 1 ambient class, `[Otilde+] 2 planes in 11.7 s` against 2, exit status 0, peak tree RSS 571 MiB |
| same | the tree of this push | the two reports apart, and all four exit statuses, each driven by a stub row: a row holding the non-isotropic subobject → `contract violation` / status 2; a row that does not return inside a 3 s cap → `undecided` / status 1; a row of three planes against two double cosets → status 3. The Coble rows themselves were not run on this VM |

Follow-up on #471 (review of `020eccfa24`): the three row statuses are one
`RowStatus` enum instead of three module-level strings compared with `==`
(`CON-08`: a chosen outcome is not a mode string; `STY-159`: a flag that
changes the return shape is named). `run_row` and `main` use its members, with
identity tests. `issue471-row-step-probe.py` and `.log` at the paths above are
the re-run on that tree, not the run cited in `020eccfa24`'s body: the values
move by noise only -- induced Gram tensor 0.231 ms against the old loop's
1.228 ms per representative (×189720 = 43.9 s against 232.9 s), `[Otilde] 2
planes in 15.4 s` and `[Otilde+] 2 planes in 11.9 s` against 2 double cosets
each, exit status 0, peak tree RSS 569 MiB, and the enum's three members with
statuses 2 / 1 / 3 driven by the stub rows.

## #468 review repair — one static star import per area package

The review of `de94fac512` accepted the one-authority result — no area-declared
name is hand-imported in `all.py`, the 75 names two areas declare are the same
objects, and `CoxeterGroups` and the #407 group categories resolve to the
preamble's constructors — and refused the mechanism: `for _area_name in
_area_package.__all__: globals()[_area_name] = getattr(_area_package,
_area_name)` is a `globals()` mutation with a dynamic lookup (STY-120; AGENTS
§3/§4 and "Dynamic peeking").  `all.py` now names each area once, in a static
`from sage_extensions.<area> import *  # noqa: F403`, in the order the loop
walked, and the `_AREA_PACKAGES` tuple is deleted, so the list of areas exists
only where it is used.  `import *` is defined as binding the package's `__all__`,
which is what the loop did by hand, so the mechanism is the declaration and
nothing else.

Measured on base `37b67b7` (that is `de94fac` plus #471, which changes only
`tests/coble_kernel_plane_rows.py` and evidence files, nothing under `src/`)
against the same commit with this repair's `all.py`.

**Same bindings.**  Dumping every non-dunder name of `sage_extensions.all` in
both trees, the two dumps differ in one line over 690 names: the private
`_AREA_PACKAGES` tuple itself.  The 689 others agree in name, in the type of the
bound object, and in the `__module__`/`__qualname__` that object declares itself
under.  An audit of the declarations finds 599 over 524 distinct names in the 22
areas, 75 declared by two areas, 0 names unbound in the session, no name bound to
an object no declarer exports beyond `Integer` and `RealNumber` (which the
session rebinds to its own runtime objects below the imports, in both trees), and
no loop temporary left in the module.

**The six names of #407's cause** resolve to the preamble's constructors and
construct: `CoxeterGroups()([[1, 3], [3, 1]]).order()` is 6 and the group is in
`FreeGroupQuotients()` and `OwnedGroups().Finite()`; `SymmetricGroups()(Sets.Δ[2])`
has order 6; `Groups.S(3).predicate_subgroup(sgn = 1)` is in
`Subgroups(Groups.S(3))` with order 3; `GeneralLinearGroups()(GF(2), 2).order()`
is 6; `Torsors(C_3)(regular C_3-set)` has cardinality 3.  `CoxeterGroups` is the
only one of the six with a Sage namesake, and the session's binding shadows it.

**The 16 files of #407's and #408's namespace causes**, one pytest process per
file, `-o addopts= -p sage_extensions.testing.suite_budget -p
sage_extensions.testing.test_lint --no-time-gates --no-test-lint`, on the base
and on this tree: 141 test ids each, 43 red each, the same id set, the same
failure kind for every shared red id, and 0 ids green on the base and red here.
The 15 ids the causes' record lists as red-to-green at `de94fac` are green in
both.

**Nothing else moves**: the tree-wide `test_lint` reports 932 files and 1424
findings with identical lines in both trees, so `TL13` stays at the 10 names
#408's `C36` filed; `import sage_extensions.all` after `sage.all` is 0.319 /
0.254 / 0.252 s on the base against 0.319 / 0.309 / 0.320 s here, three fresh
processes each, under the suite's 3.0 s ceiling for that workload.

| log | commit cited | result |
| --- | --- | --- |
| `issue468-star-bindings.py` | — | the audit, re-runnable: reads the areas from `all.py` (star imports, or `_AREA_PACKAGES` on the base), checks every declaration is bound to the declarer's object, prints the six and eighteen names with owner, Sage namesake and origin, then constructs the six |
| `issue468-star-bindings-base.log` / `-repair.log` | base `37b67b7` / the tree of this push | 22 areas, 599 declarations, 524 distinct, 75 shared, 0 unbound, no loop temporary; `CoxeterGroups` `SHADOWED`, the other 22 `none`; the five constructions |
| `issue468-star-namespace-dump.py` | — | the dump: name, bound type, and the object's `__module__`/`__qualname__`; a `LazyImport` is recorded unresolved because ten `categories.functions` names raise on first access (#440, older than this repair) |
| `issue468-star-namespace-dump-base.log` / `-repair.log`, `issue468-star-namespace-diff.log` | base `37b67b7` / the tree of this push | 690 names against 689; the `diff` is one deleted line, `_AREA_PACKAGES` |
| `issue468-star-cause-ids.py` | — | the id-level comparison of two trees' JUnit reports |
| `issue468-star-causes-base.log` / `-repair.log` | base `37b67b7` / the tree of this push | the 16 files' pytest summaries side by side; identical in every file |
| `issue468-star-causes-ids.log` | base `37b67b7` / the tree of this push | 141 ids and 43 red in both; same id set; no id green on the base and red here; the 15 recorded ids green in both |
| `issue468-star-runs/base/*.log`, `issue468-star-runs/repair/*.log` | base `37b67b7` / the tree of this push | the 32 whole runs, one process per file |
| `issue468-star-lint-tree-base.log` / `-repair.log` | base `37b67b7` / the tree of this push | tree-wide `test_lint`: 932 files, 1424 findings in each, lines identical |
| `issue468-star-import-time.py`, `-base.log`, `-repair.log` | base `37b67b7` / the tree of this push | `import sage_extensions.all` after `sage.all`, three fresh processes: 0.319 / 0.254 / 0.252 s against 0.319 / 0.309 / 0.320 s |
| `issue452-controls.log` | `eb07c43`'s tree (the probe carries its own copy of the locus' class reading) | the control search for #405: `U(2) + U(2) + <2>`, 64 classes reported and 32 integral — **DISAGREE, 32 extra**; the four existing controls and five further candidates agree | 
| `issue452-locus-cosets.log` | `eb07c43`'s tree (same probe) | the corrected coset reading at card 029J's 4.3.8 line: period 4, ten Smith invariants one, **1024 representatives, 256 passing, `|K| = 1024`**, the 275-member family all integral, **`ρ(K_v)` order 256**, passing+generator integral and refused+generator not | 
| `issue452-locus-tests.log` | `eb07c43`'s tree with this commit's change to `isotropic_lifts.py` | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`: **4 passed in 5.09 s**, lint on, exit 0 — the new `U(2) + U(2) + <2>` control included | 
| `issue452-reduction-image-tests.log` | `eb07c43`'s tree with this commit's changes | `tests/lattices/test_the_isotropic_reduction_image.sage`: **11 passed in 1183.07 s**, including the five-row chamber test at 554.82 s and the strengthened two-lifts test at 234.91 s; `--no-time-gates` because four calls are over the 20 s ceiling (the overrun is reported in the log) | 
| `issue452-locus-tests-merged.log` | `27fd250`, the merge of this repair with `a8b7eb8` | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`: **4 passed in 4.83 s**, lint on, exit 0 | 
| `issue452-reduction-image-tests-merged.log` | `27fd250`, the same tree | `tests/lattices/test_the_isotropic_reduction_image.sage`: **11 passed in 1504.36 s**, the five-row chamber test at 752.69 s and the two-lifts test at 272.78 s; `--no-time-gates`, the five overruns printed | 
| `issue452-tco-coset-count.log` | `fd0f1c0`, the pushed tree (the probe reads the locus' own Smith data) | the number of lift tests a `T_Co = <2> + (U + E8(-1))(2)` line of divisibility two forces: period 4, rank 9, nine Smith invariants one, **512 coset representatives, `|K| = 512`**, `|P/mP| = 262144` — so one `integral_restriction` per coset is the 512-test cost the repair adds to that line, and no `T_Co` row was run | 
| `issue452-unequal-steps-search.py`, `.log` | `045fe69`, the tree before this repair | the sweep for a control whose section has unequal Smith steps: 140 (lattice, marked vector) pairs over `U(k)`, `U(2)`, `U(4)`, `U(8)` summed with `<2>+<2>`, `<2>+<4>`, `<4>+<4>`, `A2`, `A2(2)`, `A3(2)`, `D4(2)`; **9 unequal**, every one of them `U(4) + <2> + <2>` at a non-basis marked vector with steps `(32, 16)`; every basis-vector marked line has all steps equal | 
| `issue452-unequal-steps-locus.py`, `-before.log` / `-after.log` | `ada50c4` / `8f6d5cf` | the chosen control `U + A3(2)` at `-2e0 + 2e1 - e2 + 2e3 - e4`: period 8, denominator 4, Smith invariants `(1, 2, 2)`, steps `(4, 2, 2)`, `V = ((0,0,-1),(-1,0,-2),(1,-1,0))` not a signed permutation of the cube; **the locus reports 256 of the 512 classes of `P/mP` before and 512 after**, the direct enumeration 512 in both | 
| `issue452-unequal-steps-red.log` | `ada50c4`, the test commit's own tree | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`: **1 failed, 4 passed in 20.17 s**; the failure is `Extra items in the right set` on the new control | 
| `issue452-locus-coset-readings.log` | `d83ae97`, the repair | the same file: **5 passed in 21.56 s**, `test_lint` on | 
| `issue452-reduction-and-eichler-tests.log` | `8f6d5cf` | `test_isotropic_reduction.sage`, `test_eichler_isometry_relations.sage`, `test_two_u_eichler_model.sage`: **18 passed, 1 failed in 7.94 s**; the failure is `test_approximate_generating_family_uses_exact_two_u_perpendicular_frames` | 
| `issue452-two-u-eichler-base.log` | `ada50c4`, before the repair | the same id fails there as well: 1 failed, 8 passed in 6.04 s — **pre-existing, not a regression** | 
| `issue452-reduction-image-tests-2.log` | `8f6d5cf`, the repaired tree | `tests/lattices/test_the_isotropic_reduction_image.sage`: **11 passed in 1168.99 s**, the two-lifts test at 239.08 s, the published-cusp-roots test at 294.36 s, the five-row chamber test at 547.53 s; `--no-time-gates`, the four overruns printed — `K_v` from the repaired locus and the sifting membership give the same answers as before | 
## Issue #500: a ring element divides in its ring, and a module's element divides by a scalar

`7717c62` replaces the per-realization placement of `b3c7ca3`. A ring is a left module over itself, so
a ring element's class carries both the ring's quotient `a b^{-1}` and the module's scalar action
`b^{-1} a`; they agree only when the ring commutes. `OwnedRings.ElementMethods` now states the
operator, `__truediv__ = Element.__truediv__`, and the module level keeps `v / r = r^{-1} v` for the
modules whose elements are not ring elements. The composition had to be read twice: a chain-built
parent composes `(Element, category.element_class)`, where the ring level already precedes the module
level, while `refine` prepends newly reached category methods to the whole native element class of an
adopted parent, so a ring first built as a module over itself kept the module's division whatever the
final category order said. `_final_category_operations` is now shared by the parent and the element
rebuild, and `_realization_operations` keeps the object's own implementation in front of a level a
refinement moved ahead of it. The two owned fields state their reciprocal as `one() / x` with no
direct `_div_` call.

| row | at a71272a (main before this push) | on the tree of this push |
| --- | --- | --- |
| `M_2(QQ)`: `~divisor` | the module's scalar action answered `__truediv__` | `1 - e_21`, the inverse in the ring |
| `M_2(QQ)`: `e_12 / (1 + e_21)` | `ValueError: ... is not in Category of sets with partial maps` (1 failed, 3 passed on the slice's own test) | `e_12 - e_11`, which is `e_12 (1 - e_21)`; `(1 - e_21) e_12` is `e_12 - e_22` |
| `RR`, `CC`: `__truediv__` written in | `ExactRealNumber`, `ExactComplexNumber` (`b3c7ca3`) | `OwnedRings.ElementMethods [Element.__truediv__]`, with `_div_` at `ExactRealNumber`/`ExactComplexNumber` |
| `QQ[x]`, `QQ[x]/(x^2-2)`, `QQ(i)`: `__truediv__` written in | `Modules.ElementMethods` | `_OwnedRingElement.__truediv__`, reached through the rebuilt element class |
| `ZZ`: `3 / 2` | `3/2` by the realization's division | `3/2`, the same realization, now also under the coercion model |
| a QQ-module vector `/ 2` | `(1)/(2)*v` by the module formula | the same, and it is the module's own operation |

| log | commit cited | result |
| --- | --- | --- |
| `500-element-class-division.log` | `7717c62` | where each ring's `__truediv__` and `_div_` are written, by class and descriptor; then `e_12/(1+e_21) == e_12 - e_11` with `!= e_12 - e_22` and `!= (~divisor) e_12`, the module's `v / r`, the lattice's refusal, and `RR`/`CC` reciprocals including `1/(sqrt 2 - 1) == sqrt 2 + 1` and `packing_radius() = 1/2` |
| `500-ring-division-new-test.log` | `7717c62` | `tests/rings/test_elements_divide_in_their_own_ring.sage`: **4 passed in 20.11 s** (1 failed, 3 passed at `a71272a`) |
| `500-gate-410-slice.log` | `7717c62` | #410's slice -- four cause-A ids, the cause-B id and #150's contract: **6 passed in 2.20 s** |
| `500-integer-literal-division.log` | `7717c62` | an integer divisor on an engine-backed ring: `ZZ(3)/2 = 3/2`, `QQ[x](x)/2`, `(1 + sqrt5)/2`, and `Sterk.sterk_roots()` returning its five diagrams |
| `500-refine-resolution-surface.log` | `7717c62` | the names the two rebuild rules resolve, over fourteen object kinds: `__truediv__` and `order_ideal` on the refined element classes, `__add__`/`__sub__` and `norm`/`trace` where a category level had moved in front of the realization, `__iter__`/`adic_completion` on the refined parents |
| `500-regression-compared.log` | `7717c62` against `a71272a` | fourteen directories and the root `tests/*.py`, one pytest process each per tree, FAILED ids and not counts: every row has an empty only-on-this-tree set; `tests/rings` has **two fixed ids** and 74 failed, 258 passed against 76 failed, 252 passed. Not measured: `tests/lattices` as one directory (6245 MiB, stopped by the 6144 MiB guard on both trees) and `tests/groups` (1000 s cap) |
| `issue452-merged-quick-tests.log` | `b2676c2`, the merge of this repair with #500's ring division | `test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`, `test_isotropic_reduction.sage`, `test_eichler_isometry_relations.sage`: **15 passed in 21.13 s** | 
| `issue452-merged-reduction-image-tests.log` | `b2676c2`, the same tree | `tests/lattices/test_the_isotropic_reduction_image.sage`: **11 passed in 1227.36 s**, the two-lifts test at 244.30 s, the published-cusp-roots test at 300.90 s, the five-row chamber test at 578.05 s; `--no-time-gates`, the five overruns printed | 
## Issue #500, the review of `7717c62`: one operator, the `_div_` hook, and the narrowed rebuild rule

The review found three things in `7717c62`: a second division operator at `_OwnedRingElement`, a `refine` rule that
went past the issue (`_realization_operations`, and a dunder widening that let `__init__`, `__eq__`, `__hash__` and
`__call__` be copied onto rebuilt classes), and a contract docstring that said "its division by a unit" where
`ZZ(3)/2` answers `3/2`. `904e079` answers all three and `9fd76e4` corrects the sentence that named the wrong owner
of the quotient's parent. The operator is the ring category's (`OwnedRings.ElementMethods.__truediv__ =
Element.__truediv__`), the engine-backed realization implements `_div_`, `_OwnedRingElement.__truediv__` and its
`__rtruediv__` are gone, `_realization_operations` is deleted, and the rebuild rule keeps the Python protocol
operations on an object's value while `_RUNTIME_OWNED_NAMES` keeps construction and identity where the runtime put
them. `QQ`, and the localization and quotient realizations, answer `divide_by_unit`: the same law `a b^{-1}` stated
at the monoid level, not the module's `b^{-1} a`.

The coercion the operator needed is not the one `7717c62` recorded. `sage.structure.element.parent` answers `int`
for a Python `int`, so the coercion model asks `_coerce_map_from_(int)` and never passes through Sage's ZZ; what it
met was that no owned ring stated a coercion from the integers. A session's literal is not even a Python int: the
preparsed `.sage` test's `2` is the session's own integer, which is why `ZZ(3)/2` divided on the old tree while
`e12/2` did not. `OwnedRings.ParentMethods` states the map from both -- the prime ring's unique unital morphism --
and `_OwnedRingParent` states it too, because it answers the canonical sources it knows before the category does.

| row | at 0a8a95b (main before this push) | on `9fd76e4` |
| --- | --- | --- |
| `M_2(QQ)`: `e12 / 2` | `TypeError: unsupported operand parent(s) for /: ... and 'Integer Ring'` | `(1/2) e12` |
| `ZZ`: `3 / 2` | `3/2`, through the realization's own operator | `3/2`, through `OwnedRings.ElementMethods` and `_OwnedRingElement._div_` |
| `QQ[x]`, `QQ(i)`: `__truediv__` | `_OwnedRingElement.__truediv__`, installed by `_realization_operations` | `OwnedRings.ElementMethods [Element.__truediv__]`, kept by `_final_category_operations` |
| names a rebuild moves | `__add__`, `__radd__`, `__rsub__`, `__sub__`, `norm`, `trace`; and `order_ideal`, `__iter__`, `adic_completion` | `__truediv__` and `order_ideal` on element classes; `__iter__` and `adic_completion` on parents |
| a category's `__init__` on a rebuilt class | reachable: every dunder passed the filter | never: `_RUNTIME_OWNED_NAMES` |
| `M_2(ZZ)(1) / 2`, open | `TypeError` | `TypeError: no conversion of this rational to integer`, the matrix realization's inverse over ZZ, not the ring's unit refusal |

| log | commit cited | result |
| --- | --- | --- |
| `500-review-surface.log` | `9fd76e4` | where `__truediv__`, `__rtruediv__` and `_div_` are written for eight owned rings; the canonical sources each states (`int` and the session's integers answered, a raw Sage integer not); `ZZ(3)/2 = 3/2` with parent `QQ`, `ZZ(2)/ZZ(4) = 1/2`, `QQ(3)/ZZ(2)`, `QQ[x](x)/ZZ(2)`, `RR(3)/ZZ(2)`, `CC(3)/ZZ(2)`, `e12/ZZ(2) = (1/2)e12`, `e12/(1+e21) = e12 - e11` against `(1+e21)^{-1} e12 = e12 - e22`, the module's `v/2 = (1/2)v`, the lattice's `2 is not a unit`; then the names the rebuilds moved, and that no rebuilt class declares a category's `__init__` |
| `500-review-literal-is-the-session-integer.log` | `9fd76e4` | a preparsed test's literal: `parent(2)` prints `Integer Ring` and `type(2)` is `_OwnedRingParent_with_category.element_class`, so the session's literal is the session's integer. The probe file was removed after the run |
| `500-review-slice.log` | `9fd76e4` | `tests/rings/test_elements_divide_in_their_own_ring.sage`: **5 passed in 18.50 s**, lint plugin on (the fix commit cites the first run of this file at `d3ca9ee`, 18.30 s) |
| `500-review-gate-410.log` | `9fd76e4` | #410's slice -- four cause-A ids, the cause-B id and #150's contract: **6 passed in 1.89 s** |
| `500-review-base-red.log` | `0a8a95b` | the same test file at main: **1 failed, 4 passed in 19.32 s**, red on `test_an_integer_literal_divides_in_the_parent_the_two_share` at `e12 / 2` |
| `500-review-regression-compared.log` | `9fd76e4` against `0a8a95b` | fourteen directories and the root `tests/*.py`, one pytest process each per tree, FAILED ids compared: **every row has an empty only-on-this-tree set**; `tests/rings` is 74 failed, 259 passed against 75 failed, 258 passed, with the one fixed id being the new test. The sweeps ran on `d3ca9ee`, whose `src` and `tests` are `9fd76e4`'s (`git diff d3ca9ee 9fd76e4 -- src tests` is empty) |
| `issue452-final-quick-tests.log` | `ba3ab60`, the pushed tree | the lift-locus file with `test_isotropic_reduction.sage` and `test_eichler_isometry_relations.sage`: **15 passed in 20.99 s** | 
| `issue452-pushed-reduction-image-tests.log` | `ba3ab60`, the same tree | `tests/lattices/test_the_isotropic_reduction_image.sage`: **11 passed in 1538.48 s**, the two-lifts test at 231.33 s, the published-cusp-roots test at 365.35 s, the five-row chamber test at 858.67 s; `--no-time-gates`, the four overruns printed | 

## Issue #500, the second review: one authority for the integer coercion, the positive criterion, and the three tests

The review of `9fd76e4` found the integer coercion stated twice, a deny-list deciding which dunders the rebuild rule
may order, three moved operations with no test, and one false sentence in the ring contract. `6828f81` answers all
four. The criterion is now the Python language reference's container protocol (Data Model, §3.3.7) and numeric
protocol (§3.3.8) plus public names, 62 names; the integer map is stated once, on `OwnedRings`, and the
engine-backed realization defers to it through `super()`; the tests are
`tests/categories/test_the_refined_category_answers_with_its_own_operation.sage`, stating for `QQ(i)` which level
answers `order_ideal`, `__iter__` and `adic_completion` and what each returns.

| log | commit cited | result |
| --- | --- | --- |
| `500b-findings.log` | `6828f81` | the four findings read on the tree that answers them: the two `_coerce_map_from_` hooks and which names their bytecode holds (`_OwnedRingParent`'s no longer names `_owned_ring_from_integer`); for eight rings what the `int` case, the session integer and a raw Sage integer answer, and the integer case reached through `super()`; the criterion's answer for twenty-one names and its 62-name size; the names the rule installs on each of the eight rings' classes, with the dunders outside the value protocol; the level answering each of the three moved operations on `QQ(i)` and its value; the ring contract's docstring |
| `500b-criterion.log` | `6828f81` | the old deny-list and the new criterion run over the same providers for eighteen constructed objects (the eight review rings, `ZZ**2`, `QQ**2`, two lattices, `ZZ_5`, `ZZ/8`, `Zp(5)`, `ZZ[i]`, `QQ[x,y]`): **the same four names are selected by both** -- `__truediv__`, `order_ideal` on element classes, `__iter__` and `adic_completion` on parent classes -- with **nothing selected by only one of the two** |
| `500b-tests.log` | `6828f81` | `tests/categories/test_the_refined_category_answers_with_its_own_operation.sage` and `tests/rings/test_elements_divide_in_their_own_ring.sage`: **8 passed in 16.57 s**, lint plugin on (the fix commit cites the first run of the same two files on the same content, 18.91 s) |
| `500b-sweep-tree.log` | `6828f81` | thirteen test directories, one pytest process each: 840 FAILED ids in total. The runs were made on the working tree before it was committed, and its `src` and `tests` are `6828f81`'s |
| `500b-sweep-base.log` | `ba3ab60` | a clean worktree at the commit fetched from main: the same thirteen directories and the root `tests/*.py` |
| `500b-sweep-tree-extra.log` | `6828f81` | the root `tests/*.py` (**25 passed in 10.92 s**), and the two lattice files that read the framed content: `test_content_and_doubling.sage` 1 failed, 3 passed; `test_reflection_rational_line.sage` 4 passed |
| `500b-sweep-base-extra.log` | `ba3ab60` | the same two lattice files on the base: 1 failed, 3 passed and 4 passed, the same ids |
| `500b-regression-compared.log` | `6828f81` against `ba3ab60` | FAILED ids compared per target: **840 on each side, 0 only on the tree, 0 only on the base**; the only count difference is `tests/categories` 59 passed against 56, which is the three new tests. Not swept as one directory: `tests/lattices`, 5.6 GiB resident and unfinished after 25 minutes here |

## Issue #500, the third review: the order-ideal regression, its owner, and the three notes

The second review's tree (`6828f810a0`) raised on `(2x+2).order_ideal()` for `ZZ['x']` and on `(x+1).order_ideal()` for
`QQ['x']`: the rebuild rule of #500 keeps `Modules.ElementMethods.order_ideal` on these rings, and that method read
`dual.codomain()` off a dual that, for an infinite chosen basis, is the product `R^S` and has no codomain attribute.
The mathematics such a call must answer is `ZZ.ideal(2)` and `QQ.ideal(1)`; both are the values the same calls
returned at `51310d6`. `af3edee` asserts them red, `ef39a9b` repairs the method at its owner, `b5cfd57` moves the
ring-point enumeration onto `OwnedRings().Finite()`, `1b8358c` states the completion at the zero ideal by its map.

| log | commit cited | result |
| --- | --- | --- |
| `500c-red.log` | `af3edee` (with only the test added to `9bc1185`) | `tests/modules/test_the_order_ideal_of_a_ring_element_over_its_base_ring.sage`: **2 failed in 1.34 s**, both at `modules.py:1663 in order_ideal -- regular = dual.codomain()`, `AttributeError: 'GeneralModules.parent_class' object has no attribute 'codomain'` |
| `500c-tests.log` | `1b8358c` | the two test files this issue changes, with the test lint plugin on: **5 passed in 1.85 s** |
| `500c-tests-uncommitted.log` | the working tree whose `src` and `tests` are `b5cfd57`'s and `1b8358c`'s, before they were committed | the two files above plus `tests/rings/test_elements_divide_in_their_own_ring.sage`: **10 passed in 21.14 s** |
| `500c-lint-uncommitted.log` | the same working tree | the two files with `-o addopts= -p sage_extensions.testing.test_lint`: **5 passed in 6.01 s** |
| `500c-order-ideal-at-51310d6.log` | `51310d6` (a clean worktree) | `(2x+2).order_ideal()` on `ZZ['x']` is `Ideal (2) of Integer Ring` and equal to `ZZ.ideal(2)`; `(x+1).order_ideal()` on `QQ['x']` is equal to `QQ.ideal(1)`; `(1+i).order_ideal()` on `QQ(i)` is equal to `QQ.ideal(1)`. All three answered by `FramedFreeModules.ElementMethods.order_ideal` |
| `500c-coercion-at-51310d6.log` | `51310d6` | `has_coerce_map_from` read source by source (int, `ZZ`, `QQ`, `QQ(i)`, `ZZ['x']`, the module `ZZ**2`) on `ZZ['x']`, `QQ(i)` and `M_2(QQ)`, with `_coerce_map_from_`'s owner |
| `500c-coercion-on-main.log` | `9bc1185` | the same probe on main. **Appeared: `int` on all three rings, and `ZZ` on `M_2(QQ)`** (whose hook owner moves from `sage.structure.parent.Parent` to `OwnedRings.ParentMethods`). **Vanished: none.** Values: `ZZ['x'](3) == 3*1`, `QQ(i)(3) == 3`, `M_2(QQ)(3) == M_2(QQ)(ZZ(3)) == 3*I`; every module and cross-ring source stays refused |
| `500c-iter-before.log` | `af3edee` (a clean worktree) | before the move: `GF(2)`, `GF(4)`, `Zmod(6)`, `Zmod(8)` enumerate through `OwnedRings.ParentMethods`; `QQ(i)` and `ZZ['x']` refuse with `it is not placed among finite sets`; `ZZ` already raises `unable to coerce <class 'dict'> to an integer` from the framed free module's enumeration |
| `500c-iter-after.log` | the working tree whose `src` is `b5cfd57`'s | after the move: the four finite rings enumerate the same points through `OwnedRings.Finite.ParentMethods`; `QQ(i)` and `ZZ['x']` refuse with `it is not a finite ring, so its points are not a finite iteration of its selected engine`; `ZZ` is unchanged. The intermediate state, with the general refusal deleted, is not in this log: measured then, `tuple(ZZ['x'])` handed back the ring itself forever and `iter(QQ(i))`/`iter(ZZ)` reached the framed coordinate enumeration and raised on the first element |
| `500c-completion-map.log` | `9bc1185` | the completion of `QQ(i)` at `(0)`: the kernel is the zero ideal, `completion_map().is_injective()` is `True`, `is_surjective()` is the proposition `is_surjective(...)` (decided only between finite enumerated endpoints), `as_isomorphism()` refuses for lack of it, and `is_isomorphic_to(field)` is `True` |
| `500c-rings-tree.log` | the working tree of `b5cfd57` | `tests/rings`, one pytest process: **74 failed, 259 passed in 49.64 s** |
| `500c-rings-base.log` | `af3edee` | the same command on a clean worktree: **74 failed, 259 passed in 55.75 s**. The 74 FAILED ids are identical; the earlier run of this change had 19 more and they were all the `refine` name shadowed by a local import, repaired before this log |
| `500c-sweep-tree.log` | the working tree of `b5cfd57` | eleven test directories, one pytest process each, plus the root `tests/*.py`: 465 FAILED ids |
| `500c-sweep-base.log` | `af3edee` | the same twelve targets on a clean worktree: 467 FAILED ids |
| `500c-compared.log` | the two sweeps above | FAILED ids compared per target: **0 only on the tree**, and the only two ids only on the base are the two red tests this issue adds, so **0 new and 2 fixed**. `tests/lattices` is not swept as a directory (5.6 GiB resident, unfinished after 25 minutes on this host); its two files that read the framed content are below |
| `500c-lattice-content-tree.log` | the working tree of `b5cfd57` | `tests/lattices/test_content_and_doubling.sage`: 1 failed, 3 passed (`test_index_two_sublattices_of_a_hyperbolic_summand`) |
| `500c-lattice-content-base.log` | `af3edee` | the same file on a clean worktree: 1 failed, 3 passed, the same id |
| `500c-lattice-reflection-tree.log` | the working tree of `b5cfd57` | `tests/lattices/test_reflection_rational_line.sage`: **4 passed** |
| `500c-lattice-reflection-base.log` | `af3edee` | the same file: **4 passed** |

The probe sources behind the `500c-*` measurement logs are session probes, not library code, and stay out of the
tree as the repository requires: each one builds the rings named in its row and prints what the call returned, its
value and the class that answered, so the log carries every reading it is cited for.

## Issue #500, fourth review (added 2026-11-15)

Base for every comparison: a clean worktree at `5f17b92fe7`, the main this round
started from.  "The tree" is the working tree whose `src` and `tests` are
`c5af4fc`, `7b23fc3` and `1a53c51`.

| log | commit cited | result |
| --- | --- | --- |
| `500d-red.log` | `5f17b92fe7` (a clean worktree, with only the new test copied in) | `tests/rings/test_a_ring_states_no_enumeration_of_its_points.sage`: **1 failed in 1.36 s** at `assert __iter__ is None` -- the general ring still answers `__iter__` with a method there |
| `500d-tests.log` | `c5af4fc`, `7b23fc3`, `1a53c51` | the four files this issue owns, with the test lint plugin on: **11 passed in 18.40 s** |
| `500d-order-ideal.log` | the tree of `1a53c51` | per object: the module, its base ring, the dual's shape, which method answers, the order ideal, whether it is in `CommutativeIdeals(R)`, the values `dual_evaluation_image_generators` returns, the framed level's own answer, and `dual_evaluation` at the first coordinate functional of the product. `Modules.ElementMethods.order_ideal` answers on `ZZ['x']`, `QQ['x']`, `QQ(i)` and `Zmod(8)`; `FramedFreeModules.ElementMethods.order_ideal` on `ZZ**2` and `Lattices(ZZ)([[2]])`. Values: `(2x+2)` -> `Ideal (2)` of `ZZ`, `(x+1)` -> the unit ideal of `QQ`, `(-6,9)` -> `(3)`, `6e0` -> `(6)`, every one of them in `CommutativeIdeals` of its base ring. `Zmod(8)(3)` is computed by neither reading: the module level raises `ValueError: Mor(Z/8, Z) has no chosen resolution` from the dual's own owner, and the framed level raises `AttributeError: ... has no attribute 'to_vector'` |
| `500d-iter.log` | the tree of `7b23fc3` | `ZZ['x']`, `QQ['x']`, `QQ` and `QQ(i)` resolve `__iter__` to `None`; `iter` and `tuple` raise `TypeError` at once (`'...' object is not iterable`), so `tuple(ZZ['x'])` does not read `ZZ['x'][0]`. `ZZ` resolves it to `FramedFreeModules.FinitelyGenerated.ParentMethods` and raises `unable to coerce <class 'dict'> to an integer` (#526, unchanged). `Zmod(8)`, `Zmod(1)`, `GF(2)`, `GF(4)`, `GF(9)` enumerate 8, 1, 2, 4 and 9 points through `OwnedRings.Finite.ParentMethods` |
| `500d-finite-probe.log` | the tree of `7b23fc3` | the finite rings of every owned constructor: quotient `Z/8` (8 points), `Z/1` (1), prime field `Z/2` (2), residue field of `Z/4` (2), polynomial quotients `GF(4)` (4) and `GF(9)` (9) -- all in the finite-ring axiom, all enumerating through `OwnedRings.Finite.ParentMethods`. Products `GF(2) x GF(2)` (4) and `Z/4 x GF(3)` (12) are in the axiom and **do not enumerate**: their class resolves `__iter__` to `FramedFreeModules.FinitelyGenerated.ParentMethods`, which raises `ValueError: (0,) should be of length 2` |
| `500d-finite-probe-before.log` | `5f17b92fe7`, unmodified | the same probe before this round: same constructor answers everywhere except that an infinite ring refuses with `it is not a finite ring, so its points are not a finite iteration of its selected engine`. The two products already answered through the framed module's coordinate iteration, so the placement change does not move them |
| `500d-sweep-tree.log` | the tree of `c5af4fc`, `7b23fc3`, `1a53c51` | twelve test directories, one pytest process each, plus the twenty root `tests/*.py` files: FAILED ids listed per target |
| `500d-sweep-base.log` | `5f17b92fe7` (a clean worktree) | the same targets on the base |
| `500d-compared.log` | the two sweeps above, and the two below | FAILED ids compared per target: **0 only on the tree, 0 only on the base** for every target. The one count difference is `tests/rings` **260 passed against 259** -- the new test |
| `500d-lattices-tree.log` | the tree of `1a53c51` | `tests/lattices/test_content_and_doubling.sage`: 1 failed, 3 passed (`test_index_two_sublattices_of_a_hyperbolic_summand`); `tests/lattices/test_reflection_rational_line.sage`: **4 passed** |
| `500d-lattices-base.log` | `5f17b92fe7` | the same two files: the same ids |
| `500d-extra-tree.log` | the tree of `1a53c51` | the seven files that read the dual, the order ideal or a lattice element: `test_lattice_semantic_api` 4 passed, `test_lattice_elements` 6, `test_named_lattice_constructions` 12, `test_hodge_calculus` 3, `test_hyperbolic_space` 3 failed, `test_all_ones_form_correlation` 2 passed, `test_infinite_form_duality` 2 failed |
| `500d-extra-base.log` | `5f17b92fe7` | the same seven, id for id |
| `500d-merge-check.log` | `7232ec0` (the merged tree; the file is `7a35416`'s, from the #285/#312 chat) | `tests/lattices/test_the_isotropic_reduction_image.sage`'s five new cusp-chamber tests under this issue's changes: **5 passed in 942.10 s**, the chamber test 938.17 s past the 20 s call gate (`--no-time-gates`, as `7a35416` measured 907.97 s). The whole file run without `-k` was cut at a 1500 s cap after eleven tests had passed and none failed |

The probe sources behind the `500d-*` measurement logs are session probes, not
library code, and stay out of the tree: each prints the rings, the values and the
class that answered, so the log carries every reading it is cited for.
## #285: the cusp group carries Sterk's printed chamber onto the returned one

`tests/lattices/test_the_isotropic_reduction_image.sage` gains
`test_each_cusps_chamber_is_sterks_under_an_element_of_the_cusp_group`. At each of Sterk's five cusps it asks the
library's `O(N).transporter` for one isometry of `N = v^⊥/Zv` carrying the card's printed wall vectors onto the
walls `cusp_chamber()` returns (the transporter searches the diagram's own symmetries and solves each exact linear
system, so no reindexing is chosen by hand), and then asks the image's `contains` — the discriminant criterion
`ρ(g) ∈ ρ(K_v)ρ(Γ_{En,2})`, one sift, no element list — whether that isometry lies in the cusp group `G_v`. The
answer is yes at all five, so Sterk's published simple roots are the returned ones moved by an element of `G_v`,
which is #285's clause; equal Gram matrices left exactly this open. The whole file, all 17 tests, runs in the image
job `isotropic-reduction-image-tests.yml`, which no turn waits on; the rows below are the run at one cusp each and
the lint, which is what a turn's feedback loop allows.

| log | commit cited | result |
| --- | --- | --- |
| `issue285-transporter-final.log` | `7a35416` plus the test change of this commit (uncommitted at the time of the run) | the new test's own body — the module's helpers and the module's assertions — at (4.3.5) and (4.3.9): 12 printed and 12 returned walls with the transporter carrying one family onto the other and `contains` `True` in 219.9 s, and 14 and 14 with `contains` `True` in 212.4 s; the two families differ as sets of walls at both cusps; the probe's whole run 436 s, peak tree RSS 1757 MiB on the pinned image with the indefinite port at `/work` |
| `issue285-transporter-435.log` | the same working tree | (4.3.5): chamber and printed family in 230.8 s, 12 walls each, 9 positions coincide, the transporter found in 0.1 s and `contains` `True` in 0.7 s |
| `issue285-transporter-four.log` | the same working tree | (4.3.6), (4.3.7), (4.3.8), (4.3.9) in one process: chambers in 234.7, 176.7, 181.3 and 197.8 s; 10, 12, 11 and 14 walls with 6, 2, 1 and 0 positions coinciding; the transporter in 0.1–0.2 s and `contains` `True` in 0.7–1.9 s at every one; the probe 802 s, peak tree RSS 956 MiB. This run compares the two families sign-insensitively, which is the earlier form of the assertion; the isometry it reads is the same object the committed test asserts, and the sign-sensitive comparison is the row above |
| `issue285-transporter-lint.log` | the same working tree | `python -m sage_extensions.testing.test_lint tests/lattices/test_the_isotropic_reduction_image.sage`: **1 files, 0 findings** in 4.0 s |

The probe sources behind these logs are session probes, not library code, and stay out of the tree: each execs the
test file through `sage.repl.preparse` and runs the test's body for the cusps named on its command line, or prints
the chamber, the transporter and the membership answer at one cusp.

## #529 — the durable timing record

`src/sage_extensions/timing.py` is the one logger (`logging.getLogger("sage_extensions")`) the long
computations record their stages through, and `src/sage_extensions/testing/timing_record.py` is the pytest
plugin that keeps a run's report log and JUnit file. Both write `.timings/` at the checkout's root, named by
commit and start time (`CONTRIBUTING.md` ENV-03); the test is
`tests/engineering/test_the_timing_record_names_each_stage.py`. Every run below is in the pinned image with the
indefinite port bound at `/work`, the checkout at `/repos/sage-extensions`, from the checkout at `0fd90fc` plus
this commit's working tree, except the two rows marked *base*, which are a clean worktree at `0fd90fc`.

| log | tree | result |
| --- | --- | --- |
| `issue529-neighbours.log` | this commit | `tests/engineering/` plus the two small-indefinite line-row files, `--no-time-gates` with `test_lint` loaded: **3 failed, 12 passed in 49.0 s**; the three failures are `test_polyhedral_engine_routes.sage`'s two (Julia/Hecke route) and `test_SO_U_has_two_orbits_on_the_primitive_isotropic_lines_of_U` |
| `issue529-baseline.log` | base | the same command on the clean worktree: **3 failed, 10 passed in 47.4 s**, the same three test ids, and the same 22.50 s performance-gate report on the small-indefinite file as this tree's 22.48 s — so the instrumentation moved no result and no gate |
| `issue529-stages.log` | this commit | the Vinberg, divided-class and stable-plane files, `--no-time-gates`: **15 passed in 66.3 s**; the divided-class construction's own 23.02 s call-gate report is the same file's pre-existing overrun |
| `issue529-real-addopts.log` | this commit | the new test file under the repository's real addopts: **2 passed in 1.93 s**, and `.timings/` afterwards holds `run-0fd90fcd0298-20261115T064853Z.jsonl`, `junit-…xml` and `stages-…jsonl` — the plugin's copy and the library's records in one directory |
| `issue529-combined-addopts.log` | this commit | the new test file, the setwise-stabilizer file and the Vinberg file under the real addopts: **9 passed in 82.5 s**; the run is red on the call gate for `test_every_setwise_stabilizer_generator_has_a_discriminant_image` at 38.13 s, which the two rows below show is this venue's |
| `issue529-setwise-base.log` | base | `test_setwise_stabilizer_discriminant_images.sage` alone under the real addopts: **2 passed in 60.6 s**, first test **41.51 s > 20 s**, plane call 17.99 s |
| `issue529-setwise-mine.log` | this commit | the same file alone: **2 passed in 60.9 s**, first test **41.07 s > 20 s**, plane call 18.54 s — the plane call the new stages wrap costs 0.55 s more, and the gate failure is the base's |
| `issue529-records.log` | this commit | the census of the six files the combined run left in `.timings/`: 15 stage records, 11 stage names, the plane row at 21.227 s of which the discriminant images are 20.290 s and the orbit set 0.925 s, and 5 Vinberg walks slowest 5.913 s |

The three pre-existing failures and the 22 s gate report were re-measured on the clean worktree in the same
session rather than assumed; nothing in this commit touches the code they run.

The seven workflow steps of ENV-03 are `results/issue529-timing-record-workflows.patch`, not history: the
connection's GitHub App may not update a file under `.github/workflows/` and the push was refused with
`refusing to allow a GitHub App to create or update workflow ... without 'workflows' permission`. The patch is
`git diff da0fa12..<the commit that carried them> -- .github/workflows/` and `git apply --check` passes against
`da0fa12`'s workflows; the two `uses:`-only tiers are not in it, as ENV-03 says.
## #530 and the last items of #500: one dual construction, and the evaluation image

`Modules.dual_module()` had two shapes -- the internal Mor when the chosen basis
was finite, the categorical product `prod_S R` when it was infinite -- selected by
`_dual_product_construction`. #530 rules that the dual has one basis-free
construction, `Mor(M, R.regular_module())`, that the order ideal is the image of
evaluation `dual_evaluation(-, v): M^* -> R` computed by the morphism's image
owner, and that `dual_evaluation_image_generators`, its shape match and the
coordinate round trip in general `Modules` go. What the probes below establish is
where that image is computable and where it is not: a module whose dual carries a
chosen presentation (`ZZ**2`, `QQ(i)`, the lattices) gets it from the image owner,
and a free module on an infinite basis cannot, because its dual is the product
`prod_S R` and no family of that product generates it. There the image is
generated by the coordinate functionals of the chosen basis, which is the framed
free module's own computation, and `order_ideal` delegates to it rather than
repeating it (`STY-54`).

| log | commit cited | result |
| --- | --- | --- |
| `530-dual-shapes-before.log` | `0fd90fc`, before this change | per module, the dual of the base commit and whether it is the Mor: `ZZ['x']` and `QQ['x']` take the product shape (`Mor(Free module on Coproduct of the family over NN, Integer Ring)` exists beside it), `ZZ**2` and `QQ(i)` take the Mor because their basis is finite. `Mor(M, R.regular_module())` carries a chosen generating set exactly when the basis is finite |
| `530-image-owner.log` | `0fd90fc` | the image of evaluation computed by the owner for `ZZ**2` at `(-6,9)` and at `0`: `Ideal (3)` and `Ideal (0) of Integer Ring`; `ZZ['x']` and `Zmod(8)` stop earlier, at `module_generating_set()` raising `has no chosen resolution` |
| `530-dual-resolutions.log` | `0fd90fc` | which modules carry a chosen resolution for their dual: `ZZ**2` (2 labels), `QQ(i)` (2), `ZZ['x']` and `QQ['x']` (aleph_0, and their duals carry none), `Zmod(8)` (the module has one, the dual `Mor(Z/8, Z)` does not) |
| `530-functionals-in-the-mor.log` | `0fd90fc` | the Mor model is complete for an infinite free module: the zero functional, the coordinate functional `e_0^*` and the constant functional are constructed from their values on `NN`, and evaluated at `e_0`, at `e_1` and at `2e_0+3e_7` (5) |
| `530-new-route-per-module.log` | this commit | the same seven objects through the new route: `ZZ**2` -> `(3)`, `(0)`; `QQ(i)` -> the unit ideal; `ZZ['x']` at `2x+2` -> `(2)`; `QQ['x']` at `x+1` -> the unit ideal; `Zmod(8)` -> the assertion naming the dual's missing presentation; `M_2(QQ)` -> the unit ideal over `QQ`, because a matrix ring's element is a module element over its coefficient ring |
| `530-answering-level.log` | this commit | which level answers `order_ideal`: `FramedFreeModules.ElementMethods` on `ZZ**2` and on the matrix ring, `Modules.ElementMethods` on `QQ(i)`, `ZZ['x']`, `QQ['x']` and `Zmod(8)`. So the module level is the level the change had to keep answering |
| `530-noncommutative-scalars.log` | this commit | over the noncommuting scalar ring `M_2(QQ)`: `dual_module()` raises `TypeError: the dual module Hom_R(...) is a left module only over a commutative ring ...`, and `order_ideal` on a free module over it raises `TypeError: the module order ideal requires a commutative scalar ring` -- from the framed level, which is the level that answers there, so the module level's deferral to `dual_module` has no reachable case to test |
| `530-before-iter-slot.log` | `7b23fc3^` | the `__iter__` slot before that commit, for `#500`'s last item: `ZZ['x'].__iter__` is a bound method of `OwnedRings.ParentMethods`, `isinstance(ZZ['x'], collections.abc.Iterable)` is **True**, and `iter` and `tuple` raise `TypeError` |
| `530-base-dual-is-the-product.log` | `0fd90fc` | the same probe on the base library: `ring.__iter__` is `None` and `isinstance` is **False** there (the slot change is in), the dual of `QQ**NN` is the product `Module over QQ on Product of the family over NN` and is not the Mor, and `(2x+2).order_ideal()` is still `Ideal (2)` |
| `530-lint-iterable-spelling.log` | this commit | the review's assertion `not isinstance(ring, collections.abc.Iterable)` written into a test and linted: `TL01 import collections.abc` and `TL03 isinstance(): introspection is not mathematics`. The test tree's own standard refuses that spelling, so `tests/rings/test_a_ring_states_no_enumeration_of_its_points.sage` records the measurement in its docstring instead of asserting it |
| `530-final-a.log` | this commit | the four lint-clean files of the change, with the repository's own addopts (test lint, suite budget, timing record): **8 passed in 1.02 s**. The run's record is `.timings/run-61797fba5100-20261115T071603Z.jsonl` and `.timings/junit-61797fba5100-20261115T071603Z.xml` |
| `530-final-b.log` | this commit | `tests/forms/test_all_ones_form_correlation.sage` (the correlation of the all-ones form, whose images are now points of the dual Mor) with the two lattice files that read `order_ideal` through `content`, repository addopts and `--no-test-lint`: **1 failed, 9 passed**; the failure is `test_index_two_sublattices_of_a_hyperbolic_summand`'s `ImportError: cannot import name 'nonprimitive_sublattice_classes'` from the indefinite port, the same id `tests/lattices/test_content_and_doubling.sage` fails with in `.tmp/qc-evidence/500d-lattices-tree.log` |
| `530-sweep-compared.log` | this commit against `0fd90fc` | `tests/modules tests/rings tests/forms tests/categories` run twice, once on the working tree and once on `git archive 0fd90fc` with the same test files: the FAILED/ERROR id sets are identical except the new test's dual-construction assertion, and the one count difference is that test. The `tests/forms` pair is in the same file, as are the per-directory timings that show the 256.71 s outlier |
| `530-sweep-new-ids.log`, `530-sweep-base-ids.log`, `530-forms-new-ids.log`, `530-forms-base-ids.log` | the same two runs | the sorted FAILED/ERROR ids the comparison reads. These four are extracted from the runs' output, not the output itself: they are the lines `comm` compares |

The probe sources are beside them (`530-probe-*.py`), session probes and not
library code, each printing the objects and the answering class it is cited for.

**After the merge of the remote main (`5d408ca`, the residue-transport perf branch).**

| log | commit cited | result |
| --- | --- | --- |
| `530-merged-a.log` | `97f9467` (this commit merged onto `5d408ca`) | the four lint-clean files of the change under the repository addopts: **8 passed in 0.93 s** |
| `530-merged-sweep-compared.log` | `97f9467` against `5d408ca` | `tests/modules tests/rings tests/forms tests/categories` on the merged tree and on the merge's own base, same test files: FAILED/ERROR ids identical except this change's new test assertion; 193 failed, 395 passed, 318 errors in 99.18 s against 194, 394, 318 in 105.20 s. The ~100 s pair also shows the earlier 256.71 s as a VM outlier |
| `530-merged-sweep-new-ids.log`, `530-merged-sweep-base-ids.log` | the same two runs | the sorted ids those two runs produced, extracted from their output |

## #529 — the reviewer's two regressions, and the repairs around them

`450a781` is the red commit: `tests/engineering/test_the_timing_record_names_each_stage.py` holds a test of the
stage wrapper under `cached_method` and a test of the package logger, and neither passes there. The repairs are the
commit after it: the stage moved into the bodies of `_vinberg_search` and `parabolic_completeness_decision`, the
timing logger made a child (`sage_extensions.timing`) that leaves `sage_extensions` alone, `current_commit`/`timing_directory`
asserted instead of falling back, the handler's write unwrapped, the plugin reading `config.option.report_log` and
`config.option.xmlpath`, and the dead paths deleted. Every run below is in the pinned image with the indefinite port
at `/work` and the checkout at `/repos/sage-extensions`.

| log | tree | result |
| --- | --- | --- |
| `issue529-review-red.log` | `450a781` | `${ARGS}` = `-p qc_sage_session -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates -q tests/engineering/`: **4 failed, 7 passed in 86.41 s** — `('Vinberg walk', 'Vinberg walk') == ('Vinberg walk',)`, `'a debug record' in ''`, and the two `test_polyhedral_engine_routes.sage` Julia/Hecke rows that fail at `5d408ca` too |
| `issue529-review-green.log` | this commit | the four tests of the file: **4 passed in 6.25 s** |
| `issue529-review-neighbours.log` | this commit | `tests/engineering/` plus the Vinberg-facet and setwise-stabilizer files, `--no-time-gates` with `test_lint` loaded: **2 failed, 17 passed in 94.08 s**, the two failures the same Julia/Hecke rows — the reindented bodies and the dropped nested stage moved no result |
| `issue529-review-real-addopts.log` | this commit | the test file under the repository's real addopts: **4 passed in 5.02 s**, and `.timings/` held `run-450a781380ab-20261115T073451Z.jsonl` and `junit-450a781380ab-20261115T073451Z.xml` — the names the addopts' own options give, read from those options |
| `issue529-review-logger-before.log` | `450a781` | the logger probe on the red commit: `pytest.log` holds `DEBUG probe.other` and nothing for `sage_extensions.categories.probe`; `logging.getLogger("sage_extensions")` reads `level 20 propagate False` |
| `issue529-review-logger-probe.log` | this commit | the same probe after the repair: `pytest.log` holds both `DEBUG sage_extensions.categories.probe` and `DEBUG probe.other`; the package logger reads `level 0 propagate True`, and `sage_extensions.timing` is the one at `20` |

The two workflow steps of ENV-03 are on `main` as `34b52a8`; the `if-no-files-found: error` that make a run without
a record fail its job are `results/issue529-upload-error.patch`, `git apply --check` clean against this tree, because
the connection's GitHub App may not update a file under `.github/workflows/`.
## #531: a finite ordered set hashes the points its equality compares

`FiniteOrderedSets.ParentMethods.__hash__` (`src/sage_extensions/categories/sets/finite_ordered_sets.py`) hashed
`hash(int(self.cardinality()))` while `__eq__` compares the cardinality and then the points in order, so every set
of one size was one dictionary key's bucket: #390's cache of `_lattice_subobject_spanning`, keyed by the span basis,
reached 1197 entries on 5 hash values and one lookup compared 5415 stored keys of 51 us each. The repair hashes the
ordered points with their own hashes (falling back to the cardinality only for a set carrying a point that refuses
a hash), which is the data equality reads and keeps Python's contract, "objects which compare equal have the same
hash value". The new file `tests/sets/test_a_finite_ordered_set_hashes_by_its_points.sage` states it: equal sets
hash equally, 200 distinct rank-two span bases on `U + U + <-2>` take 200 distinct hashes, and a dictionary keyed by
those sets reaches each entry without scanning the others.

| log | commit cited | result |
| --- | --- | --- |
| `issue531-red.log` | `da0fa12` (the red test alone) | the new file: **2 failed, 1 passed in 5.11 s**; `test_distinct_span_bases_of_one_rank_do_not_share_a_hash` fails `assert 1 == 200`, `test_a_span_basis_finds_its_own_cache_entry_without_scanning_the_others` fails `assert 2 != 2` |
| `issue531-lint-red.log` | the same tree | `test_lint` on the new file: **1 files, 0 findings** |
| `issue531-green.log` | the repair | the new file, now four tests: **4 passed in 7.06 s** |
| `issue531-hash-cost-before.log` | `da0fa12` | one hash of a lattice vector 3.2 us, of a rank-2 span basis 5.2 us, `__eq__` of two equal rank-2 span bases 61.9 us; 200 distinct span bases took **1 distinct hash value** |
| `issue531-point-hash.log` | `da0fa12` | two equal vectors built separately hash equally (-4024491175064079283 twice); a fifteen-point set 5.2 us to hash against 344.4 us to compare; an isometry is hashable |
| `issue531-sets-slice.log` | the repair | `tests/sets`, one pytest process: **29 failed, 131 passed in 21.00 s** |
| `issue531-sets-slice-base.log` | `da0fa12` (a clean worktree) | the same: **29 failed, 127 passed in 27.28 s**; the 29 FAILED ids are identical to the row above, so the 4 extra passes are the new file and nothing regressed |

The probes behind the two measurement rows are session probes and stay out of the tree: `issue531-hash-cost.py`
times a hash and counts distinct hash values over 200 span bases, `issue531-point-hash.py` hashes equal vectors
built two ways, and `issue531-subobject-scan-after.py` is #390's probe S with the hash of a finite ordered set
censused by caller and cardinality.

### #531: the rerun of #390's reproduction, and the T_Co row

| log | commit cited | result |
| --- | --- | --- |
| `issue531-subobject-scan-after.log` | the repair (`0066795`) | #390's probe S unchanged in its workload — 600 transports on `U + U + <-2>`, windows of 100 — with the hash censused: **600 transports in 32.0 s, mean 53.34 ms** (the record on `cef9c5d` is 104.7 s, mean 174.43 ms); `_lattice_subobject_spanning` cache **1187 entries on 1187 distinct hash values** (the record: 1197 on 5); the equality comparisons `subobject_on` makes are **1.0 per call in every window** (the record: 525.3 rising to 5415.4); process time per transport **14.89 ms in the first window against 12.16 ms in the last, ratio 0.82** — flat in the number of subobjects built, where the wall clock of this host (load 9) moves 35.15 to 22.46 ms with no trend |
| `issue531-hash-census-row.log`, `issue531-hash-census-row-large.log` | the repair | who hashes a finite ordered set inside the ambient `O(L)` plane row of `T_Co`: 1040 hashes of sets of at most 129 points in the first 150 s, then **one hash of a lazily enumerated 131072-point image set (points `_GeneralPresentedElement`), 20.6 s**, asked from `set_categories.py:1504 _finite_product` — its interning key is an index set this large. That is the one cost the repair adds (it was `O(1)` before) and it is the interning site's, not the hash's: no other consumer in this row hashes a set of more than 512 points |
| `issue531-tco-row.log` | the repair | the `Otilde(T_Co)` plane row capped at 520 s (probe J, `cap=520`, inner 560 s): **0 lifts, 0 planes transported; the whole cap inside the ambient `O(L)` plane row** (519.9 s of 520.0 s), so the transport's per-plane time is not reached |
| `issue531-tco-row-base.log` | `da0fa12` (a clean worktree) | the same probe and cap on the tree before the change: **also 0 lifts, 520.0 s in the same stage** — the row's setup, not this hash, is what keeps the transport from starting. The record's 138.5 s for that stage belongs to `484e4c52`; main has moved since. Against the record's **637 ms per plane** the transport therefore cannot be timed from the row on this tree |
| `issue531-lint.log` | the repair | `test_lint` on the new file: **1 files, 0 findings** |

The probes behind these rows are session probes and stay out of the tree: `issue531-subobject-scan-after.py` is #390's
probe S with the hash of a finite ordered set censused by caller and cardinality (and the process time of each
transport recorded beside its wall time); `issue531-hash-census-row.py` runs the ambient `O(L)` plane row of `T_Co`
under that census and prints it while the row runs, so a cap leaves the table behind.

### #531: the fallback removed, and what reads the hash

| log | commit cited | result |
| --- | --- | --- |
| `issue531b-repro.log` | `63797cf6f0` (main, before the change) | the defect the review names, reproduced: a mutable `vector([1, 2])` is unhashable and equals its immutable copy, `FOS((mutable)) == FOS((immutable))` is **True**, and the two hashes are **5300508251815892961** and **-2700102052487898497**; the same for a mutable and an immutable `identity_matrix(2)` (**5300508251815892961** against **8810013589662299418**) |
| `issue531b-red.log` | `63797cf6f0` (the red test alone) | the new test: **1 failed, 4 passed in 3.55 s**; `test_a_set_with_an_unhashable_point_is_unhashable` fails `DID NOT RAISE TypeError` on `hash` of the set holding the mutable point |
| `issue531b-formed-broken.log` | the FOS repair alone, before the quotient hash | what the strict hash exposes: `tests/categories/test_formed_vector_space_placement.sage` **1 failed in 2.42 s** — `A2` over `F_3`'s `radical()` raises, the span basis over `ZZ/(3)` cannot key `_lattice_subobject_spanning` |
| `issue531b-formed.log` | the tree of this push | the same file: **1 passed in 1.81 s** — the quotient class hashes, so the sparse vector, the span basis and the cache key do |
| `issue531b-census.log` | the tree of this push | who hashes a finite ordered set, counted: **127 hashes from three callers** — `lattices.py:3976 subobject_on` 104, `set_categories.py:1504 _finite_product` 21, `modules.py:816 tensor_product` 2 — over `A2 (x) F_3`'s radical, 400 `subobject_on` calls on `U + U + <-2>` and one product; **4 refusals, all at `subobject_on`**, on a one-point span basis of a `_SparseFreeModuleElement` over `ZZ/(3)` |
| `issue531b-green.log` | the tree of this push | the two new test files: **7 passed in 2.70 s** |
| `issue531b-sets-slice.log`, `issue531b-sets-slice-base.log` | the tree of this push; `63797cf6f0` (a clean worktree) | `tests/sets`: **29 failed, 132 passed in 8.97 s** against **29 failed, 131 passed in 8.46 s**; the FAILED id sets are identical, so the extra pass is the new file |
| `issue531b-neighbours.log`, `issue531b-neighbours-base.log` | the same two trees | `tests/categories tests/objects`: **174 failed, 272 passed in 55.75 s** against **176 failed, 270 passed in 50.71 s**; **no FAILED id is the changed tree's alone**, and the two that are the clean worktree's alone pass here, so they are this host's flakes |
| `issue531b-rings.log`, `issue531b-rings-base.log` | the same two trees | `tests/rings`: **74 failed, 260 passed in 46.51 s** against **74 failed, 260 passed in 55.63 s**, the same FAILED ids |
| `issue531b-lint.log` | the tree of this push | `test_lint` on the three touched test files: **3 files, 138 findings**, all 138 in `test_products_and_coproducts_of_finite_and_countable_sets.sage` and in the codes it already carried (TL01, TL02, TL03, TL04, TL08, TL09, TL10); the two new files carry none |

The probes behind the census and the reproduction stay out of the tree: the reproduction builds the mutable and immutable Sage point pairs; the census wraps
`FiniteOrderedSets.ParentMethods.__hash__`, records the calling frame's file, line and function, and re-raises so a refusal is counted where it happens.
## #529, third review — one record per run, an input named without rendering it, and the workflow's record

The reviewer's findings on `63797cf`, and what each one measured. `${ARGS}` is
`-p qc_sage_session -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates -q`.

| log | tree | result |
| --- | --- | --- |
| `issue529-engineering-red.log` | `63797cf`'s `timing_record.py` and `_named` | `${ARGS} tests/engineering/test_the_timing_record_names_each_stage.py`: **2 failed, 3 passed in 5.28 s** — the `-n 2` run kept `('report',)` against the one `('junit', 'report')` a run writes: a worker's copy of the controller's report log, and no JUnit file at that moment; and the four stage records carried `Integral lattice of rank 5 and signature (2, 3)`, the signature being the diagonalization the record was paying for |
| `issue529-engineering-tests.log` | `5e15399` | the same command: **5 passed in 5.26 s**, with `test_lint` loaded and the session's run, so the in-session lint reports nothing |
| `issue529-engineering-all.log` | `5e15399` | `${ARGS} tests/engineering/`: **2 failed, 11 passed in 33.44 s**; both failures are `test_polyhedral_engine_routes.sage`'s `u.basis()` rows |
| `issue529-base-polyhedral.log` | clean worktree `63797cf` | `test_polyhedral_engine_routes.sage` alone: **2 failed in 1.16 s**, the same two ids, `AttributeError: ... has no attribute 'basis'` — pre-existing, not this change's |
| `issue529-readme-record.log` | `5e15399` | the command `results/issue529-readme-record.patch` installs, `pytest --doctest-glob=README.md README.md`: **1 passed in 0.39 s**, `time gates on: star import 0.32 s (ceiling 3 s)`, and `.timings/` afterwards holds `junit-5e15399a8bae-20261115T081817Z.xml` and `run-5e15399a8bae-20261115T081817Z.jsonl` — the two files the upload step names |
| `issue529-lint-base.log` | `63797cf` | `python -m sage_extensions.testing.test_lint tests/engineering/test_the_timing_record_names_each_stage.py`: **4 findings, all TL13** for the names `tests/engineering/conftest.py` binds in `pytest_configure` — the standalone entry point does not run that hook, so this directory is not lintable through it; at `5e15399` the same command reports the same four plus one for the new test's `kept_test_run`, and the applicable check is the in-session lint the row above carries |

The workflow change is `results/issue529-readme-record.patch`, not history: the connection's GitHub App may not
update a file under `.github/workflows/`. `git apply --check` passes against `63797cf`, and the command the patch
installs is the one `issue529-readme-record.log` runs. ENV-03's sentence that named `results/issue529-upload-error.patch`
as the thing to install with `git apply` was stale — the change landed as `c68730d47` — and that file is deleted in
this commit.
## #500 and #530, sixth round (added 2026-11-15)

| log | commit cited | result |
| --- | --- | --- |
| `500e-red.log` | `27d76f3` (the test and the module-level rewrite, with `refine.py` at its base commit) | `tests/modules/test_the_order_ideal_of_a_ring_element_over_its_base_ring.sage` plus the categories file: **3 failed, 3 passed in 2.65 s**. The new test and both polynomial tests stop at the stated hypothesis: `Modules.ElementMethods.order_ideal` is reached, its dual `Mor(Free module on Coproduct ... , Integer Ring)` holds no generating family, and the value is not computed. This is the red state the test was committed in |
| `500e-answering-level-base.log`, `500e-answering-level-tree.log` | base `9d278f5`, then the tree with the `refine.py` repair (committed as `6578c33`) | per object (`ZZ`, `QQ`, `RR`, `CC`, `ZZ**2`, `QQ**2`, `ZZ['x']`, `QQ['x']`, `QQ(i)`, `Zmod(8)`, `GF(4)`, `M_2(QQ)`, its regular module, `Lattices(ZZ)(2)`): the class that declares each of `__truediv__`, `__rmul__`, `__add__`, `order_ideal`, `__iter__`, `adic_completion`, `content`, `to_vector`, `primitive_part`, for the parent and for the element class. The only differences the repair makes are `order_ideal` and `primitive_part` on `QQ(i)`, `ZZ['x']` and `QQ['x']`: from `Modules.ElementMethods` and `Modules.Free.ElementMethods` to `FramedFreeModules.ElementMethods`. Division, the scalar action, iteration, the completion, the content and the coordinates are unchanged on all fourteen, and `M_2(QQ)`'s `e12/e12 = e11`, `ZZ**2`'s `v/2`, `RR(3)/2`, `CC(3)/2` and `tuple(Zmod(8))` print the same on both trees |
| `500e-green.log` | `27d76f3` + `6578c33` | the three files of the repair with `-p qc_sage_session`: **8 passed in 1.94 s** |
| `500e-tests.log` | `6578c33` with the working-tree changes that are `6a24ab7` and `618fb82` | the five files of this round under the repository's own addopts (`test lint`, `suite_budget`): **13 passed in 1.42 s** |
| `500e-lattice-test.log` | the same tree | `tests/lattices/test_lattice_semantic_api.sage` alone: **4 passed in 1.80 s** |
| `500e-sweep-tree-ids.log`, `500e-sweep-base-ids.log`, `500e-sweep-compared.log` | tree `6578c33` + the two following commits' content (7 files dirty), base `9d278f5` (clean) | `tests/modules tests/categories tests/rings tests/forms`, one pytest process each: **265 failed, 642 passed in 410.06 s** against **265 failed, 641 passed in 423.47 s**. The FAILED/ERROR id sets are identical -- **0 ids only on either side**; the one count difference is this round's new test |
| `500e-lattice-tree-ids.log`, `500e-lattice-base-ids.log` | the same two trees | the seven `tests/lattices` files that read the dual, the order ideal or the content: **2 failed, 21 passed** on the tree against **3 failed, 20 passed** on the base. The one id only on the base is the rewritten test's old name, `test_the_infinite_rank_dual_is_the_product_and_evaluates_by_projections` |
| `500e-lattice-batch-killed.log` | the same tree | 40 `tests/lattices` files from `test_arithmetic_applications` on, cut by the inner 550 s cap at 79% of the batch's tests with the ids unprinted; peak tree RSS 5880 MiB (julia 5168 MiB). Recorded as an unfinished run, not as a comparison |
| `500e-lattice-L2-unfinished.log` | the same tree and the base | a second seven-file `tests/lattices` batch whose tree run never reached its summary and whose base run was cut at its first line. Unfinished; no ids |

`tests/lattices` is not run as one directory on this host: the 40-file batch above is the
measurement that says so, at 5.9 GiB and past 550 s. The comparison this round can
stand on is the seven files that read the changed operations, and the four directories
of the sweep.

The merge with main (`67f856c`) was checked with the five files of this round under the
repository addopts: `500e-merged-tests.log`, **13 passed in 3.61 s**. The four-directory
sweep on the merged tree was started and cut by the inner 550 s cap with no ids printed
(`merged-sweep.log`, session-only, not published): the VM was carrying other work at that
moment, so the merged tree has the five files' run and not a directory comparison.

One collateral level move the repair makes is `primitive_part` on `QQ(i)`, `ZZ['x']`
and `QQ['x']` (from `Modules.Free.ElementMethods` to the framed level). Two probes
record what its value does: `500e-primitive-part-values.log` (the framed reading's
value is the one the answering method returns on `ZZ['x']` at `2x+2` and at
`6x^2+9x`, `x + 1` and `2*x^2 + 3*x`) and `500e-primitive-part-over-qq.log` (over
`QQ`, both implementations and the answering one raise the same `TypeError:
integer content requires a free module over ZZ`, so the move changes no answer
there).

### #531 round 2: the quotient hash's canonical representative, and the interning key

| log | commit cited | result |
| --- | --- | --- |
| `issue531r2-probe-engine.log` | `ad28ef0116` | the engine of a quotient and its representative: `ZZ[x,y]/(4, 6x)` has engine `QuotientRing_generic` over `Integer Ring`, and its one class of `x` and `3x` has the representatives `xbar` and `-xbar` with engine hashes **3744985340818229357** and **-3744986470996619882**; `QQ[t]/(t^2+1)` is not a `QuotientRings` object at all (it is a free module on `{1, t}`, with no `_preamble_engine_ring`) |
| `issue531r2-red.log` | `ad28ef0116` (the red test alone) | the new ZZ test: **1 failed, 2 passed in 2.19 s**, `DID NOT RAISE TypeError` on the hash of the class of `x` |
| `issue531r2-gate.log` | this tree | the quotient file, the formed-module file and the finite ordered set file: **9 passed in 3.06 s** — `ZZ/(3)` still hashes, so `A2` over `F_3`'s `radical()` still returns, and the class over `ZZ` refuses a hash |
| `issue531r2-product-base.log` | `ad28ef0116` (a clean worktree) | what round 1's restated test had narrowed: the index set of `[0], [1]` has no hash, and `Sets().product(family)` raises `TypeError: … FiniteOrderedSets.parent_class is not hashable and does not implement _cache_key()` |
| `issue531r2-product.log` | this tree | the same family: `Sets().product(family)` returns **Product of the family over {[0], [1]}**, and a separately built equal family returns **the same object** |
| `issue531r2-sets-slice.log`, `issue531r2-sets-slice-base.log` | this tree; `ad28ef0116` (a clean worktree) | `tests/sets`: **29 failed, 133 passed in 8.23 s** against **29 failed, 132 passed in 8.96 s**, the same FAILED ids (the extra pass is the new SET-05 test; the restored list-label test passes on both) |
| `issue531r2-rings.log`, `issue531r2-rings-base.log` | the same two trees | `tests/rings`: **74 failed, 263 passed in 39.92 s** against **74 failed, 262 passed in 40.69 s**, the same FAILED ids (the extra pass is the new ZZ test) |
| `issue531r2-neighbours.log`, `issue531r2-neighbours-base.log` | the same two trees | `tests/categories tests/objects`: **174 failed, 272 passed in 49.41 s** against **176 failed, 270 passed in 48.14 s**; no FAILED id is this tree's alone, and the two that are the clean worktree's alone are the same two that passed on round 1's tree, so they are this host's flakes |
| `issue531r2-lint.log` | this tree | `test_lint` on the three touched test files: **3 files, 144 findings**, all in `test_products_and_coproducts_of_finite_and_countable_sets.sage` and in the codes it already carried; the two files of this change carry none |

The product probe stays out of the tree: it builds the family over `finite_ordered_set(([0], [1]))` twice, reports whether the index set hashes, and compares the two products by identity.
## #529, third review — one run one record, a caller's name for its input, and the README as a recipe

The reviewer's three findings on `fc4f322`, and what each one measured.  `${ARGS}` is
`-p qc_sage_session -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates -q`.

| log | tree | result |
| --- | --- | --- |
| `issue529c-red.log` | `fc4f322`'s stamps | `${ARGS} tests/engineering/test_the_timing_record_names_each_stage.py -k 'two_runs or parallel'`: **1 failed, 1 passed in 9.98 s** — `assert ('junit', 'report') == ('junit', 'junit', 'report', 'report')`: two probes started before either was waited on kept one record between them, because both stamped to the second and the second copy landed on the first |
| `issue529c-tests.log` | `ad28ef0` | the timing-record file and the suite-plugin file: **8 passed in 9.91 s**, with `test_lint` loaded; the two-run test now sees four files, two stamps, and each report log naming only its own test, and the `-n 2` test checks the probe's exit status |
| `issue529c-engineering-all.log` | `ad28ef0` | `${ARGS} tests/engineering/`: **2 failed, 12 passed in 30.43 s**; both failures are `test_polyhedral_engine_routes.sage`'s `u.basis()` rows |
| `issue529c-plane-names.log` | `ad28ef0` | a probe over the plane row of `U + U + <-2>`: the names the stages now record — `rank-2 subobject row of the rank-5 lattice on generators 0, 1, 2, 3, 4`, `1 ambient plane representative of …`, `a rank-2 subobject of …` — and the row returns 1 orbit; no stage of this row printed an object, and `_named` inspected none |
| `issue529c-neighbours.log` | `ad28ef0` | the Vinberg and small-indefinite line-row files, which hold the call sites: **1 failed, 9 passed in 25.27 s**, the failure `test_isotropic_parabolic_restriction.sage`'s `kernel.group_generators()` `ValueError` |
| `issue529c-base-parabolic.log` | clean worktree `fc4f322` | the same file alone: **1 failed, 1 passed in 7.25 s**, the same test id and the same `ValueError` at `set_categories.py:4463` — pre-existing, and not on a path this change touches |
| `issue529c-just-readme.log` | `ad28ef0` | `SAGE_BIN=/sage/.venv/bin/sage just readme`: **1 passed in 0.39 s**, and `.timings/` holds `junit-ad28ef011653-20261115T090006896917Z-1810853.xml` and `run-ad28ef011653-20261115T090006896917Z-1810853.jsonl` — the recipe the workflow step runs, and the record it leaves |

The README workflow step is `results/issue529-readme-record.patch`, not history: the connection's GitHub App may
not update a file under `.github/workflows/`, and `git apply --check` passes against `ad28ef0`.

## #528 (part of #390): the Otilde(T_Co) plane row's setup stages, each timed alone

The row is `NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)`.
Its setup is measured one stage per run, never the row: `issue390-stage-alone.py` builds
only the inputs a stage takes, times the stage, and stops, and prints one `RESULT` line.
Two trees: **base** `a71272add96485c3e6ceeda07572bf40c5b2b5c0` and **main**
`3a1964060ab55a6b09207f0ceeff67960fb3ef9b`. Every run carries `calib=`, the wall time of
a fixed workload (a 300000-iteration integer loop plus one GAP `Order(SymmetricGroup(8))`),
because this VM is shared: the same `group` stage measured 1.81 s at load 1.0 and 6.36 s at
load 11.6. `calib` is the run's CPU-share normaliser and the ratios below are quoted
against it; a wall-clock number without its `calib` is not comparable across runs.
`input=direct` makes the plane's stages take a primitive isotropic plane built from the
lattice's own vectors (bounded search, `RESULT`-logged separately) instead of the port's
first ambient class, because on main that input is what does not return.

| log | commit cited | result |
| --- | --- | --- |
| `issue528-stage-alone.py` | base `a71272add9`, main `3a1964060a` | the probe: one setup stage per run (`stage=lattice|group|ambient_row|direct_plane|parabolic|complete|index|disc_images|walk`) or `profile=<stage>`, a timing proxy on `libgap` in every loaded `sage_extensions` module, the quotient's own call sites wrapped where they are defined so the caches stay in force, exclusive stage time with nested sub-stages subtracted, inputs charged to separate `input:` rows, a `/proc/self/status` sampler, a `/proc/loadavg` sampler and the `calib` control. `profile=` adds `cProfile`, the heaviest-caller chain of the top five entries, a 0.5 s main-thread stack sampler (so a run the cap stops still names where it was), and the construction/computation split by own time. `input=direct` and `cap=` are the other two switches |
| `issue528-base-lattice.log` | base `a71272add9` | `stage=lattice`: **0.03 s**, `calib` 0.135 |
| `issue528-main-lattice.log` | main `3a1964060a` | `stage=lattice`: 0.06 s, `calib` 0.325 -- **0.02 s at the base's CPU share: flat** |
| `issue528-base-group.log` | base `a71272add9` | `stage=group`, `lattice.stable_orthogonal_group()`: **2.66 s**, `calib` 0.136, peak 405 MiB |
| `issue528-main-group.log` | main `3a1964060a` | `stage=group`: 2.30 s, `calib` 0.161 -- 1.94 s normalised: **flat** |
| `issue528-base-direct-plane.log` | base `a71272add9` | `stage=direct_plane`, the bounded isotropic-plane search in the lattice's own coordinates: **0.18 s**, `calib` 0.163 |
| `issue528-main-direct-plane.log` | main `3a1964060a` | `stage=direct_plane`: 0.19 s, `calib` 0.167: **flat** |
| `issue528-base-ambient-row.log` | base `a71272add9` | `stage=ambient_row`, `O(T_Co).isotropic_orbit_representatives(2)`: **54.18 s**, `calib` 0.165, peak 577 MiB, returns 1 plane |
| `issue528-main-ambient-row.log` | main `3a1964060a` | `stage=ambient_row` capped at 300 s: **did not return**, `calib` 0.165 (the base's own share) -- **>= 5.5x the base, and the only stage that moved by more than 1.6x** |
| `issue528-base-parabolic.log` | base `a71272add9` | `stage=parabolic input=direct`, `plane.parabolic_stabilizer_generators()`: **27.21 s**, inputs (lattice, direct plane) 0.23 s, `calib` 0.163 |
| `issue528-main-parabolic.log` | main `3a1964060a` | `stage=parabolic input=direct`: 27.70 s, `calib` 0.169 -- 26.7 s normalised: **flat** (with the port's own plane as the input the stage is never reached on main: the input row alone exceeds the run's cap) |
| `issue528-base-complete.log` | base `a71272add9` | `stage=complete input=direct`, `plane.is_parabolic_complete()`: **37.48 s**, `calib` 0.163 |
| `issue528-main-complete.log` | main `3a1964060a` | `stage=complete input=direct`: **55.36 s**, `calib` 0.153 -- 59.0 s normalised, **1.57x the base**: the second-largest move in the table and the largest in any stage that does not touch the ambient row |
| `issue528-base-index.log` | base `a71272add9` | `stage=index`, `quotient.index()` (= `image_order`): **114.67 s**, `calib` 0.163, inside it `_ambient_generators` 71.9 s and `ambient_discriminant_images` 34.0 s |
| `issue528-main-index.log` | main `3a1964060a` | `stage=index`: 112.54 s, `calib` 0.157 -- 116.8 s normalised: **flat** |
| `issue528-base-disc-images.log` | base `a71272add9` | `stage=disc_images`, `quotient.ambient_discriminant_images()`: **108.25 s**, `calib` 0.162, inside it `_ambient_generators` 71.9 s |
| `issue528-main-disc-images.log` | main `3a1964060a` | `stage=disc_images`: 111.73 s, `calib` 0.165 -- 109.7 s normalised: **flat** |
| `issue528-base-walk.log` | base `a71272add9` | `stage=walk`, the coset action, the closure and GAP's breadth-first walk up to the first lift, its caches pre-warmed: **152.94 s** with 364.43 s of pre-warming inputs (`_sign_descent_rank`, `_im_rho_engine_and_section`, `ambient_discriminant_images`), `calib` 0.168, peak 1448 MiB |
| (no log) the main walk stage | -- | *not produced*: its input is the port's first ambient plane, and on main that input does not return inside a run's ten minutes, so the stage was not reached. The table quotes the base's line and says so |
| `issue528-bisect-ambient-row.log` | base `a71272add9` .. main `3a1964060a` | `git bisect run` on the one stage that moved, `ambient_row`, with the predicate `wt528_bisect_stage.sh`: time the stage with its own cap at the threshold and exit 1 at or above 300 s, 0 below, 125 on a raise. **5 steps, 24 -> 12 -> 5 -> 2 -> 0 revisions**, every step undecided at 300 s, and **`204ffbb96ef6f6502e126e93f671628b823c988f` is the first bad commit** -- `fix: the integral lift locus reads its cosets in the section's own Smith coordinates (#405, #452)`; the probe's per-step logs carry each commit's `calib` (2.17-4.73), so no step's verdict is a load artifact |
| `issue528-profile-base-lattice.log`, `-main-lattice.log` | base / main | `profile=lattice`: construction **0.02 s (11.8 %)** of a 0.14 s stage on the base and 0.01 s (10.6 %) of 0.09 s on main |
| `issue528-profile-base-group.log`, `-main-group.log` | base / main | `profile=group`: construction 2.09 s (19.9 %) of 10.49 s and 2.01 s (21.1 %) of 9.54 s; the largest construction entries are `category.py:436 __classcall__` and `owned_category.py:1102 is_subcategory`, the largest computation ones `lattices.py:5814 b` (`_evaluate_gram`) |
| `issue528-profile-base-parabolic.log`, `-main-parabolic.log` | base / main | `profile=parabolic input=direct`: construction 10.14 s (11.3 %) of 89.57 s and 8.75 s (11.4 %) of 76.55 s; the top construction entries are `category.py:436 __classcall__` 2.44 s and `set_categories.py:6716 _element_constructor_` 2.42 s, the top computation `lattices.py:5814 b` cum 33.46 s over 16248 calls through `_evaluate_gram` |
| `issue528-profile-base-direct-plane.log`, `-main-direct-plane.log` | base / main | `profile=direct_plane`: construction 0.05 s (7.9 %) of 0.62 s and 0.08 s (10.5 %) of 0.80 s |
| `issue528-profile-base-ambient-row.log` | base `a71272add9` | `profile=ambient_row`, 168.1 s under the profiler: construction **30.07 s (18.1 %)**, computation **0.20 s (0.1 %)**, other **135.74 s (81.7 %)**; the 0.5 s stack sampler's most frequent leaf frames are `category.py:693 __contains__` (16), `modules.py:244 <genexpr>` (13), `ring_foundation.py:5605 _backend` (11), `ring_foundation.py:6508 _element_constructor_` (9) |
| `issue528-profile-main-ambient-row.log` | main `3a1964060a` | the same stage, cap 300 s, stopped: construction **54.81 s (18.3 %)**, computation **0.17 s (0.1 %)**, other **244.95 s (81.6 %)** -- the same proportions as the base at 1.8x the rate, so the doubling is not a change of what the row does but of what each step costs. The heaviest own-time entries are `isinstance` 19.8 s, `objects.py:158 __contains__` 16.8 s, `ring_foundation.py:6594 _from_engine_element` 16.7 s, `5683 _operand_in_ring` 12.7 s, `category.py:693 __contains__` 9.3 s, `2174 _fraction_equality_status` 8.3 s own / 91.4 s cumulative; the top call's chain is `primitive_covering_vectors (eichler.py:980) <- __init__ (eichler.py:852) <- _model (recursive.py:840) <- primitive_vector_classes (recursive.py:1754) <- _computed_isotropic_vector_classes (isotropic_induction.py:78) <- isotropic_vector_classes (isotropic_induction.py:68)`, and the last sampled stack is `ring_foundation.py:5930 _div_ <- module_morphisms.py:245 solve <- _preimage_or_none <- _preimage_through_the_extension_framing <- factor_through_or_none <- lattice_morphisms.py:1511 is_integral_on <- recursive.py:1716 _isotropic_pointed_isometry` |
| `issue528-profile-main-index.log`, `-main-complete.log` | main `3a1964060a` | the same treatment for `index` and `complete input=direct`: construction **43.39 s (17.5 %)** of 247.59 s and **9.30 s (15.0 %)** of 62.16 s, computation 0.62 s (0.3 %) and 0.18 s (0.3 %). For `index` the largest construction entries are `category.py:436 __classcall__` 9.58 s, `set_categories.py:6716 _element_constructor_` 7.19 s over 191 s of cumulative calls, `ring_foundation.py:6623 _element_constructor_` 4.93 s and `owned_category.py:1102 is_subcategory` 2.76 s |
| `issue528-product-2p17.py` | main `3a1964060a` | the probe for the reviewer's lead: every call of `Sets.SubcategoryMethods._finite_product`, of `_cartesian_product_of_finite_family` (the cached key included) and of `_cartesian_product_of` inside the ambient plane row, each with the cardinality of the index set it was handed, its own time and the innermost library frames |
| `issue528-main-product-2p17.log` | main `3a1964060a` | the ambient `O(L)` plane row, full and decided, **114.7 s**: **2093 product calls, and every index set has cardinality 2 (2030 calls) or 3 (63 calls) -- not one of 2^17**, so the lead's 131072-point `_finite_product` is not on this row's route in this tree; the top product call is `modules.py:5992 _tensor_label_set` inside `_module_tensor_product_with_data` at 0.002 s. The largest index set the row hands any product is 3, so `_finite_family_key`'s `tuple(family)` has nothing to enumerate here |
| `issue528-spanning-scan.py` | main `3a1964060a` | the probe for the per-plane construction `25eea761af` measured at 3.93 ms early and 126.82 ms after 2005 planes: one cold `_lattice_subobject_spanning` per call (a distinct basis each time, because the function is a `cached_function` -- 1480 *repeated* calls cost 0.04 s in total, a dictionary lookup), the four steps timed separately (`_module_subobject_constructor_data`, the fresh framed module, the `rank^2` Gram tensor, and the placement through `_form_module_from_bilinear_computation` -> `_form_module_categories` -> `_construct_form_module` -> `_module_with_structure`), the populations a growth could scan, and `cProfile` over early and late blocks |
| `issue528-main-spanning-scan.log` | main `3a1964060a` | `U + U(2) + <-2>`, rank 5, **1200 calls, 1180 cold constructions in 2.45 s = 2.08 ms a call**, and the cost does **not** grow: first 100 calls 2.64 ms, last 100 calls 1.99 ms (ratio 0.75). What one call computes: the support union of the two basis vectors and a coordinate matrix (`_module_subobject_constructor_data` 0.561 ms), a fresh framed free module on the two labels (`_fresh_free_module_on` 0.562 ms, two calls a construction), the `rank^2 = 4` restricted Gram values through `lattices.py:5800 _evaluate_gram` and the tensor (`4a` 0.716 ms), then the placement (`4` 1.035 ms), of which the category join `_owned_join_as_tuple` and `is_subcategory` are 0.038 ms (`4b`) and `_object_of` the rest. It **scans nothing that grows**: the module's generating set stays 5 and the `__classcall__` caches the probe could read stay empty or absent over 1200 constructions. So the row's 126.82 ms a call after 2005 planes is not this function's own algorithm on a small input, and the next run has to repeat the same cold-basis measurement on `T_Co` itself to name which of the four steps grows there |

## #500's review of `6578c33`, sixth round's follow-up (added 2026-11-15)

| log | commit cited | result |
| --- | --- | --- |
| `501-red-torsion-annihilator.log` | `27d76f3` (the order before the repair), with the new test copied in | `tests/categories/test_the_refined_category_answers_with_its_own_operation.sage`: **1 failed, 3 passed in 0.80 s**, at `annihilator()` -- `AssertionError: the annihilator Ann_R(...) over Integer Ring has no algorithm ...`. Red where the values changed, so the test states a change and not a tautology |
| `501-provider-order.log` | this round's tree, `probe501a.py` | 25 objects x 3 attributes: the provider sequence of every one, and whether any pair is ordered both ways. **0 pairs ordered both ways, 0 sequences changed** when the reverse conjunct of `_precedes` is deleted |
| `501-answering-level.log` | this round's tree, `probe501b.py` | the class declaring each of twelve operations, for the parent and the element class, on the same 25 objects: identical to `500e-answering-level-tree.log`'s list, so the three deletions in `algebras.py` moved no answer |
| `501-tests.log` | this round's commits | the five files of #500/#530 under the repository addopts: **14 passed in 1.34 s** |
| `501-algebras-tree.log`, `501-algebras-b61.log`, `501-algebras-compared.log`, `501-algebras-ids.log` | this tree and `b61feeb`, both with the change | `tests/algebras`, one pytest process each: **45 failed, 44 passed, 124 errors in 32.78 s** against **45 failed, 44 passed, 124 errors in 32.64 s**, **0 FAILED/ERROR ids only on either side**. The same directory on `27d76f3` has 21 ids fewer, so those 21 are main's and predate this round: their root exception on `test_power_algebras.sage` is `RecursionError: maximum recursion depth exceeded` through `objects.py:172`, `set_categories.py:532` and `ring_foundation.py:6651`, reached while an exterior or divided power algebra of a torsion module is built. Open, and not repaired here |

## #531 round 4: the quotient hash's cover, and the interners' key

The tree is `ca9b5a8` unless a row names another; the base is a clean worktree at
`76b4449`, the commit the round started from. Port `991b88b0`. Each run is one
pytest process in the pinned image with the repository's own addopts; the
products file carries its own pre-existing lint findings, so the three
directory runs carry `--no-test-lint`, and the two clean test files are also run
with the gate on (`issue531r4-lint-gate.log`).

| log | commit cited | result |
| --- | --- | --- |
| `issue531r4-red-quotient.log` | `76b4449` with the test file of `ab14fef` | `tests/rings/test_a_quotient_class_hashes_by_its_class.sage`: **1 failed, 4 passed in 0.24 s**; the failure is `test_classes_of_a_laurent_quotient_refuse_a_hash` at `:84: Failed: DID NOT RAISE TypeError` |
| `issue531r4-green-quotient.log` | `ab14fef` with `9fd14a2` | the same file: **5 passed in 0.21 s** |
| `issue531r4-red-sets.log` | `76b4449` with the test file of `ca9b5a8` | `tests/sets/test_products_and_coproducts_of_finite_and_countable_sets.sage`: **8 failed, 27 passed in 1.98 s**, of which the two this change states are red there -- `test_finite_family_hash_does_not_require_hashable_index_labels` and `test_equal_families_of_points_with_a_hashable_and_an_unhashable_form_hash_alike` -- and six are main's own |
| `issue531r4-sets.log` / `issue531r4-sets-base.log` | `ca9b5a8` / `76b4449` | `tests/sets`: **29 failed, 135 passed in 6.45 s** against **29 failed, 133 passed in 7.20 s**, the 29 FAILED ids identical; the two extra passes are the two tests this change adds |
| `issue531r4-rings.log` / `issue531r4-rings-base.log` | `ca9b5a8` / `76b4449` | `tests/rings`: **76 failed, 263 passed in 44.30 s** against **76 failed, 261 passed in 43.65 s**, FAILED ids identical |
| `issue531r4-categories-objects.log` / `-base.log` | `ca9b5a8` / `76b4449` | `tests/categories` + `tests/objects`: **183 failed, 264 passed in 56.19 s** against **183 failed, 264 passed in 54.87 s**, FAILED ids identical |
| `issue531r4-lint-gate.log` | `ca9b5a8` | `tests/rings/test_a_quotient_class_hashes_by_its_class.sage` + `tests/sets/test_a_finite_ordered_set_hashes_by_its_points.sage` with the test lint in force: **10 passed in 1.80 s**; `test_lint` on the rings file alone: **1 files, 0 findings** |
| `issue531r4-intern-count.log` / `-base.log` | `5277c4e` / `76b4449` | 200 distinct products over one four-point label set, with `IndexedFamily.__eq__` wrapped by the session probe: **0 family comparisons, 0.2827 s** against **20100 comparisons, 2.2002 s**, and the store's own count **0 families in the cardinality buckets against 201**. The intermediate tree `ca9b5a8`, whose bucket also held the keyed families, made **19900 comparisons in 2.1957 s** -- the count is what found that, and no log of it is published because the run wrote over itself |

The probe that named the engines is a session probe and stays out of the tree: it
prints, for each quotient, its engine's class, `cover_ring()`, `base_ring()` and
whether `_engine_quotient_reduction_is_canonical` admits it, which is how the
table in `9fd14a2`'s message was read.  A second session probe was meant to
build a mutable Sage vector and its immutable copy -- equal, one hashing -- as
the point pair the family hash must not separate; it stopped at
`NameError: name 'vector' is not defined` under the session import, so no such
row is claimed, and the test uses a tuple and a subclass of it with no hash
instead.  The probe behind the comparison counts (`issue531r4-intern-count.log`)
builds 200 products over one label set and wraps `IndexedFamily.__eq__` to count
the comparisons; it is the same file on both trees.
## #528, second round: are the lift tests more numerous, or dearer?

`204ffbb96e` corrected the integral locus' Smith reading *and* replaced its per-class test: the
old test formed, per class, `eichler_transvection_matrix(f, s(a)) * base_images` with
`base_images` computed once for the lattice; the new one composes the owned isometries,
`eichler_transvection(f, s(a)) * base_point()`, and asks the composition for its
`integral_restriction`. The two explanations have different owners, so one probe counts both.

| log | commit cited | result |
| --- | --- | --- |
| `issue528-lift-test-cost.py` | base `a71272add9`, `204ffbb96e` | the probe: one file, run unchanged on both trees. It calls the same public entry at both, `IsotropicReductionLiftTorsors.integral_parameter_classes()`, on the commit's own control `U(2) + U(2) + <2>` (the one where #405 reproduced: 64 classes reported, 32 lifting), wraps by name the calls the test can make (`eichler_transvection`, `eichler_transvection_matrix`, `integral_restriction`, `is_integral_on`, `_preimage_or_none`, `factor_through_or_none`, `_fraction_equality_status`, `_lift_at`, `parameterization`, `base_point`, `_target_section`) and reports a name a tree does not have as absent rather than as zero. Its `row` mode runs the same instrumentation over T_Co's ambient plane row, capped, and prints the counts whether the row returns or not |
| `issue528-lift-cost-base-control.log` | base `a71272add9` | the control: locus **0.042 s**, **2** classes tested, each by `eichler_transvection_matrix` -- **20.97 ms a test**, no composition, no `integral_restriction` |
| `issue528-lift-cost-204ffbb-control.log` | `204ffbb96e` | the same control: locus **0.165 s**, **8** classes tested, each by `_lift_at` (composition) -- **20.6 ms a test**. On the rank-5 control the count went up 4x and the per-test cost did **not** move: the control alone would have said the cost is owed |
| `issue528-lift-costs-base-row.log` | base `a71272add9` | T_Co's ambient plane row, **61.3 s and decided**: **1536 lift tests**, `eichler_transvection_matrix` 3.43 s in total, **2.23 ms a test**, `parameterization` 0.63 s over 5 calls |
| `issue528-lift-costs-204ffbb-row.log` | `204ffbb96e` | the same row, capped at 240 s and **not returned**: **1362 lift tests**, `_lift_at` **183.67 s of the 240** -- **134.9 ms a test**, of which `eichler_transvection` is 40.29 s (29.6 ms), so **105 ms a test is the composition and the integral restriction**. The count is the same order as the base's 1536 (the base finished its whole row with it); the per-test cost is **61x**. The question is decided for dearer tests, and the rank-5 control was the wrong input to decide it on |

## #528, the repair: the lift test reads the lift's matrix, with its datum built once

The decision made the cost per test, not owed: `_lift_at(coordinates).integral_restriction(...)`
builds a transvection, a composition and a preimage of the target's frame for every class, where
the pre-204ffbb route formed `transvection matrix * base_images` with `base_images` taken once.
The repair keeps 204ffbb's corrected coset reading and restores the matrix test.

| log | commit cited | result |
| --- | --- | --- |
| `issue528-lift-matrix-equivalence.py` | the tree of the repair | the probe: wraps `_parameter_at`, which every tested class passes through, so the tested coordinates are recorded without reconstructing the Smith reading, runs the locus, then asks each recorded class for the composition's own `integral_restriction` and compares. Prints a disagreement with its coordinates |
| `issue528-lift-matrix-equivalence.log` | main `6ce8d8a8` + the repair | the control `U(2) + U(2) + <2>`: **8 of 8 classes agree**; the T_En line of Sterk's cusp 4: **1024 of 1024 agree**, the matrix reading **37.205 s** against the composition's **66.028 s** on the same classes |
| `issue528-locus-tests-repaired.log` | main `6ce8d8a8` + the repair | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` with the test lint plugin: **6 passed in 16.97 s**, the new counting test included |
| `issue528-locus-tests-204ffbb-red.log` | `204ffbb96e` | the same file there: the new test **fails** -- the torsor asks for its base point **10** times where the repair asks **3** -- and one existing test fails too (the unequal-Smith-steps control, which `d83ae97`, the child of 204ffbb, repairs; 204ffbb is not main) |
| `issue528-repaired-row-counts.log` | main `6ce8d8a8` + the repair | T_Co's ambient plane row: **returns in 217.9 s** with `_lift_at` called **0** times, where `204ffbb96e` did not return at 300 s with 1362 calls costing 183.67 s, and `a71272add9` returned in 54-61 s. The per-class lift test is gone from the row; the remaining gap to the base is not the lift test and is the next measurement |

## #528, the tree's own comparison: one cProfile of the ambient row per tree

The slow-run triage's third step: one profile of the ambient `O(L)` plane row of `T_Co` at
`a71272add9` and one at main `cff6a3a`, compared function by function by own time and call
count. Each run is one process, capped at 520 s, with the row's two inputs (the lattice and its
stable orthogonal group) built outside the profiled region, and each prints the wall time of a
fixed workload beside the row's seconds.

The two tables are the raw record; `issue528-row-profile-compare.py` joins them on
`(path, function)` and prints what grew, which is what the log holds.

| log or table | tree | what it is |
| --- | --- | --- |
| `issue528-row-profile.py` | -- | the probe: builds the inputs, profiles the row alone, writes one table per run |
| `issue528-row-profile-compare.py` | -- | the comparison: two tables in, the growth of own time and of call count out |
| `issue528-profile-t-row-base.log` | `a71272add9` | the base run's log: **232.4 s** under the profiler, `calib=0.164`, the row **returns**, **448,757,911** calls |
| `issue528-profile-t-row-base.tsv` | `a71272add9` | the base run's table, 5,448 functions |
| `issue528-profile-t-row-main.log` | `cff6a3a` | the main run's log: **did not return at 520 s** (`calib=0.162`), **1,408,289,407** calls in the calls that completed |
| `issue528-profile-t-row-main.tsv` | `cff6a3a` | the main run's table, 5,350 functions, marked `decided=False` |
| `issue528-profile-t-row-compare.log` | both | the comparison, and its own statement that one table is truncated |

The base row was profiled once before (`issue528-profile-base-ambient-row.log`, 168.1 s at
`calib=0.165`); this run of the same tree took 232.4 s at `calib=0.164`. The two are not
reconciled here and no number is quoted from either alone: the comparison below is one base
run against one main run under the same probe in the same session, and the calibration of the
two runs agrees to 1.2 %.

What the tables say, per call and not per row (the main table is truncated, so it is read per
call and never as a row total):

| function | base calls / cum | main calls / cum |
| --- | --- | --- |
| `recursive._isotropic_pointed_isometry` | 28 / 182.9 s (6.5 s a call) | 6 / 509.6 s (**84.9 s a call**) |
| `isotropic_lifts._integral_lift_locus` | 8 / 127.6 s (15.9 s a call) | 2 / 498.8 s (**249 s a call**) |
| `isotropic_lifts.integral_parameter_classes` | 8 / 114.7 s (14.3 s a call) | 2 / 65.7 s (32.8 s a call) |
| `lattice_morphisms.is_integral_on` | 28 / 6.5 s | 6 / 0.27 s |
| `module_morphisms.solve` | 441 / 6.6 s | 192 / 0.11 s |

So the row's growth is not the ring division of `solve` on this tree: `is_integral_on` and
`solve` are *cheaper* per call at main. It is the part of `_integral_lift_locus` that is not
`integral_parameter_classes` -- the product and image-set construction over the passing
classes and the kernel -- which goes from 1.6 s a call to about 216 s a call, and the owned
set and category machinery under it is what the comparison ranks first: `set_categories
.__call__` 10.5 -> 75.2 s own at 9.2x the calls, `__contains__` 5.3 -> 37.6 s at 9.0x,
`_element_constructor_` 4.3 -> 34.4 s at 9.2x, and, multiplicatively, `component` 597x,
`index_set` 459x, `family` 442x, `point_at` 66x. The commit that grew it is not bisected in
this round, and the row's number at main is not the whole row.

## #528, the review of `0a55452cfa`: what a test of its matrix reading can and cannot see

The review ordered a behaviour test whose reduction isometry has a non-integral base point, red at
`0a55452cfa`. Two probes were run before writing it, and the answer they give is why the test
below is green at that commit and not red.

| log or table | tree | what it is |
| --- | --- | --- |
| `issue528-lift-transpose.py` | -- | the probe: per class of the parameter quotient, the lift's own `integral_restriction`, the locus' reported classes, and both matrix readings (`T * B^t`, what `0a55452cfa` computes, and `T * B`, with the images in columns), at every signed permutation and Eichler transvection of a control's reduction and their pairwise products |
| `issue528-lift-transpose.log` | `cff6a3a` | `U(2) + U(2) + <2>`: 110 reduction isometries, **30** with a base point whose coordinate matrix is not symmetric; at the three printed, `membership_disagreements` **0** and `matrix_disagreements` **0** -- the two readings give the same class set, and both agree with the truth and with the reported locus. `U + A3(2)`: 6 isometries, 4 with a non-symmetric base-point matrix, again **0**. The transposed product is a different *matrix* (it differs from the lift's at 64 of 64 and 63 of 64 classes there) but it is the same *verdict*: integrality and `det` are transpose-invariant for a square matrix |
| `issue528-lift-nonintegral-base.py` | -- | the search for the case the review names: every lift of a reduction isometry, over the seven small controls the locus' tests use, asked whether its **base point** restricts integrally |
| `issue528-lift-nonintegral-base.log` | `cff6a3a` | **0 of 252** reduction isometries have a base point that does not restrict integrally: every rational lift of a reduction isometry of `U + <2>`, `U + U + <2>`, `U(2) + <2>`, `U(2) + U(2)`, `U(4) + <2>`, `U(2) + U(2) + <2>` and `U + A3(2)` is already an isometry of the lattice. The condition the review says the answer changes under does not occur on a control a test can afford |
| `issue528-integrality-split.py` | -- | the per-lattice datum the ordered repair would cache: identity of the objects across two accesses, and the per-call cost and split of `integral_restriction` and `is_integral_on` |
| `issue528-integrality-split.log` | `cff6a3a` | `ModulesOverIntegralDomains(ZZ)(L)` **is the same module**, its `generic_fibre_map()` **the same morphism**, `Modules(QQ).restriction_of_scalars(f)` **the same category**, and `_integral_extension_coordinate_span()` **the same datum** on a second access; `integral_restriction(L, L)` **3.61 ms** a call and `is_integral_on(L, L)` **2.66 ms** a call on the rank-5 control, both dominated by element and ring construction (`_element_constructor_`, `isinstance`, `__contains__`, `__classcall__`), not by a repeated frame. The profile of the T_Co row agrees: `_integral_extension_coordinate_span` is called twice per row at both trees |
| `issue528-locus-nonidentity-test-on-0a55452.log` | `cff6a3a` | the new test `test_the_locus_at_a_non_identity_reduction_is_every_class_that_lifts` with the file's six others and the test lint plugin: **7 passed in 12.52 s** -- green, not red, at the commit under review |

## #528, the restore of the per-class lift test and the row after it

`0a55452cfa` replaced the locus' per-class lift test by the product `T * base_images`; its
`base_images` is filled by rows (source-major entries into a `matrix(QQ, n_target, n_source, ...)`),
so the product is `T * B^t`.  The restore puts back `_lift_at(coordinates).integral_restriction(source, target)`
and deletes `lifts_integrally`, `base_images`, the per-call assertion and their imports.  The
call-count test of the previous round counts calls of `base_point`, which the restored route makes
once per class again, so it is removed with the mechanism it counted.

| log | tree | result |
| --- | --- | --- |
| `issue528-locus-tests-restored.log` | `cff6a3a` + the restore | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` with the test lint plugin: **6 passed in 13.24 s**, the new non-identity-reduction test included |
| `issue528-row-after-restore.log` | `cff6a3a` + the restore | `T_Co`'s ambient plane row, cap 520 s: **did not return**; `_lift_at` **1536 calls, 162.155 s** and `eichler_transvection` **1536 calls, 30.851 s** inside the window -- about 105 ms a class, against the matrix test's row of 217.9 s (`issue528-repaired-row-counts.log`) |
## The fifth review of #500: the torsion reading and the provider order

The four logs below are the runs the commits `030a528` and `476f87c` cite.  The
probes were run in the adopted image with the checkout bound at
`/repos/sage-extensions` and the port at `/work`, the same shape as above but
with `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`
and the script bound at `/probe.py`.  The tree is `6e4e097`, which is the four
commits merged onto the remote main `1cc2481`; the source files these logs
measure are unchanged by that merge.

| log | commit cited | result |
| --- | --- | --- |
| `issue500r5-name-owners.py` | the tree of `476f87c` | the probe: for twenty-six constructed objects and each of `ParentMethods`, `ElementMethods`, `MorphismMethods`, computes the order the deleted insertion loop gave and the order the tree gives, prints the two wherever they differ, and then asks, for every name any provider declares, which provider answers it first under each |
| `issue500r5-name-owners.log` | the tree of `476f87c` | three runs in fresh processes: the orders differ in **2, 1 and 1** of the 78 pairs -- always `Modules.FinitelyGenerated` against `FramedFreeModules`, in `QQ(i)` and `Z[x]/(x^2)`'s `ParentMethods` -- and **no name's answering provider moves in any run** |
| `issue500r5-answering-class.py` | the tree of `030a528` | the probe: names the class in the rebuilt type's method resolution order that declares `_torsion_freeness_decision`, and the answer |
| `issue500r5-answering-class.log` | the tree of `030a528` | `Z[x]/(x^2)`: `AlgebrasWithChosenFinitePresentation.ParentMethods` **True**; `Z/4[x]`, `Z[x]`, `Q(i)`: `FramedFreeModules.ParentMethods` **True** |
| `issue500r5-refusal.log` | the tree of `587aabd` | the order-ideal refusal on `2` in `Z/8` as a `Z`-module, printed: the message names the element, the ideal, the functionals that are missing and what they are for, and no word STY-49 bans |
| `issue500r5-tests.log` | the tree of `6e4e097` | `tests/categories/test_the_refined_category_answers_with_its_own_operation.sage tests/modules/test_the_order_ideal_of_a_ring_element_over_its_base_ring.sage`, test lint loaded: **10 passed in 0.91 s**; the same two files at `a106d23` with the two new tests: **2 failed, 8 passed in 4.59 s** |
| `issue500r5-sweep.log` | the tree of `6e4e097` and a clean worktree at `1cc2481` | a digest, assembled from the run logs and labelled as one: twelve directories, the five root test modules and `tests/lattices/test_lattice_surfaces.sage`, each summary line with its count of FAILED/ERROR ids, and the ids present on one side only -- **none, in any of the fourteen**; the only count that differs is `tests/categories`, 45 passed against 42, the three tests this round adds |

## #531 round 5 (2026-11-15): one store for the finite interners

The round's work is `aafb4ac` (the red tests) and `df5f484` (the repair).  The
two red rows are at the round's base `1cc2481`, the base the review read; the
head rows are at `1775a6f`, whose measured content is the tree this evidence
commit produces, and the base rows at `5fabcdc`, the remote main the round is
rebased onto.  The SHAs the repair was first written and measured at are older
than its rebases -- `d43bab4` and `aed5e3e` -- and the patches of `aafb4ac`
against `d43bab4` and `df5f484` against `aed5e3e` are byte-identical
(`git show --format= <sha> -- src tests` on each side, digest
`75dd05cb…` and `c87f2942…`).

| log | commit cited | result |
| --- | --- | --- |
| `issue531-r5-order.py`, `issue531-r5-order.log` | `1cc2481` | item 1, both construction orders, with both stores emptied between runs: **product and coproduct are one object when the key-less family is built first and two objects when the keyed one is** (`True` then `False`, both operations) -- the order the existing test did not build |
| `issue531-r5-red.py`, `issue531-r5-red.log` | `1cc2481` | item 2: a mutable `vector(QQ, [1, 2])` answers `isinstance(..., Hashable)` **True** while `hash` raises `TypeError: mutable vectors are unhashable`; `T = S.filtered(lambda p: True)` over two mutable vectors reports `points_have_a_hash` **True**, and the product of the one-factor family over `T` raises `TypeError: cannot use 'tuple' as a dict key (mutable vectors are unhashable)`.  The probe reads `points_have_a_hash`, which the repair deletes, so it runs at the base only |
| `issue531-r5-factors.py`, `issue531-r5-factors.log` | `1cc2481` | the counterexample to keying the store by the factors: `hash(finite_ordered_set(([0],)))` raises `TypeError: unhashable type: 'list'`, and yet `Sets().product` of a family with that factor **builds and interns** (`second product is the first` True, coproduct likewise); a family whose values are Python lists is refused by the product with its own message |
| `issue531-r5-accept.py`, `issue531-r5-accept.log` | `1775a6f` | the repair, measured: one product and one coproduct in **both** orders; a family whose factor refuses a hash still interns; the product over the filtered set of mutable `QQ` vectors builds with `factor(v) is factor` and two equal filtered families share it; an undecided family equality builds **both** constructions and keeps both |
| `issue531-r5-four-head-mine.log` | `1775a6f` | `tests/sets/test_products_and_coproducts_of_finite_and_countable_sets.sage`, `tests/sets/test_a_finite_ordered_set_hashes_by_its_points.sage`, `tests/rings/test_a_quotient_class_hashes_by_its_class.sage`, `tests/modules/test_dual_point_hash.sage`, `--no-test-lint`: **6 failed, 47 passed in 4.08 s** |
| `issue531-r5-four-head-base.log` | `5fabcdc` (a clean worktree) | the same four files: **6 failed, 46 passed in 4.12 s**; the six FAILED ids are identical -- `test_unchecked_discrete_diagram_cannot_certify_infinite_factors`, `test_finite_diagram_restricted_to_infinite_parity_family`, `test_constant_countable_coproduct_has_diagonal_enumeration`, `test_selected_nonconstant_countable_coproduct_is_enumerated`, `test_componentwise_set_maps_accept_additive_diagrams`, `test_infinite_componentwise_set_maps_use_a_selected_natural_transformation` -- so the extra pass is this round's net one test |
| `issue531-r5-sets-head-mine.log` | `1775a6f` | `tests/sets`, `--no-test-lint`: **29 failed, 136 passed in 12.11 s** |
| `issue531-r5-sets-head-base.log` | `5fabcdc` | the same directory: **29 failed, 135 passed in 12.97 s**; the FAILED id sets are identical, and the one extra pass is the added test net one against the one it replaces |
| `issue531-r5-lint-head-mine.log` | `1775a6f` | `test_lint` on the three test files this round touches: **3 files, 167 findings** |
| `issue531-r5-lint-head-base.log` | `5fabcdc` | the same three: **3 files, 161 findings** -- the products file already ends the run red at the base, and the six added findings are the three kinds its other tests carry (TL01 local imports, TL08 `finite_ordered_set` and `indexed_family` construction), which a test in that file cannot avoid without rewriting the file |

## #529, the seventh round: identity is the run and the stage id, the name describes the input

The record's `input` stops being an identity: every stage line now carries `id`
(unique in the run's file) and `parent` (the enclosing stage's `id`), and the
canonical-form naming machinery is deleted. The first log is the red state on
main; the rest are the repair, on the commit this section's push names.

| log | commit cited | result |
| --- | --- | --- |
| `issue529-reflection-hyperbolic-main-red.log` | main `1cc2481` | `tests/lattices/test_reflection_hyperbolic.sage` alone: **3 failed, 1 passed in 2.05 s**, all three red on `TypeError: 200 of _OwnedRingParent_with_category.element_class has no canonical form for a record name` at `_lattice.py:1579` -- the `.sage` bound `max_decompositions=200` raised inside the timed call, so the Vinberg walk did not run. The second call of each walk failed as `KeyError: ((None, None, 200, None), ())`: the raise sat inside `cached_method` |
| `issue529-timing-record-tests-green.log` | `8b7e517` | `tests/engineering/test_the_timing_record_names_each_stage.py` with the test lint and the suite budget: **9 passed in 11.41 s**, the three round-7 tests among them (the `Õ`/`Õ⁺` rows of one lattice named apart; a stage's record carrying its own `id` and its enclosing stage's `id`; `cusp_chamber(max_decompositions=200)` named, not refused) |
| `issue529-vinberg-tests-green.log` | `8b7e517` | `tests/lattices/test_reflection_hyperbolic.sage` and `tests/lattices/test_the_subgroup_cusp_chamber.sage`: **7 passed in 155.61 s** -- the file that was red on main above, and the `.sage` literals at `test_the_subgroup_cusp_chamber.sage:119-120` (`max_decompositions=400` beside a filter) |
| `issue529-reduction-image-cusps-green.log` | `8b7e517` | the two cusp-chamber tests of `tests/lattices/test_the_isotropic_reduction_image.sage` selected by node id -- `max_decompositions=8` and `max_decompositions=20`, the file's literal sites: **2 passed in 148.92 s** |
| `issue529-reduction-image-whole-file-capped.log` | main `1cc2481` + the repair, before it was committed | the same file whole, capped at 560 s: **6 passed** and the seventh still running when the cap killed it (peak RSS 1882 MiB). No verdict on the file; the two cusp-chamber tests above are what was decided |

## #529, the eighth round: each owner names its kind, and a stage asserts its own close

The group's name moved out of the naming layer: `Subgroups.ParentMethods`,
`PredicateSubgroups.ParentMethods` and `LatticeIsometryMor` each state their own
`description()`, and `_group_label` is `return group.description()`. The lattice
name reads the public `gram_matrix()` and each entry's `repr`; a keyword argument
is written by its `repr` or its owner's description, with no callable branch; a
stage's close asserts it closed its own id; and the tests that asserted only
`!=` or a two-level parent now assert the description and a three-level chain.

| log | commit cited | result |
| --- | --- | --- |
| `issue529b-tests-at-base-1cc2481.log` | base `1cc2481` | the round-8 test file and `conftest.py` copied into a worktree of that commit, nothing else changed: **4 failed, 5 passed in 9.94 s**. The Integer test is red on `TypeError: 200 of _OwnedRingParent_with_category.element_class has no canonical form for a record name` -- `ZZ(200)` reached `_canonical`; the parent test red on `KeyError: 'id'`; the row test red on `AttributeError: ... has no attribute 'description'` |
| `issue529b-timing-record-tests-green.log` | `238ec3c` | `tests/engineering/test_the_timing_record_names_each_stage.py` with the test lint and the suite budget: **9 passed in 10.24 s** |
| `issue529b-vinberg-tests-green.log` | `238ec3c` | `tests/lattices/test_reflection_hyperbolic.sage` and `tests/lattices/test_the_subgroup_cusp_chamber.sage`: **7 passed in 131.41 s** |
| `issue529b-reduction-image-cusps-green.log` | `238ec3c` | the two cusp-chamber tests of `tests/lattices/test_the_isotropic_reduction_image.sage` by node id (`max_decompositions=8` and `=20`): **2 passed in 149.95 s** |
## #500, the sixth round: the citation, the false clause, the docstring, the dead line, the record

The five corrections `b762a8a`, `5f69bb3`, `2ac0d5c`, `851df47` and the commit
that carries `results/issue500-fifth-review.md`: what the order and the walk
really do across processes, where the recursion really runs, and the regression
the five commits do not move.

| log | commit cited | result |
| --- | --- | --- |
| `issue500r6-seeds-orders.log` | `6e51d33` | the provider probe run once per `PYTHONHASHSEED` in 0-9, one fresh process each, over 26 objects x 3 levels: **the walk has two forms** for `QQ(i)`'s and `Z[x]/(x^2)`'s `ParentMethods` and one for the other 76 pairs, **`_owned_mixins` has one form for all 78 pairs in all ten seeds**, and the first provider of every name is the same in all ten; **the old insertion order has two forms**, the same two the walk has. The digest of all 780 probe lines is in the log, the probe in `issue500r6-seeds-orders.py` |
| `issue500r6-relation.log` | `6e51d33` | `_precedes` on the 33 (object, level) pairs of the relation probe and on 84 of the extension probe: **0 classes precede themselves, 0 pairs precede each other both ways, 0 triples break transitivity**, and **neither order puts a relation-ordered pair the wrong way round** -- so the relation is a strict partial order where measured and the sort's contribution is the `CycleError`, not a corrected order |
| `issue500r6-recursion.log` | `2ac0d5c`, `851df47` | `TensorAlgebras(ZZ)` and `SymmetricAlgebras(ZZ)` both **construct**; `Z[x]/(x^2).is_torsion_free()` is **True** from the framed branch at `algebras.py:3759`; and the recursion is #533's path -- `algebras.py:3773` -> `_represented_relation_torsion_witness` (`:3804`) -> `presentation_ring` (`:3564`) -> `selected_algebra_presentation` (`:3553`) -> `selected_algebra_resolution` (`:2057`) -> `objects.py:383` -> **`owned_category.py:669 linearize`**, the frame census showing **1303 frames, 127 in `linearize` and 43 in `_declared_category_linearization`**, repeating through `super_categories` -> `_commutativity_decision` -> `tensor_product` -> `module_generating_set` -> `parent_class` -> `linearize`. `Z[x]/(2x)`, one of #533's three objects, raises the same `RecursionError` from `is_torsion_free()` |
| `issue500r6-tests.log` | `851df47` | the round's two test files under the test lint: **10 passed in 0.87 s** |
| `issue500r6-sweep-tree.log` | `851df47` | `tests/modules`, `tests/algebras`, `tests/categories`, one pytest process each: **90 failed 222 passed**, **103 failed 110 passed**, **63 failed 61 passed** |
| `issue500r6-sweep-base.log` | `6e51d33` (a clean worktree) | the same three directories: **the same three summaries, the same FAILED ids, 0 on either side only** |

## #528, third round: the constructor inside one `_lift_at`, and the base point as one datum

`843bb5b000` restored the per-class lift test and left the row at about 105 ms a class, naming the
element and ring construction of the lift's images from a whole-row split.  This round splits one
call.  `issue528-lift-split.py` wraps `_lift_at`, records the classes the locus itself tests, and
re-runs the body of `isotropic_lifts.py:388-401` stage by stage (parameter, section, `Aut()`, the
transvection's column matrix, the isometry from it, the base point, the composition, the locus'
`integral_restriction`), checking once that the reproduction is the library's lift on all 11
generators.  `mode=row` installs the split in place of `_lift_at`, so the classes are the row's own
and the twentieth stops the row; `mode=line` does the same on the primitive isotropic basis line
`ep` of `T_Co`.  What it found: `TrivializedTorsors.base_point` (`g_sets.py:2055`) recomputed
`trivialization()(one())` on every call, and each evaluation pays the condition set's ingress
(`set_categories.py:4461` -> `is_parent_of` `:4429` -> `is_in_image`/`solve`), a membership test per
lattice generator for a point that never changes.

| log | tree | result |
| --- | --- | --- |
| `issue528-lift-split-row.log` | base `4237442` | `T_Co`'s ambient plane row, 20 classes, 1 torsor: `_lift_at` **90.1 ms a class**, `base_point` **59.739 ms**, `eichler_transvection` 19.326 ms, `_target_section` 3.527 ms, `_parameter_at` 1.391 ms, composition 0.891 ms; `is_parent_of` **52 calls at 31.46 ms**; `first.base_point() is first.base_point()` **False**; the base point's own profile 0.142 s under the profiler, its ingress `trivialization()(one())` 100.245 ms a call over the first two (cold) |
| `issue528-lift-split-row-after.log` | `4237442` + the repair, uncommitted | the same 20 classes: **33.4 ms a class**, `base_point` **0.001 ms**, `is_parent_of` **7 calls**, the two base points **the same object** |
| `issue528-lift-split-line-base.log` | base `4237442` | the rank-11 line torsor of `T_Co`, 20 classes: 29.4 ms a class, `base_point` 8.752 ms, the test's `integral_restriction` 16.549 ms |
| `issue528-lift-split-line.log` | `4237442` + the repair, uncommitted | the same 20 classes: 20.4 ms, `base_point` 0.001 ms, the test 16.507 ms |
| `issue528-base-point-once-red.log` | base `4237442` | `tests/lattices/test_integral_reduction_lift_witness.sage` with the test lint: **1 failed, 2 passed in 1.34 s** -- the new test, at `base is fibre.base_point()` |
| `issue528-base-point-once-green.log` | `4237442` + the repair, uncommitted | the same file: **3 passed in 1.11 s** |
| `issue528-locus-tests-after.log` | `4237442` + the repair, uncommitted | `test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` and the witness file: **9 passed in 13.54 s** |
| `issue528-neighbours-base.log` | a clean worktree at `4237442` | `test_g_sets_torsor_archive.sage`, `test_finite_cosets.py`, `test_finite_group_subgroups_and_quotients.sage`: **2 failed, 15 passed** |
| `issue528-neighbours-green.log` | `4237442` + the repair, uncommitted | the same three: **the same two FAILED ids, 2 failed, 15 passed** -- neither failure is this round's |
| `issue528-row-after-base-point-cache.log` | `4237442` + the repair, uncommitted | `issue528-lift-test-cost.py`'s own row probe, cap 520 s: `T_Co`'s ambient plane row **returns in 175.3 s** (`_lift_at` 4096 calls, 113.940 s; `eichler_transvection` 4096, 80.994 s), against **undecided at 520 s** at `843bb5b000` (`issue528-row-after-restore.log`, 1536 calls, 162.155 s) |
| `issue528-tests-rebased.log` | `11eec17` + this round's commits | the tree this branch pushes, after the rebase onto the new main: the witness file, the locus file and `test_g_sets_torsor_archive.sage`: **1 failed, 10 passed in 14.22 s**, the failure the same pre-existing `test_the_equivariant_self_maps_of_the_regular_c3_set_are_its_three_translations` |

## #528, fifth round: the locus at a reduction whose base point is not integral

`integral_base_point_or_none` (`isotropic_lifts.py:768`) answers from the rational base point when
that point restricts integrally, and walks `integral_parameter_classes` only when it does not.  Every
control in the locus' test file is of the first kind; this round finds and tests a specimen of the
second.  The specimen found is `U(5) + U(5) + U(4)` at `-2 e_1 - e_5`, at the Eichler transvection of
its reduction: even, primitive isotropic of divisibility two, base point not integral, period eight,
`P/mP` of 4096 classes against the locus' 512.  Odd lattices are refused by the locus itself
(`isotropic_lifts.py:473` asserts evenness), so the search carries that filter.

| log | commit / run | result |
| --- | --- | --- |
| `issue528-base-point-early-return.log` | `fa5c08b` | the premise: `U(2) + U(2) + <2>` at the identity of the reduction and at its Eichler transvection -- "the base point restricts integrally: True", "`integral_base_point_or_none()` returns the base point: True", "the locus was consulted: False" at both |
| `issue528-integral-base-point-search-even-3to5.log` | `03c9f76` | ranks 3-5, even lattices only: 343 of 1650 lattices searched (270 odd skipped), 1064 marked lines, **1568 torsors, 0 hits**, budget-limited at 486 s |
| `issue528-integral-base-point-search-even-6to7.log` | `03c9f76` | ranks 6-7, even lattices only: 50 lattices (40 odd skipped), 419 marked lines, 822 torsors, **3 hits** -- `U(5) + U(5) + U(4)` at `(-2, 0, 0, 0, -+1, 0)`, `P/mP` 4096, the locus 512; the run stops after the third hit, 2055 lattices of its space unsearched |
| `issue528-integral-base-point-rank5.log` | `03c9f76` | rank-five even candidates of the specimen's shape, sized: 264 torsors, **16 hits, all of them on `U(5) + U(4) + A2`, which is rank six** (period 8, 4096 classes); no rank-five hit |
| `issue528-integral-base-point-specimen.log` | `03c9f76` | the candidates' sizes: `U(5)+U(4)+U(4)` at `-2 e_0 - e_2` has an integral base point (4096 classes, locus 2048); `U(5)+U(5)+U(4)` at `-2 e_0 - e_4` does not (4096, locus 512); the rank-four sums raise from the reduction, which has no non-identity transvection |
| `issue528-integral-base-point-targeted.log` | `03c9f76` | twelve lattices with definite quotients -- reflections, signed Gram symmetries, transvections and their products, 33 to 60 isometries each: **476 torsors, 0 hits** |
| `issue528-integral-base-point-tco.log` | `03c9f76` | `T_Co`'s two primitive isotropic basis lines at the identity of the reduction: both base points integral; neither reduction has a non-identity Eichler transvection among its basis and short vectors |
| `issue528-locus-tests-nonintegral-base.log` | `fa5c08b` | `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` with the test lint: **6 passed in 216.73 s**, the non-identity test at **181.11 s** against the 20 s gate (4096 lift tests) and the pre-existing unequal-Smith test at 29.12 s in the same loaded run |
| `issue528-locus-tests-final-tree.log` | `108ef8d` + this round's commits | the tree this branch pushes, after the rebase onto the new main: the same file with the test lint: **6 passed in 227.02 s**, the non-identity test at 201.07 s against the 20 s gate |
| `issue529-last-timing-tests.log` | `108ef8de` + this round's repair, uncommitted | `tests/engineering/test_the_timing_record_names_each_stage.py`: **9 passed in 21.68 s** |
| `issue529-last-names-doctest.log` | the same tree | `_group_label`'s doctest through `SageDocTestParser(('sage',))`: **0 failed of 7**; and the descriptions the repair makes: `O(L)`, `the subgroup where sn_RR(g) = 1`, the preimage sentence, `the intersection of the subgroup where rho_L(g) lies in … and …`, `the subgroup transported from a subgroup the engine computed`, a generated subgroup with and without a caller's description, and the `NotImplementedError` a kind that states none raises |
| `issue529-last-groups-green.log` | the same tree | `test_generated_model_character_quotient.sage`, `test_character_intersection_generators.sage`, `test_predicate_kernel_and_stabilizer_subgroups_of_s4.sage`: **2 failed, 19 passed in 21.78 s** |
| `issue529-last-groups-base.log` | a clean worktree at `108ef8de` | the same three files: **the same two FAILED ids, 2 failed, 19 passed in 21.66 s** -- neither failure is this round's |
| `issue529-last-hyperbolic-tests.log` | the same tree | `tests/lattices/test_the_subgroup_cusp_chamber.sage` and `tests/lattices/test_reflection_hyperbolic.sage`: **7 passed in 318.56 s** |
| `issue529-transport-repr-at-108ef8d.log` | a clean worktree at `108ef8d` | the rendering the transport started from, before any of this issue's rounds: `repr(centre of S_4)` = `Subgroup of Symmetric group S_4`, `latex` = `\langle \rangle`; the derived subgroup and an owned Sage subgroup likewise |
| `issue529-transport-repr-restored.log` | `6d848c5` + this round's repair, uncommitted | the same probe on the repaired tree: **the same `repr` and the same `latex`, byte for byte** -- the record words no longer reach `_description` |
| `issue529-transport-words-stated-by-callers.log` | the same tree | what the callers now state: `the centre of Symmetric group S_4`, `the derived subgroup of Symmetric group S_4`, `a subgroup of Symmetric group S_4 that GAP lists` (the 30 listed subgroups), `the subgroup of its ambient group with the same elements as the Sage subgroup it was realized from`; and `O^+(L)`'s `repr`/`latex`/`description` unchanged by the clause rename |
| `issue529-final-names-doctest.log` | the same tree | `_group_label`'s doctest: **0 failed of 7**, plus the five kinds' descriptions and the raise for a kind that states none |
| `issue529-final-timing-tests.log` | the same tree | `tests/engineering/test_the_timing_record_names_each_stage.py`: **9 passed, 96 warnings in 10.96 s** |
| `issue529-final-groups-green.log` | the same tree | `test_generated_model_character_quotient.sage`, `test_character_intersection_generators.sage`, `test_predicate_kernel_and_stabilizer_subgroups_of_s4.sage`, `test_finite_group_subgroups_and_quotients.sage`, `test_owned_groups.sage`: **4 failed, 33 passed in 10.11 s** |
| `issue529-final-groups-base.log` | a clean worktree at `6d848c5` | the last two of those files, where two of the four live: **the same two FAILED ids, 2 failed, 14 passed in 2.21 s** -- neither is this round's (the other two are `test_adjust_witness_into_subgroup_matches_elementwise_search` and `test_normalizer_retains_its_conjugation_action_functor`, unchanged since `108ef8d`) |
| `issue529-final-archive-green.log` | the same tree | `test_symmetric_group_s3.sage`, `test_quaternion_group.sage`, `test_orthogonal_group_of_a2.sage`, `test_group_owned_meets.sage`, `test_groups_archive.sage`: **17 failed, 28 passed in 13.58 s** |
| `issue529-final-archive-base.log` | a clean worktree at `6d848c5` | the same five: **the same 17 FAILED ids, 17 failed, 28 passed in 12.72 s** -- the two `diff`ed sets are identical |
| `issue528-transvection-split-base.log` | `6d848c5` | one `eichler_transvection` of `T_Co`'s **rational** lattice, split: **28.252 ms** a call, the rank^2 entries' loop **35.358 ms of 41.220 ms** staged, the same formula in the engine **0.709 ms**; per call 3761 `_owned_engine_element`, 9039 `_element_constructor_`, 441 `_engine_element`, 534 `_engine_ring` |
| `issue528-transvection-split-after.log` | `a7ffee2` | the same probe at the repair: **1.481 ms** a call, the base arrangement still 18.889 ms as a control, the formula **0.389 ms**; 65 `_owned_engine_element`, 79 `_engine_element`, 166 `_element_constructor_` (load average 4-6: the ratio inside a run is the reading) |
| `issue528-transvection-split-counts-base.log` | `6d848c5` | the crossings a test can see, shadowed on the instances: `T_Co` `e.to_vector` **11**, `a.to_vector` **13**, `ring.one` **13**; the rank-3 control **3, 5, 5** |
| `issue528-transvection-split-counts-after.log` | `a7ffee2` | the same counts: `T_Co` **1, 3, 1**; the control **1, 3, 0** |
| `issue528-transvection-neighbours-base.log` | `580fc27` with the base `lattices.py` | five files, the new test's own file excluded: **1 failed, 27 passed in 247.99 s**, the failure `test_approximate_generating_family_uses_exact_two_u_perpendicular_frames`; the lift locus' non-identity test call **207.43 s** |
| `issue528-transvection-neighbours-green.log` | `a7ffee2` | the same files plus the new test: **1 failed, 28 passed in 60.44 s**, the same one failure; the lift locus' test call **44.94 s** |
| `issue528-row-before-transvection-repair.log` | `6d848c5` | `T_Co`'s ambient `O(L)` plane row, bare, capped 520 s: **130.2 s**, 1 plane |
| `issue528-row-after-transvection-repair.log` | `a7ffee2` | the same, bare: **141.7 s**, 1 plane -- a re-run that overwrote a **55.9 s** run of the same code; the row's own route and the VM's load both vary, so its wall time is not the reading (see the two instrumented rows) |
| `issue528-row-before-instrumented.log` | `6d848c5` | the same row, instrumented: **203.7 s**, 4096 `eichler_transvection` costing **107.376 s**, 4096 column matrices 100.076 s |
| `issue528-row-after-instrumented.log` | `a7ffee2` | the same row, instrumented: **522.8 s, did not return**, **0** transvections -- that run never left the stages before the lift locus, which is why it is not this repair's |
| `issue528-row-after-instrumented-2.log` | `a7ffee2` | the same row, instrumented: **78.3 s**, 2560 `eichler_transvection` costing **14.078 s** |
| `issue528-otilde-row.log` | `a7ffee2` | `Otilde(T_Co)`'s plane row, instrumented, progress every 30 s: 5652 transvections by 150 s, then none, only coordinate reads (to 468060 `to_vector`), and **no return inside 520 s**; the launcher closed it at 590 s |
| `issue528-transvection-tests-rebased.log` | `a6cac20` | the tree this branch pushes, after the rebase onto `6a348a2`: `test_eichler_transvection_construction.sage`, `test_eichler_isometry_relations.sage` and `test_isotropic_reduction.sage` with the test lint: **11 passed in 1.30 s** |
| `issue528-locus-specimen.log` | `fed237b` (worktree) | the search for a smaller non-integral-base-point specimen: nine small even lattices, their primitive isotropic markings of coordinates at most two, and each reduction isometry the reduction has (identity, negation, transvection, reflection, and those with negation); the eight survivors are all `U(2) + A2`, `|P/mP| = 256`, the whole class-by-class enumeration **1.7-2.3 s**, against the `U(5) + U(5) + U(4)` specimen's `|P/mP| = 4096` and 181-201 s |
| `issue528-specimen-detail.log` | `fed237b` (worktree) | the specimen the test uses, printed from one process: `U(2) + A2` at `-2e_0 + e_1 - 2e_3`, divisibility 2, reduction of rank 2 with basis squares `(2, 2)`, period 16, **256** classes; base point not integral, `integral_base_point_or_none` **0.14 s**, `integral_parameter_classes` **0.01 s**, the class-by-class enumeration **1.71 s**, the two sides equal, nonempty, the zero class on neither side, not the whole quotient |
| `issue528-locus-test-durations.log` | `fed237b` (worktree, modified) | the rewritten locus file and the accepted base-point witness file, per-test durations: **slowest call 6.22 s**, the non-integral-base-point test **2.35 s**, **9 passed in 13.45 s** -- against the 20 s test-call ceiling and the 60 s hang bound |
| `issue528-locus-and-torsor-tests.log` | `fed237b` (worktree, modified) | the rewritten locus file and the new `Torsors.from_trivialization` test, with the test lint: **7 passed in 12.24 s** |
| `issue528-otilde-stage-slice-run1.log` | `fed237b` | `Otilde(T_Co)`'s plane row, sampled once a second with `faulthandler` watching the GIL: the transvections stop at ~150 s (the ambient `O(L)` row), the row sits in `libgap.FactorCosetAction` (`orthogonal_quotients.py:2003`, called from `_plane_orbit_from_parabolic_stabilizer`, `:3482`) for the next ~140 s, and then walks; **4.50 `to_vector` per `_span_basis_elements` coordinate read in all thirteen 15 s windows from 363.8 s to 562.8 s**, those reads flat at **200-274 a second** -- a constant per element |
| `issue528-otilde-stage-slice-run2.log` | `fed237b` | the same row on the same tree with profiling windows armed by elapsed time: the sampler starves for 14 consecutive 20 s `faulthandler` dumps inside `orthogonal_quotients.py:2003`, the run's `FactorCosetAction` -- the same stage is 130 s in one run and over 270 s in another on one tree, which is the stage's own variability |
| `issue528-otilde-growth.log` | `fed237b` | the same row with every `_lattice_subobject_spanning` timed in blocks of 50 and two 40 s `cProfile` windows: the walk runs from 283.9 s to 568.2 s, **2.56 ms a call at the start and 1.18-1.23 ms at the end (median 1.23, range 1.10-2.99)** -- no growth, and a halving; 190-339 planes transported per 10 s window, 22 `to_vector` per plane, constant; the profile (39.98 s, 84.1M calls) is dominated by the per-construction machinery: `mor_categories.py:2166 Of` **8.811 s** cumulative over 70,053 calls, `set_categories.py:778 __call__` **5.830 s** over 304,024, `_owned_join_as_tuple` **1.339 s** over 20,448, `refine.py:394 _declaring_classes` **1.588 s** over 12,780; 7.636 s of the window is the probe's own `gc.get_objects` and is not the row's |
| `issue528-coordinate-read.log` | `fed237b` | one `to_vector` of a `T_Co` vector, dense and two-term: **< 0.025 ms** each (200 reads apiece), so the row's 22 coordinate reads a plane are not its cost; one **cold** span basis 2.319 ms; the same with the coordinates retained 1.816 ms on a disjoint basis range, which is not a controlled comparison and is not read as a gain |
| `issue528-locus-and-torsor-tests-merged.log` | `b4bb518`, the tree this round pushes | the locus file, the new `Torsors.from_trivialization` test and the accepted base-point witness file, with the test lint: **10 passed in 12.98 s** |
| `issue528-transvection-crossings-base.log` | `6d848c5` | one `eichler_transvection` over `QQ`, owned-ring crossings counted (`_owned_engine_element`): rank 3 **336**, rank 6 **1165**, rank 9 **2539**, rank 12 **4453** -- ratios 3.47 and 13.3 against the rank's 2x and 4x, i.e. quadratic in the rank; `_engine_element` 69/294/600/1014 |
| `issue528-transvection-crossings.log` | `9e9c24a` worktree, uncommitted at run time | the same probe on the tree this round pushes, with the duplicated `b(e, a) = 0` guard decided once: rank 3 **28**, rank 6 **32**, rank 9 **41**, rank 12 **50** -- ratios 1.14 and 1.79, linear; `_engine_element` 40/76/112/148; `t(e) = e`, `t(a) = a - 6e` and `t(f) = f + a - 3e` on every rank |
| `issue528-transvection-tests-new.log` | the same worktree | `test_eichler_transvection_construction.sage`, `test_eichler_isometry_relations.sage`, `test_isotropic_reduction.sage` with the test lint: **12 passed in 2.67 s** |
| `issue528-transvection-neighbours-base-9files.log` | `eb3aec7`, a clean worktree | the nine lattice files that mention `eichler_transvection`: **6 failed, 40 passed in 17.79 s** |
| `issue528-transvection-neighbours-new9.log` | the tree this round pushes | the same nine: **6 failed, 41 passed in 15.65 s** -- the FAILED **ids** are identical to the base run's, and the extra pass is this file's second test |

## #541, the plane row's per-plane cost: what one transport builds

The census is on the smallest lattice of the row's kind whose plane transport
costs more than 5 ms a plane: `U + U` (rank 4), at a median **10.59 ms cold**
(span uncached) and **1.55 ms warm**. Each timed transport is of a fresh plane
of a fresh equal lattice, so the span is built inside the timed region as the
row builds it. Both logs are the probe's own output; the probe files sit beside
them and the launcher is the one the header names.

| log | commit cited | result |
| --- | --- | --- |
| `541-plane-transport-census.log` | `2291235` (main) | sections A-D: the cold/warm ladder on `U+U` (10.59 / 1.55 ms), `U+U+<-2>` (10.25 / 1.63) and `T_En` (13.95 / 2.09); one transport of one fresh plane under `setprofile` -- **35 567 calls, 1 span**, `_MorCategoryOf.Of` 111 calls 23.23 ms incl, `_declaring_classes` 15 calls 1.96 ms own, `OwnedCategory.__contains__` 942, `NaturalNumberSets` element constructions 1066; the unprofiled cold attribution (**13.07 ms a plane**, own ms: `_span_basis_elements` 1.88, `cokernel` 1.14, `Of` 1.02, `_lattice_subobject_on_basis` 0.86, `_declaring_classes` 0.30, `_owned_join_as_tuple` 0.37); the identity table |
| `541-plane-datum-identity.log` | `2291235` (main) | which public datum is one object per parent: `L.gram_matrix()` **False**, `plane.embedded_module_generators()` **False**, and `module_generating_set`, `inclusion`, `cokernel`, `subobject_on`, `Mor(plane, L)` all **True**; per-call cost `gram_matrix` 604.55 us, `subobject_on` 1021.64 us, `embedded_module_generators` 10.99 us; the two `_span_basis_elements` calls of one transport see **different** families, so a family-keyed cache would not merge them |
| `541-embedded-framing-red.log` | `4c29488` | `tests/modules/test_the_embedded_framing_is_one_datum.sage` on the tree before the repair: **1 failed, 1 passed in 3.14 s** -- `plane.embedded_module_generators() is plane.embedded_module_generators()` is False, while the same family's points are still the generator images |
| `541-embedded-framing-green.log` | `ca1f0b2` + the repair | the same file with `embedded_module_generators` cached per subobject: **2 passed in 1.15 s** |
| `541-embedded-framing-lint.log` | `ca1f0b2` + the repair | `sage_extensions.testing.test_lint` on the new test file: **1 files, 0 findings** |
| `541-otilde-row-capped.log` | `cb9ba77` | `NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)`, once, capped at ten minutes: **0 planes transported** by 510.6 s (the tick log), killed by the 600 s inner cap with the walk still inside its first stage; peak tree RSS 1145 MiB. So there is no planes-per-second to report, and the 283.9 s to a first transport that `7c0859c832` recorded is not reproduced on this tree. Not bisected |
| `541-plane-transport-census-after.log` | `cb9ba77` | the same census after the repair: `U+U` **10.45 ms cold / 1.62 ms warm**, `U+U+<-2>` 10.49 / 1.66, `T_En` 14.71 / 2.20, and **35 569 calls** for the profiled transport against 35 567 before -- the repair restores a contract, it does not move the plane's cost |
| `issue540-toric-chart-presentation.log` | `f7bc9b9` (base `2291235e3d`) | `tests/divisors/test_toric_class_groups.sage`, the file #540 names, one process: **7 passed in 2.08 s** on the base tree and **7 passed** on each of ten `PYTHONHASHSEED`s, so the four failures do not reproduce; cone equality requires one fan object (`fans.py:751`) while the hash is the ray coordinates (`fans.py:95`), and every equal copy inside one fan lists one Hilbert basis in one order (0 disagreements over P2, P1xP1, Hirzebruch 2, the A1 cone, P3), so the repair is the invariant the code now enforces. The 18 files reaching the toric chart API, one process: base **42 failed, 72 passed in 15.53 s**, fixed **42 failed, 73 passed in 13.40 s**, FAILED id sets identical; the test lint on `tests/schemes/test_toric_schemes.sage` reports the same 34 findings before and after, none in the new test |
| `541-embedded-framing-green-merged.log` | `1e18b98` (the merge) | the same file after omm/main `2993a51` was merged in: **2 passed in 1.09 s** |
| `issue540-toric-chart-presentation.log` (section 6 of the same log) | `2993a51`/`d1ab7fc` base, repair in this round's commit | #540's four failures **do** occur, and not from the toric cone caches: two `tests/sets` files then `tests/divisors/test_toric_class_groups.sage` in one process is **7 failed, 5 passed** on base `d1ab7fc` (four toric ids) and **3 failed, 12 passed** with the repair (only the three pre-existing `tests/sets` ids). Cause: a semigroup algebra on a free monoid answers `_algebra_mor_class` from `FreeAlgebras.ParentMethods` or from `AlgebrasWithChosenFinitePresentation.ParentMethods`, whichever its generated parent class lists first, and the first is decided by what was built before (`QQ.polynomial_ring("y")` is enough); the second builds `PresentedAlgebraMor.identity` from `engine.hom(engine)`, which `PresentedAlgebraMorphism` refuses, so the augmentation of the free algebra's own degree-zero resolution dies. The minimal reproduction is three lines in `tests/algebras/test_affine_semigroup_algebras.sage`, red on base **1 failed, 2 passed in 5.11 s**, green **3 passed in 1.49 s**. No regression: the 58 `tests/algebras` files **103 failed, 110 passed in 61.79 s** base against **103 failed, 111 passed in 65.65 s** fixed with identical FAILED ids, and the 18 toric files **42/73** against **42/72** with identical ids (the one fewer pass is the deleted first-turn test, which passes without any repair). Section 3's "cannot occur" sentence is retracted in place |
| `531f-red-tests.log` | `d1ab7fc` (main) | the three test files of this round on main: **5 new tests red, 3 polytope-suite failures pre-existing at main, 0 lint findings** -- `test_triangles_with_one_vertex_set_are_one_polytope_with_one_hash` raises on the undecided `is_subset(...) and is_subset(...)`, `test_a_subset_hash_decides_each_member_once` sees the second hash ask the predicate again (4 extra questions), and the three cone tests see one hash for three half-planes, for the two sides of one line and for the two quarter-spaces; `tests/sets/test_products_and_coproducts_of_finite_and_countable_sets.sage` is not part of the run: it holds 160 pre-existing lint findings at main, so every test in it errors at setup |
| `531f-green-tests.log` | `96c6f3d` + the repair | `tests/schemes/test_polytopes.sage`, `tests/sets/test_a_subset_is_a_cache_key.sage` and `tests/lattices/test_rational_polyhedral_cones.sage`, one process: **3 failed, 16 passed in 2.45 s**, and the 3 failures are exactly the polytope-suite failures of main (the `rational_point` AttributeError below); the 5 tests of this round pass, the lint reports no finding in any of the three files |
| `531f-lint.log` | `96c6f3d` + the repair | `sage_extensions.testing.test_lint` on the four test files: **4 files, 162 findings**, all 162 in `tests/sets/test_products_and_coproducts_of_finite_and_countable_sets.sage` and the same 162 (kind for kind, line numbers narrowed) as at main, so this round adds no finding; the new file, the polytope suite and the cone suite have none |
| `531f-sets-main.log` | `d1ab7fc` (main) | `tests/sets`, one process: **10 failed, 57 passed, 102 errors in 6.22 s** |
| `531f-sets-fixed.log` | `96c6f3d` + the repair | `tests/sets` on the fixed tree: **10 failed, 58 passed, 102 errors in 6.75 s** -- the FAILED id set is identical to main's, the extra pass is the new cache-key test |
| `531f-schemes-main.log` | `d1ab7fc` (main) | `tests/schemes`, one process: **254 failed, 90 passed, 68 errors in 111.63 s** |
| `531f-schemes-fixed.log` | `96c6f3d` + the repair | `tests/schemes` on the fixed tree: **251 failed, 94 passed, 68 errors in 115.49 s**; the FAILED set drops exactly `test_lattice_polygon_invariants.sage`'s three polytope-equality tests, which raise on `is_subset(...) and is_subset(...)` at main |
| `531f-modules-main.log` | `d1ab7fc` (main) | `tests/modules tests/objects`, one process: **162 failed, 330 passed, 148 errors in 51.44 s** |
| `531f-modules-fixed.log` | `96c6f3d` + the repair | the same two directories on the fixed tree: **160 failed, 332 passed, 148 errors in 56.48 s**; the FAILED set drops exactly `tests/objects/test_standard_triangle.sage`'s `test_the_invariants_of_the_triangle` and `test_the_order_of_the_vertices_does_not_matter` |
| `531f-polytopes-main.log` | `d1ab7fc` (main) | `tests/schemes/test_polytopes.sage` at main: **3 failed, 1 passed**; the failures are `interior_contains_point((1, 0))`-shaped `AttributeError: 'tuple' object has no attribute 'parent'` in `polytopes.py:684 rational_point` and the dodecahedron row, all three unchanged on the fixed tree |
| `531f-probe.log` | `96c6f3d` + the repair | polytope identity (**equal triangles one hash and one product**, five triangles five hashes, the halfspace triangle the same hash and product), the cost of the three hashes, and the canonical forms: `y >= 0` `(((1, 0),), ((0, 1),))`, `y <= x` `(((1, 1),), ((1, -1),))`, `x + y <= 0` `(((1, -1),), ((-1, -1),))`, `y <= 0` `(((1, 0),), ((0, -1),))`; the 119-gon's first hash **115.171 ms** then 0.002 and 0.000 ms, the cone with a lineality space 0.564 then 0.001/0.000 ms, a subset of 2000 points **76.782 ms** then 0.001/0.001 ms with 2000 membership decisions at the first hash and none after; on 8 half-planes and 56 wedges of `Z^2` the canonical form agrees with the cone equality on every pair (**28 + 1540 pairs, 0 disagreements**) |
| `531f-cost-main.log` | `d1ab7fc` (main) | the same three hashes repeated on main, for the cost the caches remove: the 119-gon 2.020 / 0.019 / 0.009 ms (main hashes the ambient space, so it is cheap and carries nothing), a subset of 2000 points **76.055 / 75.912 / 77.746 ms with 2000 membership decisions at each hash**, the cone with a lineality space 0.413 / 0.202 / 0.175 ms |
| `531f-green-merged.log` | `7de970f` (the merge of `5370933`) | the three files of this round plus `tests/algebras/test_affine_semigroup_algebras.sage` on the merged tree, one process: **3 failed, 16 passed, 3 errors in 4.22 s** -- the 3 failures are the polytope-suite failures of main and the 3 errors are that algebras file's own lint findings (TL01/TL02 at its imports), so the round's tests stay green after `#540`'s merge |
| `531last-probe.log` | `52cbab3` + this round's changes | the canonical form the cone tests now document: `y >= 0` `(((1, 0),), ((0, 1),))`, `y <= x` `(((1, 1),), ((0, -1),))`, `x + y <= 0` `(((1, -1),), ((0, -1),))`, `y <= 0` `(((1, 0),), ((0, -1),))` -- the two that moved are the two the removed orthogonal projection stated as `(1, -1)` and `(-1, -1)`, and the transversal of the Hermite basis states the class each ray is in; on 15 cones of `Z^2` and `Z^3` **120 pairs, 0 disagreements** between cone equality, canonical-form equality and hash equality; the polytope vertex set, read from the private polyhedron, is `{(0, 0), (1, 0), (0, 1)}` for all three presentations of the triangle; `Sets().product((relocated, Sets.Δ[1])) is product`, the same for `cut`, and another triangle gives another product |
| `531last-core.log` | `52cbab3` + this round's changes | `tests/schemes/test_polytopes.sage`, `tests/lattices/test_rational_polyhedral_cones.sage`, `tests/sets/test_a_subset_is_a_cache_key.sage`, `tests/objects/test_standard_triangle.sage`, `tests/lattices/test_reduction_cell_adjacency.sage`, `tests/lattices/test_reduction_cell_faces.sage`, one process: **8 failed, 20 passed in 4.26 s**, no lint finding in any of them; the polytope file's own test, with the product assertions added, passes |
| `531last-core-main.log` | `52cbab3` (main) | the same six files on main: **8 failed, 20 passed in 3.28 s**; the FAILED sets of the two runs are identical, and the three `interior_contains_point`/dodecahedron rows of `test_polytopes.sage` are main's |
| `531last-wide-ids.log` | `52cbab3` + this round's changes | the eight other cone- and polytope-touching test files: **6 failed, 9 passed, 55 errors** on the fixed tree and **6 failed, 9 passed, 55 errors** on main, FAILED ids and the files with a setup ERROR identical; the extracts of both runs, the full logs being 1.2 MB of repeated lint findings in the sets file |
| `531last-tensor-boundary.log` | `52cbab3` + this round's changes | `just tensor-boundary scope=all`: **168** suspected coordinate operations on main and **166** on the fixed tree, none of them in `polyhedral_cones.py`; the two that leave are the `$X.transpose()` calls of the removed projection and no pattern's count rose |
| `532-green-nonunit.log` | `9bc00c1` + the quotient repair | `tests/lattices/test_rational_polyhedral_cones.sage` alone: **15 passed in 0.68 s**, the test that was red in `532-red-nonunit.log` among them |
| `532-core.log` | `9bc00c1` + the quotient repair | the six-file core batch: **8 failed, 21 passed in 2.39 s**; the FAILED set is `531last-core-main.log`'s eight, unchanged, and the 21st pass is the new test |
| `532-wide-ids.log` | `9bc00c1` + the quotient repair | the eight other cone- and polytope-touching files: **6 failed, 9 passed, 55 errors** here and on `52cbab3`, FAILED ids and the files with a setup ERROR identical; extracts, the full logs being repeated lint findings |
| `532-probe.log` | `9bc00c1` + the quotient repair | the reviewer's pair: one form `(((3, 1, 2),), ((-1, 3), (0, 1)))` and one hash for both presentations, and `cardinal({short, longer}) == 1`; **398 cones of `Z^3` cut out twice with a redundant positive combination, 0 disagreements**; on the sample's 79003 pairs the canonical form equals the cone equality everywhere (**0 form collisions among unequal cones**), and the one unequal pair with one hash is a CPython collision (`hash(-1) == hash(-2)`), which the family store resolves by comparing inside the bucket; the two sides of one line stay two sets; the polytope vertex set and the four product assertions are unchanged |
| `532-cost.log` | `9bc00c1` + the quotient repair | the first hash of a fresh cone and the cached ones: pointed `Z^2` 0.462 ms, pointed `Z^3` 0.261 ms, with a lineality `Z^3` 1.008 ms, cached 0.0001–0.0004 ms; the whole `Z^1` cut out by no covector is the zero cone and hashes as `((), ())` |
| `532-tensor-boundary.log` | `9bc00c1` + the quotient repair | `just tensor-boundary scope=all`: 168 on main, **166** here, `polyhedral_cones.py` contributing none and adding none; the two that leave are the removed projection's `$X.transpose()` calls |
| `540r-red-reproduction.log` | `75cbec5` (the repair reverted, `5370933`'s probe deleted) | `tests/divisors/test_toric_class_groups.sage`, one process: **5 failed, 3 passed in 1.12 s** -- the new first row, `test_the_class_group_of_the_hirzebruch_surface_survives_a_polynomial_ring_built_first`, and the four rows the flipped parent-class order reaches, each at the endpoints `ValueError` through `toric_schemes.py:262` -> `algebras.py:4645` -> `:4789` -> `:4911`; the three rows that do not reach it pass |
| `540r-red-algebras-file.log` | `75cbec5` | `tests/algebras/test_affine_semigroup_algebras.sage`, one process: **1 failed, 3 passed in 0.83 s** -- `test_a_semigroup_algebra_keeps_its_identity_after_a_polynomial_ring_is_built` fails at `augmentation` on the same `ValueError`; the file's four rows run at all now, its three pre-existing lint findings (TL01, TL02, TL07) being gone |
| `540r-toric-fix.log` | `b64b6d1` | the same file, one process: **8 passed in 2.10 s**, the new first row included |
| `540r-algebras-file.log` | `b64b6d1` | the same algebras file, one process: **4 passed in 0.79 s**, no lint finding |
| `540r-both-orders-probe.log` | `b64b6d1` | `QQ[S]` for `S = <(1,0),(0,1)>` in both construction orders, one process each, no `QQ[y]` first and `QQ[y]` first: `_algebra_mor_class()` is `FramedFreeAlgebraMor` in the first and `PresentedAlgebraMor` in the second, and in **both** `selected_algebra_resolution().augmentation()` is built, fixes `s0`, has parent `Mor_UnitalAlg(A, A)`, `algebra_framing_morphism()` is the identity of `A.Mor(A)`, and `class_group()` of the Hirzebruch surface is free of rank 2 |
| `540r-scenario-base.log` | `52cbab3` (main) | the issue's scenario, `tests/sets/test_cardinality_construction_comparisons.sage`, `tests/sets/test_standard_cardinals_archive.sage` and `tests/divisors/test_toric_class_groups.sage` in one process: **3 failed, 9 passed in 2.89 s**, the three failures the two `tests/sets` files' own |
| `540r-scenario-fix.log` | `b64b6d1` | the same three files on the repaired tree: **3 failed, 10 passed in 2.67 s**; the FAILED id set is identical to main's and the extra pass is the new toric row |
| `540r-algebras-base.log` | `52cbab3` (main) | `tests/algebras` with `--ignore=tests/algebras/test_module_structure.sage` (that file aborts inside `QuadraticField` on both trees), one process: **44 failed, 43 passed, 125 errors in 42.71 s** |
| `540r-algebras-fix.log` | `b64b6d1` | the same directory on the repaired tree: **44 failed, 47 passed, 122 errors in 43.88 s**; the FAILED id set is identical to main's, the four extra passes are the semigroup file's four rows, which no longer error at setup, and the three fewer errors are that file's lint findings |
| `540r-edge-refused.log` | `52cbab3` with `5370933`'s probe removed | the placement repair this review asks for, measured: with `FreeAlgebras(R)` declared below `AlgebrasWithChosenFinitePresentation(R)` the two quadric-cone rows of the toric file fail (**....FF..**) because the presented parent class then answers for the polynomial algebra a semigroup algebra is built from and `_finitely_presented_algebra_from_data` (`free_algebras.py:1319`, `:1320`) reads a resolution truncated in degree zero; the same happens with `presentation_ring()` answering its degree-zero source, and with `SymmetricAlgebras(R)` declared below the presented category as well |
| `540r-rebased-red-reproduction.log` | `1bbe9a9` | the row above's tree after the series was rebased onto main `b33d193` (`#531`'s cone canonical form): `tests/divisors/test_toric_class_groups.sage` **5 failed, 3 passed in 1.66 s**, the same five rows |
| `540r-rebased-toric-fix.log` | `6141e01` | the same file at the rebased repair: **8 passed in 3.03 s** |
| `540r-rebased-algebras-file.log` | `6141e01` | `tests/algebras/test_affine_semigroup_algebras.sage`: **4 passed in 1.33 s** |
| `540r-rebased-scenario-base.log` | `b33d193` (main) | the issue's scenario at the new base: **3 failed, 9 passed in 3.32 s**, the two `tests/sets` files' three |
| `540r-rebased-scenario-fix.log` | `6141e01` | the same three files at the rebased repair: **3 failed, 10 passed in 1.81 s**, FAILED ids identical |
| `540r-rebased-algebras-base.log` | `b33d193` (main) | `tests/algebras` with `test_module_structure.sage` ignored: **44 failed, 43 passed, 125 errors in 25.07 s** |
| `540r-rebased-algebras-fix.log` | `6141e01` | the same directory at the rebased repair: **44 failed, 47 passed, 122 errors in 21.91 s**; FAILED ids identical to the new base's |
| `540r-lint-base.log` | `52cbab3` (main, the merged tree the round before) | `python -m sage_extensions.testing.test_lint tests/algebras/test_affine_semigroup_algebras.sage`: **1 files, 8 findings (TL01, TL02, TL07)**, exit 1 -- five TL01 at the three function-local module imports, two TL02 at `_owned_integers`, one TL07 at `repr(algebra)`; as a pytest plugin each finding errors the tests of the file that holds it, which is the three setup errors `531f-green-merged.log` records |
| `540r-lint-main.log` | `dcdeddde` | the same command on the file as this round leaves it: **1 files, 0 findings**, exit 0 |
| `540r-lint-pytest-main.log` | `dcdeddde` | the file collected by pytest with `-p sage_extensions.testing.test_lint` named as well: **4 passed in 0.69 s**, so the four rows run and no finding errors them |

## #541 -- the Õ(T_Co) row's setup, measured against the VM's load

The row is `NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)`.
`7c0859c832` reached its first transported plane at 283.9 s; main did not reach one
at all in ten minutes, and the question was whether a commit between them slowed
the setup or the VM's load decided the two readings.  Every run below carries
`calib`, the wall time of one fixed workload (10M integer cubes and a GAP
`Order(SymmetricGroup(8))`) timed in the same process, and every run is capped at
500 s of row inside a 545 s inner and a 595 s outer kill.  Alternating order:
base, main, main, base.

| log | commit cited | result |
| --- | --- | --- |
| `541-otilde-row-calibrated-base-1.log` | `7c0859c832` | first plane **352.6 s**, calib 0.362 (974 units), 8758 planes at the cap, 58.89 planes/s |
| `541-otilde-row-calibrated-base-2.log` | `7c0859c832` | first plane **356.9 s**, calib 0.364 (980), 8324 planes, 56.04 planes/s |
| `541-otilde-row-calibrated-main-1.log` | main `d1ab7fc785` | **no plane by 514.1 s**, calib 0.415 (>= 1239) |
| `541-otilde-row-calibrated-main-2.log` | main `d1ab7fc785` | first plane **441.8 s**, calib 0.363 (1217), 3283 planes, 55.99 planes/s |
| `541-otilde-row-bisect.log` | -- | the `git bisect run` transcript: predicate `first plane / calib >= 1100`, `022f7a5271` red (1263), `5e7eb7ccdd` green (941), `2291235e3d` red (1340), `10c3902861` green (504); **`2291235e3d2c04d7ca5effb4b9c0f8b6cfaa5537 is the first bad commit`** |
| `541-bisect-step-022f7a5271.log`, `-5e7eb7ccdd.log`, `-2291235e3d.log`, `-10c3902861.log` | each step's own tree | the four step runs, each with its stack samples (`faulthandler`, every 120 s): at 120 s the base sits in `integral_restriction` and by 240 s in the coset walk, while main sits in `_finite_family_key` -> `__hash__` -> `point_at` |
| `541-hash-red.log` | main `d1ab7fc785` | `tests/sets/test_the_hash_of_a_finite_ordered_set_is_one_datum.sage`: **1 failed, 2 passed in 2.03 s**, `assert (0, 1, 2, 3, 0, 1, ...) == (0, 1, 2, 3)` |
| `541-hash-green.log` | the repair | the same file: **3 passed in 1.18 s** |
| `541-hash-lint.log` | the repair | test lint: **1 files, 0 findings** |
| `541-otilde-row-after-hash-repair.log` | the repair | first plane **483.6 s**, calib 0.577 (838 units), 2089 planes, 72.67 planes/s |
| `541-framing-test-after-docs.log` | the docs commit | `tests/modules/test_the_embedded_framing_is_one_datum.sage`: **2 passed in 1.10 s** |
| `541-two-test-files-on-the-pushed-tree.log` | the pushed tree (`ea895a8` + this round's four commits) | `tests/sets/test_the_hash_of_a_finite_ordered_set_is_one_datum.sage` and `tests/modules/test_the_embedded_framing_is_one_datum.sage` together: **5 passed in 1.36 s** |
| `532-merged-core.log` | `fb7c2b4` (the merge of `95be77c`) | the six-file core batch on the merged tree: **8 failed, 21 passed in 2.38 s** |
| `532-merged-core-main.log` | `95be77c` (main) | the same six files on main: **8 failed, 20 passed in 2.22 s**, the FAILED sets identical; the 21st pass on the merged tree is this round's new test |
| `532-merged-wide-ids.log` | `fb7c2b4` (the merge of `95be77c`) | the eight other cone- and polytope-touching files: **6 failed, 9 passed, 55 errors** on the merged tree and **6 failed, 9 passed, 55 errors in 14.12 s** on `95be77c`, FAILED ids and the files with a setup ERROR identical; extracts of both runs |

## #541 -- the hash's lifetime, and one plane transport priced on T_Co

The reviewer's round kept the bisection (`2291235e3d`), the red test and the
cache's correctness, and asked for `cached_method` instead of an
instance-dictionary cache, for the hash tests to state contracts, and for one
correction in the cone docstring; then for the census of one plane transport on
T_Co itself, which is the row's own lattice.

| log | commit cited | result |
| --- | --- | --- |
| `541-hash-cached-method-green.log` | the `cached_method` commit | `tests/sets/test_the_hash_of_a_finite_ordered_set_is_one_datum.sage`: **3 passed in 1.76 s** |
| `541-hash-cached-method-lint.log` | the same | test lint: **1 files, 0 findings** |
| `541-cones-docs-green.log` | the docstring commit | `tests/lattices/test_rational_polyhedral_cones.sage`: **15 passed in 1.51 s** |
| `541-tco-census-probe.py`, `541-tco-census.log` | main `664a9c3` | one plane transport on T_Co: **2.69 ms** warm, 2.5 ms cold, 14.33 ms and 9 261 calls under `setprofile`; own time per plane `_span_basis_elements` 1.719 ms, `Lattices._repr_` 0.626, `FiniteOrderedSets.from_indexed` 0.555, `NaturalNumberSets.__call__` 0.231 over **644** constructions |
| `541-natural-number-identity-red.log` | main `664a9c3` | `tests/sets/test_the_points_of_a_finite_ordinal_are_values.sage`: **2 failed in 2.03 s**, `assert 1 is 1` |
| `541-natural-number-identity-green.log`, `-lint.log` | the repair | the same file **2 passed in 1.01 s**; lint **1 files, 0 findings** |
| `541-tco-census-after-ordinal-repair.log` | the repair | the same transport: **2.43 ms**, `_span_basis_elements` 1.070 ms, `from_indexed` 0.145 ms, `NN` 0.162 ms over the same 644 calls |
| `541-sets-dir-after.log`, `541-sets-dir-base.log` | the repair / a clean tree at `664a9c3` | `tests/sets/` whole: **29 failed, 146 passed in 7.44 s** against **29 failed, 144 passed in 8.27 s**; the 29 FAILED ids are the same set, so no new failure |
| `541-row-after-ordinal-repair-1.log`, `-2.log` | the pushed tree | the row under the ten-minute cap, twice: **0 planes by 511.5 s and by 511.6 s**, calib 0.378 both times (>= 1352 calib units), both stack-sampled inside `_finite_family_key` -> `__hash__` -> `point_at`. The 838-unit run `353418f` quotes does **not** reproduce |

## #540, fourth round: the free algebra's own presentation, and two operations the tree refuses

Base: main `664a9c3b72`, port at `991b88b095`, image `ghcr.io/dzackgarza/sage@sha256:59568577…`
through `~/sage-image/run.sh -w /work`.  Every run blanks the repository `addopts` and loads
`qc_sage_session`; `--no-time-gates` is passed where a row is legitimately over the 20 s call
ceiling.  "plain order" is a session with no `QQ.polynomial_ring` built first; "poly order" is
one that builds `QQ.polynomial_ring("y")` first.

| log | tree | result |
| --- | --- | --- |
| `540d-presentation-row-red.log` | main `664a9c3` with this round's test files | `tests/algebras/test_affine_semigroup_algebras.sage`: **1 failed, 3 passed in 3.49 s**; both orders' session scripts exit 1 at `assert algebra.presentation_ring() is algebra` |
| `540d-two-orders-on-main.log` | main `664a9c3` | the conftest session script run twice on main: **order 0 returncode 1, order 1 returncode 1**, both at `assert algebra.presentation_ring() is algebra` (line 15 of the script as it stood) -- the record for the claim that the red row is red for the presentation methods, not for the augmentation |
| `540d-algebra-and-cells.log` | this round's tree | `tests/algebras/test_affine_semigroup_algebras.sage` + `tests/algebras/test_free_algebra_issue614_cells.sage` in one process: **1 failed, 8 passed in 5.31 s**, the failure `test_cell_61_tensor_and_divided_power_algebras_of_a_torsion_module`, which fails alone on main too |
| `540d-toric-and-sets.log` | this round's tree | `tests/divisors/test_toric_class_groups.sage` after the two `tests/sets` triggers in one process: **3 failed, 10 passed in 1.95 s** -- all 8 toric rows pass |
| `540d-toric-and-sets-main.log` | main `664a9c3` | the same three files: **3 failed, 10 passed in 2.41 s**, the same three `tests/sets` ids |
| `540d-algebras-dir.log` | this round's tree | the whole `tests/algebras/` directory in one process: **103 failed, 112 passed in 102.83 s** |
| `540d-algebras-dir-main.log` | main `664a9c3` | the same directory: **103 failed, 112 passed in 88.86 s**; the two FAILED-id sets are identical (`comm -23` and `comm -13` both empty) |
| `540d-lint.log` | this round's tree | `python -m sage_extensions.testing.test_lint tests/algebras/test_affine_semigroup_algebras.sage`: **1 files, 0 findings** |
| `540d-rebased-cells-toric-sets.log` | the rebased tree, on `e763219` | the two algebra files, the toric file and the two `tests/sets` triggers in one process: **4 failed, 18 passed in 6.45 s** -- every toric row and every row of this round's algebra file pass |
| `540d-sets-on-the-new-base.log` | `e763219` | the two `tests/sets` files alone: **3 failed, 2 passed in 1.33 s**, the same three ids, so they are not this round's |

Not evidence that anything passed: the two operations this round did **not** deliver, and the runs
that establish why.  The placement of the two `ParentMethods` was attacked three ways and each was
measured on 2026-11-15 in the same image:

- declaring `FreeAlgebras(R).FinitelyGeneratedAsAlgebra()` a subcategory of
  `AlgebrasWithChosenFinitePresentation(R)` through a `CategoryWithAxiom` with that
  `extra_super_categories` leaves the object's category holding the plain `FreeAlgebras(R)` and
  `AlgebrasWithChosenFinitePresentation(R)` as incomparable factors, so the join still orders the
  two `ParentMethods` by creation: `FramedFreeAlgebraMor` plain, `PresentedAlgebraMor` poly.
- additionally placing a finitely generated free algebra in that refinement makes the two
  comparable and answers `PresentedAlgebraMor` in both orders, but puts every free algebra inside
  `AlgebrasWithChosenFinitePresentation`; `AffineSemigroupAlgebras(ZZ)(((1,0),(0,1),(1,1)))` then
  dies building its own relation lift, at `free_algebras.py:1311`'s quotient-of-a-quotient branch
  reading `lift_to_presentation` of a free algebra.
- one shared `_algebra_mor_class_of` keyed on the algebra -- first on AWCFP membership, then on
  `is_free` -- answers deterministically, but `tests/algebras/test_free_algebra_issue614_cells.sage`
  then loses `SparseFreeAlgebraMorphism` from the graded Mor's element class and its cell 84 cannot
  substitute in `Sym(ZZ[NN])` (`3 failed, 2 passed` against main's `1 failed, 4 passed`).

The augmentation, likewise: building it as `self.Mor(self).identity()` (`algebras.py:5324`) gives
`augmentation().parent() is A.Mor(A)` for `QQ[S]` and in the toric chart, but the tensor algebra of
the torsion module in cell 61 realizes its degree-zero resolution *during* construction
(`QuotientRing._reduce_` -> `homogeneous_components` -> `algebra_generator` -> the augmentation
factory), so the graded element class of `GradedAlgebras(ZZ)` is built there and cell 84's sparse
arrow loses its class; with the branch reverted the cells file returns to main's `1 failed, 4
passed` and `QQ[S]`'s augmentation parent is `Mor_UnitalAlg(A, A)` again.
## #541 -- the integral lift locus is a subset of its torsor, not an image of a product

`integral_parameter_classes` is a datum of the torsor and is built in 4 ms on
`T_Co`, but `_integral_lift_locus` presented `T_Z` as the image of
`C x ker r`, and the product interner keys a family by its factors' hashes: the
hash of the 131072-class residue locus walked all of it, **65.2 s a candidate**
(`541-locus-baseline.log`).  The locus is the subset of the torsor cut out by
the parameter's residue class, so nothing is asked for.

| log | commit cited | result |
| --- | --- | --- |
| `541-locus-probe.py`, `541-locus-baseline.log` | main `e763219` | `T_Co` at its first isotropic vector, identity reduction isometry: `\|passing\|` 256, `\|kernel\|` 512, period 4, `\|C\|` 131072; residue locus **0.004 s**, `integral_members()` **65.218 s**, `is_empty()` 0.000 s, `integral_base_point_or_none()` 0.016 s; a subset of the torsor **0.000 s**, one admitted point 0.003 s, membership 0.000 s |
| `541-locus-red.log` | main `e763219` | `tests/lattices/test_the_integral_lift_locus_is_a_subset_of_the_torsor.sage`: **3 failed in 2.03 s**, `AttributeError: ... has no attribute 'integral_lift_locus'` |

## #541 -- the locus is the subset, and the row reaches its first plane at base parity

`_integral_lift_locus` built `C x ker r` to name the integral lift locus, and the
product interner keys a family by its factors' hashes, so each candidate the
`T_Co` plane row tested walked the residue locus' 131072 classes.  The locus is
the subset of the torsor cut out by the parameter's residue class; the repair
constructs that subset, admits one point so its emptiness is decided, and returns
the empty set when the residue locus is empty.

| log | commit cited | result |
| --- | --- | --- |
| `541-locus-after.log` | the repair | same probe, same specimen: `integral_members()` **0.021 s** (was 65.218 s), `integral_base_point_or_none()` 0.000 s (was 0.016 s), the subset cut in 0.000 s, one admitted point 0.003 s, membership 0.000 s |
| `541-locus-green.log` | the repair | the new file with `test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage` and `test_integral_reduction_lift_witness.sage`: **12 passed in 16.24 s** |
| `541-locus-lint.log` | the repair | test lint on the new file: **1 files, 0 findings** |
| `541-coble-line-base.log`, `541-coble-line-after.log` | main `e763219` / the repair | `test_the_coble_lattice_line_orbit_call_returns.sage`, the port's own consumer of `integral_members`: **100.0 s -> 59.5 s**, 1 passed on both |
| `541-levi-files-base.log`, `541-levi-files-after.log` | main `e763219` / the repair | nine Levi/isotropic-reduction files: **5 failed, 38 passed** on both, the FAILED ids identical |
| `541-locus-doctests-broken.log`, `-base.log` | the repair / main `e763219` | `sage -t` on `isotropic_lifts.py`: 24 of 24 and 19 of 19 failed — the forker attributes nested-scope docstrings to `_vector_denominator.ParentMethods`, so the module's doctests are not runnable this way at either tree |
| `541-locus-doctest-run.log` | the repair | the examples this round touches, run by hand: `integral_torsor`'s four, `integral_lift_locus`'s two, `integral_members`' one — all hold |
| `541-row-after-locus.log`, `541-row-probe.py` | the repair | the `Õ(T_Co)` plane row, `ROW_DEADLINE=500`, calib **0.369 s**: **first plane at 353.3 s = 957 calib units** (base `7c0859c832` 974-980, main `e763219` >= 1352), **11 191 planes** by 502.1 s at **75.2 planes/s, 13.3 ms a plane** |

## #541 -- the same runs on the rebased tree, which is the pushed one

Main moved to `7784c13e44` (the `#540` round, whose moves are `algebras.py`,
`semigroup_algebras.py` and `tests/algebras/`) while this round's repair was
being written, so the repair and its test were rebased onto it.  The lattice,
sets and `isotropic_lifts` code is byte-identical between `e763219` and the
rebased tree, and the rows below are the same commands re-run so that each log
names the pushed commit.

| log | tree | result |
| --- | --- | --- |
| `541-locus-green-rebased.log` | `c8790f2` | the new file with the two existing locus files: **12 passed in 11.28 s** |
| `541-levi-files-after-rebased.log`, `541-levi-files-base-rebased.log` | `c8790f2` / `e763219` | the nine Levi/isotropic-reduction files: **4 failed, 39 passed in 14.95 s** against **4 failed, 39 passed in 15.47 s**, the FAILED ids identical |
| `541-levi-onefile-after-rebased.log`, `541-levi-onefile-base.log` | `c8790f2` / `e763219` | `test_higher_rank_levi_lifts.sage` alone: **8 passed** on both.  The batch's fifth failure in `541-levi-files-after.log` and `541-levi-files-base.log` is this test, which passes alone on both trees: a cross-test interaction of the tree, not of this round |
| `541-coble-line-after-rebased.log` | `c8790f2` | the port's own consumer, `test_the_coble_lattice_line_orbit_call_returns.sage`: **58.07 s, 1 passed** (100.0 s at `e763219`) |
| `541-row-after-locus-rebased.log` | `c8790f2` | the row again, calib **0.364 s**: **first plane at 440.0 s = 1209 calibration units**, 2 756 planes by 521.0 s at **34.0 planes/s, 29.4 ms a plane**; load average **8.45 on 4 CPUs** during the run (other sessions' Lean builds and pandoc).  Against `541-row-after-locus.log`'s 353.3 s at calib 0.369 (957 units, 75.2 planes/s): the walk's per-plane rate halved while the calibration moved 1.4 %, so the calibration under-normalises and the two runs are not comparable with each other |

Both capped runs of the repair reach a plane (353.3 s and 440.0 s, 957 and 1209
units) where the parent tree `e763219` reached none in 511.5 s and 511.6 s at
calib 0.378 (>= 1353 units), and neither run's stack samples enter
`_finite_family_key`: the 120 s sample of the rebased run is inside
`integral_restriction` at `isotropic_lifts.py:644`, the residue locus' own
per-representative test.

## #541, the naturals' intern table given a lifetime, and the row at low load

| log | commit cited | result |
| --- | --- | --- |
| `541-weak-natural-red.log` | `9d07255` | the two test files before the repair: **3 failed, 5 passed in 2.65 s**.  Both lifetime tests stop at `assert 3 == 2` -- the strong `cached_method` table is the third reference -- and the pickle test at `loads(dumps(point)) is point` False.  Test lint loaded, no finding on either file |
| `541-weak-natural-green.log` | `ac4edea` | the two test files after: **8 passed in 0.40 s**, test lint loaded, **0 findings** |
| `541-weak-natural-sets-dir-base.log`, `541-weak-natural-sets-dir-fix.log` | `ac941dc62b` / `ac4edea` | `tests/sets` whole: **29 failed, 146 passed in 6.68 s** against **29 failed, 149 passed in 7.79 s**; the FAILED id sets are identical under `sort` and `diff`, and the three that now pass are this round's tests |
| `541-weak-natural-retain-base.log`, `541-weak-natural-retain-fix.log` | `ac941dc62b` / `ac4edea` | 10^6 distinct naturals, one probe on both trees: resident **+287.5 MiB, table of 1 000 000 entries**, 1.6 s at the base, against **+0.0 MiB, table of 1 entry**, 1.1 s.  Pickle protocols 0/2/5, `copy` and `deepcopy`: base refuses 0 (`TypeError: Cannot convert NaturalNumberSets.element_class to sage.structure.parent.Parent`) and loses identity on the rest; the repair returns the one point on all of them, and `loads(dumps(NN)) is NN` (False at the base) |
| `541-weak-natural-point-base.log`, `541-weak-natural-point-fix.log` | `ac941dc62b` / `ac4edea` | one point of `NN`, 200 000 hits and 200 000 misses: a repeat construction **0.22 -> 0.24 us**, a first construction **1.10 -> 1.02 us** (a second pair of runs put the repeat at 0.25 and the first at 1.17 us, so the hit is +0.02-0.03 us and the miss is inside the noise) |
| `541-row10-repair-1.log`, `541-row10-base-1.log`, `541-row10-repair-2.log`, `541-row10-base-2.log` | `ac4edea` / `7c0859c832` | the Otilde(T_Co) plane row, four runs alternating between the repaired tree and the base, each calibrated and killed at 590 s outer / 570 s inner with `ROW_DEADLINE=540`: see the table below |
| `541-weak-natural-consumers-base.log`, `541-weak-natural-consumers-fix.log` | `ac941dc62b` / `ac4edea` | the 46 test files outside `tests/sets` that name `NN`, `NN.`, `NN(` or `Sets.Δ`: **81 failed, 174 passed in 3:51** against **81 failed, 174 passed in 4:05**, FAILED id sets identical under `sort` and `diff`.  The failures are the tree's, not this round's |

The row, in the order it was run.  Load averages are the line the log's own header
records, read from `/proc/loadavg` on 4 CPUs immediately before the run; "units"
is the first-plane time divided by the run's own calibration.

| run | tree | load before | calibration | first plane | units | planes at the cap | planes/s over the walk | first 29 s window |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `-repair-1` | `ac4edea` | 1.55 1.54 2.48 | 0.365 s | **345.4 s** | **946** | 11 036 by 554.1 s | **52.88** (18.9 ms) | 72.19 |
| `-base-1` | `7c0859c832` | 5.76 3.82 3.02 | 0.713 s | **478.5 s** | **671** | 5 283 by 567.2 s | **59.55** (16.8 ms) | 49.74 |
| `-repair-2` | `ac4edea` | 2.50 5.91 4.97 | 0.568 s | **341.8 s** | **602** | 14 305 by 550.4 s | **68.55** (14.6 ms) | 69.03 |
| `-base-2` | `7c0859c832` | 1.79 2.64 3.64 | 0.429 s | **349.3 s** | **814** | 11 690 by 561.2 s | **55.17** (18.1 ms) | 54.98 |

What the four runs decide.  The repaired tree's first plane is **345.4 s and
341.8 s** in two runs whose calibrations differ by 55 % (0.365 and 0.568 s): the
stage is reproducible in absolute seconds and the calibration is not, so the
same 345 s reads as 946 units in one run and 602 in the other.  The base tree's
two runs are **349.3 s** at load 1.79 and **478.5 s** at load 5.76.  So at
comparable load -- 345.4 s (load 1.55) against 349.3 s (load 1.79) -- the
repaired row's first plane is within 1.1 % of the base tree's, which is the
parity `ac941dc62b` could not establish from 957 and 1209 units; those two runs
had near-equal calibrations (0.369, 0.364) and first planes 353.3 s and 440.0 s,
so their disagreement was the 8.45 load of the second, not the calibration.  The
per-plane rate does not separate the trees either: 52.9 and 68.6 planes/s on the
repair against 55.2 and 59.6 on the base, with the rate drifting inside a run as
the machine's load moved (run 1 goes 72.2 -> 52.9 over 209 s while the load
average goes 1.5 -> 5.9).

## #541, the review round: the table declared, the release observed, and the census' display

| log | commit cited | result |
| --- | --- | --- |
| `541-review-release-red.log` | `ac941dc62b` | the release test of this round on the tree before the intern table has a lifetime: **2 failed** -- `assert reference() is None` reports `assert 70002 is None` (the strong `cached_method` holds the element) and the pickle test `False`.  The file and `tests/sets/conftest.py` were copied onto that tree, so the log's "2 modified paths" is exactly them |
| `541-review-green.log` | `18b34bd` | the description contract file with the two sets files: **8 passed in 0.52 s**, test lint loaded, 0 findings |
| `541-review-retain.log` | `309ab54` | the retention probe after the review's three source findings: 10^6 distinct naturals leave the table at **1 entry and +0.0 MiB** in 1.1 s; pickle protocols 0/2/5 and `copy`/`deepcopy` return the interned point; `loads(dumps(NN)) is NN` |
| `541-review-sets-dir.log` | `18b34bd` | `tests/sets` whole: **29 failed, 149 passed in 7.37 s**; the 29 are the tree's, and this round adds the description test |
| `541-review-modules-base.log`, `541-review-modules-fix.log` | `ac941dc62b` / `18b34bd` | `tests/modules`, where the span bases are consumed: **90 failed, 224 passed** on both trees, FAILED id sets identical under `sort` and `diff` |
| `541-review-description-red.log` | `ac941dc62b` | the description contract at the base: **1 failed**, `KeyError: 'description'` from `sage/structure/category_object.pyx`: a named set has no way to describe itself except by being displayed |
| `541-census-before.log`, `541-census-after.log` | `6b6cfe2` + the review fixes / `309ab54` + the description repair | one plane transport on T_Co, the same probe minutes apart: warm **2.29 -> 1.63 ms**, cold 2.38/2.34/2.26 -> 1.69/1.60/1.64 ms, wrapped-site median **2.53 -> 1.86 ms**, and `Lattices._repr_` **0.588 ms over 1.0 calls a plane -> 0.000 ms over 0.0 calls** |
| `541-census-final.log` | `18b34bd` | the same probe on the pushed commit: warm **1.73 ms**, `Lattices._repr_` still 0 calls a plane.  The cold and per-site figures are higher than `-after`'s on this run (cold 2.33/2.05/2.21 ms, wrapped-site median 2.92 ms) because the machine was carrying a load of 1.5-2.3; the warm median over 20 transports and the call count are the stable readings |
| `541-row11-repair.log` | `18b34bd` | the Otilde(T_Co) plane row once, at load average **0.55 1.19 1.89** on 4 CPUs (the lowest of the round), calibration **0.362 s**, `ROW_DEADLINE=540` inside 570 s inner / 590 s outer: **first plane at 292.3 s = 807 units**, **19 637 planes** by 565.2 s, **71.96 planes/s, 13.9 ms a plane** |

What the row run says.  The first-plane stage transports nothing, so it cannot
carry the repair: its 345.4 s and 341.8 s in the previous round's two runs and
292.3 s here differ by the machine, whose load was 1.55 and 2.50 then and 0.55
here.  The per-plane rate is where the repair lands, and 13.9 ms against the
previous round's 14.6 and 18.9 ms is the transport's -0.66 ms a plane on a plane
whose 14 ms are mostly the walk (the transport is 2.3 of them).  So the row at
low load is **292.3 s to the first plane and 72.0 planes/s**, and the census, not
the row, is the measurement of the repair.

## The review round's second pass (#541, 2026-11-15/16)

Commands are the previous section's: the same image, the same blanked `addopts`,
`-p qc_sage_session`, and `-p sage_extensions.testing.test_lint` where the lint
was loaded.  The comparison rule is the same: diff FAILED ids against a clean
worktree at the base commit, never absolute counts.

| log | commit cited | result |
| --- | --- | --- |
| `541r2-description-red.log` | `4c9e42cda0` | the description contract of this round on the tree before the repair: **2 failed** -- a second read renders the name again (`assert (1, 1) == (1,)`), and a filtered subset's display returns the description function itself (`assert <function ...> == "the even numbers below six"`) |
| `541r2-subobject-red.log` | `dad9e44187` | the span-basis contract on the tree before `18b34bd`: **1 failed**, `assert (1, 1) == (1,)` -- building `L.subobject_on` rendered the ambient lattice, and the test renders the lattice once by hand to show its guard is live |
| `541r2-green.log` | `3a3440f` | the description file with the subobject file: **3 passed in 1.18 s**, test lint loaded, 0 findings |
| `541r2-green-final.log` | `acbce0b` + the annotation | the three files of this round (description, subobject, one-span transport): **4 passed in 1.88 s**, test lint loaded |
| `541r2-sets-base.log`, `541r2-sets.log` | `4c9e42cda0` / `3a3440f` | `tests/sets`: 10 failed, **66 passed** and 102 errors against 10 failed, **67 passed** and 102 errors; FAILED/ERROR id sets identical, and the extra pass is the new filtered-subset test |
| `541r2-modules-base.log`, `541r2-modules.log` | same | `tests/modules`, where the span bases are consumed: 68 failed, 177 passed, 69 errors on both trees, FAILED/ERROR id sets identical |
| `541r2-span-red.log`, `541r2-span-green.log` | `4c9e42cda0` / `acbce0b` | one transport of the plane `<e_1, f_2>` of `U (+) U` by the summand swap: **2 span constructions -> 1**; red is `assert (1, 1) == (1,)`, green asserts the images of the basis lie in the transported plane and `e_1` does not |
| `541r2-transport-consumers-base.log`, `541r2-transport-consumers.log` | same | the four lattice files that transport planes (partial flag orbits, parabolic retention, line transporter, cusp lattices): 8 failed, 11 passed on both trees, FAILED id sets identical |
| `541r2-transport-probe.log` | `acbce0b` | the transport probe on `U (+) U`: **1** span construction a transport, the images of the basis in the moved plane, `e_1` outside it |
| `541r2-step-census.log` | `3a3440f` (before the transport repair) | the census of one coset step in the row itself, `setprofile` window at plane 150 at load **2.27**: interval between transports **12.86 ms** median, inside `transport_isotropic_object` **11.36 ms**, outside it **1.50 ms**; profiled, `primitive_isotropic_subobject` 43.7 and `ModuleMorphismMethods.image` 23.1 of the transport's 72.8 ms inclusive, `subobject_on` **2.0 calls a plane**, `_MorCategoryOf.Of` 129.6 calls |
| `541r2-row.log` | `acbce0b` | the row once at load average **0.86 2.66 2.92** on 4 CPUs (the lowest of the round), inner cap 540 s: **first plane at 309.6 s**, **19 000 planes by 534.7 s = 84.4 planes/s, 11.9 ms a plane**, the interval between transports a median of **9.17 ms early and 9.68 ms by plane 19 000** as RSS grows to 4.4 GiB, and **one span construction a plane** (19 447 for 19 000 planes, the 447 before the loop) |
| `541r2-calibration.log` | `1e3da25` | the fixed-work calibration of the previous section, run in its own process at load **1.54 2.09 2.41**: **0.362 s**, the same number as the previous round's row, so the two rows' rates are on one machine speed |

What the second pass measured.  The census contradicts the premise that the
walk is the per-plane cost: `splitting_isometries` materialises its lifts before
the first plane, and after it the step outside `transport_isotropic_object` is
1.50 ms while the transport is 11.36 ms.  Inside the transport the plane's span
was built twice -- once by `(self * obj.inclusion()).image()`, whose subobject
the transport only read the basis of, and once by
`primitive_isotropic_subobject`, where the plane is admitted -- so the repair
removes one of the two.  Against the pre-repair median interval of 12.86 ms the
post-repair early median is 9.17 ms (-29%, matching the image's 23.1 of 72.8 ms
profiled), and against the previous round's 13.9 ms mean at the same 0.362 s
calibration this round's mean is 11.9 ms.  The walk is unchanged: 309.6 s here
against 292.3 s there, at a higher load.

## The same repair on the tree that now carries `main` (#541, 2026-11-16)

`main` moved while the round ran: `0f7d1ad` brings three later commits, and
`7eb5248` removed `owned_parent_class`'s memoization, which is the per-object
class construction the transport's category objects use.  So the row was
measured again, before and after the repair, on that base: two runs of the same
probe minutes apart, whose span counts are the probe's own and whose loads are
in the logs.

| log | commit cited | result |
| --- | --- | --- |
| `541r2-green-merged.log` | `4adbc38` (the merge) | the three contract files on the merged tree: **4 passed in 1.90 s**, test lint loaded |
| `541r2-sets-merged-base.log`, `541r2-sets-merged.log` | `0f7d1ad` / `4adbc38` | `tests/sets` on the merged base: 10 failed, **66 passed** and 102 errors against 10 failed, **67 passed** and 102 errors; FAILED/ERROR id sets identical |
| `541r2-modules-merged-base.log`, `541r2-modules-merged.log` | same | `tests/modules` on the merged base: 63 failed, 182 passed, 69 errors on both trees, FAILED/ERROR id sets identical |
| `541r2-transport-probe-merged.log` | `4adbc38` | the transport probe on the merged tree: **1** span construction a transport, the basis images in the moved plane, `e_1` outside it |
| `541r2-calibration-merged.log` | `4adbc38` | the fixed-work calibration: **0.359 s** against 0.362 s before the merge, so the two bases are on one machine speed |
| `541r2-row-base-merged.log` | `0f7d1ad` (no repair) | the row at load **0.52 1.20 1.84**: first plane **330.5 s**, 13 000 planes by 502.1 s, the interval between transports a median of **11.65-11.69 ms**, and **26 543 span constructions for 13 000 planes = 2.04 a plane** |
| `541r2-row-merged.log` | `4adbc38` | the row at load **1.51 1.87 2.29**: first plane **327.3 s**, 14 000 planes by 491.7 s, median interval **10.44-10.45 ms**, **1.04 span constructions a plane** |
| `541r2-row-merged-second.log` | `4adbc38` | the same run again at load **1.34 1.31 1.65**: first plane **302.0 s**, **20 000 planes by 533.5 s (86.4 planes/s, 11.6 ms a plane)**, median interval **10.17 ms early and 10.43 ms by plane 20 000**, **20 546 span constructions for 20 000 planes = 1.03 a plane** |

What the pair says.  The load-free number is the span count: **2.04 -> 1.03**
constructions a plane, which is the contract the repair states.  The per-plane
time moved from a median of 11.69 ms at load 0.52 to 10.43 ms at load 1.34 --
-11% while carrying two and a half times the load -- and the two earlier
pre-merge runs, on a tree that still memoized `owned_parent_class`, moved
12.86 -> 9.17 ms (-29%).  The difference between the two percentages is the
memoization's removal: the category construction the transport still does per
plane grew, so the span it no longer builds is a smaller share of the step.  The
walk is untouched by the repair and its first-plane time is the machine's: 330.5 s
at load 0.52 and 302.0-327.3 s at 1.34-1.51.

What is still owed, and is not this repair's: the row's mean is worse than its
median because RSS grows to 4.4 GiB as the 189 720 orbits are retained, so the
walk's late planes pay for the memory it is keeping (9.17 -> 9.68 ms across
19 000 planes before the merge).  That growth is the row materialising every
orbit, not the transport.

The tree that was pushed is `6b4d623` (the merge of `0f7d1ad` and `#540`'s two
algebra commits onto this round's work).  `541r2-green-pushed.log` is the three
contract files on it: **4 passed in 1.74 s** with the test lint loaded.  The row
is measured on `4adbc38`, the same tree without `#540`'s two algebras commits,
which are not on the transport's path.

## #541 round 3: the walk step priced apart from the plane, and the primitivity decision repaired

Measured on `main` `4f540a2` and on the repair that follows it.  Each log records
its own tree, its own load and the exact command in its header.

| log | commit cited | result |
| --- | --- | --- |
| `541r3-walk-step-census.log` | `4f540a2` | the row's per-plane cost, unprofiled and phase by phase: the walk's first `next()` (its setup, the coset action and its 189720-point walk) **174.1 s** ending at 509.7 s; the next 198 steps a median of **0.775 ms** and flat (0.795 ms over 2..25, 0.764 ms over 194..199); the 199 transports a median of **10.073 ms** and flat (10.283 -> 9.902 ms); per plane over 80 planes `is_primitive` **5.425 ms** (54.2 %) of which `cokernel` **4.244 ms** (42.4 %), `subobject_on` 2.876 ms (28.7 %), `is_torsion_free` 0.392 ms, `refine` 0.165 ms, the rest 1.714 ms |
| `541r3-primitivity-red.log` | `4f540a2` | the new contract file red at the base tree: **1 failed, `assert 1 == 0`** — deciding a span's primitivity built one quotient module |
| `541r3-primitivity-green.log` | `80a135c` + the repair | the same file after the repair: **1 passed in 1.63 s**, test lint loaded |
| `541r3-plane-parts-base.log` | `4f540a2` | one plane of `T_Co`, 8 cold spans, at load **4.36**: `subobject_on` 3.408 ms, `is_primitive` **6.512 ms**, span + decision 9.920 ms |
| `541r3-plane-parts-repaired.log` | the repair (same tree) | the same probe at load **4.61**: `subobject_on` 3.199 ms, `is_primitive` **2.083 ms**, span + decision **5.282 ms** |
| `541r3-review-tests.log` | `80a135c` | the three contract files of the review round with the test lint loaded: **4 passed in 7.03 s** |
| `541r3-row-repaired.log` | `b383a80` | the row on the pushed tree at load **0.94**: first plane **306.7 s**, **26 506 planes by 516.6 s**, the ticks reading **127.98 planes/s (7.8 ms a plane)** at 486.5 s and **126.31 planes/s (7.9 ms)** at 516.6 s, peak RSS 3330 MiB; against the base's **86.4 planes/s and 11.6 ms a plane** (`541r2-row-merged-second.log`) that is +47 % planes a second and -32 % a plane, the walk's setup unchanged |
| `541r3-consumers-base.log`, `541r3-consumers-repaired.log` | `4f540a2` / `b383a80` | the nine `tests/lattices` files that consume the primitivity decision: **9 failed, 9 passed** in 177.62 s and **8 failed, 10 passed** in 172.65 s, and `diff` of the FAILED id sets is exactly `test_a_planes_primitivity_is_decided_from_its_coordinates.sage`, the contract file that is red at the base; no other id moved |

## #534: the characteristic classes of `A_{T_Co}`, decided on the form rather than by the engine's integer ring

The issue reports `DiscriminantClass.is_characteristic` answering `False` for every class of
`A_{T_Co}` because the owned value lifts are not members of Sage's `ZZ`. The lifted code is
not the tree's: `ef8fb06` (#348, 2026-11-11) asks the membership of the module's own base ring
and answers correctly. Every log below is at base `897e7f7` (tree `897e7f7`, adopted runtime,
`bash .scratch/wt534_launch.sh` and `bash .scratch/wt534_pytest.sh`), and each is named by what
it decided.

| log | commit cited | result |
| --- | --- | --- |
| `issue534-tco-characteristic-and-the-zero-class.log` | `897e7f7` | `[h/2].is_characteristic()` **True** in 258.95 s and `zero.is_characteristic()` **False** in 145.72 s, with an independent table over all 2048 classes from the gram data on 11 generators: 0 non-integral differences for `[h/2]`, 1024 for the zero class. Its `factor 1` column is a wrong polarisation (`q(g1+g2) = 1` where `q(g1)+q(g2)+b(g1,g2) = 0`): the form's relation is `q(x+y) = q(x)+q(y)+2b(x,y)`, which the same log prints on four pairs, and the `factor 2` column is the form's |
| `issue534-tco-class-table-and-cost.log` | `897e7f7` | the same table before the polarisation was pinned: 11 generators of order 2, `elements()` **2048 in 76.68 s**, 11 `q` evaluations 0.10 s and 11 `b` evaluations 0.30 s -- the enumeration is the cost, not the form values |
| `issue534-value-membership-in-both-integer-rings.log` | `897e7f7` | the issue's own observation, located: for the mixed classes that give the unreduced representatives `(0)/(4)` and `(4)/(4)`, `difference in ZZ` is **True** in the session's owned integers and **False** in `sage.rings.integer_ring.ZZ`, `0` included; `q([h/2]) - b([h/2], 0) = (1)/(2)` is in neither |
| `issue534-tco-isotropic-type-even-ordinary.log` | `897e7f7` | `get_isotropic_type(ep)` on `T_Co`: **Even ordinary** in 99.86 s, `q([ep/2]) = 0`, the divided class not characteristic -- the correct classification, since the one characteristic class `[h/2]` has `q = 1/2` |
| `issue534-five-small-forms-exact-agreement.log` | `897e7f7` | the method against an exact pass on `<2>`, `U(2)`, `diag(2,-2)`, `I_2(2)`, `U(2)+<2>`: the same characteristic class counted in each, in 0.72--4.05 s |
| `issue534-consuming-tests-green.log` | `897e7f7` | the two files that consume the method, `test_characteristic_discriminant_elements_archive.sage` and `test_isotropic_type_archive.sage`: **5 passed in 59.71 s**, slowest call 0.97 s |
| `issue534-reconfirmed-on-the-push-base.log` | `c41476f` (the record correction, on `55defcb`) | the same statements on the pushed tree: `<2>`, `U(2)`, `diag(2,-2)`, `I_2(2)`, `U(2)+<2>` each give the same single characteristic class by the method and by the exact pass (0.6--1.1 s a form); `zero.is_characteristic()` **False** in 104.86 s, `[h/2].is_characteristic()` **True** in 180.51 s, `get_isotropic_type(ep)` **Even ordinary** in 194.18 s |
## #541 round 4: the presented quotient's construction, the criterion over every PID, and the test repairs

Measured on `main` `897e7f7` and on the four commits that follow it (`90d57a1`,
`bb62b83`, `400940e`, `a6e6a31`).  Each log records its own tree, its own load and
the exact command in its header.  The four fixes answer the review of `80a135c`
and `de9a1d1`.

| log | commit cited | result |
| --- | --- | --- |
| `541r4-red-contract-base.log` | `897e7f7` | the new contract file, `test_a_presented_module_is_built_before_it_computes.sage`, red at the base: **2 failed, `assert 1 == 0`** twice -- constructing a cokernel materialized one relation matrix -- and the two primitivity tests passing beside it |
| `541r4-red-sets-base.log` | `897e7f7` | `test_a_set_is_named_or_described_and_not_both` red at the base: **1 failed, `DID NOT RAISE ValueError`** |
| `541r4-green-final.log` | `35a5ec9` | the same five files on the tree this round pushes, rebased again onto `7752e73` (`#552`, which landed while it ran): **9 passed in 1.36 s** with the test lint loaded |
| `541r4-green-rebased.log` | `7eef5b5` | the same five files after the rebase onto `5589af3` (`#538`'s character work): **9 passed in 1.29 s** with the test lint loaded |
| `541r4-green-contract.log` | `bb62b83` | the five changed and new test files with the test lint loaded: **8 passed in 2.19 s** |
| `541r4-cokernel-base.log` | `897e7f7` | one plane of `T_Co`, 6 cold spans, at load **2.65**: `inclusion.cokernel()` median **5.400 ms** (4.856..26.277); the part-by-part rows are warm reads of the same construction |
| `541r4-cokernel-repaired.log` | `bb62b83` | the same probe at load **2.65**: `inclusion.cokernel()` median **0.145 ms** (0.136..1.432) -- the construction stores the datum and computes nothing |
| `541r4-prim-base.log`, `541r4-prim-repaired.log` | `897e7f7` / `400940e` | `probe541prim.py` back to back at load **12.9** and **13.6**, under another session's job: `is_primitive` 5.619 ms and 10.869 ms with 2.7..77 ms spread in eight samples, `inclusion().cokernel()` 15.287 ms and 0.327 ms. The `is_primitive` pair is noise at that load and nothing is claimed from it; the cokernel pair is the same 37x reduction the load-2.65 run shows |
| `541r4-modules-base.log`, `541r4-modules-base-rerun.log` | `897e7f7` twice | the 41 `tests/modules` files that mention a cokernel, a presentation, an invariant factor or a torsion decision: **24 failed, 80 passed, 45 errors** in 155.61 s and again in 75.81 s, with identical FAILED/ERROR id sets -- a deterministic baseline |
| `541r4-modules-repaired.log` | `a6e6a31` | the same 41 files on the repaired tree: **24 failed, 80 passed, 45 errors** in 43.43 s, and `comm` in both directions against the base's id set is empty: no test moved |
| `541r4-modules-subset-repaired.log` | the repair before the last two, kept for the record | the six files that the recursion and the dropped torsion placement broke in a first shape of the fix, after their repair: **6 failed, 30 passed**, every failure one of the base's own |
| `541r4-lattices-base.log`, `541r4-lattices-repaired.log` | `897e7f7` / `a6e6a31` | the decision's consumers in `tests/lattices`: the two display/transport contract files and the primitivity file pass in both; `test_zero_isotropic_subobjects.sage` fails the same three ids in both. The repaired-tree run was killed inside `test_lattice_elements.sage` at the 260 s inner cap, at load 14 |
| `541r4-lattice-elements-repaired.log` | `a6e6a31` | `test_lattice_elements.sage` (six tests, all passing) and `test_chosen_target_primitive_embeddings.sage`, which did not finish inside 260 s at load 21 -- the gap the commit body names |
| `541rev-finding-1-red.log` | `961b68a` | the new contract file on that commit: **3 failed in 4.59 s**, each at the `from_module` torsion guard | 
| `541rev-forms-base.log` | `9a04b45` | `tests/forms/test_torsion_forms.sage` and `tests/forms/test_discriminant_subgroups.sage`: **8 failed, 12 passed in 4.09 s** | 
| `541rev-forms-240ce65.log` | `240ce65` | the same two files on the parent of the placement change: **5 failed, 15 passed in 4.51 s**; the three differences are the regression | 
| `541rev-forms-ctl.log` | `9a04b45` | `tests/forms` as one directory, unchanged: **43 failed, 40 passed, 58 errors in 95.98 s** | 
| `541rev-forms-fix1.log` | `961b68a` + the finding-1 repair | the same directory: **38 failed, 48 passed, 58 errors in 123.98 s**; the three new tests are among the 48, and the FAILED/ERROR id set differs from the control's by the five regression ids and nothing else | 
| `541rev-finding-2-red.log` | `ae8becb` | the second contract file on the finding-1 tree: **2 failed in 1.71 s**, each at `TypeError: base_ring (=Real Field) must be a ring or a semiring` | 
| `541rev-finding-2-green.log` | the repair's commit | the two contract files and the laziness file: **7 passed in 5.44 s** | 
| `541rev-finding-2-probe.log` | the repair's commit | `_coordinate_images` on a projection of `RR^2` reads `((1, 0), (0, 0))` and `_relation_images(RR^2)` reads `()` -- the two answers the review's probe found at `240ce65` and lost at `2bc5aff` | 
| `536r2-scan.log` | `2f8c801` | the walk's cell over 914 points of positive square: `U+U+A1` 434 (co-ordinates -3..3), `U+U+A1+A1` 200, `U+U+A2` 280 (-2..2): one, two or three normals, Stieltjes Gram, no cell refused |
| `536r2-records-base.log`, `536r2-records-fix.log` | `2f8c801`, `481184c` | four layers of `cusp_layer_enumerations` at `e_2+f_2` of `U+U+A1`: the normals, duals, cell candidates and whole-lattice candidates are identical in the two trees |
| `536r2-green-parent.log` | `2f8c801` + the test commit | the new test file with `main`'s `isotropic_orbits.py`: **2 passed in 33.88 s** |
| `536r2-green-fix.log` | `481184c` | the same file with the repair: **2 passed in 22.13 s** |
| `536r2-red-prewalk.log` | `5871adf`'s walk + the repair | the same file: **2 failed in 49.32 s**, each at the new refusal (`the roots through the controlling vector ... cut no cell there`), which is the walk's record of its cone being observable from the public call |
| `536r2-chambers.log` | `481184c` | the five Vinberg-chamber files: **2 failed, 17 passed in 106.77 s**, the two failures the reviewer found at the parent (`test_hilbert_basis_of_a_nonunimodular_plane_cone_exceeds_its_rays`, `test_lorentz_plane_has_one_reflective_wall_and_orthogonal_group_of_order_four`) |
| `536r2-image-base.log` | `2f8c801` | `test_the_isotropic_reduction_image.sage -k the_fourth_cusps_first_layers`, the call's one consumer: **1 passed in 524.76 s** |
| `536r2-image-fix.log`, `536r2-image-segfault.log` | `481184c` | the same test: reached the host's ten-minute ceiling twice (540 s and 560 s inner) without finishing; the third run segfaulted in `element()` converting a whole-lattice candidate at layer 1, under `ring_foundation._neg_` / `framed_free_modules._neg_`, a frame the repair does not touch |

## #521, the session binds its own names, and the dialect reads them

`sage_extensions.all` published six scalar rings and installed the research dialect
by handing its own `globals()` to two functions. The rings now belong to
`sage_extensions.rings`, which binds them in its body and declares them in
`__all__`, and the dialect registers at import and resolves the session's
vocabulary from the session module by `import *`'s own definition. The base is
the merge base `2f8c801`, a clean worktree; the repair is the source commit
`bc56fad`.

The pytest shape differs from this file's header in one way: the run keeps the
repository's two plugins and the durations,
`-o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget -p
sage_extensions.testing.test_lint -q --no-header --durations=5`, because the change
is a namespace the test lint also reads.

| log | commit cited | result |
| --- | --- | --- |
| `issue521-test-red.log` | `dbf2911` | the new test file alone, run in the base worktree (HEAD `2f8c801` with the two new test files in it, which is `dbf2911`'s content): **1 failed, 2 passed in 1.59 s** -- `AssertionError: assert ('AA', 'CDF', 'QQbar', 'RDF') == ()` |
| `issue521-test-green.log` | `bc56fad` (the two modified paths are this section's own files) | the same file: **3 passed in 2.11 s** |
| `issue521-test-base.log` | `2f8c801` | `tests/foundations`, `tests/rings`, `test_group_algebras.sage`, `test_coextension_of_scalars.sage`, `test_products_equalizers_and_fibre_products_of_lines.sage`: **54 failed, 161 errors, 153 passed in 245.45 s** |
| `issue521-test-repair.log` | `bc56fad` | the same selection: **54 failed, 161 errors, 156 passed in 372.51 s**; the 215 FAILED/ERROR ids are the same set test for test, and the three extra passes are the new file.  Same host, different wall times: the runs of this host vary by a third |
| `issue521-names-base.txt`, `issue521-names-repair.txt` | `2f8c801`, `bc56fad` | the session's public namespace, one name per line: **678 names against 677**, the difference being `ring_constructor_surface`, which the installer's dictionary had leaked into the session |
| `issue521-session.py`, `issue521-session-base.log`, `issue521-session-repair.log` | both | the sixteen scalar names against the ring package's exports (`identical=True` and `declared=True` for each here; six of them not on the package at all there) and the lowering of `M = Modules[ZZ]`, `R = ZZ[x]`, `T = Modules[k]`, which is the same text in both trees |
| `issue521-load.py`, `issue521-load-base.log`, `issue521-load-repair.log` | both | the scope a `load` writes into, holding the session's names and polluted with `ZZ` and `Integers`: the session's `ZZ` back, `AA`/`RDF`/`GF` present, the engine spellings gone, and `41 + 1` an owned 42 -- the same lines in both trees |
| `issue521-cpu.py`, `issue521-cpu-base-1.log`, `issue521-cpu-base-2.log`, `issue521-cpu-repair-1.log`, `issue521-cpu-repair-2.log` | both | CPU seconds to lower 200 assignments, five repetitions each: **0.0942 / 0.0832 s at the base against 0.0884 / 0.0817 s here**, so the per-assignment tree walk both trees run is the same work |
| `541rev-laziness-green.log` | the finding-3 commit | the reworked laziness contract: **2 passed in 1.00 s**, the construction's count 0 and the first request's above it | 
| `541rev-laziness-calibration.log` | `897e7f7` | the same file against the construction that computed: **2 failed in 7.91 s** at `assert 2 == 0` -- the instrument sees a construction that realizes its resolution, which the engine-matrix count alone did not | 
| `541rev-presented-base.log` | `2e9b362` | nine presented-module, torsion, localization and contract files: **8 failed, 2 passed, 9 errors in 19.29 s** | 
| `541rev-presented-fix.log` | the finding-4/5/6 commit | the same files: **8 failed, 7 passed, 9 errors in 38.28 s**; FAILED/ERROR id sets identical to the base's (`comm` both directions empty), the five extra passes are the new contract files | 
| `541rev-laziness-ordering.log` | the ordering repair | the laziness file beside the lattice primitivity file and the torsion archive: **3 failed, 4 passed in 9.34 s**, the three failures the archive's two-adic ones and the laziness contract green | 
| `541rev-consumers-after-citation.log` | the finding-8/9 commit | the primitivity, torsion-form, real-field and laziness contracts beside the selected-relation contract: **12 passed, 4 errors in 6.19 s**, the four errors the pre-existing test-lint findings in `test_the_selected_relation_morphism_contract.sage` | 
| `541rev-torsion-validator.log` | the validator's contract commit | `validate_torsion_claim` asked and not asked: **3 passed in 2.99 s** | 
| `541rev-final-forms-wt541rev.log`, `541rev-final-modules-wt541rev.log`, `541rev-final-lattices-wt541rev.log` | the last commit of this round | the three consumer suites on the repaired tree: **38 failed, 48 passed, 58 errors in 148.98 s** (`tests/forms`), **26 failed, 92 passed, 55 errors in 112.67 s** (the 48 `tests/modules` files that mention a cokernel, a presentation, an invariant factor or a torsion decision), and **1 failed, 9 passed, 4 errors in 289.95 s** (the primitivity, transport, content and chosen-target files) | 
| `541rev-final-forms-wt541ctl2.log`, `541rev-final-modules-wt541ctl2.log`, `541rev-final-lattices-wt541ctl2.log` | `901ff18` | the same three suites on main: **38 failed, 48 passed, 58 errors in 78.41 s**, **26 failed, 92 passed, 55 errors in 61.23 s**, and a run killed at its 540 s cap inside `test_chosen_target_primitive_embeddings.sage`. The forms and modules FAILED/ERROR id sets are identical between the two trees (`comm` both directions empty) | 
| `541rev-rebased-contracts.log` | the rebased tip before the push | the five contract files (torsion forms, inexact-engine coordinates, the torsion validator, laziness, lattice primitivity): **12 passed in 6.53 s** | 
| `542r2-reals-red.log`, `542r2-reals-green.log` | the finding-1 test commit, then its fix | one file, `tests/rings/test_reals_and_completions_hash_by_their_value.sage`: **1 failed, 3 passed in 1.99 s** at `8977add` (`assert 93032432 == 2` at `hash(RR(2)) == hash(ZZ(2))`), **4 passed in 3.79 s** at `32d9bd7` |
| `542r2-completion-red.log`, `542r2-completion-green.log` | the finding-2 test commit, then its fix | one file: **1 failed, 4 passed in 4.92 s** at `d6de023` (`assert 125752016330832 == 1`), **4 passed in 3.79 s** at `b7e9453` (the reals file), and the five completion files of this round: **5 failed, 8 passed, 4 errors in 13.53 s** |
| `542r2-completion-base.log` | `090a0d9` | the same five completion files on the base: **5 failed, 5 passed, 4 errors in 8.32 s**; the FAILED and ERROR ids are identical to the repaired tree's, the three extra passes being the new tests |
| `542r2-picard-red.log`, `542r2-picard-green.log` | the finding-3 test commit, then its fix | `tests/divisors/test_divisor_classes_hash_by_their_equality.sage`: **1 failed, 2 passed in 4.81 s** at `de0493a` (`hash(class of O)` -1793465262270530806 against the group's -2123201063562690755), **3 passed in 2.54 s** at `dfa197f` |
| `542r2-morphisms-red.log`, `542r2-morphisms-green.log` | the finding-4 test commit, then its fix | `tests/categories/test_structurally_defined_set_maps_hash_by_their_maps.sage`: **4 failed, 1 passed in 3.48 s** at `deb82b6`, **5 passed in 2.16 s** at `5bfbf23` |
| `542r2-modules-red.log`, `542r2-modules-green.log` | the finding-5a test commit, then its fix | `tests/modules/test_general_module_elements_hash_by_their_equality.sage`: **3 failed in 4.87 s** at `5b22e25` (three TypeErrors naming the three element classes), **3 passed in 3.47 s** at `ef6fc1f` |
| `542r2-schemes-red.log`, `542r2-schemes-green.log`, `542r2-schemes-base.log` | the finding-5b test commit, then its fix, and `090a0d9` | `tests/schemes/test_a_glued_scheme_morphism_hashes_by_its_endpoints.sage` alone: **1 failed in 4.56 s** at `f956ddb` (TypeError on the fold's hash); beside `test_glued_finite_affine_atlases.sage`: **4 failed, 3 passed in 5.20 s** at `2ca6141` against **4 failed, 2 passed in 5.72 s** on the base, the four FAILED ids identical |
| `542r2-lint.log` | the lint commit | `tests/rings/test_completion_arithmetic.sage` with the test lint: **4 passed in 5.20 s** at `3eebb4e`, where the file's TL01 at line 12 made it 4 setup errors |
| `542r2-consumers-sets-categories-{mine,base}.log` | the round's tip, and `090a0d9` | `tests/sets tests/functions tests/topology tests/categories`: **86 failed, 147 passed, 150 errors in 95.93 s** here against **86 failed, 146 passed, 150 errors in 73.17 s** on the base; 236 FAILED/ERROR ids, `diff` empty both ways, the extra pass the new categories test |
| `542r2-consumers-modules-divisors-{mine,base}.log` | the round's tip, and `090a0d9` | `tests/modules tests/divisors`: **104 failed, 220 passed, 69 errors in 103.66 s** here against **104 failed, 216 passed, 69 errors in 146.46 s** on the base; 173 FAILED/ERROR ids, `diff` empty both ways, the four extra passes the new tests |
| `542r2-consumers-reals-{mine,base}.log` | the round's tip, and `090a0d9` | the exact-real consumers (the real-division, owned-rings, division and rational-real files, the graded Lebesgue file, `tests/objects`): **95 failed, 163 passed, 86 errors in 151.81 s** here against the same counts in 182.23 s on the base, 181 FAILED/ERROR ids, `diff` empty both ways |
| `542r2-consumers-schemes-{mine,base}.log` | the round's tip, and `090a0d9` | nine scheme files that build morphisms (affine, the three gluing files, standard charts, relative spec, toric, pullback): **12 failed, 17 passed, 22 errors in 36.96 s** here against the same counts in 24.73 s on the base, 34 FAILED/ERROR ids, `diff` empty both ways |
| `542r2-rebased.log` | the rebased tip before the push | the six test files this round adds or changes: **21 passed in 6.71 s** |
| `542r2-probe-a.py` … `542r2-probe-l.py` | the base and the repair | the measurements behind the findings: `hash(RR(2))` against `hash(2)`, `hash(AA(2))` against `hash(2)`, the image of `1` in a completion against the ring's `1`, `FiniteOrderedSets` cardinalities, the two-point chain's four hash comparisons, the fold of the glued pair, and the specimens that do not build (`QuasiCoherentSheaves(scheme)(cover, …)`, the plane cubic's structure sheaf, the affine structure sheaf's `tensor_power`) |
## `#535` round 3: the Eichler gate, the decomposition family, and the displayed blocks (2026-11-16)

The round's two authorities for Eichler's hypothesis become one gate; the
family of indecomposable summands is decided by the same datum as
`is_decomposable` and refused where nothing decides it; the blocks of a
displayed Gram matrix are the Gram graph's components, taken as sublattices.
Runs are the launcher `.scratch/launch535r3test.sh` (`pytest -o addopts= -p
qc_sage_session -q --no-header`, the checkout bound at `/repos/sage-extensions`
with the shared `.git` bound at its host path, the port at `/work`) and
`.scratch/launch535r3lint.sh` (the test lint, same binding).  The tree column
names the commit the run was made on; a run made with the repair in the working
tree therefore names the commit before it.

| log | tree | result |
| --- | --- | --- |
| `535-r3-probe-gate.log` | `2f8c801` | the gate the round inherits: on `U + U + <1>`, `U + U + <3>`, `U + U + <-1>` `is_even` is False, `hyperbolic_index` is 2 and `eichler_criterion_applies` is False, while `_two_hyperbolic_planes` is True -- and each of the three takes the single-sign-character certificate before the criterion's gate, so both gates answer `NOSPLIT` on them. Primitive isotropic vectors of `U^2 + M` have divisibility one and trivial divided class, so no specimen at this scale reaches the class machinery. |
| `535-r3-probe-family.log` | `2f8c801` | the family the round inherits: `LK3` is `is_decomposable` True with 5 summands named `('U','U','U',None,None)`, the scrambled K3 is an `AtomicProposition` with **cardinality 1** and names `(None,)`, and the Gram graph of `LK3` cuts at `(2, 4, 6, 14)`. |
| `535-r3-red-family.log` | `2f8c801` | the new family contract: **2 failed in 13.99 s** -- `A_1^4` in the basis `e_1+e_2, e_2+e_3, e_3+e_4, e_4` has `is_decomposable` undecided, and the scrambled K3 does **not** raise (`DID NOT RAISE ValueError`). |
| `535-r3-fix-family.log` | the family's test commit + the repair | the family contract and the graph file: **8 passed in 10.88 s**. |
| `535-r3-red-graph.log` | `4089966` | the graph owner's components with a loop present: **1 failed, 3 passed in 11.56 s**, `ValueError: cannot add edge from 0 to 0 in graph without loops`. |
| `535-r3-red-blocks.log` | `2f8c801` + the round's test commits | the displayed-blocks contract: **2 failed in 8.08 s**, `AttributeError: no attribute 'inclusion'` -- the summands are fresh Gram lattices. |
| `535-r3-fix-blocks.log` | the blocks' test commits + the repair | the blocks contract and the graph file: **6 passed, 2 failed in 20.65 s**; the two failures are the family contract above, repaired in the next commit. |
| `535-r3-gate-tests.log` | the family's fix commit | the gate contract's tests, which have **no red state** (see the commit body): **10 passed in 54.30 s**. |
| `535-r3-consumers.log` | the gate's test commit + the repair | the ten files that consume the change: **42 passed, 2 failed in 97.02 s**. Both failures are pre-existing and touch no changed API. |
| `535-r3-base-preexisting.log` | `2f8c801` + the round's test commits | the same two files without these changes: **2 failed, 1 passed in 9.42 s**, the same two FAILED ids -- `(a1+a1).orthogonal_decomposition()` wants an `embeddings` argument and `a2.basis()` is not a lattice method. |
| `535-r3-owner-contracts.log` | the gate's test commit + the repair | `tests/lattices/test_lattice_database_owner_contracts.sage`: **11 passed, 1 failed in 152.05 s**; the failure is `hyperbolic_partner` on the odd binary lattice `[[1,0],[0,-1]]`, inside the presented module's iteration. |
| `535-r3-base-hyperbolic-partner.log` | `2f8c801` + the round's test commits | that test alone without these changes: **1 failed in 16.07 s**, the same id and the same frame. |
| `535-r3-heavy-stable-line.log` | the gate's fix commit | the two stable-line-orbit row files, `U(2) + <-6>` and `T_Co`: **2 passed in 1073.83 s (0:17:53)**. |
| `535-r3-lint.log` | the gate's fix commit | the test lint on the five touched test files: **5 files, 0 findings**. |
| `535-r3-docs.log` | the docs commit | the four files the round's docstrings name, after the docstring pass: **14 passed in 51.27 s**. |

The same runs on the commit this round pushed (`main` at `39c2bed`), after the last
rebase onto `8c4f5ba`:

| log | result |
| --- | --- |
| `535-r3-main-consumers.log` | the ten consuming files: **42 passed, 2 failed in 71.95 s** |
| `535-r3-main-owner-contracts.log` | `tests/lattices/test_lattice_database_owner_contracts.sage`: **11 passed, 1 failed in 119.95 s** |
| `535-r3-main-lint.log` | the five touched test files: **5 files, 0 findings** |
| `535-r3-main-heavy.log` | the two stable-line-orbit row files, `U(2) + <-6>` and `T_Co`: **2 passed in 1156.96 s (0:19:16)** |
| `535-r3-main-base.log` | the three ids above on `8c4f5ba` without this branch's commits: **3 failed, 1 passed in 16.00 s**, the same ids |
| `535-r3-main-docs.log` | `test_integral_hyperbolic_index_is_owned_by_the_lattice` after the docstring pass: **1 failed in 14.84 s**, the same pre-existing id |
| `536r2-rebased.log` | `4944d38` after the last rebase onto `7f36d57` | the new file and the five Vinberg-chamber files together: **2 failed, 19 passed in 52.33 s**, the two failures the same pre-existing ids |
| `536r2-rebased-90e3356.log` | `56cd171` after the rebase onto `90e3356` | the new file and the five Vinberg-chamber files: **2 failed, 19 passed in 141.09 s**, the same two pre-existing ids; this is the tree the round pushed |
| `525-r2-base-engineering.log` | `7f36d57` | `tests/engineering` without this round, the commit it is rebased onto: **11 failed, 14 passed in 147.84 s**.  The eleven are the two `test_polyhedral_engine_routes.sage` ids, the eight `test_the_timing_record_names_each_stage.py` ids, and `test_no_source_file_names_an_issue_number.py::test_no_source_file_names_an_issue_number`, which is red on the base tree's own `src/` -- and red for the second reason the review gave: it runs `git ls-files`, which exits 128 here too. |
| `525-r2-base-race.log` | `7f36d57`, an earlier pass of the same command | **12 failed, 13 passed in 40.36 s**: the eleven above and, newly red, `test_the_incidence_row_reports_a_broken_contract_apart_from_an_undecided_row.py::test_a_broken_contract_is_reported_apart_from_an_undecided_row`.  That id is a race and not a state: the driver's row step is called under a `0.01` s cap, and when the cap has not expired before the driver's first `stage()` the call reaches `timing.current_commit()`, whose `git -C <tree> rev-parse HEAD` exits 128 in a worktree mount.  Run alone it is **2 passed in 9.63 s**, and the later directory pass above is green on it. |
| `525-r2-fix-engineering.log` | `5812648` | the same directory with this round: **10 failed, 13 passed in 55.26 s**.  The FAILED ids are the base's eleven minus the scan's, one for one; the scan's file and its two tests are gone, so the base collects twenty-five and this tree twenty-three. |
| `525-r2-greps.log` | `5812648`, with `7f36d57` for the contrast | the contract's greps, each with its full output rather than a count: the number sign 0, the issue spelling in a path 0 (**17 at the base**), the word `issue` 0 (**18 at the base**), the `.tmp` run-log pointers 0, the `results/` notes 0.  The history vocabulary is printed line by line, so each remaining match can be read: they are the instrumental `used to build` and the engine's `may advertise`. |
| `525-r2-import.log` | `5812648` | every edited module imports in the pinned image: `sage_extensions.all` and the eight modules whose prose changed, 677 public names, exit 0. |
#541, round 5. The runs of this round name the commit they were taken on inside
each log, and every one was made in the adopted runtime with the worktree at
`/work` and `PYTHONPATH` carrying the port copy.
| log | commit | result |
| `541r5-red-torsion-placement.log` | `2f2fcad` (this round's base) plus the round's two test files | the new file and the rewritten claim file: **3 failed, 4 passed in 8.14 s**; the three failures are the placement refined from a computed `is_torsion()`, the torsion-form constructor refuting the claim it was asked to store, and the claim's validator answering on a module that claimed nothing |
| `541r5-green-torsion-placement.log` | the round's fix commits | the five affected files: **15 passed in 10.60 s** |
| `541r5-probe-base-placement.log` | `08322de` | a fresh `coker(5)` formed without a claim is in `FormModules(ZZ).FinitelyPresented().Torsion()`, and its construction costs 4 units of work, as does the claimed one |
| `541r5-probe-presented-construction.log` | the round's fix commits | cokernels over `ZZ` and `QQ`, a lattice plane quotient, a claimed torsion module with its elements, and `direct_sum_of_cyclics((2,3))` after the dead constructor parameters were deleted |
| `541r5-probe-matrix-space-containment.log` | the round's fix commits | a lattice inclusion's homset is **not** in `MatrixSpaces(ZZ)` while it does retain a coordinate matrix, so `MatrixSpaces` containment is not the discriminator finding F asks for |
| `541r5-rebased.log` | the same five files after the rebase onto `bbb0dd6`; the tree SHA it ran on is the first line of the log | **15 passed in 93.95 s** |

## `#543`: the cardinal and ordinal order-morphism rows, 2026-11-16

Seven repair commits on the base tree `e13a23c`, then this commit, which adds
nothing but these files.  A rebase re-identifies a commit — this branch was
rebased four times while main moved under it — so the rows name the trees they
ran on: the base tree, the branch's test commit of the row they belong to, its
repair, or the repair head (the last repair commit, the one this commit
follows).  Only the base carries a SHA, because only the base stays put.

Main advanced from `e13a23c` to `a2d1490` under the branch.  Of those rounds,
only two things touch a path a row below reads: eleven lines of arrow-hash
memoisation and a docstring in `set_categories.py`, which no order row reaches,
and a new `tests/rings/test_a_matrix_ring_divides_only_by_its_units.sage`.  The
`tests/rings` rows were taken before that file arrived and are a FAILED-id
comparison between the two trees they name, not a count on today's main.

Every row is `tests/sets/test_cardinal_and_ordinal_order_morphisms.sage` unless
it names another path, in the pinned image with `-p qc_sage_session -o addopts=`,
`PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work`, the worktree
bound at `/work`.  `-p sage_extensions.testing.test_lint` is added where the row
says so.

| log | tree | result |
| --- | --- | --- |
| `543-base-d1ab7fc-acceptance.log` | `d1ab7fc`, the tree the issue names | the file alone: **4 failed, 14 passed in 7.65 s** — the four rows the issue reports |
| `543-red-constant-sum.log` | the constant-sum test commit | the file with the constant-family row: **3 failed, 15 passed in 10.15 s**, at `assert ... indexed_sum(NN, cardinal(1)) == aleph0` |
| `543-fix-constant-sum.log` | its repair | the same file: **2 failed, 16 passed in 10.77 s** — the sum row green |
| `543-red-ring-ingress.log` | the ring test commit | the file with the split ring row: **2 failed, 17 passed in 9.01 s**, at `QQ(cardinal(7))` -> `TypeError: category() needs an argument`, `ring_foundation.py:1719` |
| `543-fix-ring-ingress.log` | its repair | the same file: **1 failed, 18 passed in 5.54 s** — the ring row green |
| `543-order-rows-lint.log` | the order-rows test commit | `test_the_order_morphism_is_empty_exactly_when_its_source_exceeds_its_target.sage` with the test lint loaded: **3 passed in 4.06 s**, no finding |
| `543-wellorder-validator.log` | the well-order test commit | the file: **19 passed in 7.74 s** |
| `543-hook-before.log` | the well-order test commit | the hook probe: the undecided cardinal comparison answers `Negation(not le((2)^(ℵ_0), ℵ_1))`, where the ordinal order answers `None` |
| `543-hook-after.log` | the repair head | the same probe: `None`, with `is_empty()` still the proposition and `ask` still `Unknown` |
| `543-acceptance-alone.log` | the repair head | the file alone: **19 passed in 12.11 s** |
| `543-both-files-alone.log` | the repair head | both order files: **22 passed in 9.76 s** |
| `543-sets-base.log`, `543-sets-head.log` | `e13a23c`, the repair head | `tests/sets` as one directory: **24 failed, 165 passed in 60.80 s** and **21 failed, 168 passed in 173.25 s**; the head's FAILED ids are the base's minus the three rows this round repaired, and nothing else |
| `543-objects-base.log`, `543-objects-head.log` | `e13a23c`, the repair head | `tests/objects` then the file in one process: **116 failed, 228 passed in 152.72 s** and **113 failed, 232 passed in 144.88 s**; the same difference and nothing else, so the file's rows pass after that prefix |
| `543-rings-base.log`, `543-rings-head.log` | `e13a23c`, the repair head before main's #541 round | `tests/rings` then the file: **78 failed, 292 passed in 275.38 s** and **75 failed, 296 passed in 756.89 s**; the same difference and nothing else.  The head's run took 12 min 37 s on a loaded host where the same selection had taken 175 s, overran the ten-minute bound, is recorded as it ran, and was not repeated |
| `543-mro-six-processes.log` | `d1ab7fc` | six fresh processes: `Cardinalities().Mor(2, 3)`'s MRO is `[OwnedCardinalityMor_with_category_with_category, Sets.ParentMethods, CardinalityMor...]` in all six, and `is_empty()` is the proposition in all six — the defect does not vary between runs |
| `543-mro-predecessors.log` | `d1ab7fc` | twelve constructions before the hom-set (`Sets().Mor(Δ2,Δ2).is_empty`, `Ordinals().Mor(1,2).is_empty`, `cardinal(2).Mor(3).is_empty`, `Sets().Finite()`, `Δ2.cardinality()`, `QQ(3)`, `m.cardinality()`, `m.unique_morphism()`, `m.base_category()`, `m.mor_category()`, and the cached hom-set again), each followed by a fresh `Mor(2, 3)`: the class, the two MRO positions and the answer are identical at every step — no earlier construction decides it |
| `543-baked-library-run.log` | `d1ab7fc`'s file, the image's own `sage_extensions` at `/repos/sage-extensions/src` (a copy at `cf656f8`) ahead of the tree's on `PYTHONPATH` | **4 failed, 14 passed in 12.10 s** — the same four rows, so importing the copy the image carries does not explain the reported pass either |

## #527 round 2: the completion at the zero ideal, and the specimen that tells its maps apart

Every row is `tests/rings/test_the_adic_inverse_system_and_its_limit_cone.sage`
unless it names another path, in the pinned image `/sage/.venv/bin/python`,
`-p qc_sage_session`, `addopts` blanked, the tree bound at
`/repos/sage-extensions`.  `-p sage_extensions.testing.test_lint` is added
where the row says so.  The two trees that are not the round's own are
`ac4ff63`, the commit before #527's first repair, and `bbb0dd6`/`a88e5cc`,
main as it stood while this round ran.

| log | tree | result |
| --- | --- | --- |
| `527-base-principal.log` | `ac4ff63` | the two principal-ideal tests alone, `-k principal`: **2 failed, 3 deselected in 15.63 s**, both `TypeError: object() takes exactly 0 positional arguments (1 given)` from `adic_inverse_system` at `commutative_algebra.py:3201` |
| `527-fix-principal.log` | the specimen's test commit | the file with the test lint loaded: **5 passed in 13.85 s**, no finding |
| `527-main-iso.log` | `bbb0dd6` | the isomorphism test alone, `-k zero_ideal`: **1 failed, 4 deselected in 11.18 s**, at `assert completion_map in Rings().Core().Mor(field, completion)` |
| `527-fix-iso.log` | the isomorphism's repair | the file with the test lint loaded: **5 passed in 11.26 s**, no finding |
| `527-base-rank.log` | `ac4ff63` | the rank-one test alone, `-k rank_one`: **1 failed, 5 deselected in 12.99 s**, the frame being `Free module on {[0], [1]} over QQ(i)` |
| `527-fix-rank.log` | the rank-one test commit | the file with the test lint loaded: **6 passed in 6.39 s**, no finding |
| `527-test-file-final.log` | `a88e5cc` plus the round's six commits | the file with the test lint loaded: **6 passed in 8.05 s**, no finding |
| `527-completion-probe.log` | the round's tree | `QQ(i)` at `(0)`: the map is a `CategoricalIsomorphism` in `Rings().Core().Mor`, both predicates `True`, `inverse()` round-trips `a`, `extended_ideal()` and `ideal_of_definition()` are the completion's zero ideal, and the system, the cone, the element constructor and `algebra_structure_morphism()` all return; at `QQ[x]` at `(x)` the map is a ring morphism and surjectivity stays undecided |
| `527-consumers-head.log` | the isomorphism's repair | `tests/rings/test_completion_inverse_system.sage`, `test_completion_arithmetic.sage`, `test_local_completions.sage`: **1 failed, 6 passed in 18.98 s** |
| `527-consumers-main.log` | `bbb0dd6`, same command | **1 failed, 6 passed in 18.08 s**, the same FAILED id (`test_completion_is_the_limit_of_the_truncations_by_powers_of_the_maximal_ideal`) |
| `527-completion-maps-base.log` | `ac4ff63` | `tests/rings/test_completion_maps.sage`: **4 failed, 1 passed in 17.42 s** |
| `527-completion-maps-main.log` | `bbb0dd6` | the same file: **4 failed, 1 passed in 12.94 s**, the same four FAILED ids |
| `527-zz-adic-completion-main.log` | `bbb0dd6` | `ZZ.adic_completion(2)` raises `AttributeError: 'int' object has no attribute 'ring'`; `ZZ.adic_completion(ZZ.ideal(2))` raises `RecursionError`; the resolved method is `ModulesWithChosenFinitePresentation.ParentMethods.adic_completion` |
| `527-zz-adic-completion-dispatch.log` | the round's tree | `ZZ` alone resolves the module owner's `adic_completion` (`QQ`, `QQ[x]`, `QQ(i)`, `Zp(5)` resolve the ring owner's), and `AdicCompletions().Local().an_object()` raises the `AttributeError` at `modules/pure/modules.py:4655` from `commutative_algebra.py:3036` |
| `527-literal-subtraction.log` | the round's tree | `(1 - x_hat).exact_source_expression()` and `(x_hat - 1).exact_source_expression()` are `None`, `(completion.one() - x_hat)` is `-x + 1`, and the induced map evaluates at the latter |
### #552, round 4: the third review's five findings

Red states are on the commit named, green ones on the fix commit directly above
the row.  Every run used one pytest process per file selection on the adopted
runtime (Sage 11.0.beta5, `/sage/.venv/bin/python`), the port repo at `/work`,
and the launcher `launch552r3.sh`.

| log | commit | result |
| --- | --- | --- |
| `552-r4-red-constructor.log` | `cd42311` (test only) | finding 1: `pytest -o addopts= tests/test_native_ring_constructions.py -k presented_algebra_constructor_states_the_quotient` is **1 failed, 8 deselected in 10.31 s** -- `AlgebrasWithChosenFinitePresentation(QQ)(P, (x*y,))` returned `P`. |
| `552-r4-fix-constructor.log` | `9a40378` | the same row: **1 passed, 8 deselected in 10.24 s**. |
| `552-r4-red-section-data.log` | `87c8d37` (test only) | finding 5: `pytest -o addopts= -p qc_sage_session tests/divisors/test_projective_section_rings.sage -k 'conic_section_ring_states or cox_ring_states'` is **2 failed** -- `section_scheme()` called the stored scheme. |
| `552-r4-fix-section-data.log` | `f5ea6f2` | the same rows: **2 passed, 3 deselected in 10.88 s**. |
| `552-r4-probe-consumers.log` | `f5ea6f2` | probe: the conic ring states its scheme and divisor, pieces 6 and 15, cached, six relations; `cox_scheme()` is the plane with three rays and `Cl = ZZ`; the coproduct's factors and the pushout's span and maps are their own; a plain quotient and the polynomial, tensor and affine semigroup rings keep their ambient categories. |
| `552-r4-probe-cover-map.log` | `f5ea6f2` | probe: the auxiliary presentation cover this round moved to a parameter still lifts -- `Z[x]/(2x)` gives `2x = 0`, `x != 0`, and the integer-torsion symmetric algebra keeps its polynomial presentation. |
| `552-r4-probe-contracts.log` | `7f36d57` | finding 2: every `ParentMethods.__init__` the presented and free constructors reach has a readable signature (no opaque level in the algebra, semigroup, free, section-ring, Cox and commutative-algebra modules), so the new refusal has no red test; the log is the record. |
| `552-r4-test-generators.log` | `a8c60d2` | finding 4: `-k line_section_ring_is_the_free_semigroup_algebra` is **1 passed, 28 deselected in 7.32 s**; the row is green because the implementation already multiplies by the semigroup law. |

The round's commits are rebased onto main before the push, and main moved while
the round ran, so the SHAs above name pre-rebase commits.  The rows below are
the same seven commits by subject at the head that was pushed:

- `test: the presented-algebra constructor states its relations (#552)`
- `fix: the presented-algebra constructor states the quotient, and one construction declares its callers (#552)`
- `test: the conic section ring records its scheme and its divisor (#552)`
- `fix: a level's construction data reach that level's own constructor (#552)`
- `fix: a level whose construction contract cannot be read refuses the datum (#552)`
- `test: the line section ring's generators are tied to their own points (#552)`
- `evidence: round 4's red and green runs (#552)` and this one

The pushed head's own SHA is the one the round's report names, and each log's
first lines record the tree SHA and the modified-path count it ran against.

| log | commit | result |
| --- | --- | --- |
| `552-r4-rebased-rows.log` | the rebased head | the four rows of this round on the rebased tree, one pytest process, `-p qc_sage_session`: **4 passed, 39 deselected in 8.63 s**. |
| `552-r4-rebased-probe.log` | the rebased head | the consumer probe of the threading repair at the rebased head: the conic ring states its scheme, its divisor and pieces 6 and 15, the Cox ring states its scheme, the coproduct's factors and the pushout's span and maps are their own, and the plain, polynomial, tensor and semigroup constructions keep their ambient categories. |

| log | commit | result |
| --- | --- | --- |
| `552-r4-head-rows.log` | the pushed head | the same four rows at the head this round pushes, one pytest process, `-p qc_sage_session`: **4 passed, 39 deselected in 5.49 s**. |
| `552-r4-final-rows.log` | the head that was pushed, after the last rebase onto main | the same four rows again: **4 passed, 39 deselected in 2.98 s**. |
| `issue521r2-red-base90.log` | the round's test commit | its two files at base `90e3356`: **1 failed, 5 passed in 4.10 s**, the failure being `test_a_subscript_of_a_name_the_file_does_not_bind_declares_no_generator` (`DID NOT RAISE NameError`) — the dialect created the name the test says is absent |
| `issue521r2-green.log` | the round's fix commit | the same two files on the repair head: **9 passed in 4.05 s** with the test lint loaded and no finding, where the nine are the two new files plus the two `tests/sets` files that write `Sets.Δ[aleph0]` |
| `issue521r2-ids-diff.log` | base `81b7bbd` against the round's fix commit | `tests/foundations tests/sets tests/rings`, one pytest process per tree: **58 failed, 246 passed, 252 errors** at the base and **58 failed, 249 passed, 252 errors** on the repair; the FAILED/ERROR id sets are 310 each and *empty* in both directions, so the three extra passes are the three new tests and nothing else moved |
| `issue521r2-corpus.py`, `issue521r2-corpus-diff.log` | base `81b7bbd` against the round's fix commit | one preparse per `.sage` file in the tree and a digest of the lowered text: 972 files at the base, 975 on the repair, and the diff is only the three files the round adds and the one it removes — no existing file's lowering changes |
| `issue521r2-research-rule.py`, `issue521r2-research-rule.log` | the rule the round replaces, before it was replaced | 1,033 `.sage` files under the research repository with `dzack_research.preamble.all` registered as a session module: **0** files whose lowering depends on the vocabulary the runtime used to copy, comparing the session rule's reading with the upstream rule's for each file |
| `issue521r2-mypy-base.log`, `issue521r2-mypy-fix.log` | base `81b7bbd`, the round's fix commit | `mypy --config-file /ci/tool-configs/mypy-sage.ini --no-incremental src/sage_extensions/language_runtime.py` inside the pinned image: **7 errors** in the file in both trees, the same seven (its untyped `Integer`, `RealNumber`, `matrix`, `factorial` and `ellipsis_*` definitions), reported at lines 50-118 and 48-116 |
## `#520` round 2: the incidence driver's outcomes, asked of real rows (2026-11-16)

The row step of `tests/coble_gamma_co_2_incidence_rows.py` answers with one
value: its status, the clause, cap or exception that decided it, and its counts.
The statuses of `tests/coble_row_status.py` carry their exit status (0 decided,
1 undecided or the whole-run budget spent, 2 a returned edge or relation that
breaks the contract, 3 a decided row whose counts differ, 4 the row step
raised), and the row's contract is a function of the relation it returned.  The
tree column names the round's tree by what it is: `base` is main at the round's
start (`e13a23cd9336437e18f2bbc7afc8c5a34778c6f7`), and a numbered tree is the
round's own commit at that position, with its repair in the working tree when
the run was made on a tree it was about to commit.  Every run is the
launcher `.scratch_pytest.sh` (`pytest -o addopts= -p qc_sage_session -p
sage_extensions.testing.test_lint`, the checkout bound at `/repos/sage-extensions`
with the shared `.git` bound at its host path, the port at `/work`) or
`.scratch_launch.sh` for a probe script.

| log | tree | result |
| --- | --- | --- |
| `520-r2-red-tests.log` | `base` | the round's first three tests: **3 failed in 25.91 s**. A cap of 0 s is `setitimer(ITIMER_REAL, 0)`, so the row is computed and reported `DECIDED`; `SO(U(2))`'s refusal escapes `run_row` as `ArithmeticError`; the module has no `row_contract`, so a relation cannot be handed to the contract. |
| `520-r2-fix-tests.log` | tree 2 plus its repair | the same three on the repaired row step: **3 passed in 6.85 s**. |
| `520-r2-driver-process.log` | tree 2 plus its repair | the driver as a process: `--cap 0` prints the lattice line and `[O(T_Co)] undecided: its cap of 0 s is spent before the call`, exit 1, in 6.6 s; `--cap 600 --budget 700` prints `[O(T_Co)] undecided: the row did not return inside its 600 s cap`, exit 1, in 613.5 s -- the first row's call starts and runs, and the alarm reaches it where Python holds control. |
| `520-r2-red-coverage.log` | tree 2 | the coverage statement: **1 failed, 4 passed in 20.46 s**. The row of `U + <-2>` -- one line cusp, no isotropic plane, no edge -- is reported `CONTRACT_VIOLATION` with detail `line cusp 0 carries no edge`. |
| `520-r2-fix-coverage.log` | tree 4 | the five tests of the file, durations printed: **5 passed in 19.04 s**, the slowest call 5.22 s. |
| `520-r2-gate-engineering.log` | tree 4 | the directory that holds the test and its harness: **2 failed, 26 passed in 277.74 s**. |
| `520-r2-base-engineering.log` | `base` | the same two files whose ids fail, without this round: **2 failed in 18.80 s**, the same FAILED ids (`test_polyhedral_engine_routes.sage`'s two, `AttributeError: ... no attribute 'basis'`). |
| `520-r2-fixture-costs.log` | tree 4 | what each candidate fixture for the refusal costs: `[[0]]` degenerate 1.19 s (`AssertionError`, the Witt index of a degenerate form), `[[2]]` and `A1.SO` decided with no cusp in 0.14/0.11 s, `diag(1,-1).SO` 4.91 s, `(U+U).Aut` 6.61 s (`TypeError` from `finite_ordered_sets.py`, the unhashable `CuspIncidence`), `U(2).SO` 2.06 s (`ArithmeticError`, the stabilizer image not certified). `U(2).SO` is the fixture the test uses. |
| `520-r2-tip-tests.log` | the round's evidence commit, after the rebase onto the main it is pushed on | the five tests of the file, durations printed: **5 passed in 14.83 s**, the slowest call 3.35 s. |
| `520-r2-tip-engineering.log` | the round's evidence commit, after the rebase onto the main it is pushed on | the directory that holds the test and its harness, after the rebase: **2 failed, 24 passed in 94.49 s**, 26 collected -- the base's 21 passed plus this file's 5, which replace the two the previous round left there. |
| `520-r2-base-engineering-rebased.log` | `fb74227`, the base the round is rebased onto | the same directory without this round: **2 failed, 21 passed in 95.74 s**, 23 collected, the same two FAILED ids. |
## #554, the review of `8e7ba2613e`/`08322dee5d`: the double dual is the primal lattice, the dual is not

`08322dee5d` decided containment, equality and the hash of two polytopes by asking whether the other's
category has `Sets().Subobjects(self.ambient_space())` among its immediate supercategories.
`ConvexPolytopes.ambient_space()` is `QQ.free_module(lattice.module_generating_set())`
(`polytopes.py:542`), so the space is keyed by the *labels* of the lattice and not by the lattice: `M`,
its dual `M^*` and every rank-2 lattice on the labels `{0, 1}` share one space, and the square of `M`
was thereby compared with the diamond of `M^*`, a subset of another space. The repair lands the one
identification that is canonical, at its owner: `polar_dual` of a polytope framed by a dual lattice
frames its result by the primal, through the evaluation isomorphism
`Modules(ZZ).dualization().double_dual_morphism(M)`, and the relations route again on the category of
the lattice (`other in ConvexPolytopes(self.ambient_lattice())`), so an operand of another kind is not
asked for its `ambient_category()` and two lattices are not identified with each other.

Still to be filed by the owner, and not repaired here: `ConvexPolytopes.ambient_space()`
(`polytopes.py:542`) and `RationalPolyhedralCones.ambient_space()` (`polyhedral_cones.py:231-233`) key
the rational space on the lattice's generating-set labels, so two lattices with the same labels share
one space. With the three relations no longer routed on the space that is latent, but it is wrong: the
space a polytope lies in is `M tensor QQ`, and `M` is the lattice.

| log | commit cited | result |
| --- | --- | --- |
| `554-double-dual-red.log` | `1488acf` + the test commit of this round | `tests/schemes/test_polytopes.sage -k double_polar_dual`: **1 failed, 5 deselected in 2.55 s** (test lint loaded, no finding), at `assert doubled.ambient_lattice() is lattice`: the double polar dual's frame is the dual of the dual, `(M^*)^*`, not `M` |
| `554-double-dual-main-probe.log` | `1488acf` | the defect on main: `doubled.ambient_lattice() is M` **False**; `diamond.is_contained_in(square)` **True** and `doubled == square` **True** (the two spaces identified, so the vertex test and the equality ran across them); `square == 1` **raises** `AttributeError: 'int' object has no attribute 'ambient_category'`, and `square == None` likewise; `polar` and the double polar's engine vertices `(±1, 0)`/`(0, ±1)` and `(±1, ±1)` |
| `554-double-dual-main-probe.py` | -- | the probe: the lattice, the dual, the double dual and their labels; `double_dual_morphism`'s codomain and its images of the basis; the four relations and the two equality operands that are not sets |
| `554-double-dual-green.log` | `1488acf` + both commits of this round | the same selection with the repair: **1 passed, 5 deselected in 1.86 s** (test lint loaded, no finding) |
| `554-double-dual-repair-probe.log` | `1488acf` + both commits of this round | the repaired contract: `_primal_lattice_of_a_dual` is `None` on `M`, `M` on `M^*`, `M^*` on `(M^*)^*` and `None` on the endomorphism Mor module (its target is not the regular module); the diamond is framed by `M^*`, the double dual by `M` and the third polar by `M^*` again; `square` and the double dual contain each other, are equal and have equal hashes; `polar.polar_dual() == square` **True**; `diamond` and the square answer each other the proposition `is_subset(...)`; `square == 1`, `== None` and `== ()` are **False**; inside `M^*` the four points `(1,0), (0,1), (-1,0), (0,-1)` are the diamond, equal to it, with its hash, and contained in it |
| `554-double-dual-repair-probe.py` | -- | the probe: the predicate on the primal, the dual, the double dual and an endomorphism Mor module; each polar dual's frame; containment, equality, hash and the two operands that are not sets; and the relations inside the dual lattice |

The round was rebased onto `9ddf7f5` before it was pushed, and the two rows below are the same
selection on that base and on the rebased head.  `polytopes.py` and `tests/schemes/test_polytopes.sage`
are byte-identical at `1488acf` and at `9ddf7f5` (`git diff --stat 1488acf 9ddf7f5 --` those two paths
is empty), so the red above is the red of the base as well; the row at `9ddf7f5` re-runs it there.

| log | commit cited | result |
| --- | --- | --- |
| `554-double-dual-red-on-base.log` | `9ddf7f5` (main, the push base) + this round's test only | the selection: **1 failed, 5 deselected in 3.41 s** at `assert doubled.ambient_lattice() is lattice` |
| `554-double-dual-green-on-head.log` | the rebased head of this round, clean tree | the selection: **1 passed, 5 deselected in 1.03 s** |
| `554-double-dual-green-on-pushed-head.log` | `67dd108`, the head this round was pushed from, clean tree | the same selection after main advanced to `26bdef1`: **1 passed, 5 deselected in 1.44 s**; neither `polytopes.py` nor the test file differs between `1488acf`, `9ddf7f5` and `26bdef1` |

## `#517` round 3: the retained sweep's regression, the discarded words, and the derived families, 2026-11-16

One file per run, in the pinned runtime (Sage 11.0.beta5, port tree `991b88b0`),
through `.scratch/wt517r3_pytest.sh`:
`run.sh -w /work`, `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`,
`/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.test_lint`.
`b54acd7` is the tree before the repair of the issue's defect; `1488acfb` is this
round's base on `main`.

| log | tree | result |
| --- | --- | --- |
| `517r3-f1-red-at-b54acd7.log` | `b54acd7`, where the defect lives | `test_a_searched_orbit_carries_no_sweep.sage` alone: **1 failed in 2.42 s** — the searched orbit of `5` carries `_retained_transitions` and `_retained_transition_augmentation` beyond the same `G`-set built directly |
| `517r3-f1-green-at-30cfb61.log` | `30cfb61`, the test commit | the same file alone: **1 passed in 2.13 s** |
| `517r3-f2-red-at-03271a9.log` | `03271a9` | `test_the_orbit_of_a_seed_is_the_set_its_sweep_reached.sage` alone: **1 failed in 3.80 s**, at `orbit is g_set` |
| `517r3-f2-green-at-16d99a4.log` | `16d99a4`, its repair | that file with the two #517 files and the six-test orbit-action file: **8 passed in 3.28 s** |
| `517r3-f3-red-at-e409a63.log` | `e409a63` | `test_each_derived_family_is_computed_once.sage` alone: **2 failed in 4.76 s** |
| `517r3-f3-green-at-7927ef8.log` | `7927ef8`, its repair | the four #517 files together: **10 passed in 6.47 s** |
| `517r3-probe-answers-at-b54acd7.log`, `517r3-probe-answers-at-1488acfb.log` | `b54acd7` and `1488acfb` | `517r3-probe-answers.py` on the same specimens (C(3) regular and beside a fixed point, S(3) conjugation, S(3)/<(1 2)>, a counting action): every public answer of the defective tree is the repaired tree's, and the two that differ are `orbit is g_set` (the discarded words) and the `drop_trivial` family (repaired earlier in the issue). The retained table agrees with the orbit's action wherever it is read, so the retained-state defect shows no wrong answer, only carried state |

## `#524` round 2: the placement claim's red, at the parent `a20a385` was diffed against, 2026-11-16

`a20a385` claimed that `_discriminant_module`'s bare cokernel raised `ValueError` out of
`TorsionQuadraticFormModules.from_module`.  That mechanism is not at its parent: `26d2fe2` had already
replaced the two placement reads with `_finitely_presented_torsion(module)`
(`form_modules.py:3442`, `:3645`), and the call it names answers there — `discriminant_group()` of
`U(2) + <2>` in **0.25 s** and its `twist(-1)` in **0.05 s** at `bf4388a`, the parent `a20a385` is
diffed against.  The defect the placement does repair is the one below, and this round lands the red
test `a20a385` lacked: `A_L` is outside the torsion placement its own construction declares
(`DiscriminantModules.super_categories`, `discriminant_modules.py:70`), so it answers `cardinality()`
and has no `elements()` at all.

One file per run, in the pinned runtime (Sage 11.0.beta5, port tree `991b88b0`), through
`.scratch/wt554_tests.sh`: `run.sh -w /work`,
`PYTHONPATH=/repos/sage-extensions/src:/ci/tool-artifacts/pytest_plugins:/work/src:/work`,
`/sage/.venv/bin/python -m pytest -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint -p qc_sage_session --no-time-gates`.
`bf4388a` is `a20a385`'s parent in `main`; `discriminant_modules.py`, the two `form_modules.py` guards
and the test file are byte-identical at `6f337e9` (the reviewer's named parent) and at `bf4388a`
(`git diff --stat 6f337e9 bf4388a --` those three paths is empty), so the red below is the red of the
parent the review names.

| log | commit cited | result |
| --- | --- | --- |
| `524r2-walk-red-at-bf4388a.log` | `bf4388a` + this round's test only | `tests/forms/test_a_torsion_cokernel_carries_its_torsion_forms.sage -k walks_the_classes`: **1 failed, 3 deselected in 1.14 s**, at `classes = module.elements()`: `AttributeError: '_SelectedFinitePresentationModules.parent_class[_PresentedModule].ObjectType' object has no attribute 'elements'` |
| `524r2-walk-green-at-3fae3b5.log` | `3fae3b5` (main, the push base) + this round's test only | the same selection: **1 passed, 3 deselected in 0.69 s** |
| `524r2-stated-valueerror-absent-at-bf4388a.log` | `bf4388a` | the mechanism `a20a385` states, probed: `discriminant_group()` of `U(2) + <2>` built in 0.25 s, its module `is_torsion()` True, `_finitely_presented_torsion()` True, `twist(-1)` in 0.05 s — no `ValueError` |
| `524r2-stated-valueerror-absent-at-3fae3b5.log` | `3fae3b5` | the same probe on `main`: the same answers, with the module in `Torsion()` |
| `524r2-walk-green-at-82cad5b.log` | `82cad5b`, the rebased head this round is pushed from, clean tree | the same selection after `main` advanced to `4936110`: **1 passed, 3 deselected in 2.39 s** (load 19.91) |

## `#523` round 3: the matrix inverse at any two endpoints, once, with its hypotheses (2026-11-16)

One file per run, in the pinned runtime (Sage 11.0.beta5, port tree `991b88b0`),
through `.scratch/launch523.sh`: `run.sh -w /work`,
`PYTHONPATH=/repos/sage-extensions/src:/ci/tool-artifacts/pytest_plugins:/work/src:/work`,
`/sage/.venv/bin/python -m pytest -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint -p qc_sage_session --no-time-gates --durations=0`.
`5ce18d3` is the test commit, `63367f9` its repair, and the probe ran on that
tree.  Both were rebased from `49361108d6` onto `ab2e435`; the three paths they
touch are identical between the two commits, so the runs are the pushed tree's.

| log | tree | result |
| --- | --- | --- |
| `523r4-red-at-5ce18d3.log` | `5ce18d3`, clean tree | `tests/rings/test_a_matrix_ring_divides_only_by_its_units.sage` alone: **2 failed, 7 passed in 1.92 s** — `f.inverse()` for a distinct-endpoint map over Z/4 raises `AssertionError: cannot compute the kernel` while `~f` answers, and `a.determinant() is a.determinant()` is False (`assert 1 is 1`) |
| `523r4-green-at-63367f9.log` | `63367f9`, clean tree | the same file alone: **9 passed in 1.51 s** |
| `523r4-probe-at-63367f9.log`, `523r4-probe.py` | `63367f9`, clean tree | the deciding expressions of the issue, one per line with its wall time: division by a unit and by a nonunit over ZZ, Z/4 and Z[x]; the distinct-endpoint inverse over Z/4 with both composites the identity; the empty and the rectangular matrix; `inverse() is inverse()`, `determinant() is determinant()` and `inverse_of_unit() is inverse()`; `A @ ~A` the identity over QQ and ZZ in ranks 2, 4, 6; the rank-one matrix space over the noncommutative M_2(ZZ), whose three spellings of the inverse all take the kernel route |

## `#523` round 3, re-taken: the matrix inverse at any two endpoints, once, with its hypotheses (2026-11-16)

The two commits were rebased from `ab2e435` onto `eb5baa8`, which changes their
ids and not their content (`git diff ab2e435 eb5baa8` over the two source files
and the test file is empty), so the three runs are taken again at the commits
being pushed and named by what they are.  `f7d2e12` is the test commit,
`e5c7a25` its repair, and the probe ran on that tree.  Same runtime and command
shape as the section above; `523r4-probe.py` is the probe.

| log | tree | result |
| --- | --- | --- |
| `523r3-red-test-commit.log` | `f7d2e12`, clean tree | `tests/rings/test_a_matrix_ring_divides_only_by_its_units.sage` alone: **2 failed, 7 passed in 3.09 s** — `f.inverse()` for a distinct-endpoint map over Z/4 raises `AssertionError: cannot compute the kernel` while `~f` answers, and `a.determinant() is a.determinant()` is False (`assert 1 is 1`) |
| `523r3-green-fix-commit.log` | `e5c7a25`, clean tree | the same file alone: **9 passed in 2.57 s** |
| `523r3-probe-fix-commit.log` | `e5c7a25`, clean tree | the deciding expressions of the issue, one per line with its wall time: division by a unit and by a nonunit over ZZ, Z/4 and Z[x]; the distinct-endpoint inverse over Z/4 with both composites the identity; the empty and the rectangular matrix; `inverse() is inverse()`, `determinant() is determinant()` and `inverse_of_unit() is inverse()`; `A @ ~A` the identity over QQ and ZZ in ranks 2, 4, 6; the rank-one matrix space over the noncommutative M_2(ZZ), whose three spellings of the inverse all take the kernel route |
## `#556` round 2: the conjugate's pair, its engine and its constructor, 2026-11-16

The review of the pushed round (`511b11a`) named six defects in the conjugate
subgroup construction.  The reds are on `3fae3b5` (the `main` this round was
rebased onto), the repairs on `76c5251`, the consumer tests the changed
semantics supersede on `76851e6`.  Runs are one file per process under the
adopted runtime, through `.scratch/wt556r_tests_one.sh`:
`run.sh -w /work`, `PYTHONPATH=/repos/sage-extensions/src:/ci/tool-artifacts/pytest_plugins:/work/src:/work`,
`/sage/.venv/bin/python -m pytest -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint -p qc_sage_session --no-time-gates`, and the
probes through `.scratch/wt556r_launch.sh` on the same image.

| log | commit cited | result |
| --- | --- | --- |
| `556r2-red-five-at-3fae3b5.log` | `3fae3b5` + this round's tests only | the four files of the subject: **5 failed, 4 passed in 7.06 s**, one failure per finding: `left is right` (the law at a normalizing element), `AttributeError: ... no attribute 'conjugated_subgroup'`, `TypeError: _GroupEngine.__call__() takes 2 positional arguments but 3 were given` (the stored pair shadowing the operation), `AssertionError: cannot compute O(...) as a finite group` (the engine asked at construction), and `AssertionError` at `groups.py:321` (`_element_to_engine` refusing a non-GAP element) |
| `556r2-green-nine-at-76851e6.log` | `76851e6`, clean tree | the same four files: **9 passed in 1.92 s** |
| `556r2-consumers-red-at-76c5251.log` | `76c5251`, clean tree | the seven consumer files of the subgroup constructions: **3 failed, 23 passed, 7 errors in 16.53 s** -- the three clauses that read the fixed point as object identity, and the seven errors are `tests/lattices/test_cyclic_normalizers.sage`, whose test-lint findings are in its own source (its imports, `len`, `generators`) and are not this round's |
| `556r2-consumers-green-at-76851e6.log` | `76851e6`, clean tree | the same seven files: **26 passed in 15.58 s** |
| `556r2-probe-six-at-3fae3b5.log` | `3fae3b5`, clean tree | `556r2-probe-six.py`: all six findings as the review states them -- `h.H` is `H` itself and carries no pair, `g.(h.H) is (gh).H` False, the conjugate kind's stored pair reached instead of its operation (`TypeError`), the abelian invariant engine refused at `_element_to_engine`, `O(U)` refused by `_assert_definite_over_integers` at construction, and one non-fixed finite conjugate costing **2** `libgap.ConjugateSubgroup` calls before any order is read |
| `556r2-probe-six-at-76851e6.log` | `76851e6`, clean tree | the same probe: the law True, the pair retained, the transported trivial subgroup of order 1, the abelian conjugate of order 2 with its generator in it, `O(U)` formed and `g^-1.(g.H) is H`, one engine conjugation per pair and none at construction (**0** forming, **1** on the first request), and the two construction data read as **required** |

Correction of the measurement stated in `76c5251`'s body: that body says one
fresh non-fixed conjugate of `S(4)` "costs one `libgap.ConjugateSubgroup` call
(the counter reads 1; reading its order costs no second one)".  Measured on the
tree it names, forming the conjugate costs **none** (the engine is realized on
first request) and the first request for its order costs **one**; the pair is
not conjugated twice, which is what the sentence was about, but the count is
read at formation in the sentence where the probe reads it at the order.  On
`3fae3b5` the same specimen reads **2** before anything is asked of the answer:
the deleted hook's equality test and the construction each called
`libgap.ConjugateSubgroup` once.

The round was rebased onto `eb5baa8` before it was pushed, so the commits the
table above names by their pre-rebase ids are these on the pushed history:
`76c5251` (the repair) is `a06e035`, `76851e6` (the two tests the review's
semantics supersede) is `555fae7`, and the two test commits keep their place
before it (`3c20c57` is `3af3c4d`).  The rebase took in `main`'s own changes
since `3fae3b5`; of the files this round edits, only `groups.py` differs
between the pre-rebase tip and the pushed one, and only in the `_TransversalCoset`
rendering docstring `main` rewrote, which no commit of this round touches.  The
three runs below are the same selections and the same probe on the rebased tree,
so the evidence covers the pushed code and not only the pre-rebase tree.

| log | commit cited | result |
| --- | --- | --- |
| `556r2-green-nine-at-89d0b4b.log` | `89d0b4b`, clean tree (the rebased tip) | the four files of the subject: **9 passed in 2.61 s** |
| `556r2-consumers-green-at-89d0b4b.log` | `89d0b4b`, clean tree | the seven consumer files: **26 passed in 18.34 s** |
| `556r2-probe-six-at-89d0b4b.log` | `89d0b4b`, clean tree | the six findings' probe: the same answers as `556r2-probe-six-at-76851e6.log`, including 0 engine conjugations forming a conjugate and 1 on the first request for its order, and both construction data read as required |

`main` moved twice more while this round was being pushed, and the round was
rebased each time; the ids in the two notes above are the ids of the
`eb5baa8`-based history.  The pushed history is `2492647` (the reds' tests),
`c591644` (the repair), `71189dd` (the two tests the review's semantics
supersede), `2a15d9f` and `cf6ba0b` (these two notes).  The runs that cite
`89d0b4b` are runs on a tree whose `src/sage_extensions/categories/group` and
`tests/groups` are byte-identical to the pushed tip's (`git diff --stat
89d0b4b cf6ba0b -- src/sage_extensions/categories/group tests/groups` is
empty), so they cover the code that was pushed.
## `#543`, round 6: the review's rows, re-taken, and one row corrected, 2026-11-16

Every row is the pinned image (`/sage/.venv/bin/python`), `-p qc_sage_session`,
`addopts` blanked, the worktree bound at `/work`, and
`PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work`, through
`.scratch/launch543.sh`.  `-p sage_extensions.testing.test_lint` is added where
the row says so.  The trees: `ab2e435`, `main` as this round is built on;
`d1ab7fc`, the tree the issue names; and the repair head, the last commit this
evidence commit follows.

| log | tree | result |
| --- | --- | --- |
| `543r2-red-at-ab2e435.log` | `ab2e435`, with this round's two test files | the two files: **1 failed, 22 passed in 12.01 s** — `test_the_rings_read_the_finite_cardinal_seven_as_seven`, at `PredicateSubrings().an_object()(cardinal(7))`, `TypeError: category() needs an argument` from `Category.__contains__` |
| `543r2-red-at-d1ab7fc.log` | `d1ab7fc`, with this round's order file | `test_the_order_morphism_is_empty_exactly_when_its_source_exceeds_its_target.sage` alone: **4 failed in 3.84 s** — the issue's four rows, the new order row among them |
| `543r2-green-both-files.log` | the repair head | the two files: **23 passed in 2.42 s** |
| `543r2-alone-cardinal.log`, `543r2-alone-order.log`, `543r2-reverse-pair.log` | the repair head | each file alone (**19 passed in 2.69 s**, **4 passed in 1.49 s**) and the pair in the other order (**23 passed in 3.46 s**): the issue's acceptance clause, in the orders a process can be given here |
| `543r2-lint-at-ab2e435.log`, `543r2-lint-at-head.log` | `ab2e435`, the repair head | the two files with the test lint: **4 passed, 19 errors in 3.81 s** and the same.  The finding sets are equal line for line; every finding is the base tree's own (TL08 `finite_ordered_set`, TL01 module imports, TL10 `len`, TL09, TL04, TL03), and this round's rows add none |
| `543r2-probe-at-ab2e435.log`, `543r2-probe-at-head.log` | `ab2e435`, the repair head | `543r2-probe.py` on the same specimens: the 36 answers are identical but one — `PredicateSubrings().an_object()(cardinal(7))` is `7` at the head and `TypeError: category() needs an argument` at the base.  The probe also prints the parent of each kind of value it is given, the localization's readings and memberships, the constant-family sums, and both orders' answers |

The order-independence row the earlier round deleted is replaced by
`test_the_order_supplies_its_own_emptiness_after_any_earlier_construction`: it
asks both orders, each through its own `Mor` and through the cached hom-set,
after the other has answered, and asks that an undecided comparison decide
nothing.  The hook's own answer is not asserted in a test: the lint's TL02
refuses a private attribute in a test, so the hook is measured through
`is_empty`, which is the public operation that reads it.  What that leaves
unmeasured here is a full-suite run of the two files: no workflow in this
repository dispatches one (the development-diagnostics job has never run) and
this VM cannot run `tests/` inside a command.  The nearest selections a
command here can take are the ones recorded above and, in the earlier round's
rows, `tests/sets`, `tests/objects` and `tests/rings` prefixed to the file.

### Correction, 2026-11-16: the `543-rings-head.log` row is not a completed row

The row `543-rings-head.log` above (round 5's table, `tests/rings` and the file
in one process) records **75 failed, 296 passed in 756.89 s**, and 756.89 s is
beyond this round family's ten-minute bound for one command.  The row is left
as it ran -- a dated audit event is not edited -- and it is withdrawn here as a
completed evidence row: a selection that overruns the bound is not a row this
round may claim, whatever it printed.  What the row was for (the head's FAILED
ids are the base's minus the three rows that round repaired) is therefore not
established by it.  That selection takes twelve minutes on a loaded host; it is
a suite and belongs to CI, and it is not re-taken here.

### `#543`, round 6: the same rows at the tree the round is pushed from, 2026-11-16

Main advanced under the branch while this round ran, and the rows above were
re-taken on the rebased tree: the test commit, the two repairs and the evidence
commit this note follows (a rebase re-identifies a commit, so the rows name the
trees by what they are).  Same pinned image, same launcher, same `PYTHONPATH`.

| log | tree | result |
| --- | --- | --- |
| `543r2-green-at-rebased-head.log` | the rebased repair head | the two files: **23 passed in 2.46 s** |
| `543r2-probe-at-rebased-head.log` | the rebased repair head | `543r2-probe.py`: the same **36** answers, and the same single difference against `543r2-probe-at-ab2e435.log` (`PredicateSubrings().an_object()(cardinal(7))` is `7` here, `TypeError: category() needs an argument` there) |

The two rows were taken once more on the tree this round is actually pushed from,
after main advanced to `a38faef` and the branch was rebased onto it:

| log | tree | result |
| --- | --- | --- |
| `543r2-green-at-pushed-head.log` | the pushed head | the two files: **23 passed in 2.78 s** |
| `543r2-probe-at-pushed-head.log` | the pushed head | the same 36 answers, the same single difference against `543r2-probe-at-ab2e435.log` |
| `issue381-base-line-row.log` | base tree `c696bf9` | the kernel line row before this round: `stable_orthogonal_group().cusps(1)` on `6JRS` raises `NameError: name '_isotropic_line_class_points' is not defined` at `orthogonal_quotients.py:2319`, 12 s in |
| `issue381-base-incidence-records.log` | `e175cdb` (the divided-class fix alone) | the same row with only that fix: `TypeError: cannot use '...ArithmeticCuspIncidence' as a dict key`, from `finite_ordered_sets.py:427` under `tits_building_incidence` |
| `issue381-6jrs-driver.log` | head of this round | `tests/coble_gamma_co_2_incidence_rows.py --rows Otilde,Otilde+ --lattice 6JRS --cap 300`: 1 edge over 1 line and 1 plane cusp for each kernel row, 13.7 s and 17.2 s, then the trivial discriminant image's agreement with the ambient `O`/`O+` rows, exit 0 |
| `issue381-u-plus-u2-driver.log` | head of this round | the same driver, `--lattice 'U+U(2)+<-2>' --cap 400`: 4 edges over 3 line and 2 plane cusps for each kernel row, 41.2 s and 63.8 s, exit 0 |
| `issue381-kernel-incidence-gate.log` | head of this round | `python -m pytest -p qc_sage_session -o addopts= -p suite_budget -p test_lint --no-time-gates tests/lattices/test_the_kernel_incidence_rows.sage`: **3 passed in 164.62 s**, calls 64.96 s, 47.11 s, 48.50 s over the 20 s gate |
| `issue381-tco-incidence-gate.log` | head of this round | the #391 file, `tests/lattices/test_the_coble_incidence_of_line_and_plane_orbits.sage`, same invocation with a 2700 s inner limit: **2 passed in 1696.37 s** (`Gamma_{Co,2}` 1685.31 s, `O(T_Co)` 10.11 s) -- the first time it has run to completion, since on the base tree its first line row raises the `NameError` above |
| `issue381-flag-stabilizer-clause.log` | main `3fae3b5` | the ambient flag row before the clause repair: `lattice.Aut().isotropic_orbit_representatives(2, flag=True)` on `6JRS` raises `TypeError: StabilizerSubgroups._call_() got an unexpected keyword argument 'description'`, 1.96 s in |
| `issue381-6jrs-driver-rebased.log` | the rebased head | the driver's `--lattice 6JRS` run on the head that is pushed: 1 edge over 1 line and 1 plane cusp for each kernel row, then the trivial-image agreement with the ambient rows, exit 0 |
| `issue381-u-plus-u2-driver-rebased.log` | the rebased head | the driver's `--lattice 'U+U(2)+<-2>'` run on the head that is pushed: 4 edges over 3 line and 2 plane cusps for each kernel row, exit 0 |
| `issue381-u-u2-m4-driver.log` | the rebased head | the driver's `--lattice 'U+U(2)+<-4>'` run: 6 edges over 4 line and 3 plane cusps for each kernel row, in 4.0 s and 19.5 s, exit 0 |
| `issue381-kernel-incidence-gate-rebased.log` | the rebased head, with the clause repair | `tests/lattices/test_the_kernel_incidence_rows.sage` with the test lint on: **3 passed in 55.45 s**, one call over the 20 s gate (21.23 s) |
| `issue381-driver-final-6JRS.log` | the head this pushes (`464a3a5` rebased) | the driver's kernel rows on `6JRS`: 1 edge over 1 line and 1 plane cusp each, then the trivial-image agreement, exit 0 |
| `issue381-driver-final-UU2-2.log` | the same head | the driver on `U+U(2)+<-2>`: 4 edges over 3 line and 2 plane cusps each, exit 0 |
| `issue381-driver-final-UU2-4.log` | the same head | the driver on `U+U(2)+<-4>`, the gate's second specimen: 6 edges over 4 line and 3 plane cusps each, exit 0 |
| `issue381-kernel-incidence-gate-final.log` | the same head | `tests/lattices/test_the_kernel_incidence_rows.sage`, lint on: **3 passed in 62.84 s**, longest call 21 s over the 20 s gate |
| `issue381-gate-final2.log` | the head this pushes (rebased onto `4936110`) | `tests/lattices/test_the_kernel_incidence_rows.sage`, two specimens -- `6JRS` and `U + U + <-4>` -- with the test lint on: **2 passed in 74.46 s**, both calls over the 20 s gate (35.29 s, 38.18 s) |
| `issue381-gate-pushed-final.log` | the head this pushes, `3fe961c` on `ab2e435` | the same gate file: **2 passed in 69.14 s**, calls 33.36 s and 35.34 s over the 20 s gate |
| `issue381-gate-eb5baa8.log` | the head this pushes, `33971c8` on `eb5baa8` | the same gate file, last run before the push: **2 passed in 103.73 s**, calls 48.71 s and 31.15 s over the 20 s gate |
| `issue381-gate-final3.log` | the head this pushes, on `e65da01` | the same gate file, the run of the push: **2 passed in 37.26 s**, both calls under the 20 s gate |
## 2026-11-16 (#521): the two `541r4` rows of `SHA256SUMS`

The evidence commit of this issue's previous round (`d3b92a4`, "evidence: the
round's rule change, measured at the commits that carry it (#521)") rewrote two
rows that were already in the file, dropping the `.tmp/qc-evidence/` prefix from
each path, where the rule is that such a round appends its own records and leaves
the existing ones as they were written.  A dated row is not edited, so the two are
restored to the text they were written with; their digests are unchanged and both
files are the ones they name:

```
013f855bd0aef1a1c0ff2d535f1cc87a1f99e8a7d1798950954fde4cdc214067  .tmp/qc-evidence/541r4-green-rebased.log
12363c1f3d00052c6074558c928766d9a280624ada7b88a1f3ea24101acb0ea7  .tmp/qc-evidence/541r4-green-final.log
```

The round that made the edit is recorded in this file as its own rows and is not
otherwise altered; this note is the correction, dated today.


## `#521` round 4: the dialect's readings, and the session's declaration of its names (2026-11-16)

The review of this issue's previous round found the fix had replaced the dialect's
grid of readings with a weaker one (a session file could declare no generator
implicitly), the round's test asserted that new rule instead of the defect, and its
evidence commit edited two rows of `SHA256SUMS`.  This round restores both readings
and gives the parser the one fact they need -- which names the session's star import
binds -- as the session's own declaration rather than a reading of its namespace.

`1c168e9` is the test commit, `ffd8209` its repair, `27a1bba` the evidence rows'
restoration; all three were rebased from `ba303ba` onto `c9568ed` and this is the
head they are pushed from.  One file, or two, per run, in the pinned runtime
(Sage 11.0.beta5, port tree `991b88b0`), through `.scratch/launch521r4pytest.sh`:
`run.sh -w /work`,
`PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`,
`/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session
-p sage_extensions.testing.test_lint`.

| log | commit cited | result |
| --- | --- | --- |
| `issue521r4-red.log` | `ba303ba` with this round's two test files only | `tests/foundations/test_a_session_file_binds_only_what_it_writes.sage` alone: **1 failed, 2 passed in 4.89 s**, the failure being `load` of a session file that writes `QQ[t]` raising `NameError: name 't' is not defined` |
| `issue521r4-green.log` | `27a1bba`, clean tree | that file with `test_the_session_names_denote_their_objects.sage`: **6 passed in 3.88 s**, exit 0, `test_lint` loaded and reporting nothing |
| `issue521r4-probe-session-base.log` | `ba303ba`, clean worktree | `issue521r4-probe-session.py`: 677 public names, no `__all__`, the dialect's vocabulary 0, and **no** snippet of the five declaring a generator -- `QQ[t]` raises `NameError`; the star import binds 677 names |
| `issue521r4-probe-session-fix.log` | `27a1bba`, clean tree | the same probe: `__all__` is the 677 public names, the vocabulary is that declaration, `QQ[t]` and `ZZ[x, y]` declare their generators (`t`, `x`, `y` land in the loaded scope), `Sets.Δ[aleph0]`, `Modules[ZZ]` and `Modules[k]` with `k` bound by the file keep the subscript, `QQ[t]` is the ring over `QQ` with `t` its generator, and `Integer`, `RealNumber` and `matrix` answer as before |
| `issue521r4-mypy-base.log`, `issue521r4-mypy-fix.log` | `ba303ba` and `27a1bba` | the mypy tier, diff-scoped to `language_runtime.py` and `all.py` inside the pinned image: **the same ten errors** in both trees (seven the runtime's untyped functions, three `all.py`'s `RealNumber` binding at line 508) |

The repair's commit message quotes an earlier run of the same two test files on the
tree the fix was written in -- **6 passed in 2.74 s**; the stored log is the run at
the head this is pushed from, where the same six pass in 3.88 s.  Neither the test
files nor the two library files changed between the two runs.


## `#521` round 4, re-taken: the runs at the head the round is pushed from (2026-11-16)

`main` moved twice while this round was being finished -- once before the rebase onto
`c9568ed`, again before the rebase onto `cf6ba0b`, whose one session-name addition
(`TransvectionOutsideTheLattice`) makes the module publish 678 names rather than the
677 the earlier rows record.  The three runs below are the same files and the same
probe on the tree this is pushed from, so the evidence names a commit in the pushed
history rather than a pre-rebase one.

| log | commit cited | result |
| --- | --- | --- |
| `issue521r4-green-rebased.log` | `5f014e0`, clean tree (the rebased head) | the two test files of this round: **6 passed in 5.84 s**, exit 0, `test_lint` loaded and reporting nothing |
| `issue521r4-probe-session-rebased.log` | `5f014e0`, clean tree | the same probe: **678** public names, `__all__` is them, the dialect's vocabulary is that declaration, `QQ[t]` and `ZZ[x, y]` declare their generators, `Sets.Δ[aleph0]`, `Modules[ZZ]` and `Modules[k]` keep the subscript, `QQ[t]` is the ring with `t` its generator, and `Integer`, `RealNumber`, `matrix` answer as before |
| `issue521r4-mypy-rebased.log` | `5f014e0`, clean tree | the mypy tier, diff-scoped to the two changed files: the same ten errors as `issue521r4-mypy-fix.log` and `issue521r4-mypy-base.log`, with `all.py`'s three at line 509 for the one added import |


`main` moved three times while this round was finished, and the round was rebased
each time; the ids in the two notes above are the ids of the `c9568ed`- and
`cf6ba0b`-based histories.  The pushed history is `0003ad4` (the reds' test),
`01c9949` (the repair), `76d3191` (the two restored rows), `69d9ae9` and
`b107242` (the evidence).  The runs citing
`27a1bba` and `5f014e0` measured trees whose four files are byte-identical to the
pushed tip's -- `git diff --stat 5f014e0 b107242 -- src/sage_extensions/all.py
src/sage_extensions/language_runtime.py tests/foundations` is empty -- so they
cover the code this is pushed from.


## `#521` round 4: the trees the runs measured, named by what they are (2026-11-16)

`main` advanced while this round was finished and the round was rebased onto it
each time, so the ids in the rows above are the ids of the trees the runs measured,
not of the commits this push carries.  The rows survive the rebases by their
subject: this round's commits are the ones carrying its four subjects -- the reds'
test, the repair, the two restored `541r4` rows, and the evidence -- and the four
files they touch are the ones at the tip of this push.

The red's tree is `ba303ba`, which is in the pushed history, and the log names it.
The other logs name trees the rebases replaced; they hold the same four files as
the tip, so every run covers the code that is pushed and none is claimed for a tree
it did not measure.
| `519r4-classsum-at-pushed.log` | the head this pushes, `5064d72` | `tests/algebras/test_group_algebra_class_sums.sage`, lint on: **5 passed in 5.06 s** -- the class-sum, refusal, centrality and inclusion tests |
| `519r4-brauer-at-pushed.log` | the same head | `tests/groups/test_module_characters.sage`, lint on: **3 passed in 3.06 s** -- the Brauer value and the modular trace at the identity of the `F_2^2` specimen |
| `519r4-scalar-at-pushed.log` | the same head | `tests/groups/test_actual_group_algebra_modules.sage`, lint on: **4 failed, 4 passed in 4.56 s**; the four ids are the file's on main `c9568ed` too (`4 failed, 3 passed in 2.19 s`), and the added test is among the passes |
| `519r4-probe-at-pushed.log` | the same head | `519r4-probe.py`: the centre's inclusion for `QQ[S_3]`, for `Algebras(QQ).Unital()(QQ^3, m, 1)` (unital, not associative) and for `Algebras(QQ)(QQ^2, m)` (not unital) -- arrow parent is `center.Mor(algebra)` in all three, `preserves_unit` True in the two unital cases |
## `#527` round 3: the review's four findings, repaired at their owners, 2026-11-16

The region review of the round that pushed `fef5e49` refused it on four counts: the
completion map's core placement and the rank-one module basis were both decided by
`_engine_ring(source) is engine` (`OWN-10`), `_completion_map_as_ring_morphism`
returned any arrow that was not a `CategoricalIsomorphism` as `Mor_Ring`, and the
refusal that replaced the silent `pass` had no red test.  This round states the datum
the placements follow -- some power of the defining ideal is zero
(`completion_defining_power_vanishes`) -- retires both engine tests, returns the ring
map the construction retained, and measures the defect the engine decisions produced:
the same theorem gave a rank-one basis to `QQ(i)` and none to `QQ` or `GF(5)`.

Every run below is one file in the pinned runtime (Sage 11.0.beta5, port tree
`991b88b0`), through `.scratch/probe527r3/runpytest527.sh`: `run.sh -w /work`,
`PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`,
`/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session`.  The red of each
`test:` commit is measured at its own parent, with that commit's test file and no
source change; the green is measured at the `fix:` commit.

| log | tree | result |
| --- | --- | --- |
| `527r3-red1-datum-at-eb5baa8.log` | `eb5baa8`, the push base, + the first test only | `-k states_whether`: **1 failed, 6 deselected in 3.23 s**, at `assert completion.completion_defining_power_vanishes() is True`: `AttributeError: 'Owned_AdicCompletionAlgebraParent_with_category' object has no attribute 'completion_defining_power_vanishes'` |
| `527r3-green1-datum-at-1efc091.log` | `1efc091`, the repair, with the test lint | the same selection: **1 passed, 7 deselected in 4.65 s**, no lint finding |
| `527r3-red2-rank-at-1efc091.log` | `1efc091` + the second test only | `-k rank_one`: **1 failed, 1 passed, 6 deselected in 4.53 s**.  `QQ` at `(0)`: `ValueError: Rational Field has no chosen resolution relative to Category of modules over Fraction Field of Integer Ring`; the `QQ(i)` row of the same selection passes, so the two answers differ only in the engine |
| `527r3-green-at-6bfc56b.log` | `6bfc56b`, the repair, with the test lint | the whole file: **8 passed in 9.62 s**, no lint finding |
| `527r3-consumers-at-6bfc56b.log` | `6bfc56b` | the consumers of the ring map, probed: `QQ(i)` at `(0)` (`_completion_map_as_ring_morphism`, `extended_ideal`, `completion_map_kernel`, `adic_projection(1)`, the arithmetic mode, and the constant inverse system), `QQ[x]` at `(x)` (the ring map, the extended ideal, the projection of `x`, and absence from the core) and `QQ[x]` at `(0)` (the ring map, the extended ideal, the projection of `x^2`): 13 answers, no failure |
| `527r3-completion-maps-at-eb5baa8.log` | `eb5baa8`, the push base | `tests/rings/test_completion_maps.sage`, the consumer file this change touches most: **4 failed, 1 passed in 7.47 s**, the four ids filed in `results/issue-to-file-completion-maps-four-failures.md` |
| `527r3-completion-maps-at-ace9f84.log` | `ace9f84`, this round's head | the same file: **4 failed, 1 passed in 10.86 s**, the same four `FAILED` ids — this round's two repairs change none of them |

## `#527` round 3, re-taken: the same six commits and five runs, rebased onto `c9568ed` (2026-11-16)

`main` advanced to `c9568ed` while this round's evidence was being written, so the six
commits were rebased from `eb5baa8` onto it and their ids changed: `ec5fdc7` is the
first test, `17238c6` its repair, `202f65c` the second test, `67a5074` its repair, and
`2577ad4` and `55aecf2` the evidence.  Their content is the content of the commits the
section above names (`git diff 6bfc56b 67a5074` over the two source files and the test
file is empty), and the only file `main` gained in between that this round touches is
none (`git diff eb5baa8 c9568ed` over those paths is empty).  The runs are taken again
at the commits being pushed, by the same command shape; the previous section's logs stay
as they were taken.

| log | tree | result |
| --- | --- | --- |
| `527r3-red1-datum-at-c9568ed.log` | `c9568ed`, the push base, + the first test only | `-k states_whether`: **1 failed, 6 deselected in 3.26 s**, `AttributeError: ... has no attribute 'completion_defining_power_vanishes'` |
| `527r3-green1-datum-at-17238c6.log` | `17238c6`, the repair, with the test lint | the same selection: **1 passed, 7 deselected in 1.69 s** |
| `527r3-red2-rank-at-17238c6.log` | `17238c6` + the second test only | `-k rank_one`: **1 failed, 1 passed, 6 deselected in 4.95 s** — `QQ` at `(0)`, `ValueError: Rational Field has no chosen resolution ...`, while the `QQ(i)` row passes |
| `527r3-green-at-67a5074.log` | `67a5074`, the repair, with the test lint | the whole file: **8 passed in 1.82 s** |
| `527r3-consumers-at-67a5074.log` | `67a5074` | the consumer probe again: 13 answers, no failure |
| `527r3-completion-maps-at-c9568ed.log` | `c9568ed`, the push base | `tests/rings/test_completion_maps.sage`: **4 failed, 1 passed in 3.55 s**, the four filed ids |
| `527r3-completion-maps-at-67a5074.log` | `67a5074`, this round's head | the same file: **4 failed, 1 passed in 2.62 s**, the same four ids |

## `#527` round 3, re-taken again: the six commits rebased onto `cf6ba0b` (2026-11-16)

`main` moved once more while this round waited for its push: `cf6ba0b`.  The six
commits are rebased onto it and their ids are now `0b3c5f4` (test), `68a0154` (its
repair), `ee2441e` (test), `2ef3d7b` (its repair), `5a47e7f`, `89a9aa4` and
`e395856` (evidence).  The three paths they touch are identical at `c9568ed` and at
`cf6ba0b` (`git diff --stat c9568ed cf6ba0b --` them is empty), and their content is
unchanged again (`git diff 67a5074 2ef3d7b` over those paths is empty), so the runs in
the two sections above are the same measurements of the same trees.  The whole file is
taken once at this head, and no red needed re-taking because none of the runs' inputs
changed.

| log | tree | result |
| --- | --- | --- |
| `527r3-green-at-e395856.log` | `e395856`, this round's head, with the test lint | the whole file: **8 passed in 5.49 s**, no lint finding |
