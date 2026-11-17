# The kernel plane rows' 12.29 GiB is one constructed representative a plane

The building incidence of `Otilde(T_Co)` now runs on the divided-class route
(`tests/coble_gamma_co_2_incidence_rows.py --route auto`), whose walk costs
1 427 B and 1.65 ms a plane.  What is left of the row is the plane vertex row it
reads: `cusps(2)` returns 189 720 cusps, and the cusp *is* a primitive isotropic
plane of `T_Co`, so the row holds 189 720 of them.

## What it costs, measured

On `T_Co = ⟨2⟩ ⊕ U(2) ⊕ E8(−2)` with `Otilde(T_Co) = ker rho`, the row built as
`_plane_orbit_from_parabolic_stabilizer` builds it — one draw from the split
iterator, one `transport_isotropic_object`, one span key, one
`register_isotropic_lift`, one `_arithmetic_cusp` — at 200 planes
(`.scratch/381/probe-plane-row.log`, tree `5f6abb8`, `PYTHONHASHSEED=0`):

| per plane | bytes | time |
| --- | ---: | ---: |
| the plane row (`cusps(2)`) | 69 570 | 5.98 ms |
| at 189 720 planes | **12.29 GiB** | **1 179 s** |

That is the whole of the divided-class route's remaining memory: the walk is
0.25 GiB and the relation 0.07 GiB beside it, and the split's coset tables are
0.85 GiB once.

## Where the bytes sit

`sage_extensions#584` attributed the same coefficient: 32.1 KB is the returned
representative subobject — "it *is* the cusp" — 7.5 KB the registry entry
`register_isotropic_lift` writes, about 23 KB the allocator's pages beyond the
live objects.  And a constructed subobject of this library is not released:
`sage_extensions#585` §3–§4 found every constructed parent still alive after
its only caller dropped it, held by `_lattice_subobject_spanning`,
`_lattice_mor`, the category packet and `_lattice_on_gram`, and making five of
those registries weak moved the coefficient from 371 to 384 KB a plane, i.e.
not at all.

## What would replace it

A vertex that keeps the plane's **span** — two rows of eleven integers, about
0.4 KB — and the finite element its registered lift already carries, and builds
the representative subobject only when a reader asks for it.  The row's readers
are the incidence's walk (spans and finite elements only) and the driver's
contract (a representative, for each cusp it names).

That is a saving of about 11.5 GiB only if the on-demand build does not re-retain
what it builds, and after `sage_extensions#585` §5 that is the question this
issue is: the retention is not one cache a caller could release but the value of
a tower of `@cached_function` registries keyed by `id(...)`, and five of them
made weak moved nothing.  So the replacement needs an owner change in the
subobject representation itself — a subobject that is not a `Parent`, or a
registry that holds its values weakly all the way down — and not a lazy property
on the cusp.

## Acceptance

* `cusps(2)` of `Otilde(T_Co)` and of `Otilde+(T_Co)` still returns 189 720
  cusps, each answering `representative()` with a primitive totally isotropic
  plane of `T_Co`;
* the incidence rows' relations are unchanged — the class route's edges are
  pairs of cusp positions, and a vertex's identity must not become the span in a
  way that merges two cusps the finite image separates;
* the plane row's peak falls from 12.29 GiB to the span row's, so the whole
  incidence row stands under 2.5 GiB and fits a 4 GiB runner instead of a 16 GiB
  one.

No lattice-database card holds a `T_Co` value (lattice-database#7), so no count
is asserted here: 189 720 is `sage_extensions#390`'s returned row, and the
coefficient is the measurement above.
