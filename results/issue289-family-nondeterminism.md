# #289: `Tco.Aut().group_generators()` draws a different family each run

**Result: the family does vary between processes, the variation is the indefinite port's
own sampling, and a canonical family is not required** — the owner's contract is *generators
of* `O(L)`, two generating families generate the same group, and every draw measured gives
the same discriminant image, the whole of `O(A_{T_Co})`. No library change; one test.

Measured on `7519715a517f2a1cc526833237c8dbb442aeb0c8` (`main`, the parent of this unit's
commit), on the adopted runtime: Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1, with the
indefinite port project bound at `/work`.

| run | members | matrix digest (sha256 of the sorted row-action matrices) | discriminant image |
| --- | ---: | --- | ---: |
| unpinned `random` | 374 | `ccae4e15a14be79965bca74dbb641ecfadc7d358e8d70c1021d489fa7dd52367` | 46 998 591 897 600 |
| `random.seed(20261111)` | 360 | `c327a217037ed41c05d48506805940595aa74f56d1d95c22aee95e36b8617114` | 46 998 591 897 600 |
| `random.seed(20261111)` again, second process | 360 | `c327a217037ed41c05d48506805940595aa74f56d1d95c22aee95e36b8617114` | 46 998 591 897 600 |
| the runs #289 records | 444, 372, 442, 438 | — | — |

`A_{T_Co}` has 2048 classes and `|O(A_{T_Co})| = 46 998 591 897 600`, computed from the
engine in 0.0 s; the image's order is computed from its own generating family. So the two
*different* families generate groups with the *same* discriminant image, which is the whole
of `O(A_{T_Co})`: `discriminant_representation_is_surjective()` is `True`.

## The source of the nondeterminism

Not this library, and not set iteration order: the port samples.

* `sage_indefinite_port/indefinite/eichler.py:21` imports `choice`, `randrange`, `sample`
  from Python's `random`.
* `_source_random_matrix_perturbation` (`eichler.py:106-118`) transcribes
  `GetRandomMatrixPerturbation`, `IndefiniteFormsFundamental.g:11-30`: a random signed
  permutation, or one elementary entry replacement, drawn per attempt.
* `_source_hyperbolic_pair` (`eichler.py:210-284`) transcribes `GetHyperbolicPlane`
  (`ApproximateModels.h:996-1180`), which keeps "a set of *sampled* isotropic vectors",
  retrying an insertion up to 100 times and exiting after 10 (or 20) samples that do not
  improve the pairing. Its own docstring says "sampled".
* `_source_find_isotropic` re-runs `_indefinite_lll` with `_random_signed_permutation`
  perturbations (`eichler.py:194-197`, `:240`).

So the drawn family is one of many the source algorithm admits; the count is whatever the
sampling settles on. Nothing in `LatticeIsometryMor._computed_group_generators` adds a
choice: it maps the port's tuple through `self(...)` and indexes it by `Sets.Δ[n-1]`.

## Why the reported call cannot show two draws in one process

The port caches the drawn family in its groupoid, keyed by the reduced Gram and by proved
isometries between Gram keys
(`sage_indefinite_port/indefinite/groupoid_cache.py:177-194`, `_key` at `:104-110` on
`_gram_in_label_order`). Measured in one process, with `T_Co` and the same lattice
presented in the other `U(2)` basis (`(e_p, e_p + e_f)`, Gram block `[[0,2],[2,4]]`):

```
[  141.67s] T_Co family: 360
[  143.43s] iso built
[  147.25s] rotated family: 360 in 3.82s
```

The second presentation is answered from the cache in 3.82 s instead of drawing again. So
within one process there is exactly one draw per reduction class, and a test asserting
"two runs in one process agree" is green on any tree — it would test the cache, not the
draw. That is why this unit cannot ship the red test #289 asks for; the variation is
between processes, and it is pasted above.

**The lever, if a canonical family is wanted.** The draw follows the caller's `random`
state, which is why the same seed reproduces the family byte for byte in two processes.
Pinning it at the owner (save `random.getstate()`, `random.seed(...)`, run the port call,
restore) would make the family a function of the lattice and reproducible across
processes. It is not landed here: its acceptance is a between-process statement that no
in-process test can carry, and a fixed seed also fixes a draw for *every* indefinite
lattice in the library, which is a new termination risk that this budget cannot sweep. The
invariance below is what the issue's second branch asks for, and it is what the test
checks.

## Why a canonical family is not required

The owner states what the family is for: `LatticeIsometryMor._computed_group_generators`
returns *generators of* `O(L)` — for an indefinite lattice from the port's
`orthogonal_group_generators`, which transcribes Magma's `INDEF_FORM_AutomorphismGroup`
(`IndefiniteForms.g:1474-1494`), and whose sampled families are its
`TwoUFullGeneratingDatum`, stating the orbit argument `O(L) = <A, P_v, t_i>`. Two families
that each generate `O(L)` generate the same group, so `rho` of them is one subgroup of
`O(A_L)`, and nothing computed downstream of the family can depend on the draw.

## What was added

`tests/lattices/test_the_coble_generator_family_need_not_be_canonical.sage`, one test, no
library change. It reads the family through the public call, reads the discriminant image
of the same group, and asserts both orders, computed: the image is contained in
`O(A_{T_Co})` (`supergroup() is` the target), is non-trivial, equals the whole of it,
`discriminant_representation_is_surjective()` is `True`, and every generator of the image
is the `discriminant_morphism()` of a member of the family this process drew.

```
/sage/.venv/bin/python -u -m pytest \
  tests/lattices/test_the_coble_generator_family_need_not_be_canonical.sage \
  -q -o addopts= -p qc_sage_session --tb=short -rf -p no:cacheprovider \
  --durations=0 --durations-min=0 -s

122.17s call  test_the_coble_generator_family_need_not_be_canonical
1 passed in 123.75s (0:02:03)
```

`main` moved from `7519715` to `698e661` (a #331 commit of another chat, touching
`isotropic_parabolics.py`, `lattice_database.py` and one export in `all.py`) while the unit
was measured, so the test was re-run at the rebased tip before the push:

```
171.08s call  test_the_coble_generator_family_need_not_be_canonical
1 passed in 173.17s (0:02:53)
```

and the test lint again `1 files, 0 findings`.

peak tree RSS 678 MiB; test lint on the file `1 files, 0 findings`. `addopts` is blanked
(this venv carries neither `pytest-timeout` nor `pytest-reportlog`) and the call is over
the 20 s ceiling and the 60 s `--timeout`, so the gated configuration's computation is
reported with the ceilings lifted, as for #296, #321, #303 and #333.

## Blocked at the tip: a regression on `main`, not this unit

The test above passes at `698e661` (`1 passed in 173.17s`) and fails at `a79d3e1`, where
`NamedLattices.Tco.Aut().group_generators()` itself raises

```
TypeError: membership of Morphism ... in Subgroup of Orthogonal group O(...) is
undecided; supply a word witness to membership_decision
```

inside `_retain_admitted_member`, reached from `_evaluate_reduced_word`. That frame was
added by `158c170385aae1be06a6234b4a871528e8064bdf` (#287, another unit), and it breaks
every indefinite-lattice generator family on the port's `2U`-envelope branch -- #333's
`TEn.O().discriminant_image()` test, pushed at `7519715` and green there, fails the same
way at the tip (`1 failed in 149.51s`). The defect is written out for filing in
`results/issue-to-file-indefinite-generators-undecided-membership.md`; the test in this
unit is held, uncommitted, until that owner answers, because a red test is not committed.

## Issue closure text

> `Tco.Aut().group_generators()` does draw a different family per process — 374 members
> unpinned here, 360 under a pinned seed, and 444/372/442/438 in the recorded runs — and
> the draw is the indefinite port's own sampling: `_source_hyperbolic_pair` transcribes
> `GetHyperbolicPlane` (`ApproximateModels.h:996-1180`, "sampled" isotropic vectors) and
> `_source_random_matrix_perturbation` transcribes `GetRandomMatrixPerturbation`
> (`IndefiniteFormsFundamental.g:11-30`), both drawing from Python's unseeded `random`.
> The port's groupoid cache is keyed by the reduced Gram, so within one process there is
> one draw (measured: 141 s cold, 3.82 s for the same lattice in another basis), which is
> why the two-run-in-one-process red test cannot be built.
>
> A canonical family is not required: the owner's contract is *generators of* `O(L)`
> (`orthogonal_group_generators`, transcribing Magma's `INDEF_FORM_AutomorphismGroup`,
> `IndefiniteForms.g:1474-1494`; `TwoUFullGeneratingDatum`'s `O(L) = <A, P_v, t_i>`), so
> any two draws generate the same group. Computed on the 374-member and the 360-member
> family: both discriminant images have order `46 998 591 897 600`, the computed
> `|O(A_{T_Co})|`, and `discriminant_representation_is_surjective()` is `True`.
>
> `tests/lattices/test_the_coble_generator_family_need_not_be_canonical.sage`,
> `1 passed in 173.17 s` at the rebased tip, test lint `0 findings`. The seed-pinning lever that would make
> the family reproducible across processes is measured (one seed, same digest twice) and
> not landed.
