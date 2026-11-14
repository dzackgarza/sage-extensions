C37: The symmetric and tensor algebra constructors refuse an owned field as their base

`SymmetricAlgebras(QQ)` and `TensorAlgebras(QQ)` raise `ValueError: base must be a ring or a subcategory of Rings()` for the owned field `QQ`, which is a ring the library builds. A user cannot construct the symmetric or the tensor algebra of the rational numbers -- the two free graded algebras the session namespace publishes names for.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_symmetric_algebra_of_qq2.sage::test_the_categories_of_the_symmetric_algebra`
  `NameError: name 'SymmetricAlgebras' is not defined`
- `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_categories_of_the_tensor_algebra`
  `NameError: name 'TensorAlgebras' is not defined`

Defective call: the base argument check of the `SymmetricAlgebras`/`TensorAlgebras` constructors (the owned field is not recognized as a ring by the check).

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`, where the test already failed with this same `ValueError`; it was masked at `c8a3ced` by C33, whose missing export made the construction raise `NameError` before reaching the base check.

Scope: the base check the two constructors share; the refusal is behind every symmetric/tensor algebra over an owned ring.

Repair: filed; unmasked by `d38845a` on main. Evidence: both tests fail with `ValueError: base must be a ring...` at `7817e87` on a clean worktree.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C37).
