An owned ring element's division recurses, and the definite metric invariants die on it

Status: repaired on `main`.  The division was repaired through `e9b6c2c`, `4c09c87`,
`4b958ef` and `b3c7ca3`; the division's further work belongs to #500, taken by another
chat, so this body is the record of the defect and its red tests and is not to be filed.

When this closes, `L.packing_radius()`, `L.center_density()` and every other definite-lattice
invariant that divides a length by an integer return their value for a lattice over the owned
reals, and `RR(1) / RR(2)` is the field division it is named after instead of a
`RecursionError`. A user who asks a definite lattice for its packing radius today gets a stack
overflow out of `Modules.ElementMethods.__truediv__`; afterwards they get `1/2` as an exact
owned real.

## Failing tests (red at `5f5fc25`, the current `main`)

```
tests/lattices/test_definite.sage::test_square_lattice_minimum_theta_and_packing_radius
tests/lattices/test_definite.sage::test_exact_cvp_babai_minima_and_voronoi_geometry_on_square_lattice
tests/lattices/test_definite_metric_invariants_archive.sage::test_square_lattice_metric_invariants_are_exact
tests/lattices/test_definite_metric_invariants_archive.sage::test_a2_invariants_see_the_nonorthogonal_hexagonal_geometry
```

## Error

```
src/sage_extensions/categories/definite_lattices.py:1206: in _packing_radius
    return RR(_engine_element(lattice.base_ring(), metric_minimum)).sqrt() / 2
src/sage_extensions/categories/modules/pure/modules.py:1704: in __truediv__
    return self.parent().scalar_multiple(ring.one() / ring(scalar), self)
E   RecursionError: maximum recursion depth exceeded
```

`center_density` reaches the same frame through `packing_radius`, and the recursion is not
specific to lattices: `RR(1) / RR(2)` and `~RR(2)` recurse in the same method, because a ring is
a module over itself and the method's own body `ring.one() / ring(scalar)` re-enters it on the
same parent.

## Introducing commit

`e4bd95d` (Zack Garza, 2026-11-06), "fix: a module element divides by a unit of its scalar ring
(#150)", which added `Modules.ElementMethods.__truediv__`.

Evidence in the image (`-o addopts=`, one pytest process per row):

| commit | `test_square_lattice_minimum_theta_and_packing_radius` |
| --- | --- |
| `e4bd95d^` | passed (`1 failed, 1 passed`: the second id was red for an older cause) |
| `e4bd95d` | failed, `RecursionError` (`2 failed`) |

The archive file's two ids were already red at `e4bd95d^` for an unrelated defect
(`'>' not supported between instances of 'OwnedJoinCategory.element_class'`), so the recursion
masks an older failure there; the first two ids are the clean flip.

## Scope

`src/sage_extensions/categories/modules/pure/modules.py` only. Every consumer of `/` on an owned
ring element is affected, not only the definite-lattice invariants.

## Repair

At the module owner: an element whose parent *is* its base ring divides by the ring's own
`_div_`; only a genuine scalar action takes the `scalar_multiple` route. The four ids above are
the regression.
