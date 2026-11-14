# #333: `TEn.O().discriminant_image()` — the two calls, and why one appears to stop

**Result: the call returns.** `NamedLattices.TEn.O().discriminant_image()` is
`NamedLattices.TEn.Aut().discriminant_image()`: one parent object, one cached generating
family, and an image of order `46 998 591 897 600` in `O(A_{T_En})`, which is all of
`O(A_{T_En})` — `rho` is onto here, decided by computation.

Measured on `a9ed52bc288d197d760a2d7ff726a35fe8ee5643` (`main`, before this unit's
commit), on the adopted runtime: Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1, with the
indefinite port project bound at `/work` (its own copy, `/work/src` ahead of the
provider's on `PYTHONPATH`).

| stage | measured |
| --- | ---: |
| `TEn.O() is TEn.Aut()` | `True` |
| `O(T_En).group_generators()` (cold) | 198 generators, 76.2 s |
| same read again in the same process | 0.00 s, the same object |
| `O().discriminant_image()` (cold) | order 46 998 591 897 600, 19.2 s |
| `Aut().discriminant_image()` (same process) | same order, 0.06 s, a *new* subgroup object |
| `O(A_{T_En}).cardinality()` | 46 998 591 897 600, 0.00 s |
| `discriminant_representation_is_surjective()` | `True`, 0.06 s |

`A_{T_En}` has 1024 classes; `O(T_En)` itself is infinite and is never enumerated.

## Where the two calls differ

There is no second code path. The differences are the parent, the cached method and the
generator source:

1. **The parent is one object.** `O` is an alias of `orthogonal_group`, which returns
   `self.Aut()`; `Aut()` is `self.Isom(self)`; `_lattice_isometry_mor` is a
   `cached_function` keyed on `(id(domain), id(codomain))`, so both spellings return the
   same `LatticeIsometryMor`. Measured: `L.O() is L.Aut()` → `True`, with equal `id`.
2. **The cached method is `group_generators`.** It is cached per isometry Mor object, so
   the first read in a process runs the indefinite-lattice computation (the port's
   `automorphism_group_generators`, 76 s for 198 generators) and every later read is
   `0.00 s`. A process that has already read the family — that is what the #325 and #331
   work on the T_En plane rows does — answers `discriminant_image()` in 0.2 s. A process
   that has not, and that caps the call, reports a stop inside `group_generators`. The
   reported stop and the reported 0.2 s are the two states of this one cache.
3. **The generator source is the port.** On an indefinite lattice,
   `LatticeIsometryMor._computed_group_generators` takes its generators from
   `sage_indefinite_port.indefinite.marked_lattices.automorphism_group_generators`, so
   the cold cost is that computation's.
4. **Only that one thing is cached.** The Mor's `discriminant_image` has no cache
   decorator (`Lattices.ParentMethods.discriminant_image`, the lattice method, is the
   cached one): the second call rebuilds a subgroup object of the same order but is not
   the same object, so a test must compare orders and generating families, not identity.

The other way this call fails in this environment is not a computation: with the port
imported from the runtime image's own baked copy instead of the port project at `/work`,
`group_generators` raises

```
File "/repos/sage-indefinite-port/src/sage_indefinite_port/indefinite/recursive.py", line 154, in _isometry_from_row_matrix
    source_coordinates = tuple(int(coordinates(label)) for label in source_labels)
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'OwnedJoinCategory.element_class'
```

which is the setup error this repository's indefinite-lattice runs already record, not a
mathematical finding. Both measurements above are with the port at `/work`.

## What was added

`tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage`, one test,
no library change: the call returns, so there is no owner to repair. It asserts

* `lattice.O() is lattice.Aut()`, and the two spellings read one generating family;
* both `discriminant_image()` calls lie in `O(A_{T_En})` (`supergroup() is` the target),
  are non-trivial, have equal computed orders and equal generating families;
* the image's order equals the computed order of `O(A_{T_En})`, and
  `discriminant_representation_is_surjective()` is `True` — so the returned subgroup is
  `rho(O(T_En)) = O(q_{T_En})`, not a proper subgroup of it;
* every generator of the image is the `discriminant_morphism()` of a generator of
  `O(T_En)`, so the subgroup is the image of the selected family.

## Run

```
/sage/.venv/bin/python -u -m pytest \
  tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage \
  -q -o addopts= -p qc_sage_session --tb=short -rf -p no:cacheprovider \
  --durations=0 --durations-min=0 -s
```

```
.
============================== slowest durations ===============================
336.92s call     ...::test_the_orthogonal_group_of_ten_has_a_discriminant_image
1 passed in 338.76s (0:05:38)
```

peak tree RSS 686 MiB. Test lint on the file: `1 files, 0 findings`.

`addopts` is blanked (this venv carries neither `pytest-timeout` nor `pytest-reportlog`)
and the call is far over the repository's 20 s ceiling and 60 s `--timeout`, so the
gated configuration's computation is reported with the ceilings lifted, as for #296,
#321 and #303.

**The 338 s is itself a measurement of the generator stage's variability.** The same
computation in a probe process took 76 s for the port's generators; in the pytest process
it took most of 338 s. Nothing in the test branch differs — the port's search is the same
call with the same arguments — so the generator stage's cost (and, as #289 records, its
family) is not pinned by this library. That is #289's subject, and it is the next unit.

## Issue closure text

> `NamedLattices.TEn.O().discriminant_image()` returns on `a9ed52b`. The two spellings are
> one group: `O` is `orthogonal_group` → `Aut()` → `Isom(L,L)`, and
> `_lattice_isometry_mor` is cached on `(id(L), id(L))`, so `TEn.O() is TEn.Aut()`. The
> image has order `46 998 591 897 600`, equal to the computed `|O(A_{T_En})|`, so
> `rho(O(T_En)) = O(q_{T_En})` here (`discriminant_representation_is_surjective()` is
> `True`).
>
> The reported stop is the cold generator stage: `group_generators` is cached per isometry
> Mor, its first read runs the port's `automorphism_group_generators` (198 generators,
> 76 s in a probe process, 338 s under pytest), and every later read in the same process is
> free — which is the 0.2 s the other chat measured. The other way it fails is the port
> being imported from the image's baked copy instead of `/work`, which raises
> `TypeError ... not 'OwnedJoinCategory.element_class'` at `recursive.py:154`; that is a
> setup error.
>
> `tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage`,
> `1 passed in 338.76 s`, test lint `0 findings`.
