# #310: the line-orbit split from the exact finite image

## The method and its citation

Let `G` act on the ambient line orbit `X = G v`, `H = Stab_G(v)`, and `Gamma = ker rho` for a
finite character `rho` of `G`.  Then `Gamma` is normal in `G`, `G/Gamma` acts on `X` through
`rho`, and the double cosets `Gamma \ G / H` correspond bijectively to the cosets
`rho(G)/rho(H)` — the orbit–stabilizer correspondence applied to the action of the quotient
`G/ker rho` (the correspondence `Gamma g H |-> rho(g) rho(H)`; it is well defined and
bijective because `Gamma = ker rho`).  So the number of `Gamma`-orbits in `X` is the index
`[rho(G) : rho(H)]`, and one representative per coset is `g v` for any isometry `g` with
`rho(g)` in that coset.

For `Otilde(L) = ker(O(L) -> O(A_L))` this is exactly the stable orthogonal group's line row;
`Otilde^+(L)` adds the real spinor norm character, the sign datum of #310's body, and the same
statement applies to the joint character `(rho, sn)`.

## The index, computed from the images themselves

Correction taken: the call computes `[rho(O(T_Co)) : rho(Stab(e_1))]` from `rho(O(T_Co))`
itself, not from `|O(q)|`.  On `T_Co` the library computes both, and it also *decides*
surjectivity, so `|O(q)|` is used only after that decision:

| quantity | value | cost | log |
| --- | ---: | ---: | --- |
| `|O(A_{T_Co})|` | 46998591897600 | 7.4 s | `.tmp/p310-probe8.log` |
| `|rho(O(T_Co))|` = `lattice.Aut().discriminant_image()` | 46998591897600 | 153.7 s | `.tmp/p310-probe8.log` |
| `discriminant_representation_is_surjective()` | **True** (computed, not cited) | 0.2 s | `.tmp/p310-probe8.log` |
| `|rho(Stab(<e_1>))|` | 89181388800 | 31.4 s | `.tmp/p310-probe8.log` |
| `|rho(Otilde(T_Co))|` | 1 | 0.1 s | `.tmp/p310-probe8.log` |
| index `[rho(O) : rho(Stab)]` | `46998591897600 // 89181388800` | — | — |

`527` is not asserted anywhere and is not a card value (lattice-database#7).

## The three rows

| row | result |
| --- | --- |
| `O(T_Co)` | **returns**, 1 orbit, representative `-e_1`, `[v/2] = -[2]`, `div = 2` (424.5 s alone; 676.7 s and 1673 s under other jobs) |
| `Otilde(T_Co)` | **stops**: `_subgroup_isotropic_orbit_representatives` → `splitting_isometries` → `_splitting_isometries_in_im_rho` → `_splitting_isometries_in_im_rho_from_image` → `image` → `discriminant_morphism` → `_normalized_form_automorphism`; still in that frame at 420 s, whole row still running at a 900 s cap (`.tmp/p310-probe9.log`, `.tmp/p310-red-tco.log`) |
| `Otilde^+(T_Co)` | **stops**: the same family demand one level up, `_image_section` → `_ambient_generators` → the port's `orthogonal_group_generators`, from 488 s to a 2100 s cap (`.tmp/p322-otilde-step.log`) |

No smaller specimen without two unimodular hyperbolic planes reproduces the stop, measured
without the profiler: `U(2) + <-6>` 10 s, `U(2)U(2)` 9 orbits in 11 s, `U(2)U(2) + <-6>`
9 orbits in 26 s, `U(2)U(2)U(2)` 35 orbits in 53 s (`.tmp/p310-probe9.log`).  `T_Co` is
therefore the specimen, as the batch allows.  The 029J rows were not re-run: this unit
changes no orbit-path file.

## The switch is not landed, and the reason is measured

Counting is possible; **realizing the representatives is not**, with the constructions the
code has:

* the only source of an explicit isometry with a prescribed discriminant image is
  `subgroup_generator_lifts()` (one live lift per generator of `rho(self)`), and on `T_Co` it
  does not return — stopped at 240 s inside `libgap.IsomorphismPermGroup` in
  `orthogonal_quotients._GapWordSection.permutation_group` (`.tmp/p310-probe8.log`).  Every
  lift it would produce is a word in the ambient generator family, which is the family whose
  computation is the stop;
* the other end is not available either: turning a divided discriminant class `c'` in the
  `rho(G)`-orbit of `c` back into an isotropic line `v'` with that class is not a construction
  the library has, so "the classes index" cannot be upgraded to "the lines" without it.

So `isotropic_orbit_representatives` can be given the *count* `[rho(G) : rho(Stab)]` but not a
family of lines, and its return type is a finite set of lines; refusing inside it would replace
the tractable rows that do return today (`U(2)U(2)` and friends, through the fallback) with a
refusal, which is a regression.  That API decision is the person's, not a guess to make here.
The two constructions that would unblock it, in order: an owner that returns live isometries
whose discriminant images generate `rho(O(L))` with a word section that does not need the full
ambient family; and a construction of a primitive isotropic vector with a prescribed divided
class.

## What is landed

* `tests/lattices/test_the_stable_line_orbit_row_returns_on_the_coble_lattice.sage` — the red
  pin of the `Otilde(T_Co)` row (commit `03435d8`, run to a 900 s cap with no result).
* `tests/lattices/test_the_stable_line_orbit_row_comes_from_the_exact_finite_image.sage` — the
  tractable regression: on `U(2) + <-6>` the row returns and its orbit count equals
  `[rho(O(L)) : rho(Stab(line))]` computed from the two exact images, with the stabilizer's
  image asserted inside the group's image.  Green: **1 passed in 10.74 s**
  (`.tmp/p310-red-row.log`).
