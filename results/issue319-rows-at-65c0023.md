# Eight rows decided at `65c0023`, and coverage reads the card rather than the label

`main` `65c0023c3663b3c1ac4d7fa901828679df98ce7f`, 2026-11-23.  The rows below were
measured in this checkout, one child process a row, on the adopted runtime
(SageMath 11.0.beta5, Python 3.14).  Their raw records are the eight lines this
commit appends to `results/issue319-rows-ledger.jsonl`; each carries the card's tag,
the lattice and group its card names, the expected value read from the card, the
value the public call returned, the state, the elapsed time and the source revision
`65c0023c3663` the run was made at.

## 1. The aggregate defect this round repaired

`--coverage` counted a required row decided when its ledger line said `PASS`.  The
ledger is a file: one line per attempt, written by whichever run measured the row,
read later by a process that measured nothing.  The label is that run's state, not a
comparison, so a line whose `returned` disagreed with the row's card was coverage of
that row all the same.

`fefeca8` writes the three ledgers that show it, and fails on two of them before the
repair: a line labelled `PASS` returning one more than the card (`--coverage` exits
0, "all 1 required rows have a PASS in the ledger"), and a self-consistent line whose
own `expected` is not the card's (also exits 0).  `65c0023` compares every attempt's
returned value against the number the card states, read by the row's tag when
coverage runs, and against nothing else the line carries.  The card's number is read
by `card_row_value`, bound in `tests/engineering/conftest.py` to the same public
reader the module measures against, so the regression types no expected value.

Run over the ledger as it stood before this round the repaired rule still decides 241
of the 349 rows, so it refuses no line the earlier rule accepted; it names the
revision each decided row was measured at, which is what makes "241 decided" a
statement about those revisions and not about this checkout's.

  tests/engineering/test_a_ledger_pass_is_the_cards_number_or_it_is_absent.py
    before the repair   2 failed, 1 passed in 5.86 s
    after it            3 passed in 4.57 s  (test_lint loaded, clean)

## 2. The eight rows, and what each was compared with

| row | card's value (read by tag) | call | time | citation |
| --- | ---: | ---: | ---: | --- |
| `6JRX:O:planes` | 4 | 4 | 92.0 s | Scattone, Prop. 5.4.7 with Cor. 5.4.8(2), Section 6.2 |
| `6JRX:O+:planes` | 4 | 4 | 95.2 s | Scattone, Section 6, Section 6.2 |
| `6JRY:O:planes` | 9 | 9 | 107.4 s | Scattone, Prop. 5.4.7 with Cor. 5.4.8(2), Section 6.3 |
| `6JRY:O+:planes` | 9 | 9 | 108.5 s | Scattone, Section 6, Section 6.3 |
| `gamma-h-2:flags` | 28 | 28 | 172.4 s | Dutour Sikirić–Hulek, Table 1, case 2, `#I_12` |
| `gamma-h-14:flags` | 76 | 76 | 211.3 s | Dutour Sikirić–Hulek, Table 1, case 14, `#I_12` |
| `6JRX:O+:lines` | 1 | 1 | 2.1 s | Scattone, Section 6, Section 6.2 |
| `6JRY:O+:lines` | 1 | 1 | 2.1 s | Scattone, Section 6, Section 6.3 |

The four plane rows are the plane rows of Scattone's two period lattices: the whole
call `group.isotropic_plane_orbits` does not enter, because a card row of those tags
names the whole orthogonal group or its index-two subgroup, so the row is
`isotropic_orbit_representatives(2)`, and on `6JRX`/`6JRY` that returns.  The two
`O+` line rows return in 2 s.

`gamma-h-2:flags` is the row that was previously absent for a reason other than "no
attempt": its three attempts at `56f0ec8` include a `BROKEN` one
(`ValueError: Generic morphism … From: Integral lattice of rank 1 and signature (0, 0)
To: … rank 10 and signature (1, 9) is not a morphism`), so coverage refused the row
at that revision even though two attempts had returned the card's 28.  At `65c0023`
it returns 28 in 172.4 s.  The intermittency is not repaired by this round: the
`56f0ec8` attempts are still in the ledger, coverage still reads a row's attempts at
the latest revision it was tried at, and a later `BROKEN` attempt at the same
revision would make the row absent again.

The raw lines appended (from `results/issue319-rows-ledger.jsonl`):

```json
{"row": "6JRX:O:planes", "card": "6JRX", "quantity": "planes", "degree": null, "lattice": "6JRX: Lambda_2", "group": "O", "expected": 4, "returned": 4, "detail": null, "state": "PASS", "elapsed": 92.0, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:10:47Z"}
{"row": "6JRX:O+:planes", "card": "6JRX", "quantity": "planes", "degree": null, "lattice": "6JRX: Lambda_2", "group": "O+", "expected": 4, "returned": 4, "detail": null, "state": "PASS", "elapsed": 95.2, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:10:47Z"}
{"row": "6JRY:O:planes", "card": "6JRY", "quantity": "planes", "degree": null, "lattice": "6JRY: Lambda_4", "group": "O", "expected": 9, "returned": 9, "detail": null, "state": "PASS", "elapsed": 107.4, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:14:41Z"}
{"row": "6JRY:O+:planes", "card": "6JRY", "quantity": "planes", "degree": null, "lattice": "6JRY: Lambda_4", "group": "O+", "expected": 9, "returned": 9, "detail": null, "state": "PASS", "elapsed": 108.5, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:14:41Z"}
{"row": "gamma-h-2:flags", "card": "gamma-h-2", "quantity": "flags", "degree": null, "lattice": "029J: U + U(2) + E8(-2)", "group": "Gamma_h,2", "expected": 28, "returned": 28, "detail": null, "state": "PASS", "elapsed": 172.4, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:17:46Z"}
{"row": "gamma-h-14:flags", "card": "gamma-h-14", "quantity": "flags", "degree": null, "lattice": "029J: U + U(2) + E8(-2)", "group": "Gamma_h,14", "expected": 76, "returned": 76, "detail": null, "state": "PASS", "elapsed": 211.3, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:21:26Z"}
{"row": "6JRX:O+:lines", "card": "6JRX", "quantity": "lines", "degree": null, "lattice": "6JRX: Lambda_2", "group": "O+", "expected": 1, "returned": 1, "detail": null, "state": "PASS", "elapsed": 2.1, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:21:40Z"}
{"row": "6JRY:O+:lines", "card": "6JRY", "quantity": "lines", "degree": null, "lattice": "6JRY: Lambda_4", "group": "O+", "expected": 1, "returned": 1, "detail": null, "state": "PASS", "elapsed": 2.1, "revision": "65c0023c3663b3c1ac4d7fa901828679df98ce7f", "measured_at": "2026-11-22T22:21:44Z"}
```

Every run selected its rows from the module's own enumeration and exited 0; no row
printed a `DEFECT` block, so nothing on these lattices and groups disagrees with its
card.  No expected value was edited to fit a call, and the digest was not touched.

## 3. Coverage after this round

`--coverage results/issue319-rows-ledger.jsonl`, one process:

```
COVERAGE over the 349 required rows of this selection
  decided 249, absent 100
  the decided rows rest on the revision each was measured at: 0efed8380e3d (18),
  56f0ec868006 (41), 652baf651b5d (38), 65c0023c3663 (8), 85336defad09 (87),
  97f2f72507c5 (56), f5e7fddf2c83 (1)
```

Every absent row is absent for one reason: it has no attempt recorded.

| dimension | decided | absent | absent rows |
| --- | ---: | ---: | --- |
| `0128` `#h` | 36 | 0 | — |
| `0128` `#Gamma_h` | 11 | 25 | 2d = 24, 26, 28, …, 72 |
| `029J` lines / planes | 3 / 3 | 0 | — |
| `otilde-plus-t-en` lines / planes | 1 / 1 | 0 | — |
| `6JRX` / `6JRY` lines | 1 / 1 | 1 / 1 | `6JRX:Otilde+:lines`, `6JRY:Otilde+:lines` |
| `6JRX` / `6JRY` planes | 2 / 2 | 0 / 0 | — |
| `gamma-h-N` lines | 87 | 0 | — |
| `gamma-h-N` planes | 87 | 0 | — |
| `gamma-h-N` flags | 14 | 73 | N = 15 … 87 |

## 4. What this does not establish

* **241 of the 249 decided rows rest on earlier revisions** — `85336defad09` (87
  line rows), `97f2f72507c5` (56), `56f0ec868006` (41), `652baf651b5d` (38),
  `0efed8380e3d` (18), `f5e7fddf2c83` (1).  Only the eight above rest on `65c0023`.
  A row decided at an earlier revision is evidence about that revision: it is not a
  statement that this checkout's code returns the card's number, and O1 is not
  decided by it.
* **100 rows have no computed value at all**: the 73 `gamma-h-15` … `gamma-h-87`
  flag rows, the 25 `0128` `#Gamma_h` rows at 2d = 24 … 72 (each needs the line,
  plane and flag counts of every primitive class of that degree), and the two
  `Otilde+(Lambda_k)` line rows.  The last two are the filed memory defect: on
  `6JRX` the row was at 5974 MiB and rising at 834 s (`results/issue319-6jrx-otilde-plus-line-row.md`),
  and on `6JRY` at 6312 MiB in 90 s (`results/issue319-6jry-otilde-plus-line-row.md`).
* **The per-row cap is not a hard bound on this host.**  `--cap` is enforced with
  `signal.alarm`, and the alarm is intermittently not delivered once the row is
  inside the GAP walk: the row then runs to completion and reports the value it
  computed (observed on `gamma-h-1:lines` with `--cap 1`: 36.7 s, `PASS`, exit 0).
  A lost cap cannot produce a false agreement — the value still has to equal the
  card's — but a row can outlast the cap the matrix gives it.

O1 and O4 remain open.
