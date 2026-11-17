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
