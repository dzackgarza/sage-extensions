C11: `subsets_of_size` coerces its argument with `int()` instead of refusing a non-natural

`points.subsets_of_size(QQ(3)/2)` raises `TypeError: int() argument must be ... not 'OwnedJoinCategory.element_class'` where the contract is `ValueError`: the size argument is run through Python's `int()` rather than being asked for a natural number, so the refusal the test states is not the refusal a user gets.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_power_set_of_a_three_element_set.sage::test_subset_cardinality_must_be_a_natural_number`
  `TypeError: int() argument must be a string, a bytes-like object or a real number, not 'OwnedJoinCategory.element_class'`

Defective call: `subsets_of_size` on a finite owned set.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the one constructor, so the scope is the argument contract of `subsets_of_size`.

Repair: repaired in this workstream by `415c2b4`, which replaces `415c2b4`'s local reading with the owner's. Evidence: red test at `415c2b4`: 1 failed, 9 passed (2 failed, 8 passed at `c8a3ced`); `tests/sets` neighbours 4 failed, 15 passed before and after, the same four ids; the refusals are now `ValueError: (3)/(2) is not a natural number` and `ValueError: -1 is not a natural number`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C11).
