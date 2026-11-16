# The plane row's walk, the covering, and the edge count as one index

Measured on the adopted runtime (Sage 11.0.beta5) at provider
`db0a12eb41bb84e7d89b0f45920f8baf70e016bc` with the paused port at
`991b88b0`, on `T_Co = <2> + U(2) + E8(-2)` (Dolgachev--Kondo, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513).

## What a slice of the plane row costs

The brief for this round proposed making the plane row's walk yield lazily,
since `walk_data = [entry for entry in coset_walk(edges, degree, base)]`
materialises the whole transversal before the first lift.  Timed one stage at
a time on `T_Co`, that premise does not hold:

| stage | measured |
| --- | ---: |
| the ambient plane row and the plane's certified parabolic (113 generators) | 101.18 s |
| `IsomorphismPermGroup(im rho)` (degree 2047) | 1.01 s |
| `rho(H_P)`, the plane's parabolic image | 5.04 s |
| `FactorCosetAction` -- the right-coset action on 189720 cosets | **144.68 s** |
| `coset_walk` -- the whole transversal of 189720 points, in GAP | **0.33 s** |

The transversal is a third of a second; the walk is not what makes a slice
expensive.  Before the first lift the route pays the plane (101.18 s) and the
coset action (144.68 s), about four minutes, and after that a lift costs what
#390 measured for its spelling, 154 ms.  So "the first ten lifts return in
seconds" cannot hold at any laziness of the walk: the fixed cost is the
action, and building that action on 189720 cosets is where the four minutes
are.  A slice of the row is available today at that fixed cost, and the driver
option that takes it is a driver option, not a library change.

Also measured here and used below: `|rho(H_P)| = 247726080`, the plane's
parabolic image, of index `46998591897600 / 247726080 = 189720`.

## The edge count as one index

The plane cusp's line neighbours are the `rho(H_l)`-cosets inside one double
coset `rho(H_P) g rho(H_l)` (Dutour Sikiric--Hulek, arXiv:2302.01679v2, Lemma
3.6, printed p. 22), so their number is
`k = [rho(H_P) : rho(H_P) cap rho(H_l)]` and the row has `E = 189720 k`.  One
probe computes the intersection: `rho(H_P)` from the plane's 113 certified
parabolic generators, `rho(H_l)` from the image of
`exact_isotropic_stabilizer_generators` at the flag's line, which is exact by
construction.

| quantity | value |
| --- | ---: |
| `|Q| = |im rho|` | 46998591897600 |
| `|rho(H_P)|` | 247726080 (index 189720) |
| `|rho(H_l)|` | 89181388800 (index 527) |
| `|rho(H_P) cap rho(H_l)|` | **82575360** |
| `k`, line cusps at one plane cusp | **3** |
| `m`, plane cusps through one line cusp | **1080** |
| `E = 189720 k = 527 m = |Q| / |D|` | **569160** |

The intersection itself took 0.00 s of GAP's time; the 145.6 s of the probe is
the plane row and the line's stabilizer family.  `k = 3` is the number the
ten-plane probe measured last round, so the two routes agree: the count is one
index and no plane needs to be enumerated for it.

## What this round lands in the library

* `tits_building_incidence` computes one plane's covering and transports it to
  every other plane cusp whose registered lift is known, whenever the subgroup
  is the kernel of the character the row was split by: conjugation by an
  ambient isometry preserves a kernel, so the transported family is exactly
  the covering at the target, and the plane's parabolic, its conjugated
  generators, its word section and its double cosets are paid once for the row
  instead of once per plane -- the 8.60 s a plane the last round measured.
  The condition is `rho(Gamma) = 1`: a subgroup that is only the preimage of a
  proper subgroup of the finite image need not have a normal image, and a
  subgroup cut by a sign condition does not survive conjugation either; both
  keep the per-plane route.  The first attempt was gated on the discriminant
  condition alone and the `Gamma_{Co,2}` row failed on it -- the row of the
  group whose image is *not* trivial -- which is the gate doing its work; the
  condition was then narrowed to the kernel.
* A line vertex whose divided class key is carried by exactly one cusp is that
  cusp, and the certificate's transporter is read off the row's own words
  where the two chains share a root, so no stabilizer word section is built;
  the exact question remains for a shared key and for chains of different
  roots.

## Contract runs

`tests/lattices/test_the_incidence_line_vertex_is_the_cusp_of_its_line.sage`
is new and asserts the statement the key route owes, on `U + U(2) + <-2>`,
whose kernel rows are four edges over three line and two plane cusps -- the
counts of the dispatched run 43866925504: each edge's line lies in exactly one
cusp of the row, and it is the cusp the edge names, and likewise for the
plane.  An edge whose vertex another cusp carries fails it.  Because the
repair changes no answer, the file is not red at its parent: it passes there
(31.78 s, the call 31.45 s) and here (33.94 s), which is what "the same 4
edges" means.  `test_the_kernel_incidence_rows.sage` (6JRS and
`U + U + <-4>`) passes at the parent and here, and the two files together are
3 passed in 79.30 s at this head.

One gate file could not be run to completion: the `Gamma_{Co,2}` row of
`test_the_coble_incidence_of_line_and_plane_orbits.sage` takes 1685 s on
`T_Co` (the #391 round's measurement on main) and was cut at 540 s, the
longest command this round may run.  It is the first item of the next
dispatch.  What protects that row in the meantime is that the transported
covering is gated on `rho(Gamma) = 1` and its image is not trivial, so its
covering is the per-plane one it always was.
