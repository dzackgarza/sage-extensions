# Stage-D handoff: apex-stabilizer generation does not return on the Enriques coinvariant lattice (port #403)

Measured at 2026-11-03 on the real case_3 inputs under the original 6144 MiB process-tree RSS guard.

## Measured evidence spine

- Probe job `jmw0d7uq2` (source `3588c8f`, [log](.tmp/enriques_stageD_job_jmw0d7uq2_source_3588c8f.log)): `subgroup_classes(G_h, lines)` entered at probe-t 395.7s; the `SE_DEBUG_STAGES` marker inside `LatticeIsometryMor._marking_stabilizer_generators` printed `_marked_automorphism_generators start` and never printed `done` before the job's inner 2400s cap (exit 124, tree RSS 4917 MiB under guard). The `DoubleCosets`-side markers inside `_splitting_isometries_in_im_rho` never fired, so the non-returned call is attributed by before/after markers on the actual call path, not by a wrapper name alone.
- Earlier full runs (jobs `jmw075b47`, `jmw09ixev`) hit the same position: stage C accepted |rho(Gamma_h)| = 92897280 (published), then the line split never printed within the 2400s cap.
- A minimal exact reproduction script is committed at `.tmp/repro_marked_stabilizer.py` (launched by `.scratch/launch_repro_stab.sh`): it exercises **only** the innermost measured call `INDUCTION.line_automorphism_generators(N, e_i)` on the two published line representatives of `N = U(1) + U(2) + E8(-2)` — fixture ids `I_1_1` (`Z e1`, `[1,0,...,0]`) and `I_1_2` (`Z e3`, `[0,0,1,0,...,0]`, gram read from `tests/fixtures/unpolarized_enriques.json`, det 1024, signature (2,10)) — and then the port wrapper at the category level. The repro is deliberately one process with stage prints before each call, so a cap still leaves ordered before/after evidence. A guarded launcher IS published with this handoff (`.tmp/launch_repro_stab.sh`, `PEAKRSS_LIMIT_MIB=6144`, inner cap 2400s). Scope of the repro, recorded precisely: the direct-gram `N` built from the fixture gram is an **isolation specimen**, not the embedded case_3 object (no involution/polarized machinery, no `coinvariant_extension_subgroup` construction; its call order is direct `INDUCTION.line_automorphism_generators` first, then the category-level wrapper, which can warm caches differently than the embedded run whose only measurement was `subgroup_classes` on the retained `G_h`). Pins (reconciled): the `jmw0lhx6q` recovery run launched ~11:19 UTC with the port checkout at `c2288184` (commit `c2288184f45869d73d95d285cbd6fb7a6a04a8b3`, 'port: retract the false congruence-surjectivity claim, and compute the actual image', 11:14:22) — the earlier `c68f101e` belongs to the states of `jmw0c2cds`/`jmw0d7uq2`, not to this run, and is explicitly not copied into this run's evidence. Bind semantics: host-path bind, no snapshot; modules read from that tree at launch time, and a checkout advanced later would only affect later reads. The port-owner diff `c68f101e..c2288184` touches the adjacent stabilizer/canonical area (recursive.py, pointwise_shell.py, marked canonical/orbit tests, ~3256 insertions) — the port owner is actively building nearby. Provider main at `b3e336a` (working tree otherwise clean). Run guard evidence: `PEAKRSS_LIMIT_MIB=6144` visible in both supervisor processes' environments; inner cap 2400s. The handoff holds independently of the repro's completion: the failing call is already identified by markers. The agent-side `background:true` stopped materializing background jobs this session (caller-visible JSON argument contains only `command`); a native Move-to-background remains the fallback for the published launcher.

## Exact owning call path and arguments (as measured)

```
tests/acceptance consumer: subgroup_classes(G_h, lines)
  -> sage-indefinite-port consumer split: lattice_.O().split_orbit(marked, subgroup)      (library: lattice_morphisms.py SplitOrbit)
  -> LatticeIsometryMor._marking_stabilizer_generators(category, marked)                  (library: lattice_morphisms.py)
  -> Lattices..._marked_automorphism_generators(diagram_category, marked)                 (library: lattices.py:1862, defer to port #403)
  -> sage_indefinite_port.indefinite.marked_lattices.automorphism_group_generators(category, marked)
       category = Ar(Lattices) sublattice category; marked = a rank-1 sublattice marking
  -> (sublattice rank 1 branch) INDUCTION.line_automorphism_generators(marked.arrow().codomain() = N, e)
       with e = INDUCTION.plane_vectors(sublattice)[0]  (the line's first vector; here Z e1 or Z e3)
  -> IsotropicInduction._stabilizer_generators((line,), ((-line,),))                       (isotropic_induction.py:306)
  -> recursion.isotropic_stabilizer_action(isotropic, radical_images) -> action.stabilizer().group_generators()
```

Expected semantic result: the generators of `Aut((N, Z e_i))` = the apex isometries generating the stabilizer action, returned as a finite ordered set of live lattice isometries; the consumer uses them to produce the double-coset splittings of each `O(N)`-line orbit under `G_h` (published counts: 5 lines / 10 planes / 19 flags; the port test asserts only these counts).

## What is being asked of the port owner

1. Reproduce and time `INDUCTION.line_automorphism_generators(N, e1)` on the direct-gram N built from the fixture gram (repro script above pins every argument byte-exactly).
2. Attribute inside `isotropic_stabilizer_action` vs `stabilizer()` vs `integral_isometry` conversion: which of these does not return — the repro's stage prints will name it without a full consumer run.
3. If the algorithm is an intractable variant for this lattice class (signature (2,10), discriminant 2^10), say so explicitly with the measured trajectory — the library's stage-C/C accepted results and the DoubleCosets-measured splitting path stand independently, and a smaller stabilizer API (e.g. expect `stabilizer` only for lines in the two published orbit classes with discriminant indices 1 and 527 as recorded in the fixture) is a valid reduced contract for the consumer's needs.

## What is NOT asked

Nothing here asks for a patch from this repository, and none was made: the port consultation is the documented owner only. The original case_3 line/plane/flag acceptance (5/10/19) and the per-generator S1 obligation remain open on their own terms; image order 92897280 and index 1011840 are published and measured, but are not substitutes for either.
