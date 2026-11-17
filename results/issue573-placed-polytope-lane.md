# The placed-polytope lane: what holds, what it cost, and what remains

Round 3 of this work unit.  The public operations are the placed category's
`on(defining_data, ambient_inclusion)`, `vertices()`, `face_poset()`,
`abstract_automorphisms()`, `geometric_automorphisms()` (`= Aut(P)`),
`geometric_to_abstract_automorphisms()` and `Isom`/`Aut`/`Core`, with the owner
constructors the ambient needs: `RealVectorSpaces(n).an_object()`,
`RealVectorSpaces(n).affinization()`, `RealAffineSpaces().an_object()`,
`AffineSpacesWithLattice().an_object()`.

A specimen is built as

    vector_space = RealVectorSpaces(2).an_object()
    affine_space = RealVectorSpaces(2).affinization()(vector_space)
    lattice = ZZ.free_module(2)
    inclusion = Sets().Mor(lattice, vector_space)(...coordinates by the lattice...)
    category = LatticePolytopesIn(AffineSpacesWithLattice().on(affine_space, inclusion))
    placed = category.on(("vertices", polygon.vertices()), category.canonical_placement(polygon))

## Measured (one session, `/sage/.venv/bin/python`, timings from pytest)

| specimen | abstract | geometric | induced map | call time |
| --- | --- | --- | --- | --- |
| square `conv{(±1,±1)}` | 8 | 8 | onto, identity to identity, law on the generators | 2.58 s |
| irregular quadrangle `{(0,0),(1,0),(0,1),(2,3)}` | 8 | 1 | trivial image, not onto | 0.18 s |
| square, explicit vertical reflection | — | order 2 element | left edge to right edge, bottom and top fixed, top and empty face fixed | 0.51 s |
| stored Sterk2 hull (17 edges) | 34 | 2 | injective, not onto | 1.14 s |

The whole file: 4 passed in 4.86 s.  With
`tests/schemes/test_polytope_face_automorphism_owner.sage`,
`tests/schemes/test_polytope_face_automorphisms.sage`,
`tests/schemes/test_lattice_affine_unit_shear.sage` and
`tests/schemes/test_integral_affine_atlas_of_a_lattice_polygon.sage`:
26 passed in 9.66 s.

## What the lane states, exactly

* the placed polytope retains the polytope it places and the placement, so
  `underlying_polytope()` is that object and `face_poset()` is that object's face
  object -- the top face is the polytope, not a copy;
* on the lattice lane the placement is checked to be the lattice embedding: each
  placed vertex differs from the placed origin by the lattice translation of the
  corresponding difference of coordinates;
* a geometric automorphism's ambient map is an arrow of the affine space *with the
  selected lattice*, and its linear part is integral there;
* an engine permutation is read back as an ambient affine map only when the
  placement is full dimensional, and the frame refuses otherwise: no map is chosen
  on a complement the polytope does not meet;
* the induced map's target is `face_poset().Aut()`, and its value on an arrow is
  that arrow's own `faces' map`.

## What remains

1. The metric placed categories (`EuclideanPolytopesIn`,
   `SphericalGeodesicPolytopesIn`, `HyperbolicGeodesicPolytopesIn`) refuse an arrow:
   `MetricPolytopeMor`'s constructor states that an ambient isometric embedding is
   required and that the ambient metric space states no isometry decision to check
   one with.  A metric lane needs that decision at the metric owner.
2. `faces`, `face_inclusion`, `boundary`, `boundary_inclusion`, `triangulate` and
   `geometric_lifts_of_face_automorphism` of the placed category are still
   unimplemented.  None of the three delegations above needs them; `faces` on a
   placed polytope would have to say whether a face is placed or underlying.
3. A polytope object still refuses a *lattice* point at its own ingress:
   `square(vertex)` raises and `vertex in square` is `False`, while
   `square.contains_point(vertex)`, `square.rational_point(vertex)` and every face's
   `contains_point(vertex)` answer.  The refusal is in the subset's ingress, which
   coerces a candidate through its ambient module before the predicate runs; the
   conversion that admits a lattice point is now one function
   (`_ambient_point_on`), used by `rational_point` and by membership.
4. The Sterk rank and dimension questions remain at parent #256.

## Round 4: the placed category's own structure

The six operations are implemented for the lattice lane and are exercised on the
three specimens by `tests/schemes/test_placed_polytope_structure.sage` (3 passed in
3.38 s: 1.47 s the Sterk2 hull, 0.98 s the square, 0.28 s the quadrangle; with the
three earlier files, 23 passed in 11.77 s).

The decision, and it is stated in the module docstring of
`src/sage_extensions/categories/schemes/polytopes.py`: **a face of a placed
polytope is a placed polytope.**  The geometric automorphisms act on the faces with
the parent's ambient map, so a face must be an object of the same placed category,
carrying the parent's placement restricted to it.  The cost is stated with it: a
face whose vertices do not affinely span the ambient space (a vertex, or an edge in
a three-dimensional ambient) carries its placement but determines no ambient affine
map of its own, so the frame refuses it and nothing is chosen on a complement the
face does not meet; its inclusion and the lift of a parent automorphism to it stay
defined, because neither reads an ambient map back from the face's vertices.

| operation | signature | specimen fact |
| --- | --- | --- |
| `faces` | `faces(self, dimension)` | square 4 vertices, 4 edges, itself, and the empty face at `-1` |
| `face_inclusion` | `face_inclusion(self, face)` | identity ambient map; fixes the face's points; top face's inclusion is the polytope's identity |
| `boundary` | `boundary(self)` | the codimension-one faces; empty for a point |
| `boundary_inclusion` | `boundary_inclusion(self)` | family of the boundary faces' inclusions, one arrow per face |
| `triangulate` | `triangulate(self)` | square two triangles of normalized volume 4 each; Sterk2 fifteen; cells on the parent's placed vertices |
| `geometric_lifts_of_face_automorphism` | `geometric_lifts_of_face_automorphism(self, geometric_automorphism, face)` | `Aut(F)`, or `None` when the parent's automorphism moves the face |

The square's vertical reflection keeps the bottom and top edges -- its lift's
lattice part is diag(-1, 1) -- and exchanges the left and right edges, where the
lift is `None`.

Two repairs were needed at their owners: `PlacedPolytopeMor.__mul__` now composes
with an isomorphism's forward arrow when the right factor is an element of
`Aut(P)`, and equality of graded-poset morphisms compares through the isomorphism's
forward arrow rather than by its parent.

Still open, and not this lane's: #580 (the isometry decision at the metric owner)
and #581 (a polytope's ingress at a lattice point).  Also open here: the *unplaced*
convex polytope's `face_inclusion`, `facet_inclusion`, `boundary` and
`boundary_inclusion` (`src/sage_extensions/categories/schemes/polytopes.py`, in
`ConvexPolytopes.ParentMethods`), and `ChosenTriangulations.on` /
`_from_engine_triangulation` (`src/sage_extensions/categories/triangulations.py`),
which is what `triangulations()` would hand the cells to.
