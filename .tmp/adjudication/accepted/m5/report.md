# Adjudication: the stable-kernel generation gap for N = U ⊕ U(2) ⊕ E8(−2)

Member m5, direction d2 (dual-lattice algebra + hypothesis verification).
Everything labelled **[verified]** was computed or proved here; **[quoted]** is second-hand
and unverified from this VM.

Lattices and conventions. U = ⟨p,q⟩, (p,q) = 1; U(2) = ⟨a,b⟩, (a,b) = 2; E8(−2) = the E8 root
lattice scaled by −2 (Gram = −2·Cartan(E8), det 2⁸). N = U ⊕ U(2) ⊕ E8(−2), det N = 2¹⁰,
A_N = N^∨/N, q_N(x) = (x,x) mod 2. O⁺(N) = ker(spinor norm θ : O(N⊗R) → R*/R*²).
Scripts (this directory): `h1_embed.py`, `h1b_glue.py`, `h2_model.py`; logs `model_log.txt`.

Sources. Vendored text, project `p-165a6922…`, `references/vendor/arxiv/2302.01679/
Enriques_compu_rev.tex`: **1428–1430** (Lemma `sublattice_approx_model`), **1432** (Eichler's
criterion, `[eichler, §3]`), **1437–1440** (U+U ≅ M₂,₂(ℤ) determinant form; SL₂² ⊂ Orth(U+U);
4 generators), **1442–1446** (Eichler transvections E_{e_i,x}, four canonical isotropic vectors
of the two hyperbolic planes), **1448–1451** (Scattone Prop 3.7.3; 4(n−1) transvections; "4n
together"), **1456–1457** ("The group provided by the Eichler algorithm acts trivially on the
discriminant"), **1463–1475** (descent theorem: L′ ⊂ L ⟹ approximate model), **1468–1470**
(Alg 1 = *stabilizer* S of L′ under Ap(L); Alg 3 = right coset decomposition), **1477–1482**
("any lattice cU + dU + W … via the following embedding in U + U + W: (x₁,x₂,y₁,y₂,w) ↦
(c x₁, x₂, d y₁, y₂, w)"), **1490–1510** (general existence theorem by the same scaling descent).
Statement numbers for the criterion: Eichler *Satz 10.4* (1952), Scattone *Prop. 3.7.3*
(Mem. AMS 70 (1987) no. 374), Freitag–Hermann *Lemma 4.4*, Gritsenko–Hulek–Sankaran
(arXiv:0810.1614) *Prop. 3.3* — **[quoted]** from arXiv:2508.12624 §1, which also states the
criterion's hypothesis as "a quadratic lattice **containing two hyperbolic planes**" and says
the criterion "determines when two primitive vectors … are equivalent under a canonical
subgroup of the orthogonal group". None of the four primary texts was readable from here:
Scattone's Memoir and Eichler's book are not reachable, so **their exact hypotheses are
unverified**; what is verified is that the lattice hypothesis used by DSH is the shape U+U+L
(1429) and by Ma is "two hyperbolic planes".

---

## H1 — Exact embedding. **PROVED (verified).**

**Theorem.** (i) N = 1·U + 2·U + E8(−2) embeds in M = U ⊕ U ⊕ E8(−2) by
T : (x₁,x₂,y₁,y₂,w) ↦ (x₁,x₂,2y₁,y₂,w), i.e. a ↦ 2p₂, b ↦ q₂, and [M : N] = 2 exactly.
This is *verbatim* DSH's own embedding at **1481** with c = 1, d = 2, W = E8(−2) (**1477–1479**).
(ii) The gluing class is h = [a/2] = [p₂] ∈ A_N, q_N(h) = 0, and
A_M = A_{E8(−2)} = (ℤ/2)⁸ → H^⊥/H ⊆ A_N is an isometry of discriminant forms; hence
A_N = (H^⊥/H) ⊕ ⟨h⟩ = (ℤ/2)¹⁰ with q_N the **split** form, A_N ≅ discriminant form of U(2)⁵.
(iii) |O(A_N)| = |O⁺₁₀(2)| = 2²¹·3⁵·5²·7·17·31 = 46998591897600, reproducing the repo's value.

*Verified numbers* (`h1_embed.py`, `h1b_glue.py`): TᵗG_M T = G_N ✓; |det T| = 2 ✓;
det N = 1024 ✓; 2N^∨ ⊆ N ✓ (A_N is 2-elementary); dim_{F₂}A_N = 10 ✓; the polar form has rank
10 ✓; q(x+y) = q(x)+q(y)+b(x,y) ✓; #{q = 0} = 528 = 2⁹ + 2⁴ ✓ (the split count); an explicit
splitting into 5 hyperbolic pairs was found ✓; |O| of the split form on (ℤ/2)² resp. (ℤ/2)⁴
computed by brute force over GL₂(𝔽₂), GL₄(𝔽₂) = 2 and 72, fixing the normalisation
|O^ε_{2m}(2)| = 2^{m(m−1)+1}(2^m − ε)∏_{i<m}(2^{2i} − 1), which gives 40320 = |O⁺₆(2)| for m = 3
and 46998591897600 for m = 5 ✓. Gluing: |A_M| = 256, |H^⊥| = 512, |H^⊥/H| = 256 = |A_M| ✓;
q_N(φ(z)) = q_M(z) on a spanning set ✓; φ(A_M) ⊆ H^⊥ ✓. Injectivity of φ is immediate:
y ∈ M^∨ with y ∈ N forces y ∈ M because N ⊂ M.

*Consequence for the route.* The embedding exists and is *exactly* the one the paper itself
writes down — but it has index 2, so N is **not primitive** in M, and M is not unique: every
isotropic order-2 class of A_N gives another index-2 overlattice. Nothing in **1477–1510** is
used by DSH for anything but the *approximate model* (orbit classification), never for
generators of a kernel.

## H2 — Which subgroup is induced. **PROVED for what the text supports; the rest unproved.**

The text's descent is its own Theorem, **1463–1475**: for L′ ⊂ L with an approximate model of L,
"we can compute the **stabilizer S of L′ under Ap(L)** by Alg 1 and this gets us an approximate
subgroup Ap(L′)" (**1468**), then Alg 3 gives the right coset decomposition of Ap(L) under S
(**1469–1470**), and the coset representatives are used **only** to transfer vector-orbit
representatives: "consider all the elements of the form g_j x_i and keep the ones that are
contained in L′" (**1473**). Hence

> E′ = **Stab_E(N)|_N = E ∩ O(N)** — the restriction of the stabiliser. Not all of E, not a
> conjugate, and Alg 3's coset representatives play no role in E′ whatsoever.

*Verified* (`h2_model.py`, in Scattone's own M₂,₂(ℤ) determinant model, cf. **1437**), rank-4
model D = (M₂(ℤ), det) ≅ U+U ⊃ L = {A : A₁₂ even} ≅ U+U(2) (the exact rank-4 shadow of N ⊂ M):

* Stab_{SL₂(ℤ)²}(L) = Γ⁰(2) × Γ⁰(2) = {(g,h) : g₁₂ ≡ h₁₂ ≡ 0 (mod 2)}, index 3·3 = **9**.
* **None** of the four quoted SL₂(ℤ)² generators (S, T in each factor) preserves L. So the
  "4 generators from SL₂(ℤ)²" of **1440, 1450** are *not isometries of N*; the stabiliser needs
  product words.
* Of the 4(n−1) = 12 transvections F_{e_i,v} for the four canonical isotropic vectors
  E₁₁,E₂₂,E₁₂,E₂₁ of D (**1444–1449**) and a ℤ-basis of e_i^⊥ ∩ M, exactly **8 preserve L and 4
  do not** (the failures are e = E₁₁,E₂₂ with x = E₁₂ ∉ L, and e = E₁₂ with x = E₁₁,E₂₂).
* Divisibilities in D: div(E₁₁) = div(E₂₂) = div(E₁₂) = div(E₂₁) = 1 ✓ (needed for the ambient
  "acts trivially on the discriminant" statement, see H4).

So "the group generated by the quoted generators acts trivially on the discriminant, hence
descends to N" is **false as stated**: most of the generators do not act on N at all.

## H3 — Equality with ker(O⁺(N) → O(A_N)). **Containment: proved. Equality: NOT established, and the criterion that would give it does not apply to N.**

**(a) Containment E′ ⊆ ker(O(N) → O(A_N)): verified on the model (all named generators and 1076
stabilising block maps), proved for the SL₂ part.**
Every element of Γ⁰(2)×Γ⁰(2) acts trivially on A_L = ⟨[E₁₂],[E₂₁/2]⟩: for
g = [[a,2b],[c,d]], h⁻¹ = [[s,−2q],[−r,p]] (a,d,p,s all odd, det = 1) one computes
gE₁₂h⁻¹ = −arE₁₁ + apE₁₂ − crE₂₁ + cpE₂₂ ≡ [E₁₂] and ½gE₂₁h⁻¹ = bsE₁₁ − 2bqE₁₂ − dqE₂₂ +
(ds/2)E₂₁ ≡ [E₂₁/2] (mod L). Verified: all 6 stabiliser generators and 200 random elements of
Γ⁰(2)² preserve L and fix A_L pointwise ✓. All 8 preserving ambient transvections also fix A_L ✓.
Broader check (`search_stab.py`): of the two cosets of O(D) (A ↦ uAv⁻¹ and A ↦ uA^Tv⁻¹, u,v in
SL₂(ℤ) of word length ≤ 4, 68 elements each), **1076 stabilising pairs** were found and **every one
of them acts trivially on A_L** (0 exceptions). The mechanism: any g with g(L) = L satisfies
g(α) = α for α = [E₁₂] and A_L is spanned by α, β = [E₂₁/2]; then q forces the second class to be
fixed too, because q(α+β) = −½ while q(α+β+α) = −1 in ℚ/2ℤ, so β ↦ β+α is excluded. Whether this
holds for *all* g ∈ O(D) with g(L) = L (rather than the tested words) I flag as verified but not
proved here; member m7 (direction d8, finding f2) asserts the general statement by a parity
argument on D/2D, which is consistent with my computation.

**(b) The U(2)-worry in the question is unfounded.** Lemma (**proved, unconditional**): for any
even lattice N, e ∈ N isotropic and x ∈ N ∩ e^⊥,
  τ_{e,x}(v) = v + b(v,e)x − b(v,x)e − ½(x,x)b(v,e)e
lies in O(N) and in ker(O(N) → O(A_N)). Indeed b(v,e), b(v,x) ∈ ℤ and (x,x)/2 ∈ ℤ for v ∈ N,
and b(y,e), b(y,x) ∈ ℤ **by definition of the dual lattice** for y ∈ N^∨. The quantity that is
½ℤ on a U(2)-summand is b(e/2, N) (i.e. e/2 ∈ N^∨ ∖ N), not b(e, N^∨) — so divisibility of e
never breaks the argument. Verified on L: e = 2E₁₂ (div_L(e) = 2) with x = E₁₁+E₂₂ and x = E₁₁,
e = E₁₁ with x = 2E₁₂+E₂₁, e = E₂₁ with x = E₁₁+E₂₂ — all in O(L), all trivial on A_L ✓.

**(c) Equality: not established, and here is the decisive obstruction.**
**Theorem (proved).** *N contains no sublattice isometric to U ⊕ U.* Proof: U ⊕ U is unimodular,
hence primitive (its saturation M̄ satisfies det M̄ = ±1/[M̄ : U⊕U]² ⟹ index 1), hence
N = (U⊕U) ⊥ K with rank K = 8 and A_N ≅ A_K. But A_K = ℤ⁸/G_Kℤ⁸ has at most 8 elementary
divisors, whereas A_N = (ℤ/2)¹⁰ needs 10 — verified: dim_{F₂}(A_N/2A_N) = 10 (`h1_embed.py`).
∎ Consequently the Eichler criterion in each quoted form (**1429** U+U+L; Scattone 3.7.3;
Eichler Satz 10.4; FH 4.4; GHS 3.3 — all for lattices **containing two hyperbolic planes**)
**does not apply to N**. It applies to M, not to N, and there is no theorem transporting the
transitivity statement along the index-2 scaling embedding of **1481**.

Useful positive structural fact (**proved**): ker(O(N) → O(A_N)) ⊆ O(N) ∩ O(M). Because
M ⊆ N^∨ (N ⊂ M, both integral), M/N ⊆ A_N is a subgroup, and g trivial on A_N forces
g(M/N) = M/N, i.e. g(M) = M. So the descent produces exactly the right *kind* of group — the
gap is generation, not containment.

**(d) The reflection alternative is refuted on this N.** Norms in U(2) are 4αβ ≡ 0 (mod 4) and in
E8(−2) are −2·(even) ≡ 0 (mod 4), so the norm-±2 vectors of N are exactly ±p±q ∈ U. The
reflections they define generate a group of order **4** (computed closure on the model: ±I, ±swap
on the U summand, identity on U(2) ⊕ E8(−2)). So "reflection generation by norm-(±2) vectors"
cannot generate a kernel containing a lattice in O(2,10).

## H4 — Spinor norms. **PROVED (verified): every named generator lies in O⁺.**

* Every Eichler transvection τ_{e,x} with (x,x) ≠ 0 equals σ_y σ_x for y = x − ((x,x)/2)e, and
  (y,y) = (x,x), so θ(τ_{e,x}) = (x,x)² ∈ (R*)² ⟹ τ_{e,x} ∈ O⁺. Verified exactly (rational
  matrices) for F_{E₁₁,2E₁₂+E₂₁} ((x,x) = −4), F_{2E₁₂,E₁₁+E₂₂}, F_{E₂₁,E₁₁+E₂₂} ((x,x) = 2):
  the identity σ_y σ_x = F holds and θ = (x,x)² ✓. The (x,x) = 0 case is unipotent, hence in the
  identity component, hence in ker θ.
* Every SL₂(ℤ)² block map lies in O⁺: SL₂(R)² = Spin(2,2) → SO(D⊗R) is connected, so its image
  lies in the identity component of O(D⊗R) ⊂ ker θ (θ is a continuous homomorphism onto the
  discrete group R*/R*²). Verified: the parabolics satisfy (M − 1)² = 0 (unipotent) ✓.
* Contrast (so that O⁺ really is a proper condition): θ(σ_v) = (v,v) mod squares, so a
  reflection σ_v lies in O⁺ iff (v,v) > 0. In particular σ_{p−q} (norm −2, div 1) lies in
  ker(O(N) → O(A_N)) **but not in O⁺(N)**. Also −1 ∈ O⁺(N) since disc N = 2¹⁰ ≡ 1 mod squares.
* Verdict: the O⁺ selection is *not* an obstruction to the route; every generator DSH lists, and
  every transvection of N, is already in O⁺.

---

## Sharpest maintained statements (what DOES hold on this N)

1. **T(N) ⊆ ker(O⁺(N) → O(A_N))**, where T(N) = ⟨τ_{e,x} : e ∈ N primitive isotropic,
   x ∈ N ∩ e^⊥⟩. Proved (Lemma H3(b) + H4). This is unconditional and needs no hypothesis on N
   whatsoever; it covers e in the U(2) summand (div e = 2) as well.
2. **ker(O(N) → O(A_N)) ⊆ O(N) ∩ O(M)** for the index-2 overlattice M = U ⊕ U ⊕ E8(−2)
   (proved, H3(c)). So any generating set of the kernel consists of isometries of N preserving M.
2′. **Γ_N(2) := ker(O(N) → O(N/2N)) ⊆ ker(O(N) → O(A_N))** (proved: for y ∈ N^∨, 2y ∈ N, so
   g(2y) − 2y ∈ 2N and hence g(y) − y ∈ N by torsion-freeness). This is a *provable* large supply
   of kernel elements, strictly bigger than T(N) in general, but again not shown to generate.
3. **Conditional generation statement**: if one proves, for N (or for a lattice of the shape
   U ⊕ U(m) ⊕ L), the Eichler-type transitivity of T(N) on primitive isotropic/Eichlerian
   vectors, *then* T(N) = ker(O⁺(N) → O(A_N)). That transitivity is exactly what the four quoted
   statements give for lattices containing U ⊕ U, and it is unavailable for N.
4. **Generator counts.** DSH's recipe gives 4n = **48** generators at rank n = 12 (4 from SL₂² +
   4(n−1) = **44** transvections; **1450–1451**), which matches the repo's "44 candidate
   transvections" (`TRAPS.md:969`). On N itself the same recipe would need isotropic vectors *of
   N* (p, q from U with div 1; a, b from U(2) with div 2) with 11 basis transvections each; the
   resulting 44 elements are transvections of N only when their x is taken in N (not in M ∖ N),
   and no theorem says they generate. A *finite* generating set of ker(O⁺(N) → O(A_N)) exists
   abstractly (it is a lattice in O(2,10), real rank 2, hence finitely generated) but is not
   produced by any statement in the quoted text.

## Cross-checks against the text's own definitions, and the precise textual claim being adjudicated

* **315–318** defines ṼO(N) as "the group of all elements in O(N) acting trivially on the
  discriminant D(N) = N^∨/N" and sets ṼO⁺(N) := O⁺(N) ∩ ṼO(N) — exactly the group of the
  question, ker(O⁺(N) → O(A_N)).
* **320–321** justifies that ṼO⁺(N) has index 2 in ṼO(N) with "the reflection with respect to a
  vector of length 2 in the summand U of N gives an element in ṼO(N) with real spinor norm −1".
  **Verified here:** σ_{p+q} ((p+q,p+q) = 2) and σ_{p−q} ((p−q,p−q) = −2) are both in ṼO(N) since
  div(p±q) = 1 and σ_v(y) − y = b(y,v)v; θ(σ_{p+q}) = +1, θ(σ_{p−q}) = −1. So the sentence is
  realised with "length 2" read as |(v,v)| = 2 and the *standard* spinor norm θ(σ_v) = (v,v) mod
  squares. Member m7 reads the same sentence as evidence for the det-twisted convention
  θ_B = det·θ_A (d8 f4); both readings fit the words of 320–321, and I flag the convention as
  **not settleable from lines 315–321 alone**. The H4 verdict is convention-independent: all named
  generators are in O⁺ under both (m7 verified this independently).
* **1513–1520** is the sentence the adjudication is really about: "Lemma … provides an approximate
  model for lattices of the form U+U+L … The lattices that we are going to consider are not
  necessarily even nor admit a decomposition U+U+L but we can find an approximate model for them …
  we are in the fortunate situation that the lattice U + U(2) + E8(−2) can be trivially embedded
  into U + U + E8(−2) by our previous remark and **so no additional work is needed**" (1519–1520).
  Read in context (1513–1515), "no additional work is needed" is a statement about *approximate
  models / orbit representatives*, obtained through the stabiliser descent of 1463–1475. (The
  paper's one explicit generation claim is elsewhere, **1556–1570**: *Orth(s)* builds "a generating
  set of Orth(L)" from an approximate model plus stabilisers computed by **Alg 1** — a generating
  set of Orth(L), not of ṼO(L), and again through a stabiliser of an overlattice, `L_{v_1} = v^⊥ +
  ℤv` at 1561–1564. So the same stabiliser mechanism is used for Orth(L) on an overlattice, never
  for ṼO⁺(N) on N.) It is
  **not** a statement about ṼO⁺(N): nothing between 1428 and 1520 mentions generating ṼO(N), and
  1456–1457's "acts trivially on the discriminant" is about the ambient U+U+L. So the H3 claim is
  an *inference the text does not make*, and the sharper of my two obstructions — N contains no
  U ⊕ U (proved in H3(c)) — shows the criterion it would have to come from is inapplicable to N.

* Numerical cross-check of the A_N computation against the paper's own data: my #{x ∈ A_N : q(x) = 0}
  = 2⁹ + 2⁴ = **528** coincides with the count of 0-dimensional cusps of ṼM_En quoted at **1168**
  ("has 528 0-dimensional cusps"). I do not claim the identification of the two counts; it is a
  consistency signal that my q_N is the right form.

## Verdicts

| | verdict |
|---|---|
| **H1** | **Proved (verified).** Embedding exists, index exactly 2, is DSH's own map at 1481 with c=1,d=2; gluing class h = [a/2], q(h) = 0, A_M = (ℤ/2)⁸ ≅ H^⊥/H isometrically; A_N split, \|O(A_N)\| = 46998591897600 reproduced. Not primitive. |
| **H2** | **Proved: E′ = Stab_E(N) = E ∩ O(N)** (Alg 1; Alg 3 is orbit bookkeeping only, 1468–1473). **Refuted:** that the quoted generators themselves act on N — none of the 4 SL₂ generators does, and 4 of 12 transvections do not (rank-4 model). Stab_{SL₂²} = Γ⁰(2)², index 9. |
| **H3** | **Containment proved** (E′ ⊆ ker; Lemma for all transvections of N; the ½ℤ-worry is unfounded; 1076 stabilising block maps tested, all trivial). **Equality refuted as a consequence of the quotations**: N contains no U ⊕ U (proved), so the two-hyperbolic-plane criterion cannot be applied to N; nothing in 1428–1510 addresses kernel generation. Structural facts: ker ⊆ O(N) ∩ O(M); the norm-(±2) reflection alternative generates only a group of order 4. |
| **H4** | **Proved (verified): all named transvections and all SL₂(ℤ)² block maps lie in O⁺** (θ(τ) = (x,x)² for (x,x) ≠ 0; unipotent/identity-component otherwise; SL₂(R)² connected). The O⁺ selection is not the obstruction; σ_{p−q} ∈ ker ∖ O⁺ shows O⁺ is genuinely a proper condition. |

## What is *not* verified here
Scattone Prop. 3.7.3 and Eichler Satz 10.4 themselves (texts unreachable): their hypotheses are
taken second-hand from DSH **1481** and from arXiv:2508.12624 §1. **Kneser's** generation theorems
for 2-elementary lattices are *not* verified from here either and no claim is made from them; in
particular the H3 verdict does not rest on Kneser. The equality of H3 is *open*,
not refuted, as a mathematical statement; what is refuted is that the quoted text supports it.
