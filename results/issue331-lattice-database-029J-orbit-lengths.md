# The row `029J` does not hold: per-orbit lengths of its isotropic planes

Card `dzackgarza/lattice-database` → `lattices/029J.md` states, in
`integral.primitive_orbits`,

```yaml
  O:
    planes: 2          # two O(T_En)-orbits of primitive isotropic planes
  Otilde+:
    planes: 24242      # the total number of 1-cusps of M~_En
```

The per-orbit split of `24242` into `527` and `23715` exists only in the rows'
`reference.citation` sentences.  Issue #331's test needs those two numbers by tag, so this
is the row to file; the digest `tests/cards/lattice-database-enriques.json` then has to be
regenerated rather than edited:

```
python3 tests/cards/refresh_lattice_database_enriques.py --ref <new database commit>
```

## Proposed card change

Under `integral.primitive_orbits.Otilde+`, next to `planes: 24242`:

```yaml
  Otilde+:
    constant: 528
    planes: 24242
    orbit_lengths: [527, 23715]
    reference:
      citation: >-
        ... unchanged; Dutour Sikirić, Hulek, "Moduli of polarised Enriques
        surfaces — computational aspects", J. London Math. Soc. 110 (2024),
        arXiv:2302.01679, Section 3.6 (The Tits building), p. 22: ... under
        O^+_10(F_2) the 528 lines fall in two orbits, of lengths 527 and 1, and
        the 24242 planes in two orbits, of lengths 527 and 23715.
```

and, under `integral.primitive_orbits.O` (which names the representatives, so the order of
the pair is the order of `P_1`, `P_2`):

```yaml
    orbit_lengths: [527, 23715]
```

The corresponding addition to the digest is one field per row,
`orbit_lengths`, read in `tests/cards/refresh_lattice_database_enriques.py`'s
`plane_orbits(...)` beside `"planes": row["planes"]`.

## Why it is not filed here

The row belongs to `dzackgarza/lattice-database`, and this session's GitHub connection is
scoped to `dzackgarza/sage-extensions` with no issue or pull-request write.  So the
numbers are read, until the row lands, from the card's own recorded sentence by
`card_plane_orbit_lengths` in `src/sage_extensions/lattice_database.py`, which checks the
pair against the card's row total and against its count of `O`-orbits and raises if either
disagrees.
