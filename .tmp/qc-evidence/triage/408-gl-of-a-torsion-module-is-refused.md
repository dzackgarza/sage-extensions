`GL` of a torsion module is refused

`GL(M)` raises `AssertionError: GL(...) is realized as a matrix group only for a free module with a finite selected basis`, so the automorphisms of `Z/6` or `F_3` have no group.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_cyclic_module_zz6.sage::test_the_endomorphisms_and_automorphisms_of_zz6`
  `AssertionError: GL(Finitely presented module on 1 module generators over Integer Ring with invariant factors Invariant-factor family: [0 ↦ 6]) is realized as a matrix group only for a free module with a finite select`

The same defect also fails `tests/objects/test_prime_field_f3.sage::test_the_automorphisms_of_f3`, in files that #412 now owns.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:4032.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_cyclic_module_zz6.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C17 of the triage in results/issue408-triage.md.
