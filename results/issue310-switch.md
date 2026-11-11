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

## The class index on `T_Co`: 1, computed

The decided design (a finite family of lines, the class bijection when the index per class is
1) was measured on `T_Co` before any code moved (`.tmp/p310-probe10.log`):

| quantity | value | cost |
| --- | ---: | ---: |
| `|rho(O(T_Co))|` | 46998591897600 | 98.2 s |
| generators of `rho(O(T_Co))` | 77 | — |
| `|rho(Stab(<e_1>))|` | 89181388800 | 20.8 s |
| `|rho(O(T_Co)) . c|` for `c = [v/div v]` | **527** | 48.5 s (class walk on `A`, 2048 points) |
| index per class `(|rho(G)|/|orbit|) / |rho(Stab)|` | **1** | — |

So the hypothesis of the class bijection holds on `T_Co`, and it holds as a *computation*
(`46998591897600 / 527 / 89181388800 = 1`), not as the citation #315 struck down.

What did not land is the second half, the construction of one primitive isotropic line per
class. The prescribed search is over `div(v) * (c~' + L)`, and the direct box scan of `L` in
the chosen coordinates measures at:

* `|x_i| <= 1`: 177147 vectors in 3.3 s, **46 of the 527 classes** hit.

The lattice is `[2] + U(2) + E8(-2)`, so its isotropic vectors have first coordinate zero and
solve `2 x_1 x_2 = -q_(E8(-2))(x)`; a plain coordinate box therefore fills the class set
slowly, and a box large enough to reach all 527 (`|x_i| <= 2` is 48.8M coordinate vectors)
was not established as sufficient within this unit. The construction needs either that
measurement or the substitution `x_1 = 1, x_2 = -q(x)/2` over a box in the `E8(-2)` part only,
which turns the isotropic condition into a solved coordinate and leaves 8 free coordinates.
Until one of them is measured, the call has no bound it can name, and a bound it cannot name
is exactly what the refusal must not invent.

## The residue construction: the convention, the derived condition, and the coverage

The person's construction is finite by the residue set: `[v/d]` depends only on `v` mod `dL`,
so there are at most `|L/dL| = d^rank` residues to treat, and each class of the orbit is the
class of a residue. On `T_Co`, `d = 2` and `|L/2L| = 2048 = |A_L|`, and the map
residue → class is a bijection, so every class has exactly one residue.

**The convention this library uses is `q(x) = b(x,x)`, not `b(x,x)/2`.** Measured
(`.tmp/p310-probe14.log`): `q(e_0) = 2` with `b(e_0,e_0) = 2`; `q(e_1 + e_2) = 4` with
`b(e_1+e_2, e_1+e_2) = 4`; `q(e_3) = -4` with `b(e_3,e_3) = -4`. A derivation that assumes
`q = b/2` writes `2ab` where the truth is `4ab` and then rejects its own solutions: the first
attempts did exactly that and reported 903 "q nonzero" hits with `q = 8` where `0` was
predicted (`.tmp/p310-probe13.log`).

**The derived condition.** For `L` with a scaled hyperbolic summand `⟨e_1, e_2⟩`,
`b(e_1,e_2) = h`, orthogonal to a complement `K`, and `v = a e_1 + b e_2 + w`,

    q(v) = 2 h a b + q(w)          (with q = b(x,x); for T_Co's U(2), h = 2, so 4ab + q(w))

so for a residue `(a_0, b_0, w_0)` with `w = w_0` fixed, the equation is linear in `b` and has
an integral solution exactly when there is a divisor pair `a·b = -q(w_0)/(2h)` with
`a ≡ a_0 (mod d)` and `b ≡ b_0 (mod d)`; the search over the divisor pairs is finite and
exact. Both coordinates must stay in their residue classes, which the first attempt dropped.

**The coverage.** With that condition, over all 2048 residues on `T_Co`
(`.tmp/p310-probe15.log`):

* 408 of the 527 orbit classes get a primitive isotropic lift with `q = 0`, divisor 2 and the
  residue's class, at 16.9 s for the whole residue set;
* **119 orbit classes are not reached**.

The 119 are not an artefact of a missing class: every class of `ρ(G)·c` is realized by
`g·v` for some `g`, so a lift exists. What the residue's own representative misses is the
freedom `w → w + 2k` inside its residue class: `q(w + 2k) = q(w) + 4 b(w,k) + 4 q(k)`, so
`q` mod 4 is invariant but the magnitude changes, and with it the divisor structure of
`q(w)/(2h)` — `q(w_0) = -4` has only odd divisor pairs and so refuses an even `b_0`, while
`q(w_0 + 2k) = -16` accepts `b = ±2`. That finite variation (`k` over `K/2K`, `2^9` values on
`T_Co`) is what the construction still needs before the row can return, and it is the step
to write next; it is not a coordinate box.

## The construction, landed

`Lattices.ParentMethods.hyperbolic_basis_pair` and `isotropic_lines_by_divided_class(d)` /
`primitive_isotropic_vector_of_divided_class(class, d)` implement the finite residue loop at
the lattice that owns both the class and the vector: residues of `L/dL`, the `k` variation in
`K/dK`, the divisor-pair test `a b = -q(w)/(2h)` with `a ≡ a_0`, `b ≡ b_0 (mod d)`, and every
candidate checked for `q = 0`, primitivity, divisor `d` and its class.  A class the loop does
not reach is refused with the residue count and the translation count named.  On
`U(2) + <-6>` it covers both classes of the exact image and refuses an absent one:
`tests/lattices/test_the_divided_class_construction.sage`, **3 passed in 2.19 s**
(`.tmp/p310-construction.log`).

`_line_orbit_from_divided_classes` wires it into the subgroup line row for
`Otilde(L) = ker rho` when the computed index per class `[Stab_(rho(G))(c) : rho(Stab_G(x))]`
is 1, and returns `None` (leaving the explicit-isometry route) when it is greater -- the case
of several isometries per class, decided by computation, not a fallback.  `Otilde^+` is the
kernel of `rho x (real spinor norm)`, whose index is not this one, so it is excluded there.

Rows after the wiring (`.tmp/p310-probe18.log`): `U(2)+U(2)` 9 lines in 11.7 s,
`U(2)+U(2)+<-6>` 9 lines in 34.8 s, `U(2)^3` 35 lines in 87.7 s -- unchanged from the
representative-family route.

**The `T_Co` stop.** `Otilde(T_Co)` does not return within 600 s: the row reaches the GAP word
section (`f.PreImagesRepresentative`) inside the discriminant-image computation and stays
there (`.tmp/p310-probe18.log`).  The residue loop itself is refused before it runs on `T_Co`
by the named budget guard (11 free coordinates give `2048 * 512 * 4` pairs), so the stop is
in the images the index needs, not in the construction.  The two things that would move it:
computing `rho(O(T_Co))` once per lattice rather than once per row (it is recomputed inside
the call), and the same for `rho(Stab)`; both are `cached_method`s on their owners already, so
the call is paying for them under contention.  `Otilde^+(T_Co)` was not reached.
