# The line row of card 6JRY under Otilde+(Lambda_4) stops at 6312 MiB without a count

Filed 2026-11-21, the day the row was measured, against `main` `5befdf9`.  State:
open.  This is the defect the acceptance work of #319 reached on the known
families: the fourteen rows that were run all agreed with their cards, and this is
the one row that was measured and could not be decided.

## The row

| | |
| --- | --- |
| card | `6JRY` of `dzackgarza/lattice-database`, row `integral.primitive_orbits.Otilde+` |
| lattice | $\Lambda_4 = U \oplus U \oplus E_8(-1) \oplus E_8(-1) \oplus \langle -4\rangle$, rank 21, signature $(2,19)$, determinant $-4$ (the card's own invariants) |
| group | $\widetilde O^+(\Lambda_4) = \ker \rho \cap O^+(\Lambda_4)$, the kernel of the discriminant character $\rho \colon O^+(\Lambda_4) \to O(A_{\Lambda_4})$ intersected with the spinor-norm-one subgroup -- the card's `Otilde+`, which it identifies with Scattone's $O^*(L) = O_-(L) \cap \widetilde O(L)$ (J. Scattone, *On the compactification of moduli spaces for algebraic K3 surfaces*, Mem. Amer. Math. Soc. 374 (1987), Section 3.6) |
| expected | one orbit of primitive isotropic lines -- the card's row, from J. Scattone, same work, Theorem 4.0.1 |
| call | `group.isotropic_orbit_representatives(1).cardinality()`, the public orbit call of #286 (`PredicateSubgroups.isotropic_orbit_representatives`) |
| outcome | no value: the process computing it was stopped at 6312 MiB of resident memory after 90 s |

The same row of the sister lattice returns: $\widetilde O^+(\Lambda_2)$ on card
`6JRX` gives the card's one orbit in 9.9 s (the acceptance module, row
`6JRX:O+:lines`).  So the defect is a property of this lattice and this group, not
of the module, the row's shape or the harness.

## The record of the stop

All measurements: the adopted runtime (SageMath 11.0.beta5, Python 3.14), the
indefinite port as the image provides it at `/repos/sage-indefinite-port` (this run
did not record which revision that copy is at), `main` `5befdf9`, one process, 4
CPUs and 15 GiB of memory on the host.  The group is built first, and it is cheap;
the growth is inside the orbit call:

```
building stable group
stable group built [0.2 s]
intersected [0.2 s]
[peakrss] STOPPED_AT_MEMORY_LIMIT: tree RSS 6312 MiB exceeded 6144 MiB
[peakrss] run: child waited=-15 shell_code=143 samples=46
[peakrss] peak tree RSS      : 6312 MiB
[peakrss] low-water MemAvail : 5781 MiB
[peakrss] peak single VmHWM  : 6312 MiB
[peakrss] peak VmHWM by executable (this is the per-process attribution):
[peakrss]   python                     6312 MiB peak
[peakrss]   t=    90.1s procs=  1 rss=  6312 MiB hwm=  6312 MiB avail=  5781 MiB
[peakrss]   t=    88.1s procs=  1 rss=  5961 MiB hwm=  5961 MiB avail=  6139 MiB
[peakrss]   t=    86.1s procs=  1 rss=  5800 MiB hwm=  5800 MiB avail=  6299 MiB
[peakrss]   t=    84.1s procs=  1 rss=  5650 MiB hwm=  5650 MiB avail=  6449 MiB
[peakrss]   t=    82.1s procs=  1 rss=  5509 MiB hwm=  5509 MiB avail=  6585 MiB
```

The command, with `<tree>` the checkout of `5befdf9`:

```
~/sage-image/run.sh -w /work -b <tree>:/work -b <tree>/.git:<tree>/.git -- /bin/sh -c '
  cd /work && PYTHONPATH=/work/src:/work CAP=600 ROW=6JRY PEAKRSS_LIMIT_MIB=6144 \
  /sage/.venv/bin/python -u .tmp/peakrss.py -- /sage/.venv/bin/python -u .tmp/probe319c.py'
```

`probe319c.py` builds $\Lambda_4$ from its own summands, calls
`lattice.stable_orthogonal_group()` and intersects it with `lattice.O_plus()`,
prints the two build times, and then calls `isotropic_orbit_representatives(1)`
under a 600 s alarm.  The memory bound was reached at 90 s, before the alarm.

The acceptance module runs each row in a child of its own for exactly this case: a
child that is killed for its memory writes no outcome, the module reports the row
`BROKEN` naming its lattice and its group, and the run exits non-zero.  That
child was not run a second time under the bound for this record: the measurement
above is the same construction in the same runtime.

## What this record does not say

* It is not a claim that the count is wrong.  No value was computed, so there is
  no disagreement with the card to decide by proof; the row is undecided.
* It is not a time-out.  The bound reached is resident memory, not the alarm: the
  samples above rise about 100 MiB a second across the last eight seconds and had
  6.3 GiB at 90 s, against the 600 s the alarm allowed.
* The cap was not raised to get past it, and the row is not dropped from the
  module: it is enumerated, run and reported like every other row.

## Closing condition

The row closes when `isotropic_orbit_representatives(1)` returns a count on
$O^+(\Lambda_4)$'s discriminant kernel for card `6JRY` and the count equals the
card's row, in the acceptance module's own run.  The repair belongs to the owner of
that call, and the acceptance module reads the closed row by tag without a change.

## Correction, 2026-11-21

The paragraph "The same row of the sister lattice returns" compares this row with
row `6JRX:O+:lines`, which is the row of $O^+(\Lambda_2)$ and not of
$\widetilde O^+(\Lambda_2)$.  The $\widetilde O^+(\Lambda_2)$ row was measured the
same day and does not return either: it passes 5974 MiB at 834 s and was stopped
there (`results/issue319-6jrx-otilde-plus-line-row.md`).  So the two $\widetilde
O^+$ line rows of the two Scattone lattices are two instances of one defect, and
the $O^+$ line row of $\Lambda_2$, which decides in 9.9 s, is not a control for
either.
