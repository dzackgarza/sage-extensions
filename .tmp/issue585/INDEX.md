# What retains the walk's 350-400 KB a plane, and why no cache repair moves it

The measurements behind `results/issue585-the-walks-per-plane-retainer.md`.  They
are on the adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5, image rootfs),
one process a probe, at `main` `901d11b2f` unless a log's own header says
otherwise.

| file | what it is |
| --- | --- |
| `launch.sh` | one probe in the image: `TREE`, `PROBE_PLANES`, `PROBE_CLEAR` in, `peakrss.py` samples out |
| `run-tests.sh` | the same image, running named test files |
| `probe-585-instrument.py` | the carry slice with `tracemalloc` and a per-structure account of the quotient at every sample |
| `probe-585-where.py` | the same slice accounting the lattice's `primitive_isotropic_subobject` registry: entries, shallow size, traced, rss |
| `probe-585-carry.py` | the record's own carry slice, unchanged, for the before/after coefficient |
| `probe-585-small.py` | `U + U(2) + <-2>`: the cache's key is by value, an equal family answers one object, one transport's entries |
| `probe-585-parentlife.py` | four specimens built and dropped: which Parents are released, and which are not |
| `probe-585-holders.py`, `-holders2.py`, `-holders3.py`, `-holders5.py`, `-latticeholder.py`, `-zeroholders.py` | the referrer walks that name the holding registry |
| `attrib-1000.log` | the instrumented slice: quotient containers, per-phase RSS, the traceback comparison |
| `where-1000.log` | the constructor registry over 1000 planes |
| `before-carry-1000.log` | the coefficient before any repair, the record's probe on this tree |
| `after-carry-1000.log` | the same probe with the five id-keyed registries holding their values weakly |
| `parentlife.log`, `latticeholder.log`, `zeroholders.log`, `small-30.log` | the lifetime and holder probes |

The command of one probe, from the repository root:

```
cd <repo>/.scratch/585
PROBE_PLANES=1000 WALL=600 ./launch-585.sh where-1000 probe-585-where.py
```

## Appended 2026-11-17: the probes of the divided-class route

The four probes of the repair `results/issue585-the-incidence-decided-by-divided-classes.md`
measures.  They are on the same runtime and the same launcher, and each log's
header names the tree it ran at.

| file | what it is |
| --- | --- |
| `probe-585-classes.py` | the class route's per-plane steps priced separately, and at every line of ten planes the carried class pair compared with the carried line's own pair and the two keys with each other |
| `probe-585-walk.py` | the class route's walk over the row's planes: per-band RSS and wall at 10, 100 and 1000 planes; `PROBE_PHASE=check` runs the certificate route beside it and compares the deciding data line by line |
| `probe-585-recordsize.py` | one record of the relation, priced by holding 200000 copies of a real one on `U + U(2) + <-2>` (its log prints the figure in KiB, 0.1 KiB = 121 B), and the literal ingress of the relation against a supplied inverse |
| `probe-585-linerow.py` | whether `Otilde(T_Co)`'s line cusp row returns at all, which is what an edge-set comparison on `T_Co` itself would need |
| `probe-585-small-row.py` | the two incidence routes and the flag row side by side on `U + U(2) + <-2>`, for both kernel groups |
| `diag_hashes.sage` | the run that names the trap: a `{...}` display in a session file is `Owned_FiniteLiteralSet`, not a `set()` |
| `classes-10.log`, `linerow.log`, `walk-phases-1000.log`, `walk-row-1000.log`, `recordsize.log`, `small-row.log` | their outputs |
