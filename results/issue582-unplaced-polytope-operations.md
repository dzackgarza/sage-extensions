# The unplaced lattice polytope's six structural operations

Issue #582, one round.  What landed, the exact signature and behaviour of each of
the six operations, the measurements they were read with, and what is open.

## The decision

The unplaced polytope is the one that knows its own face object, so it answers its
own structure and the placed category delegates to it.  Stated in the module
docstring of `src/sage_extensions/categories/schemes/polytopes.py` (the paragraph
beginning "**The unplaced polytope is the one that knows its own face object**").

What the two owners answer differently is one thing -- what a face *is* -- and it is
stated once, in `faces`.  Everything else reads `faces`, `dimension` and
`face_inclusion`, which each owner states in its own arrows.

## The six operations, on the unplaced polytope

| operation | signature | where | what it answers |
| --- | --- | --- | --- |
| `face_inclusion` | `face_inclusion(self, face)` | `polytopes.py:2068` | the subset inclusion `Sets().Mono(face, self)._from_subset_inclusion()`: a point of the face to that same point of the ambient space, injective, image the face; the top face's inclusion is the identity |
| `facet_inclusion` | `facet_inclusion(self, facet)` | `polytopes.py:2146` | `face_inclusion` at a face of codimension one, the dimension decided first, so a vertex or the polytope itself is refused |
| `boundary` | `boundary(self)` | `polytopes.py:158` (`_PolytopeFaceStructureMethods`) | the faces of codimension one; the empty family below dimension one |
| `boundary_inclusion` | `boundary_inclusion(self)` | `polytopes.py:173` (same owner) | one arrow per boundary face, the arrow at a position being that face's `face_inclusion` |
| `triangulate` | `triangulate(self, engine="auto")` | `polytopes.py:2410` | the cells of one triangulation, as polytopes of the polytope's own ambient lattice |
| `geometric_lifts_of_face_automorphism` | `geometric_lifts_of_face_automorphism(self, geometric_automorphism, face)` | `polytopes.py:2366` | `Aut(F)` for a face the automorphism preserves, `None` for one it moves |

Two declarations carry the delegations the placed lane needed:

| operation | signature | where | why it exists |
| --- | --- | --- | --- |
| `face_poset_inclusion` | `face_poset_inclusion(self, face)` | `polytopes.py:2090` | the inclusion of a face's face object into the polytope's, as a map of finite graded posets: the second component of a placed arrow's pair is a map between the *unplaced* face objects, so the polytope owns it and the placement does not |
| `dimension` (placed) | `dimension(self)` | `polytopes.py:1041` | the shared `boundary` body asks each owner for its dimension; a placement preserves it |

## What the placed category now does

* `face_inclusion(face)` (`:1021`) takes its faces' map from
  `underlying_polytope().face_poset_inclusion(...)` and computes neither component;
  its private `_parent_face_by_coordinates` is deleted, since the identity on faces
  is what that coordinate keying was reconstructing.
* `boundary` / `boundary_inclusion` are the shared body, inherited at `:741`; the
  placed copies are deleted, so `placed.boundary()` is still `placed.faces(d - 1)`
  object for object.
* `triangulate(engine="auto")` (`:1052`) places the cells the polytope answers
  instead of re-running the triangulation; its private copy is deleted.
* `geometric_lifts_of_face_automorphism` is unchanged: its two components are the
  parent's ambient map and the parent's faces' map, neither of which the unplaced
  object holds.

## LC-09, search before each declaration

`LC-09` is not a code in this repository -- `rg -n "LC-09|LC-"` over `AGENTS.md`,
`CONTRIBUTING.md`, `TRAPS.md`, `docs/` and `src/` finds nothing, and the test lint's
codes are `TL01`--`TL14`.  Read as search-before-declaration, what was done before
each new name:

| name | searched | found | consequence |
| --- | --- | --- | --- |
| `face_inclusion` | `rg -n "def inclusion|Inclusion" src/` | `SubsetEngine.inclusion` -> `Sets().Mono(...)._from_subset_inclusion()`, `FiniteOrderedSets.inclusion`, `cell_complexes.face_inclusion` | the existing owner of a subset inclusion, used rather than restated |
| `boundary` / `boundary_inclusion` | `rg -n "def boundary_inclusion" src/` | `stratified_atlases.py`, `manifolds_with_boundary.py`, `integral_affine_manifolds.py`, `cell_complexes.py` | each is another kind's boundary; the polytope's is written once, in the shared mixin, since both owners answer it the same way |
| `triangulate` | `rg -n "def triangulate" src/` | `cell_complexes.py` (four), `integral_affine_manifolds.py:705`, `polyhedral_cones.py` | none is a polytope's; the private polyhedral computation's `triangulate(engine, connected, fine, regular, star)` is the owner, and the one free choice it offers is exposed as `engine` |
| `facet_inclusion` | `rg -n "facet_inclusion" src/ tests/` | nothing | declared new; it is `face_inclusion` narrowed to codimension one |
| `face_poset_inclusion` | `rg -n "face_poset_inclusion|subposet" src/` | nothing | declared new, as the seam of the delegation |
| `geometric_lifts_of_face_automorphism` | `rg -n "geometric_lifts_of_face_automorphism" src/ tests/` | the placed copy at `:1071` only | the placed signature is the one the issue names, and the unplaced one now matches it |
| `dimension` | `rg -n "def dimension" src/sage_extensions/categories/schemes/polytopes.py` | `:1737` (unplaced) and `:1503` (regular polytopes) | the placed category had none; added as the one read the shared body needs |

## Measurements

Runs are one at a time in the pinned image (`/sage/.venv/bin/python`, pytest with
`qc_sage_session`, `suite_budget` and `test_lint`, `--no-time-gates`).

`tests/schemes/test_unplaced_polytope_structure.sage`: **6 passed**, per-operation
durations 3.95 s the lifts, 1.14 s the triangulation, 1.13 s the faces and
inclusions, 0.23 s the facets, 0.18 s the boundary's inclusion, 0.02 s the boundary.
With `tests/schemes/test_placed_polytope_structure.sage`: **9 passed in 11.67 s**.
With the four files the placed lane reads its own change through and the atlas file
(`test_placed_polytope_face_automorphisms.sage`,
`test_polytope_face_automorphism_owner.sage`,
`test_polytope_face_automorphisms.sage`, `test_lattice_affine_unit_shear.sage`,
`test_integral_affine_atlas_of_a_lattice_polygon.sage`): **35 passed in 36.29 s**,
peak tree RSS 658 MiB.

The red, on the parent `f2e1dcb`: **6 failed in 3.25 s**, one failure per operation,
each raised where the test reads the answer the stub does not give (`None.domain()`
for the two inclusions, `None` iterated for `boundary`, `boundary_inclusion` and
`triangulate`, and a signature error for the lift, which took only the
automorphism).  The file passes the test lint at both commits.

### Triangulations, against the placed round's numbers

| specimen | vertices | cells, unplaced | cells, placed (round 4) | `n - 2` | normalized volumes of the cells | the polytope's |
| --- | --- | --- | --- | --- | --- | --- |
| square `conv{(+-1,+-1)}` | 4 | 2 | 2 | 2 | 4, 4 | 8 |
| irregular quadrangle | 4 | 2 | 2 | 2 | 2, 3 | 5 |
| stored Sterk2 hull | 17 | 15 | 15 | 15 | 15, 561, 24, 37, 69, 35, 13, 18, 6, 7, 1, 19, 6, 6, 3 | 820 |

The counts agree with the placed lane's and are `n - 2` in each case, which is what
a triangulation of a convex polygon whose vertices are all extreme points has; they
are asserted as `n - 2` rather than as the numbers, and the volumes are asserted to
add up to the polytope's.  The engine is an argument (`engine="auto"` by default,
its own default stated), so the answer is not a hidden choice of algorithm; the
internal routine gives the same counts on all three specimens.

## Open

* `ChosenTriangulations.on` (`src/sage_extensions/categories/triangulations.py:83`)
  and `_from_engine_triangulation` (`:87`) are still stubs, and
  `covers_target` (`:121`), `intersections_are_common_faces` (`:125`) and the
  `Integral`/`Unimodular` axioms' members with them, so `triangulations()` hands the
  cells to nothing yet.  What the six operations give is the cells themselves:
  `ConvexPolytopes(ambient_lattice)` objects on the polytope's own vertices.
* A lattice point is still not admitted at a polytope's ingress (#581), which is why
  `face_inclusion`'s docstring says its points are the ambient space's and the file
  reads a face's vertices through `rational_point`.  The arrow's type already says
  this: its source is the polytope as a subset of the ambient space, whose points
  are the ambient ones.
* `triangulate` answers a triangulation of the whole polytope; a star, a fine or a
  regular triangulation at a chosen point would be further arguments of the private
  computation, and nothing in the tree asks for one yet.
