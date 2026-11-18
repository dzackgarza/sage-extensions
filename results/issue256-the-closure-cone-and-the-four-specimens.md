# The integral-affine sphere of a Sterk cusp (#256): the closure cone, the four
# specimens, and where the leaf stops

One round.  What landed, what each specimen question answers with what value, and
the exact failure where an item is not done.

## 0. The runtime: this VM cannot import the library

Every geometry module of `sage_extensions` fails to import here, at one line, before
any test can be collected:

```
$ PYTHONPATH=src sage -c "import sage_extensions.categories.schemes.polytopes"
  File ".../src/sage_extensions/categories/modules/native_modules.py", line 227, in construct
    free = self.base_ring().free_module(1)
  File "/opt/math/lib/python3.12/site-packages/sage/categories/rings.py", line 1710, in free_module
    raise ValueError("base must be a subring of this ring")
ValueError: base must be a subring of this ring
```

`RR = ExactRealField()` runs `_algebra_from_native_ring`, which asks the owned ring for
`free_module(1)`; the owned `Rings.ParentMethods.free_module(rank_or_index_set)`
(`ring_foundation.py:4699`) is not the method the class resolves, so Sage's
`Ring.free_module(base=1)` is called instead.

The host is Sage **10.8** (`sage --version` -> `10.8`) at `/opt/math/bin/sage`.  The
adopted runtime (`sage-image/rootfs`, Sage 11.0.beta5) is not present on this VM, and
`sageparse` -- which `sage_extensions/all.py` and `language_runtime.py` import -- exists
nowhere on this filesystem (`find / -name "sageparse*"` is empty, and it is not on PyPI),
so `from sage_extensions.all import *`, every `.sage` test file, and `qc_sage_session`
cannot run at all.  Nothing in this round was measured on the pinned image.

Two consequences, stated once and applied throughout: modules that do not touch
`rings.real` **do** run (`ring_foundation`, `polyhedral_cones`), and everything in the
geometry layer (`polytopes`, `sterk`, `catalogue`, `integral_affine_manifolds`) does not.
The specimen answers below were therefore computed from the source's own data with
Sage's exact linear algebra and polyhedra, and the assertions of the tests written here
were executed through their two library names rather than through `all`.

## 1. The closure cone and its combinatorics -- landed, and the three conditions

The operation itself already existed: `RationalPolyhedralCones.from_nonnegative_solutions`
(`polyhedral_cones.py:284`, landed as `4a33efc` for this issue) is the cone
`{ l in Z_{>=0}^n : sum_i l_i v_i = 0 }` of a morphism `Z^n -> L`.  What the issue's trap
asks for -- that the three conditions be kept apart in the API and not only in the prose
-- was not there, and is now:

| operation | where | what it decides |
| --- | --- | --- |
| `has_a_nonzero_point()` | `polyhedral_cones.py:513` | the cone is not `{0}`, i.e. a closed polygon exists at all |
| `has_a_strictly_positive_point()` | `polyhedral_cones.py:535` | the cone meets the open positive orthant, i.e. a polygon exists with **every** prescribed edge present |

Both are decided on the retained exact polyhedron: the second by intersecting it with the
orthant translated to `x_i >= 1` and asking emptiness, which is exact because the cone is
closed under positive scaling.  The third condition -- the polygon is nondegenerate -- is
not a property of the cone but the rank of the direction family, and the docstring says so
rather than folding it in.

The distinction is one specimen: `(1,0), (-1,0), (0,1)` has the closure cone
`l_1 = l_2, l_3 = 0`, one-dimensional with the single ray `(1,1,0)`.  It has nonzero points
and no strictly positive one, so *a closed polygon exists and none uses all three edges*.
The independent pair `(1,0), (0,1)` answers `False` to both.

Tests: `tests/lattices/test_rational_polyhedral_cones.sage` gains
`test_a_nonzero_point_and_a_strictly_positive_point_are_two_decisions` and
`test_the_open_orthant_and_the_cone_meet_exactly_when_a_positive_relation_exists`.
No red was possible: the two names did not exist at the parent, so a "red" would have been
an `AttributeError` for the missing fix, which is not a red.

## 2. Specimen question 1 -- the complete Sterk2 polygon, roles preserved

Decided.  The nineteen vectors of Coble cell 59 are **not** nineteen cyclic edges.  With
the source's roles:

* `v_2 .. v_18` are seventeen path steps walked from `p_0 = (0,0)`;
* `v_1 = (-1,2)` and `v_19 = (1,2)` are the surgery triangles' side directions, placed on
  the path's edges at zero-based positions 2 and 14, and are not edges of the polygon;
* the path's total vertical displacement is zero (the source's `constraint` row is exactly
  that) and its total horizontal displacement is negative, so **the closing side runs along
  `(1,0)` from `p_17` back to `p_0`**.  That is the side the plotter's convex hull supplies.

So the polygon has **eighteen** cyclic edge directions, `v_2 .. v_18` followed by `(1,0)`,
and its closure cone is sixteen-dimensional.  For the stored specimen
(`l = 4,1,2,1,2,1,2,1,2,0,2,1,2,1,2,1,2,1,4`) the source's `M_18_0_0` gives the seventeen
boundary coefficients `1,1,3,1,1,1,1,1,0,1,1,1,1,1,3,1,1`, so one prescribed direction is
absent, the path ends at `(-24, 0)`, and the closing side has length `24`.

Computed through the library's own cone:

```
sterk2: dim 16 rays 65 nonzero True positive True
rays of two-element support 2
   (0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1)      support {(-1,0), (1,0)}
   (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0)      support {(0,1), (0,-1)}
stored specimen in the cone: True
```

The two two-element rays are exactly the two antipodal pairs of the eighteen directions;
there is no third.  The stored lengths, read as the eighteen lattice lengths
`1,1,3,1,1,1,1,1,0,1,1,1,1,1,3,1,1,24`, lie in the cone.  Test:
`test_the_sterk2_boundary_path_closes_with_the_horizontal_side`.

The polygon itself (raw Sage, the source's own `Polyhedron` on the walked points): `17`
vertices -- the zero coefficient merges two of them -- ambient area `410`, i.e. normalized
area `820`, which is the number `sterk.py` states.

## 3. Specimen question 2 -- the admissible parameter space is ten-dimensional

Decided, and the eleven-parameter statement is false for this construction.

Cell 8's `Sterk2.__init__` builds `A` from **ten** rows: one constraint and nine symmetry
relations `l_i - l_{20-i}`.  Computed:

```
A dimensions (10, 19) rank 9
kernel dim 10
constraint in symmetry span: True sym rank 9
P dims (19, 10) rank 10
```

The constraint row `(3/2, 1, 2, 3, 5/2, 2, 3/2, 1, 1/2, 0, -1/2, -1, -3/2, -2, -5/2, -3,
-2, -1, -3/2)` is exactly `sum_{i=1}^{9} c_i (e_i - e_{20-i})` with
`c = (3/2, 1, 2, 3, 5/2, 2, 3/2, 1, 1/2)`, so it adds nothing to the symmetry rows: the
"vertical constraint" *is* the symmetry, and the kernel is the space of symmetric length
vectors, of dimension `19 - 9 = 10`.

The half weights and offsets are the source's `M_18_0_0`, not a statement about the raw
directions: it halves the odd-labelled lengths and adds `l_1/2` to `v_4` and `l_19/2` to
`v_16`.  The parity vector `[2,1,2,1,...]` scales the ten kernel *basis columns* so that
`soln_projection_18_0_0` is integral; that matrix is `19 x 10` of rank `10`, and `a_to_ell`
therefore takes ten parameters because the kernel has ten, not because a parity convention
fixes eleven to ten.

## 4. Specimen question 3 -- the Sterk4 maps and ranks

Decided from the named roots, the permutation and the projection, and the stored
`(20,12) 11` is **not** reproduced.

The objects: `L_20_2_0 = U (+) U(2) (+) E8 (+) E8` with `U = H`, `U(2) = H.twist(2)` and
`E8 = IntegralLattice("E8").twist(-1)` (Coble cells 6, 70), the twenty-two vectors
`v_1 .. v_22` of cell 4 read through the dual basis `G^{-1}`, the order
`W = v_13, v_12, ..., v_1, v_16, v_15, v_14, v_20, v_19, v_18, v_17, v_22, v_21`, and the
permutation `F4 = [12,11,10,9,8,7,6,5,4,3,2,1,0,15,14,13,19,18,17,16,21,20]` of the
formal root basis.  The construction is pinned by the relations the source itself prints:
with Sage's own E8 Cartan ordering the twenty-two vectors have exactly the four printed
relations and no others, and no pair of them is linearly dependent otherwise.

```
norms [-4, -2] V rank 18
printed relation space inside my kernel: True dims 4 4
Sterk4 (cell 20): |Fix| 12 (source says 12); image dims (20, 12) rank 10 kernel 2
dim(Fix) = 12  dim(Rel) = 4  dim(Fix ∩ Rel) = 2
```

The +1 eigenspace of `F4` is twelve-dimensional, as the cell states.  The twenty-two named
roots span eighteen dimensions, so the projection `W: Q^22 -> Q^20` has a four-dimensional
kernel `Rel`; the fixed space meets it in two dimensions; hence the projection restricted to
the fixed space has rank `12 - 2 = 10` and a two-dimensional kernel.

That identity fixes the answer independently of the basis chosen: the rank is
`dim(Fix) - dim(Fix ∩ Rel)`, both terms identified.  The stored `(20,12) 11` would require
the fixed space to meet the relation space in one dimension, and with the source's own
printed relations it meets it in two.  The later Sterk3-labelled cells 29--31 compute
`A = R(P-I)`, a different map on a different permutation: `rank 8` there is
`22 - 14` and says nothing about this one.

## 5. Specimen question 4 -- the polygons of cells 11--13 and their groups

Decided for the three specimens.  Each is the convex hull of the walked path of the
`18_2_0` family (`v_0 .. v_15` through `M_18_2_0`), with the source's own lengths:

| cell | cusp | lengths `l_0 .. l_19` | coefficients | vertices | normalized area | `Aut` |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | Sterk1 | `1,2,1,2,1,0,1,2,1,2,1,2,1,0,1,2,6,6,6,6` | `4,1,1,1,4,0,1,1,4,1,1,1,4,0,1,1` | 14 | 236 | `C2`, generator `diag(-1,-1)` |
| 12 | Sterk2 | `4,1,2,1,2,1,2,1,2,0,2,1,2,1,2,1,2,1,4` | `1,1,3,1,1,1,1,1,0,1,1,1,1,1,3,1,1` | 17 | 820 | `C2`, generator `diag(-1,1)` |
| 13 | Sterk3 | `2,2,2,2,2,2,2,4,2,4,2,2,2,2,2,2,24,6,30,6` | `14,1,2,1,5,1,2,2,17,2,2,1,5,1,2,1` | 16 | 1141 | `C2`, generator `[[0,1],[1,0]]` |

The printed generators are exactly the saved outputs of the three cells: `diag(-1,-1)` for
Sterk1, `diag(-1,1)` for Sterk2 and the transposition matrix for Sterk3.  Cell 11's path
closes on itself (its coefficients sum to zero) and cell 13's ends at `(-6,6)`, so only
Sterk2's needs the hull's closing side in the same sense as §2.

These are three specimens.  Each claimed group is established for its own length choice;
nothing here says `Aut(P)` is `C2` for every Sterk length vector, and the issue says it
does not.

The two polytope operations the issue lists as `pass` are **not** `pass` at this parent:
`ConvexPolytopes...abstract_automorphisms` (`polytopes.py:2314`) delegates to the face
poset's own `Aut`, and `geometric_to_abstract_automorphisms` (`:2367`) builds the group map
from the vertices' face permutation.  They landed under #573/#582.  What was not done here
is running them: the specimens above were computed with `restricted_automorphism_group`,
not through the library, because of §0.  The one `pass` body left under the names the issue
cites is `RegularPolytopes...abstract_automorphisms` (`:1518`), a different owner.

## 6. The three surgery stubs -- not implemented, and why

`SingularIntegralAffineSpaces.surgery`, `symington_surgery` and `basis_triangle_surgery`
(`integral_affine_manifolds.py:614`, `:623`, `:627`) still have `pass` bodies.  They are not
implemented because their ingredients are themselves `pass`, so any body written now would
be an invention rather than a construction:

| missing owner | where | needed by |
| --- | --- | --- |
| ~~`TopologicalSpaces.mapping_cylinder`~~ | `topological_spaces.py:643` | **not** needed: see §9, the pushout is available through the coequalizer |
| `TopologicalSpaces.subspace` | `:647` | the cut region's own topology |
| `IntegralAffineCollars.on` | `integral_affine_collars.py:89` | every `affine_collars` argument |
| `IntegralAffineCollars.comparison` | `:93` | the regluing's collar agreement |
| `SingularIntegralAffineSpaces.on` | `:600` | the object the three of them return |

and `SingularIntegralAffineSpacesOfDimension` repeats three of them at its own owner
(`:762` `on`, `:772` `from_face_gluing`, `:782` `surgery`), so the parameterized category is
stubbed too.

`on` is pure assembly and is the one of these that could be written blind; the other four
need either the topological pushout or a decision about what a collar *is* in this tree, and
the runtime of §0 cannot run a single line of either.  So the acceptance item "no `pass`
body remains on these methods" is **not** met: the honest state is five stubs, three of them
the issue's.

## 7. The edge-length space and the sigma-invariant root space -- dimension only

Not proven.  What is established: the two spaces have the same dimension, from the same
source.  Cell 8's symmetry relations are nine pairings of nineteen roots, and
`Sterk._sterk_roots_cached()["Sterk_2"]` is the ten orbit sums
`w1+w17, w2+w16, w3+w15, w4+w14, w5+w13, w6+w12, w7+w11, w8+w10, w9, w18+w19`, which span
the sigma-invariant root space.  Ten orbit sums, ten lengths `a_0 .. a_9`.

That is a dimension agreement and a natural basis correspondence, not an isomorphism of the
objects built here: no map has been constructed that carries the edge-length lattice and
its cone to the invariant root lattice and its cone, and naming one on the strength of the
dimensions would be a guess.  The exact failure is therefore: *the correspondence is
established on dimensions and on the orbit basis, and not as a map of integral-affine
objects*; the operation that would carry it (`LatticeMorphisms.invariant_lattice`, and the
`Sterk_2` orbit data) cannot be run here at all under §0.

## 8. What was run

* `PYTHONPATH=src sage .scratch/probe_predicates.py` -> the cone numbers of §2 and §1.
* `PYTHONPATH=src sage .scratch/specimen_cell12.py` -> the Sterk2 specimen of §2.
* `PYTHONPATH=src sage .scratch/specimen_cells11_13.py` -> the table of §5.
* `PYTHONPATH=src sage .scratch/sterk4_rank.py` -> the ranks of §4.
* `PYTHONPATH=src sage .scratch/run_test_bodies.py` -> the seven test bodies of
  `tests/lattices/test_rational_polyhedral_cones.sage` and
  `tests/schemes/test_lattice_polygon_edge_lengths.sage` (the four that were there and the
  three added), executed with `sage_extensions.all` replaced by the two names they use:

```
PASS test_a_nonzero_point_and_a_strictly_positive_point_are_two_decisions
PASS test_the_open_orthant_and_the_cone_meet_exactly_when_a_positive_relation_exists
PASS test_the_polygon_of_example_4_13_closes_with_two_free_edge_lengths
PASS test_the_polygon_of_example_4_14_closes_with_two_free_edge_lengths
PASS test_the_polygon_of_example_4_15_closes_with_the_alternating_lengths
PASS test_edge_directions_with_no_positive_relation_close_no_polygon
PASS test_the_sterk2_boundary_path_closes_with_the_horizontal_side
failures: 0
```

Not run: the pytest suite, the test lint, and every import of the geometry layer.  The two
test files were not collected and the lint was not applied, because neither can start on
this host.

## 9. This round's probe: what is actually behind the surgery, and one correction

The three surgery stubs are the first item §6 leaves open, so this round probed it.
Result: they are behind the runtime of §0 and nothing else in the tree.

```
topological_spaces           OK
manifolds                    ValueError: base must be a subring of this ring
```

`integral_affine_manifolds` imports `manifolds`, so the module that holds `surgery`,
`symington_surgery` and `basis_triangle_surgery` cannot be imported here, and a test of
them cannot start.  The failing call is the same one: `RR = ExactRealField()` at
`rings/real.py:1189`.

**Correction to §6.**  The glued space does not need `TopologicalSpaces.mapping_cylinder`,
which is a `pass` body.  `TopologicalSpaces._categorical_coequalizer` (`:680`) and
`_categorical_coproduct_construction` are implemented, so the pushout
`X |-> (X - region) glued along the boundary isomorphism` is constructible from them: the
coproduct of the cut space and the replacement, coequalized by the two embeddings of the
common boundary.  Of §6's five rows, only `IntegralAffineCollars.on` (`:89`),
`IntegralAffineCollars.comparison` (`:93`) and `SingularIntegralAffineSpaces.on` (`:600`,
and its three repeats at `:762`, `:772`, `:782`) remain, and all four are assembly rather
than new mathematics.  The surgery item is therefore one runtime away from being
implementable, not one construction away.

**Why the runtime is not repaired here.**  The owned `free_module` is reachable for some
rings and not for the real field:

```
ZZ OK OwnedRings.ParentMethods.free_module -> Free module on {[0]} over Integer Ring
QQ OK OwnedRings.ParentMethods.free_module -> Free module on {[0]} over Fraction Field of Integer Ring
```

so the call `free_module(1)` in `native_modules.py:227` is this library's own convention and
is right; what fails is that the dynamically generated parent class of `ExactRealField`
resolves Sage's `Ring.free_module` instead of `OwnedRings.ParentMethods.free_module`.  That
class is built from `ExactRealField.__init__`'s category meet, and the difference from `QQ`
is the meet: `OwnedFields`, `OwnedOrderedRings`, `UncountableSets`, the regular algebra and
`FinitelyGeneratedFreeModules(RR)` together.  No issue in this repository owns it --
`#38` (`Modules(R)(S)` is the free module) and `#37` (group-algebra modules) are the only
issues that mention `free_module`, and neither is this -- and whether the meet should be
repaired or the pinned image restored is a decision, not a measurement: the pinned runtime
is Sage 11.0.beta5 and this host is Sage 10.8, so a meet that is correct on one is not
established on the other by anything measurable here.

## 10. Where the runtime block actually lives: `ExactRealField`'s parent class

The previous section left the repair as "the meet or the pinned image".  This round found
the mechanism, by asking the regular-module construction which class its base ring is and
which classes in that class's MRO provide `free_module`:

```
class: _OwnedRingParent_with_category          (the owned integers, and the rationals)
  sage_extensions.categories.rings.ring_foundation._OwnedRingParent
  sage_extensions.owned_category.OwnedJoinCategory.parent_class
  ... OwnedRings.ParentMethods                 <-- provides free_module

class: ExactRealField_with_category
  sage.rings.ring.Field
  sage.rings.ring.Ring
  sage.structure.parent_old.Parent
  sage.categories.category.JoinCategory.parent_class
  sage.categories.fields.Fields.parent_class
```

`ExactRealField` is a Python subclass of **Sage's** `sage.rings.ring.Field`, while every
other owned ring is built on the repository's own `_OwnedRingParent`.  Sage's parent classes
therefore come first in the MRO, and `free_module` resolves to
`sage.categories.rings.Rings.ParentMethods.free_module` -- the earlier probe's
`Rings.parent_class` provider -- instead of `OwnedRings.ParentMethods.free_module`.  On the
argument `1` that method reads `base`, refuses it, and the construction of `RR` stops before
anything in the geometry layer exists.

Two hypotheses were tested and both fail, so this is not a category-meet ordering issue:

* naming `OwnedRings()` first in the meet `ExactRealField.__init__` builds changes nothing;
  the same `ValueError` comes back from the same line;
* patching Sage's `Rings.ParentMethods.free_module` before importing the module changes
  nothing either, because Sage copies the method into the dynamically generated parent class
  when that class is created.

The file that would have to change is `src/sage_extensions/rings/real.py`, and the issue that
declares it its owner is **dzackgarza/sage-extensions#97** ("The real line is a smooth
manifold"), whose stated owner and delta are "`rings/real.py` and `categories/manifolds.py`"
and whose subject is exactly how `RR` is constructed.  `#153` records a symptom of the same
root (`matrix_rank()` over `ExactRealField`: "base_ring Real Field must be a ring"), and
`#97` is the one that owns the construction.

A third repair was tried before concluding, and it also fails for a reason worth recording:
declaring `free_module = OwnedRings.ParentMethods.free_module` in the body of
`ExactRealField` -- naming the owner's method rather than reimplementing it -- changes
nothing either.  The class whose method is consulted is the generated
`ExactRealField_with_category`, and the category parent classes Sage composes into it
(`Fields.parent_class`, `Rings.parent_class`) shadow the attribute set on the Python base
class.  The resolution therefore cannot be reached from the class body at all: what has to
change is the category `ExactRealField` is placed in, which is what makes it a subclass of
Sage's `Field` in the first place.

So the surgery item, the Sterk4-rank test and the folding identification all wait on `#97`,
or on the pinned Sage 11.0.beta5 image, and nothing in this issue can move them.  Three
independent repairs have now been measured and refused, so a later round does not need to
try them again: the meet's ordering, Sage's method, and the class body.

### What still does not import, measured at `92188cb`

The Sterk4-rank test would be the other acceptance item with a decidable number in it, so
its route was measured too:

```
categories.schemes.polytopes   ValueError: base must be a subring of this ring
sterk                          (imports polytopes, so the same)
```

`manifolds` and `integral_affine_manifolds` import because #97 made them defer the exact
real field; `polytopes` still constructs it at import, so `Sterk.roots_18_2_0()` -- the
named roots the rank is derived from -- cannot be reached here.  The rank itself is
settled (twelve, eighteen, two, ten, two, in §4 and §11's terms); what is missing is only a
test that can call the library's own roots.

## 12. The first of the surgery's missing calls is implemented: `subspace`

`TopologicalSpaces.subspace` (`topological_spaces.py:647`) was a `pass` body returning
`None`.  It now returns ``(space, inclusion)``: the selected subset with the initial
topology along its inclusion, and the continuous map that is the identity on points from the
first into the second.

A subset ``V`` of the subspace is open exactly when it is ``f^{-1}(U)`` for an open ``U`` of
the ambient space (Mathlib, ``TopologicalSpace.induced``).  The inclusion is injective, so
``V = f^{-1}(f(V))`` and the largest candidate is ``f(V)`` together with everything outside
the image of the subspace, which no preimage can see; the ambient space's own openness
decision then answers.  The opens are enumerated for a finite enumerated set of points, and
anything else is refused rather than guessed.

Test: `tests/topology/test_the_induced_topology_of_a_subspace.sage`, both bodies pass
(2 passed, 0 failures) -- the Sierpinski space ``{0,1,2}`` with opens ``{}, {2}, {1}, {1,2},
{0,1,2}`` and the subset ``{0,1}``, whose opens come out as ``{}, {1}, {0,1}``, and a
one-point subspace.

**Correction to the previous section.**  The cut space's *set* does not need a new
operation: the power set's `from_predicate` names the complement of the region in one line,
so with `subspace` in place `X - int(region)` is constructible.  What the three surgery
methods still lack is only the collar: `IntegralAffineCollars.on`
(`integral_affine_collars.py:89`) is still a `pass` body, so every `affine_collars` argument
is unbuildable.  That is the next call to implement.

## 13. The collar is in: the surgery's arguments are now all constructible

`IntegralAffineCollars.on` (`integral_affine_collars.py:89`) was the last `pass` body among
the three surgery methods' argument builders.  It now selects the four data a collar is --
the affine piece, the face, a neighbourhood of the face, and an affine chart of that
neighbourhood -- refusing a piece that is not an integral-affine manifold, a face or
neighbourhood selected into another manifold, and a chart stated on something that is not
the neighbourhood.

One limit is stated in the docstring rather than papered over: an arrow of integral-affine
manifolds has no constructor in this tree (`IntegralAffineManifoldMor._element_constructor_`
is a `pass` body at `integral_affine_manifolds.py:71`), so a face cannot be selected into
the piece *as an affine object*; the selections are into the smooth manifold the piece adds
its structure to, which is where its faces live.

Test: `tests/schemes/test_the_integral_affine_collar_selection.sage`, both bodies pass
(2 passed, 0 failures) -- the retention of the four data on the plane's one-chart structure,
and the three refusals.

**State of the three surgery methods.**  `surgery(region_inclusion, replacement,
boundary_isomorphism, affine_collars)` now has every argument it names constructible: a
monomorphism of topological spaces, a singular integral-affine space (`on`, §11), an
isomorphism of topological spaces, and collars (here).  What remains is the body itself:
cut, using `subspace` (§12) on the complement named by `from_predicate`; glue, using the
coproduct (`topological_spaces.py:683`) and the coequalizer (`:680`); and read the singular
locus off the identified boundary.  That is the next piece of work, and it is construction
rather than a missing operation.

## 14. What the surgery body itself needs: an atlas morphism

§13 left the three methods as construction.  Writing `surgery` showed the next missing
call, and it is not topological: the regluing *is* an integral-affine map of the two collar
charts, so the result's atlas is built by restricting a chartwise affine map along the
boundary isomorphism.  That map cannot be constructed:

```
$ sage -c "... IntegralAffineAtlases().Mor(atlas, atlas)(Sets().Mor(plane, plane).identity(), {})"
atlas morphism: None
```

`IntegralAffineAtlases().Mor(...)(smooth_map, chartwise_affine_maps)` answers `None`:
`IntegralAffineAtlasMor._element_constructor_` is a `pass` body
(`integral_affine_atlases.py:48`), and so are the three element methods a regluing would
read it through -- `integral_affine_morphism` (`:39`), `smooth_atlas_morphism` (`:42`) and
`__mul__` (`:45`), which is what composing the cut's chart with the regluing and the
replacement's chart would need.

Without an arrow of integral-affine atlases the collars of §13 have no codomain object to
be compared in, so `surgery`, `symington_surgery` and `basis_triangle_surgery` cannot be
written past their argument checks: the operation they perform is that arrow.  The missing
call is the atlas morphism constructor, not a topological one.

## 15. The atlas morphism constructor needs a contract nobody has stated

§14 named the call.  Implementing it needs one thing that is not in the tree: what the
`chartwise_affine_maps` argument *is*.  It appears in exactly two places, both `pass` bodies
-- `integral_affine_atlases.py:26` and `integral_affine_stratified_atlases.py:39` -- and
there is no other reference to it anywhere in `src/` or `tests/`:

```
$ rg -n "IntegralAffineAtlasMor|IntegralAffineAtlases\(\)\.Mor|chartwise_affine" src tests
src/sage_extensions/categories/integral_affine_stratified_atlases.py:39,42,48,49,63
```

No caller, no docstring and no test says whether it is keyed by a chart, by a pair of
charts, or is a map of affine maps; and `integral_affine_morphism(source, target)` -- its
reader, `:39` -- does not constrain it either, being a `pass` body itself.  The constructor
`_element_constructor_` is four lines once that is decided (`self.element_class(self,
smooth_map, chartwise_affine_maps)`, with the two underlying-manifold checks), and the
three element methods follow from it; what cannot be written without a decision is the
contract the surgery's regluing is expressed in.

So the item is named once more, at the level that actually blocks it: **the keying and
meaning of an integral-affine atlas morphism's chartwise data is an open design decision of
the atlas layer**, and no issue here states it.

## 16. The atlas morphism constructor is in, and its keying was forced, not chosen

§15 called the keying of the chartwise data an open decision.  It is not: the reader's own
signature fixes it.  `integral_affine_morphism(source, target)` takes the two charts as two
arguments, so the retained data are indexed by the pair, and no other keying can answer that
call.  With that, the whole arrow is writable:

- `IntegralAffineAtlasMor._element_constructor_(smooth_map, chartwise_affine_maps)`
  (`integral_affine_atlases.py:48`) builds the arrow, refusing a smooth map whose endpoints
  are not the manifolds the two atlases are atlases of;
- `integral_affine_morphism(source, target)` (`:39`) answers the map of that pair, and
  refuses a pair the arrow is not affine in rather than answering an identity;
- `smooth_atlas_morphism` (`:42`) answers the smooth map the atlases are on;
- `__mul__` (`:45`) composes, keeping the endpoints and composing the chartwise maps
  through the middle chart;
- `identity()` composes the plane's identity with the model's identity at each chart's own
  pair.

Test: `tests/schemes/test_the_integral_affine_atlas_morphism.sage`, three bodies, 3 passed,
0 failures -- the identity's chartwise map, the composite of an arrow with itself, and the
refusal of a smooth map between other manifolds.

**That closes the last `pass` on the surgery's route that the surgery itself needs.**  A
regluing is now an arrow of integral-affine atlases: the cut's chart composed with the
chartwise affine identification of the collar charts and the replacement's chart.  What is
left for `surgery`, `symington_surgery` and `basis_triangle_surgery` is their bodies: cut
with `subspace` on the complement named by `from_predicate`, glue with the coproduct and the
coequalizer, read the singular locus off the identified boundary, and restrict the two
atlases along the regluing.

## 17. The surgery's result has no specimen: a real surface has no points

§16 left the three bodies as construction.  Writing `surgery` showed that the construction
cannot be *decided*, because its result cannot be built at all on this tree:

```
$ sage -c "from sage_extensions.categories.manifolds import SmoothManifolds; ...
           SmoothManifolds()(2, 'R^2')((1, 2))"
ValueError: cannot give a point of 2-dimensional smooth manifold R^2 by its coordinates:
            the manifold has no chart to read them in
```

A smooth manifold built by `SmoothManifolds()(dimension, name)` has no chart, so it has no
points.  Every step of a surgery needs them: the cut `X - int(region)` is a subspace, and
`TopologicalSpaces.subspace` (§12) is stated on a finite enumerated set of points; the
coequalizer of the coproduct (`topological_spaces.py:680`, `:683`) is computed on point
sets; and the singular locus of the result is the image of the identified boundary, which is
a set of points of the surface.  The integral-affine side is the same: an atlas records
chart domains and chart maps and never evaluates them, so a specimen can be *stated* without
points, but a surgery cannot be *run* without them.

So the three methods are named, once more and at the level that blocks them: **a point of a
smooth manifold**.  The failing expression is above; the owner is `categories/manifolds.py`,
whose manifolds are built without a chart and therefore without an element constructor for
their points.  The atlas test that this issue's vertex work rests on already records the
same limit for chart values ("a point of a real smooth manifold cannot be built in this
tree"), and landings since then -- including #97 -- have not removed it.

## 18. Where a manifold's points come from, and the call that is missing there

§17's failing expression is not the end of the chain: a manifold *does* have points when it
is placed under an atlas with charts (`manifolds.py`'s `point(coordinates, chart_label)`
reads a chart of the manifold).  The placing operation is what is missing:

```
$ sage -c "... SmoothManifolds().on(X, None)"
SmoothManifolds().on(space, atlas) -> None
```

`TopologicalManifolds.on(underlying_space, atlas)` is a `pass` body at
`manifolds.py:959`, and the `C^k` and smooth versions repeat it at `:1891` and `:1968`.  The
atlas side is ready -- `RealCkAtlases.on(topological_manifold, chart_domains,
chart_domain_inclusions, charts, overlap_inclusions, transition_maps)`
(`real_ck_atlases.py:130`) is implemented and returns the six selected data -- so a smooth
manifold with a chart exists exactly when those two are joined, and the joining operation is
the one that returns `None`.

That is the last link between this issue and the three surgery bodies: place a surface under
a chart atlas, and its points, its subspaces, the cut, the coproduct and the coequalizer all
follow from operations that are now implemented and tested here.

### Re-measured after the evening's landings

The two imports this issue needs besides the manifold placement were checked again at the
head of `main` after #97 and the landings that followed it:

```
categories.schemes.polytopes     ValueError: base must be a subring of this ring
manifolds                        OK
integral_affine_manifolds        OK
```

`polytopes` still constructs the exact real field at import, so `sterk` and
`Sterk.roots_18_2_0()` remain unreachable and the Sterk4-rank test remains unwritable,
while the manifold and integral-affine layers import and their four stubs closed here
(`SingularIntegralAffineSpaces.on`, `subspace`, `IntegralAffineCollars.on`, the atlas
morphism arrow) are exercised by tests that run.

## 19. What the missing placement has to supply, read off the manifold class

§18 named `TopologicalManifolds.on(underlying_space, atlas)` (`manifolds.py:959`, `pass`) as
the last link.  It is not a body that can be filled from outside, and this records why, so
that whoever owns the manifold layer does not have to re-derive it.

`Manifolds`' `ParentMethods.__init__` (`manifolds.py:1084`) takes exactly these data:
`engine_manifold` (the engine realization whose charts the atlas' charts are),
`manifold_dimension`, `manifold_name`, `manifold_structure`, `differentiability_degree`
(`None` for a topological manifold, `Infinity` for a smooth one), `manifold_field`,
`chart_index_set` and `chart_provider`.  `_retain_manifold_structure` (`:1118`) records all
eight and clears `_preamble_charts` and `_preamble_transitions`, which the atlas is what
fills.

So `on`'s job is to turn an exact space plus a chart atlas into those eight: the dimension
and the structure from the atlas, the chart index set from `chart_labels()`, the provider
from the atlas, and an engine realization *of the given space* -- which is the part that is
not a matter of copying data across, since every existing constructor builds the engine from
a dimension and a name (`_SageManifold(dimension, name, structure=...)`).  Filling it means
deciding what the engine realization of a space that already exists is, and that decision is
the manifold layer's, not this issue's.

Until it is made, `SmoothManifolds()(2, "R^2")` has no chart, its points raise
`cannot give a point of 2-dimensional smooth manifold R^2 by its coordinates: the manifold
has no chart to read them in`, and the three surgery bodies of this issue have no specimen.

## 20. State of the leaf, in one table

Everything this issue can decide from its own files is decided.  What is open is open on
operations in three other layers, each named by call and by file, and none of them is a
choice this issue can make.

| acceptance item | state | what carries it |
| --- | --- | --- |
| two polytope stubs implemented | met | `polytopes.py:2314`, `:2367` (#573, #582) |
| three surgery stubs implemented | open | bodies need `TopologicalManifolds.on` (`manifolds.py:959`, `pass`); its eight data and the one real decision are in §19 |
| the object a surgery returns | met | `SingularIntegralAffineSpaces.on`, §11, tested |
| the cut a surgery makes | met | `TopologicalSpaces.subspace`, §12, tested; the complement is `from_predicate`, §12 |
| the collars a surgery glues with | met | `IntegralAffineCollars.on`, §13, tested |
| the regluing arrow | met | `IntegralAffineAtlasMor`, §16, tested |
| Sterk2 closure-cone test | met | dimension 16, 65 rays, the two antipodal pairs, the stored lengths, §2, tested |
| Sterk4 ranks asserted in a test | open | ranks settled (12, 18, 2, 10, 2), §4; test needs `Sterk.roots_18_2_0()`, and `categories.schemes.polytopes` still constructs `ExactRealField()` at import |
| source questions settled mathematically | met | §2--§5 |
| the exploration uses only these operations | open | it is #260's deliverable |

Six `pass` bodies were implemented and tested on the way: `RationalPolyhedralCones.has_a_nonzero_point`
and `has_a_strictly_positive_point` (§1), `SingularIntegralAffineSpaces.on` (§11),
`TopologicalSpaces.subspace` (§12), `IntegralAffineCollars.on` (§13), and
`IntegralAffineAtlasMor`'s constructor with its four element methods (§16).

Every test named above had its body executed on this host with the session's
`from sage_extensions.all import *` replaced by the names the file uses; the pytest suite and
the test lint cannot start here, and the two specimen tests whose model is `RR.free_module`
(`test_the_singular_integral_affine_space_selection`, `test_the_integral_affine_collar_selection`)
ran with the rational field in the model's place, which decides the objects they assert and
not the model's base ring.
