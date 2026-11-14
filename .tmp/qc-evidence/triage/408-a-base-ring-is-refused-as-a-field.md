A base ring is refused as a field

`ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring`, raised on the base change of a free module to `QQ`.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_free_module_of_rank_three.sage::test_the_base_change_to_the_rationals`
  `ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring`

Defective call: /sage/.venv/lib/python3.14/site-packages/sage/categories/vector_spaces.py:70.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: `test_free_module_of_rank_three.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C26 of the triage in results/issue408-triage.md.
