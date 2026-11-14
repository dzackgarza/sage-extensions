C03: A finite owned group is not a member of `FiniteGroups()`

`a2().O()`, `Groups.Q(8)` and `Groups.S(3)` are finite groups whose order the library states, but `group in FiniteGroups()` is `False` for all three. A user who asks whether the library's own group is finite -- the first question any homological or representation computation asks -- gets `False` for groups the library computes the order of.

Failing tests (3, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_orthogonal_group_of_a2.sage::test_o_a2_is_the_dihedral_group_of_order_twelve`
  `assert Orthogonal group O(Integral lattice of rank 2 and signature (0, 2)) in Category of finite groups`
- `tests/objects/test_quaternion_group.sage::test_the_categories_of_q8`
  `assert Quaternion group Q_8 in Category of finite groups`
- `tests/objects/test_symmetric_group_s3.sage::test_the_categories_of_s3`
  `assert Symmetric group S_3 in Category of finite groups`

Defective call: the owned group categories' membership; `Groups.Q(8)` and `Groups.S(3)` are owned specimens and `O(A_2)` is an owned orthogonal group.

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: type object 'Groups' has no attribute 'Q'`.

Scope: every owned finite group, so it reaches the group slices and every test that asks membership before asking a group question.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C03).
