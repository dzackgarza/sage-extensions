# Issue to file: `DiscriminantClass.is_characteristic` answers `False` for every class of `A_{T_Co}`

**Retracted: the defect this body reports was repaired before the body was filed.** The
quoted line is not the code. `is_characteristic` compared the owned value lifts against
**Sage's** integer ring only until `ef8fb06` (#348, 2026-11-11), which asks the membership
of the module's own base ring; that commit is an ancestor of the main branch this body was
filed against four days later. Against the owned integers the lifts are members, including
the unreduced representative `(0)/(4)` that a mixed class produces, and against the
engine's `ZZ` every owned value element answers `False`, `0` included -- which is what the
`in ZZ: False` line below measures, in a probe that never called the method.

Measured at `897e7f7` on the specimen below: `[h/2].is_characteristic()` is `True` and
`zero.is_characteristic()` is `False`, the second because `q([h/2]) - b([h/2], 0) = 1/2`.
An independent pass over all 2048 classes, built from the gram data on the 11 generators
with `q(x+y) = q(x) + q(y) + 2b(x,y)`, finds 0 non-integral differences for `[h/2]` and
1024 for the zero class, so the method's two answers are the form's. The cost is the
surviving defect: 145.7 s for the first call and 113.2 s for the second, 76.7 s of it
enumerating the classes.

The consequence drawn below does not hold on this specimen either. `b` is nondegenerate on
`A_{T_Co}`, so `[h/2]` is the only characteristic class, and its value `q([h/2]) = 1/2` is
not one a divided isotropic class can take: for a primitive isotropic `v` of divisibility 2
the class `[v/2]` has `q([v/2]) = (v,v)/4 = 0`. Measured: `get_isotropic_type(ep)` on
`T_Co` answers `Even ordinary` (99.86 s), which is the correct answer, and the same
classification answers `Even characteristic` on the lattice
`tests/lattices/test_isotropic_type_archive.sage` names for it.

`TRAPS.md` and `results/issue286-tco-run.md` carry the same correction.

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body. `repo:dzackgarza/sage-extensions is:issue
is_characteristic` returns 0 hits, so no open issue holds it.

## Title

`is_characteristic` compares owned value lifts against `ZZ`, so it is `False` for every class of an even 2-elementary discriminant form

## Body

`DiscriminantClass.is_characteristic`
(`src/sage_extensions/categories/modules/framed/formed/discriminant_modules.py:503`)
decides whether a class `v` satisfies `q(x) - b(x, v) in ZZ` for every `x` by evaluating

```python
parent.q(element).lift() - parent.b(element, self).lift() in SageZZ
```

On `A_{T_Co}` for `T_Co = <2> + E(2)`, `E = E8 + U` (rank 11, signature (2, 9),
determinant -2048, even, `A = (Z/2)^11`), the two `.lift()` values are
`OwnedJoinCategory.element_class` instances -- the owned value elements -- and `in ZZ` is
`False` for them even when the value is `0`. Measured on the class `[h/2] =
divided_discriminant_class(h)` and on the zero class:

```
x = zero: (0, 0, 0)          q.lift(), b.lift(), difference
  types: ('OwnedJoinCategory.element_class', 'OwnedJoinCategory.element_class')
  difference in ZZ: False
```

so the method answers `False` for **all 2048 classes**, including the zero class and
classes that are characteristic. It is not a statement about the form: the condition
holds for `[h/2]`, whose failing-summand check is `q(w) - b(w,w) = 1/2 - 1/2 = 0`,
`q(u1+u2) - b(u1+u2,w) = 1 - 0 = 1`, and `q(x) - b(x,w) = -k` for `x = y/2` in
`A_{E8(2)}`.

## Why it matters beyond this specimen

`Lattices.ParentMethods` uses the method to classify a primitive isotropic vector of an
even 2-elementary lattice (`lattices.py:5753`): every vector of divisibility 2 is
reported `"Even ordinary"`, and none `"Even characteristic"`, on any lattice whose value
elements behave as they do here. `T_Co` is such a lattice, so the classification is wrong
exactly on the specimen `#286` runs on.

## Acceptance

`is_characteristic` decides `q(x) - b(x, v) in ZZ` exactly on the form's value modules --
comparing the two values in one value module rather than comparing owned lifts with
`ZZ` -- and a test states a class that is characteristic and a class that is not, on a
form where the two differ. `T_Co`'s `[h/2]` is one specimen of each statement's shape:
characteristic, while the library currently answers `False` for it.

## Evidence

`.tmp/p286-probe6.log` (the four classes above, their types and the `in ZZ` answer);
`.tmp/p286-probe1.log` (`q([h/2]) = 1/2`, `b` values), both on the adopted runtime with
`bash .scratch/issue315_launch.sh`.
