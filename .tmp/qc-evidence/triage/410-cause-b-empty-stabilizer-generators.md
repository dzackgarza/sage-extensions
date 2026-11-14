A finite G-set stabilizer over a trivially generated group raises IndexError

Status: repaired on `main` at `852a901` (`libgap.Group(engine_generators,
libgap.Identity(<engine image of group.one()>))`, which accepts an empty generating
family).  This body is the record of the defect and its red test and is not to be filed.

When this closes, asking for the stabilizer of a point of a `G`-set whose acting group has an
empty generating family returns the trivial subgroup, so every stabilizer query that bottoms out
at a trivial acting group answers instead of raising `IndexError: index out of range`. A user who
asks `O(<1> + <-2>).vector_stabilizer_generators(e)` today gets an `IndexError` from the GAP
plumbing; afterwards they get the stabilizer they asked for.

## Failing tests (red at `5f5fc25`, the current `main`)

```
tests/lattices/test_definite.sage::test_norm_one_vectors_of_x2_minus_2y2_form_one_orbit
```

This cause also masks `tests/lattices/test_definite.sage::test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so`,
which falls back to its own cause (filed as cause H) once this one is repaired.

## Error

```
src/sage_extensions/categories/group/g_sets.py:913: in _named_stabilizer
    libgap.Group(engine_generators, libgap.Identity(engine_generators[0])),
E   IndexError: index out of range.
```

The route is `O(L).vector_stabilizer_generators(e)` -> `_marking_stabilizer_generators` ->
`rational_integral_stabilizers.finite_stabilizer()` ->
`permutation_representation().codomain().stabilizer(point)` -> `_named_stabilizer`, where
`generators = tuple(group.group_generators())` is empty.

## Introducing commit

`bbb6608` (D. Zack Garza, 2026-11-14), "perf: finite G-set stabilizers by GAP; integer point
lookup by engine key", which introduced the GAP stabilizer route and its
`libgap.Identity(engine_generators[0])`.

Evidence in the image (`-o addopts=`):

| commit | `test_norm_one_vectors_of_x2_minus_2y2_form_one_orbit` |
| --- | --- |
| `bbb6608^` | passed |
| `bbb6608` | failed, `IndexError: index out of range.` |

## Scope

`src/sage_extensions/categories/group/g_sets.py` `_named_stabilizer` only.

## Repair

An empty generating family is the trivial group, whose point stabilizers are trivial: the method
returns `group.subgroup((group.one(),))` before building the GAP homomorphism. The id above is
the regression.
