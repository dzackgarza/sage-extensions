The session namespace does not publish the constructors the suite names

`from sage_extensions.all import *` binds a namespace that omits nineteen owned constructors the suite names: `AbsoluteGaloisGroup`, `AbsoluteGaloisGroups`, `AbsoluteGaloisGroupsOfFiniteFields`, `FinitelyGeneratedGroups`, `FinitelyPresentedGroups`, `ProfiniteGroups`, `AlternatingAlgebras`, `SymmetricAlgebras`, `TensorAlgebras`, `StrictlyGradedCommutativeAlgebras`, `FractionalIdeals`, `ModulesWithConnection`, `ModulesWithFlatConnection`, `FinitelyGeneratedModules`, `FinitelyPresentedModules`, `ProjectiveModules`, `TorsionModules`, `TensorProductModules`, `SymmetricBilinearFormModules`. A user who writes the session-standard import gets `NameError` for a constructor the library owns, and the repository's own test lint reports the same names as TL13.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_categories_of_the_absolute_galois_group`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_of_a_finite_field_is_zhat`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_frobenius`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_finite_quotients`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_has_one_endomorphism_category`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_cyclic_module_zz6.sage::test_the_categories_of_zz6`
  `NameError: name 'FinitelyPresentedModules' is not defined`
- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_categories_of_the_exterior_algebra`
  `NameError: name 'AlternatingAlgebras' is not defined`
- `tests/objects/test_fractional_ideal_2z.sage::test_the_category_construction_agrees`
  `NameError: name 'FractionalIdeals' is not defined`
- `tests/objects/test_fractional_ideal_2z.sage::test_the_categories_of_2z`
  `NameError: name 'FractionalIdeals' is not defined`
- `tests/objects/test_free_group_of_rank_two.sage::test_the_categories_of_f2`
  `NameError: name 'FinitelyGeneratedGroups' is not defined`
- `tests/objects/test_free_module_of_rank_three.sage::test_the_categories_of_zz3`
  `NameError: name 'FinitelyGeneratedModules' is not defined`

The same defect also fails `tests/objects/test_root_lattice_a2.sage::test_the_categories_of_a2`, `tests/objects/test_symmetric_algebra_of_qq2.sage::test_the_categories_of_the_symmetric_algebra`, `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_categories_of_the_tensor_algebra`, `tests/objects/test_tensor_product_of_zz2_and_zz3.sage::test_the_categories_of_the_tensor_product`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_categories_of_the_module_with_connection`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_every_connection_on_a_line_over_a_curve_is_flat`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_module_with_connection_has_one_endomorphism_category`, in files that #412 now owns.

Defective call: /repos/sage-extensions/tests/objects/test_absolute_galois_group_of_f5.sage:5, /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:29, /repos/sage-extensions/tests/objects/test_exterior_algebra_of_qq2.sage:20, /repos/sage-extensions/tests/objects/test_fractional_ideal_2z.sage:13, /repos/sage-extensions/tests/objects/test_fractional_ideal_2z.sage:9, /repos/sage-extensions/tests/objects/test_free_group_of_rank_two.sage:15, /repos/sage-extensions/tests/objects/test_free_module_of_rank_three.sage:37.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 6 files of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C01 of the triage in results/issue408-triage.md.
