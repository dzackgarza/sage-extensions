# Issue to file under #518: `ConvexPolytopes.from_halfspaces` reads its ambient dimension off the halfspaces

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body under #518. No repair is made here: this
round repaired the cone category's crossings (`polyhedral_cones.py`, #544), and the
polytope category is a different owner.

## Title

`from_halfspaces` of an empty family is a point in `QQ^0`, so the unbounded region is
never refused as unbounded

## Body

`ConvexPolytopes.from_halfspaces`
(`src/sage_extensions/categories/schemes/polytopes.py:591`) builds

```python
polyhedron = Polyhedron(ieqs=engine_rows, base_ring=SageQQ)
assert polyhedron.is_compact(), (
    f"the halfspaces {halfspaces} cut out an unbounded region, so they do not define a polytope"
)
```

The docstring promises that "a polytope is bounded, and an unbounded intersection is
refused rather than truncated". `Polyhedron` reads its ambient dimension off the rows,
so an empty family of halfspaces - the region `L tensor QQ` itself, of rank `n` and
unbounded - is handed no row and becomes `A 0-dimensional polyhedron in QQ^0 defined as
the convex hull of 1 vertex`, which is compact: the refusal never fires for exactly the
case it is written for. Measured 2026-11-16 in the adopted runtime (SageMath 11.0.beta5,
Python 3.14) on `ConvexPolytopes(ZZ.free_module(2))`:

```
square, four halfspaces: Lattice Polygon of dimension 2 with 4 vertices, 0.03 s
one halfspace:           AssertionError: the halfspaces ((1, (1, 0)),) cut out an
                         unbounded region, so they do not define a polytope, 0.00 s
no halfspace:            AssertionError: the vertices have 0 coordinates, but the
                         lattice Free module on {[0], [1]} over Integer Ring has rank
                         2, 0.00 s
```

So the empty family fails in a later assertion about vertex coordinates rather than in
the unboundedness check, and the message names the vertices, not the region the caller
stated. The dimension check is not the guard the docstring describes: it is reached only
because the engine was never told the rank.

The engine's demand is the TRAPS.md row "Sage's `Polyhedron` reads its ambient dimension
off the H-representation rows"; the cone category states it (`polyhedral_cones.py`,
`ambient_dim=len(labels)`), and this crossing does not.

## Repair

State the ambient dimension where the rows are built: the rows are written in the
coordinates of `self.ambient_lattice()`, so `ambient_dim=len(labels)` (the length of
each row minus one) with `labels = tuple(self.ambient_lattice().module_generating_set())`.
Then the empty family is the whole plane and `is_compact()` refuses it as unbounded,
which is the answer the docstring states. The test of the empty family states that
refusal, beside the test that already refuses one halfspace.
