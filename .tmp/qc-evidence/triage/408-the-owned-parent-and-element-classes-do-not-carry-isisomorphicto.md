The owned parent and element classes do not carry `is_isomorphic_to`

`is_isomorphic_to` -- the spelling `ring_foundation` already installs as an alias of `is_isomorphic` -- is absent from the owned parent and element classes of modules, schemes and sets, so `A.is_isomorphic_to(B)` raises `AttributeError` and Sage itself answers `Did you mean: 'is_isomorphic'?`. A user of the public spelling gets an attribute error on objects that do support the relation.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_an_affine_line`
  `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?`

The same defect also fails `tests/objects/test_projective_plane_over_qq.sage::test_the_projective_plane_is_glued_from_its_charts`, `tests/objects/test_projective_plane_over_qq.sage::test_the_standard_affine_charts`, `tests/objects/test_projective_plane_over_qq.sage::test_the_picard_group_and_the_canonical_bundle`, `tests/objects/test_regular_module_of_c2.sage::test_the_permutation_module_is_the_regular_module`, `tests/objects/test_regular_module_of_c2.sage::test_the_coinduced_module_is_the_regular_module`, `tests/objects/test_symmetric_group_s3.sage::test_the_automorphisms_of_a_three_element_set`, in files that #412 now owns.

Defective call: sage/cpython/getattr.pyx:357.

Introduced by: `git bisect` in the image on the signature `object has no attribute 'is_isomorphic_to'`; the first commit where it appears is `55927425bcff` -- fix: let the cached quotient-by-relations constructor read its keyword defaults (Zack Garza <dzackgarza@gmail.com>), in 12 bisect steps.

Scope: 1 file: `test_a_coordinate_line_in_the_affine_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C04 of the triage in results/issue408-triage.md.
