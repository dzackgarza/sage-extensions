# #319 — the card rows of the 87 numerical polarizations and of card 0128

Commit: (this commit, `main`).

This unit adds tests and edits no library file.  The acceptance module exists, runs
end to end, and decides every row it can; the rows it cannot decide are reported
`UNDECIDED` with the cap and the stage, which is red, not a pass.  **No row of the
87 polarization cards is decided today**: the public call of #286 does not return on
`Gamma_h` for the smallest of them, and the same call blocks the second line of
every Table 4 row.

## What landed

| path | what it is |
| --- | --- |
| `tests/cards/lattice-database-enriques.json` | the rows, read from `dzackgarza/lattice-database` at commit `587d56febe5856d54c6bc9fc023fa5a425f76bfb`: the 87 `gamma-h-N` cards (lattice, parent group, LaTeX subset `S`, `|Gamma-bar_h|`, `#I_1`, `#I_2`, `#I_12`, citation) and card `0128`'s `integral.polarization_counts` rows per degree `2d = 2, ..., 72` (`#h`, `#Gamma-bar_h`, citation) |
| `tests/cards/refresh_lattice_database_enriques.py` | regenerates that digest from one database commit; it refuses a ref that is not a full 40-hex SHA |
| `tests/cards/README.md` | which card field backs which digest field, and the paper version the cited pages belong to |
| `tests/enriques_polarization_rows_by_card.py` | the acceptance module: builds each lattice and group as its card states, calls the public method, compares, prints a defect block on a difference, exit 1 on any difference or undecided row |
| `.github/workflows/enriques-polarization-rows.yml` | the one CI job the long rows live in: `workflow_dispatch` (cards, degrees, per-call cap, budget) and nightly, 350-minute ceiling.  Stored at `results/issue319-enriques-polarization-rows.workflow.yml`: the GitHub connection of this session has no `workflows` permission, so a push creating a file under `.github/workflows/` is rejected for the whole ref (measured; see below) |

## The acceptance, item by item

**One test module reads each card value by its tag and compares it with the call's
result through the same public call that #286 uses.**  `tests/cards/…json` is written
by the refresher from the cards themselves; the module reads a row by its card tag
(`gamma-h-N`, or `0128` and a degree) and compares:

* a `gamma-h-N` row: the card names the lattice (`029J`, $N = U \oplus U(2) \oplus
  E_8(-2)$) and the parent group (`o-t-en`, $O(N)$), and its LaTeX names the subset
  $S$ that $h$ is orthogonal to — `\overline{\{0\}}` for card 1, `\emptyset` for card
  87.  The module builds $h = \sum_{i \in S} g_i$ in the paper's $g$-basis (equation
  (7), p. 9), transports it to the invariant lattice, and takes
  `Involutions.I_En.polarized(h).coinvariant_extension_subgroup()` — $\Gamma_h$ as
  equation (5), p. 7, defines it.  The three counts are
  `isotropic_orbit_representatives(1)`, `(2)` and `(2, flag=True)`:
  `PredicateSubgroups.isotropic_orbit_representatives`, the public call of #286 on
  which `cusps` and `tits_building_incidence` are built.
* an `0128` row: `#h` is `Lattices(ZZ)(W).Aut().vector_orbit_representatives(2d)` on
  the card's own lattice, and `#Gamma-bar_h` is the number of distinct
  line/plane/flag triples the call returns over those classes — the paper's own class
  invariant is the order and the orbit sizes of the group (p. 11).

Every row prints its card's citation, which names the paper, the table and the page:
Table 1, p. 13 for cards 1–41 and Table 2, p. 14 for cards 42–87, Table 4, p. 17 for
the degree rows, all of arXiv:2302.01679 **version 2 (26 Sep 2023)** — the version
those page numbers were checked against.

The decode is not trusted on its own: over the 87 cards it reproduces, row for row,
the subset and the three counts that `tests/lattices/test_enriques_polarization_orbits.sage`
transcribed from pages 13 and 14 — 87 cards compared, 0 disagreements, 87 distinct
subsets (`python3 -` over the digest and that module's `_CASES`; recorded in
`.tmp/qc-evidence/INDEX.md`).

**A mismatch is filed the same day; a tolerance or a skipped row is not a pass.**
Nothing today *differs*: the rows are undecided, because the call does not return.
That is itself the defect to file, and it names the lattice and the group:

```
dzackgarza/sage-extensions — the public isotropic-orbit call does not return on Gamma_h
  lattice: 029J (U + U(2) + E8(-2), rank 12, signature (2,10), determinant 1024)
  group:   gamma-h-1 = Gamma_h of case 1, S = overline{0}, |Gamma-bar_h| = 696729600
  row:     #I_1 = 5, #I_2 = 9, #I_12 = 18 (D. Dutour Sikirić, K. Hulek,
           arXiv:2302.01679, Table 1, p. 13)
  measured: Gamma_h builds in 38.0 s, contains_character_kernel() and
           character_data_is_complete() are True, discriminant_image().order() is the
           card's 696729600 in 136.7 s; isotropic_orbit_representatives(1), (2) and
           (2, flag=True) each did not return in 300 s
```

The connected GitHub connection of this session cannot create issues (it reads issues
and writes branches only), so this block is what the orchestrator posts; it is written
here rather than left implicit.

## What is decided today, with its output

* **Card `0128`, degree 6 (`#h`).** The card says 2; the call returns 2 in 285 s:
  `#h: expected 2, call 2 (285 s)` — `.tmp/qc-evidence/p319-0128-runner-degree-6.log`.
* **Card `0128`, the `#Gamma-bar_h` line of degree 6.** Undecided: class 1 of 2
  transfers to the invariant lattice (`q = 6`), the group builds, and the line call
  does not return in 300 s.  The same call blocks the row at every other degree.
* **The `#h` line above degree 6.** Not measured: `2d = 2, 4, 8, 10, 12` did not
  return in 120 s each on the card's own lattice (`.tmp/qc-evidence/p319-0128-h-unimodular.log`);
  they belong to the CI job at its 1800 s cap.
* **All 87 `gamma-h-N` rows.** Undecided: the group is the card's, the counts are not
  reachable.  `gamma-h-1` is the cheapest of the 87 by every published count (5 line
  orbits, the smallest row), so the block is not a per-card cost.

## What this unit did not do

* No library file is edited, so the missing capability is not repaired here; it is
  named above.
* `#Gamma-bar_h` is compared nowhere yet: it needs the same orbit call the
  `gamma-h-N` rows need, so it becomes decidable when they do.
* The workflow file is not installed under `.github/workflows/`.  The push that
  carried it there was rejected — `refusing to allow a GitHub App to create or update
  workflow .github/workflows/enriques-polarization-rows.yml without workflows
  permission` — so it sits at `results/issue319-enriques-polarization-rows.workflow.yml`
  with the one-command install in its header, and `just enriques-card-rows` runs the
  same module from any checkout with the Sage container.
* The job has not run: no run of this repository's CI has ever run (the shared
  workflow drops the Sage container when the caller passes a setup recipe).  The job
  is written so that the rows report progressively: `--cap` bounds one call,
  `--budget` bounds one run, and a run that exhausts its budget names the rows it did
  not reach instead of failing without a finding.
