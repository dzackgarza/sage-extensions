# #344: the edgewalk's port API is the pinned one, and the wrapper advertised more

**Result: `allcock_edgewalk` works against the pinned port again; the module that tested the
options it advertised is replaced by one that tests what the walk decides.** The four failures
were not in the port — they were sage-extensions calling keywords and a function that no
revision of the port has ever had.

## The four failures, on `main` at `5a9874e`

```
FFFF                                                                     [100%]
tests/lattices/test_edgewalk_source_options.sage:22: in test_k3_mode_excludes_the_norm_four_wall
    all_walls = tuple(lattice.allcock_edgewalk().simple_roots())
src/sage_extensions/categories/hyperbolic_lattices.py:1100: in allcock_edgewalk
    return self._edgewalk(option_norms, early_termination, initial_vertex)
src/sage_extensions/categories/hyperbolic_lattices.py:1052: in _edgewalk
    return edgewalk_fundamental_domain(
E   TypeError: edgewalk_fundamental_domain() got an unexpected keyword argument 'option_norms'
4 failed in 1.10s
```

All four fail the same way, the first on the *default* call: the wrapper passes
`option_norms`, `early_termination` and `initial_vertex` on every invocation.

**The port the environment imports**, measured inside the runtime:

```
sage_indefinite_port: /work/src/sage_indefinite_port/__init__.py
edgewalk module: /work/src/sage_indefinite_port/indefinite/edgewalk.py
edgewalk_fundamental_domain: (lattice: 'HyperbolicLattices.ParentMethods') -> 'AllcockEdgewalkReport'
has edgewalk_isometry: False
_Edgewalk.walk signature: (self) -> 'AllcockEdgewalkReport'
/work revision: 991b88b095a42a1e3679569ea42328c900c120f6
```

That is the paused pin. The checkout the image itself carries,
`/repos/sage-indefinite-port` at `4f0ee50`, has the same one-argument signature and no
`option_norms` or `edgewalk_isometry` either, and `git log --all -S` finds neither name in any
branch of the port's history. So there was never an engine behind these four parameters.

## Ownership: sage-extensions owns the operation

The test never imports the port. Every call goes through a public sage-extensions method:

* `HyperbolicLattices.parent_class.allcock_edgewalk` — `src/sage_extensions/categories/hyperbolic_lattices.py:1093`,
  documented as its API: "``option_norms="K3"`` walks the norm-two reflection subgroup.
  ``early_termination=False`` lists every vertex orbit of a non-reflective lattice.
  ``initial_vertex`` prescribes the start."
* `HyperbolicLattices.parent_class.edgewalk_isometry` — `:1102`, "Return an isometry to ``other``
  found by the edgewalk route, or ``None``."

Both were added by sage-extensions commit `451d4b8`. So the defect is here, not in the port, and
it is repaired here.

## The repair

`src/sage_extensions/categories/hyperbolic_lattices.py`:

* `_edgewalk()` takes no parameters and calls the port's actual entry point,
  `sage_indefinite_port.indefinite.edgewalk.edgewalk_fundamental_domain(self)`. The `(1,n)`
  transport through the twist functor is unchanged.
* `allcock_edgewalk()` takes no parameters, and its docstring names the port module, its
  revision and its signature, so the next caller sees the engine's shape.
* `edgewalk_isometry` is removed: the port publishes no such route, and building one here
  would be a second algorithm in the consumer.
* `edgewalk_is_reflective` and `edgewalk_simple_roots` are unchanged and keep working.

`tests/lattices/test_edgewalk_source_options.sage` becomes
`tests/lattices/test_edgewalk_fundamental_domain.sage`, testing the three decisions the walk
makes, with the values it returns at the pin:

| lattice | reflective | simple roots | root norms | vertices |
| --- | --- | --- | --- | --- |
| `U + <2>` | True | 3 | `{2}` | 2 |
| `U + <4>` | True | 3 | `{2, 4}` | 2 |
| `U + <46>` | False | 0 | — | 3 |

The norm-four wall in `U + <4>` is the invariant the old module was built for, and it holds:
the walk is over every root, so no restriction to the norm-two ones is in force.

## Green, and what the neighbouring module does

```
....FFFF                                                                 [100%]
1.91s call  …::test_the_walk_is_over_every_root_so_the_norm_four_wall_is_one
1.72s call  …::test_a_non_reflective_lattice_is_reported_and_no_reason_is_recorded
1.07s call  …::test_the_walk_certifies_the_reflectivity_of_the_chamber_it_finds
4 failed, 4 passed
```

The three new tests pass. The four failures are in `test_reflection_hyperbolic.sage`, and they
are **pre-existing**: at `8b54761`, with none of this unit's change in the tree, that module is
`4 failed, 1 passed` with the same four ids (`…represents` is missing on a local ring), so they
belong to another issue and are reported rather than touched.

## Parked, not supplied

The norm-two (`K3`) filter, the prescribed start vertex, the full walk and the isometry witness
have no engine in the pinned port, which the user has paused; they are not re-implemented in
this consumer. They return to this API when
`sage_indefinite_port.indefinite.edgewalk` exposes them, and until then the wrapper states what
it does instead of advertising what it cannot.
