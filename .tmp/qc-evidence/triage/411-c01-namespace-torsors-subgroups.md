C01: The session namespace does not publish the subgroup constructors the suite names

A user who writes the session-standard import cannot name a subgroup category at all: `Subgroups(G)`, `GeneratedSubgroups(G)` and `Torsors(G, action)` raise `NameError`, so every question about a subgroup, a generating family or a torsor has to reach into a private module.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_g_sets_torsor_archive.sage::test_the_transporter_of_the_regular_c3_torsor_from_x_to_gx_is_g`
  `NameError: name 'Torsors' is not defined`
  at `tests/groups/test_g_sets_torsor_archive.sage:20: in test_the_transporter_of_the_regular_c3_torsor_from_x_to_gx_is_g`
- `tests/groups/test_group_morphisms_archive.sage::test_noninjective_group_map_factors_through_its_proper_image`
  `NameError: name 'Subgroups' is not defined`
  at `tests/groups/test_group_morphisms_archive.sage:148: in test_noninjective_group_map_factors_through_its_proper_image`
- `tests/groups/test_group_morphisms_archive.sage::test_generated_subgroup_finite_image_lifts_use_its_selected_generators`
  `assert {1, (1 3)(2 4)} == {(1 3)(2 4), 1}`
  at `tests/groups/test_group_morphisms_archive.sage:183: in test_generated_subgroup_finite_image_lifts_use_its_selected_generators`
- `tests/groups/test_group_morphisms_archive.sage::test_generated_subgroup_map_image_uses_its_retained_generator_family`
  `NameError: name 'Subgroups' is not defined`
  at `tests/groups/test_group_morphisms_archive.sage:199: in test_generated_subgroup_map_image_uses_its_retained_generator_family`
- `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_group_equalizer_has_its_subgroup_inclusion_and_universal_map`
  `NameError: name 'Subgroups' is not defined`
  at `tests/groups/test_group_products_and_coproducts_of_presentations.sage:273: in test_group_equalizer_has_its_subgroup_inclusion_and_universal_map`

Defective call: src/sage_extensions/all.py (the group import block); the names are defined at categories/group/groups.py:8204 (Subgroups), :8358 (GeneratedSubgroups) and categories/group/g_sets.py:1832 (Torsors).

Introduced by: not bisected: the namespace never published these names, so their absence is at main's root commit c731175 (2026-10-26, Zack Garza), which imported the suite; the file was run there and the failing tests fail there too.

Scope: the session namespace itself, not three names: `all.py` restates the area packages' public surfaces by hand, and the copy has drifted. `sage_extensions/groups/__init__.py` already declares `Subgroups` and `Torsors` in its `__all__` (and does not declare `GeneratedSubgroups`, which its owner module defines), so publishing the owners' declarations and declaring the missing name is the repair; editing three names into the copy leaves the mechanism in place. That reaches every name in the session, so it is filed and not patched here. It is the same cause as #408's, whose hand-added names were reverted for this reason (`50a83cb`). Measured, not landed: adding the three names to `all.py` cleared four of these five tests and left the fifth reporting its next defect, a Python `set` of group elements whose equality disagrees with the owned set.

Triage record: `results/issue411-triage.md` (C01), slice of #411.
