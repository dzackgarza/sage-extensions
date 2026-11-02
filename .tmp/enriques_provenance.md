# Enriques case_3 measured terminal provenance (jmvzp7ijo)

**Source:** port `p-165a6922b36b40789ddc90db34bb23c7/repo` at `7b0f45db` (current `main`), provider `p-8c69fc7199b5456b9cfab0b695f65a6c/repo` at `835cbdf` (then) → `500f480` → `7a3a570` → `835cbdf` (current `835cbdf` at run time, now `7a3a570` with retained character_data fix), runtime `ghcr.io/dzackgarza/sage@sha256:122ccd3aac6d7dc7a991a3c35bbeb9e5749125dab8b0b62d6da004731e2ab8fb`? No — live rootfs at run was the original immutable `sage-image/rootfs` (Debian trixie, Sage 11.0.beta5, GAP 4.14, Julia 1.12) with `SAGE_BIN=/sage/.venv/bin/sage`, `JULIA_DEPOT_PATH=/root/.julia:/opt/julia-depot`. New `122ccd3a` image not adopted mid-run per instruction; pins frozen.

**Launch:** `peakrss.py -- timeout -s KILL 2400 run.sh -w /work -b p-165a:/work -b ai-review-ci:/ci -b p-8c69:/repos/sage-extensions -b probe_enriques_stages.py:/probe.py -- python -u -s /probe.py` with `PYTHONPATH=/ci/...:/work/src:/work`, `PEAKRSS_LABEL=enriques-heavy LIMIT 6144`, `SWEEP_TOKEN=5016f34d...`

**Stages (case_3 92897280;5/10/19):**
- `imports 0.0s`, `fixtures 1.0s`, `invariant 3.7s`, `Isom 20.6s` (transport isometry)
- `coinvariant_extension_subgroup 209.6s`
- `G_h built 209.7s` (intersection 0.1s — new character∩character branch fired, not whole-group enumeration)
- `discriminant orthogonal group + discriminant morphisms` bundle CAPPED at `2400s`, `peak tree RSS 4541 MiB (julia 3226 + python 1312)`, `low-water 5432`, `VmHWM 4549`, `cysignals → permgroup_element → gap/util → gap/element` stack — caller is `discriminant_morphism() = O(A_L).from_morphism(discriminant_isometry())` at `lattice_morphisms.py:1795-1805`, not the cheap ambient constructor (`orthogonal_group_base_change` 0.04s measured earlier).

**Distinction:** Generator realization for `G_h` (now via retained `character_data` → `finite_character_quotient` exact index, not product bound) is distinct from finite-character image construction (`OrthogonalCharacterQuotient._gap_regular_model` via libgap `Group`+`RightCosets` at `orthogonal_quotients.py:188-240`, cheap) and discriminant morphism application (`O(A) → gap` for each `G_h` generator). The capped trace is the third, not the first.

**Preserved:** Original `Γ_h` predicate (`spinor_kernel` + `discriminant_preimages`), `92897280` + `5/10/19` assertions unchanged; no arbitrary `|G|>200k` cutoff (reverted `94853f6`), no direct private-method replacement.

**Logs:** `/.nucleus/jobs/jmvzp7ijo.log` (5.2K, `code 124`, first stage verified) and `/.tmp/enriques_heavy_4541.log` (4541 MiB) retained.
