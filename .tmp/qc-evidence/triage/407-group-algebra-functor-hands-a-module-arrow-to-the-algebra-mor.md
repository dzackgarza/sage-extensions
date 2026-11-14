The group-algebra functor builds its arrow in the wrong Mor and CON-17 refuses it

`R[f]` for a group morphism `f` --- the image half of `GroupAlgebraFunctor`, and so what
induction and coinduction of modules are made of --- raises:

    TypeError: Generic morphism: ... belongs to Free module on ..., not to
    Mor_UnitalAlg(R[G], R[H]); apply the functor between the categories instead of
    constructing an arrow from another arrow (CON-17)

When this closes, `R[f]` is constructed through the functor that owns it, and the induced and
coinduced `Z/4`-modules of `C_2 <= S_3` are three copies of `Z/4`.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    src/sage_extensions/categories/algebras/group_algebras.py:305: in _apply_morphism
        return Algebras(source.base_ring()).Associative().Unital().Mor(source, target)(linear)
    src/sage_extensions/categories/abstract_categories/mor_foundation.py:57: TypeError

`linear` is an arrow of `source.module_category()`'s Mor; the algebra Mor refuses an arrow
belonging to another Mor, which is the CON-17 rule the library states for itself.

## Failing tests

- `tests/groups/test_group_adjunctions.sage::test_inducing_the_z4_sign_module_from_c2_to_s3_gives_three_copies_of_z4`

## Cause and introducing commit

`c731175` (Zack Garza, 2026-10-26, the initial import): `git log -S 'apply the functor
between'` over `mor_foundation.py` returns that commit alone, and so does the caller's line.
The guard and its caller arrived together and disagree.
