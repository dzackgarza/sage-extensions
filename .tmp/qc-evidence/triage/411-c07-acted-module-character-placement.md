C07: An acted group module is not placed in its character-representation category

`Modules(R[G])(M, action).character()` and `.brauer_character()` raise `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`; the ordinary and Brauer character surfaces exist, but the module the user builds is never placed in the category that carries them.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_group_law.sage::test_the_natural_permutation_module_of_s3_has_character_3_1_0`
  `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`
  at `tests/groups/test_group_law.sage:25: in test_the_natural_permutation_module_of_s3_has_character_3_1_0`
- `tests/groups/test_module_characters.sage::test_the_character_of_sign_plus_trivial_of_s3_is_2_0_2`
  `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`
  at `tests/groups/test_module_characters.sage:15: in test_the_character_of_sign_plus_trivial_of_s3_is_2_0_2`
- `tests/groups/test_module_characters.sage::test_the_2_modular_brauer_character_of_the_order_three_action_of_c6_on_f2_squared_is_2_minus1_minus1`
  `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'brauer_character'`
  at `tests/groups/test_module_characters.sage:32: in test_the_2_modular_brauer_character_of_the_order_three_action_of_c6_on_f2_squared_is_2_minus1_minus1`

Defective call: the acted-module route, `Modules(R[G])(module, action)`; the surface it does not reach is categories/modules/group_modules/group_modules.py:1738 (OrdinaryCharacterRepresentations.character) and :1777 (BrauerCharacterRepresentations.brauer_character).

Introduced by: not bisected: the categories and their `_call_` refinements are in the root commit c731175 (2026-10-26, Zack Garza), and the acted-module constructor never refines into them.

Scope: the placement of an acted module; three tests, ordinary and modular.

Triage record: `results/issue411-triage.md` (C07), slice of #411.
