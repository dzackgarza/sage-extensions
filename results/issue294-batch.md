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
