C05: The conjugation morphism hands a GAP whole-group map to the element constructor

`G.conjugation_morphism()`, the map that sends an element to its inner automorphism, raises `TypeError: a GAP whole group map is private engine output; give generator images`, so `Aut(G)` cannot be reached from `G` and no inner-automorphism subgroup, kernel or index can be computed.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_group_automorphisms_archive.sage::test_conjugation_realizes_all_automorphisms_of_s3`
  `TypeError: a GAP whole group map is private engine output; give generator images`
  at `src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_`
- `tests/groups/test_group_automorphisms_archive.sage::test_s6_has_outer_automorphisms_of_index_two`
  `TypeError: a GAP whole group map is private engine output; give generator images`
  at `src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_`
- `tests/groups/test_groups_archive.sage::test_conjugation_on_d4_has_the_centre_as_kernel_and_inner_group_v4`
  `TypeError: a GAP whole group map is private engine output; give generator images`
  at `src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_`
- `tests/groups/test_groups_archive.sage::test_conjugation_on_s3_is_an_isomorphism_onto_its_automorphism_group`
  `TypeError: a GAP whole group map is private engine output; give generator images`
  at `src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_`
- `tests/groups/test_mathieu_automorphism_archive.sage::test_m12_inner_automorphisms_have_index_two_in_the_full_automorphism_group`
  `TypeError: a GAP whole group map is private engine output; give generator images`
  at `src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_`

Defective call: src/sage_extensions/categories/group/groups.py:5993 (conjugation_morphism) calls `automorphisms(libgap.ConjugatorAutomorphism(...))`, which is the public element constructor refusing at :4572.

Introduced by: not bisected: both the refusal (:4572) and the call that trips it (:5993) are in the root commit c731175 (2026-10-26, Zack Garza); the line was blamed there.

Scope: one call site and the five tests that conjugate. Measured candidate repair, NOT landed: routing the conjugator through the documented protected crossing `automorphisms._from_engine_morphism(...)` builds the map and moves every one of the five to its next defect -- `AttributeError: 'OwnedGroupAutomorphismGroup...ArrowType' object has no attribute 'gap'` from `kernel()`, and M12's file did not finish in 360 s where it used to fail in 0.87 s -- so the crossing alone is not a repair.

Triage record: `results/issue411-triage.md` (C05), slice of #411.
