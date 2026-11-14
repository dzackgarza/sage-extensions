C23: `q` of a lattice is the doubled quadratic form

`lattice.q(e0) == -1` fails with `-2 == -1` for `A_2` with `b(e0, e0) = -2`: the selected norm `q` returns `b(x, x)` where the test states `q(x) = b(x,x)/2`. One of the two conventions is wrong and the library does not say which in the operation's own docstring, so a user cannot tell which quadratic form they are computing with.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_root_lattice_a2.sage::test_the_invariants_of_a2`
  `assert -2 == -1`

Defective call: `FormModules.ParentMethods.q`/`norm` (`src/sage_extensions/categories/modules/framed/formed/form_modules.py:2140`).

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the test fails there with this same signature, so the assertion has never been green on main.

Scope: the selected-norm operation on every formed module, so the repair must state the convention once and apply it everywhere; this slice's one test is the statement of it.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C23).
