C33: The session namespace does not publish five constructors the suite names

`from sage_extensions.all import *` omits `SymmetricBilinearFormModules`, `SymmetricAlgebras`, `TensorAlgebras`, `TensorProductModules` and `ModulesWithConnection`, all of which the library defines. A user writing the session-standard import gets `NameError` for a constructor the library owns.

Failing tests (5, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_root_lattice_a2.sage::test_the_categories_of_a2`
  `NameError: name 'SymmetricBilinearFormModules' is not defined`
- `tests/objects/test_tensor_product_of_zz2_and_zz3.sage::test_the_categories_of_the_tensor_product`
  `NameError: name 'TensorProductModules' is not defined`
- `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_categories_of_the_module_with_connection`
  `NameError: name 'ModulesWithConnection' is not defined`
- `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_every_connection_on_a_line_over_a_curve_is_flat`
  `NameError: name 'ModulesWithConnection' is not defined`
- `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_module_with_connection_has_one_endomorphism_category`
  `NameError: name 'ModulesWithConnection' is not defined`

Defective call: `src/sage_extensions/all.py`.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the constructor was never published by the session namespace. Repaired on main by `d38845a` (2026-11-14, agent, "fix: The session namespace publishes the constructors the suite names (#408)"); this slice's five tests are green at `7817e87` and at `4a17b1e` (`tests/objects/test_trivial_connection_on_the_affine_line.sage` 4 passed, `test_the_categories_of_a2` and `test_the_categories_of_the_tensor_product` passed).

Scope: the session namespace. This is one defect with #408's cause C01 and it is repaired on main by `d38845a`; five of this slice's seven tests are green at `7817e87`, and the other two are C37.

Repair: closed on main by `d38845a` (#408), before this slice was filed. Evidence: 5 of the 7 tests green at `7817e87` and at `415c2b4`; the two still red are C37, unmasked by that fix.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C33).
