# Card `6JRR`'s two orbit fields now have a reader, and both agree

`tests/coble_card_isotropic_orbits.py`, one run
(`.scratch/w286-probes/card-iso-driver2.log`, load 12.7-14.4):

```
[card] 6JRR: the form's orthogonal group built in 0.3 s
[card] the isotropic orbits: 2, of sizes (527, 1), 528 classes
[card] isotropic_orbits: computed 2, card states 2 — agrees
[card] isotropic_classes: computed 528, card states 528 — agrees
[card] the comparison ran in 12.6 s
```

So the card's two remaining fields are read by tag and compared against the
library's own computation, and both agree: `O(q)`'s isotropic orbits on
`A_{T_Co}` are the zero class and one orbit of 527, hence 528 isotropic classes
-- the card's `isotropic_orbits: 2` and `isotropic_classes: 528`.

The two come from one computation, which is what makes the pair cheap enough to
be worth running: the orbit decomposition costs 13.65 s and every isotropic
orbit is decided by one `q` on one of its classes, so the class count is the sum
of the isotropic orbits' sizes rather than an enumeration of the form.

## Why a script and not a gate test

The same comparison written as a pytest test measured **33.90 s** against the
20 s call ceiling on this VM at load 20, and the script form measures **12.6 s**
at load 13.  The difference is pytest's own overhead on a loaded host, and the
ceiling is per test call, so the comparison lives in the acceptance tier beside
the row drivers: it reports, prints both numbers, and exits 0 when they agree and
1 when one does not.

## Item 6, complete

| card field | value | read by |
| --- | --- | --- |
| `rank` | 11 | `tests/lattices/test_discriminant_form_of_the_coble_lattice.sage:102` |
| `signature` | `[2, 9]` | same `:103-104` |
| `determinant` | -2048 | same `:106-107` |
| `orthogonal_group_order` | 46998591897600 | same `:161`, `:220` |
| `isotropic_classes` | 528 | `tests/coble_card_isotropic_orbits.py` |
| `isotropic_orbits` | 2 | same |

All six are compared by tag and all six agree.
