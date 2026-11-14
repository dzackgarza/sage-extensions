C19: A quotient of two cardinals is refused

`group.cardinality() / alternating.cardinality()` raises `TypeError: unsupported operand type(s) for /: 'Cardinalities.parent_class' and 'Cardinalities.parent_class'`, so the index of a subgroup cannot be written as the quotient of two orders.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_predicate_subgroups_archive.sage::test_even_permutations_of_s3_form_the_normal_subgroup_of_order_three`
  `TypeError: unsupported operand type(s) for /: 'Cardinalities.parent_class' and 'Cardinalities.parent_class'`
  at `tests/groups/test_predicate_subgroups_archive.sage:12: in test_even_permutations_of_s3_form_the_normal_subgroup_of_order_three`

Defective call: src/sage_extensions/categories/sets/cardinals.py, whose `Cardinalities` element has `__add__` (:717) and no `__truediv__`.

Introduced by: not bisected: the cardinal arithmetic is in the root commit c731175 (2026-10-26, Zack Garza).

Scope: cardinal division; one test. Whether `/` should exist on cardinals is a design question (the pole is at zero, and the index is a group-theoretic operation), not a test bug: the library bans `/` on modules for the same reason (#408's C44).

Triage record: `results/issue411-triage.md` (C19), slice of #411.
