# #406 — the suite stopped before its first test

## The invocation on main

`main` at `9b297125` (2026-11-14), adopted image, the repository's own
`addopts` in force (`suite_budget`, `test_lint`, `--timeout=60`,
`--report-log`, `--junit-xml`), nothing lifted:

```
cd /repos/sage-extensions
PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src:/repos/sage-extensions/.pydeps \
  /sage/.venv/bin/python -m pytest -p qc_sage_session --collect-only
```

```
time gates on: star import 0.26 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
collected 3930 items / 1 error
============== 3930 tests collected, 1 error in 232.95s (0:03:52) ==============
! _pytest.outcomes.Exit: collection took 232.90 s; the measured ceiling is 6 s !
EXIT=1
```

* exit **1** (`pytest.ExitCode.TESTS_FAILED`);
* 3930 tests collected, **0 run**;
* the stop is `pytest.exit` in `suite_budget.pytest_collection_finish`,
  `src/sage_extensions/testing/suite_budget.py:72` of that tree;
* message: `collection took 232.90 s; the measured ceiling is 6 s`;
* peak process-tree RSS 3763 MiB, log
  `.tmp/qc-evidence/issue406-suite-collection-stop.log`.

The `.pydeps` path is where `pytest-timeout` and `pytest-reportlog` were put:
this venv carries `pytest` only, and without them the declared `addopts` cannot
even be parsed (`exit 4`, `unrecognized arguments: --timeout=60
--timeout-method=signal --report-log=...`).  That gap is its own filed cause
(`.tmp/qc-evidence/triage/406-image-lacks-declared-pytest-plugins.md`); nothing
else in the command differs from `just test`.

## Three stops in a row, and what is behind each

Each run below was taken on the tree the previous repair left.

| # | where | what it says | effect |
| --- | --- | --- | --- |
| 1 | `suite_budget.pytest_collection_finish`, `suite_budget.py:72` (and `pytest_sessionstart`, `:59`) | `collection took 232.90 s; the measured ceiling is 6 s` | `pytest.exit` — 3930 collected, 0 run |
| 2 | `test_lint.pytest_collection_finish`, `test_lint.py:413` | `test lint: 1514 findings` | `pytest.exit` — 3930 collected, 0 run |
| 3 | `tests/functions/test_young_convolution.sage` at collection | `RecursionError` in `modules.py:1704` `__truediv__` | `Interrupted: 1 error during collection` — 3930 collected, 0 run |

`14b9cc16` ("Move the session namespace and the mathematics test suite from
research", Zack Garza, 2026-10-26) introduced 1 and 2: `git blame` puts all
three `pytest.exit` calls there, the commit brought 1437 test files into the
repository in the same change, and the ceilings above them were measured on a
26-test tree in the repository they came from.  `git log --follow` shows that
one commit and no other for `suite_budget.py`, so no earlier commit of this
repository can stop the run this way; the image run at its parent `fca190e`
finishes `--collect-only` with no ceiling message
(`.tmp/qc-evidence/issue406-bisect-good-fca190e.log`).  The bad side was not
measured again at `14b9cc16` itself: collecting that commit's 1437-file tree
held 6.4 GiB after nine minutes and the run was stopped to keep the shared
VM's memory.  That one measurement is **unrun, not passing**.

3 is #398, already filed, and it is the stop that survives the other two: with
1 and 2 repaired the run reports both and then ends at collection with
`Interrupted: 1 error during collection` and `3930 deselected`
(`.tmp/qc-evidence/issue406-run-before-issue398-repair.log`).  Its repair is in
this session as well, below.

## The run after all three repairs

`.tmp/qc-evidence/issue406-final-full-run.log`, the repository's `addopts` in
force, whole tree collected, two tests selected:

```
..                                                                       [100%]
=============================== time-gate report ===============================
collection took 224.19 s; the measured ceiling is 6 s
...
2 passed, 3939 deselected in 241.97s (0:04:01)
EXIT=1
```

The collection ceiling is over, it is reported against the workload it
measured at the end of the run, the run's selected tests execute, and the run
is red on that report rather than on an abort.  Peak process-tree RSS 3945 MiB.

## The repair of 1 and 2

`src/sage_extensions/testing/suite_budget.py`: a measurement over its ceiling is
recorded with the workload it measured and reported in the end-of-run summary,
the way the 20 s call ceiling already was; `pytest_sessionfinish` makes the run
red.  Recording is independent of `--no-time-gates`, which now lifts what makes
the run red without lifting what the run measured.

`src/sage_extensions/testing/test_lint.py`: the findings are filed under the
file that holds them at collection, each test of such a file fails at its setup
with the findings that concern it (`path:line: CODE message`), and the run ends
red even for a file with no collected test.  `just test-lint` is unchanged.

## The repair of 3 (#398)

The recursion is `Modules.ElementMethods.__truediv__`
(`src/sage_extensions/categories/modules/pure/modules.py`), added by
`e4bd95d` (#150): it stated `v / r = r^{-1} v` and implemented the inverse as
the quotient `ring.one() / ring(scalar)`.  A ring is a module over itself, so
its element class carries that method, and for the exact real field
`RR.one() / x` asks the same method for `1 / x` again, with the same operands.
Measured at `9b297125` with the session imported:

```
ZZ(1) / ZZ(2)              -> 1/2              (equal parents, so Sage's
                                                 Element.__truediv__ takes
                                                 _div_ and this method is not
                                                 entered)
RR(1) / RR(2)              -> RecursionError
RR(1) / (RR(2).sqrt() - 1) -> RecursionError
~RR(2)                     -> RecursionError
```

The operation is one formula — division by a scalar is the scalar action of its
inverse, and a ring element dividing in its own ring is the same operation, not
a second one — so the repair is that formula, and the quotient that re-entered
the method is gone:

```python
ring = self.parent().base_ring()
return self.parent().scalar_multiple(ring(scalar) ** -1, self)
```

`AGENTS.md` §6 ("do not add a special case for this object; strengthen the
general interface so the special case disappears") and the `STY-*` one-shot
table's "structural predicate implemented by ..." rows are what rules out the
alternative repair, which dispatched on `self.parent() is ring` and took the
ring's own `_div_` in that branch: the branch is a case split for the object
the failure was found on, and the remaining branch computed the inverse as
`ring.one() / ring(scalar)`, the same circular quotient.  That branch landed on
`main` as `e9b6c2c` (#410) while this slice was running; this slice replaces it
with the single formula and adds the test that states the acceptance.

What the formula keeps, measured on this tree
(`.tmp/qc-evidence/issue398-division-after.log`):

```
ZZ(1) / ZZ(2)   -> 1/2                       (unchanged: not this method)
QQ(1) / QQ(2)   -> 1/2                       (unchanged)
RR(1) / RR(2)   -> 1/2                       (was RecursionError)
RR(1) / (RR(2).sqrt() - 1), ~x -> 1/(sqrt(2) - 1)
ZZ(2) inverted, a ZZ-module vector divided by ZZ(2) -> refused, as before
```

Files, `-o addopts= -q --tb=no -rA`
(`.tmp/qc-evidence/issue398-green-three-files.log`):

```
PASSED tests/lattices/test_rational_scalars_on_a_base_changed_lattice.sage  (#150's contract)
PASSED tests/rings/test_exact_real_division.sage  (2 tests, red at 9b297125)
PASSED tests/rings/test_rational_exact_reals.sage (1 failed at 9b297125)
tests/functions/test_young_convolution.sage: collects and runs (ERROR collecting at 9b297125)
3 failed, 8 passed in 6.24 s
```

`tests/rings/test_rational_exact_reals.sage` was `1 failed in 5.32 s`
(`RecursionError`) on `main`; `tests/functions/test_young_convolution.sage`
could not be collected at all and now does.  The three failures it reports are
its own and newly visible: `KeyError: (('finite', 2), 93168848, 93168848)` in
the `Lp` construction, a `NotImplementedError`, and `TypeError: unsupported
operand parent(s) for ^: 'Symbolic Ring' and 'Integer Ring'` in the Gaussian
test.  None of them touches division.

Regression set, 8 files over rings, lattices and modules, `-o addopts= -q`:

```
9b297125:  8 failed, 22 passed in 5.57 s
this tree: 7 failed, 23 passed in 4.51 s
```

`diff` of the two FAILED lists shows exactly one line: the rational exact reals
test that flipped to passing.  No other test changes state.

## Red tests for the plugins, and the same tests after

`tests/engineering/test_the_suite_plugins_report_what_they_measured.py` runs a
separate pytest over a tree written for it (`tests/engineering/conftest.py`
binds the abbreviation through the mechanism `TL13` documents) and asserts what
that run reported: on the old plugins each probe run reported no tests at all.

| tree | command | result |
| --- | --- | --- |
| `main` `9b297125` | `pytest tests/engineering/test_the_suite_plugins_report_what_they_measured.py -q` (repository `addopts`, nothing lifted) | **2 failed in 18.03 s**, exit 1 |
| this commit | same | **2 passed in 22.44 s**, exit 0; calls 11.63 s and 10.72 s against the 20 s ceiling, `setup` 0.00 s |

## What is not verified

* No full execution of the 3941 collected tests was run: that is hours on this
  VM.  What is measured is that the whole tree collects, the gate reports, and
  the selected tests run; the claim is "the run no longer stops before its
  first test", not "the suite passes".  After these commits what the run
  reports is a red suite, not a missing one.
* The bad-side bisect measurement at `14b9cc16` (memory, above).
* The published image `ghcr.io/dzackgarza/sage:develop` cannot be run on this
  host (no OCI runtime); every run here is the adopted pinned runtime with the
  two dev-group plugins supplied at a scratch path.

## The causes, as issues to file

`.tmp/qc-evidence/triage/`, paste-ready, title line first:

* `406-time-gate-ends-the-run.md` — repaired in this slice.
* `406-lint-ends-the-run.md` — repaired in this slice.
* `406-stale-time-gate-baselines.md` — open; the 6 s collection ceiling and the
  3 s star-import ceiling were measured on 26 tests and no run of this tree can
  meet them, so every run now ends red on the gate report.
* `406-image-lacks-declared-pytest-plugins.md` — open; the image does not carry
  `pytest-timeout` or `pytest-reportlog`, so the declared `addopts` do not
  parse.
* The collection error is #398, filed; `e9b6c2c` (#410) first repaired it with a
  branch, and this slice replaces that branch with the one-formula division and
  adds its red test.
