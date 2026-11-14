C18: The base ring's scalar action on a group-algebra module element is refused

`QQ(2)/QQ(3) * total`, scaling a module element by a base-ring element, raises `TypeError: unsupported operand parent(s) for *: 'Fraction Field of Integer Ring' and 'Module over Group algebra of Symmetric group S_3 ...'`, so a linear combination with rational coefficients cannot be written.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_restricted_actions.sage::test_reflection_in_the_trivial_line_is_plus_one_on_standard_and_minus_one_on_invariants`
  `TypeError: unsupported operand parent(s) for *: 'Fraction Field of Integer Ring' and 'Module over Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring on Free module on {[0], [1], [2]} over Fraction Field of Integer Ring'`
  at `tests/groups/test_restricted_actions.sage:71: in test_reflection_in_the_trivial_line_is_plus_one_on_standard_and_minus_one_on_invariants`

Defective call: the left scalar action on an acted module element (the ring element's `__mul__` does not reach the module's scalar multiplication).

Introduced by: not bisected: the failure is reached through C03 and C04 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.

Scope: the scalar action on module elements over a group algebra; one test.

Triage record: `results/issue411-triage.md` (C18), slice of #411.
