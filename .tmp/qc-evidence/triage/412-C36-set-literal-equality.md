C36: The category applied to its own points does not agree with the set

`{1, 2, 3} == {1, 2, 3}` is `False`: a three-element set built by the category's constructor and one written as a literal are two objects, so `test_the_category_applied_to_the_points_agrees` cannot compare them even though both print the same.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_three_element_set.sage::test_the_category_applied_to_the_points_agrees`
  `assert {1, 2, 3} == {1, 2, 3}`

Defective call: equality of owned finite sets (facade sets against constructed sets).

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: finite-set equality, so it reaches every comparison of a constructed set with a facade.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C36).
