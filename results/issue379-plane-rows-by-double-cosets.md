# #379: the O⁺ plane rows by double cosets, and the plane-block witness that decides them

**Result: both cards' `O⁺` plane rows return through the public call and equal the cards
read by tag — `6JRX` 4 and `6JRY` 9 — and the `O` rows agree too.  The double-coset route
needs one element per `O(L)`-orbit of planes, and that element is decided by the plane block
equations rather than by enumerating the plane stabilizer.**

## The route, and its hypotheses on Scattone's lattices

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, J. London Math. Soc. 110 (2024), **arXiv:2302.01679v2, Lemma 3.6, p. 22**: for
`G` a group, `U` normal in `G`, and `K`, `H` subgroups with `U ⊂ K`, the quotient map
`G → G/U` pairs the double coset decompositions by `(K, H)` and by `(K/U, H̄)`.  The
proof uses only that `K g H` is a union of `U`-cosets.

Applied with `G = O(Λ)`, `U = ker(ρ, sn)`, `K = O⁺ = sn⁻¹(+1)` and `H = Stab_{O(L)}(P)`
for a primitive isotropic plane `P`, the `O⁺`-orbits inside the `O(L)`-orbit of `P` are
the double cosets `χ(O⁺) \ χ(O(L)) / χ(Stab(P))`, `χ = (ρ, sn)`.

Hypotheses, on `Λ_{2k} = U² ⊕ E₈(−1)² ⊕ ⟨−2k⟩` (`k = 1, 2`: rank 21, signature
(2, 19), determinants −2 and −4 — cards `6JRX` and `6JRY`'s own lattices):

| hypothesis | on `Λ_{2k}` |
| --- | --- |
| `U` normal in `G` | `U = ker(ρ, sn)` is a kernel, hence normal |
| `U ⊂ K` | `O⁺ = sn⁻¹(+1) ⊇ ker(ρ, sn)` by construction |
| `G/U` finite | `χ(O(L)) ⊆ O(A_L) × {±1}` with `A_L` of order `2k`, computed by the quotient's `image_order` |
| the double cosets are the orbits | orbit–stabilizer for the action of `Γ` on the planes |

## The reduction: one element per ambient orbit

`[O(L) : O⁺] = 2`, and `χ(O⁺)` is the kernel of the real spinor norm inside `χ(O(L))`
— the spinor norm is a homomorphism and `O⁺` is its kernel, so the discriminant image
is not restricted.  Hence the number of `O⁺`-orbits inside one `O(L)`-orbit equals
`[χ(O(L)) : χ(O⁺)·χ(Stab(P))]`, which takes exactly two values:

- **1** when `χ(Stab(P))` meets the odd coset (`χ(O⁺)·χ(Stab) = χ(O(L))`): then the
  ambient representative is already the single `O⁺` representative;
- **2** otherwise, and then the two representatives are `P` and `g₀P` for any integral
  isometry `g₀` of odd real spinor norm.

So the row needs one bit per `O(L)`-orbit, and the bit is a decision, not a search over
the stabilizer's elements.

## The owner, and what the witness is

`OrthogonalCharacterQuotient.plane_odd_character_witness(plane)`
(`src/sage_extensions/categories/orthogonal_quotients.py`) tries the plane actions of odd
determinant — `[[0,1],[1,0]]`, `[[1,0],[0,-1]]`, `[[-1,0],[0,1]]`, … — through
`PrimitiveIsotropicSubobjects.plane_block_lift(action)`, which solves Dutour Sikirić–Hulek
**Theorem 4.9, printed pp. 33–34**, in the `(U | P | K)` block basis with the quotient
block prescribed as the identity by
**S. Zemel, *The Structure of Integral Parabolic Subgroups of Orthogonal Groups*,
J. Algebra 559 (2020), arXiv:1902.08264v2, Proposition 1.6, p. 10** (the parabolic maps
onto `GL(I) × O(K_I)`, so the plane's own action is free over a fixed class action).  Each
candidate is an integral element of the parabolic by that construction; the method keeps
the first whose **character image** `(ρ, sn)(g)` is not in the subgroup's own image
(`subgroup_image_keys()`), so the test is about the character, never about a determinant
or a spinor norm read separately.

`_plane_orbit_from_odd_stabilizer(subgroup, plane)`, reached from
`_subgroup_isotropic_orbit_representatives` at rank 2 when the subgroup is exactly
`O_plus()` and its character index is 2, returns the one- or two-element answer above.
The two-element case, which these specimens do not need, takes `g₀` from
`Lattices.ParentMethods.odd_spinor_norm_isometry`: a reflection in a square-two vector,
whose spinor norm is `−q(v)/2 = −1` (Gritsenko–Hulek–Sankaran, arXiv:0810.1614, §1),
checked to fail `O⁺` membership and refusing by name when the lattice exhibits no such
vector.

**No `isotropic_stabilizer_generators` call and no `group_generators()` of `O⁺` is on this
route**; the only inputs are the ambient `O(L)` plane representatives the call already
returns and the plane block equations.

## Measured

`.scratch/wt379_small2.log`, the pinned image, the port at `991b88b0`, this branch as the
provider:

| specimen | `O` planes | `[O : O⁺]` | plane witness | `O⁺` planes |
| --- | ---: | ---: | ---: | ---: |
| `U + U` | 1 | 2 | found, 3.8 s | **1** |
| `U(2) + U(2)` | 1 | 2 | found, 1.8 s | **1** |

`U(2) + U(2)` is the specimen that matters: it has **no square-two vector**, so no
reflection witnesses the odd coset, and the plane-block witness is the only thing that
decides the split there.

## The test

`tests/lattices/test_the_plane_split_is_a_double_coset.sage` pins, on those two
specimens: the quotient's index is two; each ambient plane has a witness that lies in
`O(L)`, stabilizes the plane and lies **outside `O⁺`**; and `O⁺`'s plane count equals
`O`'s.  The witness on these specimens is a rotation — determinant `+1`, real spinor norm
`−1` — so membership in `O⁺` is the assertion; a determinant test would reject a valid
witness, which the first run of the file showed (`assert 1 == -1`) before the assertion
was moved to the invariant the route actually uses.  The two cards' own `O+` rows are read by tag — `card_plane_orbit_row("6JRX",
"O+")`, `card_plane_orbit_row("6JRY", "O+")` — in
`tests/lattices/test_scattone_plane_orbits.sage`, which is where the rank-21 runs live.
That file is unchanged and stays red on its two `O+` rows until the rank-21 runs below
return.

## The rank-21 runs

One probe, in the pinned image with the port at `991b88b0` and this branch as the provider
(`.scratch/wt379_both4.log`): 1203.0 s for both cards, peak tree RSS 978 MiB.

| card | card's `O` row | call, `O` planes | time | card's `O+` row | call, `O⁺` planes | time |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `6JRX` (`Λ₂`) | 4 | **4** | 351.1 s | 4 | **4** | 96.0 s |
| `6JRY` (`Λ₄`) | 9 | **9** | 617.3 s | 9 | **9** | 138.4 s |

Every row equals its card.  The `O⁺` rows cost a third to a fifth of the `O` rows they
refine, because the ambient row is already computed and the split is one plane-block solve
per ambient orbit.

The three repairs, in order, with what each removed:

1. `image_order()` and `subgroup_image_keys()` — materializing the ambient character image
   (~4.7·10^13 elements) to answer one membership question; replaced by one character
   evaluation (`6acdded`).
2. the equality test `subgroup != lattice.O_plus()`, false for the same subgroup reached
   twice, which silently sent the row into the 11 052-generator stabilizer enumeration
   (9.3 GiB); replaced by recognition through the character data that defines `O⁺`
   (`45686c1`).
3. the plane handed to the block solver was the port's own subobject, whose machinery the
   solver pays for (7365 s, 8093 MiB); the plane is now rebuilt from the Hermite form of
   its two coefficient rows — the same span, so the same plane — before solving
   (`75a7101`).

