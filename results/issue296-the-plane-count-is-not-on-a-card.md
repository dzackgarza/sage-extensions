# The T_Co plane row has no card row, so no plane count is a certificate

The acceptance asks that exact computed results belong on their lattice cards
before downstream use as certificates.  On `T_Co` that splits in two.

## What the card certifies, and what the library reproduces

Card `6JRR` (`dzackgarza/lattice-database`, `lattices/6JRR.md`) is `T_Co`
itself: rank 11, signature `(2, 9)`, determinant `-2048`.  Its
`integral.discriminant_form` block carries three numbers, minted and certified
by `latticedb certify` from the card's own Gram tensor — the card states that no
invariant on it is transcribed from a source — under the stamp
`0be391409303d25f25d126795ee881040661b4883ad7473272b34b60b8c414da`:

| row | card | library, measured |
| --- | --- | --- |
| `orthogonal_group_order` | 46998591897600 | 46998591897600 |
| `isotropic_classes` | 528 | 528 |
| `isotropic_orbits` | 2 | 2 (the zero class, and one orbit of 527) |

All three are read by tag in `tests/lattices/`.  The order is asserted in
`test_discriminant_form_of_the_coble_lattice.sage` and in
`test_isotropic_subobjects_of_finite_quadratic_modules.sage`; the class and
orbit counts are asserted in the second, through `isotropic_elements()` and one
line orbit, so that the orbit-stabilizer product on the plane is the card's
order rather than the module's own number.

## What has no card row

The plane result this issue delivers is `|orbit(J)| = 23715` and
`|Stab(J)| = 1981808640` for the image `J` of the plane `<e_1, e_3>` of `T_Co`.
Neither number is on a card, and their product is checked only against the
card's order:

* `6JRR`'s `integral.primitive_orbits` block is **absent by design**.  The card
  says so and gives the reason: the block's constant term is the number of
  `Gamma`-orbits of primitive isotropic lines, "and not a count of vectors
  (`theory/orbits.md`); the preamble operation that returns it for an indefinite
  lattice does not return it yet."
* The digest's `arithmetic_groups` section holds the 87 `gamma-h-N` cards of the
  87 numerical polarizations.  The two `T_Co` arithmetic-group cards the lattice
  card names, `otilde-t-co` and `otilde-plus-t-co`, are not read into it, so no
  `data.line_orbits` / `data.plane_orbits` / `data.flag_orbits` row for `T_Co`
  exists here either (`tests/cards/README.md`).

So there is nothing to pin `23715` to, and no test asserts it.  A count that is
not on a card must not be used as a certificate downstream.

## The row to request

Either of these would carry it, and both are upstream of this repository:

1. `integral.primitive_orbits.{O, Otilde+}` on `lattices/6JRR.md` — the block
   the card already names as absent, whose preamble operation for an indefinite
   lattice is the missing piece in `latticedb`;
2. `data.plane_orbits` (and `data.flag_orbits`) on
   `arithmetic-groups/otilde-plus-t-co.md`, which is the shape the digest
   already reads for `gamma-h-N`.

The database computes and certifies its rows rather than transcribing them, so
the request is for the computation and the stamp, not for these numbers.  What
this library computes, for the database side to cross-check once its operation
returns:

```
J = the image of the plane <e_1, e_3> of T_Co, |J| = 4
  |orbit(J)|  = 23715          (O(q) on isotropic planes of A_{T_Co})
  |Stab(J)|   = 1981808640     (6 generators, engine order)
  product     = 46998591897600 = card 6JRR's orthogonal_group_order
line side, from the same action:
  527 nonzero isotropic classes, one O(q)-orbit of 527 (card: 528 with zero, 2)
  |Stab(line)| = 89181388800, index 527
```

The connection this repository is worked through reads issues and pushes
commits; it cannot create issues.  This request therefore cannot be filed from
here, and the plane half of the cusp count stays uncertified until it is.
