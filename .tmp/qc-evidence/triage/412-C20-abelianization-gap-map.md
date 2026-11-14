C20: The abelianization is refused because GAP hands back a whole-group map

`group.abelianization()` raises `TypeError: a GAP whole group map is private engine output; give generator images`. The engine's own answer is refused at the boundary and no generator images are synthesized, so `Q_8^ab` and `S_3^ab` cannot be computed -- the simplest functor out of the group category.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_quaternion_group.sage::test_the_abelianization_of_q8`
  `TypeError: a GAP whole group map is private engine output; give generator images`
- `tests/objects/test_symmetric_group_s3.sage::test_the_abelianization_of_s3`
  `TypeError: a GAP whole group map is private engine output; give generator images`

Defective call: the group carrier boundary that rejects a whole-group map (`src/sage_extensions/categories/group/`).

Introduced by: `6c381ad` (2026-11-01, agent, "fix: export the group owner, and compare the Sterk archive table in one representation"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); at `14b9cc1` the same test failed earlier with `AttributeError: 'Groups_with_category' object has no attribute 'abelianization'`.

Scope: the engine boundary for group maps, so it reaches every GAP-backed map: abelianization, derived subgroup, and the quotient machinery built on them.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C20).
