C10: `finite_subsets()` and `power_set()` are two objects where there is one

`three().finite_subsets() == power()` is `False`: `Finite subsets of {0,...,2}` and `Power set of {0,...,2}` are two different objects, so a user who goes through either door cannot compare the results. The power set of a finite set is the finite subsets of it, and the library offers both names for one construction.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_power_set_of_a_three_element_set.sage::test_every_subset_of_a_finite_set_is_finite`
  `assert Finite subsets of {0,...,2} == Power set of {0,...,2}`

Defective call: the power-set/finite-subsets constructors of a finite set.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the power-set constructor identity, so it reaches `Sets.Δ[n].power_set()` and `subsets_of_size`.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C10).
