# Issue body: the flag stabilizer's adapted basis is not unimodular under some hash seeds

Draft, because this project's GitHub connection reads issues and pushes commits
but cannot create one: file this with `gh issue create -F` or the web form.

**Title.** `flag_stabilizer`'s adapted basis is not unimodular under some values of `PYTHONHASHSEED`

**Body.**

An ambient flag row of `U + U(2) + <-2>` fails, four tests of the incidence gate
of `#381`/`#585`, under some values of `PYTHONHASHSEED`, and passes under
others, with no change to the tree. The failure is not in the incidence routes:

```
src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:4291
    flag_stabilizer -> change * generator * ~change
src/sage_extensions/categories/modules/pure/modules.py:7718
ZeroDivisionError: Generic endomorphism of Integral lattice of rank 2 and
signature (0, 0) has no inverse in ... over Integer Ring:
its determinant -2 is not a unit of Integer Ring
```

reached from the port's `IsotropicInduction.flag_action_data`
(`/repos/sage-indefinite-port/src/sage_indefinite_port/indefinite/isotropic_induction.py`,
`flag_action_data`, `domain.general_linear_group().flag_stabilizer(terms)`), as
the ambient flag row of `isotropic_orbit_representatives(2, flag=True)` builds
it.  The `change` the module automorphism group calls its adapted basis
(`_flag_stabilizer_engine_data` -> `_engine_flag_adapted_rows`'s
`right.inverse() * rows`) has determinant -2, so the "basis" it stacks is a
basis of an index-two sublattice and the conjugation cannot be inverted.

**What is hash-order dependent is not established.**  The call's terms are one
term (`flag_action_data(space, (term,))`), so the chain's order is not it; the
candidates are the `finite_ordered_set` ingress of the flag
(`flag_stabilizer`'s `case _ if flag in Sets()`), the Smith-form rebase, and the
induction's own caches.  A `tracemalloc`/`sys.settrace` run at a failing seed
that prints the adapted rows, the Smith diagonal and the stacked determinant is
the measurement that decides it, and it is not in this draft.

**Reproduction, as measured.**  An export of `main` `43e0f72`
(`git archive 43e0f72 | tar -x`; the commit hash the copy carries is irrelevant,
the source is the commit's):

```
PYTHONHASHSEED=1 <runtime>/sage/.venv/bin/python -m pytest -o addopts= \
  -p qc_sage_session -p sage_extensions.testing.suite_budget -q \
  tests/lattices/test_the_incidence_decided_by_divided_classes.sage \
  tests/lattices/test_a_row_computes_one_plane_covering.sage \
  tests/lattices/test_the_incidence_line_vertex_is_named_by_the_finite_image.sage
```

fails `test_the_class_route_and_the_flag_row_agree_for_the_otilde_row_of_u_u2_m2`,
`..._otilde_plus_row_of_u_u2_m2`, `test_the_otilde_row_computes_one_plane_covering`
and `test_the_otilde_plus_row_computes_one_plane_covering` (4 failed, 4 passed,
30 s) and passes all eight at `PYTHONHASHSEED` 0, 2, 3 and 4 (45-58 s each).
The same three files pass in the unseeded runs of the same day.

**Why it matters.**  Every change that touches the incidence gate is red at some
seeds through no fault of its own, and a dispatch that reads the ambient flag
rows can hit a wrong adapted basis rather than an exception wherever the
determinant happens to be a unit -- the exception is the loud case, not the only
case.

**Owner.**  `ModuleAutomorphismGroup.flag_stabilizer` and
`_flag_stabilizer_engine_data` in `src/sage_extensions/categories/modules/`,
with `_engine_flag_adapted_rows` in `src/sage_extensions/tensors/tensor.py`;
the port's call site is read-only for this project.
