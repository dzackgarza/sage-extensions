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
