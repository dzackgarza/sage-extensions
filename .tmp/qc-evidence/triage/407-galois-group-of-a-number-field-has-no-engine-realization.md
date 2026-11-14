The absolute Galois group of a number field has no engine realization to compute with

`QQ.absolute_galois_group()`'s stage at a number field is constructed, but computing with its
normalizer raises:

    AssertionError: computation with Gal(Free module on {1, a} over Fraction Field of Integer
    Ring / Fraction Field of Integer Ring) through a group engine requires a selected
    realization; this group supplies none

When this closes, the Galois group of a number field either selects the engine that computes
it or refuses at construction, and `Gal(Q(5^(1/2)))`'s normalizer quotient is decided.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/group/groups.py:5739: in _engine_group
        assert False, ("computation with {self} through a group engine requires a selected "
                       "realization; this group supplies none")

## Failing test

- `tests/groups/test_galois_normalizer_archive.sage::test_the_normalizer_quotient_for_root_five_is_its_galois_group_of_order_two`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S 'requires a selected
realization'` over `groups.py` returns that commit alone.
