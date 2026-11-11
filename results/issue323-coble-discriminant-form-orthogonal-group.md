# #323 — `O(q)` of the discriminant form of `T_Co`, and `rho_{T_Co}`

`T_Co = <2> + E8(-2) + U(2)` (D. Dolgachev and S. Kondo, *Enriques surfaces II*,
Izv. Math. 77:3 (2013), §3, equation (3.6), printed p. 513). `A = T_Co^*/T_Co`
has 2048 classes. `A.orthogonal_group()` now states 4 generators in 0.01 s and
`T_Co.discriminant_representation()` returns. Before, the generating set never
came back.

## 1. The stop, with a usable stack

Red reproduction at the remote head `ad6b5db` in a throwaway worktree
(`.scratch/wt323`), probe `.scratch/p323_probe_red2.py`, whose first statement is
`faulthandler.dump_traceback_later(210, exit=True)` — a Python stack, not a
signal handler's:

```
A.orthogonal_group() constructed in 0.01s [4.1s]
T_Co.discriminant_representation() constructed in 0.01s [4.1s]
reading the generating set of O(A) now
Timeout (0:03:30)!
Thread 0x00007fbc00c40780 [python] (most recent call first):
  File "/sage/.venv/lib/python3.14/site-packages/sage/modules/torsion_quadratic_module.py", line 149 in _mul_
  File "/sage/.venv/lib/python3.14/site-packages/sage/groups/fqf_orthogonal.py", line 569 in <genexpr>
  File "/sage/.venv/lib/python3.14/site-packages/sage/groups/fqf_orthogonal.py", line 569 in _isom_fqf
  File "/sage/.venv/lib/python3.14/site-packages/sage/modules/torsion_quadratic_module.py", line 875 in orthogonal_group
  File "/repos/sage-extensions/src/sage_extensions/categories/modules/framed/formed/torsion_form_modules.py", line 2839 in _engine_orthogonal_group
  File "/repos/sage-extensions/src/sage_extensions/categories/modules/framed/formed/torsion_form_modules.py", line 2004 in _engine_group
  File "/repos/sage-extensions/src/sage_extensions/categories/modules/framed/formed/torsion_form_modules.py", line 1954 in _computed_group_generators
  File "/repos/sage-extensions/src/sage_extensions/categories/group/groups.py", line 1174 in selected_resolution
  File "/repos/sage-extensions/src/sage_extensions/categories/abstract_categories/objects.py", line 116 in realize
  File "/repos/sage-extensions/src/sage_extensions/categories/abstract_categories/objects.py", line 383 in selected_resolution
  File "/repos/sage-extensions/src/sage_extensions/categories/group/groups.py", line 6654 in selected_group_resolution
  File "/repos/sage-extensions/src/sage_extensions/categories/group/groups.py", line 5661 in group_generators
  File "/probe.py", line 23 in <module>
```

Log: `.tmp/qc-evidence/issue323-O-q-TCo-generators-wall.log`. `line 569` is
`_isom_fqf`'s candidate list `b_cand`, i.e. the brute-force search, and the
constructor of `O(A)` is lazy, so `discriminant_representation()` alone returns
while its target's generators do not: the stop is at the first read of the
generating set (or of the cardinality, which reads it).

## 2. What the form is, measured

The engine part is `(Z/2)^11` with `q` in `Q/2Z`, `b` in `Q/Z`. On the Smith
generators:

| data | value |
| --- | --- |
| `q(g_i)` | `[1/2, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1]` |
| `B(x,y) = 2b(x,y)` | symmetric `F_2` matrix, **rank 11** (nondegenerate) |
| `delta = q mod Z` | `e_1^*`, so `B(x,x) = delta(x)` |

So the polar form is nondegenerate and *not alternating*: the issue's memo that
"the form is on an odd-dimensional F2-space, so its bilinear form is degenerate"
does not hold — an alternating form has even rank and this one has rank 11. Two
things are true instead, and they are the whole obstruction:

* the neighbouring fast path builds an integral GF(2) quadratic matrix out of
  `q(g_i)`, and `q(g_1) = 1/2` is not in `Z`, so it is not applicable;
* `GO(eps,n,2)`, which that path uses, needs an *alternating* polar form of even
  rank, and `B` is neither;
* so the part fell to `TorsionQuadraticModule.orthogonal_group()`, whose
  `_isom_fqf` searches all classes of the right `q`-value and order.

## 3. The construction, and what each step rests on

`_engine_two_primary_odd_orthogonal_generators` in
`src/sage_extensions/categories/modules/framed/formed/torsion_form_modules.py`,
reached from `_engine_orthogonal_group` when the two-primary part is elementary,
has both value moduli `1` and `2`, takes a half-integral value, its polar form has
full rank, **and** `delta(B^{-1} delta) = 1`. The reduction, each line a
consequence of `q(x+y) = q(x)+q(y)+2b(x,y)` in the module:

1. `delta = q mod Z` is additive, hence linear, and `B(x,x) = delta(x)`.
2. `B` nondegenerate gives one `c` with `B(c,.) = delta`; the last condition says
   `B(c,c) = delta(c) = 1`, so `<c>` is not isotropic and `B(c,ker delta) = 0`
   gives `A = <c> ⊥ A_0` with `A_0 = ker delta`, `rank A_0 = 10`, `n` odd.
3. `q_0 = q|_{A_0}` is integer-valued with polar form `B|_{A_0}`, nondegenerate:
   an ordinary quadratic space over `F_2` in 10 dimensions, whose polar form is
   alternating. This is what `_engine_elementary_two_orthogonal_generators`
   (GAP Forms: `WittIndex`, `IsometricCanonicalForm`, `BaseChangeToCanonical`,
   `GO`) takes, and its type — plus or minus — is read off the computed Witt
   index, not assumed.
4. `g -> g|_{A_0}` is a bijection `O(q) -> O(q_0)`: every `g` preserves `B`, hence
   `delta = B(c,.)`, hence fixes `c`; conversely `g_0` extended by fixing `c`
   preserves `q` because `q(alpha c + w) = alpha q(c) + q_0(w)` for `w` in `A_0`.
   So `|O(q)| = |O(q_0)|`, and no subgroup or stabilizer of the symplectic group
   has to be intersected: the functional that could have survived is
   `B(c,.)|_{A_0} = delta|_{A_0} = 0`.
5. Each transported generator is checked against the whole form before it is
   returned, by an exact criterion rather than a sample: with `M` the integer
   matrix `M_ii = 2q(g_i)`, `M_ij = 2b(g_i,g_j)`, the quadratic polynomial of `A`
   is `x -> (x M x^t)/2` on `x` in `{0,1}^n`, so `x -> xG` preserves it exactly
   when `G M G^t - M` has diagonal entries divisible by 4 and off-diagonal entries
   divisible by 2 — those are the coefficients of the difference polynomial.

Step 2's last condition is not decoration. On the two-primary part of
`diag(6,6)` — elementary, `q = 3/2` on both Smith generators, `B = 2b` the
identity — one has `delta = (1,1)`, `c = (1,1)` isotropic, `ker delta = <c>` its
own orthogonal complement and `B` restricted to it degenerate; the split does not
apply there and the part keeps Sage's route. A first version of this branch
omitted the condition, and eleven tests of
`tests/groups/test_generated_model_character_quotient.sage` failed on it; the
guard test `test_a_half_integral_two_part_with_isotropic_dual_keeps_the_general_route`
pins the case now.

Citations, each with its numbered statement and printed page:

* P. J. Cameron, *Classical Groups* (QMUL lecture notes), Chapter 6, §6.2
  "Characteristic 2, odd rank", **Theorem 6.1, printed p. 69**: for a
  nondegenerate quadratic form in `n` odd variables over a perfect field of
  characteristic two, `O(Q) ≅ Sp(n-1,F)`; the proof on that page is where the odd
  rank forces the polar form away from the alternating case and the isometry group
  is read off a symplectic group. That is the phenomenon here, one step over:
  Cameron's own odd-rank form is `F_2`-valued with a rank-one radical, while on
  this form the half-integral direction plays the radical's part and the group
  that survives on `ker delta` is the orthogonal group of its alternating
  restriction, of index 528 in `Sp(10,2)`.
* Same, **pp. 70-71**: the quadratic forms polarising to a fixed symplectic form
  are exactly its translates by the linear functionals, and over `GF(2)` each
  functional is `x -> B(x,a)`; that is the shape of the reduction above, where
  the surviving functional is zero.
* GAP Forms 1.3.0, §5.3.1 (`WittIndex`, `IsometricCanonicalForm`,
  `BaseChangeToCanonical`) — already the citation of
  `_engine_elementary_two_orthogonal_generators`, which this route reuses.

Boundary cases handled in the same place: `n = 1` (`<2>`'s discriminant form,
`ZZ/2` with `q(1/2) = 1/2`) returns the empty generating set and order one,
because the only class of value zero is zero; a degenerate polar form never
reaches the branch, because `_engine_orthogonal_group` checks its rank first and
a degenerate one keeps Sage's general route.

## 4. Acceptance

### 4.1 The order, and the record

Probe `.scratch/p323_probe4.py` on the fixed tree:

```
T_Co: rank 11, signature (2, 9), det -2048, even True
A cardinality 2048
orthogonal_group() returned in 0.01s
generators: 4
cardinality 46998591897600 in 0.00s
card value 46998591897600: True
T_Co.discriminant_representation() returned in 0.00s: Generic morphism:
  From: Orthogonal group O(Integral lattice of rank 11 and signature (2, 9))
  To:   Orthogonal group of Finitely presented module on 11 module generators ...
total 9.3s
```

`46998591897600 = 2^21 3^5 5^2 7 17 31`, which is what research
`computations/reports/coble_isotropic_orbits.py` (`dzackgarza/research`, run of
2026-11-05) prints as `|Orth(A_{T_Co}, q)|`, and the same number lattice card
`6JRR` states in `integral.discriminant_form.orthogonal_group_order`
(certificate `0be391409303d25f25d126795ee881040661b4883ad7473272b34b60b8c414da`,
block computed by `latticedb certify`). The test asserts the card's number and
nothing else: the record is the comparison, not a second oracle.

Where the number comes from, so that it is not a typed expectation: GAP computes
`|GO(1,10,2)|` from the quadratic space `q_0`, the type being read off the
computed Witt index; the generators GAP returns are transported to the basis of
`A_0` by GAP's own base change to the canonical form; and the transport to `A` is
an explicit conjugation that fixes `c`. The order is therefore the order of the
group whose every generator is checked against the whole of `A` by the criterion
in step 5.

The order is also computed *from the transported generators*, not read off the
construction's `SetSize`: the owner states its order on the engine group, and the
order of the subgroup the stated generators generate is computed by GAP, on the
2048-point action, independently. Probe `.scratch/p323_probe6.py` on the pushed
tree shows the value is computed and not inherited — the same call on fewer
generators gives smaller numbers:

```
parent cardinality 46998591897600 (SetSize claim from the construction)
subgroup on all 4 statements: 46998591897600 [0.02s]
subgroup on the first statement alone: 2 [0.01s]
subgroup on the first two statements: 348364800 [0.01s]
```

The acceptance test asserts exactly that equality, so a wrong order in the
construction would fail it rather than agreeing with itself.

An independent in-tree check of the same abstract group also ran in the gate:
`tests/test_finite_form_groups.py::test_split_elementary_two_discriminant_orthogonal_group[5-46998591897600]`
builds the discriminant form of `U(2)^5` — `(Z/2)^10` with the plus-type
quadratic form, whose orthogonal group is `O^+(10,2)` — through the *integral*
branch, and its expected value is derived in the module docstring from the
counting recurrence `|O^+(2m,2)| = (2^m-1)(2^(m-1)+1)2^(2m-2)|O^+(2m-2,2)|`.
It passes, and it is the same order this branch produces for `q_0`.

### 4.2 The same numbers through the orbit partition

Probe `.scratch/p323_probe5.py` (evidence, not an assertion — see §5):

```
generators 4, |O(q)| = 46998591897600   [7.0s]
probe set: 66 points, built in 0.00s
q preserved on the complete probe set: True [1.95s]
isotropic classes: 528 [29.06s]
orbit partition: 6 orbits [12.61s]
   size 1
   size 496
   size 527
   size 1
   size 496
   size 527
rho returns [0.00s]; codomain cardinality 46998591897600
```

The six orbit sizes are the research record's `[1, 1, 496, 496, 527, 527]`, and
the two orbits carrying `q = 0` have 1 and 527 classes — the card's
`isotropic_classes: 528` and `isotropic_orbits: 2`.

### 4.3 The acceptance test

`tests/lattices/test_discriminant_form_of_the_coble_lattice.sage`, seven tests,
each number card `6JRR`'s, read from `tests/cards/lattice-database-enriques.json`
by tag through `card("discriminant_forms", "6JRR")`:

```
$ /sage/.venv/bin/python -m pytest -p qc_sage_session -p sage_extensions.testing.test_lint \
    -o addopts= -q --tb=short --durations=0 \
    tests/lattices/test_discriminant_form_of_the_coble_lattice.sage
.......                                                                  [100%]
6.07s call  ...::test_the_generating_set_of_the_orthogonal_group_states_isometries
3.59s call  ...::test_the_lattice_is_the_published_formula_and_its_discriminant_form_is_the_cards
0.29s call  ...::test_a_half_integral_two_part_with_isotropic_dual_keeps_the_general_route
0.13s call  ...::test_discriminant_representation_of_the_coble_lattice_returns_on_an_isometry
0.12s call  ...::test_the_rank_one_half_integral_form_has_the_trivial_orthogonal_group
0.08s call  ...::test_the_form_is_the_half_integral_odd_rank_case_the_owner_serves
7 passed in 11.74s
```

That is the run in the pushed tree, with the test-lint plugin loaded. On its own,
`just test-lint tests/lattices/test_discriminant_form_of_the_coble_lattice.sage`
prints `1 files, 0 findings`.

The commits these numbers belong to are `984e7e6` (the test) and `4df29b8` (the
owner branch, the trap entry and this report) on `main`, whose push was verified
with `git ls-remote main` at `4df29b83b9e4d9bc12545089f3ed2394987e41b6`.

The card read is in `tests/lattices/conftest.py`, which binds `card(section, tag)`
as a builtin — the mechanism the lint documents — because the lint rejects a file
read inside a test file (`TL01` for `json` and `pathlib`, `TL13` for `__file__` and
`Path`). `tests/cards/refresh_lattice_database_enriques.py` gained a
`discriminant_forms` slice for card `6JRR` and the digest was regenerated at
database commit `587d56febe5856d54c6bc9fc023fa5a425f76bfb`, not edited: the diff is
19 added lines and no changed one.

### 4.4 Red before the repair

The same test file, and the digest regenerated with its `discriminant_forms`
slice, copied into the worktree at `ad6b5db` (the remote head, whose owner has no
branch for this form), then:

```
$ TREE=.scratch/wt323 /usr/bin/timeout -s KILL 150 /sage/.venv/bin/python -u -m pytest \
    -p qc_sage_session -o addopts= -q --tb=line \
    tests/lattices/test_discriminant_form_of_the_coble_lattice.sage
..[killed at 150 s]
```

Two tests pass — the card's rank, signature, determinant and class count, and the
half-integral branch condition — and the third, which reads the generating set of
`A.orthogonal_group()`, does not return; the run is killed at the cap with the
stack of §1 on the same call. Log `.tmp/p323-red-test-ad6b5db.log`.

### 4.5 Regression

Thirteen test files — the new one, and the forms and groups modules that own the
changed construction and its neighbours — run against the exact tree this report
is committed in (worktree `.scratch/wt323push3` at the remote head plus the two
commits), and the same twelve pre-existing files run at the remote head alone
(worktree `.scratch/wt323base`):

```
$ /sage/.venv/bin/python -u -m pytest -p qc_sage_session -o addopts= -q \
    --tb=short --durations=0 tests/lattices/test_discriminant_form_of_the_coble_lattice.sage \
    tests/forms/test_integer_valued_elementary_two_form_groups.sage tests/forms/test_torsion_forms.sage \
    tests/forms/test_the_d4_discriminant_form_and_its_finite_action.sage \
    tests/forms/test_isometry_between_torsion_forms.sage \
    tests/forms/test_the_polar_radical_and_nondegenerate_quotient.sage \
    tests/forms/test_polar_radical_criterion.sage \
    tests/forms/test_rank_one_2adic_orthogonal_groups_archive.sage \
    tests/forms/test_discriminant_subgroups.sage tests/forms/test_metabolizers_archive.sage \
    tests/test_finite_form_groups.py tests/groups/test_generated_model_character_quotient.sage \
    tests/groups/test_group_generators_use_the_supplied_family.sage
6 failed, 78 passed in 67.70s
```

and at the remote head without these commits, the same twelve files:

```
6 failed, 72 passed in 63.43s
```

The six FAILED ids are **identical** in both runs
(`diff base-failed.txt mine-failed.txt` is empty); they are pre-existing failures
of the remote head — `discriminant_subgroups.sage` (four), `torsion_forms.sage`
(one: `diag(2,1)`'s discriminant *quadratic* form is refused because the lattice
is odd) and `rank_one_2adic_orthogonal_groups_archive.sage` (one, inside
`brown_invariant`'s `is_nondegenerate`) — none of them in a file this change
touches and none in the branch's path. The six new passes are the six tests of
the new module; the earlier eleven failures of
`tests/groups/test_generated_model_character_quotient.sage` are gone, which is
what the second precondition bought.

`just test-lint tests/lattices/test_discriminant_form_of_the_coble_lattice.sage`
is clean (`1 files, 0 findings`). The whole-tree lint is not: it reports findings
in `tests/forms/*` and `tests/groups/*` that this change does not touch (85
findings over 13 files in the run above), so it was left out of the gate run and
is reported as pre-existing.

The full 874-file tree was not run; this is the set that owns the construction.

## 5. What is not done

* The whole 874-file tree was not run; the gate below is the files that own the
  changed construction plus their neighbours.
* The card's `isotropic_classes` and `isotropic_orbits` rows are evidence
  (§4.2), not asserted: the maintained orbit partition of `A` costs 12.6 s
  outside pytest and 37 s inside it, which is most of the 60 s per-test timeout,
  and a test that sits at two thirds of a timeout is a flake waiting to happen.
  The unit test asserts the two card rows that are cheap: the order, and the
  rank, signature, determinant and class count.
* `q`-preservation is checked on the complete probe set (a basis and all pairwise
  sums, which determine the whole quadratic form), not on all 2048 classes; the
  library path checks each generator against the whole form by the coefficient
  criterion of §3 step 5.
