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
