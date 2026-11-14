The assertion at `test_affine_plane_over_qq.sage:15` does not hold: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring

The proposition asserted at `/repos/sage-extensions/tests/objects/test_affine_plane_over_qq.sage:15` is false on main: `Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring`. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_affine_plane_over_qq.sage::test_the_affine_plane_is_the_spectrum_of_its_coordinate_ring`
  `assert: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring`

Defective call: /repos/sage-extensions/tests/objects/test_affine_plane_over_qq.sage:15.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_affine_plane_over_qq.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C33 of the triage in results/issue408-triage.md.
