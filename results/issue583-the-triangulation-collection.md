# The triangulation collection of a lattice polytope

Issue #583, one round.  What the collection now is, the exact signature and
behaviour of each of the four operations and the two axiom families, the search
made before each declaration, the measurements, the comparison against #582's
numbers, and what is open.

## The decision

The collection receives cells and computes none of them.  A triangulation of a
polytope is a property of the polytope, and the polytope answers it in
`triangulate(engine="auto")` on both lanes (#582), so `on` takes that family and
`_from_engine_triangulation` translates the private computation's own answer into
the same family.  Nothing in `triangulations.py` runs a triangulation.

Stated in the module docstring of
`src/sage_extensions/categories/triangulations.py` and in the docstring of each
operation.

## The four operations

| operation | signature | where | what it answers |
| --- | --- | --- | --- |
| `on` | `on(self, cells)` | `triangulations.py:116` | the collection on the family `cells`: each admitted as a polytope of the target's own ambient lattice lying in the target, then `_object_of(self, target=target, cells=selected)`; the family is not recomputed |
| `_from_engine_triangulation` | `_from_engine_triangulation(self, engine_triangulation, vertex_map)` | `:183` | the same collection from the private computation's answer: each simplex is positions in `vertex_map`, each cell is the convex hull of the points those positions name, read through the target's own `rational_point`; it ends in `on` |
| `covers_target` | `covers_target(self)` | `:267` | containment of each cell plus equality of the summed normalized volumes with the target's |
| `intersections_are_common_faces` | `intersections_are_common_faces(self)` | `:295` | for each pair of distinct cells, the intersection is a face of each — membership of the intersection in each cell's `face_poset()`; an empty intersection is the empty face |

Two decisions carry the axioms, on the object and not at construction
(`OWN-22`):

| operation | signature | where | what it answers |
| --- | --- | --- | --- |
| `cells_are_integral` | `cells_are_integral(self)` | `:323` | every cell is a lattice polytope in the target's lattice |
| `cells_are_unimodular` | `cells_are_unimodular(self)` | `:334` | every cell has normalized volume one |

The two axiom families:

| declaration | signature | where | what it answers |
| --- | --- | --- | --- |
| `SubcategoryMethods.Integral` | `Integral(self)` | `:99` | this category with the axiom; the spelling the category had declared and did not answer |
| `SubcategoryMethods.Unimodular` | `Unimodular(self)` | `:108` | the same for the unimodular axiom |
| `Integral` | `_certifying_predicate = "cells_are_integral"` | `:350` | the axiom, decided by that predicate |
| `Integral.ParentMethods.simplex_vertices_are_integral` | `simplex_vertices_are_integral(self, simplex)` | `:359` | one cell's vertices are points of the lattice it is framed by |
| `Integral.ParentMethods.lattice_comparison` | `lattice_comparison(self)` | `:356` | **open** — a stub, see below |
| `Unimodular` | `_certifying_predicate = "cells_are_unimodular"`, `extra_super_categories` = `Integral()` | `:369` | the axiom and its refinement of `Integral` |
| `Unimodular.ParentMethods.normalized_volume` | `normalized_volume(self, simplex)` | `:378` | one cell's normalized volume, in the lattice parallel to its affine hull |

`Integral` is read as the category states it — "integral relative to the
target's selected lattices", with `simplex_vertices_are_integral` as its own
member — and not as the name suggests; `Unimodular` is read as its declaration
states it, "maximal simplices have normalized volume one".

The property-named constructions, which decide their claim and place the result:

| construction | signature | where | behaviour |
| --- | --- | --- | --- |
| `integral` | `integral(self, cells)` | `:157` | `refine(on(cells), Integral())`; a family whose cells are not lattice polytopes raises `ValueError` naming `cells_are_integral()` |
| `unimodular` | `unimodular(self, cells)` | `:171` | `refine(on(cells), Unimodular())`; a cell of normalized volume other than one raises `ValueError` naming `cells_are_unimodular()` |

`Refine` is the library's own placement of an already constructed object in a
verified property category (`refine.py:610`); the two constructions are the
public spelling of it, because `refine` is not a session name and a test file may
take nothing but the session (TL01/TL13).

## One repair at the owner

The intersection of two polytopes of one lattice did not exist and
`intersections_are_common_faces` needs it, so it is declared at the owner of the
operation and not reached for past it:

| operation | signature | where | what it answers |
| --- | --- | --- | --- |
| `intersection` | `intersection(self, other)` | `polytopes.py:1842` | the private exact computation's intersection of the two halfspace presentations, framed in this polytope's lattice; two polytopes of different lattices are refused |

Because a polytope is its vertex set (`__eq__`, `__hash__`, `_convex_polytope`'s
interning store), an intersection equal to a face *is* that face object, which is
what makes "is it a face" a membership rather than a comparison.

## Deleted, because the object no longer holds them

`simplicial_complex`, `realization_map`, `simplices(dimension)`,
`simplex_inclusion(simplex)`, `_TriangulationSourceFunctor` (to
`SimplicialComplexes`) and `source()`.  The object holds the target and its cells;
those members named data it does not hold, and a functor whose `_apply_object`
reads a deleted method is a landmine.  The morphism family
(`ChosenTriangulationMor`, its category construction, `identity`,
`_element_constructor_`, `__mul__`) is untouched and still unimplemented.

## A placement is needed by none of the four

Requirement 4 of the brief asks which operation cannot be total without a
placement.  None of them: a placed polytope is one polytope of a lattice moved by
one injective affine map, and that map carries a subset to a subset, an
intersection to an intersection and a normalized volume to the same normalized
volume, so each decision is read at the polytope each cell is
(`_unplaced_polytope`, `:25`, reads `underlying_polytope()` for a placed cell and
the polytope itself otherwise).  The placed lane was probed and answers all four:
the placed square `conv{(±1,±1)}` gives 2 placed cells, `covers_target()` true,
`intersections_are_common_faces()` true, `cells_are_integral()` true, and
`unimodular` refuses it in 0.026 s.  Nothing was made partial, so there is nothing
for a type to say.

## Search before each declaration

| name | searched | found | consequence |
| --- | --- | --- | --- |
| `on` | `rg -n "def on\(" src/sage_extensions/categories/` | `integral_affine_atlases.py:112`, `stratified_atlases.py`, `manifolds_with_boundary.py`, `metric_affine_spaces.py:72`, `finite_graded_posets.py:376`, `integral_affine_collars.py:89`, `topological_atlases.py:87`, `holomorphic_atlases.py:102`, `real_ck_manifolds.py:115` | every `on` takes all of its defining data as arguments and computes none of it; `integral_affine_atlases.on` is the model, including its statement that covering is a decision of the object and not a construction condition |
| `cells` | `rg -n "def cells" src/` | `cell_complexes.py:311,432` `cells(dimension)`, `reduction_complexes.py:332,483` `cells()` | a different kind's cells; a triangulation's are the family it received, so `cells()` with no dimension |
| `_from_engine_triangulation` | `rg -n "def _from_engine_" src/sage_extensions/categories/` | `cell_complexes.py:407,510,626,727` (all stubs), `groups.py:4765`, `algebras.py:5065`, `ring_foundation.py:665,974`, `torsion_form_modules.py:2208` | no triangulation conversion exists elsewhere; the arithmetic of the conversion is `polytopes.py:2410`'s own, which reads `_owned_vertices_in_engine_order()` as the position map |
| `covers_target` | `rg -n "covers_target" src/ tests/` | the stub at `triangulations.py:121` only | declared new meaning; the volume argument is stated in the docstring |
| `intersections_are_common_faces` | `rg -n "intersections_are_common_faces\|common_faces" src/ tests/` | the stub at `:124` only | declared new; needs an intersection, see below |
| `intersection` (polytopes) | `rg -n "def intersection" src/` | `polyhedral_cones.py:598`, `finite_ordered_sets.py:691`, `set_categories.py:2878`, `lattice_morphisms.py:4252`, `predicate_subgroups.py:455`, `absolute_galois_group.py:1075`, `arrow_categories.py:1943` | none is a polytope's; the cone's is the model — same-lattice assertion, then the exact computation |
| `cells_are_integral`, `cells_are_unimodular` | `rg -n "def cells_are\|_certifying_predicate" src/` | `form_modules.py:2553,2564`, `lattices.py:3424` and four more, `modules.py:3834`, `number_fields.py:399` | a category-with-axiom is decided by a predicate of the object's own public operations; those two names are new and state what they read |
| `Integral`, `Unimodular` (as spellings) | `rg -n "\bIntegral\b" src/sage_extensions/categories/`, `rg -n "class SubcategoryMethods" -A 25 groups.py` | `schemes.py:3404` `SubcategoryMethods.Integral` + `class Integral(CategoryWithAxiom)`; `groups.py:5324` `SubcategoryMethods` | an axiom is reached by an explicit `SubcategoryMethods` method over `_with_axiom`; the category's nested axiom classes were unreachable as attributes without it |
| `integral`, `unimodular` (constructions) | `rg -n "def integral\|def unimodular" src/`, `rg -n "\brefine\b" tests/` | `tests/modules/test_the_paired_module_readings_of_an_algebra.sage:108` uses `refine`; `refine` is not a session name (probed) | a constructor named for the property is how CONTRIBUTING states such a placement (`R.maximal_ideal`); lowercase names keep the axiom's own spelling for the category |
| `_unplaced_polytope` | `rg -n "underlying_polytope" src/sage_extensions/categories/schemes/polytopes.py` | `:756` (the placed accessor), `:1021`, `:1082`, `:1178` | the placed lane's one read of the polytope it places; the helper is the same read for a cell |

## Measurements

One at a time in the pinned image (`/sage/.venv/bin/python`, pytest with
`qc_sage_session`, `suite_budget` and `test_lint`, `--no-time-gates`).

* The red, on the parent `829e0c1`: **4 failed in 2.09 s**, one failure per test,
  each where the test reads the answer the stub does not give.  Three raise
  `TypeError: ChosenTriangulations.on() missing 2 required positional arguments:
  'realization_map' and 'simplex_inclusions'`; the fourth raises
  `AttributeError: ... 'ChosenTriangulations_with_category' object has no
  attribute 'unimodular'` — the axioms are declared in the category and neither is
  reachable from it, so the property-named construction has no spelling at the
  parent at all.  The file passes the test lint at both commits.
* `tests/schemes/test_a_polygons_triangulation_collection.sage`: **4 passed in
  1.77 s**, per test 0.65 s the cells, 0.22 s the common faces, 0.20 s the
  coverage, 0.14 s the axioms.
* With the two polytope files and the category-graph file
  (`test_unplaced_polytope_structure.sage`, `test_placed_polytope_structure.sage`,
  `tests/engineering/test_the_declared_category_graph_reads_a_source_tree.py`):
  **23 passed, 3 failed in 11.26 s**.  The same 3 fail on the parent `829e0c1` in
  a clean worktree (**10 passed, 3 failed in 5.84 s**), so they are not this
  change's.
* Probes, one process: `on` 0.386 s on the square (first polytope of the run),
  0.017 s on the irregular quadrangle, 0.094 s on the Sterk2 hull;
  `_from_engine_triangulation` 0.008 s and 0.048 s, the same family as
  `on(triangulate())` on both; the placed square 0.026 s.

### Against #582's numbers

The test asserts the polygons' own facts (`n - 2` cells, volumes adding up to the
polygon's).  The numbers #582 recorded, read again through the collection:

| specimen | vertices | cells | #582's cells | normalized volumes of the cells | sum | #582's sum | covers | common faces |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| square `conv{(±1,±1)}` | 4 | 2 | 2 | 4, 4 | 8 | 8 | true | true |
| irregular quadrangle | 4 | 2 | 2 | 2, 3 | 5 | 5 | true | true |
| stored Sterk2 hull | 17 | 15 | 15 | 1, 3, 6, 6, 6, 7, 13, 15, 18, 19, 24, 35, 37, 69, 561 | 820 | 820 | true | true |

The counts and the volume sums agree; the per-cell volumes are the same multiset
#582 printed.  None of these is unimodular, including the Sterk2 hull.

## Refusals measured

* an engine position outside `vertex_map`: `ValueError` naming the position and
  the map's range;
* a cell repeating a position: `ValueError` naming the tuple and saying it is not
  a simplex;
* a cell that is not a subset of the target: `AssertionError` at `on`;
* `unimodular` on the square `conv{(±1,±1)}`, on the Sterk2 hull and on the
  triangle of normalized volume two: `ValueError` from `cells_are_unimodular()
  answers False`.

## Open

* `Integral.ParentMethods.lattice_comparison` (`triangulations.py:356`) is still a
  stub.  The tree states no meaning for it — `rg -n "lattice_comparison" src/
  tests/` finds the declaration and nothing else — and its name alone does not
  say which two lattices it compares or in which direction, so any implementation
  would be a guess.  The axiom answers without it: `cells_are_integral` is its
  decision and `simplex_vertices_are_integral` its member.
* `_from_engine_triangulation` has no test and cannot have a lint-clean one: it is
  private and a test file may not read a private attribute (TL02).  It is probed
  on both specimens instead, and the probe's output is in the fix commit's body
  and above.
* `covers_target` is decided by volume addition, which is exact for a family whose
  cells have pairwise disjoint interiors — the cells of a triangulation — and is
  `False` for a family whose cells overlap in interior, where the volume sum is
  larger than the union's.  A family that overlaps *and* still fills the polytope
  (a redundant cell beside a cover) is therefore answered `False` although its
  union is the polytope; deciding that case needs the volume of a union, which the
  polytope does not answer.
* `ChosenTriangulations.an_object()` (`:95`) is still a stub, as are the morphism
  family's members.  Neither is one of the four.
* `ConvexPolytopes.intersection` is added on the unplaced polytope only.  A placed
  polytope's intersection is the same subset placed where both are placed, and two
  placed polytopes of one category are not stated to be placed by one map, so it
  was not written; no operation of this issue needs it.
