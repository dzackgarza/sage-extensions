# issue 312: `G_v = Stab_Γ(v)`'s image on `v^⊥/⟨v⟩`, at Sterk's five Enriques cusps

The public call is
`subgroup.isotropic_vector_reduction_image(v)` on the subgroup's own category
(`PredicateSubgroups.ParentMethods`), returning
`IsotropicVectorReductionImage`.  It is run here on `T_En` with
`Γ_{En,2}` at Sterk's representative of each of the five cusps.

## 1. The call

`L` even, `v` a primitive isotropic vector, `Γ ≤ O(L)` a subgroup equal to the
preimage of its own discriminant image, `N = v^⊥/⟨v⟩`, `P_v = Stab_{O(L)}(v)`,
and `λ: P_v → O(N)` the Levi map (Dutour Sikirić–Hulek, arXiv:2302.01679v2,
theorem `theorem_isotropic_k_planes`, printed p. 22: the block form of an
isometry preserving a primitive isotropic sublattice, with its quotient block).
The object returns

- `reduction()`, `line()`, `vector()`, `lattice()` — `N` and the line;
- `kernel_transvections()` — one Eichler transvection `t(v,a)` per basis vector
  of `v^⊥`, each asserted to fix `v` and to act trivially on `N`; they generate
  `K_v = ker λ` for a line (Gritsenko–Hulek–Sankaran, arXiv:0810.1614, §3.1,
  equations (4)–(5); for a line the setwise kernel is `F⁺(1) ∪ F⁻(1)` and only
  `F⁺(1)` fixes `v`, and that fibre is the integral Eichler transvection kernel);
- `kernel_discriminant_image()` and `kernel_discriminant_image_is_trivial()` —
  `ρ(K_v) ⊆ O(A_L)`, an **output**, because one lift of an isometry decides
  membership only when it is trivial;
- `lift(σ)`, `reduction_image(g)`, `contains(σ)`, `contains_root_reflection(root)`
  — the membership test: the lifts of `σ` are `{k g_0 : k ∈ K_v}`, and
  `Γ = ρ⁻¹(ρ(Γ))`, so `σ ∈ G_v ⟺ ρ(g_0) ∈ ρ(K_v)ρ(Γ)`, a computation in the
  finite group `O(A_L)`;
- `reflection_generators(roots)` — the reflections of `N` in `G_v` among a
  supplied family of ambient roots, decided by the same criterion, and
  `generation_obstruction()` — what keeps `generators()` from being all of
  `G_v`.

`Γ = ρ⁻¹(ρ(Γ))` is checked at construction (`contains_character_kernel`), and
so is primitivity and isotropy of `v`; a subgroup not of that shape, or a vector
that is not primitive isotropic, is refused rather than answered for.

## 2. The five cusps of `Γ_{En,2}` on `T_En`

`T_En = U ⊕ U(2) ⊕ E8(−2)`, rank 12, signature (2,10), `|det| = 1024`;
`Γ_{En,2}` by the construction of #286 item 2 (Alexeev–Engel–Garza–Schaffler,
Nagoya Math. J. 259 (2025), Def. 2.6; Sterk, Math. Z. 207 (1991), Proposition
2.7, p. 6), whose five 0-cusps are Proposition 4.2.3 with Remark 4.2.4, p. 16.
The representatives are `Sterk.selected_isotropic_vectors()`.

| cusp | `N = v^⊥/⟨v⟩` | `ρ(K_v)` | kernel transvections | Sterk's diagram | printed roots in `G_v` |
| --- | --- | --- | --- | --- | --- |
| `Sterk_1` (`e`) | rank 10, (1,9), even, `det −1024` | trivial (order 1) | 11 | 12 walls | **12 of 12** |
| `Sterk_2` (`e'`) | rank 10, (1,9), even, `det −256` | trivial | 11 | 10 walls | **10 of 10** |
| `Sterk_3` | rank 10, (1,9), even, `det −256` | trivial | 11 | 12 walls | **12 of 12** |
| `Sterk_4` | rank 10, (1,9), even, `det −256` | trivial | 11 | 11 walls | no `T_En`-coordinate family held |
| `Sterk_5` | rank 10, (1,9), even, `det −256` | trivial | 11 | 14 walls | no `T_En`-coordinate family held |

`issue312-probeG.log`.  The diagram sizes are `Sterk.sterk_roots()`'s own
families — Sterk's 4.3.5–4.3.9 — and the last column is the exact criterion, not
the "one lift each" check of research 882541e13b: at the three cusps whose
printed roots the library also holds in `T_En` coordinates
(`Sterk.sterks_in_TEn()`), **every** root's reflection lies in `G_v`.

That is one lift deciding nothing and the kernel deciding it: with `ρ(K_v)`
trivial the value `ρ(g)` is independent of the lift chosen, so the criterion
collapses to `ρ(g) ∈ ρ(Γ)` — and it is exactly that collapse which makes the
twelve, ten and twelve printed reflections members.  (Measured on the *uncoerced*
copy of `T_En` the same test answers zero of twelve, because a vector of an equal
copy is a different lattice element: the call reads such a vector by its
coordinates and asserts the two Gram matrices equal.)

## 3. What is missing, and named

Three owner-side gaps, measured here, are what keep `generators()` short of all
of `G_v`; `generation_obstruction()` returns them as its text:

1. **The parabolic's generator family is plane-only.**
   `parabolic_stabilizer_generators()` and `parabolic_transvection_generators()`
   raise for a rank-one subobject: *"the parabolic construction here is stated for
   a primitive isotropic plane, but … has rank 1"* (`isotropic_parabolics.py`,
   `plane_basis`).  So a line has no constructed parabolic family at all.
2. **The port's line stabilizer does not return.**
   `RECURSION.pointwise_stabilizer_generators(v)` on `T_En` at Sterk's first
   cusp was still running after 540 s and was stopped; so was
   `levi_action().kernel().group_generators()` (`issue312-probeB.log`,
   `issue312-probeC.log`, `issue312-probeF.log`).
3. **Phantom port methods on the line's unipotent path.**
   `lattices.py:11688` calls `RECURSION.isotropic_quotient_kernel_generators`
   and `lattices.py:11734` calls `RECURSION.isotropic_quotient_lift`; neither
   exists in the port (`src/sage_indefinite_port/indefinite/recursive.py`,
   `EichlerRecursion`).  So `unipotent_group_generators()` on any *line* raises
   `AttributeError: 'EichlerRecursion' object has no attribute
   'isotropic_quotient_kernel_generators'` (`issue312-probeA.log`).  This route is
   not used by the call — it uses the Eichler transvections directly — but the
   public method is broken on main.

Also measured, and worked around rather than repaired here:
`IsotropicReduction.levi_action(subgroup=Γ)` raises *"Γ must be a subgroup of
O(T_En)"* because `_levi_action_in_subgroup` compares the subgroup's supergroup
with a freshly built `O(L)` by identity (`lattices.py:11488`), and
`parabolic_obstruction()` raises for a line at `plane_basis`.

## 4. What #297 must supply

The wall count is #297's: a fundamental chamber of the *reflection subgroup* of
`G_v` generated by the roots above, anchored at the cusp, i.e. Vinberg's
algorithm run for a prescribed finite-index subgroup given by generators.  What
`#297` needs from this call is exactly
`reflection_generators(roots)` — the reflections of `N` in `G_v`, each decided by
the discriminant criterion — and what it must supply in return is the
classification of subdiagrams (elliptic, parabolic, indefinite) and the wall
count of the chamber.  The library has that algorithm for the full `O(K)` only
(`HyperbolicLattices.fundamental_chamber`, `_vinberg_search`); nothing in it takes
a subgroup given by generators.  Until it does, the record above is the subgroup
per cusp and the published roots it contains.

## 5. The tests

`tests/lattices/test_the_isotropic_reduction_image.sage` — three tests over the
five cusps: the reduction's rank, signature, parity and determinant; eleven
kernel transvections per cusp with `ρ(K_v)` of order 1; and every printed root of
cusps 1–3 reflected inside `G_v`, with Sterk's pages in the docstring.
