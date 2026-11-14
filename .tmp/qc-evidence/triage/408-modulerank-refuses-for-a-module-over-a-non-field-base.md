`module_rank` refuses for a module over a non-field base

`M.module_rank()` raises `AssertionError: the rank of ... is computed over a finite field for a finite module, or from a chosen basis`, for `QQ` over `ZZ`, for a fractional ideal, and for an exterior algebra's graded piece.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_graded_pieces_of_the_exterior_algebra`
  `AssertionError: the rank of Lambda(Free module on {[a], [b]} over Fraction Field of Integer Ring) over Fraction Field of Integer Ring is computed over a finite field for a finite module, or from a chosen basis or pre`
- `tests/objects/test_fractional_ideal_2z.sage::test_2z_is_principal_and_free_of_rank_one`
  `AssertionError: the rank of Fractional ideal (2) of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or presentation, and Fractional ideal (2) of Integer Ring`

The same defect also fails `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_centre_of_the_tensor_algebra`, in files that #412 now owns.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/pure/modules.py:2466.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: `test_exterior_algebra_of_qq2.sage`, `test_fractional_ideal_2z.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C15 of the triage in results/issue408-triage.md.
