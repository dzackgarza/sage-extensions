`decomposition_group_class(p)` returns an object with no `.image`

The decomposition group at a prime --- what the decomposition/normalizer computation is stated
on, and what the test asks with `group.decomposition_group_class(2).image(quotient, prime)` ---
returns something that is not a map:

    AttributeError: 'Sets.parent_class[_DecompositionGroupConjugacyClassEngine].ObjectType'
    object has no attribute 'image'

When this closes, `decomposition_group_class(p)` answers a morphism on the conjugacy classes it
acts on, and "2 is inert in `Q(5^(1/2))`" is decided by the decomposition group of `2` there.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    tests/groups/test_galois_decomposition_archive.sage:21:
        group.decomposition_group_class(2).image(quotient, prime).order() == 2
    AttributeError: ... has no attribute 'image'

## Failing test

- `tests/groups/test_galois_decomposition_archive.sage::test_two_is_inert_in_the_field_of_root_five`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S
'decomposition_group_class'` over `categories/group` returns that commit alone.
