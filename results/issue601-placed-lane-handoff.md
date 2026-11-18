# The hyperbolic placed lane's automorphism search: what is measured, and what it needs

#601's acceptance is met at `manifolds.py`/`hyperbolic_geometry.py`. Its body names
one consumer, "#580's hyperbolic lane", and that lane's geometric automorphism
search is the one thing still open. It is not this issue's code: the failure is in
`schemes/polytopes.py`, which the #580 chat has been landing into, and this note is
the handoff rather than a second implementation.

## What works

Measured on `656791f`, Sage 11.0.beta5 in the pinned image, at a hyperbolic
triangle of `I_{1,2}` with vertices `(2,1,0), (2,0,1), (2,1,1)`:

```
core (a lattice polygon)     : Lattice Polygon of dimension 2 with 3 vertices
placed by .on(...)           : built, ambient_space() is the hyperbolic space: True
placed.Aut()                 : a Mor of HyperbolicGeodesicPolytopesIn
placed.Aut().cardinality()   : 6
tuple(placed.Aut())          : TypeError: 2*[0] + [2] does not describe an element of
                               Free module on {[0], [1], [2]} over Real Field
                             at framed_free_modules.py:425
```

So a hyperbolic geodesic polygon is placeable, and the geometric automorphism Mor
exists. Two things are wrong below that.

## What is wrong, with its line

1. **The search is affine.** `polytopes.py:931` `_ambient_map_of_positions` builds an
   ambient map through `RealAffineSpaces()` (`:919`) with
   `space.underlying_affine_space()` (`:906`, `:949`) and
   `affine_space.translation_action()` (`:979`). A hyperboloid model has none of
   those three, and none of them is honest there: a hyperbolic isometry is linear on
   the Lorentz space, not affine on the space. Publishing them on
   `HyperbolicSpaces` would be a proxy, not an operation.
2. **Element construction stops earlier.** `framed_free_modules.py:423-425` refuses a
   foreign-parented element, and the vertex-position route hands it a point from a
   module with the same labels but a different parent. Not a coefficient-ring
   problem: `RR.free_module((0,1,2))` accepts `{0:2, 2:1}`, `(2,0,1)` and the same
   over `RR`, all giving `2*[0] + [2]`.
3. **The count is not the geometric group.** `b` on the specimen's vertex pairs is
   `4, 3, 3`: the triangle is isoceles, so the isometries preserving it have order
   **2**. `Aut().cardinality()` answers **6**, the abstract group of its three
   vertices. A specimen whose isometry group is known must answer `2`.

## What the search needs

For a non-affine ambient, `_ambient_map_of_positions` should solve the vertex
correspondence linearly in `L ⊗ RR` instead of affinely: the isometry `g` with
`g(v_i) = v_{sigma(i)}`, three spanning vertices determining it, and then ask
`space.is_an_isometry(g)` — which already reads exactly that datum
(`hyperbolic_geometry.py:735`, through the arrow's `lattice_isometry`). On the
specimen above `g` is integral (`lattice.reflection` of a root swaps the equal
sides), so #601's arrow constructor admits it and the group comes out `2`.

## Ownership

`schemes/polytopes.py` is #580's, whose chat landed the two prerequisites for this
very item — `622fd8a` (the hyperbolic isometry decision, 05:25) and `80e95fb`
(`point_set`, 05:38) — and the Euclidean and spherical arms before them
(`74e216e`, `4b89c46`, `418044f`). The file itself is idle since 04:25 while 75
commits landed elsewhere. Whoever holds #580's arm should take this; it is one
commit in their search and a test with the specimen above.
