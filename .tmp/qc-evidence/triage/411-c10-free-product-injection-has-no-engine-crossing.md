C10: The free-product injection has no engine crossing

Taking a factor injection out of a free product raises `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'` (after `KeyError: <id>`), so a free product's structure morphisms, and every cocone factorization through them, cannot be produced.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_free_product_of_infinite_free_and_finite_cyclic_groups`
  `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'`
  at `src/sage_extensions/categories/group/groups.py:5417: in injection`
- `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_free_product_factors_a_cocone_into_a_non_gap_predicate_group`
  `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'`
  at `src/sage_extensions/categories/group/groups.py:5417: in injection`

Defective call: src/sage_extensions/categories/group/groups.py:5417 (injection of the free product), on the arrow type `OwnedIndexedFreeGroupMor`.

Introduced by: not bisected: the injection and its arrow type are in the root commit c731175 (2026-10-26, Zack Garza); blamed at :5417.

Scope: the free-product structure morphisms; two tests.

Triage record: `results/issue411-triage.md` (C10), slice of #411.
