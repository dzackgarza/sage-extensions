The Enriques line stabilizer's generator family does not return, so `test_a_stabilizers_generators_generate_a_subgroup.sage` never finishes

`O(T_En)`'s setwise stabilizer of a primitive isotropic line is constructed in about two
seconds, and then asking it for its generators does not return: a session that wants the
subgroup those generators generate waits indefinitely, and #341's acceptance file never
finishes -- 1 of its 3 tests passes, the second is still running when the run is killed at
2400 s, the third never starts. When this closes, `stabilizer.group_generators()` answers
the family, `group.subgroup(family)` is constructed from it, and the third test -- the
`U` over `Z` specimen where `G.subgroup((swap,))` must refuse -- runs.

Every step is timed by `issue407-probe-stabilizer-steps.py`, whose whole output is
`issue407-probe-stabilizer-steps.log`:

    [     1.8s] import sage_extensions.all
    [     1.9s] lattice.O() -> Orthogonal group O(Integral lattice of rank 12 and signature (2, 10))
    [     2.2s] primitive_isotropic_subobject -> Integral lattice of rank 1 and signature (0, 0)
    [     2.2s] stabilizer -> {g in O(...) : g(im(...)) = im(...)}
    ... no further mark: `tuple(stabilizer.group_generators())` does not return

and the run of the file itself, `issue407-stabilizer-file.log`:

    tests/groups/...::test_a_generated_groups_line_stabilizer_generates_a_subgroup PASSED [ 33%]
    tests/groups/...::test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup Killed
    exit=137
    [peakrss] peak tree RSS : 1304 MiB

1304 MiB at the kill, so this is a computation that does not terminate, not one that runs
out of memory.

## Failing tests of this cause

- `tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage::test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup` (does not return)
- `tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage::test_a_family_outside_the_group_is_refused` (never starts: the file's second test has not returned)
- `tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage::test_a_generated_groups_line_stabilizer_generates_a_subgroup` passes, and is listed so the three tests of the file are accounted for.

## Relation to #384

#384 is `_GapWordSection.permutation_group` rebuilding `Group(gens)`, and its route is
`discriminant_lift -> letters_of -> permutation_group`.  This hang is **not** that route:
`issue407-probe-stabilizer-section.py` instruments `_GapWordSection.__init__`,
`.permutation_group` and `.gap_group` and its whole output
(`issue407-probe-stabilizer-section.log`) shows the stabilizer built and then nothing --
no `_GapWordSection` is constructed at all before the hang.  #384's *other* engine site is
still a candidate: `orthogonal_quotients.py:151` and `groups.py:671` build
`IsomorphismPermGroup(Group(...))` models, and one of those may be what the stabilizer's
generator computation enters.  That is not established here.  If the owner finds this is
#384's, close this as that issue's; the measurement that separates them is which of the two
engine constructions is entered, and no `_GapWordSection` is entered on this path.

## Cause and introducing commit

The test file arrived at `e87f372` (2026-11-11), so a bisect on `main` is bounded below by
that commit; the library path it exercises is the initial import's. No commit on `main`
carries the file green.
