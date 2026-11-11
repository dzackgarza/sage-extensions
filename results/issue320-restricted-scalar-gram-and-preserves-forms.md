# #320 — a formed submodule over restricted scalars: its Gram matrix and `preserves_forms`

Two defects on one object: `Res_ι ℚ` is ℚ read as a ℤ-module, and a formed module whose
values lie in it is the shape every lattice in the lattice-database Höhn–Mason intake
has (`res-29`, record 02AQ: `A ⊂ leech[1]`, ambient rank 24, subobject rank 19).

## 1. `gram_matrix()` raised

On `main` at `9c3abc0`, with the value object `free module on {[0]} over QQ restricted to
ZZ`, `gram_matrix()` reads the value object for a matrix space it does not have:

```
  File "src/sage_extensions/categories/modules/framed/formed/form_modules.py", line 4119, in gram_matrix
    .matrix_space(size, size)
AttributeError: 'RestrictedScalarsModules.parent_class' object has no attribute 'matrix_space'
```

The repair: the Gram matrix's entries are the form's values *read as scalars of one
ring*, and that ring supplies the matrix space.  `_scalar_value_identification`
(next to `_regular_module_scalar_identification` in `modules/pure/modules.py`) is now
the single reading — a value object that is a ring's own regular module, or a
restriction of scalars from one — and `gram_matrix` builds the coordinate matrix from
the form's Gram tensor, which for a pulled-back form is the ambient Gram tensor
transported along the basis, `B G Bᵗ`, taken once.  A non-ring value object with no
such reading refuses with a `TypeError` naming it instead of an `AttributeError` from a
missing method.

## 2. `preserves_forms` expanded a tensor per entry

`_form_square_commutes` gates its Gram-tensor comparison on the value object's
*extension* being an owned ring.  For `Res_ι ℚ` the extension is `ℚ`'s regular module,
not `ℚ`, so the gate was closed and the decision fell through to one `b` evaluation per
pair of generators — and to `_mapped_value` per pair — which expands a pure tensor at
each entry.

The repair opens the gate with the same owner reading: both value objects must read
their elements as scalars of one ring.  No second code path was added; the existing
tensor branch is the decision, and it now states the case its own docstring already
described ("values in the same R-algebra S, regarded as an R-module by restriction of
scalars").  `_as_numerical_tensor` uses the same helper instead of carrying its own
copy of the reading.

### Measurement (not an assertion)

`preserves_forms(R, A)` on the rank-19 case, `R` the record lattice on card 02AQ's Gram
tensor and `A` the coinvariant subobject of `leech[1]`, both built with
sage-extensions only from the stored basis and Gram data:

| | before | after |
|---|---|---|
| one `preserves_forms(R, A)` | did not return within the 1500 s cap (`launcher exit 124`) | `True` in **1.04 s** |

Supporting numbers on the same subobject before the repair: one `b(x, x)` costs
**77.93 s** on its first call (0.001 s on the same element afterwards, so the cost is the
per-pair expansion, not one construction), against **0.353 s** for its Gram tensor; the
decision makes 19 × 19 pairs.

## Red and green

The test module is `tests/modules/test_formed_submodule_over_restricted_scalars.sage`:
the submodule `S ⊂ V` on four stated rows `B` of `V = ℤ⁸` with `E₈`'s Gram matrix over
`Res_ι ℚ`, asserting `G_S = B G_V Bᵗ` entry by entry, `G_S` symmetric with
`b(e_i, e_i)` read as a rational on its diagonal, and the decisions on the identity, on
`−1` and on the map that doubles one basis vector.

Pre-fix worktree (`9c3abc0`, the fetched `main`), same test file:

```
FAILED tests/modules/test_formed_submodule_over_restricted_scalars.sage::test_the_gram_matrix_of_the_submodule_is_the_pulled_back_ambient_gram
FAILED tests/modules/test_formed_submodule_over_restricted_scalars.sage::test_the_submodule_gram_is_symmetric_with_the_norm_of_each_basis_vector_on_its_diagonal
2 failed, 1 passed in 4.06s
```

After the repair:

```
3 passed in 2.61s
```

The third test — the decisions — passes on `main` too: on a small submodule
`preserves_forms` already answers correctly (identity and `−1` True, doubling a basis
vector False); only its cost is wrong.  There is therefore no *behavioural* red test for
the second defect that is committable here: the test standard forbids a time assertion
and forbids mocks, and the two routes agree on every decision measured.  The red
evidence for defect 2 is the measurement above.

## Gate

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates --no-test-lint tests/modules tests/forms tests/tensors
```

`tests/modules tests/forms tests/tensors`, before (clean worktree at `9c3abc0`) and after
(this commit):

```
baseline : 161 failed, 327 passed, 1 warning in 522.78s
after    : 161 failed, 330 passed, 1 warning in 506.20s
diff of the FAILED id sets: identical
```

The 161 failures are the tree's at `9c3abc0`, not this change's; the three extra passes
are this test module's three tests.  `--no-time-gates` is needed because the collection
ceiling (6 s) is measured on the default 26-test tree and this selection collects 135
files (34 s); `--no-test-lint` because the wide selection carries 181 pre-existing lint
findings.  The touched test module itself passes the lint:

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  tests/modules/test_formed_submodule_over_restricted_scalars.sage
3 passed in 2.61s      (no lint findings, no gate failures)
```
