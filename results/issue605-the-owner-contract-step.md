# #605, item 3: the owner-contract step runs green on `<1> + <-1>`

The repair landed as `ea85485` (`test:`) and `741d6a3` (`fix:`); the third
acceptance item of #605 is that the consumer's owner-contract step passes. That
step is not runnable from this machine — the CI image needs an OCI runtime the
host does not have — so this note records the step re-run from its own command,
in the pinned research runtime, at the commit named below, and says what remains
outside it.

## The step

`dzackgarza/lattice-database`, `.github/workflows/tests.yml` at `9f891eeaae`
("Validate preamble owner contracts"), whose last two steps are:

    docker exec -i --workdir "$GITHUB_WORKSPACE/sage-extensions" \
      --env "PYTHONPATH=$GITHUB_WORKSPACE/_ci-support/ai-review-ci/tool-artifacts/pytest_plugins:$GITHUB_WORKSPACE/sage-extensions/src:/repos/sage-extensions/src" \
      ... \
      sage-env /sage/.venv/bin/python -c 'import sage.all, sys, pytest; from sage.all import ZZ; from sage_extensions.categories.lattices import Lattices; Lattices(ZZ)([[2, -1], [-1, 2]]).orthogonal_group().order(); sys.exit(pytest.main(sys.argv[1:]))' \
      -p qc_sage_session -p qc_unique_inventory --no-time-gates \
      tests/lattices/test_lattice_database_owner_contracts.sage \
      tests/lattices/test_coordinate_diagonal_embeddings.py

The checkout it runs in is `dzackgarza/sage-extensions` at `main`; the step
before it binds that checkout to the container's git through `safe.directory`
(`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`), because the
session's timing record ends on `git rev-parse HEAD` (run 44304988129, step 9).

## The run

Three runs of the step's selection and eight runs of its last contract alone,
in the pinned research runtime (Sage
11.0.beta5, Python 3.14.10) with the checkout at `f1b037c2e177` and the
container given the same `safe.directory` binding:

| selection | result |
| --- | --- |
| both files, run 1 | 13 passed in 16.39 s |
| both files, run 2 | 13 passed in 26.00 s |
| both files, run 3 | 13 passed in 12.41 s |
| `test_primitive_orbit_series_counts_primitive_isotropic_lines`, 8 runs | 1 passed each, 4.10 s in the first |

`test_integral_hyperbolic_index_is_owned_by_the_lattice`, the contract #605 is
about, is among the twelve in the `.sage` file and passes in every run.

## What the run is sensitive to

Without the `safe.directory` binding, the same twelve tests fail on the last
one, `test_primitive_orbit_series_counts_primitive_isotropic_lines`, in 1.23 s:

    src/sage_extensions/categories/lattice_orbit_invariants.py:141:
        "constant": subgroup.isotropic_orbit_representatives(1).cardinality(),
    src/sage_extensions/categories/lattice_morphisms.py:5490:
        return _isotropic_orbit_representatives(self, rank, flag=flag)
    src/sage_extensions/timing.py:508:
        with stage(name, input(*arguments, **keywords)):
    src/sage_extensions/timing.py:356:
        assert checkout is not None, (
    AssertionError: /repos/sage-extensions/src/sage_extensions carries no
    source_revision, and the tree above it is not a source checkout ...

`_isotropic_orbit_representatives` is wrapped in `timing.stage`, and a stage
record carries `current_commit()`. So an environment whose container cannot
read the checkout's git turns that instrumentation into a test failure. The
step above binds `safe.directory` for exactly this reason, so the step is not
affected; the sensitivity is recorded here because it is the one way this
selection goes red without anything being wrong with the mathematics.

## What this does not establish

* The CI run itself. No tool here dispatches a workflow, and the connection
  cannot add files under `.github/workflows/`; the step is confirmed by the
  next scheduled or manual run of `tests.yml` in `lattice-database`, at the
  `sage-extensions` `main` this note names.
* Anything about `lattice-database`'s own suite: only the owner-contract step's
  two files were selected.

## Addendum, 2026-11-18: the selection in the container's own path shape

The runs tabulated above bound this tree over both of the step's `PYTHONPATH`
entries. CI does not: the image carries its own copy of the library at
`/repos/sage-extensions`, and the step puts the checkout's `src` first. The
selection re-run in that shape — checkout at `2286251`, the image's copy left
at the second entry, the container given `safe.directory` for the checkout:

    PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/repos/sage-extensions/src
    sage_extensions from /work/src/sage_extensions/__init__.py
    hyperbolic_partner from /work/src/sage_extensions/categories/lattices.py
    13 passed in 33.24s

So the code under test is the checkout's, and the second entry cannot supply
it: the image's copy predates `sage_extensions.testing.timing_record`, which
this tree's `addopts` load, and with that copy alone the session dies at plugin
import with

    ImportError: Error importing plugin "sage_extensions.testing.timing_record":
    No module named 'sage_extensions.testing.timing_record'

## What the next run tests

`tests.yml` checks `sage-extensions` out with no `ref`, so it takes that
repository's default branch, and the repair is on `main` (`741d6a3`, with this
note at `e47bdb3`). The workflow runs on `cron: 17 3 * * *` and on
`workflow_dispatch`; the next scheduled run is 2026-11-19T03:17Z. The verdict
appears in the step named "Validate preamble owner contracts".

The run list itself could not be read for this addendum: `api.github.com`
answered

    403 {"message":"API rate limit exceeded for 85.25.187.233. ...
         x-ratelimit-reset: 1795045486"}

for this shared egress (60 requests an hour, reset 2026-11-18T23:44:46Z), on
two attempts 23:39Z and 23:43Z. Nothing in that list would have shown a run
after the repair in any case, unless one was dispatched between 23:00Z and
23:39Z: run 44392454284, the one #605 reports, started at 21:37Z.
