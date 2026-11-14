C20: The session's `matrix` takes one row family, not a ring and a row family

`matrix(ZZ, [[0,-1],[1,0]])`, Sage's own spelling for a matrix, raises `TypeError: matrix() takes 1 positional argument but 2 were given`; the session's `matrix` reads the coefficient ring from the entries only. And the one-argument form answers an engine matrix-space element, not the owned matrix-Mor its docstring states, which a preamble group then refuses.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_sl2z_serre_archive.sage::test_sl2z_is_generated_by_elements_of_orders_four_and_six_amalgamated_over_minus_one`
  `TypeError: matrix() takes 1 positional argument but 2 were given`
  at `tests/groups/test_sl2z_serre_archive.sage:13: in test_sl2z_is_generated_by_elements_of_orders_four_and_six_amalgamated_over_minus_one`

Defective call: src/sage_extensions/language_runtime.py:68 (`matrix`).

Introduced by: 14b9cc1 (2026-10-26, Zack Garza) 'Move the session namespace and the mathematics test suite from research'; blamed at :68.

Scope: the session's `matrix`; one test. Measured candidate repair, NOT landed: accepting the ring-first form makes `matrix(ZZ, rows)` answer, but the object it answers is `Generic endomorphism of Free module ...` -- an engine matrix-space element -- and `Groups.SL(2, ZZ)(...)` then refuses it with `it is a Sage object, not an element of a preamble group`. The arity and that engine crossing are one defect of this constructor.

Triage record: `results/issue411-triage.md` (C20), slice of #411.
