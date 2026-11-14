# Triage of the failing tests of the second half of `tests/objects` on main (#412)

Run on main `c8a3cedb1ba27` (2026-11-14) in the published image, one file per pytest
process, with the repository's own invocation (`just test`, which delegates to
`~/ai-review-ci/justfiles/sage.just`) and its `addopts` blanked because the image's venv
has neither `pytest-timeout` nor `pytest-reportlog`:

```
~/sage-image/run.sh -w /work -b <port-repo>:/work -b ~/ai-review-ci:/ci \
  -b <worktree>:/repos/sage-extensions -b <repo>/.git:<repo>/.git -- \
  /bin/sh -c 'export HOME=/root; export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; \
    cd /repos/sage-extensions; exec just test "$@"' sh \
  -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates --no-test-lint -q --tb=line <one test file>
```

**Result.** 75 failing tests in 24 of the 25 files, 99 passed (174 tests in the slice). Two
files of the slice are green in full: `test_product_of_a_two_and_a_three_element_set.sage` (6) and
`test_slice_set_invariants.sage` (2).

The slice was then re-run on the main this workstream's repair is rebased onto, with that
repair in place (`415c2b4`, which is `7817e87` plus one commit): **69 failing, 105 passed**, and the six
that are green are C11's one test and five of C33's seven. Both runs are recorded under
`412-run-c8a3ced/` and `412-run-415c2b4/`; the per-file logs are the full pytest output.

The failures are assigned to 37 causes, one defect of one call, fixture or plugin each.
Every failing test is in exactly one cause: 75 = 75, no test in two and none unassigned
(the emitter asserts this).

## Causes

| cause | defect | tests | introduced by | repair |
| --- | --- | --- | --- | --- |
| C01 | The K3 lattice does not carry its summands | 1 | `9f5831e` | filed |
| C02 | The owned ring adapter has no constructor for the symbolic ring | 6 | `14b9cc1` (import of the suite) | filed (shared with #408 C02) |
| C03 | A finite owned group is not a member of `FiniteGroups()` | 3 | `6c381ad` | filed |
| C04 | The spinor kernel's preimage is refused for the group ring it is taken in | 1 | not bisected (the body says what the runs do establish) | filed |
| C05 | The stabilizer of a discriminant class is built through an element with no ambient category | 1 | not bisected (the body says what the runs do establish) | filed |
| C06 | The kernel of the de Rham differential is refused | 1 | `c546077` | filed |
| C07 | A subset of `ZZ` cut by a predicate carries neither its ambient category nor its countability | 2 | `14b9cc1` (import of the suite) | filed |
| C08 | The cardinality of a homset of owned objects is not computed | 3 | not bisected (the body says what the runs do establish) | filed |
| C09 | `Mor(A, B)` of two predicate subsets has no ambient category | 1 | `caa3825` | filed |
| C10 | `finite_subsets()` and `power_set()` are two objects where there is one | 1 | `14b9cc1` (import of the suite) | filed |
| C11 | `subsets_of_size` coerces its argument with `int()` instead of refusing a non-natural | 1 | `14b9cc1` (import of the suite) | repaired `415c2b4` |
| C12 | An element of `ZZ/3` carries no `inverse` | 1 | `14b9cc1` (import of the suite) | filed |
| C13 | `GL` of a finite field is refused as a matrix group | 1 | `365abfb` | filed |
| C14 | Owned objects do not carry `is_isomorphic_to` | 6 | `6c381ad` | filed |
| C15 | `Modules()` does not carry `extension_of_scalars` | 1 | `6c381ad` | filed |
| C16 | The action on the permutation module returns vectors that do not compare equal | 1 | `6c381ad` | filed |
| C17 | The base-category class of `Modules.FinitelyGenerated` mismatches its own class | 1 | `6c381ad` | filed |
| C18 | A subobject category does not carry `cardinality` | 2 | `6c381ad` | filed |
| C19 | The cardinality of a finitely presented group is refused | 2 | `6c381ad` | filed |
| C20 | The abelianization is refused because GAP hands back a whole-group map | 2 | `6c381ad` | filed |
| C21 | `CartanType` is called with a list | 2 | `39d3db4` | filed |
| C22 | Two constructions of one lattice do not compare equal | 3 | `14b9cc1` (import of the suite) | filed |
| C23 | `q` of a lattice is the doubled quadratic form | 1 | `14b9cc1` (import of the suite) | filed |
| C24 | Two constructions of one endomorphism category do not compare equal | 2 | `14b9cc1` (import of the suite) | filed |
| C25 | A direct sum is not an object of the decomposition category | 1 | `14b9cc1` (import of the suite) | filed |
| C26 | Four tests evaluate an undecided-capable `Predicate` as a Python truth value | 4 | `14b9cc1` (import of the suite) | filed |
| C27 | A finite set of lattice points cannot be formed | 1 | not bisected (the body says what the runs do establish) | filed |
| C28 | The lattice points of a polytope are a bare list | 1 | not bisected (the body says what the runs do establish) | filed |
| C29 | The Ehrhart polynomial is an element that cannot be applied | 1 | `3ab7407` | filed |
| C30 | `toric_variety()` demands a base ring the polytope already knows | 1 | not bisected (the body says what the runs do establish) | filed |
| C31 | `C^k(X, Y)` refuses `RR` as a real vector space | 5 | `14b9cc1` (import of the suite) | filed |
| C32 | `L2` and its categories are not implemented | 4 | `14b9cc1` (import of the suite) | filed |
| C33 | The session namespace does not publish five constructors the suite names | 5 | `14b9cc1` (import of the suite) | closed by `d38845a` |
| C34 | `module_rank` refuses a module over a non-field base | 1 | `14b9cc1` (import of the suite) | filed |
| C35 | A three-element set built by the category's own name has no ambient category | 2 | `14b9cc1` (import of the suite) | filed |
| C36 | The category applied to its own points does not agree with the set | 1 | `14b9cc1` (import of the suite) | filed |
| C37 | The symmetric and tensor algebra constructors refuse an owned field as their base | 2 | `14b9cc1` (import of the suite) | filed |

Each cause is one paste-ready issue body under this directory,
`.tmp/qc-evidence/triage/412-<cause>-<slug>.md`: its first line is the issue title and
the rest is the body -- the failing tests with the error each reports, the defective
call, the introducing commit with its author, and the scope.

## Where each cause's repair stands

| cause | state | evidence |
| --- | --- | --- |
| C01 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C02 | filed; the same defect as #408's cause C02 | still red at `415c2b4` (`test/laurent_monomials` 3 failed, `test_sinc_translates` 3 failed). |
| C03 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C04 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C05 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C06 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C07 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C08 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C09 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C10 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C11 | repaired in this workstream by `415c2b4`, which replaces `415c2b4`'s local reading with the owner's | red test at `415c2b4`: 1 failed, 9 passed (2 failed, 8 passed at `c8a3ced`); `tests/sets` neighbours 4 failed, 15 passed before and after, the same four ids; the refusals are now `ValueError: (3)/(2) is not a natural number` and `ValueError: -1 is not a natural number`. |
| C12 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C13 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C14 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C15 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C16 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C17 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C18 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C19 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C20 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C21 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C22 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C23 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C24 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C25 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C26 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C27 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C28 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C29 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C30 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C31 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C32 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C33 | closed on main by `d38845a` (#408), before this slice was filed | 5 of the 7 tests green at `7817e87` and at `415c2b4`; the two still red are C37, unmasked by that fix. |
| C34 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C35 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C36 | filed and not repaired in this workstream | still red at `415c2b4`. |
| C37 | filed; unmasked by `d38845a` on main | both tests fail with `ValueError: base must be a ring...` at `7817e87` on a clean worktree. |

## How the introducing commit was found

Every cause was first run at `14b9cc1`, the commit that imported `tests/objects`
(`.tmp/qc-evidence/triage/412-base-14b9cc1.txt`, one test per process). A cause whose
failure signature is that same failure there is reported as present at the import: the
assertion has never been green on main. A cause whose signature is absent there was
bisected in the published image over `--first-parent 14b9cc1..c8a3ced`, with the cause's
own test as the predicate (`.tmp/qc-evidence/triage/412-bisect.txt`); the commit named is
the first mainline commit where the signature appears, and where that commit is a merge
the change itself is on the merged branch. Three results were re-run independently at the
commit and at its first parent before being reported (`C01` present at `9f5831e`, absent at
`25bddba`; `C03` present at `6c381ad`, absent at `6ce8cde`; `C13` present at `365abfb`,
absent at `9c159ae`). A cause whose test does not finish at the older trees inside the
per-step cap is reported from the run it does complete, and says so.

## The commit ids in this record

This workstream's own commits were rebased onto main's tip before the push, so the two ids
that name its repair are `873ef1f` (superseded) and `bdfaafb` (the repair on the pushed
tree). The slice re-run recorded under `412-run-415c2b4/` was made at `415c2b4`, the
pre-rebase id of that same source change; each log names the commit it ran at in its own
`provider SHA:` line, so no log's attribution depends on this table. The red test was run
again at the pushed tree (`412-c11-red-at-pushed-tree.log`): 1 failed, 9 passed, the same
result.

## What is not repaired, and why

Thirty-four of the thirty-seven causes are filed and unrepaired here. Each named repair is
a feature of the library, not a slice-local patch: a missing operation (`summands`,
`inverse`, `extension_of_scalars`, `cardinality` on a subobject category), a name the test
surface and the library disagree on (`is_isomorphic_to`), a decision the owner does not
take (`is_finite` of an orthogonal group, `q` versus `b(x,x)`), or a construction that
does not exist (`L2`, the toric variety's default base ring). `A repair is a new commit on main
with its failing tests as the red tests` -- C11 is such a commit; the rest need their own.

Two causes changed state while this slice was triaged, and both are recorded rather than
assumed: #408's push to main repaired the session namespace (C33, five of its seven tests
green) and that unmasked a further defect in the same two tests (C37). The slice was
re-run on the rebased main (`415c2b4`, which is `7817e87` plus this slice's one repair) so
the states in these tables are the states at that commit, not at the triage commit.

## The environment, recorded rather than hidden

`just test` as written fails on this host before any test runs, for two reasons that are
properties of the adopted image and not of the repository: `pytest-timeout` and
`pytest-reportlog` are absent from its venv, so the repository's `addopts` are rejected as
`unrecognized arguments`. The two plugins the suite needs are reselected by hand, exactly
as `pyproject.toml` lists them, with `-o addopts=` to clear the rest. `--no-time-gates` is
the same flag the issue#412 body used; the gates are reported in the logs where they fire
(`test_the_catalogue_entry_is_three_hyperbolic_planes_and_two_e8: 23.26 s > 20 s`).


