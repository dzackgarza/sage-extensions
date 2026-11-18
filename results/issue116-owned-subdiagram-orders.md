# #116: the owned subdiagram orders, decided item by item

**Result: every item of the acceptance holds on `main` at `f2c519c`, and none of
them needed a change in `src/`.** The six `CoxeterDiagrams` queries answer
objects of `PartiallyOrderedSets()`, the posets are constructed from a set and
its order relation, the members keep their vertex inclusion, the orbits are cut
out by the owned group action, and both closure specimens hold. What the tree
was missing was a test deciding those statements, which is
`tests/categories/test_the_subdiagram_orders_are_owned_partial_orders.sage`
(4 tests, 1.61 s). Because the behaviour already holds at the parent, no red
test was possible on this issue; the probe below is the parent-commit evidence,
and the module is green at the parent as well.

Run in the adopted runtime with the tree bound at `/work`:

```
~/sage-image/run.sh -w /work -b <worktree>:/work -b ~/ai-review-ci:/ci -- \
  /bin/sh -c 'export HOME=/root;
    export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src;
    /sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
      -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
      --durations=0 <files>'
```

## The items

| # | The acceptance says | Decided by | The site that states it |
| --- | --- | --- | --- |
| 1 | `PartiallyOrderedSets()` constructs a finite poset from its finite set `X` and its relation `le`, retaining both, and answers `le`, `cardinality`, iteration, `maximum`, `minimum` | `test_a_partial_order_retains_its_set_and_its_relation` (the four-point chain `0<1<2<3`) | `set_categories.py:6958` `_PosetOnOrderRelation`, `:7023` `PartiallyOrderedSets.__call__`, `:7053-7088` `le`/`maximum`/`minimum` |
| 2 | the `A_2` closure specimen: an object of `PartiallyOrderedSets()` of cardinality 4, maximum the diagram, minimum the subdiagram on no vertices | `test_the_a2_subdiagram_poset_is_the_four_point_order_of_inclusion` | `coxeter_diagrams.py:1833` `_subdiagram_poset_on`, `:1841` `subdiagram_poset` |
| 3 | the six queries answer such objects | `test_the_six_subdiagram_orders_of_d4_are_owned_partial_orders` (`D_4`: 16, 16, 0, 8, 8, 0) | `coxeter_diagrams.py:1841,1851,1857,1863,1899,1905` |
| 4 | members are induced subdiagrams retaining their vertex inclusion into the diagram | the `A_2` test: each point's `arrow()` is the identity on its own vertices and has the diagram as codomain | `coxeter_diagrams.py:735` `induced_subdiagram`, the inclusion at `:820` |
| 5 | orbits are computed through the owned group action, not by iterating the group | no test can assert this (it is a property of the computation, not of a value); the probe below and the site | `coxeter_diagrams.py:1565` `_subdiagram_g_set`; `g_sets.py:603` `_orbit_labels` takes the images of `group_generators()` and makes one `Orbits` call on them |
| 6 | an orbit is the orbit, not a representative | `test_an_outer_vertex_orbit_of_d4_is_the_orbit_not_its_representative`: the three outer singletons of `D_4` are one point of the orbit set, and that point holds all three | `g_sets.py:1332` `_Orbit`, `:1450` `_OrbitSet.orbit_of` |
| 7 | `subdiagram_orbit_poset` takes no caller-supplied representatives | the same tests: its one argument is an orbit set, and an orbit set of another diagram is refused (probe below) | `coxeter_diagrams.py:1863` signature `(self, orbits)`, assertion at `:1875` |
| 8 | `Aut` computed by networkx stays inside a declared private adapter returning an owned group | probe: `d4().Aut() in Groups()`, order 6 | `coxeter_diagrams.py:1389` `_bond_preserving_permutation_group`, the `import networkx` at `:1399`, `:1439` `Aut` |
| 9 | `plot()` returning Sage `Graphics` is a display artifact, recorded in its docstring | probe: `type(d4().plot())` is `Graphics` | `coxeter_diagrams.py:2097-2107`, the ruling of 2026-10-14 in the docstring |
| 10 | the `D_4` closure specimen: `elliptic_subdiagram_orbit_poset()` of cardinality 8, the centre's orbit not below the three outer nodes' orbit | `tests/lattices/test_coxeter_subdiagrams.sage:70-92`, green, and independently brute-forced in the probe | `coxeter_diagrams.py:1899` |

## The probe at the parent

`PartiallyOrderedSets()(X, le)` on `Sets.Δ[3]`, the two closure specimens, the
`D_4` orbit poset compared with the definition on every ordered pair, the orbit
set, and the drawing:

```
1 constructor: True True True 4 (0, 1, 2, 3) 3 0 True False
2 A2 poset: True 4 True True 0
3 six queries in PartiallyOrderedSets(): True | cardinalities: (16, 16, 0, 8, 8, 0)
3 D4 orbit poset: cardinality 8 | pairs 64 | disagreements 0 | centre below three outer: False | outer vertex orbit size: 3
4 orbit of three outers is one point: True | points: 3
5 plot type: Graphics
```

Line 1 is, in order: an object of `PartiallyOrderedSets()`; of `FiniteSets()`;
`underlying_set() is` the set supplied; cardinality 4; iteration `(0, 1, 2, 3)`;
maximum 3; minimum 0; `le(1, 2)` true and `le(2, 1)` false. Line 3's `pairs 64`
is all ordered pairs of the eight orbit points, and `disagreements 0` is the
orbit order checked against "some member of `[H]` is contained in some member of
`[K]`" read off the vertex sets of every point of both orbits.

The caller-supplied-representatives case, and a foreign orbit set:

```
representatives refused with: AttributeError | 'SliceCategory.parent_class[...' ...
foreign orbit set refused with: AssertionError | Orbit set of {0, ..., 7} with Subgroup of Symmetric group S_3-actio...
```

## The runs

| run | result |
| --- | --- |
| the new module, time gates and the test lint on | 4 passed in 1.61 s |
| `tests/lattices/test_coxeter_subdiagrams.sage` + `tests/objects/test_coxeter_diagram_a2.sage` | 13 passed in 3.57 s |
| `tests/categories/test_partially_ordered_set_mor.sage` | 1 passed in 0.58 s |
| `tests/lattices/test_the_maximal_subdiagram_orbits.sage` (#254's module, the other consumer of `subdiagram_orbit_poset`) | 7 passed in 418.89 s; the run ends red on the 20 s call gate alone, with 136.04 s, 46.24 s and 229.42 s on three rows |

The last row is a cost reading, not a behaviour one: no test of that module
fails, and the three overruns are on the heavy rows (partitioning the maximal
elliptic orbits, `subdiagram_rank`, and the vertex relabelling). It was measured
while three other sessions' jobs held the four CPUs (load average 5.8), so it is
not a regression measurement against the parent; the cost of those rows belongs
to #254's owner and is not a statement of this issue's delta.

## Outside this issue's delta

The delta of the issue body owns `categories/sets/set_categories.py` and
`categories/coxeter_diagrams.py`. The complaint's `RegularPolytopes` paragraph
(`categories/schemes/polytopes.py`, `CAT-15`) is not in it, and the tree has
moved on there: `abstract_polytope()` builds through `from_face_poset`
(`polytopes.py:219`), the object retains the finite graded poset of faces, and
`face_poset()` answers the polytope itself (`:253`). The `Groups.Coxeter`
observation of 2026-10-07 no longer reproduces either: `Groups.Coxeter(["A", 2])`
answers a group of order 6 and `Groups.Coxeter(D_4.coxeter_matrix())` one of
order 192.
