# #17: the Γ_h line rows as preimages, by card

**Result: the Γ_h line row is `Γ_h.isotropic_orbit_representatives(1)` with `Γ_h` built as a
preimage of a subgroup `H ≤ O(q_N) × {±1}` under `(ρ, sn)`, and every expected value is now
the card's own row read by tag.  77 of the 87 cards are decided and every one of
them equals its card: 0 disagree and 0 is `UNDECIDED`.  The rows not
decided when this was written are gamma-h-78, gamma-h-79, gamma-h-80, gamma-h-81, gamma-h-82, gamma-h-83, gamma-h-84, gamma-h-85, gamma-h-86, gamma-h-87; that run is still
going and its log is `.scratch/wt17b_rows.log`.**

## Γ_h, and the subgroup H ≤ O(q_N) × {±1} it is the preimage of

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2:

- **p. 7** defines the stabilizer `O(M(1/2), h) = O(M, h) = {g ∈ O(M) : g(h) = h}` and
  records that `π_M: O(M) → O(D(M))` and `π_N: O(N) → O(D(N))` are surjective with
  `(D(M), q_M) ≅ (D(N), −q_N)`, the two discriminant groups being identified;
- **equation (5), p. 7** is the definition, `Γ_h := π_N^{-1}(π_M(O(M, h))) ⊂ O(N)`;
- **p. 7** also states that `Γ_h⁺ = Γ_h ∩ O⁺(N)` has index 2 and that
  `Γ̄_h := π_M(O(M, h)) ⊂ O⁺(F₂¹⁰)`.

In the form this issue states it,

    H := (ρ, sn)(Γ_h) = Γ̄_h × {±1} ≤ O(q_N) × {±1},     Γ_h = (ρ, sn)^{-1}(H),

the sign being all of `{±1}` because `Γ_h ∩ O⁺(N)` has index 2 (p. 7) while
`Õ(N) = ker(ρ, sn) ⊂ Γ_h` is normal of finite index.  So `H` is computed from `h` by taking
the stabilizer `O(M, h)`, its discriminant image, and transporting that image across the
gluing `(D(M), q_M) ≅ (D(N), −q_N)`.

D. Dutour Sikirić and K. Hulek, **Lemma 3.6, p. 22**, splits the orbits inside the finite
quotient under exactly the hypothesis `U ⊂ K` with `U` normal; the paragraph applying it,
**p. 23**, names the groups: "`U = Õ(N)` the kernel of the action of `O(N)` on the
discriminant, `K = Γ_h` and `H = G_x`", together with "the quotient `O(N)/Õ(N) ≅ O⁺(F₂)` is
finite".  (The earlier record `results/issue17-double-coset-row.md` cites that paragraph as
"same page"; it is p. 23.)

**Where the library computes H from h.**
`Involutions.I_En.polarized(h).coinvariant_extension_subgroup()`
(`src/sage_extensions/categories/lattice_centralizers.py`):

- `:1006` — `stabilizer = extension.invariant.O().stabilizer(self.invariant_polarization())`,
  i.e. `O(M, h)` as a predicate subgroup, never a generating set;
- `:1136–1146` — that stabilizer's discriminant image, transported across the full-glue
  anti-isometry by `_coinvariant_discriminant_from_invariant`, and taken as the preimage in
  `O(N)` by `discriminant_preimage`.

The returned subgroup is `(ρ, sn)^{-1}(H)` itself, so the row never asks any subgroup for
`group_generators()`: the ambient `O(N)`-lines, the stabilizer images the certificates of
#351 supply, and the double cosets in the finite group are the whole route.

## The run

One background job, once: `tests/enriques_polarization_rows_by_card.py --degrees none
--rows lines --cap 1200 --budget 10800`, all 87 `gamma-h-N` cards, in the pinned image with
the port at `991b88b0`.  The harness gains `--rows`, so a run can take the line row alone;
the card is read by tag from `tests/cards/lattice-database-enriques.json` (lattice-database
`1e1cadcf` at this head; the run below read `dbc9fc6a`, whose 87 rows are identical), and a row that does not return inside the cap is reported `UNDECIDED`, which is
not a pass.

```
decided 77 cards: 77 pass, 0 fail, 0 undecided
gamma-h-1  PASS  203 s
gamma-h-2  PASS  13 s
gamma-h-3  PASS  12 s
gamma-h-4  PASS  12 s
gamma-h-5  PASS  14 s
gamma-h-6  PASS  12 s
gamma-h-7  PASS  10 s
gamma-h-8  PASS  15 s
gamma-h-9  PASS  12 s
gamma-h-10  PASS  14 s
gamma-h-11  PASS  15 s
gamma-h-12  PASS  15 s
gamma-h-13  PASS  14 s
gamma-h-14  PASS  19 s
gamma-h-15  PASS  12 s
gamma-h-16  PASS  13 s
gamma-h-17  PASS  19 s
gamma-h-18  PASS  14 s
gamma-h-19  PASS  15 s
gamma-h-20  PASS  20 s
gamma-h-21  PASS  14 s
gamma-h-22  PASS  13 s
gamma-h-23  PASS  13 s
gamma-h-24  PASS  14 s
gamma-h-25  PASS  15 s
gamma-h-26  PASS  21 s
gamma-h-27  PASS  28 s
gamma-h-28  PASS  27 s
gamma-h-29  PASS  24 s
gamma-h-30  PASS  26 s
gamma-h-31  PASS  18 s
gamma-h-32  PASS  22 s
gamma-h-33  PASS  16 s
gamma-h-34  PASS  18 s
gamma-h-35  PASS  14 s
gamma-h-36  PASS  14 s
gamma-h-37  PASS  16 s
gamma-h-38  PASS  17 s
gamma-h-39  PASS  16 s
gamma-h-40  PASS  17 s
gamma-h-41  PASS  18 s
gamma-h-42  PASS  14 s
gamma-h-43  PASS  14 s
gamma-h-44  PASS  17 s
gamma-h-45  PASS  12 s
gamma-h-46  PASS  23 s
gamma-h-47  PASS  16 s
gamma-h-48  PASS  16 s
gamma-h-49  PASS  26 s
gamma-h-50  PASS  18 s
gamma-h-51  PASS  29 s
gamma-h-52  PASS  18 s
gamma-h-53  PASS  19 s
gamma-h-54  PASS  18 s
gamma-h-55  PASS  24 s
gamma-h-56  PASS  19 s
gamma-h-57  PASS  18 s
gamma-h-58  PASS  20 s
gamma-h-59  PASS  20 s
gamma-h-60  PASS  16 s
gamma-h-61  PASS  20 s
gamma-h-62  PASS  25 s
gamma-h-63  PASS  25 s
gamma-h-64  PASS  30 s
gamma-h-65  PASS  24 s
gamma-h-66  PASS  21 s
gamma-h-67  PASS  24 s
gamma-h-68  PASS  24 s
gamma-h-69  PASS  41 s
gamma-h-70  PASS  22 s
gamma-h-71  PASS  24 s
gamma-h-72  PASS  23 s
gamma-h-73  PASS  58 s
gamma-h-74  PASS  117 s
gamma-h-75  PASS  132 s
gamma-h-76  PASS  118 s
gamma-h-77  PASS  181 s
```

`gamma-h-1` pays the one-off ambient sweep (203 s); the other rows take 10-181 s each on a
machine whose load average was 6-18 during the run, so these times are recorded, not claimed
as the rows' cost.

## The test

`tests/lattices/test_enriques_polarization_orbits.sage` now reads every expected row from the
card by tag: `_card_row(N)` is `card("arithmetic_groups", f"gamma-h-{N}")`, and the line,
plane and flag tests compare against that card's `line_orbits`, `plane_orbits` and
`flag_orbits`.  The file's transcription of Tables 1 and 2 stays as the cases' definition and
is pinned against the cards by the new `test_the_cited_rows_are_the_cards_rows`, which a
stale or mistyped row would fail.  That pin passes on all 87 rows:

```
1 passed, 266 deselected in 1.12s
```

so the typed table and the cards agree row for row and every long row is compared with its
card rather than with the table.
