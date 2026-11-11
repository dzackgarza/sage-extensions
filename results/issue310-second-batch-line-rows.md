# #310, second batch: the `029J` line rows by tag, and where the `Otilde(T_En)^+` line row stops

The unit: `T_En.stable_orthogonal_group().intersection(T_En.O_plus()).isotropic_orbit_representatives(1)`
returns, and its count is compared with card `029J`'s `Otilde+` row read by tag.

## 1. The card states the line row, and the digest now keeps it

`029J`'s `integral.primitive_orbits.Otilde+` row carries `constant: 528` beside
`planes: 24242`, and its citation says what `constant` is:

> the space M~_En = Otilde^+(N)\D_N, for N = U + U(2) + E8(-2), has 528 0-dimensional cusps
> (isotropic lines) and 24242 1-dimensional cusps (isotropic planes); under O^+_10(F_2) the 528
> lines fall in two orbits, of lengths 527 and 1, and the 24242 planes in two orbits, of lengths
> 527 and 23715. — D. Dutour Sikirić, K. Hulek, arXiv:2302.01679v2, section 3.6, p. 22

So the expected count is the card's own `constant` row, and it is **528**.  The digest did not
keep that row: `tests/cards/refresh_lattice_database_enriques.py` read only `planes`, and its
filter `if "planes" in row` dropped a group row that states `constant` alone — which is how
`6JRX` states its `Otilde+` line row at all.  The reader, the digest and the export changed:

* the refresh script keeps `constant` as the `lines` field of a group row (and keeps a row that
  states either count);
* the digest is **regenerated**, not edited, at the pinned ref
  `587d56febe5856d54c6bc9fc023fa5a425f76bfb`; the diff is 14 insertions and one provenance line:
  `lines: 2` (`029J` `O`), `lines: 528` (`029J` `Otilde+`), `lines: 5` (`029J` `gamma-en-2`),
  `lines: 1` (`6JRX`/`6JRY` `O+`), and the two `6JRX`/`6JRY` `Otilde+` rows that the old filter
  dropped entirely;
* `card_line_orbit_row(tag, group)` reads it, and `card_line_orbit_lengths(tag, group)` reads the
  per-orbit split out of the same citation, checked against the row total and against the card's
  own count of `O`-orbits (two), exactly as `card_plane_orbit_lengths` does for planes;
* both `card_plane_orbit_row` and `card_line_orbit_row` resolve a tag through one `_orbit_rows`
  helper, so two rows of one card cannot be read from different cards.

`tests/lattices/test_the_enriques_line_rows_by_card.py`: **3 passed in 0.43 s** — the split sums
to the row, the split has the card's own number of orbits, and `6JRX`'s `Otilde+` line row (which
has no plane row) is read while `card_plane_orbit_row` refuses it by name.

The divided-class module and this one together: **8 passed in 63.61 s**, the `T_Co` case at
59.86 s (it was 78.58 s before the loop's bilinear form was evaluated one residue at a time).
`_line_orbit_from_divided_classes` now asks the residue loop for the whole class orbit in one
call, in the order the walk reaches it, instead of one search per class; `T_Co`'s class orbit is
the 527 nonzero isotropic classes (the research record `coble_isotropic_orbits.py`: "orbits
contained in the isotropic classes: 2, of sizes [1, 527]"), so one call instead of 527 is what
keeps that route usable at all.

## 2. The row does not return, and the frame is not the image

`Otilde(T_En)^+ = stable_orthogonal_group().intersection(O_plus())` builds in **5.43 s** with
complete character data (`has_discriminant True`, `determinant_kernel False`,
`spinor_kernel True`), and the ambient `O(T_En)` line classes come back in **45.37 s**.  Then the
row raises, in two places on two routes:

* the current route: `isotropic_orbit_representatives` -> `isotropic_stabilizer_generators` ->
  `_isotropic_stabilizer_generators` -> (port) `marked_lattices.py:116`
  `line_automorphism_generators` -> `isotropic_induction.py:304` ->
  `action.stabilizer().group_generators()` -> the owned resolution's generator ->
  `groups.py:4111 _evaluate_reduced_word` -> `set_categories.py:4296 _retain_admitted_member` ->
  `groups.py:1571 _element_constructor_` -> `groups.py:1594 __contains__`, which raises
  `TypeError: membership of Morphism from Lattice of rank 12 and signature (2, 10) to Lattice of
  rank 12 and signature (2, 10) in Subgroup of Orthogonal group ... is undecided; supply a word
  witness to membership_decision`;
* the route through the exact stabilizer image, which is the one this batch is about: every
  character-quotient computation starts at `_im_rho_engine_and_section` -> `_ambient_generators`,
  i.e. at `O(T_En)`'s **own** selected generating family, and
  `has_selected_finite_group_generating_set()` -> `selected_group_resolution` ->
  `_core_automorphism_generators` -> `_computed_group_generators` -> (port)
  `orthogonal_group_generators` -> `recursive.py:852 _generation_step` -> `eichler.py:901
  approximate_generators` raises the *same* `TypeError`.  So on `T_En` the row cannot reach
  `rho(O(T_En))`, `_sign_descent_rank`, `_joint_discriminant_image_gap` or the double cosets at
  all.

**The missing step** is a generating family of `O(T_En)` — or a route that does not need one.  The
second is prepared and *not* landed: `_splitting_isometries_in_im_rho_from_image` already accepts
the right-hand subgroup of the double cosets as a `right` argument, so
`stabilizer_discriminant_image()` (which exists without any family of `G_x`) can be passed there,
with the sign datum supplied by a norm `+2` root orthogonal to the line.  On `T_En` that witness
does not exist — the lattice has no norm `+2` vector (its summands are `U`, `U(2)` and
`E8(-2)`) — so the sign component would have to come from `_sign_descent_rank`, which is exactly
what needs the missing family.  Nothing was landed for it: no row exercises it, and unexercised
machinery is not a deliverable.

## 3. A regression on main that this batch did not introduce, and that this batch ran into

At **3795d5206a** (this session's #310 commit, clean worktree, no change of this batch), the
`U(2)^n` line rows that returned 2 / 9 / 9 / 35 at `8d44136` now raise the same `TypeError:
membership ... undecided`:

| row | `8d44136` | `3795d5206a` |
| --- | --- | --- |
| `U(2)+<-6>` | 2 | 2 |
| `U(2)U(2)` | 9 | `TypeError` in 9.4 s |
| `U(2)U(2)+<-6>` | 9 | `TypeError` in 12.5 s |
| `U(2)U(2)U(2)` | 35 | `TypeError` in 54.8 s |

The commits between the two are the #287 series (`158c170 fix: Admit a free cover's word values
into its generated subgroup (#287)`), which is where the word-value admission now asks a
membership question that an indefinite lattice's subgroup cannot decide.  Filed here as a defect
for its owner; this batch does not touch those lines.
