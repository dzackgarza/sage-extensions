C04: A reduced acted module cannot build the morphism that restricts it

`representation.restrict_action_to(sub.inclusion())` raises `TypeError: ... belongs to Free module on Product of the family over {0,...,1} ..., not to Mor_Alg(...); apply the functor between the categories instead of constructing an arrow from another arrow (CON-17)`, so an isotypic component or an invariant submodule of a group representation cannot be produced with its restricted action.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_restricted_actions.sage::test_the_standard_isotypic_component_is_the_standard_representation`
  `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free module on Product of the family over {0,...,1} over Fraction Field of Integer Ring, not to Mor_Alg(Free module on {[0], [1], [2]} over Fraction Field of Integer Ring, Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring); apply the functor between the categories instead of constructing an arrow from another arrow (CON-17)`
  at `src/sage_extensions/categories/algebras/group_algebras.py:96: in _finite_group_algebra_center`
- `tests/groups/test_restricted_actions.sage::test_the_invariants_of_the_permutation_module_are_the_trivial_representation`
  `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free module on Product of the family over {0,...,1} over Fraction Field of Integer Ring, not to Mor_Alg(Free module on {[0], [1], [2]} over Fraction Field of Integer Ring, Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring); apply the functor between the categories instead of constructing an arrow from another arrow (CON-17)`
  at `src/sage_extensions/categories/algebras/group_algebras.py:96: in _finite_group_algebra_center`

Defective call: src/sage_extensions/categories/modules/group_modules/group_modules.py:800 (restrict_action_to) into :1283 (_from_equivariant_images); the refusal is the Mor_Alg element-constructor check reached at src/sage_extensions/categories/abstract_categories/mor_categories.py:835.

Introduced by: not bisected: the failure is reached through C03 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.

Scope: the acted-module reduction; two tests.

Triage record: `results/issue411-triage.md` (C04), slice of #411.
