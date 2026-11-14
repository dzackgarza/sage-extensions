C23: A character is not a member of the set of irreducible characters

`group.trivial_character() in group.irreducible_characters()` is false, printing the trivial character as a member of a three-element set that contains a character of the same degree: the equality (or the hash) of two `Character` objects does not decide membership.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_groups_archive.sage::test_archived_finite_group_character_surface_is_live_on_the_owned_group`
  `assert Character of degree 1 of Symmetric group S_3 in {Character of degree 1 of Symmetric group S_3, Character of degree 2 of Symmetric group S_3, Character of degree 1 of Symmetric group S_3}`
  at `tests/groups/test_groups_archive.sage:146: in test_archived_finite_group_character_surface_is_live_on_the_owned_group`

Defective call: the membership test at tests/groups/test_groups_archive.sage:146 over the characters built by `irreducible_characters()` / `trivial_character()`.

Introduced by: not bisected: the character surface is in the root commit c731175 (2026-10-26, Zack Garza).

Scope: equality and membership of finite-group characters; one test.

Triage record: `results/issue411-triage.md` (C23), slice of #411.
