# #113: the acceptance, item by item

**Result: every clause of the issue's "Required result and acceptance
criteria" holds on this tree, and one clause did not at `f2c519c`.** The
diagram of a Cartan label was placed on the index set Sage assigns to the
type, `{1, ..., n}` for a finite type, while the rows of its matrix and the
simple roots of the type's root lattice were placed on the owned ordinals
`{0, ..., n-1}`.  Equality is by vertex set and entries, so the third closure
specimen — "`CoxeterDiagrams()(["A", 2]) == CoxeterDiagrams()([[1, 3], [3, 1]])`
with vertices relabelled to agree" — was false.  It is true now: the label's
entries are raised onto the ordinals, in the order the type lists its simple
roots, so the engine's naming of those roots does not reach owned data.

## The clauses, and what decides each

| clause | decided by | verdict |
| --- | --- | --- |
| constructed from owned data only: the owned `m`, rows, a family of roots, a plain Cartan label `[letter, rank(, affine)]` | `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_rows`, `test_the_affine_a2_triangle_is_the_three_by_three_matrix`, `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_simple_roots`, `test_the_retained_datum_is_the_family_of_entries` (rows and `m`), `test_a_rooted_diagram_is_its_roots` (roots) | holds |
| no Sage `CoxeterMatrix` or `CartanType` is admitted | probe, 8 questions: `CoxeterDiagrams()` and its two constructors, `Groups.Coxeter` and `CoxeterGroups()`, each given a Sage `CoxeterMatrix` and a Sage `CartanType` | holds: all 8 refuse |
| the stored datum is the owned `m`; a Sage `CoxeterMatrix` is computed on request in a declared private adapter | probe: `coxeter_matrix()` is an `IndexedFamily`, is not a Sage matrix, its values are owned cardinals, and `_engine_coxeter_matrix()` returns the Sage matrix that realizes it | holds |
| the underlying labelled graph is constructed through `LabelledGraphs.object(...)` | probe: one interception of `LabelledGraphs.object` during construction records exactly one call, with `categories=(CoxeterDiagrams(),)`; plus `test_the_diagram_is_a_labelled_graph_on_its_vertices` | holds |
| diagrams are equal exactly when their vertex sets and `m` agree, and for rooted diagrams their roots too | `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_rows` (`A2 != B2`), `test_a_rooted_diagram_is_its_roots` (one `m`, two root realizations, distinct diagrams) | holds |
| a rooted and an unrooted diagram are distinct objects | `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_simple_roots`, `test_the_rooted_diagrams_are_a_data_subcategory` | holds |
| rooted diagrams are a data subcategory constructed with their roots, not an axiom | probe (`CoxeterDiagrams().Rooted()` is not a `CategoryWithAxiom`, and is a subcategory of `CoxeterDiagrams()`) and `test_the_rooted_diagrams_are_a_data_subcategory` | holds |
| `Groups.Coxeter` and `CoxeterGroups` admit no Sage datum | probe (4 refusals); the label path they do accept is exercised by `tests/groups/test_coxeter_finite_orders_archive.sage`, 2 passed | holds |
| `lexicon/geometry.py` exports no Sage `CoxeterMatrix` | probe: no exported name mentions Coxeter or Cartan, and the session binds no `CoxeterMatrix` at all | holds |
| closure specimen 1: `CoxeterDiagrams()(Lattices(ZZ)([[-2, 2], [2, -2]]).module_generators())` equals `from_roots` on the same roots | probe, verbatim: `True`; the same statement on `A2`'s simple roots, with the rooted and unrooted diagrams distinguished, is `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_simple_roots` | holds |
| closure specimen 2: `[[1, 3, 3], [3, 1, 3], [3, 3, 1]]` is the affine `A2` triangle | `test_the_affine_a2_triangle_is_the_three_by_three_matrix`: connected, parabolic, form rank 2, nullity 1, and equal to the diagram of `["A", 2, 1]`; the probe asks the same of the triangle on its own | holds |
| closure specimen 3: the label and the rows of one matrix are one diagram, and neither is the rooted `A2` | `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_rows`, `test_the_diagram_of_a_cartan_label_is_the_diagram_of_its_simple_roots` | **was false at `f2c519c`; holds here** |

A test may name only session names (`test_lint` `TL01`/`TL13`), and the
session publishes no Sage constructor, so no test can write a Sage
`CoxeterMatrix` to hand to a constructor.  The four negative and structural
clauses are therefore probes, and the fields of a probe are what they are
evidence for.

## The red, before the repair

`tests/objects/test_coxeter_diagram_constructed_from_its_data.sage` on a
worktree at `f2c519c`, run the way CI runs it (`-p qc_sage_session -p
sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint
--no-time-gates`, `pytest -o addopts=`):

```
>       assert CoxeterDiagrams()(["A", 2]) == a2_rows()
E       assert Coxeter diagram on 2 vertices == Coxeter diagram on 2 vertices
>       assert unrooted.index_set() == rooted.index_set()
E       assert {1, 2} == {0, 1}
2 failed, 5 passed in 1.20s
```

Both failures are assertions on library constructor calls, not the absence of
a method.  On this tree the same file is `7 passed in 1.28s`.

## What was changed, and the searches

`_coxeter_matrix_of_cartan_label` is the one site: `vertices =
finite_ordered_set(engine.index_set())` became `vertices =
finite_ordinal_set(int(engine.rank()))`, with the engine's vertices mapped to
the ordinals positionally.  The `_call_` docstring example that read
`C(["A", 2]).coxeter_entry(1, 2)` now reads `(0, 1)`.

Searched, in the order the work needed them:

- the repository, for every consumer of the adapter:
  `rg -n 'from_cartan_type\(|CoxeterGroups\(|Groups\.Coxeter\(' src tests` and
  `rg -n '_coxeter_matrix_of_rows\(|_coxeter_matrix_of_cartan_label\(' src`.
  Six test files consume it (`tests/objects/test_coxeter_diagram_a2.sage`,
  `tests/groups/test_coxeter_finite_orders_archive.sage`,
  `tests/foundations/test_refine_archive.sage`,
  `tests/lattices/test_coxeter_affine_unions.sage`,
  `tests/lattices/test_vinberg_invariants.sage`,
  `tests/lattices/test_the_maximal_subdiagram_orbits.sage`); two library
  consumers, `ade_surfaces.coxeter_diagram()` and
  `vinberg_invariants.from_coxeter_diagram`, are vertex-label agnostic, and
  `definite_lattices`' plate recognition uses Sage's own
  `CartanType.dynkin_diagram()` from inside its engine adapter.
- the library, for the convention the vertices should take:
  `Lattices(ZZ)("A2").module_generators()` is labelled `{0, ..., 1}` and
  `_coxeter_matrix_of_rows` uses the row positions, so the ordinals are the
  owned vertex set and Sage's `{1, ..., n}` was the outlier.
- Mathlib, for whether relabelling is the missing operation:
  `Mathlib/GroupTheory/Coxeter/Matrix.lean:89-96` has `CoxeterMatrix.reindex`
  (`M.reindex e i i' = M (e.symm i) (e.symm i')`), and it was read and not
  added: a relabelling is already an arrow of this category
  (`CoxeterDiagrams().Mor(D, D')(bijection)`), and the specimens need no
  relabelling once the three constructors place the matrix on one ordinal set.
- `lean-categories` for the morphisms of Coxeter data the issue requests: not
  checked out in this VM.  That is an access failure, never a negative
  result, and it is not code work in this repository.

## The runs

- the new file, this tree: `7 passed in 1.28s`, test lint `0 findings`.
- the six consuming files, this tree, 463.72 s:
  `26 passed, 1 failed, 12 errors`.
  - the failure is `test_vinberg_invariants.sage::test_cos_pi_over_n_are_the_reflection_cosines_and_one_third_is_not`,
    `ValueError: Real Algebraic Field is not in Category of sets with partial
    maps` from `QQbar(cosine)` over an owned real algebraic: identical at
    `f2c519c`, so pre-existing and unrelated.
  - the 12 errors are the test lint's own findings in
    `tests/lattices/test_coxeter_affine_unions.sage`: `20 findings (TL01,
    TL02, TL03, TL08, TL10)` on this tree and on `f2c519c` alike, reported as
    the failure of each test in the file.
- `sed`-free: no engine file was edited; the runtime image was not modified.
