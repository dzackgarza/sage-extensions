C35: A three-element set built by the category's own name has no ambient category

`Sets.Δ[2]` -- the standard three-element set -- reports `{1, 2, 3} has no ambient category: it was not built by a category's constructor, so nothing recorded which category it is an object of`, although it reports that it *is* placed in a join of finite sets. A user cannot ask for its morphisms, so the smallest finite set in the library has no hom sets.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_three_element_set.sage::test_maps_out_of_and_into_a_three_element_set`
  `AssertionError: {1, 2, 3} has no ambient category: it was not built by a category's constructor, so nothing recorded which category it is an object of (it is placed in Join of Category of finite sets and Category of facade sets and Category of finite countable sets)`
- `tests/objects/test_three_element_set.sage::test_a_three_element_set_has_one_endomorphism_category`
  `AssertionError: {1, 2, 3} has no ambient category: it was not built by a category's constructor, so nothing recorded which category it is an object of (it is placed in Join of Category of finite sets and Category of facade sets and Category of finite countable sets)`

Defective call: the standard finite set `{1,2,3}` and its ambient-category record.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the standard finite sets, so it reaches every `Sets.Δ[n]` morphism test.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C35).
