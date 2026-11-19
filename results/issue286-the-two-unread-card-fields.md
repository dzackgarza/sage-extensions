# The two unread fields of card `6JRR`: one is compared, one has no route

Card `6JRR` (`tests/cards/lattice-database-enriques.json`,
`discriminant_forms.6JRR`, from `dzackgarza/lattice-database` at ref
`23c0f9ca`) states `isotropic_classes: 528` and `isotropic_orbits: 2`.  No test
reads either.  This note measures what comparing them costs, so that "owed" is a
number and not a guess.

## `isotropic_classes`: computed, agrees, and it is one gate over

Probe `.scratch/w286-card2/.tmp/probe-carded.py` (log
`.scratch/w286-probes/probe-carded.log`, one process, load 1.5-2.7):

```
2048 classes
  q on every class                                    20.15 s
  isotropic classes: 528
```

`form.q` on the 2048 classes of `A_{T_Co}` costs **20.15 s** and returns **528**,
which is the card's field exactly.  The call's ceiling is 20 s, and the run
around the enumeration (lattice, form, class set) adds about six seconds, so a
test that compares this field is over the ceiling on this host and would make CI
red.  It is therefore owed to a row -- the same kind of row as the `T_Co` orbit
rows -- and the number the field must be compared against is now measured
rather than assumed.

The earlier estimate in `results/issue286-acceptance.md` said "about 80 ms a
class, 65.43 s"; the enumeration as written here is **9.8 ms a class**, 20.15 s,
so that estimate was three times too pessimistic.  The conclusion is unchanged:
one gate over.

## `isotropic_orbits`: no library route

The second field asks for the number of `O(q)`-orbits on the isotropic classes
of `A_{T_Co}` -- `{0}` and the 527 nonzero ones, so 2.  The finite orthogonal
group offers no orbit decomposition of the classes: `orbits_on_classes`,
`orbits`, `orbit_decomposition` and `class_orbits` are all absent from it
(`.scratch/w286-probes/probe-carded.log`), and the class-set orbit machinery the
library does have (`isotropic_class_orbit`, `stabilizer_of_classes`) answers
orbits of a *set* of classes under a subgroup, not the orbit decomposition of
the whole class set.

So this field is owed to a new capability, not to a row: either an orbit
decomposition of the classes of a finite formed module, or the count read off
the stabilizer chain (`|O(q)| / |Stab|` over a transversal), which is the same
computation as `plane_class_index` generalized from a point to the whole set.

## What this changes

* `results/issue286-acceptance.md`'s item 6 stands, with its cost figure
  corrected and its second field's blocker named exactly.
* No test is added this round: the one field would be over the ceiling and the
  other has nothing to call.
