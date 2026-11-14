C13: The endset of a finite group action has no cardinality

`Mor_G(X, X).cardinality()` for a finite `G`-set raises `AssertionError: cannot compute the cardinality of Mor_Cyclic group C_3 of order 3(...)`: the equivariant self-maps of a finite action are finite and computable, and their number cannot be read.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_g_sets_torsor_archive.sage::test_the_equivariant_self_maps_of_the_regular_c3_set_are_its_three_translations`
  `AssertionError: cannot compute the cardinality of Mor_Cyclic group C_3 of order 3({1, (1 2 3), (1 3 2)} with Cyclic group C_3 of order 3-action, {1, (1 2 3), (1 3 2)} with Cyclic group C_3 of order 3-action): its construction supplies no exact value or decided finite enumeration (it is in Join of Category of endsets and Category of homsets of sets and Category of sets)`
  at `src/sage_extensions/categories/sets/set_categories.py:2503: in cardinality`

Defective call: src/sage_extensions/categories/sets/set_categories.py:2503 (cardinality), for the endset of an action; the construction supplies no exact value (this is #408's C17/C18 refusal class).

Introduced by: not bisected: the refusal is in the root commit c731175 (2026-10-26, Zack Garza).

Scope: the endset of a finite group action; one test.

Triage record: `results/issue411-triage.md` (C13), slice of #411.
