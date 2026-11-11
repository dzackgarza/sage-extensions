# #285: which step of the filtered walk takes the time

**Result: the sift is not the step, the product beside it is, and the walk's real
cost is the number of roots the engine's enumeration puts in front of the
filter.** The measurements below are new, on the adopted runtime, at Sterk's
first cusp, and they correct the per-step table of
`results/issue312-membership-sift.md` §2 by splitting the sift call from the
group multiplication inside it.

Nothing here bounds the delivered route: no measurement below is a time cap, and
where a run was stopped it was stopped by the probe's own budget and is reported
as stopped.

## 1. The specimen and the controlling vector

`T_En = U ⊕ U(2) ⊕ E8(−2)`, `Γ_{En,2}`, cusp `Sterk_1` (`v = e`),
`N = v^⊥/Zv` of rank 10 and signature (1, 9).  Sterk's controlling vector
at this cusp is `x = e' + f'` (§4.3.5, p. 19 of *Compactifications of the period
space of Enriques surfaces, Part I*, Math. Z. 207 (1991)), of square 4, and his
printed roots are `Sterk.sterks_in_TEn()["Sterk_1"]`.

Checked against the library's transcription, not quoted:

| printed root | `q(α)` | `b(x, α)` | `b(x,α)²/|q(α)|` |
| --- | --- | --- | --- |
| α₁ … α₉ | −4 | 0 | 0 |
| α₁₀ | −4 | 4 | **4** |
| α₁₁ | −4 | 8 | **16** |
| α₁₂ | −4 | 16 | **64** |

which is exactly the three heights Sterk prints on p. 19 (`4`, `16`, `64`) and his
sentence "orthogonal to x we find α₁, …, α₈, and e₉".  So `x = e' + f'` is the
point he used, its first nine walls pass through it, and the last three are at
the heights he records.  The height functional is Vinberg's
(*On the groups of unit elements of certain quadratic forms*, Math. USSR Sb. 16
(1972), §3.2, formula (43): `sinh²ρ(p₀, Π_e) = (e,e)(v₀,v₀)/(e,v₀)² − 1`).

## 2. One question of the walk, step by step

`IsotropicVectorReductionImage.admits_root(root)` is one question.  Its steps,
timed on 40 candidates the walk itself produced (`time.process_time`, quiet
machine, Sage 11.0.beta5 on the pinned image with the indefinite port at `/work`):

| step | per call |
| --- | --- |
| the coordinates of the root in `N` (the memo key) | 0.048 ms |
| `class_lift` — the class lifted into `v^⊥` | 1.30 ms |
| the reflection of `T_En` in that lift | 15.22 ms |
| **its discriminant image `ρ(g)`** (`discriminant_morphism`) | **55.89 ms** |
| the sift call (`_coset_meets_the_subgroup`) | see below |

and inside that last call, after the chain exists:

| ingredient of `_coset_meets_the_subgroup(image)` | per call |
| --- | --- |
| `one * image` — one product in `O(A_L)` | **43.69 ms** |
| `membership.contains(image)` — the sift itself | **0.334 ms** |
| the whole call | 38.32 ms |

`ρ(K_v)` has order 1 at this cusp (`|rho(K_v)| = 1`, measured), so
`_coset_meets_the_subgroup` iterates `kernel_discriminant_image()` once, over the
identity, and forms `identity * image`:

    any(membership.contains(element * image) for element in self.kernel_discriminant_image())

The product is therefore pure overhead — the sift could take `image` itself —
and at 43.7 ms it costs 130 times the 0.334 ms sift it wraps.  That is the step
the 964 s went to, together with the 56 ms discriminant image beside it: a
question costs about **0.116 s of CPU**, of which 0.056 s is `ρ(g)` and 0.044 s
is an identity product, and 0.0003 s is the sift.

The chain itself is a one-off: the first call of `discriminant_image_membership()`
builds the Schreier–Sims chain of `ρ(Γ_{En,2}) ≤ O(A_L)` (order 696729600) in
**94.0 s**, and every later sift is 0.334 ms.  That 94 s is what
`results/issue312-membership-sift.md` saw as "the first question builds `ρ(Γ)`".
The 964 s of the earlier run over 1400 questions is the 0.116 s per question at
a loaded machine (0.69 s of wall each, load average 17), not a 0.3 ms sift.

## 3. The walk, and what actually stops it

Three measurements at `Sterk_1`, all with Sterk's point and no time cap inside
the algorithm:

- **The cone at `x`.**  `FundCone` asks the filter about every root of `x^⊥`:
  242 of them are admitted, which are the roots through the point `p₀` that the
  subgroup contains (Vinberg 1972, §3.2, rule 1 and (39)).
- **The enumeration.**  With the filter asked first, the walk had put **2825
  distinct questions** to the filter by 1489 s of wall time (704 s of CPU) and
  had not established finite volume; 664 of the answers were "admitted".  With
  the filter asked last — after the wall condition `(e, e_i) ≤ 0` of (40), which
  is the same conjunction in another order — the walk asked 200 questions in
  150 s and then spent 800 s inside a single layer of the engine's candidate
  enumeration without asking another, because the layer's solutions are then
  rejected cheaply and there are very many of them.
- **The shell at the third wall.**  The candidates at height `h` lie in one shell
  of the definite lattice `x^⊥`: `w = d·e − a·x` with `a = b(e,x)`, `d = q(x)`,
  `q(w) = d(d·q(e) − a²)` — the decomposition
  `HyperbolicLattices.isotropic_elements_below_height` uses for isotropic
  vectors.  For Sterk's third wall `a = 16` and `q(e) = −4`, so the shell is the
  vectors of square 1088 in a rank-nine lattice of determinant 256; asking for
  the shell of square 1056 (the same shape, one step nearer) **exceeded the
  6 GiB resident guard** without returning a list.

So the filter is not what makes the walk expensive, and neither is the sift.  The
walk is expensive because the engine enumerates *all* solutions of the norm
equation in a layer and only then applies the wall condition, while Vinberg's
§4.1 (p. 30) prescribes the opposite:

> "Construction of the sequence (38) thus reduces to writing down those solutions
> of the Diophantine equation (57) that satisfy conditions (58) in increasing
> order of the quantity (59), and in checking conditions (49) for each solution
> as it is written down."

Conditions (58) are the cone conditions `b_i ≤ 0` against the normals already
accepted; checking them inside the enumeration is what keeps the count small, and
it is the one thing the engine does not do.

## 4. What that leaves

Three units, in the order they pay:

1. **The enumeration** — enumerate the solutions of the norm equation *subject to
   the wall conditions*, as in §4.1 (58), instead of filtering after the fact.
   This is the blocker: no arrangement of the filter makes the third wall of
   Sterk's first diagram reachable, because its shell cannot be materialized.
2. **`identity * image`** — `_coset_meets_the_subgroup` should sift `image`
   directly when `ρ(K_v)` is trivial, which it is at all five cusps (measured;
   the family that decides it is the Eichler transvections of
   Gritsenko–Hulek–Sankaran, arXiv:0810.1614, §3.1, equation (4)).  44 ms of
   every question, removed by an `if`.
3. **`ρ(g)` of a reflection** — 56 ms per question; `discriminant_isometry()`
   computes the action in both directions, and for a reflection the two are the
   same isometry, so the inverse is recomputable at no cost.

The wall counts themselves are pinned and red by
`tests/lattices/test_the_isotropic_reduction_image.sage`
(`test_every_cusp_chamber_has_the_wall_count_of_its_card_row`, commit `4dc896d`,
which does not return at any of the five cusps).
