# #581: a polytope's ingress admits a lattice point

Working head: `8e84152` (`main`), worktree `.scratch/w581`, runtime
`/sage/.venv/bin/python` (Sage 11.0.beta5) through `~/sage-image/run.sh -w /work`.

## The defect, measured at the parent

On the lane's square `conv{(±1,±1)}`, the vertex `-[0] - [1]` is a point of the
polytope, and the named operation says so, while the ordinary subset tests refuse
it:

| route | answer at `8e84152` |
| --- | --- |
| `square.contains_point(-[0] - [1])` | `True` |
| `square.rational_point(-[0] - [1])` | `-[0] - [1]` (the ambient point) |
| `-[0] - [1] in square` | `False` |
| `square(-[0] - [1])` | `ValueError: -[0] - [1] is not in Lattice Polygon of dimension 2 with 4 vertices` |

The refusal is the subset level's, and it happens before any predicate runs:
`SetSubobjectCategory.ParentMethods.__contains__` (`src/sage_extensions/categories/abstract_categories/arrow_categories.py:1886`)
asks `base.is_parent_of(member)` about the ambient space `M_QQ`, and
`M_QQ.is_parent_of(m)` is `False` for a point of `M`.  The element constructor is
`_ConditionSetEngine._element_constructor_`
(`src/sage_extensions/categories/sets/set_categories.py:4492`), which reads the
same refusal as the subset's `is_parent_of`.

The generic subset level cannot do the conversion: `M_QQ(m)` refuses a lattice
point as well (`TypeError: -[0] - [1] does not describe an element of Free module
on {[0], [1]} over Fraction Field of Integer Ring`).  The identification is not
the module's -- it is the inclusion `M -> M tensor QQ` that the **polytope**
states in `rational_point`.  So the ingress belongs to the polytope.

## The repair

`src/sage_extensions/categories/schemes/polytopes.py`, in `ConvexPolytopes.ParentMethods`:

| line | what |
| --- | --- |
| 2603 | `_ambient_point_or_none`: the candidate read by `rational_point`; only the ambient space's own refusal is reported, as `None` |
| 2618 | `__contains__`: `contains_point` on that point; a value that is no point of the ambient space is not a member |
| 2631 | `is_parent_of = __contains__`: one function, so the two names cannot drift |
| 2633 | `_element_constructor_`: returns the ambient point, refuses a point outside the polytope and a value that is no point of the ambient space, and retains the admitted member through the inherited subset engine |

`__contains__` and `_element_constructor_` sit earlier in the polytope object's
MRO than `SetSubobjectCategory.ParentMethods` and `_ConditionSetEngine` (printed
MRO, in this order: `ConvexPolytopes.{Polygon,Integral,}ParentMethods`,
`_PolytopeFaceStructureMethods`, `SetSubobjectCategory.ParentMethods`,
`SliceCategory.ParentMethods`, `_ConditionSetEngine`, `Parent`), so the polytope
states these two and the subset level keeps the rest (`inclusion`, `<=`, union,
intersection, difference).

## Acceptance, item by item

1. **The ingress runs the same conversion as `contains_point`.** `contains_point`
   (`polytopes.py:2593`) reads its argument through `_engine_coordinates`
   (`:1719`) -> `rational_point` (`:1702`) -> `_ambient_point_on` (`:108`).  The
   ingress now reads it through `rational_point` (`:2603`, `:2614`, `:2628`, `:2642`).
   Same function, one conversion.
2. **`v in P`, `P(v)` and `P.contains_point(v)` agree on the three specimens, at
   a lattice point, a rational point and a point outside.** Measured in one
   process at the repaired head:

   | specimen | lattice vertex | rational point on a chord | point beyond every vertex |
   | --- | --- | --- | --- |
   | square | `in`/`contains_point`/`P(v)` all True/True/`-[0] - [1]` | True/True/`-(4)/(4)*[0]` | False/False/`ValueError` |
   | irregular quadrangle | True/True/`0` | True/True/`(2)/(4)*[1]` | False/False/`ValueError` |
   | stored Sterk2 hull (17 vertices) | True/True/`-24*[0]` | True/True/`-(96)/(4)*[0] + (2)/(4)*[1]` | False/False/`ValueError` |

   The same agreement holds at a vertex of every face of each specimen: 9 faces
   of the square, 9 of the quadrangle, 35 of the Sterk2 hull, 0 disagreements.
   A lattice point is the ambient point at its coordinates, so `P(v)` answers a
   point of `M tensor QQ`; the outside point is refused by both routes.

   Exhaustively over the lattice of each specimen's bounding box: 9 points for
   the square, 12 for the quadrangle, 675 for the Sterk2 hull.  `v in P` and
   `P.contains_point(v)` agree at every one of them, and `contains_point` admits
   exactly the polytope's own integral points (9 of 9, 6 of 12, 433 of 675); 0
   disagreements.
3. **The regression test asserts the agreement, not the internal route.**
   `tests/schemes/test_polytope_ingress_at_a_lattice_point.sage` asserts
   `(point in P) is member`, `P.contains_point(point) is member`, and
   `P(point) == P.rational_point(point)` when it is a member (or a `ValueError`
   when it is not), where `member` is placed by the mathematics of the specimen.
   It names no private operation and reads no internal datum.

## Cost

Per call, 200 calls each, this VM at load 15: `in` 0.873 ms (square) / 1.320 ms
(Sterk2), `contains_point` 1.245 / 1.314 ms, `P(v)` 1.942 / 2.117 ms.  The ingress
reads the candidate twice (once itself, once inside `contains_point`); that is
1 conversion, well inside a call that already runs the exact polyhedron.

## What was run, and what was not

* `tests/schemes/test_polytope_ingress_at_a_lattice_point.sage` alone:
  2 failed, 2 passed in 8.14 s at the parent `8e84152` (the value
  disagreement, not an `AttributeError`); 4 passed in 3.55 s at the repair.
  The suite's time-gate report printed `session star import took 3.01 s; the
  measured ceiling is 3 s` -- the star import of the session, shared by every
  file, not this change.
* `test_unplaced_polytope_structure`, `test_placed_polytope_structure`,
  `test_polytopes`, `test_lattice_polygon_invariants`: 23 passed, 1 failed in
  61.75 s -- `test_dodecahedron_has_coxeter_diagram_h3_and_symmetry_group_of_order_120`
  (`RegularPolytopes` has no `f_vector` at `8e84152`).
* `test_polytope_face_automorphisms`, `test_placed_polytope_face_automorphisms`,
  `test_polytope_face_automorphism_owner`, `test_standard_triangle`,
  `test_group_scheme_actions`, `test_hyperbolic_space`: 25 passed, 7 failed in
  82.09 s at the repair.  In a clean worktree at the parent `8e84152` the same
  seven ids fail in 257.57 s (7 failed, 25 passed) -- the same set, so the change
  is not the cause:
  `test_the_ehrhart_polynomial_of_the_triangle`,
  `test_the_toric_variety_of_the_triangle_is_the_projective_plane`,
  `test_the_group_laws_of_ga_and_gm_are_addition_and_multiplication`,
  `test_mu2_is_etale_over_qq_and_nonreduced_over_gf2`,
  `test_positive_cone_component_through_a_timelike_vector_separates_the_two_sheets`,
  `test_hyperbolic_space_identifies_positive_multiples_of_a_timelike_vector`,
  `test_projectivized_isotropic_cone_is_the_whole_hyperbolic_line_with_two_ideal_ends`.
* The subset operations of the repaired object were probed after the change and
  answer as before: `is_parent_of('x')` False, `'x' in P` False, `P('x')` /
  `P(5)` / `P(None)` a `ValueError`, `<=` and `==` between two polygons decided,
  `intersection` an object of `Subobjects(ambient)`, `an_element`, `is_empty`,
  `n_integral_points`, `boundary_integral_points`, `interior_contains_point`.
* Not run here: the whole suite; the `ast-grep` gates (the tool is not installed
  on this host); CI.
* **Out of this change:** the placed wrapper (`LatticePolytopesIn(...).on(...)`)
  is an object of `Objects()`, not a subset, and has no `contains_point`; its
  `underlying_polytope()` is the polytope repaired here and is one of the
  specimens above.  Giving the placed object these three operations would be new
  operations on another owner, not this issue's ingress.

## Closing comment (cannot be posted: the connected GitHub repository is read for
issues and pushed to, and offers no issue comment)

> `v in P`, `P(v)` and `P.contains_point(v)` are now one answer on a lattice
> polytope.  The ingress is stated at `ConvexPolytopes.ParentMethods`
> (`src/sage_extensions/categories/schemes/polytopes.py:2603`, `:2618`, `:2633`):
> it reads the candidate through `rational_point`, the conversion
> `contains_point` already used, so a lattice point is admitted as the ambient
> point at its coordinates.  The regression test
> `tests/schemes/test_polytope_ingress_at_a_lattice_point.sage` asserts the three
> answers on the square, the irregular quadrangle and the stored Sterk2 hull, at
> a lattice point, a rational point and a point outside, and at a vertex of every
> face.  Landed on `main` as a `test:` commit carrying the failing file and a `fix:` commit carrying the repair.
