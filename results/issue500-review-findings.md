# The second review of #500: one authority for the integers, a criterion with a reference, and the tests the rule owed

`904e079`, `9fd76e4` and `cef9c5d` put a ring element's `/` on the ring category's
element methods, left the engine-backed realization with the `_div_` hook, and stated
the integer coercion the operator needs.  The review found four things, each answered
at `6828f81`; this note records what the code said, what it says now, and what was
measured.

## 1. The integer coercion had two authorities

`OwnedRings.ParentMethods._coerce_map_from_` (ring_foundation.py:4298) states the
integers as the prime ring: the unique unital map $\mathbf{Z} \to R$, $n \mapsto n\cdot 1$,
for both the session's own integer and the Python `int` a caller passes.  The
engine-backed realization `_OwnedRingParent._coerce_map_from_` stated the same case
again, and ended its `match` in `case _: return None`.

The realization's method is the one that ran.  `_OwnedRingParent` precedes
`OwnedRings.ParentMethods` in the method resolution order of an engine-backed ring
(measured on `ZZ`, `QQ(i)` and the localizations), so the category's hook was
unreachable for the integers, and its `case _: return None` also meant that no other
source ever reached it.  Two authorities for one map is `OWN-19`; the repair is to
delete the realization's copy, not to keep them agreeing.

The realization now answers what it owns -- the engine's canonical maps between owned
rings, and the initial semiring -- and calls `super()._coerce_map_from_(source)` for
everything else, which lands on the ring category's hook:

```
$ cat .tmp/qc-evidence/500b-findings.log            (read at 6828f81)
  the hook of the engine-backed realization names:
    ('OwnedRings', '_engine', 'has_coerce_map_from', '_engine_ring', 'OwnedSemirings',
     'initial_object', 'initial_morphism', 'super', '_coerce_map_from_')
  ZZ: _coerce_map_from_(int) -> <function _owned_ring_from_integer ...>;
      the integer case of the ring category answers with the same function
```

The behaviour the previous commits bought is unchanged: `ZZ(3)/2 = (3)/(2)` in
$\mathbf{Q}$, `2/ZZ(4) = (1)/(2)`, `e12/2 = (1/2)e12`, `RR(3)/2` and `CC(3)/2`, and a
raw Sage integer still refused by every engine-backed ring.

## 2. The rule decided by a deny-list

`refine._final_category_operations` orders the category levels' operations after a
refinement.  Which names it may order was decided by exclusion: `_is_bookkeeping_or_hook`
admitted every dunder that was not in `_CLASS_BOOKKEEPING` or `_RUNTIME_OWNED_NAMES`, so
a protocol name a category declared later would have been admitted by omission.

The criterion is now positive, and cited: the special methods the Python language
reference defines for emulating container types (Data Model, §3.3.7) and numeric types
(§3.3.8) -- 62 names in `_VALUE_PROTOCOL_NAMES` -- plus the public names.  A
single-underscore name is a construction hook and stays on the provider that declared
it; any other dunder names construction, identity, attribute access, representation,
comparison or a context manager, and belongs to the object's own class.  The condition
that the rule acts only where two category levels disagree is untouched.

Eleven dunder names are declared in the tree that the deny-list admitted and the
protocol refuses: `__lt__`, `__le__`, `__gt__`, `__ge__`, `__bool__`, `__repr__`,
`__classcall__`, `__classcall_private__`, `__post_init__`, `__get__`, `__set__`.  Four
of those are rich comparisons and two are the descriptor protocol, so the criterion has
to say why they are not operations on a value: they are in the data model's §3.3.1 and
§3.3.2, and `__eq__`, `__hash__` and `__ne__` -- which the rule must never move -- sit
in the same section as the comparisons.

Narrowing a filter is only safe if nothing depended on what it let through.  The old
predicate is re-run over the same providers, the same carried classes and the same
rebuilt class for eighteen constructed objects, so the two selections are compared on
one tree:

```
$ cat .tmp/qc-evidence/500b-criterion.log           (read at 6828f81)
  constructed 18 objects: ['CC', 'Lattices(QQ)([[1]])', 'Lattices(ZZ)(2)', 'M_2(QQ)',
   'M_2(ZZ)', 'QQ', 'QQ(i)', 'QQ**2', 'QQ[x,y]', 'QQ[x]', 'RR', 'ZZ', 'ZZ**2', 'ZZ/8',
   'ZZ[i]', 'ZZ[x]', 'ZZ_5', 'Zp(5)']
  selected by the new criterion:
    __iter__: ['Owned_OwnedAlgebraParent_with_category', 'Owned_OwnedRingParent_with_category']
    __truediv__: ['Owned_AdicCompletionAlgebraParent_with_category.element_class', ...]
    adic_completion: ['Owned_OwnedAlgebraParent_with_category', 'Owned_OwnedRingParent_with_category']
    order_ideal: ['Owned_NativeFreeAlgebraParent_with_category.element_class', ...]
  only the old criterion selected: []
  only the new criterion selected: []
```

The same four names, by both criteria, on every object built.

## 3. The three operations the rule moves now state which level answers

`tests/categories/test_the_refined_category_answers_with_its_own_operation.sage` names,
for each moved operation, the category level that answers and the value it returns, on
`QQ(i)` -- an algebra over `QQ` that is also a finitely generated framed free module, a
module with a chosen finite presentation, and an infinite ring, so all three rebuilds
happen to it:

| operation | level that answers | what it returns on `QQ(i)` |
| --- | --- | --- |
| `order_ideal` | `Modules.ElementMethods` | $O_{\mathbf{Q}(i)}(1+i) = \mathbf{Q}$: the evaluation image is the unit ideal |
| `__iter__` | `OwnedRings.ParentMethods` | the `TypeError` of a ring that is not finite, instead of the framed module's coordinate enumeration |
| `adic_completion` | `OwnedRings.ParentMethods` | the completion of the field at $(0)$, whose `completion_source()` is the field; the module level's base change refuses that ideal, which is not an ideal of the base ring `QQ` |

The two run together with the division test in **8 passed in 16.57 s**, test lint loaded.

## 4. The contract's false sentence

The ring contract's docstring said the quotient "is computed in the parent the two
elements have in common, which is the ring exactly when the divisor is one of its
units".  In `Z(3)/2` the two elements meet in `Z`, and the answer `3/2` is an element of
`Q` because the realization's `_div_` decides where the quotient lands.  The clause is
deleted; the docstring now states that the operands meet in a common parent, that the
quotient need not stay in it, and that the realization that computes the division owns
the codomain.

## What is not repaired here

`order_ideal` on an element of the free algebra `QQ[x]` or `ZZ[x]` raises
`AttributeError: 'GeneralModules.parent_class' object has no attribute 'codomain'`.  The
category order of that join places `Modules.ElementMethods` before
`FramedFreeModules.ElementMethods`, so the evaluation image answers where the coordinate
reading would compute.  The cause is `Modules.ElementMethods.order_ideal`'s
`dual_module()` on a free algebra, in files this push does not touch (`git diff 0a8a95b
6828f81 -- src/sage_extensions/categories/modules` is empty), and it needs the module
dual repaired at its owner.  It is reported rather than asserted: a test that pinned the
correct value there would be red on `main`.

`M_2(ZZ)(1) / 2` keeps refusing with a `TypeError` from the matrix realization's inverse
over `ZZ`; that refusal is #523, not this issue.

## Regression

Thirteen test directories and the root `tests/*.py`, one pytest process per target, on
this tree and on a clean worktree at `ba3ab60`: **840 FAILED ids on each side, none only
on the tree, none only on the base**.  The only count difference is `tests/categories`,
59 passed against 56, which is the three new tests.  `tests/lattices` is not run as one
directory -- 5.6 GiB resident and unfinished after 25 minutes on this host -- so the two
files under it that read the framed content (`test_content_and_doubling.sage`,
`test_reflection_rational_line.sage`) were run on both trees and match id for id.
