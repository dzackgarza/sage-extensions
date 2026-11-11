# #17: the double-coset route to subgroup isotropic-line rows, and the sign witness it needed

## The statement used, and its hypotheses on N

**D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6, p. 22:**

> **Lemma 3.6** Let \(G\) be a group, \(U\) a normal subgroup and \(K\), \(H\) two subgroups of
> \(G\) such that \(U \subset K\). Then the quotient map \(G \to G/U\) establishes a
> many-to-one correspondence between double coset decompositions of \(G\) by \((K, H)\) and of
> \(G/U\) by \((K/U, \bar H)\) where \(\bar H\) is the image of \(H\) in \(G/U\).
>
> *Proof.* Let us take a double coset decomposition \(G = \cup_i K g_i H\). Then mapping to the
> quotient we obtain \(G/U = \cup_i K/U \bar g_i \bar H\). Since \(U \subset K\), the double
> coset \(K g_i H\) is actually a union of left \(U\)-cosets. Therefore the double cosets
> \(C_i = K/U \bar g_i \bar H\) are disjoint … This establishes that the mapping is well
> defined and it is surjective by construction. □

and, immediately after it, the application the issue's formula comes from (same page):

> "We can apply the above lemma to our case with \(U = \widetilde O(N)\) the kernel of the
> action of \(O(N)\) on the discriminant, \(K = \Gamma_h\) and \(H = G_x\). The second key
> ingredient is that the quotient \(O(N)/\widetilde O(N) \cong O^+(\mathbf F_2)\) is finite.
> We can apply the existing approach for finite groups … and thus reduce the orbit splitting
> from \(O(N)\) to the group \(\Gamma_h\)."

**Hypotheses, checked on \(N = U \oplus U(2) \oplus E_8(-2)\):**

| hypothesis | on N |
| --- | --- |
| \(U\) is normal in \(G\) | \(U = \ker(\rho, \mathrm{sn})\), the kernel of a homomorphism \(O(N) \to O(A_N) \times \{\pm 1\}\), so normal |
| \(U \subset K\) | \(K = \Gamma = (\rho,\mathrm{sn})^{-1}(S)\), so it contains the whole kernel by construction |
| \(G/U\) finite | \(|O(A_N) \times \{\pm1\}| = 2 \cdot 46\,998\,591\,897\,600\), computed below, and \((\rho,\mathrm{sn})\) is onto its image |
| the double cosets are what the orbits are | orbit–stabilizer: \(G\)-orbits of \(x\) under \(K\) are \(K \backslash G / H\) with \(H = \mathrm{Stab}_G(x)\) |

The proof itself needs nothing else: it uses only that \(K g_i H\) is a union of \(U\)-cosets,
which is where \(U \subset K\) enters. So the lemma applies, and the count is a finite one in
\(O(N)/U\), not a statement about generators of \(\Gamma\) — which is the whole point of the
issue's rewrite.

The row this is compared against is DSH **§3.6, p. 22**: \(\widetilde O^+(N) \backslash D_N\)
has **528** zero-dimensional cusps, which under \(O^+(\mathbf F_2^{10})\) split into orbits of
lengths 527 and 1; the two \(O(N)\)-orbits of lines are spanned by \(L_1 = \mathbf Z e_1\) and
\(L_2 = \mathbf Z e_3\), with stabilizer images of index 1 and 527.

## The owner, and the call site replaced

The owner is `_subgroup_isotropic_orbit_representatives`
(`src/sage_extensions/categories/orthogonal_quotients.py`), reached by
`PredicateSubgroups.ParentMethods.isotropic_orbit_representatives`.  For a subgroup it
sequences: ambient representatives from
`O(N).isotropic_orbit_representatives(rank)`; then, per representative, either
`OrthogonalCharacterQuotient.isotropic_line_stabilizer_image` (the Eichler-criterion route,
which **refuses** a lattice without two hyperbolic planes — #315, and N has rank₂ = 2), or
`OrthogonalCharacterQuotient.splitting_isometries(stabilizer_generators)` with
`stabilizer = O(N).isotropic_stabilizer_generators(representative)`.

The Õ⁺ row reached a `group_generators()` call on the *subgroup* inside that second route:
`_splitting_isometries_in_im_rho_from_image`, the sign-witness loop

```python
stable = self.lattice.stable_orthogonal_group()
for candidate in stable.group_generators():      # <- Otilde(N): an infinite arithmetic group
    if any(not sign_of(candidate, label) for label in sign_labels):
        flip_element = candidate
        break
```

`stable` is \(\widetilde O(N) = \ker \rho\), which by sage-extensions#17's reading
(`results/issue17-kernel-generation-blocker.md`, `ab3323baa7`) has **no published or selected
generating family**: Kneser's conditions fail on N (rank₂ = 2) and N has no second hyperbolic
plane (Gritsenko–Hulek–Sankaran, arXiv:0810.1614v1, Proposition 5.6, p. 17).  That call does
not return, and it is where the row stopped (#310, #339).

## The repair

Two changes, both in `src/sage_extensions/categories/orthogonal_quotients.py`, at that owner:

1. **A sign witness instead of a generating family.**  `OrthogonalCharacterQuotient` gains
   `_kernel_sign_flip(label)`: it returns one explicit isometry of \(\ker\rho\) whose named
   sign is \(-1\), out of the lattice's own basis and the pairwise sums and differences of
   that basis — the same finite candidate list `isotropic_line_stabilizer_image` already
   searches for its sign witness — with each candidate checked (integral reflection, trivial
   discriminant image, the named sign \(-1\)).  The `flip_element` step of
   `_splitting_isometries_in_im_rho_from_image` now calls it instead of iterating
   `stable_orthogonal_group().group_generators()`.
   For \(N = U \oplus U(2) \oplus E_8(-2)\) the witness is the reflection in a vector of
   square 2 in the hyperbolic summand, which is *named on the page*: DSH arXiv:2302.01679v2,
   **p. 2** — "the reflection with respect to a vector of length 2 in the summand \(U\) of
   \(N\) gives an element in \(\widetilde O(N)\) with real spinor norm \(-1\)" — the element
   that makes \(\widetilde O^+(N)\) the index-two subgroup of \(\widetilde O(N)\).  In
   §1 of Gritsenko–Hulek–Sankaran the real spinor norm of a reflection is \(-(r,r)/2\), so
   square 2 is exactly sign \(-1\).  A lattice where no candidate is a witness returns
   `None` and the row refuses with the same message as before, rather than guessing.
2. **No `.group_generators()` on any subgroup of the row.**  With (1) in place the route is
   the double coset computation the issue asks for: the ambient orbit representatives from
   `O(N).isotropic_orbit_representatives(rank)`, the character image of each ambient
   generator from the quotient's own cached `ambient_discriminant_images()` and
   `_image_section()`, the stabilizer's image from the images of its retained generators, and
   the double cosets in the finite group.  Nothing calls `group_generators()` on \(\Gamma\),
   on \(\widetilde O(N)\), or on any other subgroup.

The sign keeps its own datum, as #310's obligation says: it is neither folded into the
discriminant image nor assumed trivial, and the witness is verified rather than supposed.


## Runs

All on this tree, inside the pinned image (`~/sage-image/run.sh`, `/probe.py`), with the port
at `/work` and `PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src`.

**The repaired step is instant.**  `.scratch/issue17_budget.py` (`.tmp/17-budget1.log`):

```
[ambient_discriminant_images] 130.5s peak=577MiB
[_image_section] 8.7s peak=585MiB
[_sign_descent_rank] 4.8s peak=586MiB
[_kernel_sign_flip] 0.9s peak=586MiB
  witness: Morphism from Integral lattice of rank 12 and signature (2, 10) to ...
[O(N) line orbits] 42.9s peak=680MiB
  ambient representatives: 2
```

so the sign witness that used to be a `.group_generators()` call on \(\widetilde O(N)\) is
found in **0.9 s** by a verified reflection.  (A second run of the same probe, on a loaded
VM, measured the ambient sweep at 417.3 s and the ambient line orbits at 174.0 s; the
numbers above are the unloaded measurement.)

**The row still does not return, and the next wall is measured.**  Same probe, continuing:

```
--- ambient representative 0
[isotropic_stabilizer_generators[0]] 2090.0s peak=3138MiB
  |stabilizer generators|: 11052
[stabilizer_sign_flips[0]] 0.5s peak=3141MiB
[peakrss] STOPPED_AT_MEMORY_LIMIT: tree RSS 6152 MiB exceeded 6144 MiB
```

and the same row through the public call
(`tests/lattices/test_the_stable_plus_line_row_is_the_card_row.sage`, `.tmp/17-row2.log`)
printed its first test's dot — the ambient `O` row passes — and then consumed the guard's
memory and produced no summary at all: peak tree RSS 6066 MiB, no pytest report line.

So the row's cost on \(N\) is, in order:

| step | measured |
| --- | --- |
| \(\rho\) on \(O(N)\)'s 198 selected generators | 130.5 s (unloaded) / 417.3 s (loaded), once per lattice |
| the joint character sweep `_image_section` | 8.7 s |
| sign descent, sign witness | 4.8 s + 0.9 s |
| \(O(N)\)'s line orbits (the row's input) | 42.9 s (unloaded) / 174.0 s (loaded) |
| **\(O(N)\)'s line stabilizer generators** (the other input) | **2090 s, 11052 generators, 3.1 GB** |
| the finite double cosets and their lifts | not reached inside the 6144 MiB guard |

The stabilizer's **image** — the input the route asks for — is only obtainable, in this
tree, by enumerating the stabilizer's *generators* through the port's marked-lattice
machinery and mapping them; 11052 of them, for the first of the two ambient lines, at
35 minutes and 3.1 GiB.  Mapping 11052 generators through \(\rho\) costs more than the
enumeration that produced them, and the finite-double-coset stage behind it does not fit
under the memory guard, so the row does not return.  That is where this unit stops: the
offending `.group_generators()` call on a subgroup is gone and measured at 0.9 s, and what
remains is a different obstruction at the same owner.

## The Γ_h rows

Not reached: the \(\widetilde O^+\) row does not return, so the 87 \(\Gamma_h\) rows — which
run the same route with \(H \ne 1\) — were not started.  Nothing about them is claimed here.

## What this does not claim

The \(\widetilde O^+(N)\) row is **not** green: it is not the card's 528 yet, and no count is
asserted anywhere in this unit.  The double-coset formula itself is not in doubt — with the
card's own indices (1 and 527, DSH p. 22) it gives 528 = 1 + 527 exactly — but computing
those indices in this tree is the measured obstruction above, not a missing theorem.
