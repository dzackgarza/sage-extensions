A time-gate breach ends the pytest run instead of reporting it, so the selected tests never run

`src/sage_extensions/testing/suite_budget.py:59` (`pytest_sessionstart`, the session star import) and `:72` (`pytest_collection_finish`, collection) call `pytest.exit` when a measurement is over its ceiling.  The run then reports the measured workload and none of the tests it selected.

Observed on `main` `9b297125` (2026-11-14) in the adopted image with the repository's own `addopts`, `pytest -p qc_sage_session --collect-only`:

```
time gates on: star import 0.26 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
collected 3930 items / 1 error
============== 3930 tests collected, 1 error in 232.95s (0:03:52) ==============
! _pytest.outcomes.Exit: collection took 232.90 s; the measured ceiling is 6 s !
EXIT=1
```

3930 tests collected, 0 run, exit 1 (`pytest.ExitCode.TESTS_FAILED`), peak process-tree RSS 3763 MiB.

Introduced by `14b9cc16` ("Move the session namespace and the mathematics test suite from research", 2026-10-26), which moved the plugin, the `addopts` that load it, and 1437 test files into this repository together with ceilings the plugin's docstring measures on a 26-test tree.  `git blame` puts both `pytest.exit` calls in that commit and `git log --follow` shows no earlier history for the file.

Repaired in the #406 commit: an over-ceiling measurement is recorded with the workload it measured, reported in the end-of-run summary the way the 20 s call ceiling already was, and makes the run red at `pytest_sessionfinish`.  `--no-time-gates` now lifts what makes the run red without lifting what the run measured.

Acceptance: a breached gate reports the workload it measured, ends the run red at the end of the session, and the run's selected tests still run.
