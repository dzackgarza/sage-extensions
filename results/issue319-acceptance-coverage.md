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

## Correction, 2026-11-21

Two counts in the table above are wrong and one gap is missing; each was checked
against the file that settles it.

* **`0128` `#h` is 36 of 36, not 3.**  `results/issue621-the-primitive-stratum.md`
  records the whole family passing — "36 of 36 rows agree with their cards", each
  row in a child process, 3.9 to 5.2 s per row — so every `#h` row has a
  current-revision value and only `#Gamma_h` is pending in that job.
* **The `gamma-h` flag rows have no recorded outcome.**  The table above cites
  `#620`'s opening sentence, that the flag-orbit row "on the same cards returned
  the card's value"; that is a claim in that note, not a run record, and no file
  carries 87 per-row flag outcomes.  They are pending, with the 86 plane rows.
* **The `0128` job cannot reach its own 72 rows.**  Its `#Gamma_h` rows cost 372 to
  887 s each at `2d` = 4 to 22 and cost more as the class count grows, so 72 rows
  do not fit the job's 19200 s budget, and a degree whose class count is large
  passes the 1800 s per-row cap whatever the budget.  The correction is the matrix
  split by degree range carried in
  `results/issue319-enriques-polarization-rows.workflow.yml` — not a changed
  expected value and not a raised cap.

* **The raw logs are not in the repository.**  `.tmp/issue319/`,
  `.tmp/issue618/` and the `.tmp/p621` logs are untracked and absent from the
  remote, so the paths the commit bodies cite cannot be opened by anyone else.
  What stands is the values pasted into those bodies and into this file, and the
  `report.txt` each matrix job now uploads beside its `.timings/`; a raw log under
  `.tmp/` is a working note, not evidence.
* **The `#h` guard ran in no job.**  The `#h` rows are the cheapest in the module
  (about 5 s each) and are the rows the `content=1` reading was repaired against,
  yet no matrix entry selected them: run 44924240209 stopped at row 36 of 349
  before any `0128` row.  The draft now carries a `--tags 0128 --rows "#h"` job.

## Correction, 2026-11-22

* **The duplication is removed.**  `.github/workflows/enriques-polarization-rows.yml`
  is deleted in the commit that carries `results/issue319-rows-2026-11-22.md`, so
  `enriques-polarization-rows-full.yml` — twenty jobs, 92 distinct tags, no gap
  and no duplicate — is the workflow that owns the remaining rows.
* **Section 3's `gamma-h-*` line row is not supported by its record.**
  `results/issue17-gamma-h-line-rows.md` names the port (`991b88b0`) and the card
  digest (`dbc9fc6a`) and no tree revision, so "the revision is the one that
  record names" names nothing: those 87 rows are pending, as the plane and flag
  rows are.
* **Rows with a current-revision value are the 18 of
  `results/issue319-rows-2026-11-22.md`**, each with its raw `@@ROW@@` line in
  `results/issue319-rows-2026-11-22.log` at `97f2f72`: `0128`'s `#Gamma_h` at
  `2d` = 2 and 4, the eight `029J`/`otilde-plus-t-en` rows, `gamma-h-1` to
  `gamma-h-8` planes, and `gamma-h-1` flags.  Every one agrees with its card.
* **Later the same day, 27 rows more.**  The 36 `#h` rows and the nine
  `0128:#Gamma_h` rows at `2d` = 6 to 22 returned at `97f2f72` and agree with
  their cards — all 36 `#h` in 3.6 to 5.2 s, the nine `#Gamma_h` in 341.1 to
  920.1 s — so 63 rows of the 349 have a current-revision value and the raw
  blocks of all of them are in `results/issue319-rows-2026-11-22.log`.  Still
  without one: `0128:#Gamma_h` at `2d` = 24 to 72 (25 rows, never measured), 79
  polarization plane rows, 86 flag rows, 87 line rows, and the 8 `6JRX`/`6JRY`
  rows recorded only at `9e36bc4`.  `#622` is not complete.
* **The line leg is decided at the current revision, and two counts were one low.**
  All 87 `gamma-h-N` line rows returned at `85336de`, every one its card's
  `line_orbits`, in 38.2 to 69.3 s a row and 3737.6 s together
  (`results/issue319-line-rows-2026-11-22.log`, one JSON object a row in
  `results/issue319-line-rows-2026-11-22.jsonl`), so the leg no longer rests on a
  record that names no tree revision.  151 of the 349 rows have a
  current-revision value; the 198 that do not are the 25 `0128:#Gamma_h` rows at
  `2d` = 24 to 72, 79 plane rows, 86 flag rows and the 8 `6JRX`/`6JRY` rows.
  The commit messages carrying the first 64 rows say "18" and "63"; both are one
  low, the flag row being a row of its own.  `#622` is still not complete.
* **The aggregate now decides the no-skip rule, and 205 of 349 rows stand.**
  `results/issue319-rows-ledger.jsonl` is the durable per-attempt record and
  `tests/enriques_polarization_rows_by_card.py --coverage` fails listing every
  required row whose latest attempt is not a `PASS`, so a family's report can no
  longer stand for the acceptance.  At `56f0ec8`: 205 decided, 144 absent, and
  `gamma-h-2:flags` is one of the absent ones because its call raised --
  `ValueError: Generic morphism: From: Integral lattice of rank 1 and signature
  (0, 0) To: Integral lattice of rank 10 and signature (1, 9) is not a morphism`
  -- which is filed as a defect of the flag branch at lattice `029J` under
  `Γ_{h,2}` (Dutour Sikirić-Hulek Table 1 case 2, `#I_12 = 28`), not as a pass.
