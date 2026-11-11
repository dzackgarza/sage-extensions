# #310: where the `Otilde(T_Co)` line row's time goes, and the divided-class construction on `T_Co`

The row is `T_Co.stable_orthogonal_group().isotropic_orbit_representatives(1)`, the red
`87388e5393` (`tests/lattices/test_the_stable_line_orbit_row_returns_on_the_coble_lattice.sage`).
`T_Co = <2> + (U + E8(-1))(2)`: Dolgachev--Kondo, Izv. Math. 77:3 (2013), (3.6), p. 513; rank 11,
signature (2, 9), `|A_L| = 2048`, `|rho(O(T_Co))| = 46998591897600`.

Every number is a printed `time.time()` delta.  The logs are in `.tmp/qc-evidence/` as
`issue310-p310b-probe{1,2,3,4,5,6,7}.log`, `issue310-p310b-test-divided3.log`,
`issue310-p310base-eichler.log` and `issue310-p310b-eichler-after.log`.  The VM was shared with other sessions' heavy jobs during these runs (four
concurrent probe processes at the peak), so each figure is an upper bound; the repeated
measurement of the same step is given where it was repeated.

## 1. Which images the row computes, and how often

| step | measured | what it is |
| --- | --- | --- |
| `O(T_Co)` selected generating family | `115.32 s` / `94.99 s` / `82.94 s` (three processes) | `group_generators()`, **340** generators; `0.01 s` on every later call |
| `rho(O(T_Co))` | `26.66 s` first, `0.02 s` cached | `Aut().discriminant_image()`, order `46998591897600` |
| `rho(Stab(<e_1>))` | `25.91 s` first, `4.48 s` on a **repeated** call | `stabilizer_discriminant_image()`, order `89181388800` |
| the ambient generator sweep | `26 s` first, `0.04 s` later | `_im_rho_engine_and_section` / `_sign_descent_rank` / `_image_order` / the double-coset route each swept `rho` over the 340 generators |
| `isotropic_stabilizer_generators(<e_1>)` | `12.03 s` | 30 generators |
| `splitting_isometries(30 generators)` | `97.16 s` | 527 double cosets; the stack at 100 s was `self.image(lift)` per coset |
| the ambient `O(T_Co)` line enumeration | **not returned at 490 s** (killed) | `G.isotropic_orbit_representatives(1)` |

The index the row needs is `[rho(O(T_Co)) : rho(Stab)] = 46998591897600 // 89181388800 = 527`,
which is card `029J`'s cited line-stabilizer index `527 = 17*31` (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, section 3.6, p. 22, read from the card's own citation), and it is also the
number of `Otilde(T_Co)`-orbits of primitive isotropic lines: `Gamma = ker rho` is normal, so
`Gamma \ G / Stab` is the set of cosets `rho(G)/rho(Stab)`.

**The images are not where the row's time went.**  They cost about 50 s once, and the row did not
return because of two other things, in this order:

1. *The ambient line enumeration.*  `_subgroup_isotropic_orbit_representatives` first asks the
   ambient group for its line orbits, and on `T_Co` that is the port's marking-class route
   (`_isotropic_orbit_representatives`, `isotropic_orbits.py:1495`): `primitive_marking_classes` ->
   `isotropic_vector_classes` -> `pointed_isometry` -> `integral_members` ->
   `_integral_lift_locus` -> `integral_parameter_classes` (`isotropic_lifts.py:412`), which builds
   one lift per coset of `P/mP` modulo the transvection kernel and asks each for its integral
   restriction.  The faulthandler dump at 300 s is inside that, at the deepest frame
   `_linear_combination_of_generator_images` (`module_morphisms.py:1091`): applying a module
   morphism costs about 80 ms on this 11-generator module.  The row never reaches a lift of its own.
2. *The lift loop.*  Reached in an earlier measurement (`splitting_isometries`, `97.16 s`), the
   inner cost is `self.image(lift)` per double-coset representative
   (`orthogonal_quotients.py:1553`), one `discriminant_morphism` construction per lift: 527 of them
   at about 80 ms is 42 s of the 97 s.

## 2. What changed

* `orthogonal_quotients.ambient_discriminant_images()`: `rho` on the selected generating family,
  `@cached_method`, once per lattice.  `_im_rho_engine_and_section`, `_sign_descent_rank` and the
  double-coset route read it instead of sweeping the family themselves, and
  `_joint_discriminant_image_gap` uses it as its `K_0` image when no sign factor remains (there
  `K_0` *is* the ambient group).
* `_im_rho_engine_and_section`, `_sign_descent_rank`, `predicate_subgroups.discriminant_image`
  and `rational_integral_stabilizers.stabilizer_discriminant_image` are cached: the two images are
  data of the lattice and of the subobject, not of a row or a class.  The repeated-call measurement
  above (`4.48 s` for a value already computed) is what this removes.
* `lattices.divided_class_residue(divided_class, divisibility)`: the residue `v mod dL` a divided
  class determines, through `discriminant_module().dual_lattice_lift` and the existing owner of
  "dual coordinates to lattice coordinates" (`_half_vector_coordinates`), with the division by `d`
  in `L` required to be integral.
* `isotropic_lines_by_divided_class(divisibility, *, classes=None)`: with `classes` given the loop
  runs the residues those classes determine -- one residue, then its `|K/dK|` translations -- and
  without it the whole `L/dL`; the bilinear form of the complement is evaluated one `w` residue at
  a time (`cross_row`) instead of as a full `|K/dK|`-square table, which was the loop's dominant
  cost; and the budget counts the loop that will run.  It **double-counted** the hyperbolic pair's
  residue (`residues * translations * d * d`, with the pair's residue already inside `residues`),
  which is exactly why it refused `T_Co`: it said 4194304 for a loop of 1048576.
* `primitive_isotropic_vector_of_divided_class` asks for its own class, and its refusal names the
  class, the divisor, and the translations that were tried.

## 3. The construction on `T_Co`

`tests/lattices/test_the_divided_class_construction.sage`: **5 passed in 82.39 s**, the `T_Co`
case at `78.58 s` (one named class, checked against the marked line's own coordinates modulo two).
The whole map on `T_Co` (2048 residues) was still running at 400 s and was stopped: it is
permitted now, not fast, and no caller in the row needs it.

## 4. The red

`tests/lattices/test_the_stable_line_orbit_row_returns_on_the_coble_lattice.sage` (clone of
`87388e5393`) still does not return.  It was run
(`--no-time-gates`, harness cap 1500 s) and stopped without a result: its own preamble is the two
images (`~141 s` on `T_Co`), and then the row's first step is the ambient line enumeration of
section 1, which had not returned at 490 s in the probe run and is the same call here.  No
assertion of the file is decided: neither the 527 nor the representative clauses.

What would have to change for it to pass is *not* an image computation: it is the cost of the
port's ambient marking-class enumeration on `T_Co`, whose inner frame is a module-morphism
application (`_linear_combination_of_generator_images`, `module_morphisms.py:1091`) at about 80 ms
on an 11-generator module, inside `integral_parameter_classes` (`isotropic_lifts.py:412`).  That is
its own owner and its own unit; #319's measurement is the same stop.

## 5. `Otilde(T_Co)^+`

`Otilde(T_Co)^+ = ker rho cap ker(real spinor norm)` is
`stable_orthogonal_group().intersection(O_plus())`, which builds in **3.0 s** with its character
data.  Its line row stops at the same first step as the red: at 300 s the stack is
`_subgroup_isotropic_orbit_representatives` -> the port's `primitive_marking_classes` ->
`isotropic_vector_classes` -> `pointed_isometry` -> `integral_members` ->
`_integral_lift_locus` -> `integral_parameter_classes` (`isotropic_lifts.py:583`) ->
`lifts_integrally` -> `eichler_transvection` (`lattices.py:7590`) ->
`_eichler_transvection_column_matrix` (`lattices.py:7520-7522`), which is one transvection per
residue class of `P/mP` modulo the transvection kernel -- 512 of them on `T_Co` at `m = 2` -- each
built through the owned ring's `__add__`.  No assertion of the row is decided.

## 6. The `029J` rows by tag and the `U(2)^n` rows

| row | result | compared with |
| --- | --- | --- |
| `T_En.Aut().isotropic_orbit_representatives(1)` | **2** in 48.4 s | card `029J`'s citation: the two `O(T_En)`-orbits of primitive isotropic lines, `Z e_1` and `Z e_3` (Sterk, Prop. 4.5, p. 28) |
| `T_En.Aut().isotropic_orbit_representatives(2)` | **2** in 25.9 s | `card_plane_orbit_row("029J", "O") = 2`, read from the digest |
| `U(2) + <-6>` `.stable_orthogonal_group().isotropic_orbit_representatives(1)` | **2** in 4.0 s | 2 (`.tmp/p310-probe9.log`) |
| `U(2)U(2)` | **9** in 12.2 s | 9 |
| `U(2)U(2) + <-6>` | **9** in 36.2 s | 9 |
| `U(2)U(2)U(2)` | **35** in 81.5 s | 35 |

`U(2)` alone is refused by name at both commits: on `8d44136` the row raises
`ValueError: no primitive isotropic vector ... has divisor 2 and divided class [0]` in 2.5 s, and
with this change the same refusal names the class `-[1]` it tried.  Its rank is two, so `K` is
trivial and that class has no lift at divisor two.

## 7. Regression check outside this unit

`tests/lattices/test_eichler_orbits.sage` reports `2 failed, 4 passed in 57.83 s` with this change
and `2 failed, 4 passed in 51.19 s` on `8d44136`, the same two ids in both
(`test_the_criterion_reads_its_hypothesis_off_the_decomposition`: `LK3.is_decomposable()` is
`True`; `test_raw_gram_factor_does_not_count_as_a_represented_u_summand`:
`hyperbolic_plane_summand_count()` is `2` on `[[2,1],[1,0]] + U`).  They are pre-existing and
neither function is in this diff.

`tests/lattices/test_the_divided_class_construction.sage` `5 passed in 82.39 s` with the `T_Co`
case at 78.58 s.  The module is run with `--no-time-gates`: the repo's call ceiling is 20 s and
this row is 78.58 s.

## 8. What this does not do

* The red is not made to pass.  Its first step, the ambient `O(T_Co)` line enumeration, is the
  cost, and its owner is `isotropic_lifts.integral_parameter_classes` /
  `Lattices._eichler_transvection_column_matrix` and the module-morphism application underneath
  them; that is a unit of its own.
* The lift loop's `self.image(lift)` per double coset (about 80 ms x 527) is measured but not
  changed.  With the ambient enumeration solved it becomes the next cost.
* No whole-map loop on `T_Co` is run here: it is permitted now (the budget allows 1048576) and it
  was still running at 400 s when stopped.
