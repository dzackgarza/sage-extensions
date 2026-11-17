# What `register_isotropic_lift` retains a plane (#584)

Every measurement here is on the adopted runtime (`~/sage-image/run.sh`, Sage
11.0.beta5, the image rootfs) at `main` `ecfbea1`, on
`T_Co = <2> + U(2) + E8(-2)` and `Otilde(T_Co) = ker rho`, one process a slice.
A memory question has no stage record to read (`CONTRIBUTING.md` `ENV-03`
records wall time), so these are probes.

| file | what it is |
| --- | --- |
| `launch.sh` | one probe in the image: `WALL`, `PROBE_PLANES`, `PROBE_MODE`, `PROBE_METER_EVERY` in, `peakrss.py` samples out |
| `probe-584-retention.py` | the row's own plane row -- `_plane_orbit_from_parabolic_stabilizer`: the certified parabolic, the finite image's coset walk, one `register_isotropic_lift` a plane -- with `VmRSS` after every plane. `PROBE_MODE=noreg` makes the same plane and span key and does not register; `PROBE_METER_EVERY=N` attributes marginal bytes every Nth plane |
| `probe-584-shapes.py` | one registration, and the shapes and shallow sizes of the span key, the lift, the transported plane and the family tuple |
| `probe-584-lift-shape.py` | what one element of `O(T_Co)` holds: a bare generator, a two-letter and a five-letter product |
| `probe-584-stageA.py`, `stageA-base-1000.log` | the same retention on a fast specimen: distinct planes carried by words in the ambient generators.  Only the `baseline` run is logged (39,638 B a plane marginal, 75.7 KB a plane resident, 40.7 s); its `noreg` twin was launched and died with this launcher's quoting fault, and it is not run again because no number in the report rests on the fast specimen -- the row's own slices do |
| `probe-584-carried-flag.py` | the two parts of an edge certificate: a carried flag (`move.transport_isotropic_object(flag)`) and a fresh transporter |
| `probe-584-small-certificates.py` | the row returned on `U + U(2) + <-2>` and its four certificates measured (the specimens there share everything, so this is the shape of a certificate, not its size) |
| `probe-584-certificate.py` | one certificate made directly on `T_Co` from the retained plane |
| `bare-base-10.log`, `bare-base-100.log`, `bare-base-1000.log` | the row, meter off, 10 / 100 / 1000 planes.  The 100-plane log was launched under the name `meter-base-100` before `launch.sh` forwarded `PROBE_METER_EVERY`, so it ran with the meter off -- which is the mode it is cited in |
| `bare-noreg-100.log`, `bare-noreg-1000.log` | the same planes and spans, nothing registered: the ceiling of every repair #584 allows |
| `meter10-base-100.log` | the attribution: marginal bytes by structure, and the plane's and the lift's own attributes |
| `lift-shape.log`, `carried-flag.log`, `carried-flag2.log`, `small-certificates.log`, `certificate.log` | the component measurements |

The command of one slice, from the repository root:

```
PROBE_PLANES=100 PROBE_MODE=baseline PROBE_METER_EVERY=0 WALL=560 \
    .scratch/584/launch.sh bare-base-100 probe-584-retention.py
```

`launch.sh` binds the paused port at `/work`, the worktree under test at
`/repos/sage-extensions`, this repository's `.git` (the worktree's gitdir is
inside it) and the probes at `/probe`, and runs

```
/sage/.venv/bin/python -u /probe/probe-584-retention.py
```

under `peakrss.py`, with `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`.
