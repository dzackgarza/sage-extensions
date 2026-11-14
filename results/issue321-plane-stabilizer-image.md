# #321 — the plane-orbit call establishes ρ(G_x), or refuses the lattice

## What changed

`<subgroup>.isotropic_plane_orbits(representatives, stabilizer_generators=None)` no
longer returns a count whose identification it has not established. Before the
count, each representative `x` must satisfy

$$\rho(G_x) = \mathrm{Stab}_Q(J_x), \qquad G_x = \mathrm{Stab}_{O(L)}(x),\quad
J_x = \text{the divided class set of } x,\quad Q = \rho(O(L)),$$

where the count of `Γ`-orbits on the finite set `Q·J_x` is the count of `Γ`-orbits of
planes (Dutour Sikirić–Hulek, arXiv:2302.01679v2, Lemma 3.6, p. 22). The inclusion
`ρ(G_x) ⊆ Stab_Q(J_x)` is free — `J_x` is built from `x` by lattice operations and
`ker ρ` acts trivially — hence `|Q·J_x| = [Q : Stab_Q(J_x)] ≤ [Q : ρ(G_x)]` and the
computed size is only a lower bound until the two agree. Three closures are
accepted; everything else raises, naming the representative and the missing fact:

| closure | when | citation |
| --- | --- | --- |
| `ρ(G_x)` from supplied generators | `stabilizer_generators={position: (g, …)}`; each `g` is checked to stabilize the plane, then `[Q : ⟨ρ(g)⟩]` bounds `[Q : ρ(G_x)]` from above and must equal the class-orbit size | Dutour Sikirić–Hulek, Lemma 3.6, p. 22 |
| trivial image `Q = 1` | vacuous: `ρ(G_x) = 1 = Stab_Q(J_x)`, class set a single point | — (no theorem needed) |
| published indices | both `O(N)`-orbit representatives present on a lattice shown isometric to `N = U ⊕ U(2) ⊕ E_8(−2)`; sizes `{527, 23715}` match the published stabilizer-image indices, so each lower bound meets its own index because the two are distinct | Dutour Sikirić–Hulek, §3.6, p. 22 |

The Enriques lattice is recognised by *exhibiting an isometry* onto `NamedLattices.TEn`,
not by comparing rank, signature, determinant and discriminant group — those do not
determine an indefinite lattice's isometry class.

## Measurements

One process per run, adopted runtime, port bound at `/work` with its `src` ahead:

```
U + U(2)  (Gram [[0,2],[2,0]] for U(2)), plane <e_1, e_3>
  |rho(O(L))| = 2, class-set orbit 2
  no stabilizer data                -> ValueError: "... is not established ... has 2 points ..."
  stabilizer generators (13, 1.76 s) -> 2 plane orbits, index [Q : <rho(h)>] = 2 = orbit size

U + U + <-2>
  |rho(O(L))| = 1 (the character quotient's image has order 2 through the SIGN
  character, so quotient.image_order() is not |rho(O(L))|)
  class-set orbit 1                 -> trivial-image closure, 1 plane orbit

T_En, both Sterk representatives
  sizes 527 and 23715 = the published indices -> closure applies, rows 9 and 24242 unchanged
```

## Tests

`tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage`, 7 tests:

```
tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage    7 passed in 256.15 s, exit 0
  Gamma_En,2 row 158.16 s, Otilde+ row 68.91 s, refusal 8.18 s,
  supplied-stabilizer 2.47 s, trivial-image 5.73 s, split orbit 3.46 s,
  representatives 8.82 s
```

The four row tests are the previously accepted ones and are unchanged in content:
`gamma-en-2` = 9, `Otilde+` = 24242, the representatives' class sets differ, and a
split orbit realizes its plane. New:

* `test_a_lattice_whose_published_indices_do_not_apply_refuses` — `U ⊕ U(2)` without
  stabilizer data raises, naming the plane and the fact that the orbit size only
  bounds the index;
* `test_supplied_stabilizer_generators_establish_the_equality` — the same lattice with
  the stabilizer's own generators returns its two plane orbits;
* `test_a_trivial_discriminant_image_establishes_the_equality_vacuously` — `U ⊕ U ⊕
  ⟨−2⟩` returns its one orbit with no stabilizer input.

Neighbouring modules, same run, gate recipe with the wall-clock gates lifted as the
rows require (`--no-time-gates --timeout=0`):

```
tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage
tests/lattices/test_unpolarized_enriques_strata.sage          (029J `O` rows)
tests/lattices/test_enriques_anti_invariant_cusps.sage
tests/lattices/test_stable_isotropic_plane_orbits.sage
tests/lattices/test_line_stabilizer_image_requires_eichlers_hypothesis.sage
  16 passed in 420.13 s, exit 0
```

`just test-lint` on the module: 1 file, 0 findings. Costs over the 20 s call gate are
the same four rows recorded in #316 (203.37 s, 88.77 s, 43.87 s, 27.30 s), so the
module is still reported under the repository's documented gate-lifting flags.

## What this does not do

* `#286`'s `T_Co` plane rows are *not* produced by this: on a lattice that is neither
  `N` nor of trivial discriminant image, the call now refuses by design. Producing
  them needs `ρ(G_x)` for `T_Co`'s planes — either stabilizer generators or a
  published index for that lattice.
* A supplied stabilizer family that fails to generate all of `ρ(G_x)` is refused by the
  index comparison, but no test pins that path: every cheap specimen with `|Q| > 1`
  whose plane can be stabilized in seconds has an index that already matches
  (`U ⊕ U(2)`), and a specimen with a deliberately too-small family would need a
  lattice with `|Q| > 2` whose stabilizer generators are cheap.
* The `\Gamma_{En,2}`/`\widetilde{O}^+` rows still rest on the published indices and on
  the isometry test that recognises `N`.
