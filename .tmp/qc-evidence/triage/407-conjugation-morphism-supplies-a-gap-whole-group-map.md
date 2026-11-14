`G.conjugation_morphism()` hands `Aut(G)` a GAP whole-group map, and `Aut(G)` refuses it

The conjugation morphism `G -> Aut(G)` that every finite group supplies raises:

    TypeError: a GAP whole group map is private engine output; give generator images

When this closes, `group.conjugation_morphism()` answers the morphism stated on generator
images, and the inner-automorphism indices of `S_3`, `S_6` and the Mathieu groups are
computable.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/group/groups.py:5992: in conjugation_morphism
        generator: automorphisms(libgap.ConjugatorAutomorphism(model, ...))
    src/sage_extensions/categories/group/groups.py:4572: in _element_constructor_
        raise TypeError("a GAP whole group map is private engine output; give generator images")

## Failing tests

- `tests/groups/test_finite_group_automorphisms_archive.sage::test_conjugation_realizes_all_automorphisms_of_s3`
- `tests/groups/test_finite_group_automorphisms_archive.sage::test_s6_inner_automorphisms_have_index_two`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): both the caller
(`libgap.ConjugatorAutomorphism(`) and the refusal (`case GapElement():`) are that commit's
text, and `git log -S` on each returns it alone. The two halves arrived together and are
inconsistent, so this pair has never been green on `main`.
