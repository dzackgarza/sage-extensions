The SO isotropic orbit route refuses an index-2 character image it cannot certify

When this closes, `U.SO().isotropic_orbit_representatives(1)` and the other isotropic orbits of a
special orthogonal group return their orbits: `SO(U) = {+-1}` acts on the two isotropic lines `Ze`
and `Zf` with two orbits. Today the call refuses, because the exact image of the rank-one
stabilizer's character has order at least 1 while the stabilizer of its divided discriminant data
has order 2, and no exhibited stabilizer element closes the index, so the route cannot certify the
image it computes. A user gets an `ArithmeticError` naming the index instead of the orbits.

## Failing tests (red at `c8a3cedb`, the current `main`)

```
tests/lattices/test_definite.sage::test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so
```

## Error

```
src/sage_extensions/categories/orthogonal_quotients.py:1626: in exact_isotropic_stabilizer_generators
    raise ArithmeticError(
E   ArithmeticError: the stabilizer of Integral lattice of rank 1 and signature (0, 0) in Orthogonal group
    O(Integral lattice of rank 2 and signature (1, 1)) has character image of order at least 1, and the
    stabilizer of its divided discriminant data has order 2; no exhibited stabilizer element closes the
    index 2, so the exact image chi(Stab) is not certified
```

## Introducing commit

`6a93efe` (D. Zack Garza, 2026-11-12), "fix: certify the exact character image of isotropic flag
stabilizers", which replaced an uncertified image by this refusal.

Evidence in the image (`-o addopts=`):

| commit | `test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so` |
| --- | --- |
| `6a93efe^` | passed |
| `6a93efe` | failed, `ArithmeticError` at `orthogonal_quotients.py` |

Between `6a93efe` and `bbb6608` the test failed on this refusal; `bbb6608` then replaced the
failure with the `IndexError` of the empty G-set stabilizer (cause B), so this cause is visible
again only after cause B is repaired.

## Scope

The certification of `chi(Stab)` in `orthogonal_quotients.py`
(`exact_isotropic_stabilizer_generators`): the repair is to exhibit the stabilizer element that
closes the index, for every rank-one definite complement and not only for `U`.
