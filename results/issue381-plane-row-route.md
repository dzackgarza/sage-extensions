# The `Otilde(T_Co)` and `Otilde+(T_Co)` incidence: what the hours are, and the route out

Where the two kernel rows of #381 stand: `Otilde(T_Co)` and `Otilde+(T_Co)`
each have 189720 plane cusps (#390) and 527 line cusps (#357), and the
incidence call asks, at every plane, one exact question per flag line that the
divided-class invariant does not separate from the plane's line (#570: 5.65 s
warm; 526 of 527 line cusps separated at 0.01 s).  At 5 s a plane the
`Otilde` row was reckoned at 263 hours, so it is not a run.

This note decides the three questions the route turns on and gives the route
with its arithmetic.  Everything was measured on the adopted runtime (Sage
11.0.beta5) at provider `9d63d56d725e58222889cb5f980de299a8a8acdf` -- the head
#570 landed -- with the paused port at `991b88b0`, on `T_Co = <2> + U(2) +
E8(-2)` (D. Dolgachev and S. Kondo, *Enriques surfaces and Borel--Weil--Bott
type duality*, Izv. Math. 77:3 (2013), section 3, equation (3.6), printed
p. 513).

## The two indices the rows are counted by

Measured on that lattice: `A_{T_Co}` has order 2048, `|O(A_{T_Co})| =
46998591897600 = 2^21 3^5 5^2 7 17 31`, and the character quotient's index is
that same number -- the discriminant image of `O(T_Co)` is all of
`O(A_{T_Co})` -- so `Q = rho(O(T_Co)) = O(A_{T_Co})` and
`Otilde(T_Co) = ker rho` is the full preimage.  The two row counts are the
recorded indices of a line's stabilizer image (`|Q| / 89181388800 = 527`,
#325) and of a plane's parabolic image (`|Q| / 247726080 = 189720`, #391);
both divisions are exact, and `189720 = 527 * 360`.

## Question 1: does an invariant of the line separate the `Otilde` orbits in the finite-image class?

**No, and none is needed.**  Two statements, one measurement each.

*No invariant computed from the lattice and the line can.*  Every one of the
527 `Otilde`-line-orbits lies in the single `O(T_Co)`-orbit: the ambient line
row is **1** (measured, 145.65 s).  An invariant of a primitive isotropic line
-- its divisor class, the genus and isometry class of `e^perp/e` with its
induced discriminant data, the class of the plane's Gram data, anything built
from `L` and `e` by lattice operations -- is an `O(L)`-invariant, so it is
constant on that orbit and therefore on all 527.  Separating two `Otilde`
orbits inside one `O(L)` orbit would take a datum that `Otilde` preserves and
`O(L)` does not, and such a datum can only come from the subgroup: it is a
coset of `rho(O(L))`, not a function of the lattice and the line.

*The divided class pair already separates all 527.*  The key the incidence
already computes -- the `rho(Gamma)`-orbit of `{c, -c}` in `A_{T_Co}`, which
for `Gamma = Otilde` is the pair itself, since `rho(Otilde)` is trivial -- was
evaluated at every representative of the row: **527 distinct keys for 527
cusps, every bucket a singleton** (4.34 s for all 527, i.e. 8.2 ms a key).

So at a line vertex the key is a *complete* decision, not a necessary
condition: the row is complete (every primitive isotropic line of the lattice
lies in exactly one cusp of the row -- the premise the empty-bucket answer
already rests on), so a line whose key is carried by one cusp lies in that
cusp.  The 5.65 s question of #570 is asked at exactly such a bucket and
answers what the key has already answered.

## Question 2: can the question be asked once per plane orbit and transported down?

**Yes, and what is transported is a name, not a search.**  The incidence is
`Otilde`-invariant: an element of the subgroup carries a line cusp into a
plane cusp exactly when it carries the pair to another incident pair.  With
`H_P = Stab_{O(L)}(P_0)`, `H_l = Stab_{O(L)}(l_0)` for a line `l_0 < P_0`,
`Q = rho(O(L))` and `Otilde = ker rho`, the subgroup's orbits inside one
`O(L)`-orbit are the double cosets of `(rho(H_P), rho(H_l))` in `Q` (D. Dutour
Sikiri\'c and K. Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
Lemma 3.6, printed p. 22), and the edges of the building are the inclusion
relation between the two vertex rows (ibid., printed p. 5).  Two consequences
follow from that alone:

* the plane cusp `u = Otilde g P_0` has as its line neighbours the
  `rho(H_l)`-cosets inside the double coset `rho(H_P) g rho(H_l)`, so their
  number is `k = [rho(H_P) : rho(H_P) cap rho(H_l)]` -- **the same at every
  plane cusp of the row**;
* the counts satisfy `E = 189720 k = 527 m` with `m = [rho(H_l) : rho(H_P)
  cap rho(H_l)]`, hence `m = 360 k`.

Measured at the source plane -- the `O(T_Co)` plane row's single
representative, whose parabolic is complete with 113 generators (4.87 s) --
the covering has **3 flag lines, and their keys name three distinct line
cusps**.  So `k = 3`: every plane cusp of the `Otilde` row has exactly three
incident line cusps, `E = 189720 * 3 = 569160`, and each line cusp lies in
`m = 1080` plane cusps.  (Equivalently the intersection predicted here has
order `247726080 / 3 = 82575360`, and `|Q| / 82575360 = 569160`.)

The three flags are what the plane's parabolic covering yields; the
divisibility of a line of the plane is a parabolic invariant, so the flags at
one plane can fall into several orbits, and three is how many this plane has.
Whether the three are exactly the divisibility classes is not decided here.
At any other plane cusp `u' = Otilde g' P_0` the three vertices are
`key(g' l_i)`, `i = 1, 2, 3`: three divided-class computations and three
dictionary hits.  No isometry search and no stabilizer question is asked at
any plane but the source.

## Question 3: the per-plane time on ten distinct planes

Ten distinct planes -- each the source plane transported by one of the line
row's own registered words, distinct spans checked -- through the same steps
the public call runs at a plane (`certified_parabolic_generators`,
`_plane_parabolic_incidence_flags`, and the line key):

| plane | vertices (positions in that process's row) | key route | today's per-plane covering |
| --- | --- | ---: | ---: |
| 0 | 0, 2, 1 | 10.1 ms | 4.14 s |
| 1 | 1, 2, 0 | 18.0 ms | 11.85 s |
| 2 | 2, 0, 1 | 16.4 ms | 9.81 s |
| 3 | 3, 2, 34 | 15.2 ms | not taken |
| 4 | 4, 2, 36 | 19.2 ms | not taken |
| 5 | 5, 13, 1 | 16.7 ms | not taken |
| 6 | 6, 9, 1 | 19.0 ms | not taken |
| 7 | 7, 2, 41 | 18.9 ms | not taken |
| 8 | 8, 2, 43 | 14.3 ms | not taken |
| 9 | 9, 6, 1 | 17.7 ms | not taken |

**16.6 ms a plane on the key route; 8.60 s a plane for today's covering
step** (10.1--19.2 ms; 4.14--11.85 s over the three planes where the whole
current step was timed).  Two entries are checks rather than costs: planes 0,
1 and 2 carry the *same* vertex set `{0, 1, 2}`, which is what question 2's
invariance says when they lie in one `Otilde`-orbit, while the other seven
carry seven different sets; and the key's vertex was confirmed by the exact
witness at plane 0 (bucket `[0]`, the cusp contains the transported line,
0.04 s once the plane's word is registered).  Positions are read inside one
process: the row's order is not reproducible across processes (#570 measured
the port's family itself varying), so cusps are named by their keys, not by
these numbers.

**The 263 hours is an undercount.**  The row pays 8.60 s a plane of covering
before any question -- 113 generators conjugated, their images, the word
section, three Levi restrictions, the double cosets -- which is 453 hours on
its own; and the covering returns three flags, so the exact question of #570
is asked three times a plane, 5.65 s each warm, not once.

## The route, and its arithmetic

**Fixed cost, once per process and per shard:**

| step | measured |
| --- | ---: |
| the `Otilde` line row, 527 representatives (the ambient row is 145.65 s of it) | 307.91 s |
| the 527 keys and the key index | 4.34 s |
| the ambient plane row (1 representative) | 1.81 s |
| the ambient flag row (1 flag) | 8.08 s |
| the source plane's parabolic family (113 generators, complete) | 4.87 s |
| the source plane's flags and their three vertices | 14.97 s |

5.7 minutes, and the same for either kernel row.  The line row is the whole of
it; a shard that keeps the key index needs it, and nothing else here.

**Per plane:** the row's own lift (154 ms a double coset, the rate #390
measured) plus the 16.6 ms of question 3.  One row is
`189720 * (0.154 + 0.0166) s = 8.97 h`; at `N = 8` shards of 23715 planes it
is 61 minutes of word spelling, 7 minutes of incidence and 6 minutes of fixed
cost a shard, so the two kernel rows are a few hours of CI.

**What sharding needs and does not have yet.**  The plane row is built by
`_plane_orbit_from_parabolic_stabilizer`, whose walk materializes its whole
transversal before it yields (`walk_data = [entry for entry in coset_walk(edges,
degree, base)]` in
`orthogonal_quotients._iter_splitting_isometries_in_im_rho_from_image`), so a
*slice* of the row costs the whole walk: taking the first ten lifts of that
walk did not return inside 130 s in this round's probe.  A shard can split the
word spelling and the incidence today, not the walk, until #390's named repair
lands (one BFS over the right-coset action of `rho(O(L))` recording each
reached word).  That repair is the other half of the job: the incidence is no
longer the cost, the row is.

## What is not done here

* No library change is landed.  Two repairs follow from the measurements --
  reading a line vertex off a singleton key (`tits_building_incidence`'s
  `line_vertex_candidates`), and skipping the plane's parabolic and double
  cosets where the plane has a registered lift and the source plane's flags --
  and neither changes any answer, so neither has a red test on a library call;
  they also want a full row to validate, which is what the job is for.
* The ten-plane measurement runs the per-plane steps the public
  `tits_building_incidence()` runs, not the public call itself: that call has
  no plane parameter, it builds both rows internally, and its plane row on
  this lattice is the 8-hour walk.
* The three planes whose covering was timed are three, not ten; the key route
  was timed at all ten.
* The edge count `E = 569160` is stated from `k = 3` and the double-coset
  count of question 2; it is not enumerated, and the intersection named in the
  next section is the check that would make it independent of the covering.

## Next image-run inputs

In this order:

1. **The controls.**  `python3 tests/coble_gamma_co_2_incidence_rows.py --rows
   'O' --lattice Tco` (one edge, 10.11 s on main) and `--rows
   'Gamma_{Co,2}' --lattice Tco` (13 edges over 4 line and 7 plane cusps,
   1685 s on main).  The second is the only row on `T_Co` whose four line
   cusps are few enough to show a *shared* key, which the key route must fall
   back to the witness on.
2. **The intersection that decides the count.**  One GAP run on `T_Co`:
   `rho(H_P)` from the source plane's 113 certified parabolic generators,
   `rho(H_l)` from the line's `exact_isotropic_stabilizer_generators` (whose
   image is exact by construction), then `Intersection`, checking
   `|rho(H_P) cap rho(H_l)| = 82575360` and so `E = 569160`.  The row's edge
   count with no plane enumerated.
3. **The ten-plane slice on the image.**  `--rows 'Otilde' --lattice Tco
   --planes 10`, once the driver can take a slice (it cannot today).  Until
   then the probe of this round is the measurement; its inputs are provider
   `9d63d56`, port `991b88b0`, the adopted image,
   `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/repos/sage-extensions/src`,
   one process.
4. **The row, after #390's BFS.**  `--rows 'Otilde,Otilde+' --lattice Tco
   --cap 3600` in 8 shards of 23715 planes, a shard being 61 minutes of word
   spelling, 7 minutes of incidence and 6 minutes of fixed cost on the
   measured rates.
