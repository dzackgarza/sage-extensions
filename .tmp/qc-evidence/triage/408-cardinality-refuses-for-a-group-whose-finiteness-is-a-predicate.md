`cardinality` refuses for a group whose finiteness is a `Predicate`

`Group.cardinality()` raises `AssertionError: cannot compute the cardinality of the group ... : its finiteness is is_finite(...)` for a finitely presented group of known finite order (Q_8, S_3, Aut of a ring), so the order of a finitely presented group cannot be read.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_integers.sage::test_the_automorphisms_of_the_integers`
  `AssertionError: cannot compute the cardinality of the group Aut_Category of modules over Integer Ring(Integer Ring): its finiteness is is_finite(Aut_Category of modules over Integer Ring(Integer Ring)), it has no cho`

The same defect also fails `tests/objects/test_quaternion_group.sage::test_the_presentation_of_q8`, `tests/objects/test_symmetric_group_s3.sage::test_the_coxeter_presentation`, in files that #412 now owns.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/group/groups.py:459.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_integers.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C13 of the triage in results/issue408-triage.md.
