# What one plane of the incidence costs after the row's first

Measured on the adopted runtime (Sage 11.0.beta5, image rootfs, the launcher's
own log) at `082dddbe7643cd7ba1ac83738a092050166218a4` with the paused port at
`991b88b0`, on `T_Co = <2> + U(2) + E8(-2)` (Dolgachev--Kondo, Izv. Math. 77:3
(2013), section 3, equation (3.6), printed p. 513), in the kernel row
`Otilde(T_Co) = ker rho`.

## What the row retains, and why the carry is exact

The incidence at a plane `P` covers the `Stab_Gamma(P)`-orbits of the lines of
`P` by the plane's parabolic: the certified family at `P`, its image in the
finite character product, the word section, and the double cosets
`K \ Pi / H` reduced to `chi(K) \ chi(Pi) / chi(H)` (D. Dutour Sikiric and
K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  That is one datum of
the *row*.  When `Gamma` is invariant under conjugation by an ambient isometry
`g`, the family at one plane carried by `g` is the family at `g`'s image of it,
with the same orbits and the same count, so a second plane costs one carry and
no computation.

`OrthogonalCharacterQuotient` retains one record per source family: the plane
the computation happened at, the registered lift onto it, and the family.
`isotropic_covering_of(plane, source)` answers that record only at the plane it
was computed at; `isotropic_covering_reference(source)` answers the row's
record; `transport_covering(reference_lift, flags, lift)` carries it by the
composite `lift * ~reference_lift`.  `preserves_conjugation` is the decision
that makes the carry exact, and it is true for every kernel of a character --
`Otilde` and `Otilde+` included.

## The measurement

One retained plane in the `Otilde(T_Co)` row, then five other planes of the row
carried from it.  The five are the retained plane's images under reflections of
the lattice in five roots; each reflecting isometry is outside `Otilde`, so each
image is a plane of a different `Otilde`-orbit and not a repeat of the retained
one.  All five spans are distinct and none is the retained span.

| stage | measured |
| --- | ---: |
| `Otilde(T_Co)` and its quotient, index 46998591897600 | 52.08 s |
| the retained plane, its 112 certified parabolic generators, its lift | 3.82 s |
| the row's one covering at that plane (three flags) | 8.46 s |
| five distinct target planes, one registered lift each (72 candidates tried) | 0.12 s |
| the carry, plane 1 / 2 / 3 / 4 / 5 | **13.25 / 13.45 / 13.57 / 13.41 / 13.46 ms** |
| the same covering computed at plane 1 instead of carried | **8.06 s** |

So the plane's covering is paid once for the row and once per ambient flag
orbit, and every other plane is about `13.4` ms: two registry hits, one
composite isometry and three flag transports.  Each carry registers the
transports of the carried lines with the same isometry, which is what the edge
certificates of that plane read.

The 8.06 s is the from-scratch covering at a plane whose parabolic family is
already registered (the conjugate family).  A plane with no registered lift
pays more: the plane's own certified parabolic and its right-coset action, the
`101.18 s` and `144.68 s` measured in
`results/issue381-the-walk-and-the-intersection.md`.  Both are routes a plane's
covering takes when nothing is carried; neither is on the carried one.

## Diagnosis of the defect, which is not a cost

On `U + U(2) + <-2>`, whose two kernel rows have two plane cusps and two
ambient flag orbits each, the parent computed the covering **four** times per
row (two planes times two source families), called `transport_covering` **zero**
times, and left a four-record registry; the head computes it **twice** (once per
source family), carries it twice, and leaves two records.  The count is what
locates the defect -- the registry was keyed by the target plane for both the
write and the read, so no covering was ever found at a plane other than the one
that made it -- and the cost of it is the table above.

## What this does not decide

The two `T_Co` kernel incidence rows are still 189720 planes each (#390), and
the incidence over them is the dispatched job's run:
`results/coble-kernel-incidence-rows.yml`, installed with

    mkdir -p .github/workflows && cp results/coble-kernel-incidence-rows.yml .github/workflows/

and dispatched with `rows: "Otilde,Otilde+"`, `lattice: "Tco"`, `cap: "10800"`,
`budget: "28800"`.  This round did not dispatch it; the probe above is the first
six planes of that run and nothing else.  The per-flag cusp matching that
dominated the `Gamma_{Co,2}` row (`results/issue381-kernel-incidence-rows.md`,
1685.31 s for 4 line and 7 plane cusps) is a separate cost and is untouched
here.
