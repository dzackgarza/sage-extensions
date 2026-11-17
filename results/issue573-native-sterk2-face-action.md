# The Sterk2 cusp polygon's face action, and what of the placed lane is blocked

Round 2 of this work unit.  The public operations are
`ConvexPolytopes.Abstract.ParentMethods.face_poset/abstract_automorphisms/
geometric_automorphisms/geometric_to_abstract_automorphisms` and, at the
abstract polytope, `AbstractPolytopes.ParentMethods.abstract_automorphisms`,
which is `Aut` of the retained finite graded poset itself
(`FiniteGradedPosets.ParentMethods.Aut/Isom`).

## The native specimen

`Sterk.sterk2_polygon(ZZ.free_module(2))` with the source's stored lengths
`(4,1,2,1,2,1,2,1,2,0,2,1,2,1,2,1,2,1,4)`:

* `Sterk.sterk2_boundary_path(...)` gives 18 points, 17 distinct: `p_8 == p_9`
  because the tenth length is zero, and `p_17 = (-24, 0)` closes on the origin.
* the polygon is the hull of those points: 17 vertices, normalized volume 820,
  433 integral points, dimension 2.
* its face poset has 36 faces, graded `-1, 0, 1, 2` as `1, 17, 17, 1`.

Measured in this runtime (`/sage/.venv/bin/python`, one session, peak RSS of the
whole probe 302 MiB):

| operation | public call | result | time |
| --- | --- | --- | --- |
| face poset | `polygon.face_poset()` | 36 faces | 0.13 s |
| abstract automorphisms | `polygon.abstract_automorphisms()` | order 34 | 0.00 s (after the poset) |
| restricted affine automorphisms | `polygon.geometric_automorphisms()` | order 2 | 0.05 s |
| induced group map | `polygon.geometric_to_abstract_automorphisms()` | owned group morphism | 0.24 s |
| engine group of the poset | `polygon.face_poset()._engine_automorphism_group()` | order 34 | with the abstract group |

The induced map's codomain *is* `polygon.abstract_automorphisms()`, its image of
the identity is the identity, it preserves multiplication on the whole source,
and it is injective and not onto.

So the specimen gives: the abstract group of the face lattice is dihedral of
order `2 * 17 = 34` (a polygon's face lattice is its vertex-edge cycle, whatever
its shape), and the affine symmetries of this hull are a proper subgroup of order
2.  The plotting notebook's saved `Aut(P) = C2` is its
`restricted_automorphism_group(output="matrix")`, i.e. the *geometric* group, and
that is the group this library returns as `geometric_automorphisms()`; the
notebook never computed the combinatorial group.  Nothing here forces `C2` on the
abstract group, and nothing asserts a count for the specimen beyond what the hull
gives.

## What is blocked, and where

The placed variants (`_PlacedPolytopeCategory.ParentMethods.face_poset,
abstract_automorphisms, geometric_automorphisms,
geometric_to_abstract_automorphisms`) cannot be exercised: no placed polytope can
be constructed in this tree.

* `src/sage_extensions/categories/real_affine_spaces.py:245` --
  `RealAffineSpaces.an_object()` body is `pass`.  Public call
  `RealAffineSpaces().an_object()` answers `None`, and
  `ConvexPolytopesIn(RealAffineSpaces().an_object())` then raises
  `AssertionError: ConvexPolytopesIn is parameterized by an object of Category of
  real affine spaces, and None is not one`.
* `src/sage_extensions/categories/real_affine_spaces.py:445` --
  `AffineSpacesWithLattice.an_object()` body is `pass`, so
  `LatticePolytopesIn(AffineSpacesWithLattice().an_object())` fails the same way.
* `src/sage_extensions/categories/real_affine_spaces.py:521,525,528` --
  `linear_extension_of_lattice_automorphisms`, `integral_affine_group` and
  `integral_affine_group_action` are `pass`; a categorical `Aut` of a *placed*
  lattice polytope would need the last of them as its engine.
* `src/sage_extensions/categories/schemes/polytopes.py:233,236` --
  `_PlacedPolytopeCategory.an_object()` and `.on()` are `pass`, and the placed
  `ParentMethods` (`vertices`, `faces`, `face_inclusion`, `face_poset`,
  `abstract_automorphisms`, `geometric_to_abstract_automorphisms`) and the
  `PlacedPolytopeMor` constructor, `identity` and `__mul__` are stubs.

`RealAffineSpaces().on(...)` and `AffineSpacesWithLattice().on(...)` do have
bodies, but the model space of the first must be an object of `VectorSpaces(RR)`
and no public construction of a rank-2 real free module in that category is
available here (`VectorSpaces(RR).free_module(2)` raises `TypeError: expected a
ring of this session, but 2 is not one`; `VectorSpaces(RR).an_object()` is rank
one).  That plumbing is the real-affine owner's, which is active, so this work
unit does not edit it.

## Remaining for the full acceptance

1. The placed variants, once an ambient `RealAffineSpaces` object exists: their
   `face_poset`/`abstract_automorphisms` delegate to the underlying polytope's
   face object, `geometric_automorphisms` is the placed category's own `Aut`
   (its elements carrying an ambient affine map and a `face_poset_map`), and
   `geometric_to_abstract_automorphisms` sends such an element to its
   `face_poset_map()`.
2. `tests/schemes/test_polytopes.sage::test_dodecahedron_has_coxeter_diagram_h3_and_symmetry_group_of_order_120`
   fails on `RegularPolytopes`' missing `f_vector`, which is that owner's stub
   and not this work unit's; it fails identically at the base commit.
3. The Sterk rank/dimension questions remain at parent #256.

Corrected 2026-11-17: the two placed-polytope stubs in
`src/sage_extensions/categories/schemes/polytopes.py` are at line 234
(`_PlacedPolytopeCategory.an_object`) and line 237 (`.on`), not 233 and 236; those
numbers were read before this round's edits to the same file.  The
`real_affine_spaces.py` line numbers above are as read on this round's base and
are unchanged by it.
