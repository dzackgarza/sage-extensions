# The orbit decomposition of a finite formed module's classes, and card `6JRR`

Card `6JRR` states `isotropic_orbits: 2` for `T_Co` and no test could read it:
the finite orthogonal group had no orbit decomposition of its classes.  It has
one now, and the field's value is measured.

## The capability

`TorsionFormOrthogonalGroup` gains three methods at that owner:

* `class_orbits()` -- the orbits on the classes of the form, as tuples of
  positions in the order `form.elements()` gives, largest orbit first;
* `class_orbit_sizes()` -- their sizes;
* `isotropic_class_orbits()` -- those all of whose classes are isotropic.

The decomposition is GAP's `Orbits` on the group's own action (Holt, Eick and
O'Brien, *Handbook of Computational Group Theory*, 2005, §4.1, p. 79), the same
engine the file's `stabilizer_of_classes` already uses.  Classes cross into that
action by `_engine_abelian_element`, and the positions are read off a table of
those same engine elements, so no engine element is converted back.  Isotropy is
one `q` per orbit -- `O(q)` preserves `q`, so an orbit is isotropic exactly when
one class of it is -- and not an enumeration of the form.

## Measured

Probe `.scratch/w286-probes/probe-orbits.py` (log `.scratch/w286-probes/probe-orbits.log`):

| lattice | `|A|` | orbits | sizes | isotropic orbits |
| --- | ---: | ---: | --- | ---: |
| `U + U(2) + <-4>` | 16 | 6 | `6, 3, 3, 2, 1, 1` | **2** |
| `T_Co` | 2048 | 6 | `527, 527, 496, 496, 1, 1` | **2** |

`T_Co`'s decomposition costs **13.65 s** and its isotropic orbits are the two of
size 1 and one of the two of size 527 -- which is the card's `isotropic_orbits:
2`, and it agrees with the isotropic class count of 528 computed by `q`
(`results/issue286-the-two-unread-card-fields.md`): `1 + 1 + 527` is not the
count, `1 + 527` is, and the other 527 is the `q = 1/2` orbit that the earlier
session recorded as an arithmetic coincidence with the isotropic 527.

So the field is now **computable**: `isotropic_class_orbits()` on `T_Co` returns
two orbits.  A gated test still cannot compare it -- 13.65 s against a 20 s
ceiling, counting setup -- but the blocker is no longer a missing capability;
it is the same one-gate-over cost the class count has.

## The test

`tests/lattices/test_the_orthogonal_group_orbits_on_its_classes.sage`, on
`U + U(2) + <-4>` where the decomposition can be counted by hand: the orbits are
`6, 3, 3, 2, 1, 1`, they partition the sixteen classes, and two of them are
isotropic, with their classes exactly the ones `q` vanishes on.  Measured 1.98 s
and 0.08 s.
