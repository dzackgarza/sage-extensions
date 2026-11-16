# What the T_Co incidence holds as it walks its planes

Measured on the adopted runtime (Sage 11.0.beta5, image rootfs, the launcher's own
log) at `bcad374a699b677d1ba9b4317c45b1b1bf540e18`, the `main` this round lands on,
on `T_Co = <2> + U(2) + E8(-2)` (D. Dolgachev and S. Kondō, Izv. Math. 77:3
(2013), §3 equation (3.6), printed p. 513), in the kernel row
`Otilde(T_Co) = ker rho`.

## Why a probe, and what it is a probe of

The two kernel rows were dispatched (`results/coble-kernel-incidence-rows.yml`,
`rows: "Otilde,Otilde+"`, `lattice: "Tco"`, `cap: "10800"`, `budget: "28800"`).
Image run 43964809482 was killed by the kernel after 80 minutes without printing a
row; run 43838676844 was killed the same way, and the Otilde+ run was cancelled.
A timing question is answered from a run's own stage records (`CONTRIBUTING.md`
ENV-03), but a *resident-memory* question has no record — the stage records carry
wall time — and the killed runs have no row. So the coefficients below come from
one probe that drives the row's own mechanism stage by stage over planes of
`T_Co` and samples `/proc/self/status`'s `VmRSS`.

The probe is `.tmp/issue381-memory/probe-incidence-memory.py`; its log is that
directory's `probe-421d836-run4.log`, and its own lines are pasted below. Every
plane it registers is a primitive isotropic plane of `T_Co` and every carrying
isometry is an isometry of `T_Co` (a power, or a short word, in the ambient
orthogonal group's own generating family), so the registry entries and the
carries are the row's own functions on the row's own objects. What the probe does
not use is #390's coset walk: it feeds the same registration and the same carry
with planes it makes itself, because the row that walk enumerates does not return
inside one command.

## The stages, and the coefficient each one gives

The stages are cumulative, so a stage's own growth is the difference of its own
samples. `rss` is MiB, `planes` the planes the stage had processed when the
sample was taken, and the registry columns are the sizes of the quotient's own
dictionaries as the sampler read them.

| stage | what it does per plane | samples | coefficient |
| --- | --- | --- | ---: |
| A | the row: a primitive isotropic plane, its image under one ambient isometry, and `register_isotropic_lift` for it | 642.5 MiB at 1 plane, 842.3 MiB at 3250 | **63.0 KB a plane** |
| B | the row's one covering, at the retained plane | 851.9 MiB before, 979.6 MiB after | 128 MiB, once |
| C | `transport_covering`: the covering carried to the plane, its three flags held as the incidence holds them, and its three line transports registered | 1007.4 MiB at 100 planes, 1849.3 MiB at 3100 | **287.4 KB a plane** |

Verbatim, the samples the two coefficients come from:

```
    A: 1 planes so far, 0.0 s, rss   642.5 MiB lifts       2 transports       0 coverings    0 bridges    0
    A: 3250 planes so far, 24.0 s, rss   842.3 MiB lifts    3251 transports       0 coverings    0 bridges    0
    C: 100 planes carried, 300 flags held,    39.84 ms a plane, rss  1007.4 MiB lifts    3303 transports     287 coverings    1 bridges    0
    C: 3100 planes carried, 9300 flags held,    15.35 ms a plane, rss  1849.3 MiB lifts    3303 transports    8317 coverings    1 bridges    0
```

`VmRSS` rises with the planes processed, linearly, in both structures, and the
two slopes are the coefficients above: (842.3 − 642.5)/3249 = 0.0615 MiB, and
(1849.3 − 1007.4)/3000 = 0.2806 MiB.

The registry column in the C samples is worth reading twice: 8317 datums at 3100
planes is 2.68 a plane, not 3.00, because the registry is keyed by the line's
span and a line of one plane can be a line of another — the repeats collapse. The
carried *flags*, by contrast, are exactly three a plane: nothing collapses them,
and each retains its own line and plane subobjects.

## What the coefficients say

* **The row's own record: 63.0 KB a plane.**  The plane's subobject, the
  registered lift that produced it and the span key the registry is keyed by —
  that is what `register_isotropic_lift` retains, one per plane, and it is
  #390's row.  At 189720 planes that is **11.4 GiB**, before a cusp object or an
  edge exists.  It is not this round's repair: the row returns one representative
  per orbit, so shrinking it is a change to what the row returns.
* **The carried covering: 287.4 KB a plane.**  The three flags of the plane and
  the three line transports `transport_covering` registers for them, held in the
  incidence's `sourced_flags` list and the quotient's transport registry.  At
  189720 planes that is **52.0 GiB**.  Nothing reads either after the plane's
  edge certificates exist, and this is what this round repairs.
* **The row's covering: 128 MiB, once per source family.**  One covering is the
  parabolic's 112 generators, its image in the character product, the word
  section and the double cosets.  It is a constant of the row, not a coefficient.

So the two kernel rows of `T_Co` cannot return as the code stood, at either
coefficient: a 6 GiB cap is passed after about 21000 carried planes at the second
coefficient alone, and the row's 11.4 GiB is passed before the incidence starts.
Which of the two killed the image runs is not settled here and is not claimed:
neither printed a row, and a memory question has no run record to read.

## What the repair changes, and what was not measured

The incidence no longer holds either per-plane structure.  Each plane's edge
certificates are made while the row holds the plane, and the plane's flags and
the transport data of its carried lines are dropped there
(`OrthogonalCharacterQuotient.release_isotropic_transports`), so what the call
retains while it walks is its coverings and the relation it returns.  The
contract — a carried line keeps no transport datum, and the edges that keep one
are at most as many as the coverings' flags — is
`tests/lattices/test_the_row_retains_no_transport_for_a_carried_line.sage`.

**Not measured in this round.**  Two numbers:

* the edge certificates' own coefficient.  The probe's fourth stage runs the
  public call over the same planes, and it did not reach them inside its command:
  the row's 527 line cusps alone took over two minutes of it under the contention
  of a second container, and the stage was cut.  The relation's size is known
  without it — `E = 189720 k` certificates with `k = 3`
  (`results/issue381-the-walk-and-the-intersection.md`), so 569160 certificates,
  each retaining a flag and two transporters.
* the post-repair coefficient of the same stages.  The repair removes the two
  structures stage C measures, and the contract test shows that it does; the
  bytes it saves on `T_Co` are the 287.4 KB a plane of stage C, extrapolated as
  above and not re-measured.

## What is left, and it is the larger half

The relation the call returns is the row's answer and not a leak, so its 569160
certificates are a floor on the call's footprint; and the row's own 63 KB a plane
is 11.4 GiB before the incidence starts.  Those two are the next units — the
relation as vertex positions rather than retained certificates, and a plane row
that realises its representatives instead of retaining them — and the image run
should not be dispatched again until at least the second is repaired.  This
round repairs neither, and says so rather than dispatching a run that would be
killed the same way.
