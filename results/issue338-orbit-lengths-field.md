# #338: 029J's plane orbit lengths are a card field, and the digest and reader carry it

**Result: the digest carries `orbit_lengths`, `card_plane_orbit_lengths` reads that field,
and the #331 plane test passes on the regenerated digest.** No sentence is parsed for a
plane row any more.

Measured on `6d486c210ff7af389f893f44596f5533fc5e320e` (the tree the change was written
on; the commit's parent in the pushed history is `959d926`, and
`git diff --stat 6d486c2 959d926 --` over the five files below is empty), on the adopted
runtime: Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1, with the indefinite port project bound
at `/work`.  Re-measured on `main` at `dbe90c02` in the section at the end of this file.

## The card, and the pin

`dzackgarza/lattice-database` `d6a539339bac5ea0ee8d8bde5dc19564955eb152` states the split
as a row field on card `029J`, in the order its citation names its representatives:

```
O:        constant: 2     planes: 2      orbit_lengths: [527, 23715]
Otilde+:  constant: 528   planes: 24242  orbit_lengths: [527, 23715]
```

The digest's pin was `587d56febe5856d54c6bc9fc023fa5a425f76bfb`; it is now that commit.
The previous digest hold on `029J`'s sentence — `"the 24242 planes in two orbits, of
lengths 527 and 23715"` — is what `card_plane_orbit_lengths` used to match with a regular
expression.

## What changed

* `tests/cards/refresh_lattice_database_enriques.py` — `plane_orbits()` emits each row's
  `orbit_lengths` as the list the card states (int-converted, card order), and the
  digest's `_provenance.rows.plane_orbits` names the field it now reads.
* `tests/cards/lattice-database-enriques.json` — **regenerated**, not edited:
  `python3 tests/cards/refresh_lattice_database_enriques.py --ref d6a539339bac5ea0ee8d8bde5dc19564955eb152`
  (`87 group cards, 36 polarization-count degrees, 1 discriminant forms`).  The diff is
  the pin, the provenance line, `orbit_lengths` on the two `029J` rows, and the two rows'
  citations as the card now states them.  No other row's numbers changed.
* `src/sage_extensions/lattice_database.py` — `card_plane_orbit_lengths` reads
  `rows[group]["orbit_lengths"]` and returns it sorted.  The plane phrase and its regex
  are gone.  The checks stay, and follow the card's own schema: the pair must agree with
  the row's `planes` under one of the two readings a card uses — the *number* of orbits
  (`O` states 2) or the *total* (`Otilde+` states 24242) — and its number must be the
  card's own `O` orbit count.  A row that states a total without the split raises naming
  the row and the field, instead of falling back to its citation.
* `tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage` — the module
  docstring said the split came from the card's sentence and asked for a structured row
  upstream; it now says the field is read by tag.  Its assertions are unchanged.
* `tests/cards/README.md` — the digest's row table names `.orbit_lengths` and `.lines`.

## Runs

| run | result |
| --- | --- |
| `tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage` (#331) | **2 passed in 93.76s** |
| `tests/lattices/test_the_enriques_line_rows_by_card.py` | **3 passed in 3.67s** |
| `tests/lattices/test_discriminant_form_of_the_coble_lattice.sage` | **7 passed in 13.73s** |

Reader behaviour by hand, on the regenerated digest:

```
card_plane_orbit_lengths('029J','O')       -> (527, 23715)
card_plane_orbit_lengths('029J','Otilde+') -> (527, 23715)
card_plane_orbit_row('029J','O')           -> 2
card_plane_orbit_row('029J','Otilde+')     -> 24242
card_plane_orbit_lengths('6JRX','O')       -> KeyError: states the total ... but not the
                                              lengths ... read from the row's own
                                              `orbit_lengths` field, not from its citation
```

**Not run to a result:** `tests/lattices/test_the_coble_lattice_line_orbit_call_returns.sage`
was in a selection that reached the 1800 s cap after seven passing tests.  That test's
inputs are byte-identical under this commit — `card_line_orbit_row` is untouched and the
digest's `lines` values (2, 528, 5) are unchanged context in the diff — so its behaviour is
that of the parent commit; it is the heavy indefinite-lattice row call, not a reader of
this field.  It is reported here rather than claimed green.

## Issue closure text

> Card `029J` states `orbit_lengths: [527, 23715]` on its `O` and `Otilde+` rows at
> `dzackgarza/lattice-database` `d6a5393`.  The digest
> `tests/cards/lattice-database-enriques.json` was regenerated at that pin by
> `refresh_lattice_database_enriques.py` (which now emits the field, and names it in the
> digest's `_provenance`), and `card_plane_orbit_lengths` reads the field instead of
> matching a sentence; the plane phrase and its regex are removed.  The checks follow the
> card's schema — the pair agrees with the row's `planes` as either the number of orbits or
> the total, and its number matches the card's `O` orbit count — and a row without the
> field raises.
>
> `tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage` 2 passed in
> 93.76 s; `test_the_enriques_line_rows_by_card.py` 3 passed in 3.67 s;
> `test_discriminant_form_of_the_coble_lattice.sage` 7 passed in 13.73 s.

## Re-verification on `main` at `dbe90c02` (the four batch steps, re-run)

**Step 1 — the digest is the script's output at the pin, and the script emits the field.**
In a detached worktree of `main` (`dbe90c02ae778d5241e1c897b4cbea872c167985`), regenerating
at the pin the digest records reproduces the committed file byte for byte:

```
$ python3 tests/cards/refresh_lattice_database_enriques.py --ref d6a539339bac5ea0ee8d8bde5dc19564955eb152
wrote .../tests/cards/lattice-database-enriques.json at database ref d6a539339bac5ea0ee8d8bde5dc19564955eb152: 87 group cards, 36 polarization-count degrees, 1 discriminant forms

real    0m58.416s
$ cmp tests/cards/lattice-database-enriques.json <the committed blob> && echo IDENTICAL
IDENTICAL
```

`plane_orbits()` emits `orbit_lengths` as the list the card states (int-converted, card
order) and the digest names the field in `_provenance.rows.plane_orbits`.  Card `029J`'s two
rows, as the digest keeps them (citation elided):

```
O        {"lines": 2,   "orbit_lengths": [527, 23715], "planes": 2}
Otilde+  {"lines": 528, "orbit_lengths": [527, 23715], "planes": 24242}
```

**The database's `main` has moved past the pin, and the move changes no row.**  At
`1224b1b184599b4956107336882e5d49c34758ab` (lattice-database `main`, `#33: the chambers at
Sterk's 0-cusps of Gamma_En,2, and the schema field for them`, 2026-11-11 10:31) the same
regeneration gives a one-line digest diff — `_provenance.ref` — and no changed card row: the
new card field is outside what this digest reads.  The pin stays `d6a5393`, the commit this
issue's acceptance names and the one three other results files call "the pin the digest
carries" (`issue297-subgroup-chamber.md`, `issue335-plane-row.md`,
`issue339-undecided-membership-repair.md`); a pin-only bump would falsify those sentences
without changing a number.

**Step 2 — the reader reads the field, and the plane sentence parser is gone.**
`_ORBIT_LENGTH_PHRASE` and its `re.compile` are deleted; `card_plane_orbit_lengths` reads
`rows[group]["orbit_lengths"]` and raises when a row states a total without it.  By hand, on
the regenerated digest:

```
card_plane_orbit_lengths('029J','O')        -> (527, 23715)
card_plane_orbit_lengths('029J','Otilde+')  -> (527, 23715)
card_plane_orbit_row('029J','O')            -> 2
card_plane_orbit_row('029J','Otilde+')      -> 24242
card_plane_orbit_lengths('6JRX','O')        -> KeyError: states the total ... but not the lengths ...
card_plane_orbit_lengths('6JRY','O')        -> KeyError: same
card_line_orbit_lengths('029J','Otilde+')   -> (1, 527)
```

The last line is `#310`'s *line* row, which still reads its sentence
(`_LINE_ORBIT_LENGTH_PHRASE`); `#338` is the plane rows.

**Step 3 — runs.**  From the same worktree, the indefinite port bound at `/work`:

```
$ ./run.sh -w /work -b <port>:/work -b <ai-review-ci>:/ci -b <worktree>:/repos/sage-extensions -- \
    /bin/sh -c 'cd /repos/sage-extensions && \
      export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src && \
      exec /sage/.venv/bin/python -u -m pytest \
        tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage \
        tests/lattices/test_the_enriques_line_rows_by_card.py \
        tests/lattices/test_discriminant_form_of_the_coble_lattice.sage \
        tests/lattices/test_genus_of_the_scattone_summands.sage \
        tests/lattices/test_setwise_stabilizer_of_an_enriques_plane.sage \
        tests/enriques_polarization_rows_by_card.py \
        -q -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
        -p sage_extensions.testing.test_lint --no-time-gates --tb=short -rf -p no:cacheprovider'

.....................                                                    [100%]
========================== test-call performance gate ==========================
tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage::test_the_plane_classes_and_their_cusp_count_are_card_029J_s_rows: 77.45 s > 20 s
tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage::test_the_plane_that_does_not_split_has_an_exact_discriminant_image: 121.80 s > 20 s
tests/lattices/test_genus_of_the_scattone_summands.sage::test_the_degree_two_summand_genus_has_the_cards_class_count: 143.26 s > 20 s
tests/lattices/test_genus_of_the_scattone_summands.sage::test_the_degree_four_summand_genus_has_the_cards_class_count: 51.08 s > 20 s
tests/lattices/test_setwise_stabilizer_of_an_enriques_plane.sage::test_every_setwise_stabilizer_generator_is_an_isometry_preserving_the_plane: 155.22 s > 20 s
21 passed in 575.42s (0:09:35)
[peakrss] issue338: child waited=0 shell_code=0 samples=293
[peakrss] peak tree RSS      : 2395 MiB
launcher exit: 0
```

The `test-call performance gate` lines are the run's informational per-call report;
`--no-time-gates` is what these rows need and nothing failed.

**`tests/lattices/test_scattone_plane_orbits.sage` — does not finish, and this change is not
on its path.**  Run alone with a 5400 s inner cap on the same worktree, it printed one dot:

```
.[peakrss] issue338: child waited=124 shell_code=124 samples=2693
[peakrss] peak tree RSS      : 1469 MiB
launcher exit: 124
```

The dot is `test_the_card_inputs_are_the_published_rank_21_lattices`, which passes: both
rank-21 cards build from their tags.  Its second test,
`test_6jrx_has_the_cards_plane_orbits_under_o`, was still running when the cap killed the
run.  That test and the three after it call `card_plane_orbit_row` — the row's `planes` total,
which this change does not touch (`orbit_lengths` is added beside it, and `planes` is
unchanged context in the digest diff of `cec2ff7`) — and then enumerate the primitive isotropic
planes of a rank-21 lattice, which `results/issue294-validation-status.md` already records as
never having returned in any attempt.  So the file is unmeasured at this commit rather than
regressed by it, and its cost is #294's to fix, not this issue's.

A first run of the whole seven-file selection was cut by its own inner 2400 s cap after six
tests had passed: the seventh file below was inside that cap when it expired.  The file was
then run on its own with a 5400 s inner cap; that is the run reported here.
