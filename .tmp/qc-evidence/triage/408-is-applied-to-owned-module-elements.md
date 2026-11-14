`/` is applied to owned module elements

The tests write `M / N` and `ZZ / I`, which the owned modules do not support; the library spells these `quotient_module` and `quotient_ring`, and `Modules.__truediv__` is absent. (Whether the operator should exist is a design question, not a test bug: `AGENTS.md` bans `__truediv__` on modules, so the suite and the policy disagree.)

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_cyclic_module_zz6.sage::test_the_cokernel_and_the_quotient_agree`
  `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`
- `tests/objects/test_cyclic_module_zz6.sage::test_the_quotient_of_the_regular_module_by_the_ideal`
  `TypeError: unsupported operand type(s) for /: '_OwnedRingParent_with_category' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`
- `tests/objects/test_free_module_of_rank_three.sage::test_a_quotient_of_zz3`
  `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`

Defective call: /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:16, /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:20, /repos/sage-extensions/tests/objects/test_free_module_of_rank_three.sage:70.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: `test_cyclic_module_zz6.sage`, `test_free_module_of_rank_three.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C27 of the triage in results/issue408-triage.md.
