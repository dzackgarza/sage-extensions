# Issue to file: `test_eichler_orbits` has two failures that predate the #315 refusal

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body. Searched first with
`repo:dzackgarza/sage-extensions is:issue is_decomposable`,
`… is:issue hyperbolic_plane_summand_count` and `… is:issue test_eichler_orbits`:
**0 results each**, so no open (or closed) issue holds either failure.

## Title

`is_decomposable()` is True for `LK3`, and `hyperbolic_plane_summand_count()` counts a raw Gram `U` factor: two failures in `test_eichler_orbits`

## Body

Two assertions in `tests/lattices/test_eichler_orbits.sage` fail on `main`. Both fail
identically in a worktree at `82715b7` and on the tree after the #315 refusal
(`92e5a4c`), so neither is caused by #315.

Failure 1, `test_the_criterion_reads_its_hypothesis_off_the_decomposition`:

```
tests/lattices/test_eichler_orbits.sage:48: in test_the_criterion_reads_its_hypothesis_off_the_decomposition
    assert not NamedLattices.LK3.is_decomposable()
E   assert not True
E    + where True = is_decomposable()
E    +   where is_decomposable = Integral lattice of rank 22 and signature (3, 19).is_decomposable
E    +     where Integral lattice of rank 22 and signature (3, 19) = NamedLattices.LK3
```

The test states that the catalogue's `LK3` is presented by a Gram matrix and therefore
reads no decomposition off it, while `NamedLattices.U ** 3 + NamedLattices.E8 ** 2`
reads three plane summands. It also asserts `NamedLattices.LK3.is_isometric(decomposed)`
(that assertion passes), so the two objects are one lattice and the difference the test
wants is in what the *presentation* exposes. Either `is_decomposable()` now answers True
for a Gram-matrix presentation (then the test's premise is stale and the criterion it
guards is not the one it measures), or the decomposition is genuinely detected and the
test's assertion is wrong. Which of the two is a decision about the owner of
`is_decomposable`, not about this test.

Failure 2, `test_raw_gram_factor_does_not_count_as_a_represented_u_summand`:

```
tests/lattices/test_eichler_orbits.sage:58: in test_raw_gram_factor_does_not_count_as_a_represented_u_summand
    assert lattice.hyperbolic_plane_summand_count() == 1
E   assert 2 == 1
E    + where 2 = hyperbolic_plane_summand_count()
E    +   where hyperbolic_plane_summand_count = Integral lattice of rank 4 and signature (2, 2).hyperbolic_plane_summand_count
E    + and   1 = Integer(1)
```

The specimen is `Lattices(ZZ)([[2, 1], [1, 0]]) + NamedLattices.U`: the first summand is
a raw Gram presentation of the hyperbolic plane (the test asserts
`raw_u.is_isometric(NamedLattices.U)`), and the test requires that it *not* count as a
`U` summand, so the count is one for the named `U` only. It now counts two, and
`decomposition_names()` — the preceding assertion in the same test — passes, so the count
is reading a plane off a factor the names do not call `U`.

## Evidence

```
/sage/.venv/bin/python -m pytest -p qc_sage_session -o addopts="" -q --tb=line --durations=0 \
  tests/lattices/test_eichler_orbits.sage \
  tests/lattices/test_isotropic_orbit_collections.sage \
  tests/lattices/test_primitive_orbit_series_on_indefinite_lattices.sage
```

| tree | result |
| --- | --- |
| `82715b7` (worktree), `test_eichler_orbits.sage` alone | 2 failed, 4 passed in 122.49 s |
| `92e5a4c` (the #315 refusal), the three files | 2 failed, 8 passed in 748.21 s |

The same two FAILED ids in both runs; no other failure. Logs
`.tmp/p315-gate-base-eichler.log`, `.tmp/p315-gate-setA.log`.

## Acceptance

Each failure is decided at its owner: either `is_decomposable`/`hyperbolic_plane_summand_count`
are repaired to the reading the test states (a raw Gram factor is not a represented `U`
summand; a Gram presentation exposes no decomposition), or the test's two assertions are
rewritten to state the reading the library now implements — with the citation for
whichever reading is correct, since the assertions are what `eichler_criterion_applies()`
is gated on and `#315`'s refusal now depends on that gate.
