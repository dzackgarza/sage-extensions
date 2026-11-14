C15: A group carries no `abelianization`, and the functor refuses presented groups

`G.abelianization()` raises `AttributeError: ... object has no attribute 'abelianization'`: the functor is published only on the category (`Groups().abelianization()`), and for a finitely presented group that functor refuses with `AssertionError: the abelianization of the finitely presented group ... is defined, but the current preamble has no presentation-quotient route for G/[G,G]`.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_owned_groups.sage::test_the_abelianization_of_the_free_product_of_c2_and_c3_is_c6`
  `AttributeError: 'OwnedJoinCategory.parent_class[_GroupEngine].ObjectType' object has no attribute 'abelianization'`
  at `tests/groups/test_owned_groups.sage:34: in test_the_abelianization_of_the_free_product_of_c2_and_c3_is_c6`

Defective call: the group's own surface (absent), and src/sage_extensions/categories/functors/abelianization.py:52 (the presented-group refusal).

Introduced by: not bisected: the category-level functor and its presented-group refusal are in the root commit c731175 (2026-10-26, Zack Garza); blamed at abelianization.py:52. The same refusal is #408's C37.

Scope: the abelianization of a group, as an object method and for presented groups; one test. The named repair is a quotient route G/[G,G] at the exact-sequence owner, which is a decision about coset enumeration, not a local patch.

Triage record: `results/issue411-triage.md` (C15), slice of #411.
