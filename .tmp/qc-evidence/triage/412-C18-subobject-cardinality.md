C18: A subobject category does not carry `cardinality`

`group.subobjects().cardinality()` raises `AttributeError: 'SubobjectCategory_with_category' object has no attribute 'cardinality'`. A subobject category is a set of subobjects; asking how many there are -- the invariants test of `Q_8` and `S_3` -- is refused.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_quaternion_group.sage::test_the_invariants_of_q8`
  `AttributeError: 'SubobjectCategory_with_category' object has no attribute 'cardinality'`
- `tests/objects/test_symmetric_group_s3.sage::test_the_invariants_of_s3`
  `AttributeError: 'SubobjectCategory_with_category' object has no attribute 'cardinality'`

Defective call: the subobject category of an owned object.

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'Q'`.

Scope: every subobject category.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C18).
