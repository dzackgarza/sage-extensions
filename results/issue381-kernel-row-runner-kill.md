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

| slice | planes | wall | peak tree RSS | the split's first lift | per plane of the split | RSS per plane of the split |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `row-10` | 10 | 220.5 s | 1365 MiB | 215.40 s | 5.2-6.1 ms | too small to resolve |
| `row-100` | 100 | 201.6 s | 1295 MiB | 195.91 s | 5.16-5.44 ms | 65.3 KB |
| `row-1000` | 1000 | 194.8 s | 1359 MiB | 183.72 s | 4.84-5.03 ms in eight of ten bands | 66 KB |

The phases of `row-10`, in the order the row runs them (the probe's own log,
`.tmp/issue381-runner-kill/row-10.log`):

| phase | wall | RSS after |
| --- | ---: | ---: |
| `T_Co` and the slicing plane | 0.08 s | 276.4 MiB |
| `Otilde(T_Co)` and its character quotient | 0.11 s | 282.4 MiB |
| the plane's parabolic: complete, 112 generators | 4.11 s | 421.2 MiB |
| the split's **first** lift (the finite image's whole coset walk) | **215.40 s** | **1360.4 MiB** |
| the 10 planes of the split, `register_isotropic_lift` each | 0.06 s | 1360.7 MiB |

Per plane of the split, in the order they were taken: `row-10` 1.794, 7.231,
6.056, 6.716, 5.604, 5.905, 5.590, 5.304, 5.237, 5.583 ms; `row-100` every
ten-plane band from 20 to 100 planes between 5.157 and 5.442 ms; `row-1000`
4.841, 4.665, 4.970, 4.985, 5.032, 4.985, 4.872, 5.069 ms a plane in eight of
its ten bands, the other two at 9.379 and 9.779 ms under the VM's load (load
average 1.3-3.9 across these runs).  The three runs are three separate
processes, each starting from `T_Co`.

So the row phase is one constant and one small per-plane cost: 183.7-215.4 s and
**+0.85 to +0.94 GiB** at the first lift -- the finite image's whole coset walk,
held for the row -- and then 4.8-5.5 ms a plane.

The walk's own per-plane work, on the row's own objects
(`probe-381-carry.py`: one covering at the first plane, then
`transport_covering`, the three `_isotropic_line_image_key` reads, and
`release_isotropic_transports`):

| slice | wall | peak tree RSS | the covering, once | carry a plane | keys a plane | RSS a plane after the covering |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `carry-10` | 176.6 s | 1249 MiB | 8.23 s | 13.15 ms | 14.82 ms | ~400 KB |
| `carry-100` | 203.9 s | 1400 MiB | 8.28 s | 12.95 ms | 18.53 ms mean | 350 KB |
| `carry-1000` | 243.9 s | 1612 MiB | 8.3 s | 15.24 ms mean, 12.7-14.7 ms in its steady bands | 15.58 ms mean | 375 KB |

The keys' mean over `carry-100` is pulled up by one band at 123.8 ms a plane; its
steady bands are 11.1-14.9 ms.  The carried transports are released every plane
-- the registry reads 1 to 2 datums at every sample -- so the 350 KB a plane is
not the transport registry.  The three carry slices are three separate
processes, and the 1000-plane one's retention is taken over planes 100 to 1000
(RSS 1278.9 to 1608.3 MiB), the allocator returning pages early in that run.

## 4. Growth, extrapolation, and whether the row is reachable at all

**The verdict: the cost per plane is flat, and the row's memory is linear in the
plane count.**  Three points and two internal traces agree.

*Wall time per plane does not rise with the planes already processed.*  The
100-plane slice holds 5.157-5.442 ms a plane across every ten-plane band from
plane 20 to plane 100; the 1000-plane slice holds 4.84-5.03 ms a plane in eight
of its ten 100-plane bands and reaches 9.38 and 9.78 ms in two of them under this
VM's load.  A slope in the last band over the first would show as a trend across
the bands; there is none.

*RSS per plane does not rise either; it is a constant 65-68 KB a plane.*  The
1000-plane slice's own bands, cumulative RSS at 100 planes and then every 100:
1296.2, 1301.9, 1308.0, 1314.7, 1321.2, 1327.9, 1334.7, 1341.5, 1348.0, 1354.7
MiB -- increments of 5.7, 6.1, 6.7, 6.5, 6.7, 6.8, 6.8, 6.5, 6.7 MiB per 100
planes.  The 100-plane slice gives 65.3 KB a plane over its last 80 planes.  The
10-plane slice cannot resolve the coefficient (0.3 MiB over nine planes, RSS's
own granularity) and is not used for it.

**Extrapolation to 189720 planes.**  At the measured 66 KB a plane that is
`189720 * 66 KB = 11.7 GiB`; at the coefficient #584 carries, 63.0 KB, it is
11.4 GiB, and the two agree within the sampling.  Add the fixed cost this phase
also pays -- `+0.85 GiB` at the split's first lift (421.1 MiB to 1290.3 MiB in
the 1000-plane slice) and the ~0.28 GiB interpreter baseline -- and the plane row
alone holds about **12.8 GiB resident** at 189720 planes, against a
GitHub-hosted runner's 16 GiB shared with its container.  That is the kill: the
row was four-fifths of the way into a footprint its runner does not have, at a
time (8649 s) when neither the 10800 s cap nor the 28800 s budget had fired.

*Time, by contrast, extrapolates inside the cap.*  `189720 * 5.0 ms = 949 s` for
the split, plus 184-215 s of fixed cost, plus the line row (measured at more than
580 s here, 342 s in `results/issue381-plane-row-route.md`), plus the walk at
27 ms a plane (carry 13.0 ms + keys ~14 ms) `= 5122 s`: about **1.9 hours**
against the driver's three-hour cap.  So the cap was never what the row needed;
the ceiling was.

**Whether the row is reachable on the runner once #584's retention is gone.**
Removing it is necessary and, on these numbers, not sufficient.  The plane row
would fall to about 1.2 GiB (fixed lift plus baseline), and the time fits.  But
the walk's own per-plane work measured a *second* flat retention: 3.2 MiB over
eight planes in `carry-10` and 34.7 MiB over 99 planes in `carry-100`, i.e.
**350-400 KB a plane**, which at 189720 planes is 62-71 GiB -- five times the
lift registry, and on its own enough to make the walk unreachable.  It is not
the transport registry: `release_isotropic_transports` runs every plane and the
registry reads 1 to 2 datums at every sample.  The walk's per-plane objects are
the carried flags (not retained), the three `_isotropic_line_image_key` reads,
and the certificates (not made here).  `isotropic_class_orbit`
(`orthogonal_quotients.py:2356`) is a `@cached_method` keyed by a per-line GAP
set, so it retains one entry per carried line -- the candidate owner.  These runs
do not separate it from the GAP objects and string markers such an entry holds,
so the attribution is recorded here as a candidate and nothing is filed or
repaired for it.

## 5. The retention filed at its owner

The per-plane retention of the plane row is filed as **sage-extensions#584**,
filed by the person because this project's GitHub connection cannot open issues;
#381 is blocked by it, and nothing here re-files or repairs it.

| what | value |
| --- | --- |
| the operation | `OrthogonalCharacterQuotient.register_isotropic_lift`, `src/sage_extensions/categories/orthogonal_quotients.py:2533`, the write at `:2551` |
| what it retains per plane | the plane's span key, the isometry that placed it, and a fresh tuple of the 112 parabolic generators |
| the coefficient | 63.0 KB a plane (`results/issue381-the-incidence-holds.md`), confirmed here at 65.3 KB (100 planes) and 66 KB (1000 planes) on `42b7cf1a` |
| at 189720 planes | 11.4-11.7 GiB, plus 0.85 GiB of fixed cost: ~12.8 GiB |
| the row it blocks | `PredicateSubgroups.tits_building_incidence` (`src/sage_extensions/categories/group/predicate_subgroups.py:718`) over the two 189720-plane rows, run by `tests/coble_gamma_co_2_incidence_rows.py --rows Otilde,Otilde+ --lattice Tco` |
| what it costs the runner | the kill at 8649 s recorded in section 1 |

The per-plane retention the *walk* adds, 350-400 KB a plane, is a second owner
and a second coefficient; it is measured in section 4 and is not #584's unit.

## 6. What these numbers do not decide

* They are not counts.  No `T_Co` incidence value is asserted here, and no
  lattice-database card holds one (lattice-database#7).
* The plane walk's certificate coefficient is not measured: the walk makes one
  certificate per endpoint pair (`retain_flag`,
  `predicate_subgroups.py:964`), and the sizes are arithmetic on the two cusp
  rows and the finite image, not a returned row.
* The line row's own cost is measured only as "more than 580 s on this VM": the
  diagnostic was cut by its own command, not by the operation.
* The walk's per-plane retention is measured at 10, 100 and 1000 planes, and all
  three give the same constant, 350-400 KB a plane, with no trend across their
  bands; the 1000-plane figure is 375 KB over planes 100 to 1000.  The ``carry``
  slice's mean carry and key times are pulled up by load spikes and by the
  allocator's page returns, so the steady bands are what is quoted.
* A segfault seen while preparing the slices, filed separately: `quotient.index()`
  on `Otilde(T_Co)` (`orthogonal_quotients.py:943`) reached
  `_ambient_generators` (`:607`), the port's
  `recursive.py:933 _lattice_action`, `lattices.py:10814 orthogonal_complement`,
  `lattice_morphisms.py:785 right_kernel`, and PARI's `matkerint`, and died with
  `cysignals.signals.SignalError: Segmentation fault`.  The same line had
  returned in earlier runs on the same tree, so it is not deterministic, and the
  slices no longer ask for the index.  This is the class of failure #296 records;
  it is not repaired here.
