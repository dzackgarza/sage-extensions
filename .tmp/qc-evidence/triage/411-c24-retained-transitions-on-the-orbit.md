C24: The retained sweep is stored on the orbit object it describes

After an orbit search, the orbit object carries `_retained_transitions` in its `__dict__`, so state that belongs to the family's sweep is attached to a single orbit and answers a later question with a stale table; a caller that inspects the orbit sees an undocumented attribute.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_the_orbit_schreier_family_reads_the_retained_sweep.sage::test_a_point_not_covered_by_the_retained_sweep_searches_as_before`
  `+  where {'_point_set': {5}, '_permutation_representation': Generic morphism:\n  From: Cyclic group C_3 of order 3\n  To:   Symme...s.ParentMethods.act of {1, 5, (1 2 3), (1 3 2)} with Cyclic group C_3 of order 3-action>, '_cache__action_of': {}, ...} = {5} with Cyclic group C_3 of order 3-action.__dict__`
  at `tests/groups/test_the_orbit_schreier_family_reads_the_retained_sweep.sage:111: in test_a_point_not_covered_by_the_retained_sweep_searches_as_before`

Defective call: src/sage_extensions/categories/group/g_sets.py:757 (the orbit's `__dict__` assignment).

Introduced by: 55592e9 (2026-11-07, D. Zack Garza) 'Read orbit generator permutations from the retained transition table'; blamed at :757.

Scope: the retention of the orbit sweep; one test.

Triage record: `results/issue411-triage.md` (C24), slice of #411.
