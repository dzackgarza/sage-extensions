# The walk's 350-400 KB a plane is one constructed subobject per plane, and the library never releases it

The incidence walk's per-plane work retains 350-400 KB a plane, flat in the plane
count (`results/issue381-kernel-row-runner-kill.md`, section 4), which at 189720
planes is 63-72 GiB.  The candidate that record named was
`isotropic_class_orbit` (`orthogonal_quotients.py`), a `@cached_method` keyed by a
per-line GAP set.  This note measures what actually retains the memory, and what
repairing it costs.  Measurements are on the adopted runtime at `main`
`901d11b2f` unless a line says otherwise; the probes, their launcher and their
logs are in `.tmp/issue585/`.

## 1. The quotient is not the retainer, and the record's candidate is bounded

`probe-585-instrument.py` runs the carry slice with `tracemalloc` and prints every
container the quotient holds at each sample:

| sample | the quotient's containers | its `_isotropic_lift_registry` | its `_cache__isotropic_class_orbit` | traced |
| --- | ---: | ---: | ---: | ---: |
| after the covering | 677.5 KiB | 660.4 KiB, 1000 entries | absent | 0.0 MiB |
| plane 10 | 687.2 KiB | 660.4 KiB, 1000 | 3.6 KiB, 8 entries | 2.9 MiB |
| plane 100 | 717.2 KiB | 660.4 KiB, 1000 | 40.4 KiB, 85 entries | 28.7 MiB |
| plane 1000 | 808.6 KiB | 660.4 KiB, 1000 | 104 KiB, 198 entries | 295.4 MiB |

The quotient's own retention is **0.13 KiB a plane** -- 131 KiB over 999 planes,
with the 1000 registered lifts flat from the start.  The record's candidate
saturates: one entry per distinct divided-class pair, 85 at plane 100 and 198 at
plane 1000, bounded by `A_{T_Co}` (at most 1024 class pairs) and at 0.5 KiB an
entry.  It is a correct cache of a bounded quantity and is not the retainer.

## 2. The retention is the construction: one subobject per line and per plane

The same slice attributes its growth to the phases of a plane (residential set,
`tracemalloc` on):

| planes | carry | keys | release | traced |
| --- | ---: | ---: | ---: | ---: |
| 10 | 1.2 MiB | 1.2 MiB | 0.0 MiB | 2.9 MiB |
| 100 | 49.6 MiB | 16.1 MiB | 0.2 MiB | 28.7 MiB |
| 1000 | 542.3 MiB | 135.7 MiB | 2.5 MiB | 295.4 MiB |

80% of it is the carry, which builds the plane's carried flags: three
`IsotropicFlag`s whose terms are built by
`Lattices.ParentMethods.primitive_isotropic_subobject`.  `probe-585-where.py`
reads that constructor's own registry over the same 1000 planes:

| sample | entries | shallow size | traced | rss |
| --- | ---: | ---: | ---: | ---: |
| start (1000 registered planes) | 1005 | 326.6 KiB | 0.0 MiB | 1385.7 MiB |
| plane 100 | 1390 (+385) | 473.9 KiB (+147.3) | 27.9 MiB | 1463.4 MiB |
| plane 500 | 2828 (+1823) | 961.6 KiB (+635.0) | 133.7 MiB | 1726.8 MiB |
| plane 1000 | 4552 (+3547) | 1459.9 KiB (+1133.3) | 262.4 MiB | 2050.4 MiB |

**3.55 entries a plane** -- the three carried lines and their shared plane -- at
269 KB of traced objects a plane, and the shallow size is only 1.13 KiB of it:
the memory is inside each constructed subobject.  The plane-100-to-plane-1000
traceback comparison names no single allocation; the growth is the construction
of a parent's category machinery, spread over `sage/categories/homset.py:694`
(+35.3 MiB), `mor_categories.py:969` (+30.2), `owned_category.py:1774` (+21.0)
and `:1697` (+15.9), `mor_categories.py:2376` (+10.6), `ring_foundation.py:6746`
(+10.2), `mor_categories.py:511` (+9.5), `:2260` (+7.1),
`finite_ordered_sets.py:586` (+4.9), `lattices.py:6890` (+4.3) and
`refine.py:377` (+3.5).

## 3. The structure that holds them is the library's construction registry, and it holds them for the process

A subobject is not registered in one cache that a caller could release.  It is
the value of a tower of `@cached_function` registries keyed by `id(...)`:

| registry | key | what it holds |
| --- | --- | --- |
| `_lattice_on_gram` (`categories/_lattice.py:522`) | `id(category), id(module), gram, names, ...` | the lattice |
| `_lattice_subobject_spanning` (`lattices.py:416`) | `id(module), basis, root_system_type_name` | the span subobject |
| `_lattice_mor`, `_lattice_embedding_mor`, `_lattice_isometry_mor` (`lattice_morphisms.py:6055-6077`) | `id(domain), id(codomain)` | the morphism set, whose object names both endpoints |
| `_category_packet` (`mor_categories.py:2117`) | `id(category)` | the Mor/End/Aut packet, which names the category |
| `_MorCategoryOf.__classcall__` (`mor_categories.py:2160`) | `cls, id(base_category)` | the fixed Mor family |

## 4. The measurement that decides it: a constructed Parent of this library is not released

Four specimens, each built and dropped by its only caller, `gc.collect()` after
(`probe-585-parentlife.py`):

| specimen | alive after the drop |
| --- | --- |
| `Lattices(ZZ)([[2]])`, a lattice nothing else names | **yes** |
| `Lattices(ZZ)("U")`, a second one | **yes** |
| `holder.basis_vector(0)`, an element | no |
| `holder.primitive_isotropic_subobject(v, w)`, a plane | **yes** |
| `holder.primitive_isotropic_subobject(v)`, a line | **yes** |
| `holder.primitive_isotropic_subobject()`, the zero subobject | **yes** |

The zero subobject has no basis and no relation to any other object, and nothing
in the probe names it; it survives.  `probe-585-latticeholder.py` follows a
dropped rank-one lattice to its holder and finds exactly one strong root,
`_lattice_on_gram`, whose own docstring states the contract: "two constructions
naming one module and one Gram presentation name one lattice ... this is Sage's
own construction cache".  `probe-585-zeroholders.py` does the same for the zero
subobject and finds its morphism sets and category packets, i.e. the same shape
one level up.

So the walk's 350-400 KB a plane is not a cache of something a caller reads and
could drop: it is four constructed parents a plane, and this library keeps every
constructed parent it has ever made.  A row of 189720 planes constructs 758880 of
them.

## 5. What the registry repair buys: nothing measurable, and why

Five of the registries in section 3 were made to hold their values weakly -- the
span registry, the three lattice morphism registries and the category packet --
and the record's own carry probe was run at 1000 planes on each tree:

| tree | wall | peak tree RSS | RSS a plane, planes 100 to 1000 | carry | keys |
| --- | ---: | ---: | ---: | ---: | ---: |
| pristine `901d11b2f` | 233.0 s | 1761 MiB | 371 KB | 14.71 ms | 16.05 ms |
| five registries weak | 231.3 s | 1675 MiB | 384 KB | 15.84 ms | 15.16 ms |

The two runs' peaks differ by their baselines, not by their slope: the split's
first lift ended at 1325 MiB in the first and 1224 MiB in the second, which is
the allocator's run-to-run variation on this VM, and the coefficient is the
comparable number.  It moves from 371 to 384 KB a plane -- neither way, inside
the 350-400 KB the record's own three slices span.  The wall time is unchanged
(233.0 s against 231.3 s) because the entries were never read twice: each
carried flag's spans are new, so the registry answered no lookup either way.

The repair makes those five registries weak holders and moves nothing, because
they were never the only holder: the parent is still named by the packet family,
the Mor-family cache and its own inclusion, and section 4 says a constructed
parent is held whatever these five do.  A weak entry whose value is alive is
still an entry, so neither the registry's size nor the process's memory changes.
That is the trade the issue asked to have stated rather than made silently, and
it is why the repair is measured here and not landed.

## 6. What the row costs at 189720 planes

| what | coefficient | at 189720 planes |
| --- | ---: | ---: |
| the walk's per-plane work (this note, section 2; the record's slices agree) | 350-400 KB | 63-72 GiB |
| the plane row's representatives (#584) | 63.0-66 KB | 11.4-12.0 GiB |
| the relation the call returns, at one certificate a plane (#584: 59,012 B a certificate) | 59 KB | 10.4 GiB |

The fixed cost of the call is 1.25-1.4 GiB (the split's first lift at +0.85 GiB
and the interpreter's baseline), and the plane row's own 11.4-12.0 GiB replaces
the 1000 registered planes of that baseline at 189720.  So the row's peak is the
three terms together: **63-72 GiB for the walk, 11.4-12.0 GiB for the plane row's
representatives, 10.4 GiB for the relation -- about 85-95 GiB against a 16 GiB
runner**.  That answers #381: the kernel rows do not run at 189720 planes, and
the walk's own retention is the largest single term.

## 7. What a repair would have to change

The retention cannot be bounded by repairing a cache, because the object it
retains is not a cache entry: it is a *construction*, and this library's
constructions are permanent by design.  `_lattice_on_gram`'s docstring says it
-- "two constructions naming one module and one Gram presentation name one
lattice ... this is Sage's own construction cache" -- and the same shape is in
the span registry, the three lattice morphism registries and the category
packets.  Making those hold weakly instead, which is the repair the issue allows
("returned to the caller and dropped by it"), moves the entries and not the
memory: the parents stay, because something else in the same tower still names
them (section 3), and the library's identity contract says a datum is one object
for the process.

Two repairs remain, and both are their own unit:

* **Bound the identity contract.**  Every registry above, and `_lattice_on_gram`
  itself, would have to hold its value while some caller holds it -- the
  lifetime semantics `_interned_points` already gives the naturals and
  `_OWNED_RINGS` gives owned rings.  That is a change to what "one object per
  datum" means library-wide, with the identity assertions of the whole tree to
  re-establish.
* **Stop constructing a parent per plane.**  The incidence's certificate is a
  relation between two cusp vertices; the flag it holds names those vertices and
  retains, beside them, a transporter (6,496 B, an element, and elements *are*
  released).  A certificate that kept the two vertices and the transporter, and
  rebuilt the flag's terms on demand, would leave the walk with no parent to
  construct per plane.  Measured against this note's numbers that is the
  repair that makes the row fit: at 6,496 B a certificate, three a plane, the
  relation is 3.4 GiB and the walk's own retention nothing.
