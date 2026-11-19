# The two kernel rows carry one relation, and `Otilde+`'s is `Otilde`'s

Last round's note decided `Otilde+`'s cusp **counts** from the sign predicate.
This one decides something stronger and cheaper to check: the two kernel rows
have the same **cusps and the same incidence relation**, so `Otilde+`'s row is
`Otilde`'s returned row -- `569 160` edges over `527` line and `189 720` plane
cusps -- and a run of it confirms rather than decides.

## What the two rows differ by, measured at `T_Co`

`probe-otilde-labels.py`, both subgroups of the driver, one process
(`otilde-labels.log`):

| | `Otilde` | `Otilde+` |
| --- | --- | --- |
| `quotient.index()` | `46 998 591 897 600` | `93 997 183 795 200` |
| `_image_labels` | `['discriminant']` | `['discriminant', 'spinor']` |
| `determinant_kernel` / `spinor_kernel` | `False` / `False` | `False` / **`True`** |
| `_sign_descent_rank()` | `j = 0`, `[]` | `j = 1`, `['spinor']` |

With last round's reading `_stabilizer_sign_flips(family) = True` at the plane
(`otildeplus-sign.log`), **neither row has a sign sheet**: `Otilde` has no sign
character to lift, and `Otilde+`'s stabilizer presents the coset the character
leaves.  In the walk's own terms, `flipped is None` on both rows.

## Why that makes the two walks one walk

`_iter_splitting_isometries_in_im_rho_from_image` builds, in order:

* `right = rho(Stab_{O(L)}(P))`, from the plane's parabolic family -- the same
  family for both rows, a function of the plane;
* `left = _joint_discriminant_image_gap()`, the subgroup's *image*, which is
  trivial for either kernel row, so `representative_points = queue`, the coset
  space `im rho / rho(Stab(P))` in walk order;
* the lifts, spelled from `ambient` -- the lattice's selected generating family
  -- and `rho_images`, with the same `small_indices`.

None of those mentions the subgroup.  So both rows yield the same planes in the
same order, and each yield is one orbit of its own subgroup.  Two partitions of
one set into the same number of classes, one refining the other because
`Otilde+ <= Otilde`, are equal: **the cusp sets of the two rows are the same
partition of the same planes.**

The line row is the same story with its own predicate: `splitting_isometries_from_line_class`
is handed `stab_sign_flip = bool(sign_labels)`, `False` for `Otilde` and `True`
for `Otilde+` (`orthogonal_quotients.py:1818`), and with `j = 0` on the first
row and a presented coset on the second neither yields a second lift.

An edge joins a line cusp to a plane cusp when *some line of the line orbit lies
in the plane orbit*, and that is a statement about the two orbit **sets**.  Those
are the same sets for the two rows, so their relations are the same relation.
The counts follow: `569 160` edges over `527` and `189 720`.

## What is measured, and where

`probe-cusp-lists.py` (`cusp-lists.log`) compares the two rows' cusp lists --
order and coordinates, not counts -- on the lattices the gate can afford:

| lattice | rank 1 | rank 2 |
| --- | --- | --- |
| `U + U(2) + <-2>` | 3 cusps each, lists **equal** | 2 cusps each, lists **equal** |
| `6JRS` | 1 cusp each, lists **equal** | 1 cusp each, lists **equal** |

and the driver's own runs on `U + U(2) + <-2>` give both rows `4` edges over `3`
line and `2` plane cusps with the *same* ordered endpoint digest
(`04c17f79…587dc2`, `.tmp/issue381-t13/small-rows.log`), and on `6JRS` and
`U + U(2) + <-4>` the same counts for both rows
(`issue381-kernel-incidence-rows.md`).

## What this settles and what it does not

It settles `Otilde+`'s acceptance values by transfer: the row is
`(569 160, 527, 189 720)`, because its cusps are `Otilde`'s cusps and its
incidence is a relation between those cusps.

It does **not** run `Otilde+`.  The `T_Co` step above is an argument from the
code's structure with its two inputs measured, not a row's output, and a row is
what would confirm it end to end.  The host is why: `MemAvailable` was
`4 085 MiB` with `oom_kill` up five since the last check, against the record's
own gate of about `8 GiB` for a `3.6 GiB` row, so the run is a scheduling
question and not an open one.

No object is introduced: `rho` and the real spinor norm are the lattice's
characters, the coset space and the index are Dutour Sikirić--Hulek, Lemma 3.6,
printed p. 22, and the predicates and counts are the library's own.
