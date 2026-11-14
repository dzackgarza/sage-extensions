# #294 prepared batch: published cusp counts through the public orbit calls

Prepared, not started: every module below needs rows that only `dzackgarza/lattice-database#10`
creates, and the issue's own order puts a Scattone module first. Nothing here is run, and no
expected number is derived in a docstring: each row is a card value with a tag and a citation.

## The calls the modules compare against

All four modules compare a card row with the same public operations of this repository:

* `<group>.isotropic_orbit_representatives(rank)` — the representatives themselves. `rank=1`
  is lines, `rank=2` planes; each representative is a subobject whose inclusion carries a
  primitive isotropic vector, so a test can assert primitivity and isotropy as the existing
  L_d module already does.
* `<group>.roots_on_isotropic_lines()` / the parabolic stabilizer calls when a row is a
  *stabilizer image index* rather than a count (T_En's `index 1` / `527` rows).
* `Lattices(ZZ)(gram)` for the specimen, built from the card's own `gram_tensor`.

## The four modules, in the issue's order

### 1. `tests/lattices/test_scattone_degree_two_and_four_boundaries.sage`

* Citation: Scattone, *On the compactification of moduli spaces for algebraic K3 surfaces*,
  Mem. AMS 374 (1987), Prop. 5.4.7 and Cor. 5.4.8(2).
* Specimens: the degree-2 and degree-4 K3 lattice cards.
* Rows needed from #10: each card's `primitive_orbits` entry for the Baily–Borel boundary,
  with the Proposition/Corollary named on the row. **Not present on any card today.**

### 2. `tests/lattices/test_unpolarized_enriques_strata.sage`

* Citation: Dutour Sikirić–Hulek, arXiv:2302.01679, the Tits-building section and
  `table_subgroups2`.
* Specimen: the T_En card `029J`, whose `primitive_orbits` field already states, with
  citations, 528 lines in two orbits (527 + 1) and 24242 planes in two orbits (527 + 23715)
  under `O^+_10(F_2)`, and the two Sterk orbits each of lines and of planes under
  `O(T_En)`.
* Public calls: `isotropic_orbit_representatives(1)` and `(2)` on the T_En lattice's
  orthogonal groups, plus the stabilizer-image indices for the rows that state an index.
  This is the module the existing T_En specimens feed; it is the cheapest of the four to
  bring up once the strata table is on the card.

### 3. `tests/lattices/test_eighty_seven_enriques_polarizations.sage`

* Citation: Dutour Sikirić–Hulek, arXiv:2302.01679, line/plane/flag counts per polarization
  group Γ_h.
* Specimen: T_En with each of the 87 polarization groups — 87 rows, each a card row with
  its Γ_h and its three counts.
* Rows needed from #10: the 87 polarization rows. **Not present today.**

### 4. `tests/lattices/test_isotropic_line_orbits_of_small_indefinite_lattices.sage` (rewrite)

* Today it asserts fifteen counts (`O`, `Õ`, `Õ⁺` on five lattices) from a derivation in its
  own docstring — the shape #294 removes.
* Required state: the five `L_d = U + U + ⟨−2d⟩`, d ∈ {1, 2, 4, 9, 36}, exist as cards with
  a `primitive_orbits` row per group, certified by computation (no paper proves these), and
  the module reads them: `card.primitive_orbits` → the count → compared with
  `isotropic_orbit_representatives(1)`; the derivation leaves the docstring.
* **The five cards do not exist**: `lattices/` carries 302 504 records and none matches
  `U + U + <-2…`; `029J.md` is present and is the T_En card.

### Then T_Co under #286 — not in this batch

#296's plane orbit and this batch's line/plane counts are different objects: 23715 also
appears as an orbit length on `029J`, but a finite discriminant orbit size is not a cusp
count, and no T_Co count is accepted from one.

## The dependency asked of `dzackgarza/lattice-database#10`

1. `L_1, L_2, L_4, L_9, L_36` cards with `primitive_orbits` rows for `O`, `Õ`, `Õ⁺`
   (computed, with the computation's provenance on the row).
2. The degree-2 and degree-4 K3 boundary rows with Scattone's Prop. 5.4.7 / Cor. 5.4.8(2)
   named.
3. The 87 Γ_h polarization rows with their line, plane and flag counts.
4. A `certifications:` digest per row, as `029J.md` already carries for
   `integral.primitive_orbits`.

## How each module will be verified when its rows exist

```
SAGE_PYTHON_BIN=$PWD/.scratch/sage-python \
PYTHONPATH=$HOME/ai-review-ci/tool-artifacts/pytest_plugins \
  ~/.local/bin/just test <module>
```

with `addopts` intact. The time gate's 20 s call ceiling and the 60 s `--timeout` apply: the
L_d specimens currently finish in seconds, and the T_En one is the risk, so a module that
trips the ceiling is reported as a cost finding rather than tuned to fit.

---

# Batch v2: prepared after `lattice-database#19` closed (tree `73d2c49`)

Supersedes the dependency list above. The Scattone rows now exist, so the question is no
longer what to ask the database for; it is which of the four modules can be brought up on the
current tree, in what order, and on which harness.

## What was read, before any value is used

`lattice-database` `main` at `67526965910fe6d4212b23705973e3abd42bcd6c`, cards read through
`git show 6752696:lattices/<tag>.md` (not from memory, and not from the old −2·E8 versions):

| tag | lattice | rank | signature | det | discriminant | certified rows |
|-----|---------|------|-----------|-----|--------------|----------------|
| `6JRX` | `Λ₂ = U ⊕ U ⊕ E8(−1)² ⊕ ⟨−2⟩` | 21 | (2, 19) | **−2** | Z/2 | `O`: planes 4 · `O+`: constant 1, planes 4 · `Otilde+`: constant 1 |
| `6JRY` | `Λ₄ = U ⊕ U ⊕ E8(−1)² ⊕ ⟨−4⟩` | 21 | (2, 19) | **−4** | Z/4 | `O`: planes 9 · `O+`: constant 1, planes 9 · `Otilde+`: constant 1 |

Both carry `certifications: integral.primitive_orbits: <sha256>` and, on every row, the
Scattone citation that proves it (Prop. 5.4.7 with Cor. 5.4.8(2) p. 78 and §6.2 p. 97 / §6.3
p. 100 for the planes; §6 p. 94 for `O+`; Thm 4.0.1 p. 55 for `Otilde+`). The Gram is `U ⊕ U`
followed by two copies of `−1 ×` the E8 Cartan matrix and the `⟨−2k⟩` line — so the
determinant is `−2k` and every row is consistent with a *rank-21* lattice, which is what the
retired cards were not.

## Harness prerequisite — a trap that already produced one false finding

`isotropic_orbit_representatives` is implemented in this repository
(`categories/lattice_morphisms.py:4085`, subgroups at `group/predicate_subgroups.py:545`) but
its classification is the port's: `categories/isotropic_orbits.py:933`
`_isotropic_orbit_representatives` calls `sage_indefinite_port.indefinite.marked_lattices.
primitive_marking_classes`. The adopted image ships a **bundled** copy at
`/repos/sage-indefinite-port`, which is what `.scratch/sage-python` imports; the port under
development is the project checkout `p-165a6922…/repo` at `991b88b0`.

Measured, same module, both harnesses:

```
.scratch/sage-python (bundled port): 2 failed, 1 passed in 47.35 s
  TypeError: int() argument must be … not 'OwnedJoinCategory.element_class'
  at ../sage-indefinite-port/src/sage_indefinite_port/indefinite/recursive.py:154
  (that TypeError is the recorded setup error, not a mathematical finding)
port bound (sage-python-port)    : test_the_line_counts_of_the_three_groups_are_the_derived_ones
                                   60.00 s > 20 s  → pytest --timeout killed it
```

So `.scratch/sage-python-port` (adds `-b <port repo>:/repos/sage-indefinite-port`) is the only
harness any of these modules may be measured on, and the standing state of
`tests/lattices/test_isotropic_line_orbits_of_small_indefinite_lattices.sage` is **red by
timeout**, not green and not port-error. That is a cost finding for #306, not a card
dependency.

## The batch, in order, with what is actually blocking each item

**1a. `tests/lattices/test_the_scattone_period_lattices_are_the_corrected_cards.sage` — do this
first; it is cheap and it is the row that would have caught the defect #19 fixed.**
Read the two cards' `gram_tensor` from the database checkout and assert, through this
repository: `Lattices(ZZ)(card gram)` has rank 21, signature `(2, 19)`, determinant `−2` / `−4`,
`is_even()`, and discriminant group `Z/2` / `Z/4`. The determinant assertion alone separates
these cards from the retired −2·E8 versions (`−131072` / `−262144`), and the discriminant group
carries the `⟨−2k⟩` line that distinguishes Λ₂ from Λ₄; the signature and evenness assertions
pin the rest. No orbit enumeration is involved. Prerequisite: none beyond the harness (this
item does not touch the port). Acceptance: passes under the declared gate, with the card's own
tag and its `certifications` digest named in the test.

**1b. The boundary counts — blocked on cost, and must be measured before it is promised.**
The rows are now on the cards (planes 4 / 9 under `O` and `O+`, one point under `Otilde+`), so
the *data* prerequisite is satisfied. What is unverified is whether
`isotropic_orbit_representatives(2)` on a rank-21 lattice returns inside any sane budget: on
the same harness, rank-5 line counts over five lattices already exceed 60 s (above). Planned
measurement, one specimen only (`6JRX`, `O`, planes), under `peakrss` with the port bound, and
if it does not return it is reported as a #306 cost finding — not tuned, and not replaced by a
literature count presented as a computation.

**2. `test_unpolarized_enriques_strata.sage` — unchanged, and not cheaper.**
T_En `029J` still states its rows (528 lines in 2 orbits 527+1; 24242 planes in 2 orbits
527+23715); the calls it needs are the rank-1 and rank-2 orbit enumerations on T_En, i.e. the
same port route that just timed out at rank 5. #296's finite-quadratic-module operations
(`subobject_orbit_action` `torsion_form_modules.py:2474`, `stabilizer` `:2584`) are a different
object and do not unblock this.

**3. `test_eighty_seven_enriques_polarizations.sage` — still blocked on rows** (the 87 Γ_h
polarization rows are not on any card).

**4. The L_d rewrite — blocked twice.** Both on the five `L_1 … L_36` cards (still absent) and
now also on the port's marking-class cost, since the module it would rewrite is the one timing
out. Ordering note: 4 cannot be scheduled before the cost unit, or it will re-encode the
timeout.

## #296's part of this batch

#296's operations are implemented and its gate is red only under #306 (first engine call
28–38 s against the 20 s call ceiling). Nothing in this batch needs them re-run, and no count
in items 1a–4 may be taken from a finite discriminant orbit — in particular the 23715 that
`029J` also carries as an orbit length is not a cusp count.

## Not done in this batch

* **No T_Co run.** Nothing above touches `T_Co`, and no count is quoted from it.
* **#307 is not claimed closed** — it is pushed as `73d2c49` for independent review.

## Measured state of the comparison unit (tree `ee13b30`, port `991b88b0`)

Group objects on `Λ₂`, timed on the port-bound harness, and the card's row keys from
`6752696:lattices/6JRX.md` (`O` → `planes: 4`; `O+` → `constant: 1`, `planes: 4`;
`Otilde+` → `constant: 1`):

```
lattice.Aut()                                   0.01 s    full O(Λ₂)
lattice.O_plus()                                0.19 s    {g in O(L) : spinor-norm predicate}
lattice.stable_orthogonal_group()              48.01 s    {g in O(L) : reflective predicate}
```

Orbit calls, same harness:

```
Λ₂, O,  rank 1 :  1 orbit,  115.06 s     valid run result; the card has no O line row
Λ₂, O+, rank 1 :  did not return within 900 s (killed; peak tree 3122 MiB, julia 2707 MiB)
Λ₂, O,  rank 2 :  did not return within 240 s in the earlier run
```

**What this does and does not establish.** The card's `O+` → `constant: 1` row is *not* yet
computed: the subgroup route did not return, so the row is an unavailable result and is
recorded as a dependency, not as a count. The `O` count of 1 is a real public-call result and
is deliberately not used as that row — one `O`-orbit is one `O+`-orbit only if some element
outside `O+` lies in the line's stabilizer, and whether `-id` is in `O+` here is exactly the
convention that must not be assumed in signature (2,19).

**Reproducing the row requires one of:** the subgroup enumeration returning (currently >900 s),
or the stabilizer/index statement itself — exhibit an isometry of the line with spinor norm
`-1` through the public calls, which is the shorter proof and the one to attempt next.

## Public-call failures found on these specimens, with their owners

1. **`discriminant_sequence_data()` raises on any lattice containing `U ⊕ U`.**
   `TypeError: int() argument must be a string, a bytes-like object or a real number, not
   'OwnedJoinCategory.element_class'` at
   `../sage-indefinite-port/src/sage_indefinite_port/indefinite/recursive.py:154`,
   `source_coordinates = tuple(int(coordinates(label)) for label in source_labels)`.
   Reproduced on `U+U` (0.76 s), `L_1 = U+U+⟨-2⟩` (0.69 s), `U+U+E8` (7.46 s) and `Λ₂`
   (129.68 s / 71.24 s).  Owner: **the indefinite port** — it converts an owned coordinate
   with `int()` instead of crossing the owned boundary.  `A2` and `E8` answer, so the defect
   is the `U` summand's coordinate labels, not the method's contract.

2. **`discriminant_group()` costs 45.95 s on `Λ₂`** (rank 21, indefinite), and `A2`'s
   `discriminant_sequence_data()` costs 64.36 s.  Both are over the 20 s call ceiling and are
   **cost**, owned by #306; neither is a wrong answer.

Neither of these blocks the structural unit above, which passes in 0.65 s using
`conway_sloane_genus_symbol()` (0.03 s) for the discriminant structure rather than the two
expensive calls.
