The collection and session-import ceilings are one-tree baselines measured on 26 tests, so every run of the current tree breaches them

`suite_budget`'s docstring states the ceilings came from `1e36cc7e03` (2026-10-19): a 26-test tree, session import 1.3-2.0 s, collection 2.7-3.8 s.  This repository's tree at `main` `9b297125` collects 3930 tests in 232.90 s on a loaded shared VM and 625.38 s in a second run; the 6 s collection ceiling and the 3 s star-import ceiling are two orders of magnitude below it.

The docstring also states the invariant the gates enforce: "A test's execution result depends only on its own duration; selecting additional tests cannot increase its allowance."  That holds for the per-test call ceiling.  Collection and the session import are properties of the whole selection, so their ceilings cannot be selection-invariant, and as published they are met by nothing.

Since the #406 repair, a breach no longer ends the run and the run ends red instead, so this shows up as a permanent red on every full-tree run and in the end-of-run `time-gate report`.

Acceptance, one of:
* the collection and star-import ceilings are re-measured on a named commit of this tree and the measurement with its headroom recorded in the docstring, as the present text records its own; or
* collection and the session import stop being gated, and the docstring says which workloads the gates cover.

Measured: `.tmp/qc-evidence/issue406-suite-collection-stop.log`, `issue406-suite-lint-stop.log`, `issue406-repair-full-run.log` (the run that reports `collection took 625.38 s; the measured ceiling is 6 s`).
