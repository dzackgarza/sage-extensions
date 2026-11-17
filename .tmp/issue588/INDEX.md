# `sage_extensions#588` -- probes, logs, and the partial repair

Base commit `6b8f2822` (`main` when the issue was taken).  Runtime: the adopted
`ghcr.io/dzackgarza/sage@sha256:59568577...` rootfs under proot, Sage 11.0.beta5
/ Python 3.14, `/sage/.venv/bin/python`.  `PYTHONHASHSEED=0` throughout.

Every run is `launch.sh <log-name> <probe>.py`, which binds the tree under
`/repos/sage-extensions` and pins `PYTHONPATH` to it; `TREE` selects the tree
(`$REPO` is `main`, `$REPO/.scratch/588` is the worktree with
`partial-repair.patch` applied), and `GIT_BIND` is needed for the worktree
because the stage recorder resolves `git rev-parse HEAD` from the tree's own
`.git`, which in a worktree is a pointer the proot root does not see.

| probe | question | log |
| --- | --- | --- |
| `probe-588-registries.py` | which registry holds a dropped plane (`SPECIMEN=plane|lattice`) | `registries.log`, `registries-deep.log`, `registries-deep2.log`, `registries-lattice.log` |
| `probe-588-holders.py`, `probe-588-roots.py` | the referrers of a dropped plane and of its inclusion | `holders.log`, `roots-after.log` |
| `probe-588-keyhold.py` | whether a weak-valued registry holds its object through its key | `keyhold-lattice.log` |
| `probe-588-external.py` | the objects outside the plane's own closure that point in | `external-plane.log` |
| `probe-588-cycle.py` | the drop test: lattice, `U`, plane, bare module subobject | `cycle-before.log` (`main`), `cycle2.log` / `cycle-final.log` / `cycle-objstrong.log` (the three tree states of the record's table) |
| `probe-588-repro.py` | the four-second repro of the formed-module failure | `repro.log`, `bisect1.log`, `bisect2.log` |
| `probe-588-locals.py`, `probe-588-valued.py` | the frames and the value modules of that failure | `locals.log`, `locals2.log`, `valued.log` |
| `probe-588-life.py` | the acceptance: cusp by span, the release test, `U+U(2)+<-2>` counts, spans and edges | `life-before.log` (`main`), `life-after.log` (the worktree) |
| `probe-588-row.py` | the row's per-plane bytes and milliseconds (`PROBE_SHAPE`) | `row-before.log` |
| `probe-588-cache-decorators.py` | how many cache decorators key on an address | run with the host `python3`, no Sage needed |

## The partial repair

`partial-repair.patch` is the diff of the worktree: the three lattice morphism
registries, `_lattice_subobject_spanning`, `_lattice_on_gram` and
`_primitive_isotropic_subobject` at `cache=0` weak values; the Mor family's
resolution record holding its Mor weakly; the cusp named by its span; and the
orbit row yielded rather than gathered, which `cusps` consumes.  It is **not
landed**: with `_MorCategoryOf._objects` still strong it releases nothing
(`cycle-final.log`: the plane survives), and with that record weak the
formed-module construction fails (`repro.log`).  Flipping
`self._objects = {}` to `weakref.WeakValueDictionary()` in
`abstract_categories/mor_categories.py` reproduces both states of the record's
section 2 table.
