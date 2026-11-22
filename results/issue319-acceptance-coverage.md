# Which rows of the published-family acceptance have current computed values

Audit of #319 at `main` `97e9335`, 2026-11-21.  Coverage is checked in the tree;
values are cited with the record and revision they were measured at.  A row with
no current-revision record is *pending*, not passed.

## 1. The matrix covers every row

`tests/enriques_polarization_rows_by_card.py` enumerates 349 rows: 6 for `029J`,
2 for `otilde-plus-t-en`, 4 each for `6JRX` and `6JRY`, 261 for the 87
polarizations (lines, planes, flags), and 72 for `0128` (`#h` and `#Gamma_h` at
each of the 36 degrees the card states).

`.github/workflows/enriques-polarization-rows-full.yml` is a matrix of 20 jobs
whose `args` cover **92 tags — the 87 `gamma-h-N` and the five card tags — with no
gap and no duplicate**, verified by reading every entry's `--tags` against the
digest's arithmetic-group keys.  Each job keeps the same container, `--cap 1800`
and report, with its own `--budget`.  No row of the module is outside the matrix.

## 2. Wiring defect: two scheduled workflows run the same acceptance

Two workflows are on `main` and both are scheduled:

| workflow | schedule | shape |
| --- | --- | --- |
| `.github/workflows/enriques-polarization-rows.yml` | `17 3 * * *` | one job, every row, `--budget 18000` |
| `.github/workflows/enriques-polarization-rows-full.yml` | `43 3 * * *` | the 20-job matrix |

The first is the shape whose run 44924240209 spent its 19200 s at row 36 of 349
and reported 313 rows not reached; the matrix was built to replace it and did not
retire it.  Two nightlies therefore run the same 349 rows, and the older one
cannot finish.  Correction, which this connection cannot push (no `workflows`
permission):

```
git rm .github/workflows/enriques-polarization-rows.yml
```

`just enriques-card-rows` runs the same module from any checkout and is
unaffected.

## 3. Values with a current-revision record

| family | rows | values | record |
| --- | ---: | --- | --- |
| `029J` (O, Otilde+, gamma-en-2) | 6 | 2, 2, 528, 24242, 5, 9 — all PASS | this session at `9e36bc4`: 7.2, 0.1, 93.2, 29.0, 39.2, 30.8 s |
| `otilde-plus-t-en` | 2 | 528, 24242 — PASS | this session at `9e36bc4`: 98.4, 28.3 s |
| `6JRX` | 4 | 4, 1, 4, 1 — PASS | this session at `9e36bc4`: 90.9, 9.9, 95.1, 2.1 s |
| `6JRY` | 4 | 9, 1, 9, 1 — PASS | this session at `9e36bc4`: 101.9, 6.6, 114.9, 2.1 s |
| `0128` `#h` | 3 of 36 | 1, 2, 2 at `2d` = 2, 4, 6 — PASS | this session, 3.9, 5.6, 4.2 s |
| `0128` `#Gamma_h` | 10 of 36 | 2, 2, 2, 3, 3, 3, 4, 4, 4, 5 at `2d` = 4 … 22 — PASS | `results/issue622-the-table-4-rows-one-per-probe.md`, at `acb675c` |
| `gamma-h-*` lines | 87 | each card's `line_orbits` — 87 pass, 0 fail | `results/issue17-gamma-h-line-rows.md`; the revision is the one that record names |
| `gamma-h-*` flags | 87 | each card's `flag_orbits`, returned where the plane row did not | `results/issue620-plane-row-cost.md`, at `b0801b6` |

The two `Otilde+` line rows of the Scattone lattices are the rows repaired today
(`results/issue618-the-ambient-family-is-the-cost.md`): before the repair they had
no value at all.

## 4. Pending, exactly

* **`0128`, all 72 rows.**  GitHub run 44998090134's job 137180730795 (Table 4,
  `#h` and `#Gamma_h`) is the current-revision run and has not reported.  Within
  it, `#622`'s review names what it needs first: `0128:#Gamma_h:2` has no
  current-revision raw outcome (its 252 s value predates `364ab82`'s successor
  chain), `0128:#Gamma_h:4` and degrees 6 through 22 need revalidation at the
  current revision, and degrees 24 through 72 have no record at all.
* **`gamma-h-*` planes, 87 rows.**  `#620` repaired the seeding and is MET as a
  repair, but the record measures one card (`gamma-h-25`) at `b0801b6`; the other
  86 plane rows have no current-revision value.
* **`gamma-h-*` lines and flags** — decided as recorded above; their revalidation
  at the current revision is what the matrix's 15 polarization jobs produce, and
  those per-row outcomes live in the run's logs, not in this tree.

Nothing in this audit changes an expected value.  A computed value that differs
from its card is a defect of the public call of #286 and belongs to that owner;
none is known at this revision.
