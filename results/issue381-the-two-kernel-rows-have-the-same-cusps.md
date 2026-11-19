# `Otilde+`'s plane cusps are 189 720: the sign sheet is redundant at `T_Co`

`Otilde = ker rho` and `Otilde+ = ker(rho, sn_RR)` are the two rows #381 owes.
`Otilde`'s row returned (`issue381-the-plane-rows-per-plane-cost.md` §10);
`Otilde+`'s was killed twice by the host.  This note decides its **cusp counts**
without the run, and leaves its **edges** to the run.

## The rule the count turns on

The walk yields, per double coset, one lift, and a second one -- the *sign
sheet* -- exactly when

    j >= 1 and len(sign_labels) == 1 and not stab_sign_flip and flip_element is not None

(`_iter_splitting_isometries_in_im_rho_from_image`; the `flipped` of the point
branch at `orthogonal_quotients.py:2368` and of the coset branch at `:2583`).
Everything but `stab_sign_flip` is measured here; `stab_sign_flip` is
`_stabilizer_sign_flips(family)`, which asks whether the plane's own ambient
parabolic family contains an `s` with `rho(s) = 1` and real spinor norm `-1`.
Such an `s` lies in `ker(rho, sn)` by definition, so a true answer is exactly
"the stabilizer already presents the sign coset", and the sheet adds nothing.

`_image_labels` is `["discriminant"]` for `Otilde` and `["discriminant",
"spinor"]` for `Otilde+` (`:397`--`:406`, from `determinant_kernel` and
`spinor_kernel`), so `Otilde` has an empty sign list, `j = 0`, and no sheet at
all -- its 189 721 registered planes are the coset space's 189 720 plus the
source.  **Nothing in `Otilde`'s count transfers to `Otilde+`.**

## What the probe measured, at the plane

`probe-otildeplus-sign.py`, `Otilde+` at `T_Co` (`otildeplus-sign.log`):

| datum | value |
| --- | --- |
| `quotient.index()`, the order of `(rho, sn_RR)(O(T_Co))` | `93 997 183 795 200` = 2 × `46 998 591 897 600` |
| `_sign_descent_rank()` | `j = 1`, labels `['spinor']` |
| ambient plane orbits of `O(T_Co)` | **1**, in 26.68 s |
| `is_parabolic_complete()` | **True**, 3.86 s |
| `parabolic_stabilizer_generators()` | **113** generators |
| `_stabilizer_sign_flips(family)` | **True**, 5.44 s |
| `_kernel_sign_flip('spinor')` | an integral isometry, 0.06 s |
| `rho(witness)` trivial / real spinor norm `-1` | **True / True** |
| `determinant` of the witness | `-1` (odd rank, a reflection) |

The joint image being exactly twice `im rho` is why `Otilde+` is index two in
`Otilde` and why `j = 1`; the 113 generators are the same family whose images
generate the stabilizer image of order `247 726 080` that the cost probe printed.

## The lemma

The predicate is true at the plane.  `T_Co` has **one** `O(T_Co)`-orbit of
planes, and `_stabilizer_sign_flips` is a function of the plane and the
lattice's characters, which are conjugation-invariant, so the value is the same
at every plane of the row.  Hence no plane of `Otilde+`'s split yields a second
lift, and the split's planes are the double cosets

$$A \backslash F / F_P, \qquad A = \chi(\Gamma) = 1,\ F = \chi(O(T_{Co})),\ F_P = \chi(\mathrm{Stab}(P))$$

of D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22
-- `189 720` of them, the index the cost probe read as
`46 998 591 897 600 / 247 726 080`.

So **`Otilde+` has 189 720 plane cusps**.  Its line row uses a different
predicate and reaches the same kind of answer: `isotropic_line_stabilizer_image`
answers `bool(sign_labels)` as its `stab_sign_flip` (`:1818`), because the
stabilizer's own exhibited patterns have just been certified to span the sign
space of `ker rho` (`:1780`--`:1782`), so no sign coset is left to lift there
either.  Its lifts are one per point of `im rho . {c, -c}`, and its count is the
orbit's **527**.

That is the `(·, 527, 189720)` half of the archive's
`(569160, 527, 189720)`.  The edge count is the run's to decide and is not
claimed here.

## What this does and does not settle

It settles the row's **length**: 189 720 planes at the measured 7.35 ms a plane
(`issue381-the-row-returns-in-its-own-cap.md`) is 1394 s of split, so `Otilde+`
costs what `Otilde` did -- about 35 minutes inside the driver's `10 800 s` cap --
and its two kills were the host's, not its length.

It does not settle `Otilde+`'s relation.  Its edges are incidences computed with
`Otilde+`'s own elements, and a smaller subgroup can only refine them; the
archive says `569 160` and the row is what would say so.

No object is introduced: `rho` and `sn_RR` are the lattice's own characters,
the double cosets and the index are Lemma 3.6's, `stab_sign_flip` and
`_sign_descent_rank` are the library's, and every count above is a datum the
library printed.
