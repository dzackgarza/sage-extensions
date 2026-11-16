# Issue to file: `primitive_isotropic_subobject` checks three properties inline, on every plane

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body. Parent: **#518** (the epic that groups the
causes found by triage). #541 measures the cost and defers this repair; it is not
repaired there.

## Title

`primitive_isotropic_subobject` decides primitivity, isotropy and independence inline at
construction, so every plane pays for three checks a construction owes nobody

## Body

`Lattices(ZZ).ParentMethods.primitive_isotropic_subobject` (`lattices.py:9348`, checks at
`9367-9390` on `897e7f7`) builds the span and then, before it returns it, asserts three
properties of it:

1. `subobject.is_primitive()` (`lattices.py:9367`) — one primitivity decision per plane;
2. `all(self.b(embedded[left], embedded[right]) == zero for left in labels for right in
   labels)` (`lattices.py:9374-9379`) — a loop over the pairings of the plane's *selected
   basis*, `rank^2` executed pairings and `rank^2` owned-scalar comparisons;
3. `subobject.module_rank() == finite_ordered_set(elements).cardinality()`
   (`lattices.py:9385-9387`) — a rank against a cardinality, which for a rank-two plane
   already constructs a finite ordered set of the input.

`AGENTS.md`, "Construction is instant; checking is asked for; loops are tensors"
(always-on), states the rule each of these breaks: "a well-definedness condition
(linearity, isometry, equivariance, injectivity, an algebra's relations) is a validator
method of the object. Construction calls the validators once, after the object exists,
and each validator returns at once unless the global strict-checking flag is on"; and "a
loop over pairings is a tensor contraction. Mathematics written as an imperative loop is
almost always one tensor operation done slowly: the pairings of many vectors are one
contraction". A plane's isotropy is one restriction of the form to the span — a
pullback tensor — not `rank^2` scalar pairings.

None of the three is a *decision the constructor needs*. The object returned is the span
refined into `PrimitiveIsotropicSubobjects`; primitivity is stated of a
`PrimitiveIsotropicSubobject` by its category (`CAT-04`: placement is the claim of the
construction), and a caller who wants the property asks `is_primitive()`, which is where
`lattices.py:10632` and the rest of the tree already ask it.

### What it costs

The #541 census of one plane of the `Õ(T_Co)` row (`de9a1d1ca6`'s body, probe
`probe541prim.py`, `.tmp/qc-evidence/541r3-plane-parts-*.log`) attributes per plane:

| one plane's transport, 10.073 ms | ms |
| --- | --- |
| `is_primitive` on the span's inclusion | 5.425 |
| `subobject_on` (the Hermite form of the span) | 2.876 |
| `refine` into `PrimitiveIsotropicSubobjects` | 0.165 |
| the two basis images through the lift, **the isotropy pairings, the rank check** | **1.714** |

So checks 2 and 3 are 17 % of a plane's transport, paid by every one of the 189 720
planes of the walk, and check 1 was a further 54 % before `is_primitive` was repaired in
#541. At the row's measured 127 planes a second (#541, `897e7f7`), that is about 2 ms a
plane, about 6.5 minutes over the walk.

### Acceptance

The three checks become what `AGENTS.md` says they are:

- primitivity: nothing at construction. `refine(subobject, PrimitiveIsotropicSubobjects(R))`
  already places the object, and `is_primitive()` states the property for a caller who
  asks (the presented-module owner's `_torsion_freeness_decision`, or the inclusion's
  coordinate matrix through `_engine_matrix`, whichever the reviewer's category argument
  selects);
- isotropy: one contraction `embedded.pullback(form)` compared against the zero tensor
  of the plane, or a validator on `PrimitiveIsotropicSubobjects` that runs only under the
  strict flag, and never a Python loop over pairs;
- independence: not a construction-time assertion. A family that does not span its own
  span of the stated rank *is* the object the caller asked for — the span of it — and a
  caller who needs a basis asks `module_rank()`.

Red first: a test that constructs a plane whose basis is **not** independent and asserts
the object it gets (the span, of the rank the span has) rather than an `AssertionError`,
and a test that counts the pairings one construction makes (the instrument beside
`spans_built_by` in `tests/lattices/conftest.py`). Which of the three checks the owner
keeps as a strict-mode validator is the reviewer's call; the acceptance is that nothing
but the span is computed on the path.

## Evidence

- `grep -n "primitive_isotropic_subobject" src/sage_extensions/categories/lattices.py`
  → `5348` (definition; `9367-9390` on `897e7f7` are the three checks).
- `.tmp/qc-evidence/541r3-plane-parts-base.log`, `541r3-plane-parts-repaired.log` — the
  per-plane attribution above, 8 cold spans of `T_Co`.
- `.tmp/qc-evidence/541r3-row-repaired.log` — 26 506 planes by 516.6 s, 127.98 planes/s.
