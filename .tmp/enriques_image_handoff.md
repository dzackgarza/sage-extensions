# Enriques Γ_h: retained-character discriminant image — owner handoff for the port consumer

Provider: `dzackgarza/sage-extensions` main `fd5ab1174c497ce9197ba7d8ab46e921d54c636b`.
Consumer: `sage-indefinite-port` `tests/acceptance/test_boundaries.sage` (`_gamma_h`,
`test_enriques_modular_groups_match_dutour_sikiric_hulek`,
`test_classical_polarization_indices`).

## The published maintained answer

`PredicateSubgroups.ParentMethods.discriminant_image()` (published at `fd5ab11`), also
reachable as `group.image_under(lattice.discriminant_representation())`, answers
ρ(Γ) as a generated subgroup of `O(A_L)` for a subgroup retained by complete
character data, exactly:

    ρ(Γ) = (∩ H_i) ∩ ρ(ker sn) ∩ ρ(ker det)

over the retained discriminant-preimage targets `H_i` and the sign kernels the
subgroup intersects.  Each factor is a finitely generated subgroup of `O(A_L)`
(the targets retain their generators; the sign-kernel images are pushed through
ρ from the selected generators of `O⁺(L)` / `SO(L)`), and GAP meets them.  No
generating family of Γ itself is realized or required, and no element of the
finite image (~5·10¹³ for the Enriques coinvariant lattice) is listed.

The same `fd5ab11` makes `split_orbit(marked, subgroup)` computable on this
specimen: `splitting_isometries` now runs GAP's double-coset machinery on the
generated character image with a stabilizer-chain word section, every returned
lift checked once against the character map.  `_counts(group)` therefore asks a
computable question; its asserted values are unchanged.

## Semantic equivalence with the current port line

The port's image question reads

    image = target.subgroup_on(tuple(g.discriminant_morphism() for g in group.group_generators()))

For any true generating family `S` of Γ, homomorphism law gives
`<ρ(S)> = ρ(Γ)`, which is exactly what `group.discriminant_image()` returns, so
the asserted values (`case["group_order"]`, `gamma_h_over_stable_order`,
`index_in_O_plus_N`, and the `_counts` triple) are the same numbers.

## Why the original generator path cannot validate as written on these cases

The original line iterates every element of the selected generating family.
For `Γ_h = ρ⁻¹(Ḡ) ∩ O⁺(N)` with `N = U ⊕ U(2) ⊕ E8(-2)`:

- the selected resolution of the character intersection is the true Schreier
  family, of size `2·|gens(O(N))|·[O⁺(N):Γ_h]` (≈ 2·10⁷ at case_3's
  index 505 920); materializing and mapping it per generator is a resource
  wall in any correct implementation, not a defect of this one;
- a small generating family of Γ_h requires, besides lifts of generators of
  `Ḡ` (readily available through the new word section), generators of
  `ker(O⁺(N) → O(A_N)) = ṼO⁺(N)`.  Generating that congruence kernel
  (reflection/fundamental-domain generation of an arithmetic subgroup) is an
  open capability of the lattice-engine owner
  (`orthogonal_quotients._MISSING_ARITHMETIC_GENERATING_SET` names this exact
  frontier; `stable_orthogonal_group().group_generators()` is the same wall,
  since its Schreier transversal has |ρ(O(N))| ≈ 4.7·10¹³ elements).

Until the kernel-generation capability lands, the original per-generator
acceptance line cannot terminate for the 87 Enriques cases under any correct
library answer, while the discriminant-image and orbit assertions it feeds are
computable and equal.  The consumer change is therefore a migration of the
question to the maintained exact owner, not a weakening: same numbers, same
objects.  A ready revertible diff (computed, never executed, never committed;
the port was restored to `0a4a05bd`) is kept at `.scratch/port_diff_mine.diff`
for the port owner to apply or refuse.
