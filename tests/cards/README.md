# Card rows read by the acceptance tests

`lattice-database-enriques.json` holds the rows of `dzackgarza/lattice-database`
that this repository's acceptance tests compare against, so a test never types
an expected number of its own. It is generated, not edited:

```
python3 tests/cards/refresh_lattice_database_enriques.py --ref <40-character database commit>
```

`_provenance.ref` names the database commit the digest was read at; the digest
was last refreshed at `587d56febe5856d54c6bc9fc023fa5a425f76bfb`. The script
fetches only the front matter of the named cards and keeps only the rows the
tests read, so a refresh is one HTTP request per card and the diff is the
database's change, not a transcription.

What is read, and from where:

| field | card | row |
| --- | --- | --- |
| `arithmetic_groups[tag].lattice`, `.parent_group` | `arithmetic-groups/gamma-h-N.md` | `lattice`, `parent_group` |
| `arithmetic_groups[tag].latex` | same | `latex` — the subset `S` of the Coxeter diagram, with the paper's overline when the printed set is a complement |
| `arithmetic_groups[tag].cardinality` | same | `data.cardinality` — the order of `/bar Gamma_h` |
| `arithmetic_groups[tag].line_orbits`, `.plane_orbits`, `.flag_orbits` | same | `data.line_orbits`, `data.plane_orbits`, `data.flag_orbits` — `#I_1`, `#I_2`, `#I_12` |
| `arithmetic_groups[tag].citation` | same | `data.reference.citation` — the paper, its table and page |
| `polarization_counts.rows[degree].primitive_classes`, `.group_classes` | `lattices/0128.md` | `integral.polarization_counts.{2d}.#h`, `.#Γ̄_h` |
| `polarization_counts.rows[degree].citation` | same | `integral.polarization_counts.{2d}.reference.citation` |

The paper the orbit rows come from is D. Dutour Sikirić and K. Hulek, *Moduli of
polarised Enriques surfaces — computational aspects*, J. London Math. Soc. 110
(2024), arXiv:2302.01679; the pages the cards cite are Table 1 (p. 13), Table 2
(p. 14) and Table 4 (p. 17) of version 2 (26 Sep 2023), which is the version
those page numbers were checked against.

The port's `tests/fixtures/DATA_SOURCES.md` in `dzackgarza/sage-indefinite-port`
lists the same sources. The port is paused; nothing here reads it.
