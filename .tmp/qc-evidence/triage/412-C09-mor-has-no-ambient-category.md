C09: `Mor(A, B)` of two predicate subsets has no ambient category

`subset.Mor(subset).identity()` is refused because `Mor(Subset, Subset)` is said to have no ambient category: the homset of a condition-set is not placed in the category its objects are in, so no morphism can be constructed in it.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_positive_integers.sage::test_the_positive_integers_have_one_endomorphism_category`
  `AssertionError: Mor(Subset of Integer Ring cut out by <function positive.<locals>.<lambda> at 0x7dbf99a72610>, Subset of Integer Ring cut out by <function positive.<locals>.<lambda> at 0x7dbf99a72610>) has no ambient category: no category above the ambient category Category of sets of Subset of Integer Ring cut out by <function positive.<locals>.<lambda> at 0x7dbf99a72610>, short of sets, contains Subset of Integer Ring cut out by <function positive.<locals>.<lambda> at 0x7dbf99a72610> (it lies in Join of Category of facade sets and Category of sets); name the category whose arrows are meant`

Defective call: the `Mor` of an owned condition set.

Introduced by: `caa3825` (2026-10-26, D. Zack Garza, "Initialize categorical isomorphisms from their selected Mor"), the first commit on main's mainline where this signature appears (bisect in the published image over `--first-parent 14b9cc1..c8a3ced`, the cause's own test as the predicate); the same test passed at `14b9cc1`, so this is a regression on main.

Scope: the hom constructor for predicate-cut sets.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C09).
