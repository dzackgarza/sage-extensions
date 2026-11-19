# The orthogonal group of a half-integral discriminant form fails on an elementary one

The orthogonal group of the discriminant form of the rank-three even lattice
`[[-6, 2, 2], [2, -2, 0], [2, 0, -2]]` — the complement of a root in `D4`, of
determinant `-8` — raises

```
AssertionError: the complement of the half-integral direction must be its orthogonal complement
```

from `src/sage_extensions/categories/modules/framed/formed/torsion_form_modules.py:3170`
in `_engine_two_primary_odd_orthogonal_generators`, called from
`torsion_form_modules.py:3055 _engine_orthogonal_group`.  The group asked for is
the orthogonal group of a form of order 8 with invariant factors `(2, 2, 2)`,
i.e. an elementary two-group, so a "half-integral direction" is not what this
form has: whatever the engine picks as that direction, its orthogonal complement
does not come out as the code claims.

Three entry points raise, and one works, on the same lattice (`C`):

| call | result |
| --- | --- |
| `C.Aut().group_generators()` | 3 generators, 0.27 s |
| `C.discriminant_quadratic_form().orthogonal_group()` | the assertion, 0.10 s |
| the same, `.group_generators()` | the assertion, 0.00 s |
| `C.discriminant_image()` | the assertion, 0.02 s |

So the failure is in the discriminant-form side only: the lattice's own
isometry group is fine, and `discriminant_image` fails because it builds the
image inside the same orthogonal group.

## Why it matters

`sage_extensions#279`'s `vectors_of_square_with_complement` collapses glue
classes by `rho_C(O(C))`.  For a definite `C` that image is computed from
`C.discriminant_image()`, which is exactly what fails here, so the rank-three
definite control that would exercise the collapse itself — `D4` with the
complement above, four candidate glue classes, one orbit — cannot be run.  The
rank-two specimen (`A3`, complement of determinant 8, invariant factors
`(2, 4)`) works and is in
`tests/lattices/test_vectors_of_square_with_complement.sage`.

## Reproduce

```
sage: C = Lattices(ZZ)([[-6, 2, 2], [2, -2, 0], [2, 0, -2]])
sage: C.discriminant_quadratic_form().orthogonal_group()
```

Measured on the adopted runtime at tree `69469e7`, gates off
(`.tmp/probe-g.log` in the project's checkout); the probe also reaches the same
failure through the `orthogonal_complement` of a root in `D4`.

## How to file

This project's GitHub connection reads issues and pushes commits but cannot
create one, so this body is the draft.  To file it:

```
gh issue create --repo dzackgarza/sage-extensions \
  --title "The orthogonal group of a half-integral discriminant form fails on an elementary one" \
  --body-file results/issue-body-the-discriminant-orthogonal-group-of-a-half-integral-form.md
```
