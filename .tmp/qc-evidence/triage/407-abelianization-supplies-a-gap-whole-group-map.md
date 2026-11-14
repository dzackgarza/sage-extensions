The abelianization functor hands `Mor(quotient)` a GAP whole-group map, and the Mor refuses it

`Groups().abelianization()(G)` --- and every adjunction whose unit is its quotient projection
--- raises:

    TypeError: a GAP whole group map is private engine output; give generator images

When this closes, `S_3^ab = C_2` and the abelianization adjunction's unit are computed on
generator images, and the functor tests below run.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/functors/abelianization.py:50: in _apply_object
        quotient_projection = group.Mor(quotient)(projection)
    src/sage_extensions/categories/abstract_categories/mor_foundation.py:61: in __call__
        return self._element_constructor_(*args, **kwargs)
    src/sage_extensions/categories/group/groups.py:4572: TypeError

## Failing tests

- `tests/groups/test_finite_group_subgroups_and_quotients.sage::test_the_abelianization_of_s3_is_c2`
- `tests/groups/test_free_and_catalogued_groups.sage::test_gap_group_morphism_requires_its_selected_endpoints`
- `tests/groups/test_functors_out_of_groups.sage::test_the_abelianization_adjunction_has_the_quotient_for_its_unit`
- `tests/groups/test_functors_out_of_groups.sage::test_the_abelianization_functor_kills_the_derived_subgroup`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S
'group.Mor(quotient)(projection)'` over `abelianization.py` returns it alone. The projection it
passes is the engine's whole-group map, which the same commit's `Mor` constructor refuses.

One test of this list, `test_gap_group_morphism_requires_its_selected_endpoints`, exercises
the refusal from the other side, as the thing it asserts; it is filed here because that is the
single defect it depends on.
