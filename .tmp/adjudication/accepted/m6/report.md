# Adjudication of H1–H4 for N = U ⊕ U(2) ⊕ E8(−2) (Enriques coinvariant with a free plane)

Member m6, swarm `smvzznqcw`. Direction d6: what the cited descent actually produces.

Conventions used throughout: `(,)` is the integral bilinear form with `(v,v) = 2q(v)`;
`A_L = L^∨/L` carries `q_L(x) = (x,x) mod 2Z`; `U = [[0,1],[1,0]]`,
`U(2) = [[0,2],[2,0]]`, `E8(−2) = −2·Cartan(E8)` (the form scaled by −2, so
`det E8(−2) = 256`, `A_{E8(−2)} ≅ (Z/2)^8`).

Everything marked **[V]** is verified here by the scripts listed in §7; everything
marked **[Q]** is a quotation whose source I could not open (§6).

---

## 0. The two premises, checked

**(0.1) [V] `A_N` and `|O(A_N)|`.**
`N = U ⊕ U(2) ⊕ E8(−2)` is even of rank 12, signature (2,10), `det N = 1024`, so
`A_N ≅ (Z/2)^10`. Its discriminant form has 528 elements with `q = 0` and 496 with
`q = 1` (`s1_forms.py`, §1–2). A nondegenerate `F_2`-quadratic form of dimension 10
has `2^9 ± 2^4 = 528` or `496` zeros, so **`A_N` is the split (plus) quadratic space of
dimension 10 over `F_2`**. Hence `O(A_N) ≅ O^+_{10}(2)` and

    |O(A_N)| = 2^21·3^5·5^2·7·17·31 = 46 998 591 897 600,

which reproduces the in-repo measured value (`TRAPS.md:976`,
`tests/groups/test_group_generators_use_the_supplied_family.sage:109`,
`tests/test_finite_form_groups.py:16`). The order formula used is validated by brute
force over `GL_4(F_2)`, `GL_6(F_2)` etc. inside `s1_forms.py` §3.

`A_{U(2)^5}` is *also* the split space of dimension 10 (`s1_forms.py` §2), so the two
in-repo assertions (the `planes = 5` parametrisation and the Enriques coinvariant) are
consistent with each other: both are the same isometry class. No correction is needed
to the premise — but note that the number is insensitive to the `E8(−2)` summand,
because `A_{E8(−2)}` is the split space of dimension 8 and `A_{U(2)}` the split space of
dimension 2, both split. This matters for §3.

**(0.2) [V] The quoted block.** `references/vendor/arxiv/2302.01679/Enriques_compu_rev.tex`
(= project p-165a6922b36b40789ddc90db34bb23c7), lines verified by `grep -n`:

| line | text |
|---|---|
| 1436 | "we can take a suitable subgroup of the group `Orth(U+U)` together with the Eichler transvections" |
| 1437 | "In [Example 3.7.2]{scattone} the lattice `U+U` is identified with the determinant form on `M_{2,2}(Z)`." |
| 1442–1445 | "apply the Eichler transvections `E_{e_i,x}` … for `e_i`, `1≤i≤4`, one of the 4 canonical isotropic vectors coming from the two hyperbolic planes `U` and `x` a vector orthogonal to `e_i`" |
| 1446 | `E_{e,x}E_{e,y} = E_{e,x+y}` for `e` isotropic |
| 1448–1450 | "According to [Proposition 3.7.3]{scattone} we simply need the generators of `SL_2(Z)^2` and the transvections `E_{e_i,v_{i,j}}` … `4(n−1)` … and so `4n` together" |
| 1457 | **"The group provided by the Eichler algorithm acts trivially on the discriminant."** |
| 1458–1461 | "For a case such as `U+U+E_8(−2)` this gets us `2^8` orbit representatives. By adding the isometries of the `E_8` component … reduced to just 3 … `W(E_8)` has 3 orbits in its action on `E_8/2E_8`, their sizes being 1, 120 and 135." |
| 1345, 1347 | Alg 1 = "generating set of the intersection `G ∩ GL_n(Z)`"; Alg 3 = "right cosets of `G ∩ GL_n(Z)` in `G`" |
| 1463–1474 | Theorem: for `L' ⊂ L`, "compute the stabilizer `S` of `L'` under `Ap(L)` by **Alg 1**" and cosets by **Alg 3** |

Two things follow from the text as quoted, and neither is the statement H3 needs:

1. Line 1457 is a **containment** statement about the *ambient* lattice `U+U+L`.
2. Lines 1458–1461 say explicitly that this group is *too small to be O(L)*: they must
   **add** the isometries of the `E_8` component, which do **not** act trivially on the
   discriminant (`W(E_8)` has orbits `1, 120, 135` on `E_8/2E_8` — reproduced in
   `s1_forms.py` §5). So the quoted group is a proper subgroup of `O(U+U+E_8(−2))`
   *by the paper's own use of it*.

---

## H1. Exact embedding — **PROVED** [V]

**Statement.** Let `M = U ⊕ U ⊕ E8(−2)`, and embed `N` by identity on the first plane
and on `E8(−2)` and by `U(2) = ⟨v1,v2⟩ ↪ U = ⟨e2,f2⟩`, `v1 ↦ e2`, `v2 ↦ 2f2`
(Gram `(e2,2f2) = 2`). Then `N ⊂ M` is a sublattice of index 2; the mirror choice
`v1 ↦ 2e2, v2 ↦ f2` (the problem's `(x1,x2,2y1,y2,w)` map) is equivalent by the
symmetry `v1 ↔ v2` and gives identical answers below (`s2_ambient.py` runs both).

**Discriminant data** (`s1_forms.py` §1, `s4_validate.py` §3):

* `|A_M| = 2^8 = 256` (`A_M = A_{E8(−2)}`), `|A_N| = 2^10 = 1024`.
* `N ⊆ M^∨` (all pairings of the two bases are integral) [V], hence the natural map
  `A_M = M^∨/M → A_N = N^∨/N`, `x + M ↦ x + N`, is well defined with
  kernel `(M^∨ ∩ N)/M = N/M ≅ Z/2` and image of order `2^7 = 128`, i.e. **index 8 in `A_N`**.
  So "acts trivially on the discriminant" for the ambient lattice constrains only a
  2^7-subgroup of `A_N`, and only modulo a kernel: the implication
  "trivial on `A_M` ⇒ trivial on `A_N`" has no chance in general (§H3).
* `N` and `M` are not isometric (`|A|` differs), and no `O(M)`-orbit statement is needed
  for what follows.

**A second, unimodular realization.** `A_N` contains an isotropic subgroup `H` with
`H = H^⊥`, `|H| = 2^5` [V] (`s1_forms.py` §6). The corresponding even overlattice is
unimodular of signature (2,10), index `2^5 = 32`, hence `≅ II_{2,10} = U ⊕ U ⊕ E8(−1)`
(even unimodular indefinite forms are determined by their signature; `E8(−1)` is the
unique even unimodular negative definite form of rank 8). In this realization
`A_M = 0`, so the hypothesis "acts trivially on the discriminant" is **vacuous**.
More generally an index `k` embedding into `U ⊕ U ⊕ L` forces `|disc L| = 2^{10}/k²`;
`k = 2` gives `L = E8(−2)` (used here explicitly), `k = 32` gives the unimodular case.

Verdict H1: **proved**, with the exact indices (2, and 32) and the exact dual maps: `A_M`
sits in `A_N` only modulo the kernel `N/M ≅ Z/2`, its image has index 8.

---

## H2. Which subgroup does the descent induce? — **REFUTED as a restriction/conjugation; the text supports only the Alg 1 stabilizer** [V]

The quotation supports exactly one construction: `Ap(N) := Stab_{Ap(M)}(N)`, computed by
Alg 1 (line 1345, used at line 1468). It does **not** support "restrict the ambient group
to `N`" (the ambient group does not act on `N`) and does not support a conjugate
(nothing conjugates `N` to a `U ⊕ U`-summand).

I computed the 48 named generators on `M` in the sense of lines 1437–1451 — the four block
maps `X ↦ AXB`, `A,B ∈ {S = [[0,−1],[1,0]], T = [[1,1],[0,1]]}` on `M_{2,2}(Z)` with the
determinant form, and the `4(n−1) = 44` Eichler transvections
`τ_{e,x}(v) = v + (v,e)x − ((v,x) + (v,e)q(x))e`, `e ∈ {e1,f1,e2,f2}`, `x` running over a
`Z`-basis of `e^⊥ ∩ M` (`4 + 44 = 48 = 4n`, matching line 1450 and the repo's
"44 candidate transvections", `TRAPS.md:969`). All three natural formulas for `τ_{e,x}`
coincide on `x` isotropic and all 48 maps are verified isometries fixing `e` and acting
trivially on `A_M` — the quoted claim, checked (`s2_ambient.py` §A, `s3_spinor.py` §1).

Then, for `N = U ⊕ ⟨e2,2f2⟩ ⊕ E8(−2) ⊂ M` (`s2_ambient.py` §B, `s3_spinor.py` §2):

* **6 of the 48 do not preserve `N`**: the two `S`-type block maps (for instance
  `X ↦ SX` sends `e1 = E11 ↦ E21 = −f2 ∉ N`, mixing the free plane with the scaled one),
  and `τ_{e,x}` for `(e,x) = (e1,f2), (f1,f2), (f2,e1), (f2,f1)` — the latter because
  `f2 ∈ M ∖ N`.
* **42 preserve `N`.** Of these, **34 act trivially on `A_N`** and **8 do not**:
  `τ_{f2,x}` for `x` running over a `Z`-basis of `E8(−2)`.

So the subgroup actually induced on `N` is *not* contained in `ker(O(N) → O(A_N))`.
The quoted justification "acts trivially on the discriminant" is true on `A_M` and false
on `A_N`, for exactly the elements attached to the scaled plane.

Verdict H2: **refuted** for the readings "restriction" and "conjugate"; the only reading
the text supports is the stabilizer reading, and that stabilizer-image leaves the
discriminant kernel (next section).

---

## H3. Equality — **REFUTED** (containment already fails); the sharp positive statements

**(E1) [V] The elementary lemma.** Let `e ∈ N` be isotropic and `x ∈ e^⊥ ∩ N`. Then
`τ_{e,x} ∈ O(N)` and `τ_{e,x}` acts **trivially** on `A_N`.
*Proof.* For `v ∈ N^∨` one has `(v,e), (v,x) ∈ Z` by the definition of the dual lattice
(`e, x ∈ N`), so `τ_{e,x}(v) − v = (v,e)x − ((v,x)+(v,e)q(x))e ∈ N`; integrality of
`τ_{e,x}` on `N` is the same computation. ∎
More generally, every reflection `s_v` with `v ∈ N`, `(v,v) = ±2`, lies in
`ker(O(N) → O(A_N))` (`s_v(u) − u = −(u,v)v ∈ N` for `u ∈ N^∨`), and every reflection
`s_v` with `v ∈ 2N^∨ ∩ N` does too.

**(E2) [V] The criterion.** For `e ∈ M ∖ N` there is `v ∈ N^∨` with `(v,e) = 1/2`
(equivalently `e ∉ (N^∨)^∨ = N`), and then `τ_{e,x}(v) − v` has the non-zero class
`(v,e)x mod N` whenever `x ∉ N`. So `τ_{e,x} ∈ ker(O(N)→O(A_N))` **iff** `e ∈ N`
(for `x ∈ N ∩ e^⊥`). This is exactly the obstruction candidate named in the question:
the half-integral pairing on the `U(2)` summand.

**(E3) [V] The explicit counterexample to the quoted route.** Take `e = f2` (isotropic,
`f2 ∈ M ∖ N`, `(f2, N^∨) = ½Z` since `(f2, ½e2) = ½`) and `x = r` a basis vector of
`E8(−2)` (`q(r) = −2`). Then `τ_{f2,r}` **preserves `N`** but

    τ_{f2,r}(½ e2) = ½ e2 + f2 + ½ r  ∉  ½ e2 + N,

so it moves the class of `½e2` in `A_N`; verified for all 8 basis vectors
(`s3_spinor.py` §3 prints the exact differences).

Thus the descended group is not inside the kernel, so it cannot equal
`ker(O⁺(N) → O(A_N))`. Equality fails **before** any question about generators arises.
(Note that this does not contradict the paper: line 1457 is used there only because an
approximate subgroup needs to act *trivially* on the discriminant to give orbit
representatives; it was never asserted to be the full discriminant kernel.)

**(E4) [V] The repaired generator set, with exact counts.** Replace the ambient isotropic
vectors by the isotropic vectors of `N` itself: `e1, f1` (the free `U`) and `e2, 2f2`
(the `U(2)` plane). For each, `e^⊥ ∩ N` has a `Z`-basis of 11 vectors, so
`4·(12−1) = 44` transvections, plus the two block maps that survive; by (E1) all 46 lie
in `ker(O(N)→O(A_N))`, and this is verified generator by generator
(`s6_repair.py`: 44/44 transvections and 2/2 block maps are isometries of `N`, trivial on
`A_N` and in `O⁺(N)`). This is the sharpest *proved* generating statement available here:
46 kernel elements attached to `N`'s own isotropic vectors. Equality
`ker(O⁺(N)→O(A_N)) = ⟨those 46⟩` is **not proved here** and must not be asserted: it is
exactly the Eichler/Kneser-type generation theorem whose hypotheses I could not verify
(§6). It is also not a corollary of lines 1429–1461, which state only triviality on the
ambient discriminant.

**(E5) [V] Why a reflection-only alternative is not a complete answer either.**
`N`'s norm-2 vectors are exactly `±(e1 ± f1) + w` with `w` isotropic in
`U(2) ⊕ E8(−2)` (the norms on `U(2) ⊕ E8(−2)` are multiples of 4), so the root system is
infinite and each root reflection is in the kernel by (E1). But the four roots with
`w = 0` act trivially on `U(2) ⊕ E8(−2)`, so a reflection-based generation of the kernel
would have to use the whole infinite family, and the standard "2-elementary ⇒ reflection
generation" statements are usually stated for hyperbolic lattices; `N` has signature
(2,10), so those hypotheses must be checked before anything is imported. Whether
reflections alone generate `ker(O⁺(N)→O(A_N))` is **not decided here**.

---

## H4. Spinor — **PROVED: nothing is lost; the spinor condition is not the obstruction** [V]

Convention: "O⁺" = kernel of the real spinor norm `sn_R : O(p,q) → R*/R*²` (index 2).
With `p,q ≥ 1` the four components of `O(p,q)` are labelled by
`(det g, c(g))`, `c(g)` the sign of the determinant of the block of `g` on a fixed
maximal positive-definite 2-plane; reflections have `(det,c) = (−1,−1)` for positive norm
and `(−1,+1)` for negative norm, the identity component is `(+1,+1)`, hence
`sn_R(g) = +1 ⟺ det g = c(g)`. The rule is validated against the theorem
`sn_R(s_v) ≡ (v,v) mod squares` on 15 reflections with both norm signs
(`s5_sn.py` §1: 15/15 agreement).

Applied to the generators (`s5_sn.py` §2):

* **All 48 named generators lie in `O⁺(M)`** (`det = 1`, `c = 1` for every one).
* **All 42 `N`-preserving generators lie in `O⁺(N)`.**
* In particular the 8 transvections `τ_{f2,x}` of (E3) are in `O⁺(N)` as well:
  the spinor condition removes none of them, so it does **not** repair the H2/H3
  failure.
* For `q(x) ≠ 0` there is a closed two-reflection identity
  `τ_{e,x} = s_x · s_{x + q(x)e}`, verified on all 32 such transvections
  (`s3_spinor.py` §4); both reflection norms equal `(x,x)`, so `sn = (x,x)² ≡ 1`.

Verdict H4: **proved**, and negative in content for the route: `O⁺` selection is free;
the failure is entirely the discriminant action.

---

## 5. Summary of verdicts

| | verdict | reason |
|---|---|---|
| H1 | **proved** | index 2 embedding `N ⊂ U⊕U⊕E8(−2)`, index 32 embedding into `U⊕U⊕E8(−1)`; `A_M (2^8) → A_N (2^10)` has kernel `Z/2` and image of index 8 |
| H2 | **refuted** (restriction/conjugate readings); only the Alg 1 stabilizer survives | 6/48 named generators do not preserve `N`; 8 of the 42 survivors act non-trivially on `A_N` |
| H3 | **refuted** (equality, and even containment, fail) | (E3): `τ_{f2,r}(½e2) = ½e2 + f2 + ½r ∉ ½e2 + N` |
| H4 | **proved**: all 48 ∈ `O⁺(M)`, all 42 descended ∈ `O⁺(N)` | spinor test validated on reflections of both norm signs |
| maintained alternative | (E1)+(E4): 46 proved kernel elements attached to `N`'s own isotropic vectors `e1,f1,e2,2f2`; equality not proved | no accessible primary statement with verifiable hypotheses (§6) |

---

## 6. What is *not* verified from here (explicitly)

* **Scattone, Proposition 3.7.3** — text not accessible from this VM. The bibliography of
  the vendored file identifies it as F. Scattone, *On the compactification of moduli
  spaces of algebraic K3 surfaces*, Mem. Amer. Math. Soc. **70** (1987), no. 374
  (line 1939 of the vendored `.tex`; the number "374" is confirmed by an independent
  citation index, the proposition itself is not). **Its hypotheses are unverified here.**
  Everything I say about it is a statement about the *quotation* at lines 1429–1461, not
  about Scattone's proposition.
* **Eichler, *Quadratische Formen und orthogonale Gruppen*, Springer 1952, §3** — cited at
  line 1436, not accessible here; hypotheses unverified.
* **GHS arXiv:0810.1614** — not needed for any claim above and not used. No claim in this
  report depends on it.
* Equality `ker(O⁺(N)→O(A_N)) = ⟨the 48 repaired generators⟩` — **open here**; it needs a
  transvection-generation theorem for 2-elementary indefinite lattices of signature
  (2,10) with hypotheses verified from a primary source.

## 7. Reproduction

In `.ultramath/smvzznqcw/m6/` (pure Python 3, `fractions` only, no Sage, no enumeration of
lattice isometries; total runtime well under a minute each):

* `s1_forms.py` — discriminate forms of `U, U(2), E8, E8(−2), E8(−1), N, M, U⊕U⊕E8(−1),
  U(2)⊕E8(−2), U(2)^5`; zero counts and type; `|O(A_N)|`; validation of the order formula
  by brute force in dims 2,4,6; `W(E8)` orbits `1,120,135` on `E8/2E8`; the Lagrangian of
  order 32 in `A_N`.
* `s2_ambient.py` — the 48 named generators on `M` (four block maps on the `M_{2,2}(Z)`
  determinant model, 44 Eichler transvections), isometry checks, triviality on `A_M`,
  preservation of `N`, induced action on `A_N`, for both scalings of the plane.
* `s3_spinor.py` — `O⁺` membership of all generators on `M` and on `N`, the explicit
  coset witnesses, and the identity `τ_{e,x} = s_x s_{x+q(x)e}`.
* `s4_validate.py` — validation of the `O⁺` rule on reflections, `q(x)=0` transvections,
  and the kernel/image of `A_M → A_N`.
* `s5_sn.py` — the spinor-norm verdicts, generator by generator.
* `s6_repair.py` — the repaired set of 46 generators attached to `N`'s own isotropic
  vectors `e1, f1, e2, 2f2`: isometry of `N`, triviality on `A_N`, `O⁺(N)` membership.
