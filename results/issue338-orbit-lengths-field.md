# #338: 029J's plane orbit lengths are a card field, and the digest and reader carry it

**Result: the digest carries `orbit_lengths`, `card_plane_orbit_lengths` reads that field,
and the #331 plane test passes on the regenerated digest.** No sentence is parsed for a
plane row any more.

Measured on `6d486c210ff7af389f893f44596f5533fc5e320e` (`main`, the parent of this
commit), on the adopted runtime: Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1, with the
indefinite port project bound at `/work`.

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
