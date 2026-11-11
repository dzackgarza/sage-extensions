# #315 — the line-stabilizer image refuses where Eichler's criterion does not apply

Commit: (filled at commit time, `main`).

## What changed

`src/sage_extensions/categories/orthogonal_quotients.py`,
`OrthogonalCharacterQuotient.isotropic_line_stabilizer_image`:

- the "sandwich" paragraph in the docstring and the sandwich comment are deleted;
- the refusal `if not _two_hyperbolic_planes(lattice): return None` is restored
  before the class-set computation, so the claim is made only where Eichler's
  criterion applies to `L` itself (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503:
  two orthogonal hyperbolic planes in `L`);
- the docstring states the criterion's hypothesis, why an enlargement does not
  transfer it, and the invariant that does decide the orbits
  (`v^\perp/Z v`, Conway--Sloane, *SPLAG*, ch. 16).

Behaviour: a lattice with fewer than two hyperbolic planes gets `None` from the
call (the pre-existing refusal the callers already handle: they keep their exact
integral route), instead of a class set certified by the invalid argument.

## Acceptance item 1 — measured

Command (repository pytest, Sage Python, port source ahead on `PYTHONPATH`):

```
/sage/.venv/bin/python -m pytest -p qc_sage_session -o addopts="" -q --tb=short --durations=0 \
  tests/lattices/test_line_stabilizer_image_requires_eichlers_hypothesis.sage
```

Result: **2 passed in 2.03 s**, exit 0; the refusal call 0.77 s, the enlargement
call 0.02 s (`--durations=0`). Log: `.tmp/p315-gate-new.log`.

Before the repair, the same call on the same specimen does not return:

```
L.O_plus().finite_character_quotient().isotropic_line_stabilizer_image(<e_0>)
  at 82715b7c94   did not return in 900 s (inner cap, exit 124)
```

Log: `.tmp/issue315-probe6.log`. So the test bites: it fails (hangs) at the base
commit and passes with the refusal.

## Acceptance item 2 — the card

`dzackgarza/lattice-database`, card **`0236`**: `name: U + E8(-1)^2`,
`aliases: ['II_{1,17}', '(r, a, delta) = (18, 0, 0)']`, rank 18, signature (1, 17),
determinant -1, in the `even-unimodular` and `nikulin-two-elementary` families.

It carries **no orbit row**. Its certification rows are
`derive, form.integer_valued, root_span.roots, root_span.norms,
integral.elementary_primes, integral.genus_symbol, integral.genus_class_count,
integral.overlattice_count, integral.spinor_genus_count, integral.spinor_genera,
integral.hyperbolic_index, hyperbolic.reflective, integral.modular_scale,
integral.anisotropic_primes, integral.local_representations,
integral.local_densities`, and its `integral:` block has no `primitive_orbits`
key. The row shape the repository reads is card `029J`'s
`integral.primitive_orbits.{O,gamma-en-2}` with `constant`, `planes` and a
`reference.citation`.

No arithmetic-group card over `0236` exists either (the `arithmetic-groups`
index lists `029J`, `6JRR`, `028S` only).

So the acceptance-item-2 test cannot be written against a card value now, and no
number is typed into the test. What the probes do and do not establish is below.

## What is established about the specimen

- `L = U + E8(-1)^2`: rank 18, signature (1, 17), determinant -1,
  `hyperbolic_plane_summand_count() == 1`, `_two_hyperbolic_planes(L)` False,
  `L.eichler_criterion_applies()` False.
- `L + U`: `_two_hyperbolic_planes` True and `eichler_criterion_applies()` True,
  so the deleted branch is exactly the one that would have fired.
- The count of `O(L)`-orbits of primitive isotropic vectors is **not** decided
  here. `L.Aut().isotropic_orbit_representatives(1)` did not return in 1800 s
  (`.tmp/issue315-probe7.log`), and the reductions `v^\perp/Z v` of five
  constructed primitive isotropic vectors came out rank 16, determinant 1,
  signature (0, 16) but were compared with `is_isometric`, which is
  `not Isom(other).is_empty()` and answers truthily on two definite lattices of
  equal determinant (`TRAPS.md`, *`is_isometric` is not a lattice-class test*).
  So those comparisons decide nothing, and the file asserts no count.

## Positive control: the refusal is not a blanket refusal

Same call, lattices that do split two hyperbolic planes (`L.O_plus()`):

| specimen | rank, det | result | time |
| --- | --- | --- | ---: |
| `U + U + E8(-2)` | 12, 256 | `NOSPLIT` | 15.6 s |
| `U + U + E8(-1)` | 12, 1 | `NOSPLIT` | 25.0 s |

Log: `.tmp/issue315-probe8.log`.

## Regression

```
/sage/.venv/bin/python -m pytest -p qc_sage_session -o addopts="" -q --tb=line --durations=0 \
  tests/lattices/test_eichler_orbits.sage \
  tests/lattices/test_isotropic_orbit_collections.sage \
  tests/lattices/test_primitive_orbit_series_on_indefinite_lattices.sage
```

- with the repair: **2 failed, 8 passed in 748.21 s**, exit 1;
- the same tree at `82715b7` (worktree `.scratch/base315`), the same file that
  fails: `tests/lattices/test_eichler_orbits.sage` **2 failed, 4 passed in
  122.49 s**, exit 1, the **same two FAILED ids**
  (`test_the_criterion_reads_its_hypothesis_off_the_decomposition`,
  `test_raw_gram_factor_does_not_count_as_a_represented_u_summand`).

Logs: `.tmp/p315-gate-setA.log`, `.tmp/p315-gate-base-eichler.log`.

## Not done here

- The card-comparison test of acceptance item 2 — it needs card `0236`'s
  `integral.primitive_orbits` row to exist.
- The `Gamma_h` line rows of `tests/lattices/test_enriques_polarization_orbits.sage`
  route through `_subgroup_isotropic_orbit_representatives`, which after the refusal
  falls back to the integral stabilizer on `T_En` (one hyperbolic plane).  One case
  measured on both trees:

  ```
  ...::test_the_source_line_row_is_the_public_line_orbit_count[case-3]
    at 82715b7                    1 passed in 128.61 s (test call 126.92 s)
    with the refusal              F, then killed at the 1800 s inner cap
                                  (launcher exit 124); pytest never flushed the
                                  failure summary -- its teardown does not return
                                  under proot, and a `--tb=long` attempt segfaulted
                                  in CPython while formatting the traceback
                                  (inspect.getmodule)
  ```

  Logs: `.tmp/p315-enriques-case3-base.log`, `.tmp/p315-enriques-case3-after*.log`.
  This is the cost of removing the false certificate, and the repair for those rows
  is the character-quotient index route of #17, not a reinstated sandwich.  The
  exception the fallback raises is not identified here: it was lost to the teardown.
