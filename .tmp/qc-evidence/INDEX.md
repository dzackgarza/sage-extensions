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

The probe sources behind the `500d-*` measurement logs are session probes, not
library code, and stay out of the tree: each prints the rings, the values and the
class that answered, so the log carries every reading it is cited for.
