# #345: the divided-class line route finds its classes at divisor 1

**Result: `primitive_orbit_series()` returns on card `026E` (`U + D4(-1) + A1(-1)`,
rank 7, signature (1, 6)) and on card `0016` (`U`, rank 2, signature (1, 1)), and every term
equals the card's own `integral.primitive_orbits` row.** The refusal was a gap in the
divided-class construction, not a case of the mathematics: the classes are realized at divisor
1 by the hyperbolic basis vector, and the search did not look there.

## The reproduction, on `main` at `8b54761`

Through the public call, with each lattice built from its card's `gram_tensor`:

```
=== 026E: U + D4(-1) + A1(-1), rank 7, signature [1, 6]
  REFUSED in 70.7s: ValueError: the divided classes of the line orbit of Integral lattice of
  rank 1 and signature (0, 0) in Integral lattice of rank 7 and signature (1, 6) are not all
  realized at divisor 1: 1 of the 1 classes have no primitive isotropic vector there, the
  first being 4*[0] + 3*[1] + 4*[2] + 4*[6]. …
=== 0016: U, rank 2, signature [1, 1]
  REFUSED in 9.4s: ValueError: … the first being -[1]. …
```

The frames are the ones the issue names:
`lattice_orbit_invariants.py:143 _primitive_isotropic_line_series` →
`predicate_subgroups.py:507 isotropic_orbit_representatives` →
`orthogonal_quotients.py:2277 _subgroup_isotropic_orbit_representatives` →
`orthogonal_quotients.py:2234 _line_orbit_from_divided_classes`.

## The cause

`Lattices.ParentMethods.isotropic_lines_by_divided_class(d)` enumerates the residues of `L/dL`
and, for a residue `(a mod d, b mod d, w mod d)` in a scaled hyperbolic pair `e, f` with
`b(e,f) = h`, solves

    q(v) = 2 h a b + q(w) = 0,   i.e.   a b = -q(w)/(2h),

over the integral pairs `(a, b)` compatible with the residue.  Its pair enumeration was

```
def divisor_pairs(value):
    if value == 0:
        return ((0, 0),)
```

and `(0, 0)` is the zero vector, which the construction then rejects as not primitive.  At
divisor 1 the residue is trivial, so `w = 0`, `q(w) = 0`, and every candidate was the zero
vector: **the loop could not produce any primitive isotropic vector at divisor 1, on any
lattice**.  Measured on `U` itself:

```
=== 0016: U, rank 2
  basis 0: q=0 div=1 class=[1] primitive=True
  basis 1: q=0 div=1 class=[0] primitive=True
  representative class: -[1]
    basis 0: class [1] equal to the representative's: True
    basis 1: class [0] equal to the representative's: True
    by the basis-0 class at divisor 1: {}
  whole map at divisor 1: {}
```

`e_0` has `div 1`, is primitive and isotropic, and its divided class *is* the representative's
class — and the construction returned no vector for it.  On `026E` the same: the representative's
class `4*[0] + 3*[1] + 4*[2] + 4*[6]` equals `[1]`, the class of `e_0`, in the module with
invariant factors `[2, 2, 2]`.

So the class is **not** empty at divisor 1 and there is nothing to cite as an emptiness
statement: the equation `a b = 0` has the solutions `(a, 0)` and `(0, b)`, and `e` realizes the
class through `(1, 0)`.

## The repair, at the owner

`isotropic_lines_by_divided_class` now decides the equation in both cases
(`src/sage_extensions/categories/lattices.py`):

* a nonzero `q(w)` keeps the divisor-pair enumeration, unchanged;
* `q(w) = 0` is decided by `vanishing_pairs(left_residue, right_residue)`: `(a, 0)` over the
  nonzero members of `a`'s class when the residue of `b` is zero, and `(0, b)` likewise.  The
  members tried are the class's smallest and its neighbours one divisor step away
  (`class_steps`), because divisibility exactly `d` is a condition on the vector and not a
  congruence on its coefficients; every candidate still passes the four checks the
  construction already made (`q(v) = 0`, primitive, `b(v, L) = d Z`, class of the residue), so
  a candidate this list does not contain can only make a class report absent, never a wrong
  vector.

The `(0, 0)` pair is gone: it could only produce the zero vector, which no check ever
accepted.  No refusal was widened, none was caught, and the budget guard is untouched.

`isotropic_lifts.py` was not touched, so nothing of `fzdd`'s #286 work is in this diff; the two
files that changed are `categories/lattices.py` and the card digest.

## Red

At `dd9e4bd4` (`main` with the digest section and the test, before the repair):

```
F.                                                                       [100%]
E   ValueError: the divided classes of the line orbit of Integral lattice of rank 1 and
    signature (0, 0) in Integral lattice of rank 2 and signature (1, 1) are not all realized
    at divisor 1: 1 of the 1 classes have no primitive isotropic vector there, the first
    being -[1].
1 failed, 1 passed in 3.00s
```

The structural test — the card's rank, signature, determinant and Gram are the lattice's —
passes, so the failure is the call and not the specimen.

## Green

```
..                                                                       [100%]
tests/lattices/test_primitive_orbit_series_on_the_catalogued_lattices.sage::
  test_the_series_returns_on_both_catalogued_lattices: 47.39 s > 20 s
2 passed in 47.83s
```

## Regression surface

| module | result |
| --- | --- |
| `test_primitive_orbit_series_on_indefinite_lattices.sage` (the `T_Co` line route, constant term 327.76 s) + the new module | **4 passed in 427.78s** |
| `test_enriques_plane_orbits_by_divided_classes.sage` (the divided-class plane route) | **7 passed in 217.60s** |
| `test_the_divided_class_construction.sage` (the owner's own module) | **5 passed** |
| `test_characteristic_discriminant_elements_archive.sage` | 1 passed, **1 pre-existing failure** |

That failure, `test_diagonal_two_minus_two_has_a_characteristic_divided_class`
(`assert divided_class.is_characteristic()` is `False`), reproduces at `8b54761` with no change
of this unit in the tree — `1 failed, 1 passed in 1.56s` in a detached worktree of that commit —
so it belongs to `is_characteristic`, not to this repair, and is reported rather than fixed
here.

The test lint over the new module: `1 files, 0 findings`.  It also reports three pre-existing
`TL07` findings in `test_the_divided_class_construction.sage` (lines 129--130), which is why
that module was run without the lint plugin.

## Not done

* `just test` over the whole suite was not run in this unit: the shared VM was carrying other
  chats' jobs (load average 7--14 on four cores) and a full run is hours.  What was run, and
  what it returned, is the table above; the modules named are the ones that reach
  `isotropic_lines_by_divided_class`.
* The three `TL07` findings in `test_the_divided_class_construction.sage` are left as they
  are — another issue's test, and not this one's subject.
