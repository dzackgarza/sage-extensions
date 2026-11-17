# A subobject's identity is its span; a Mor's is its endpoints', while they live

This note scopes the identity contract under which a constructed subobject is
named, records the measurement that chooses between the two candidate repairs,
and reports one converted chain -- the plane representative's path -- measured at
10, 100 and 200 planes.  All measurements are on the adopted runtime
(`ghcr.io/dzackgarza/sage@sha256:59568577...`, Sage 11.0.beta5 / Python 3.14,
`/sage/.venv/bin/python`), `PYTHONHASHSEED=0`, probes and logs in
`.tmp/subobject-identity/`.

## 1. The contract

Three statements.  The pilot's code states each where the object it is about is
built, and the tests beside it read them.

1. **An object is identified by its placement; a subobject additionally by a
   datum it carries.**  `subobject_on` builds a parent: its module, its Gram, its
   category placement and its inclusion.  A primitive isotropic subobject of a
   lattice carries a *span*: the row Hermite form of its generator coordinates in
   the ambient lattice's basis (`_span_key`).  Two subobjects of one ambient
   lattice span the same sublattice exactly when those forms agree (Cohen, *A
   Course in Computational Algebraic Number Theory*, GTM 138, section 2.4,
   Algorithm 2.4.5: the integer row Hermite form is a normal form for a row
   lattice), so the span is
   the exact name of the sublattice and not an invariant that stands in for it.
   Everything that must name a subobject across the death of the object keys on
   that name: the cusp row, and `register_isotropic_lift`'s registry.
2. **A Mor's identity is its endpoints' identity, and only while they are
   alive.**  `Mor(A,B)` is one object for one live pair of objects.  A rebuilt
   endpoint is a different object, hence a different pair, hence a Mor of its
   own.  No record may promise that a Mor outlives the objects it was built
   between, and no reader may ask for `Mor(P,P)` across the death of `P`
   (`_remember_between`, `_cached_between`).
3. **No registry may answer a question about an address it does not hold.**  A
   memo keyed by `id(...)` names an object only while the object at that address
   is that object.  A registry whose key can die either verifies what it finds or
   does not keep the answer (`_address_registry`).

## 2. The measurement that chooses between the two repairs

The two candidates were: (1) re-key the id-keyed registries on something the
object carries; (2) make `__contains__` not an identity question.  Both were
tried on this chain.

**(1) is wrong at the identity record, measured.**  Two subobjects of one span
are two objects (a cleared construction registry rebuilds the plane from its
span: `probe-reject-588.py`, `[probe] two objects, one span: True, the same
object: False`), each has its own Mor naming its own endpoint (`True, True`), and
a record keyed on the span answers the question about the second with the Mor of
the first: `answered.domain_object() is first` → `True`, `is second` → `False`.
A datum names a sublattice; a Mor names objects, and that is what its consumers
read.  Re-keying the record on the carried datum therefore does not migrate it,
it changes what it answers.

**(2) is unnecessary at `__contains__`, measured.**  With the record holding its
Mor weakly, every containment reading of one category of sets is what it is on
`main` (`probe-containment.py`, both trees, all eight lines identical): `Of`
twice is one object, the end of a point is that Mor, the arrows of the monos are
that Mor, `Mor in MorCategories()`, the family contains its own Mor, a constant
is in `Mor` and in neither `Monos` nor `Epis`, a swap is in both, and the
identity of the swap is idempotent.  A weak entry lives exactly as long as its
subject, so "is this the one" still answers `True` for a live candidate: the
reader needed no change, and changing it would have loosened a decision that is
still exact.

**What actually blocks the release is the record owning its member, and what
breaks when it stops owning is the neighbour.**  Weakening the record alone
reproduces `sage_extensions#588`'s four-second failure, and the failing question
is now named: `_represented_value_module` is keyed by `id(formed_module)` and its
answer -- a module -- outlives its key, so a formed module built at a collected
one's address was answered with the dead one's module:

```
[stale-address] _represented_value_module keyed on id(formed)=124118530048560
  recorded dead->Integer Ring asked ...->Integer Ring
[stale-address] _represented_value_module keyed on id(formed)=124118317640560
  recorded dead->Integer Ring asked ...->Free module on {[0]} over Fraction Field of Integer Ring
TypeError: a lattice morphism ... needs both forms valued in one module, but they
  take values in Free module on {[0]} over ... and Integer Ring
```

(diagnostic run `diag3-588`, `.tmp/subobject-identity/diag3-588.log`.)  The
repair at that owner is the third statement: the registry verifies that the
object at its key's address is the object it recorded, and otherwise asks the
question again.  This is the pilot's chosen shape: **candidate 2's principle --
the record stops owning its members -- applied where it operates, which is the
registry's answer and not its `__contains__`; candidate 1's datum keys used only
where the object really carries a name.**

The recommendation is therefore: convert the remaining 100 address-only
registries the same way, one decorator and one run of that site's consumers
each, and do not re-key the identity record (§6 gives the counts and the cost).

## 3. The chain the pilot converts

The plane representative's path, in the order the row walks it:

* `_plane_orbit_from_parabolic_stabilizer` -- the representatives are yielded,
  not gathered (`_yield_subgroup_isotropic_orbit_representatives`), so a
  representative finished with is dropped before the next is drawn.
* `transport_isotropic_object` -- unchanged: one plane, built from the images of
  the source's basis by the constructor that verifies isotropy and primitivity.
* the span key -- `_span_key` is computed on the transported plane and is what
  the row keeps; the plane itself is not kept.
* `register_isotropic_lift` -- already keyed by the span, so the split's own
  lift, the source parabolic and the discriminant image survive the plane.
* `_arithmetic_cusp` -- a cusp is its subgroup, its representative's span and its
  rank; `cusp.span()` answers without a plane, and `cusp.representative()` builds
  one on demand and retains nothing.
* the record and its neighbours -- `_MorCategoryOf._objects` and
  `_resolved_endpoint_categories` hold their Mor weakly (the second is swept);
  `_represented_value_module` and `_represented_module` are `_address_registry`
  memos; the construction registries on the path (`_lattice_object`,
  `_lattice_subobject_spanning`, `_lattice_on_gram`, `_lattice_mor`,
  `_lattice_embedding_mor`, `_lattice_isometry_mor`) hold their values weakly at
  `cache=0`, and `primitive_isotropic_subobject` builds through one of them.

## 4. The row at 10, 100 and 200 planes

`probe-pilot-row.py`, 200 draws from
`OrthogonalCharacterQuotient._iter_splitting_isometries_in_im_rho` of the
plane's certified parabolic (112 generators), one transport, one span key, one
`register_isotropic_lift` and one cusp wrapper a draw.  `before` is `main`
`8f2f158` in a separate worktree; `after` is the pilot.  The row's wall is the
split's first lift (the finite image's whole coset walk, ~200 s) on both.

| measurement | before (`main`, one plane a cusp) | after (the pilot, one span a cusp) | control (the pilot, one plane a cusp) |
| --- | --- | --- | --- |
| planes 1 -> 10 | 2.7 KiB a plane | 0.4 KiB a plane | 0.4 KiB a plane |
| planes 10 -> 100 | 52.4 KiB a plane | 0.2 KiB a plane | 17.8 KiB a plane |
| planes 100 -> 200 | 70.1 KiB a plane | 1.2 KiB a plane | 62.1 KiB a plane |
| planes of the row alive at 200, beside the source | 199 | **0** | 199 |
| lifts retained | 200 | 200 | 200 |
| rss at 200 planes | 1338.7 MiB | 1376.4 MiB | 1340.1 MiB |
| wall | 199.6 s | 206.7 s | 214.9 s |
| at 189720 planes, from the 100 -> 200 band | 12.69 GiB | **0.22 GiB** | 11.23 GiB |

The control is the same tree with the row keeping a plane a cusp: it reproduces
the old slope, so the release is the span-named cusp and not the weakened record
(nor a faster transport).

The drop test (`probe-588-life.py`, the same probe on both trees): **20 of 20**
planes of `T_Co` alive after being named by a cusp and dropped on `main`,
**0 of 20** on the pilot.

## 5. What is unchanged, and one number that cannot be compared

* `U+U(2)+<-2>`: 3 line cusps, 2 plane cusps, 4 incidence certificates, on both
  trees.  Each certificate's line lies in its plane, and each of its two
  transporters carries its term to its cusp (`test_a_cusp_names_its_plane_by_span.sage`).
* Containment: the eight readings of §2 are identical on both trees.
* `tests/categories`, `tests/modules`, `tests/objects`, `tests/sets`: the
  FAILED and ERROR id sets are **identical** on both trees -- 211 failed, 519
  passed, 299 errors, none of them caused by this change (`sweep-base2` against
  `sweep-pilot`).
* `tests/lattices`, the files that consume this chain: 10 passed, 3 errors on
  both trees; the errors are one pre-existing test-lint finding (`TL10` at
  `test_isotropic_routes_small_examples.sage:29`).  The three new files: 4 passed
  in 17.4 s with the time gates on (9.7 s, 4.7 s, 2.1 s, 0.2 s a test).

**The row's representative choice is not stable across runs.**  Three runs of the
same tree give three different line and plane representative spans
(`probe-588-life.py` on the pilot, three runs: plane cusps `((0,1,0,0,0),(0,0,0,1,0))` and
`((2,0,1,0,0),(0,1,0,-1,0))`, then `((1,1,1,0,-1),(0,8,-1,-2,-2))` and
`((1,1,1,0,-1),(0,6,-2,-1,-2))`), and the ambient generator count of the
five-dimensional example moves between 290 and 312 across runs.  So "the spans are
identical" is a within-run statement: what is comparable across trees is the
orbit *count* and the relation, not the chosen representative.

## 6. What remains, exactly

* **`src/` holds 1779 cache decorators** (1781 on `main`; the pilot replaced two).
  **196** of them take an explicit `key=` (197 on `main`); of those, **100** key
  on addresses and constants only -- naming no object the entry would hold, so
  they answer for an address rather than for an object -- and **95** name an
  object, which their entry then holds (`probe-address-keys.py`).  The pilot
  converted the two that its chain reaches: `_represented_value_module` and
  `_represented_module`.  **100 remain.**
* The coarser count in `.tmp/issue588/` -- 176 registries "keyed by `id(...)`" --
  reads a twelve-line block around each decorator including the body, so it
  counts a `@cached_method` whose *body* mentions `id(` as an address key.  The
  exact population is the 196 above.
* The identity record is **one** class, `_MorCategoryOf`, with **two** dicts.  It
  is written by `_remember_between` at **14** call sites (the earlier count of 15
  counted the definition line) and read by `_cached_between` at **13** sites, of
  which the two `__contains__` readings are unchanged and measured unchanged.
* Cost of the rest: each of the 100 is a decorator swap to `_address_registry`
  plus one run of that site's consumers to show its answer is unchanged -- the
  shape this pilot repeated twice, finding one site from the record's own repro
  and one from the next consumer's failure.  The 14 writers need no code change:
  the statement of what they remember is made once at the owner
  (`_remember_between`), where every writer inherits it.  What must not be done
  is re-keying a registry whose value names its key's identity onto a datum that
  datum does not determine: measured at the record in §2.

## 7. What was run

Every command ran in the pinned image through the launcher that binds the tree
and the port (`launch.sh`, `run-tests.sh`), on `main` `8f2f158` in a separate
worktree (`git worktree add .scratch/588base omm/main`, its `.git` bound so the
stage recorder resolves the commit) and on the pilot tree.

| what | command | result |
| --- | --- | --- |
| the red test, before the repair | `pytest tests/lattices/test_a_dropped_plane_is_collected.sage` on the worktree | 1 failed in 1.44 s |
| the three new files, after | same, three files, time gates on | 4 passed in 17.4 s |
| the consumed lattice files | `test_a_transported_line_keeps_the_word_that_placed_it`, `test_a_row_computes_one_plane_covering`, `test_a_plane_transport_builds_one_span`, `test_the_stable_plane_rows_equal_their_double_coset_counts`, `test_isotropic_routes_small_examples` | 10 passed, 3 errors, both trees |
| four directories | `pytest tests/categories tests/modules tests/objects tests/sets` | identical id sets, both trees |
| the row | `probe-pilot-row.py`, 200 planes, three trees | §4 |
| the drop test | `probe-588-life.py`, both trees | 20 of 20 / 0 of 20 |
| containment | `probe-containment.py`, both trees | identical, §2 |
| the rejected alternative | `probe-reject-588.py` | §2 |
| the neighbour defect | `diag3-588` | §2 |

## Provenance

`main` `8f2f158`; the red release test is `f4aa805`, the repair `f364ef7`, this
note the commit that carries it.  Probes, launchers and logs:
`.tmp/subobject-identity/`; the #588 probes it reuses
(`probe-588-life.py`, `probe-588-repro.py`) are in `.tmp/issue588/`.
