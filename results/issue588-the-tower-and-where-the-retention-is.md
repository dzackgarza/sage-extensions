# The plane row's 12.29 GiB is one identity record, and both owner changes are migrations

`cusps(2)` of `Otilde(T_Co)` costs 12.29 GiB because the row holds one
constructed parent a plane.  This note names every registry in the retention
path of one plane, measures which of them is the retainer, and measures the two
owner changes the issue names.  Both turn out to be larger than the issue:
one is 140 call sites, the other 176 registries over an identity contract that a
consumer of this tree reads.  Measurements are on the adopted runtime at
`main` `6b8f2822`, probes and logs in `.tmp/issue588/`.

## 1. The tower, as the process holds it

`sage_extensions#585` §3 listed five `@cached_function` registries keyed by
`id(...)` and made them weak; the coefficient moved 371 to 384 KB a plane.
A scan of the whole process -- every `CachedFunction`, every `_cache__*` store on
an owned object, and every attribute dict of an owned category -- enumerates what
actually holds one plane of `T_Co` after its only caller drops it
(`probe-588-registries.py`):

| registry | key | value is a parent | holds a dropped plane |
| --- | --- | --- | --- |
| `Lattices.ParentMethods.primitive_isotropic_subobject` (`lattices.py:9462`, a `@cached_method`) | the spanning family, **by value** | yes | yes |
| `_lattice_subobject_spanning` (`lattices.py:408`) | `id(module), basis, None` | yes | yes |
| `_lattice_embedding_mor` (`lattice_morphisms.py:6105`) | `id(domain), id(codomain)` | no (a homset) | yes, through the arrow |
| `_lattice_mor`, `_lattice_isometry_mor` (`:6097`, `:6113`) | same | no | yes |
| `_lattice_on_gram` (`_lattice.py:512`) | `id(category), id(module), gram, names, ...` | yes | not for a subobject; for a lattice it is the only one |
| `_category_packet` (`mor_categories.py:2118`) | `id(category)` | no | no |
| `_MorCategoryOf._objects` (`mor_categories.py:2181`, ~20 stores, one per category level a plane lives in) | `id(domain), id(codomain)` | no (a Mor, which names both) | **yes** |

Two of the entries in `sage_extensions#585`'s five are not in this list at all:
the `@cached_method` on the ambient lattice, which is keyed by the span *by
value* and so cannot be released by keying anything weakly, and the Mor-family
identity record, which is not a `@cached_function` but a plain dict on a
category object.  Neither of them was weakened in that experiment.

## 2. The sixth: the Mor family's identity record, and a 16-value hedge

Two separate reasons the five-weak repair could not move anything, both
measured:

* `weak_cached_function` defaults to `cache=16`: the sixteen most recently
  computed values are held **strongly** (`sage/misc/weak_dict.pyx:1074`,
  `CachedWeakValueDictionary`).  A "weak" registry therefore still pins sixteen
  parents at every one of the five sites, and a one-object probe reports the
  object alive whether or not the registry is weak.  `cache=0` is what "weak all
  the way down" means here.
* the two registries above are the actual retainers.

The decisive experiment is a drop test on `U + U(2) + <-2>`'s parent construction
and on one plane of `T_Co`, with each change applied separately
(`probe-588-cycle.py`, `probe-588-repro.py`):

| state of the tree | rank-one lattice released | `U` released | plane of `T_Co` released |
| --- | --- | --- | --- |
| `main` `6b8f2822` | no | no | no |
| the five `@cached_function`s weak at `cache=0`, `_objects` strong | yes | yes | **no** |
| also `_MorCategoryOf._objects` weak | yes | yes | **yes** |

So the retention of a dropped plane is exactly the Mor-family identity record.
Everything else in the tower can be released, and then a plane, its inclusion,
a rank-one lattice and `U` are all collected after the drop -- 20 of 20 planes
dropped with 0 surviving, against 20 of 20 surviving at `main`.

## 3. What weakening that record does

With `_MorCategoryOf._objects` weak, the port's generator computation on
`U + U(2) + <-2>` fails in four seconds, deterministically
(`probe-588-repro.py`):

```
ValueError: the value map Generic endomorphism of Integer Ring must end at the
value module Free module on {[0]} over Fraction Field of Integer Ring of Lattice
of rank 5 and signature (2, 3), but ends at Integer Ring
    form_modules.py:443  FormedModuleMorphism.__init__
    form_modules.py:552  FormedModuleMorphism.base_change
    form_modules.py:962  FormModules._element_constructor_
    recursive.py:1603    pointed_isometry
```

The check is an identity comparison, `value_morphism.codomain() is not
target_values`, and the two value modules were one object before the record was
weakened.  The record is what makes `Mor(A, B)` one object for the process; a
consumer of this tree reads that identity, and the formed-module constructor
states it.  Nothing about the row's memory is at stake in that check, which is
exactly why it is the deciding measurement: the identity contract is not a cache
whose reach the row's need can bound.

## 4. The two candidates, counted

* **(A) a subobject that is not a `Parent`.**  `primitive_isotropic_subobject(`
  has **140 call sites in 64 files** under `src/`, `tests/` and `docs/`, and
  `subobject_on(` has 74 under `src/`.  Every one of them receives a parent
  today.  This is the migration the issue's own last paragraph describes.
* **(B) a registry chain weak all the way down.**  `src/` holds **1781** cache
  decorators, of which **176** are keyed by `id(...)`
  (`probe-588-cache-decorators.py`).  An id-keyed registry is sound only while
  the object at that address cannot die, because the registry does not retain
  its key; the moment one of them is made weak the others become machines for
  returning another object's answer, which is the shape of the `form_modules`
  failure above rather than a hypothesis.  Alongside them,
  `_MorCategoryOf._objects` is written by `_remember_between` (**15** call sites)
  and read by `_cached_between` and `_MorCategoryOf.__contains__`, whose stated
  contract is that membership reads the record.

So (B) is 176 registries and an identity contract, not six functions, and (A) is
140 call sites.  **Neither belongs to one issue.**  The finding is that this is
a migration, and it is recorded here rather than started.

## 5. What the change that is available does measure

A cusp named by its span -- the issue's own "a vertex that keeps the plane's
span" -- is exact and answer-preserving, measured on the tree that carries it
(`probe-588-life.py`):

| statement | `main` `6b8f2822` | cusp by span |
| --- | --- | --- |
| `cusp.span()` is `_span_key(representative)` | no `span()` | yes |
| the rebuilt representative is the same subobject | -- | yes |
| it is primitive and totally isotropic, rank 2 | -- | yes |
| `U+U(2)+<-2>` line cusps / plane cusps | 3 / 2 | 3 / 2 |
| their spans | `((0,1,0,0,0),(0,0,0,1,0))`, `((0,1,0,0,0),(0,0,1,0,0))` ... | identical |
| incidence certificates and their endpoints | 4 | 4, identical |
| a plane named by a cusp and dropped | 20 of 20 survive | 20 of 20 survive |

The last row is the reason the change is not landed on its own: with the
identity record still strong, a cusp that keeps a span releases nothing, and the
row keeps its 12.29 GiB.  Landing it now would be a change that cannot have a
red test and does not move the number the issue is about.

The row's cost on this runtime, for the record (`probe-588-row.py`,
`PROBE_SHAPE=representatives`, 200 planes, `PYTHONHASHSEED=0`): **66 730 B and
7.25 ms a plane**, 11.79 GiB and 1376 s at 189720 planes, per band 67.5 to
71.1 KB -- `sage_extensions#381`'s 69 570 B and 12.29 GiB reproduced inside its
own band at this base commit.

## 6. What a repair has to do, named

1. **Settle the identity contract of ints, not of caches.**  176 id-keyed
   registries either hold their key objects or are re-keyed on the objects; the
   Mor-family record either keeps its Mor or `__contains__` stops being an
   identity question.  Until one of those holds, no registry may be made weak,
   because its neighbours are not.
2. **Keep the plane out of the row.**  The row builds a plane per cusp because
   `isotropic_orbit_representatives` returns subobjects and `cusps` maps them.
   The cusp now costs a span; the row must be able to yield an item whose span
   is computable without the parent -- a `TransportedIsotropicObject` spanning
   its transport applied to the source plane's coordinates, with one
   `_span_of_vectors` at the owner that `_span_key` delegates to.  That is this
   issue's own continuation, and it needs (1) to matter for memory at all.

## Provenance

`main` `6b8f2822`.  Probes, launcher and logs: `.tmp/issue588/`.  The partial
repair measured in sections 3 and 5 -- the weak registries at `cache=0`, the
weak resolution record, the span-named cusp, the yielded orbit row -- is kept as
a patch at `.tmp/issue588/partial-repair.patch` and is **not** landed.
