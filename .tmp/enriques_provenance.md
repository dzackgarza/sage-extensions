# Enriques case_3 measured terminal provenance (jmvzp7ijo) — RETRACTED staged attribution

**Source:** port `p-165a6922b36b40789ddc90db34bb23c7/repo` at `a764f46` (measured run, see `enriques_jmvzp7ijo_terminal.log`), provider `p-8c69fc7199b5456b9cfab0b695f65a6c/repo` at `835cbdf` (pinned `sweep_nodes.PROV` at launch; subsequent `500f480→7a3a570→835cbdf` history in previous draft was contradictory and is retracted), runtime `sage-image/rootfs` (Debian trixie, Sage 11.0.beta5, GAP 4.14, Julia 1.12) with `SAGE_BIN=/sage/.venv/bin/sage`. `122ccd3a` image existed but was not used for this run (frozen pins).

**Launch:** `peakrss.py -- timeout -s KILL 2400 run.sh -w /work -b p-165a:/work -b ai-review-ci:/ci -b p-8c69:/repos/sage-extensions -b probe_enriques_stages.py:/probe.py -- python -u -s /probe.py` with `PYTHONPATH=/ci/...:/work/src:/work`, `PEAKRSS_LABEL=enriques-heavy LIMIT 6144`.

**Stages (case_3 92897280;5/10/19) as printed BEFORE the bundle:**
- `imports 0.0s`, `fixtures 1.0s`, `invariant 3.7s`, `Isom 20.6s`
- `coinvariant_extension_subgroup 209.6s`
- `G_h built 209.7s` — this is **construction** (`IntersectionSubgroups.__call__` predicate), not realization; `G_h built 0.1s` does **not** prove its lazy `group_generators()` were realized. Realization is deferred to first `group_generators()`/`finite_character_quotient` read, which occurs inside the following bundle.

**Bundle `discriminant orthogonal group + discriminant morphisms` (single log line at 209.7s, 2400s CAPPED, 4541 MiB, C-only `cysignals→permgroup_element→gap/*` stack):** The terminal log contains only C/GAP frames without Python `File "...py", line ...` call path, so **no single Python caller (e.g. `lattice_morphisms.py:1795 discriminant_morphism`) can be established from this transcript**. Distinguishing generator-family realization (`self.finite_index_schreier_generating_morphism` on `G_h`), discriminant-group construction (`A_L = N*/N`, `O(A_L)`), each generator's `discriminant_morphism()` map application, and finite-character image work (`OrthogonalCharacterQuotient._gap_regular_model` at `orthogonal_quotients.py:188-240`, previously measured cheap at 0.04s) requires separate instrumentation.

**Next:** Minimal stage instrumentation (see `.tmp/enriques_stage_instrumentation.py`) will separate those four sub-stages on the same specimen (`case_3`, same `G_h` predicate, same `6144` guard) without repeating the full 2400s indistinguishable bundle.

**Preserved:** Original `Γ_h` predicate (`spinor_kernel` + `discriminant_preimages`), `92897280` + `5/10/19` assertions unchanged; no arbitrary cutoff.
