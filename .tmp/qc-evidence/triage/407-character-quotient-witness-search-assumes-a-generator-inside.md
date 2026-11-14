The character-quotient witness search assumes a nonidentity generator lies in the intersection

`test_adjust_witness_into_subgroup_matches_elementwise_search` picks its witness with

    inside = next(g for g in G.group_generators() if g in inter and g != G.one())

and raises `StopIteration`: on the model the test builds, no generator of `G` other than the
identity lies in `inter`. One of two things is wrong and this issue is to decide which: the
intersection `inter` is smaller than the mathematics says (a subgroup or membership defect), or
`G.group_generators()` is a family whose nonidentity members miss `inter` (a generator-family
defect). When this closes, the witness exists and the adjusted witness equals the elementwise
search's.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    tests/groups/test_generated_model_character_quotient.sage:158: StopIteration

## Failing test

- `tests/groups/test_generated_model_character_quotient.sage::test_adjust_witness_into_subgroup_matches_elementwise_search`

## Cause and introducing commit

This test arrived at `fd5ab11` (2026-11-02), later than the rest of the slice, so a bisect on
`main` is bounded below by that commit rather than by the imports; the library code it
exercises is the initial import's `c731175`.
