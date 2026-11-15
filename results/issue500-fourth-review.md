# The fourth review of #500: one pairing for the dual's two shapes, the language's refusal, and the finite axiom in the placement

The review of `af3edeec78`, `ef39a9bfbb`, `b5cfd57f77` and `1b8358c261` made four
claims.  Each is checked below against the tree at `5f17b92fe7`, then answered.
The subject of #500 does not change: a ring element's `/` is the ring's own
quotient $a b^{-1}$, owned once at `OwnedRings` with `_div_` at the realization,
and the rebuild rule `refine._final_category_operations` moves no other operation
because of it.  What follows is the collateral the rebuild touches.

## 1. `order_ideal` repeated `dual_module`'s split and read framed coordinates

**Claim, and it holds.**  `Modules.ElementMethods.order_ideal` matched
`module._dual_product_construction()` with a `None` case (`STY-158`) and thereby
repeated the shape split `dual_module` makes (`STY-107`).  Its product branch
read `framing_morphism().lift(self)`, `module_generating_set()` and the framing
source parent's protected `_selected_module_coefficients` inside general
`Modules` (`OWN-05`, `ARC-15`, `CAT-05`), re-deriving the coordinate reading of
`FramedFreeModules.ElementMethods.order_ideal` (`STY-54`).  The module level is
the level that answers for an element of $\mathbf{Z}[x]$: the category order of
that join puts `Modules` first and `_final_category_operations` keeps its method,
so the framed level's own operation did not answer (`git show
ef39a9b:src/sage_extensions/categories/modules/pure/modules.py`; measured in
`.tmp/qc-evidence/500d-order-ideal.log`).

**The repair is the first option the review offered, at the owner of the missing
operation (`OWN-11`).**  The algebraic dual $\operatorname{Hom}_R(M,R)$ has two
shapes -- the module of functionals into ${}_R R$, and the product
$\prod_S R$ -- and `dual_evaluation` now pairs with both.  The case that raised
`TypeError` (`modules.py:3107`) is the module-of-functionals shape: a functional
there is a module map into ${}_R R$, so its value is that map applied to the
vector and read in the ring through `regular_module_isomorphism`.  The product
shape is unchanged.

`order_ideal` then states one thing, with no branch and no frame:

```python
return ring.ideal(*module.dual_evaluation_image_generators(self))
```

`dual_evaluation_image_generators` sits next to the pairing and says which
functionals generate the evaluation image in each shape: the generators of the
dual's chosen presentation, or -- for the product, which has no presentation at
all -- the coordinate functionals at the labels whose coordinates the
construction retained, whose values are those coordinates.  `_dual_coefficients`
is now the single place a vector's retained coordinates are read, and
`_selected_module_coefficients`'s protected contract names it among its
permitted callers (`OWN-05`).  The pairing's own coordinate reading is the one
the review did not object to and could not have: evaluating a functional at a
vector is what a pairing does.

`_dual_product_construction` is still the datum that fixes which shape exists,
and it is now read by `dual_module` and by the pairing only -- that is, by the
operations whose whole subject is the dual's shape (`STY-107`).

**Why not the second option.**  "The framed level's own `order_ideal` answers"
would make `FramedFreeModules.ElementMethods.order_ideal` the answer for
$\mathbf{Z}[x]$, and it is not: the join's category order puts `Modules` first
and the rebuild rule keeps it, which is why the defect appeared at the module
level in the first place.  Taking that route changes that rule's outcome for
this join, not the dual, and leaves the module-level operation unable to answer
for any module with an infinite chosen basis.  Its value is unchanged and right
on the same elements -- `.tmp/qc-evidence/500d-order-ideal.log` prints both
levels' answers side by side -- so nothing about the mathematics is traded.

## 2. The general ring's `__iter__` only raised, and its reason was false

**Claim, and it holds.**  `OwnedRings.ParentMethods.__iter__` raised
`TypeError("... it is not a finite ring ...")`, and the reason is not
mathematics: $\mathbf{Z}$, $\mathbf{Z}[x]$ and $\mathbf{Q}(i)$ are countable and
an iterator need not be finite.  What the method guarded is Python's sequence
fallback: `__getitem__` on a ring is the adjunction $R[x_1,\ldots,x_n]$, so with
`__iter__` merely absent `tuple(ZZ['x'])` reads `ZZ['x'][0]` -- a ring -- as the
first point and never stops.

**The repair is `__iter__ = None` on the general ring.**  The Python Language
Reference, Data Model, §3.3 "Special method names": setting a special method to
`None` states that the operation is not available, so `iter()` raises
`TypeError` *without falling back to `__getitem__`*.  The ring therefore states
no enumeration rather than refusing one it claims to have, and the block is the
language's.  Measured on this tree
(`.tmp/qc-evidence/500d-iter.log`): `iter(ZZ['x'])`, `iter(QQ['x'])`,
`iter(QQ)` and `iter(QQ(i))` raise `TypeError` at once, `tuple(ZZ['x'])` fails
at once instead of looping, and `Zmod(8)`, `Zmod(1)`, `GF(2)`, `GF(4)`, `GF(9)`
still enumerate their points through `OwnedRings.Finite.ParentMethods.__iter__`.

`ZZ` is unaffected and was already: its class resolves `__iter__` to
`FramedFreeModules.FinitelyGenerated.ParentMethods`, which raises
`unable to coerce <class 'dict'> to an integer`.  That is #526's subject (a
finitely generated framed ring enumerating its points through its framing), and
this change neither creates nor fixes it.

## 3. `OwnedRings.Finite`: an engine-defined axiom, a refusal, and a late placement

**Claim, and all three parts hold.**  The axiom's docstring said a finite ring
"is exactly the rings whose points are enumerated by the engine that realizes
them" (`ARC-08`: availability is not existence).  `Finite.ParentMethods.__iter__`
refused with `raise TypeError` where `STY-49` asks for an assertion of the
algorithm's hypothesis.  The axiom itself was added by
`refine(self, OwnedRings().Finite())` after `super().__init__` and after
`realize_owned_category`, while the comment ten lines above it says a
post-construction refinement is too late for owners that construct the regular
module during the hooks (`OWN-03`, `OWN-23`).  The local import
`_refine_into_finite` existed only to perform that refinement.

**Repair.**  The docstring now states finiteness as a fact about the ring and
the listing as an algorithm over the realization.  The listing asserts its
hypothesis:

```python
engine = self._selected_engine_ring()
assert engine is not None and engine is not self, (...)
```

The axiom is now part of the placement *before* `Parent.__init__`:
`_with_finite_ring_axiom(placement)` joins `OwnedRings().Finite()` when the
placement the constructor states is already among the finite sets, at both
places that fix a ring's placement (the initial one and the deferred
ring-facet one).  The local import and its refinement are deleted.

**The finite rings of the other constructors, probed for enumeration**
(`.tmp/qc-evidence/500d-finite-probe.log`):

| constructor | ring | finite sets / axiom | cardinality | level answering `__iter__` | points |
| --- | --- | --- | --- | --- | --- |
| owned quotient | $\mathbf{Z}/8$ | yes / yes | 8 | `OwnedRings.Finite.ParentMethods` | 8 |
| owned quotient | $\mathbf{Z}/1$ | yes / yes | 1 | `OwnedRings.Finite.ParentMethods` | 1 |
| prime field | $\mathbf{Z}/2$ | yes / yes | 2 | `OwnedRings.Finite.ParentMethods` | 2 |
| residue field of $\mathbf{Z}/4$ | $\mathbf{Z}/2$ | yes / yes | 2 | `OwnedRings.Finite.ParentMethods` | 2 |
| polynomial quotient | $GF(4)$ | yes / yes | 4 | `OwnedRings.Finite.ParentMethods` | 4 |
| polynomial quotient | $GF(9)$ | yes / yes | 9 | `OwnedRings.Finite.ParentMethods` | 9 |
| owned product | $GF(2)\times GF(2)$ | yes / yes | 4 | `FramedFreeModules.FinitelyGenerated.ParentMethods` | **raises** |
| owned product | $\mathbf{Z}/4\times GF(3)$ | yes / yes | 12 | `FramedFreeModules.FinitelyGenerated.ParentMethods` | **raises** |

The two owned products are finite rings, are placed in the axiom, and do not
enumerate: the class that answers is the framed free module's coordinate
iteration, which raises `ValueError: (0,) should be of length 2`.  They are not
a gap this change opens -- the placement change leaves the answering level where
it was, measured before and after
(`.tmp/qc-evidence/500d-finite-probe-before.log`) -- and they are not this
issue's: a ring whose class resolves `__iter__` to the framed module's coordinate
iteration is #526, filed.  What #500 owed here is the probe, and the answer is
that the quotient, residue-field and polynomial-quotient constructors enumerate
and the product constructor does not.

## 4. Tests

* The red test now asserts that the order ideal is an ideal of the base ring and
  not only that it equals one: `ideal in CommutativeIdeals(ZZ)` and
  `ideal in CommutativeIdeals(QQ)` beside the equalities.  At `51310d613c` the
  call a reviewer read as $O(x+1)$ was a module that compared equal to
  $\mathbf{Q}$, and equality alone cannot tell the two apart.
* The finite-ring enumeration test states the level that answers
  (`OwnedRings.Finite.ParentMethods.__iter__`), and what the other two would do
  instead: the general ring states no enumeration, the framed module would list
  a chosen basis' coefficients.
* The unused `import pytest` is deleted from
  `tests/categories/test_the_refined_category_answers_with_its_own_operation.sage`.
* `tests/rings/test_a_ring_states_no_enumeration_of_its_points.sage` is the red
  test for §2: on `5f17b92` the ring's `__iter__` is a method, so
  `ring.__iter__ is None` fails; with the repair, `iter` and `tuple` raise the
  language's `TypeError` and $\mathbf{Z}[x]$ is placed among the countably
  infinite sets, so the refusal is not a claim about its cardinality.

## What is not repaired here

* #526 -- a finitely generated framed ring enumerating its points through its
  framing.  `iter(ZZ)` and the two owned products above are its instances.
* #527 -- the completion test's codomain, the undecided surjectivity, and the
  inverse system's `TypeError`.
* The dual of a quotient that has no chosen presentation
  ($\mathbf{Z}/8$ as a $\mathbf{Z}$-module): `dual.module_generating_set()`
  raises `ValueError: Mor(Z/8, Z) has no chosen resolution`, as it did before
  this change, so $O_{Z/8}(3)$ is not computed there by either reading -- the
  framed level raises `AttributeError: ... has no attribute 'to_vector'` on the
  same element.  Reported rather than asserted; no test pins it.
* $M_2(\mathbf{Z})(1) / 2$ -- #523.

## Regression

The same targets on this tree and on a clean worktree at the base commit
`5f17b92fe7`, one pytest process per target, FAILED **ids** compared and never
counts (`.tmp/qc-evidence/500d-sweep-tree.log`,
`.tmp/qc-evidence/500d-sweep-base.log`, `.tmp/qc-evidence/500d-compared.log`):

| target | this tree | base `5f17b92` | only here / only base |
| --- | --- | --- | --- |
| `tests/categories` | 61 failed, 59 passed | 61 failed, 59 passed | 0 / 0 |
| `tests/algebras` | 64 failed, 149 passed | 64 failed, 149 passed | 0 / 0 |
| `tests/modules` | 82 failed, 227 passed | 82 failed, 227 passed | 0 / 0 |
| `tests/sets` | 29 failed, 127 passed | 29 failed, 127 passed | 0 / 0 |
| `tests/foundations` | 2 failed, 6 passed | 2 failed, 6 passed | 0 / 0 |
| `tests/objects` | 115 failed, 211 passed | 115 failed, 211 passed | 0 / 0 |
| `tests/functions` | 48 failed, 15 passed | 48 failed, 15 passed | 0 / 0 |
| `tests/engineering` | 2 failed, 6 passed | 2 failed, 6 passed | 0 / 0 |
| `tests/divisors` | 42 failed, 25 passed | 42 failed, 25 passed | 0 / 0 |
| `tests/tensors` | 19 failed, 24 passed | 19 failed, 24 passed | 0 / 0 |
| `tests/topology` | 1 failed | 1 failed | 0 / 0 |
| `tests/rings` | 74 failed, **260 passed** | 74 failed, **259 passed** | 0 / 0 |
| `tests/*.py` (twenty files) | all as on the base | all as on the base | 0 / 0 |

The one count difference is the new test in `tests/rings`.  `tests/lattices` is
not run as one directory on this host; the files under it and the two under
`tests/forms` that read the dual, the order ideal or the framed content were run
on both trees and match id for id
(`.tmp/qc-evidence/500d-extra-tree.log`, `.tmp/qc-evidence/500d-extra-base.log`).
