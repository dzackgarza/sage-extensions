# #286, batch 1: the rank-2 branch and card `029J`'s `O` row

Branch at `8b1ec17`.  Nothing on T_Co is run in this batch.

## What is implemented

`categories/isotropic_orbits.py`: `_isotropic_orbit_representatives` now reads
primitive isotropic planes from the *lines* of the reduction instead of asking the
port to enumerate plane classes directly, which is Scattone's method (Mem. AMS 374,
Prop. 5.4.7 with Cor. 5.4.8(2), p. 78, as `tests/fixtures/DATA_SOURCES.md:172`
summarises it):

- `_hyperbolic_completion(lattice, line)` returns `(v, <v, f>)` when the line's
  generator `v` splits off a hyperbolic plane at index one, decided by
  `det(L) = det(<v, f>) det(<v, f>^perp)`.  With that split,
  `v^perp = <v> + <v, f>^perp`, so `K_v = v^perp/Zv` *is* the complement, every
  isometry of it extends to `L` fixing `v`, and `Stab_{O(L)}(v)` acts on `K_v`
  through all of `O(K_v)`.  That is what makes one representative per `O(K_v)`-orbit
  of isotropic vectors one representative per `Stab(v)`-orbit of planes through `v`.
- `_planes_through_line` lifts each isotropic class of `K_v` back through the
  reduction's frame and returns `<v, lift>` in the lattice itself.
- `_isotropic_plane_orbit_representatives` collects those over the line
  representatives and then *identifies* the pairs `(v, line of K_v)`: one plane is
  reached from every line orbit meeting it, so two candidates are one class exactly
  when an isometry of `L` carries one plane onto the other (exact plane
  equivalence, not a count and not an invariant comparison).
- A lattice whose line representatives do not satisfy the split keeps the port's
  marking-class route; the branch never returns a partial family.

## Measured, `029J` row `O` (`constant: 2`, `planes: 2`)

`NamedLattices.TEn.Aut()`:

```
rank-1 orbits: 2 in 41.1 s                     (matches the card's `constant: 2`)
K_v for line 0: rank 10, signature (1,9), det -1024, 1 O(K)-class in 2.3 s
K_v for line 1: rank 10, signature (1,9), det  -256, 2 O(K)-classes in 4.7 s
split checks:   line 0 v = -e_e,  f = e_f,  b = -1, det <v,f> = -1,
                complement det -1024, det T_En 1024
                line 1 v = e_fp, f = e_ep, b =  2, det <v,f> = -4,
                complement det -256,  det T_En 1024
candidates:     3 (1 + 2), one merge by exact plane isometry (16.6 s)
planes:         2 in 62.8 s, whole call from a cold process
```

The two representatives are `Z e_f + Z(e_ep + 2 e_fp + w_1)` and
`Z(2 e_e + 2 e_f + w_2) + Z e_ep`; the second is the card's
`P_2 = Z(2 e_1 + 2 e_2 + w) + Z e_3` with `w` of norm 4 in `E_8`.

Test: `tests/lattices/test_unpolarized_enriques_strata.sage`, which reads the row
by its tag and asserts `2` and `2`, and checks every returned object is a primitive
isotropic line, respectively a primitive isotropic rank-two plane.  Under
`--no-time-gates`: **2 passed in 202.55 s**, exit 0; the two calls were 116.95 s
and 84.37 s on a machine at load 10.6, against 41 s and 22 s measured alone.

## Corrected: the Enriques plane count under `O(N)` is 2, not 9

`tests/lattices/test_orbit_milestones.sage` asserted nine primitive isotropic planes
modulo `O(N)`, citing Sterk without a proposition.  Card `029J`'s `O` row states two
(Sterk, Props 4.5 p. 28 and 4.6 p. 29) and the call above returns two, with the third
candidate carried onto the first by an explicit isometry.  Nine is that card's
`gamma-en-2` row, i.e. the count modulo a smaller arithmetic group.  The test now
asserts two and names the row.

## Cost: the plane call is over the repository's per-call gate

62.8 s from a cold process, of which 41.1 s is the *line* classification the call
starts from (pre-existing), ~7 s the two reductions, 16.6 s the one exact plane
isometry.

On a quiet host with the repository's `addopts` intact (`time gates on … each test call
ceiling 20 s`, `--timeout=60`):

```
tests/lattices/test_unpolarized_enriques_strata.sage::test_the_o_row_states_two_primitive_isotropic_lines: 41.80 s > 20 s
tests/lattices/test_unpolarized_enriques_strata.sage::test_the_o_row_states_two_primitive_isotropic_planes: 23.02 s > 20 s
========================= 2 passed in 65.22s (0:01:05) =========================
```

Both comparisons pass inside the 60 s hang bound and the session exits red on the 20 s
per-call ceiling: 41.8 s is the pre-existing line classification, 23.0 s is this call.
That is a cost finding for #306, not a disagreement with the card.

## Not delivered, with what blocks each

1. **`6JRX` / `6JRY` planes (4, 9)** — the reduction of the single line class of
   `Lambda_2 = U^2 + E8(-1)^2 + <-2>` is `U + E8(-1)^2 + <-2>`, rank 19, signature
   `(1,18)`, so the next step is the O-classification of the isotropic vectors of a
   rank-19 Lorentzian lattice.  `INDUCTION.isotropic_vector_classes` did not return on it
   within the probe's 2400 s inner cap (`launcher exit: 124`, peak tree RSS 1086 MiB);
   `tests/lattices/test_scattone_plane_orbits.sage` is unchanged and still does not
   return.
2. **`029J` rows `gamma-en-2` and `Otilde+`** — both are subgroup rows, so the
   full-group plane representatives have to be split by double cosets, which needs
   generators of `Stab_{O(L)}(P)` for a *plane*.  The port's
   `automorphism_group_generators` on a marked plane of `T_En` did not return in
   7 min on this host.  `Otilde+` additionally needs 24 242 plane representatives
   realised one by one.  `gamma-en-2` finally needs an in-repository construction of
   `Gamma_En,2 = Gamma_En cap Gamma_dP`; none is pinned, and guessing one would be a
   substituted object rather than the card's group.

## Regression runs on the same tree (`--no-time-gates`, exit 0)

```
tests/lattices/test_unpolarized_enriques_strata.sage     2 passed in 202.55 s
tests/lattices/test_orbit_milestones.sage                2 passed in 246.54 s
tests/lattices/test_special_orthogonal_split_building.sage  1 passed in  33.31 s
tests/lattices/test_stable_isotropic_plane_orbits.sage   3 passed in  50.57 s
```

The last two are the ones the branch could have moved and did not: `SO(2U)` still splits
its single `O`-plane class into the two `SO`-plane classes of the quotient building, and
`L_1 = U + U + <-2>` keeps its `Otilde` and `Otilde+` plane fibres.  Those four runs share a
host at load 10.6, so their wall times are contention-inflated; the same two card modules
together run in **90.36 s** (4 passed) on a quiet host, where the plane call alone is
13.95 s once the line classes are warm.
