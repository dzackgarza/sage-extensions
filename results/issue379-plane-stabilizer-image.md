# #379: the O⁺ plane rows need one bit per O-orbit, and that bit is a Levi element

**Result: the double-coset route is wired at its owner and the row reduces to a single
computed bit per `O(L)`-orbit of planes — whether the plane stabilizer contains an isometry
of real spinor norm −1.  The rows of `6JRX` and `6JRY` are not returned by this turn: the
certificate for that bit is a Levi element of the plane stabilizer, and nothing in the tree
constructs one.  No count is asserted anywhere below.**

## The route, and its hypotheses on these two lattices

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, arXiv:2302.01679v2, **Lemma 3.6, p. 22**: for `G` a group, `U` normal in `G` and
`K`, `H` subgroups with `U ⊂ K`, the quotient map `G → G/U` pairs the double coset
decompositions by `(K, H)` and by `(K/U, H̄)`.  Its proof uses only that a double coset is a
union of `U`-cosets, which is where `U ⊂ K` enters.

Applied as the issue states it, with `G = O(Λ_{2k})`, `U = ker(ρ, sn)`, `K = O⁺ = sn⁻¹(+1)`
and `H = Stab_{O(L)}(P)` for a primitive isotropic plane `P`, the `O⁺`-orbits inside the
`O(L)`-orbit of `P` are the double cosets
`(ρ,sn)(O⁺) \ (ρ,sn)(O(L)) / (ρ,sn)(Stab(P))`.

Checked on `Λ_{2k} = U² ⊕ E₈(−1)² ⊕ ⟨−2k⟩` (`k = 1, 2`; rank 21, signature (2, 19),
determinants −2 and −4, the two cards' own symbols):

| hypothesis | on `Λ_{2k}` |
| --- | --- |
| `U` normal in `G` | `U = ker(ρ, sn)` is the kernel of a homomorphism, so normal |
| `U ⊂ K` | `O⁺ = sn⁻¹(+1) ⊇ ker(ρ, sn)` by construction |
| `G/U` finite | the character image is `ρ(O(L)) × {±1}` with `ρ(O(L)) ⊆ O(A_L)` finite (`A_L` of order `2k`), computed by the quotient's own `image_order` |
| the double cosets are the orbits | orbit–stabilizer: `Γ`-orbits of `P` are `Γ \ G / Stab_G(P)` |

## The reduction: one bit per O-orbit

Both lattices have `O⁺ ⊂ O(L)` of index 2, `O⁺ = sn⁻¹(+1)`, and `ρ(O⁺) = ρ(O(L))` — a
reflection in a norm-2 vector has trivial `ρ` and spinor norm −1, so the sign can always be
corrected without touching the discriminant image.  Hence
`(ρ,sn)(O⁺) = ker(sn)` inside `F = (ρ,sn)(O(L))`, and

    # of O⁺-orbits inside one O(L)-orbit of P  =  [F : ker(sn)·F_P]  =  1 if F_P ⊄ ker(sn), else 2,

where `F_P = (ρ,sn)(Stab_{O(L)}(P))`.  So the whole row is `Σ` over the `O`-orbits of one bit
each: **does the plane stabilizer contain an isometry of real spinor norm −1?**

The cards say the `O⁺` rows equal the `O` rows on both lattices, so that bit is 1 for every one
of the 4 + 9 planes; the row is therefore the `O` row whenever the bit is certified.  Nothing
below assumes that: the bit is what a certificate has to produce.

## Why the existing witnesses do not supply the bit

The witnesses the tree already has are reflections in vectors of square 2 (`sn = −(r,r)/2 =
−1`, Gritsenko–Hulek–Sankaran §1) and the Levi part `1_plane ⊕ (−1)_complement` of #351.

- A reflection `s_r` fixes a **totally isotropic** plane `P` setwise exactly when `r ∈ P^⊥`:
  for `p ∈ P`, `s_r(p) = p − 2b(p,r)/q(r)·r` lies in `P` only if `b(p,r) = 0` (a nonzero
  multiple of `r` is not isotropic), and `r ∉ P` because `P` is isotropic.
- `P^⊥/P` is **negative definite** here — `P^⊥` has rank 19 and signature (2, 19) minus a
  2-dimensional totally isotropic subspace leaves (0, 17) — so every vector of `P^⊥ \ P` has
  negative square, and a reflection in it has positive spinor norm.

So the odd stabilizer element of a plane is necessarily a **Levi element that acts nontrivially
on `P`** (a `GL(P)` part of determinant −1, which the whole element's determinant and spinor
norm are read from — Zemel, *The Structure of Integral Parabolic Subgroups of Orthogonal
Groups*, J. Algebra 559 (2020), arXiv:1902.08264v2, Proposition 1.10, p. 13, the statement
#351 already uses for the line case).  The tree constructs the line's Levi part and the
split-signature witness; it constructs no `GL(P)` Levi lift for a plane.

## What is wired

`OrthogonalCharacterQuotient.splitting_isometries_from_stabilizer_image`
(`src/sage_extensions/categories/orthogonal_quotients.py`) is #17's double-coset computation
factored out of `splitting_isometries`: it takes the stabilizer's **image** in the finite group
and returns one lift per double coset `(ρ,sn)(Γ) \ (ρ,sn)(O(L)) / (ρ,sn)(Stab)`.  A caller that
can certify a plane stabilizer's image therefore gets the plane split without enumerating that
stabilizer; `splitting_isometries` now delegates to it, so the line route and any plane route
run the same code.

## Measured

The probe `.scratch/p379_probe.py` (the pinned image, the port at `991b88b0`, this worktree as
the provider) runs, for `k = 1` and `k = 2`: the `O` plane row (the route's input), the
character image orders of `O(L)` and `O⁺`, and — per plane, capped — the plane stabilizer's
generating family and its image.  The factored method agrees with the generator form on the small specimen `U + U`
(`.scratch/p379_factor.py`, `.scratch/wt379_factor.log`): seven stabilizer generators, and
both `splitting_isometries(generators)` and
`splitting_isometries_from_stabilizer_image(images)` return **1** lift.

The Scattone probe was started and had not reached its first `O` row's end when this was
committed: at load average 14 on the four CPUs, `Λ₂`'s `O` plane row — the route's *input*,
which is on main at `dc56ac5a73` — was still running after five minutes
(`.scratch/wt379_probe.log`).

The `O` rows are the input and they are not free at rank 21; the O⁺ rows stopped in the
current route at 5099 MiB and 3600 s on degree 2 (the issue's own measurement), which is the
`isotropic_stabilizer_generators` enumeration this route exists to avoid.

## What this does not claim

- The `O⁺` plane rows of `6JRX` and `6JRY` are **not** returned by this route yet, and no count
  is asserted.  The committed test
  `tests/lattices/test_scattone_plane_orbits.sage` already reads both cards' `O+` rows by tag
  (`card_plane_orbit_row("6JRX", "O+")`, `("6JRY", "O+")`); it stays red on the two `O+` rows
  until the Levi certificate exists.
- The missing piece is a construction, not a theorem: the double-coset statement applies, and
  the card rows say the bit is 1 for all thirteen planes.  What is missing is an integral lift
  of a `det = −1` element of `GL(P)` on `P^⊥/P`, with its spinor norm computed.
