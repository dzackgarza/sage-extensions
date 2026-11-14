# Retained evidence: the stable-kernel adjudication (swarm smvzznqcw)

This directory publishes the accepted mathematical evidence for the claims recorded in
`TRAPS.md` (the stable-kernel half, `ker(O⁺(N) → O(A_N))` with `N = U+U(2)+E8(-2)`).
The member reports live in the git-ignored `.ultramath/` tree; this directory keeps the
accepted proofs/scripts and the judge-side verification under the tracked `.tmp/` tree.

## Judges' verification (run independently in this runtime)

`verify_witness_m1.py` (+ `verify_witness_m1.out`, `ALL OK`): the decisive witness
`τ_{a₂,r₀}` with `a₂` the isotropic vector of the unscaled plane and `r₀` an `E8` root —
isometry of `M`, preserves `N` in both directions, trivial on `D(M)` across the full dual
basis, and moves the class `[½·b₂] ∈ D(N)` (displacement `a₂ + ½·r₀` has an odd `a₂`
coefficient, hence `∉ N`). Refutes the descent-inside-kernel premise. Command:
`python3 .tmp/adjudication/verify_witness_m1.py` (plain Python 3, no Sage).

## Accepted member reports (reproduced or line-checked, verdicts recorded)

| member / direction | status | evidence kept here |
|---|---|---|
| `accepted/m1` (d4, reflections) | **accepted** (witness reproduced by judge) | `proof.md`, `scripts/verify.py` (+ `verify.out`) |
| `accepted/m2` (d5, indefinite controls) | **accepted** (load-bearing outputs reversioned by judge) | `results/adjudication.md` + core step scripts |
| `accepted/m5` (d2, structural negation) | **accepted** | `report.md`, `h1_embed.py`, `h1b_glue.py`, `h2_model.py` |
| `accepted/m6` (d6, descent refutation + repair) | **accepted** | `report.md`, `s1_forms.py`, `s2_ambient.py`, `s3_spinor.py`, `s4_validate.py`, `s5_sn.py`, `s6_repair.py` |
| `accepted/m7` (d8, resubmitted after rejection) | **accepted** after repair | `adjudication.md`, `witness_H2.py`, `transcript_witness.txt` |
| `accepted/m8` (d3, congruence characters) | **accepted** | `REPORT.md`, `adjudicate.py`, `run.log` |

## Rejected reports — not published here as accepted proof

- The first submission from direction d8 (member m7) claimed blanket containment of the
  descended stabilizer in the kernel; it was **rejected** by the judge, and then
  **repaired and resubmitted**; the accepted version is the one in `accepted/m7/`. The
  rejected text stays only in the swarm records (issue-ledger, not evidence).
- The submission from direction d7 (member m4) was **rejected**: its descent lemma inferred
  "trivial on `L^∨/N`" from triviality on both subquotients of
  `0 ⊂ L/N ⊂ L^∨/N ⊂ A_N`; `1+φ` crossed nilpotents — exactly the reproduced
  transvections — invalidate it, and its lossless-descent and "U(2) costs nothing"
  theorems fall with it. Its correct pieces (`H2.1` ambient auto-triviality, `H2.2`
  kernel-preserves-overlattices) are recorded in `TRAPS.md`. Its resubmission, if it
  arrives, will be judged on the same evidence standard before any acceptance.

## Member reports accepted without re-publication

`accepted/m2/` keeps `results/adjudication.md` and the core direct-gram step scripts; the
remaining m2 step files stay in the swarm directory (their conclusions are already mapped
by the accepted peers).  Nothing here claims generation equality for the stable kernel:
the repaired 46-element family (m6, `E4`) is a **partial verified in-kernel family**, and
the original per-generator S1 acceptance stays open.
