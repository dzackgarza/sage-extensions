# Why the dispatched kernel incidence row was killed, and how far the row is from returning

The job https://github.com/dzackgarza/sage-extensions/actions/runs/44012568639,
revision `921dcf6ed7b921ff78479cd4eb067008e2eff42a`, `rows=Otilde,Otilde+`,
`lattice=Tco`, ended `failure`: the step *Each kernel incidence row against the
public incidence call* reported

```
/__w/_temp/....sh: line 7: 165 Killed   "$sage_python" tests/coble_gamma_co_2_incidence_rows.py ...
##[error]Process completed with exit code 137.
```

and wrote no row.  This note settles which limit killed it, measures the row's
per-plane retention on slices of its plane row, and files that retention at the
operation that holds it.

## 1. Which limit killed it: the memory ceiling, not a clock

| quantity | value |
| --- | --- |
| run started | 2026-11-17T03:46:48Z |
| job started / completed | 03:46:50Z / 06:16:01Z, 8951 s |
| failing step started / completed | 03:51:48Z / 06:15:57Z, **8649 s** |
| job `timeout-minutes` in the installed workflow | **350**, i.e. 21000 s |
| driver `--cap` (one row) | 10800 s |
| driver `--budget` (whole run) | 28800 s |
| the step after the failing one | *Keep the run's timing record*, **succeeded** at 06:15:57Z |

* The job's own limit is 350 minutes and the job ran 149.2 minutes; the step ran
  144.2 minutes.  A wall-clock limit of either kind is 2.4× away from where the
  step stopped, so neither fired.
* The driver's two clocks cannot produce this exit status.  `--cap` is a
  `signal.setitimer` that raises `RowUndecided`, and `--budget` is a check
  between rows; both end the run as a *reported* undecided row with exit status
  1 (`tests/coble_gamma_co_2_incidence_rows.py`, `run_row` and `main`).  A
  SIGALRM or a spent budget is reported, never signalled.
* A runner-side cancellation would have cancelled the job.  The step after the
  failing one ran and succeeded, and the post- and stop-steps ran, so nothing
  cancelled anything.

What is left is a SIGKILL delivered to the `sage_python` process itself: `bash`
prints `Killed` only for its own child being signalled, and 137 is 128 + 9.  On
a GitHub-hosted `ubuntu-latest` job the container shares the runner's memory and
no per-step memory limit exists, so the sender is the kernel's OOM killer at the
runner's memory ceiling.  **The row was killed by memory, not by time**, and it
died inside the call, which is why it wrote nothing: the driver prints a row only
when the call returns, is capped, or raises.

**No memory figure is quotable from the run, and that is a fact about this
connection, not about the run**: the job-log endpoint answers `403 Must have
admin rights to Repository`, and the check-run annotation for the failing line
carries only `Process completed with exit code 137.`  The slices below supply
the RSS the log would have had to show.

## 2. The phases of the call, and the one no ten-minute command can reach

`PredicateSubgroups.tits_building_incidence()`
(`src/sage_extensions/categories/group/predicate_subgroups.py:718`) computes, in
this order: the line row `self.cusps(1)`, the ambient flag row
`self.supergroup().isotropic_orbit_representatives(2, flag=True)`, and then walks
the plane row `self.cusps(2)` carrying one covering to each plane.

A stack-sampled diagnostic on the adopted runtime (`diag-1.log`, a sample every
10 s of the running process's own frame stack) measured the line row of
`Otilde(T_Co) = ker rho`:

| t | RSS | where the process was |
| ---: | ---: | --- |
| 57.1 s | 596.9 MiB | the character quotient done, entering the line row |
| 287.3 s | 1115.3 MiB | `orthogonal_quotients.py:3818 _isotropic_line_class_points` |
| 559.5 s | 1717.5 MiB | `lattices.py:6930 div`, under `finite_ordered_sets` and the GAP orbit |

so the 527-cusp line row alone did not return inside a 580 s command, at
~2.7 MiB/s of growth.  The record's 142 s (`#357`) and 342 s
(`results/issue381-plane-row-route.md`) are both smaller than what this tree
does under this VM's load, and no command of this turn could therefore reach the
plane walk through `tits_building_incidence()` itself.

The slices are consequently taken on the two phases separately, each through the
row's own objects and functions, and each in its own process:

| phase | what it runs | the row's own call it is part of |
| --- | --- | --- |
| `row` | `T_Co`, `Otilde`, the plane's certified parabolic (112 generators), the split's first lift, then N planes of the split with `register_isotropic_lift` per plane | the plane row, `cusps(2)` |
| `carry` | the same N planes, one covering computed at the first by `_plane_parabolic_incidence_flags`, then `transport_covering` per plane, the three `_isotropic_line_image_key` reads the walk makes, and `release_isotropic_transports` | the plane walk inside `tits_building_incidence()` |

**Departures from the dispatched call, stated as departures and not as the
call.**  (i) The ambient flag row is not recomputed: `O(T_Co)` has one orbit of
primitive isotropic flags over `T_Co` (the ambient incidence is one edge), so
one flag built from the slicing plane's own adapted basis
(`lattice.isotropic_flag(v0, v1)` for the plane `span{v0, v1}`) is that row, and
it is patched in place of the row.  It is a fixed cost of the call and not a
per-plane cost.  (ii) The driver's contract pass over the returned relation —
`row_contract`, one pass over the returned certificates — is not run: the
slices measure the call, not the contract.  (iii) The plane walk is measured
through the per-plane functions the walk calls, not by calling
`tits_building_incidence()` and cutting it short: item (iii) is forced by the
line row above, and it is the reason no edge count comes out of these numbers.

### The `TypeError` that killed the first slice: the probe's call shape, not the library's

The first `row-10` attempt died at `quotient.supergroup().one()` with
`TypeError: CoreMor.__call__() missing 1 required positional argument:
'forward'`.  `OrthogonalCharacterQuotient.__init__` sets
`self.supergroup = subgroup.supergroup()`
(`src/sage_extensions/categories/orthogonal_quotients.py:313`), so on the
quotient `supergroup` is an *attribute* holding the ambient group's core
morphism, and a core morphism is called with its forward map:
`CoreMor.__call__(self, forward, inverse=None, **kwargs)`
(`src/sage_extensions/categories/abstract_categories/arrow_categories.py:2543`).
On the subgroup, `supergroup()` is a *method* returning that group -- the walk
itself writes `identity = self.supergroup().one()` -- and the quotient's own
readers write `self.supergroup...` (`orthogonal_quotients.py:604`,
`ambient = self.supergroup`).  The defect was therefore the probe's: it called
the quotient's attribute as if it were the subgroup's method.  Both probes now
write `quotient.supergroup.one()`, and the `row-10` run below passes that line
and registers the plane.  Nothing is filed against the library for it.  What it
did expose is a naming inconsistency between two owners -- `supergroup` is a
method on a subgroup and an attribute on its quotient -- which is recorded here
and not repaired.

## 3. The three slice points

| slice | planes | wall | peak tree RSS | last 10% of the planes | `lifts` at the end |
| --- | ---: | ---: | ---: | ---: | ---: |
| `row-10` | 10 | 220.5 s | 1365 MiB | 5.58 ms a plane | 10 |

The 100- and 1000-plane slices of the same phase are running; this commit
carries the first point, and the next one adds those two.

The phases of `row-10`, in the order the row runs them (the probe's own log,
`.tmp/issue381-runner-kill/row-10.log`):

| phase | wall | RSS after |
| --- | ---: | ---: |
| `T_Co` and the slicing plane | 0.08 s | 276.4 MiB |
| `Otilde(T_Co)` and its character quotient | 0.11 s | 282.4 MiB |
| the plane's parabolic: complete, 112 generators | 4.11 s | 421.2 MiB |
| the split's **first** lift (the finite image's whole coset walk) | **215.40 s** | **1360.4 MiB** |
| the 10 planes of the split, `register_isotropic_lift` each | 0.06 s | 1360.7 MiB |

Per plane of the split, in the order they were taken:
1.794, 7.231, 6.056, 6.716, 5.604, 5.905, 5.590, 5.304, 5.237, 5.583 ms.

So the row phase has one large fixed cost and one small per-plane cost: 215.4 s
and **+939 MiB** in the first lift, which materializes the finite image's coset
walk, and then 5.2–6.1 ms and a fraction of a MiB a plane.  The 0.3 MiB over
nine planes is the size of the per-plane trace at ten planes and is not a
coefficient; the 100- and 1000-plane slices below are what decide it.

## 4. Growth, extrapolation, and whether the row is reachable at all

Decided by the 100- and 1000-plane slices, which are running: a slope needs at
least two points of the same phase.  What the first point already fixes is that
the split's per-plane cost is small and the row's cost is not per plane at all
but two constants -- 215.4 s and +939 MiB at the first lift.  Its per-plane
retention is what the other two points measure.

## 5. The retention filed at its owner

The measurement this filing rests on is
`results/issue381-the-incidence-holds.md`: **63.0 KB a plane**, from
`register_isotropic_lift` (`orthogonal_quotients.py:2533`, writing at `:2551`),
which retains for every plane of the row the span key, the isometry that placed
it, and a fresh tuple of the 112 parabolic generators --
`189720 * 63.0 KB = 11.4 GiB`.  The slices above decide whether that
coefficient holds on this tree; the filing and its issue number follow with
them.

## 6. What these numbers do not decide

* They are not counts.  No `T_Co` incidence value is asserted here, and no
  lattice-database card holds one (lattice-database#7).
* The plane walk's certificate coefficient is not measured: the walk makes one
  certificate per endpoint pair (`retain_flag`,
  `predicate_subgroups.py:964`), and the sizes are arithmetic on the two cusp
  rows and the finite image, not a returned row.
* The line row's own cost is measured only as "more than 580 s on this VM": the
  diagnostic was cut by its own command, not by the operation.
* A segfault seen while preparing the slices, filed separately: `quotient.index()`
  on `Otilde(T_Co)` (`orthogonal_quotients.py:943`) reached
  `_ambient_generators` (`:607`), the port's
  `recursive.py:933 _lattice_action`, `lattices.py:10814 orthogonal_complement`,
  `lattice_morphisms.py:785 right_kernel`, and PARI's `matkerint`, and died with
  `cysignals.signals.SignalError: Segmentation fault`.  The same line had
  returned in earlier runs on the same tree, so it is not deterministic, and the
  slices no longer ask for the index.  This is the class of failure #296 records;
  it is not repaired here.
