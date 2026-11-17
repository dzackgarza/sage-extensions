# The incidence's walk needs no constructed parent per plane: the edges are decided by divided classes

`results/issue585-the-walks-per-plane-retainer.md` measured the incidence walk's
350-400 KB a plane and found it to be one constructed subobject per line and per
plane, kept for the process by the library's construction caches.  This note
computes the same edges from the data that decides them.  Measurements are on
the adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5) at `main`
`bf92710`, load average 0.7-8.5 from other projects' work on the same VM; each
log's header names the tree and the load.  The probes are in `.tmp/issue585/`.

## 1. What one plane of the incidence needs, read off the certificate route

`PredicateSubgroups.tits_building_incidence` (`predicate_subgroups.py`) walks the
plane cusps `cusps(2)` and, at each plane `P`, needs exactly this:

| what | where it comes from |
| --- | --- |
| the plane `P` itself | the cusp's own representative; the row built it |
| the registered lift `s_P`, carrying the covering's plane `P_0` onto `P` | `quotient.isotropic_lift_of(P)`, one span-keyed dictionary hit |
| one covering per ambient flag orbit, computed once at `P_0` | `_plane_parabolic_incidence_flags`; three flags for `T_Co` |
| the covering's carried lines at `P` | `transport_covering`: `move = s_P s_{P_0}^{-1}` applied to each flag |
| the line cusp each carried line lies in | the `rho(Gamma)`-orbit of the line's divided class pair `{c, -c}` (`_isotropic_line_image_key`), and the row's index by it |
| the plane cusp | the cusp being walked |

The pairing that decides an edge is therefore **not** a containment: it is the
`rho(Gamma)`-orbit of the line's divided class pair naming exactly one line cusp
of the row.  Containment is the reason that orbit is an invariant -- an isometry
`g` carries `c = [v/div(v)]` to the divided class of `gv`, so a line of `P_0`
carried onto `P` has its class among `P`'s -- but containment is necessary and
not sufficient, and the route that decides by it would be a different
computation.  The divided classes enter the certificate route at exactly one
place, as the key of a carried line; everything else in the walk is flags,
subobjects and transporters of them.

## 2. The route

`PredicateSubgroups.tits_building_incidence_by_divided_classes` computes the
same relation from the classes:

* the row's one covering per ambient flag orbit is computed once, at the first
  plane of the row that has a registered lift for that source, and kept as its
  three line class pairs (`_isotropic_line_class_points`) -- one plane's worth of
  flags for the whole row;
* at each plane the composite `s_P s_{P_0}^{-1}` is read as its action on
  `A_L`, one element of `O(A_L)` (the quotient's own discriminant component,
  `_divided_class_action`), and the three class pairs are carried by it
  (`_carried_divided_classes`, GAP's setwise image);
* each carried pair's `rho(Gamma)`-orbit names its line cusp in the index the
  row already holds, and the edge is that cusp with the cusp being walked;
* one flag is built at one plane, to check that the carried class pair is the
  class pair of the carried line (`_isotropic_line_class_points` of the
  transported line), so the finite action is pinned to the lattice's own image
  rather than to a convention about the group law.

The returned relation is a `FiniteOrderedSets` point set of
`DividedClassCuspIncidence` records: the two cusps and the class-orbit datum
that named the line vertex, no flag, no subobject, no transporter.  The
certificate route is unchanged and remains the one that answers where a
transporter is wanted.

The route refuses rather than guesses in three places, each naming what is
missing: a subgroup that cuts no discriminant condition (no class data names a
line); a subgroup that is not invariant under conjugation (each plane's covering
would have to be computed at that plane, which is the certificate route's work);
and a line whose orbit names more than one cusp of the row, where the class data
does not separate the vertices and a lattice witness does.

## 3. The edges agree

Three comparisons, because the two routes can be run together on different
lattices.

**On `T_Co`'s own slice, line by line.**  `probe-585-classes.py` walks ten
planes of `Otilde(T_Co)`'s row and, at every one of the thirty lines, compares
the class pair the finite image carried with the class pair of the line the
certificate route actually carried there (`_isotropic_line_class_points` of the
transported line), and the class route's key with the certificate route's own
`_isotropic_line_image_key` of that line.  `classes-10.log`: 30 of 30 class
pairs agree and 30 of 30 keys agree.  `probe-585-walk.py` with
`PROBE_PHASE=check`, over the row's first hundred planes (`walk-row-1000.log`):
**297 of 297**, and no disagreement at any line of any plane.

The line cusp row of `T_Co` is what an edge-set comparison on `T_Co` itself
would need, and it does not return here: `probe-585-linerow.py` builds
`Otilde(T_Co)`'s `cusps(1)` alone and is killed at 552 s still inside the row
(`linerow.log`), so the cusp objects the edges join are not available in this
session.  That row's cost is #390's, not this route's.

**On the lattices whose rows return, edge set against edge set.**
`tests/lattices/test_the_incidence_decided_by_divided_classes.sage` runs both
public calls and the flag row on `U + U(2) + <-2>` (both kernel groups) and on
`U + U + <-4>`, and asserts that all three state one relation: 4 edges over 3
line and 2 plane cusps on the first, 1 edge over 1 and 1 on the second.  The flag
row, `isotropic_orbit_representatives(2, flag=True)` read as endpoint pairs, is
the independent computation: it shares no code with either incidence route.  Six
tests pass in 76.06 s (these three and the three of
`test_the_incidence_line_vertex_is_named_by_the_finite_image.sage`, which consume
the certificate route this changes nothing about).

Two facts about reading that relation in a session file, both of which cost a
run to find and neither of which is about the mathematics: a cusp's equality is a
transporter search, which reads the quotient's retained transports, so the routes
fill it as they walk -- a row's positions must be read by identity, and the flag
row before the routes run; and a `{...}` display in a session file is the
library's `Owned_FiniteLiteralSet`, whose `==` with a `set()` is a statement about
two kinds of set, so an edge set is built with `set()`.

## 4. What it costs a plane

Every step of the walk, priced separately on the row's own planes
(`probe-585-walk.py` with its phases timed, `walk-phases-1000.log`; the figures
are the band means at plane 10 and at plane 1000 of the same run):

| step a plane | plane 10 | plane 1000 |
| --- | ---: | ---: |
| the registered lift, by span | 1.00 ms | 0.79 ms |
| the composite as an element | 0.87 ms | 0.61 ms |
| **its action on `A_L`** (`discriminant_morphism`) | **51.44 ms** | **64.65 ms** |
| the three class pairs carried | 0.09 ms | 0.05 ms |
| the three line keys (cache hits) | 0.06 ms | 0.02 ms |
| **the walk** | **53.4 ms** | **66.1 ms** |

and the same step on the certificate route, measured in the same harness
(`walk-row-1000.log`, `PROBE_PHASE=check`): the carry, the three keys and the
release at **38.7 ms a plane**, flat in the plane count.

So this route does not make the row faster: the class data is carried in 0.05 ms
a plane and the *action* that carries it costs 51-65 ms, because
`discriminant_morphism` inverts the isometry's matrix to read its dual action on
`L^\#/L`, and the row's lifts are words whose entries grow with the plane.  The
route that avoids that inversion is not a second implementation of the dual
action but the datum the split already computes: it evaluates `rho` on every lift
to check its own word section, so the finite element is in its hand and is
dropped.  Registering it beside the lift would make the walk's action a product
in `O(A_L)`; that is the next repair, and it is not made here.

Two readings measured and **not** shipped: the action through the lattice's owned
`rho` morphism, `discriminant_representation()(move)`, at 41.5 ms a plane (the
first call, which is the whole cost -- the second call on the same element is a
cache hit at 0.12 ms, which is why a probe that times it twice prices it wrong);
and the plane's divided class set, `_divided_discriminant_classes`, at 7.2 ms a
plane, which is what a containment test would need and containment is not what
decides an edge.

**Memory.**  `walk-phases-1000.log` bands, walk only, no certificate work in the
process: plane 100 **1421.1 MiB**, plane 1000 **1428.2 MiB** -- **7.9 KB a
plane**, steady over the nine bands (0.7-0.9 MiB each).  The certificate route's
coefficient on the same slice is 371-384 KB a plane
(`results/issue585-the-walks-per-plane-retainer.md`), so the walk's retention
falls 47-48 fold.  The relation adds **121 B a record** (200000 held copies of a
real one, `probe-585-recordsize.py`), three a plane.

What the 7.9 KB is made of is **not** established here.  The walk's Python-side
holdings are the relation's tuples (0.2 KB a plane) and its key index (423
frozensets over the whole run), which do not account for it; the candidates are
the GAP objects the three carries build per plane and whatever the discriminant
morphism builds per element.  A `tracemalloc` comparison of planes 100 to 1000
is the measurement that decides it, and that measurement is not in this note.

**The relation's ingress.**  `finite_ordered_set(tuple(records))` identifies
repeated points through a dictionary of them, and a cusp's hash is constant over
its universe by the category's own rule (`_ArithmeticCuspEngine.__hash__`), so
that ingress compares every point with every other: one comparison of two
distinct records costs **3.35 ms** (a transporter search,
`probe-585-recordsize.py`) and the literal ingress of four edges already costs
**57.2 ms** against **0.040 ms** for the same four through a supplied inverse.
At 569160 edges the literal ingress is ``n(n-1)/2`` such comparisons and cannot
return.  The route therefore builds its set through `from_indexed` with the
identity index its walk already keeps; the points are distinct objects because
the walk admitted one per endpoint pair.

## 5. What the row still spends

At 189720 planes, with the measured coefficients:

| term | coefficient | at 189720 planes |
| --- | ---: | ---: |
| the walk (this route) | 7.9 KB a plane | **1.43 GiB** |
| the relation (121 B an edge, three an edge pair a plane) | 363 B a plane | 0.07 GiB |
| the plane row's representatives (#584) | 63.0-66 KB a plane | 11.4-12.0 GiB |
| fixed cost of the call | 1.25-1.4 GiB | 1.25-1.4 GiB |
| **peak** | | **14.2-14.9 GiB** |

The walk is no longer the largest term: it falls from 63-72 GiB to 1.43 GiB, 45x,
and the row's memory is now the plane row's own representatives at 11.4-12.0
GiB.  Against the runner's 16 GiB the row is inside, with 1-2 GiB of headroom,
and the next owner is #584.

The time does not fall with it: 53-66 ms a plane is 10000-12500 s at 189720
planes, against the driver's 10800 s cap.  The three terms that bound the row are
therefore the plane row's memory, the dual-action inversion's 51-65 ms, and the
cap; the first is #584's and the second is the repair named in section 4.
