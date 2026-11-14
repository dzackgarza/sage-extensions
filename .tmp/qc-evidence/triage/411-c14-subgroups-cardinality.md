C14: `Subgroups(G)` has no cardinality

`Subgroups(C_6).cardinality()` raises `AssertionError: cannot compute the cardinality of Subgroups of Cyclic group C_6 of order 6`: the number of subgroups of a finite group is finite and computable, and cannot be read.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_groups_archive.sage::test_finite_group_subgroups_are_owned_and_keep_the_ambient_group`
  `AssertionError: cannot compute the cardinality of Subgroups of Cyclic group C_6 of order 6: its construction supplies no exact value or decided finite enumeration (it is in Join of Category of finite sets and Category of facade sets and Category of finite countable sets)`
  at `src/sage_extensions/categories/sets/set_categories.py:2503: in cardinality`

Defective call: src/sage_extensions/categories/sets/set_categories.py:2503 for the object at src/sage_extensions/categories/group/groups.py:8204 (Subgroups).

Introduced by: not bisected: both the parameterized category and the refusal are in the root commit c731175 (2026-10-26, Zack Garza).

Scope: the subgroup set of a finite group; one test.

Triage record: `results/issue411-triage.md` (C14), slice of #411.
