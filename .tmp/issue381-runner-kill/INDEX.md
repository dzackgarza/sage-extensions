# The kernel incidence row's kill and its slices (#381)

What each file is, and the command that produced it.  The measurements are on
the adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5, image rootfs) at
`main` `42b7cf1a1b32fe1c2fae0743a597894dd8a47d30`, under `peakrss.py`, one
process a slice.

| file | what it is |
| --- | --- |
| `launch.sh` | one slice in the image: `WALL`, `PROBE_PLANES`, `PROBE_PHASE` in, `peakrss.py` samples out |
| `probe-381-slice.py` | phase `row`: `T_Co`, `Otilde(T_Co)`, the plane's parabolic, the split's first lift, N planes with `register_isotropic_lift` each; phase `walk`: the same plus the public `tits_building_incidence()`, which this VM's line row does not reach inside a command |
| `probe-381-carry.py` | the walk's per-plane work on its own objects: one covering at the first plane, `transport_covering` and the three line keys at each further plane |
| `row-10.log` | the first slice: 10 planes, wall 220.5 s, peak tree RSS 1365 MiB |
| `diag-1.log` | the stack-sampled diagnostic that measured the line row: still inside `_isotropic_line_class_points` at 559.5 s, RSS 1717.5 MiB |

The command of one slice, from the repository root:

```
cd <repo>/.scratch/381
PROBE_PHASE=row PROBE_PLANES=10 WALL=280 ./launch.sh row-10 probe-381-slice.py
```

`launch.sh` binds the paused indefinite port at `/work`, this repository at
`/repos/sage-extensions`, and runs

```
/sage/.venv/bin/python -u /repos/sage-extensions/.scratch/381/<probe>
```

under `peakrss.py`.  The logs here are the probe's own, verbatim.
