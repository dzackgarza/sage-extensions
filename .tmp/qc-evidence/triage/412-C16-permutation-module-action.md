C16: The action on the permutation module returns vectors that do not compare equal

`assert [0] == [0]` fails in `test_the_action_on_the_permutation_module`: two copies of the same zero vector of the permutation module do not compare equal, so the group action cannot be checked at all -- a user comparing a computed orbit element with the expected one gets `False` for equal vectors.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_regular_module_of_c2.sage::test_the_action_on_the_permutation_module`
  `assert [0] == [0]`

Defective call: the permutation module's element equality (the action of the cyclic group on its own regular module).

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'C'`.

Scope: vector equality on the permutation module, so the scope is element equality for group-algebra modules.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C16).
