The test lint ends the pytest run before any test instead of naming the tests it concerns

`src/sage_extensions/testing/test_lint.py:413` calls `pytest.exit` on the first finding, at `pytest_collection_finish`.  One finding anywhere in the tree ends the run with every test unrun, and no test is named against the finding.

Observed on `main` `9b297125` in the adopted image with `--no-time-gates` (the time gates lifted, so the lint is reached), `pytest -p qc_sage_session --collect-only -q --no-time-gates`:

```
3930 tests collected, 1 error in 471.88s (0:07:51)
! _pytest.outcomes.Exit: test lint: 1514 findings (run just test-lint for all) !
EXIT=1
```

3930 tests collected, 0 run, 1514 findings, exit 1.  The findings are printed (`tests/algebras/test_group_algebras.sage:22: TL01 ...`, and 1464 more), but nothing runs and no test carries a failure.

Introduced by `14b9cc16`.

Repaired in the #406 commit: the findings are filed under the file that holds them at collection, each test of such a file fails at its setup with the findings that concern it (`path:line: CODE message`), the other files' tests still run, and the run ends red even for a file with no collected test.  `just test-lint` is unchanged.

Acceptance: each finding is reported against the tests of the file that holds it, the remaining tests run, and the run ends red.
