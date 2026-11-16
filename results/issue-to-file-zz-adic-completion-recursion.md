# Issue to file: `ZZ.adic_completion` is the module-level constructor, so it recurses on an ideal and rejects an integer

Not filed by a push: this project's GitHub connection reads issues and pushes
but cannot create them, so the orchestrator posts this body.  The connection
also has no issue search, so no "is this already filed" check was made here;
the only issue read this round was #527.

## Title

`ZZ.adic_completion` resolves to the module owner and recurses on an ideal, and it rejects the integer `AdicCompletions().Local().an_object()` passes it

## Body

`ZZ` is a finitely presented module over itself, so the parent it resolves
places it in `ModulesWithChosenFinitePresentation`, whose `adic_completion`
drops a raw ideal into `M ⊗_R R_hat`.  That method precedes
`OwnedRings.ParentMethods.adic_completion` in the MRO of `ZZ` alone -- `QQ`,
`QQ[x]` and `QQ(i)` all resolve the ring owner's -- and it does two things the
ring owner does not:

- it takes only an ideal, so the integer `2` raises
  `AttributeError: 'int' object has no attribute 'ring'`;
- for an ideal it computes `ring = self.base_ring()`, which is `ZZ` again, and
  calls `ring.adic_completion(ideal, precision=precision)`, which resolves to
  itself: `RecursionError: maximum recursion depth exceeded`.

```python
sage: ZZ.adic_completion(2)
AttributeError: 'int' object has no attribute 'ring'
sage: ZZ.adic_completion(ZZ.ideal(2))
RecursionError: maximum recursion depth exceeded
```

The second is a crash of a shipped category constructor: `AdicCompletions()
.Local().an_object()` is `_owned_integers().adic_completion(2)`, and it raises
the `AttributeError` at `modules/pure/modules.py:4655`, in `an_object` at
`commutative_algebra.py:3036`.

The 2-adic ring itself is reachable as `Zp(5)`'s sibling, `Zp(2)`, whose
`adic_completion` is the ring owner's; what is broken is the *general* call on
`ZZ`, which is what the completion category's own object constructor uses.

## Reproducer

```python
from sage_extensions.all import *
print(ZZ.adic_completion.__qualname__)
# ModulesWithChosenFinitePresentation.ParentMethods.adic_completion
print(AdicCompletions().Local().an_object())
```

## Evidence

Run in the adopted image, `PYTHONPATH=<tree>/src`, `/sage/.venv/bin/python -u`,
tree `bbb0dd6` (main at the time of writing) and the #527 round's tree, which
does not touch this: same output on both.

| tree | call | result |
| --- | --- | --- |
| `bbb0dd6` | `ZZ.adic_completion(2)` | `AttributeError: 'int' object has no attribute 'ring'` |
| `bbb0dd6` | `ZZ.adic_completion(ZZ.ideal(2))` | `RecursionError: maximum recursion depth exceeded` |
| `bbb0dd6` | `AdicCompletions().Local().an_object()` | `AttributeError` at `modules.py:4655`, from `commutative_algebra.py:3036` |
| `bbb0dd6` | `QQ`, `QQ[x]`, `QQ(i)`, `Zp(5)` | resolve `OwnedRings.ParentMethods.adic_completion` |

Logs `.scratch/probe527/check10-main.log`, `.scratch/probe527/check11.log`.

## Acceptance

`ZZ.adic_completion` answers for both of the forms the ring owner's constructor
accepts -- an ideal of `ZZ` and an integer -- and `AdicCompletions().Local()
.an_object()` builds.  Which owner is repaired is the decision at that owner:
either the module-level `adic_completion` stops shadowing the ring one for a
ring that is a module over itself (the ring's own constructor is the one a ring
must resolve), or it is renamed and the two callers of the ring-level form are
redirected.  `M ⊗_R R_hat` for a module that is not the base ring keeps the
meaning it has today.
