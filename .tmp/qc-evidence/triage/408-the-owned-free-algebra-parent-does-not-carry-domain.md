The owned free-algebra parent does not carry `domain`

`Spectrum`'s functor asks its source for `domain` and the owned free-algebra parent does not carry it, so the spectrum functor cannot be applied to a ring.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_affine_plane_over_qq.sage::test_the_spectrum_functor_agrees`
  `AttributeError: 'Owned_NativeFreeAlgebraParent_with_category' object has no attribute 'domain'`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_affine_plane_over_qq.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C07 of the triage in results/issue408-triage.md.
