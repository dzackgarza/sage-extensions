The cardinality of `Mor_G(X, Y)` is undecided for finite `G`-sets

`Mor` in the category of `G`-sets has no cardinality: the equivariant self-maps of the regular
`C_3`-set are its three translations, but

    AssertionError: cannot compute the cardinality of Mor_Cyclic group C_3 of order 3(...):
    its construction supplies no exact value or decided finite enumeration

When this closes, the homset of two finite `G`-sets is enumerated --- it is the subset of the
`|Y|^|X|` set maps commuting with the action --- and the transporter of a torsor is counted.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/sets/set_categories.py:2503: AssertionError

## Failing test

- `tests/groups/test_g_sets_torsor_archive.sage::test_the_equivariant_self_maps_of_the_regular_c3_set_are_its_three_translations`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S 'its construction supplies
no exact value'` over `set_categories.py` returns that commit alone.
