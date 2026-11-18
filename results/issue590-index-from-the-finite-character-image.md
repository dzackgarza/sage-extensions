# #590: a subgroup's index from its finite character image

`L = NamedLattices.Tco`, `G = L.stable_orthogonal_group()`.  The contract is the
issue's acceptance, item by item; each row names the declaration that decides it
and the measurement that settles it.

| acceptance item | declaration that decides it | file:line | measured |
| --- | --- | --- | --- |
| `G.index()` returns exactly 46,998,591,897,600 | `PredicateSubgroups.ParentMethods.index` → `OrthogonalCharacterQuotient.index`; the image order is `Lattices.ParentMethods.discriminant_representation_is_surjective_by_theorem` with `OrthogonalCharacterQuotient.discriminant_image_order` | `categories/group/predicate_subgroups.py:516`, `categories/orthogonal_quotients.py:856`, `categories/lattices.py:4337` | `46998591897600`, `7.11 s` on the first call in a fresh process, `0.00 s` cached |
| agrees with `G.finite_character_quotient().index()` | the same quotient method, reached directly | `categories/orthogonal_quotients.py:984` | `46998591897600`, `0.00 s` |
| does not enumerate image cosets | the route reads `O(A_L, q)`'s order from the discriminant form; the coset space is never realized | `categories/orthogonal_quotients.py:856` | with `_ambient_generators` replaced by a refusal that raises, `G.index()` still answers `46998591897600` in `8.41 s`; the same refusal makes `A_2`'s index raise, so the instrument is live.  Peak tree RSS `330 MiB` on the Coble runs |
| the 6JRR card certifies under its memory budget | the no-enumeration route, through the consumer's own worker | `latticedb/src/latticedb/sage_genus.py:128` → `:152` (the consumer's worker, unmodified) | the worker emits `{"tag": "6JRR", "by": "research preamble", "arithmetic-group.otilde-t-co.index_in_orthogonal_group": 46998591897600}` and `{"tag": "6JRR", "done": true}`, the value the card stores, in `18.73 s` at a peak tree RSS of `311 MiB`; the run it replaces was cut at `5609.903 s` and `14,061,043,712` bytes.  Called directly on the same group, `_index_in_orthogonal_group` answers in `0.92 s` |
| a small nontrivial finite-character regression | `test_the_two_routes_to_a_small_discriminant_kernel_agree`, `test_the_index_of_the_discriminant_kernel_of_the_coble_lattice_is_the_discriminant_group_order` | `tests/lattices/test_the_index_of_a_finite_character_subgroup.sage:39`, `:25` | index, quotient index and coset count all `2` on `U(2)`; the Coble index is card `6JRR`'s discriminant-group order |
| a generic subgroup regression | `test_a_subgroup_without_character_data_indexes_by_its_coset_count` | `tests/lattices/test_the_index_of_a_finite_character_subgroup.sage:89` | `3` for a transposition in `S_3`, `6` for a 4-cycle in `S_4`, `3` for the same subgroup re-cut by a bare predicate; the generic route is `Subgroups.ParentMethods.index` |

## Where the index came from, and why not from an ambient order

`rho_{T_Co}: O(T_Co) -> O(A_{T_Co}, q)` is onto because `T_Co` is even,
indefinite, nondegenerate and 2-elementary (Nikulin, *Integral symmetric
bilinear forms and some of their applications*, Math. USSR-Izv. 14 (1980),
103--167, Theorem 3.6.3), so the index of its kernel is `|O(A_L, q)|` -- the
finite group's own order, which the discriminant form supplies.  The four
hypotheses are decided on the Gram matrix
(`discriminant_representation_is_surjective_by_theorem`), and each of the three
lattices in `test_the_finite_image_order_is_certified_only_under_all_four_hypotheses`
that fails one of them -- definite, not 2-elementary, odd -- is asserted not to
be certified, so the theorem is not quoted outside them.

For a lattice outside the class the order still comes from a computation:
`rho` on the selected generating family of `O(L)`, and the order of the subgroup
those images generate.  That is the route `A_2` takes, and it agrees with the
coset count there.

## What was run

`sage 11.0.beta5`, `/sage/.venv/bin/python`, image
`ghcr.io/dzackgarza/sage@sha256:59568577...`, the source tree bound at `/work`:

```
$ python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
    -p sage_extensions.testing.test_lint --durations=0 \
    tests/lattices/test_the_index_of_a_finite_character_subgroup.sage
5 passed in 20.14s
 9.49s the Coble index   2.07s A_2   0.60s the generic subgroups
 0.51s U(2)              0.20s the four hypotheses
```

The consumer files were run on this tree and on a clean worktree at the same
base commit `8e84152`, to compare failure sets rather than counts.  Both runs
report the same seven failures and thirty-three passes, and the same seven test
ids: `test_two_elementary.sage` (2), `test_forms/test_discriminant_subgroups.sage`
(4) and `test_generated_model_character_quotient.sage` (1), all of them in code
this change does not touch (block orthogonal sums, primary components, a
fraction-field quotient comparison).  7 failed, 33 passed in 137.11s at the base
commit and 7 failed, 33 passed in 147.71s on this tree.
`tests/groups/test_generated_model_character_quotient.sage` does not pass the
repo's test lint at either commit (TL01/TL02/TL04/TL10), so that comparison was
made without the lint plugin; on this tree its own file was also run with the
lint on, where it stops at collection as it does at the base commit.

Not run: the CI image (`ghcr.io/dzackgarza/sage:develop` has no OCI runtime on
this host), and the ast-grep gates (`ast-grep` is not installed here).
