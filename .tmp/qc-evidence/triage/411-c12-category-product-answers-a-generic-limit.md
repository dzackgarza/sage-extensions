C12: `Groups().product` and `Groups().coproduct` answer the generic limit object

`Groups().product((C_2, C_3))` answers `Product of the family over {0,...,1}`, which is not an object of `Groups()` (and the same for `coproduct`), so the category-level product of groups cannot be asked its order or compared with `C_6`.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_groups_archive.sage::test_finite_group_product_retains_group_structure_and_order`
  `assert Product of the family over {0,...,1} in Category of groups`
  at `tests/groups/test_groups_archive.sage:9: in test_finite_group_product_retains_group_structure_and_order`
- `tests/groups/test_groups_archive.sage::test_group_coproduct_is_the_owned_free_product`
  `assert Coproduct of the family over {0,...,1} in Category of groups`
  at `tests/groups/test_groups_archive.sage:37: in test_group_coproduct_is_the_owned_free_product`

Defective call: `Groups().product` / `Groups().coproduct` (the categorical limit in categories/abstract_categories/products.py), which answers the generic limit rather than the owned group construction that `product_construction` builds.

Introduced by: not bisected: the failure is reached through C03 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.

Scope: the category-level product and coproduct of groups; two tests.

Triage record: `results/issue411-triage.md` (C12), slice of #411.
