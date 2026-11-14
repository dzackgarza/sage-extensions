Two constructions of one lattice do not compare equal

`Lattices(ZZ)("A1") + Lattices(ZZ)("A2")` and the block-Gram construction of the same lattice do not compare equal, and neither do the catalogue and Gram constructions of `A_2`, `E_8` and `U + U`.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_a1_plus_a2.sage::test_the_sum_and_the_block_gram_agree`
  `assert: Integral latt...gnature (0, 3) == Integral latt...gnature (0, 3)`
- `tests/objects/test_degenerate_plane.sage::test_the_lattice_and_the_form_module_constructions_agree`
  `assert: Integral latt...gnature (1, 0) == Free module o...r Integer Ring`

The same defect also fails `tests/objects/test_root_lattice_a2.sage::test_the_named_and_the_gram_constructions_agree`, `tests/objects/test_root_lattice_e8.sage::test_the_catalogue_entry_agrees`, `tests/objects/test_two_hyperbolic_planes.sage::test_the_sum_and_the_block_gram_agree`, in files that #412 now owns.

Defective call: /repos/sage-extensions/tests/objects/test_a1_plus_a2.sage:9, /repos/sage-extensions/tests/objects/test_degenerate_plane.sage:12.

Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: `test_a1_plus_a2.sage`, `test_degenerate_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Cause C28 of the triage in results/issue408-triage.md.
