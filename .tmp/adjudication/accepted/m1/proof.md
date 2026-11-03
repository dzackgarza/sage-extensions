# Adjudication: Scattone 3.7.3 / Eichler's criterion and ker(O⁺(N) → O(A_N)) for N = U ⊕ U(2) ⊕ E8(−2)

Member m1, swarm `smvzznqcw`, direction d4 (root-system / reflection direction).
Every claim below is tagged **[proved]**, **[quoted]** (source read, with location), or
**[unverified from here]**. Machine checks: `scripts/verify.py` → `scripts/verify.out`.

---

## 0. Conventions, and what the two sources actually say

`(·,·)` is an integral bilinear form on a Z-lattice, `q(x) = (x,x)/2` for even lattices, so
`(v,v)` and `q(v)` differ by a factor 2; I give both wherever the distinction matters.
`U = Ze ⊕ Zf` with `(e,e) = (f,f) = 0`, `(e,f) = 1`; `U(2)` is the same Z² with the form
multiplied by 2; `E8` = Z⁸ with Gram = Cartan matrix `C` (so `(r,r) = 2`, `q(r) = 1` on roots,
E8 unimodular); `E8(−2)` = the same Z⁸ with Gram `−2C`.
`D(L) = L^∨/L` with discriminant form `q_L`.

**Source A** (definitions; GHS = Gritsenko–Hulek–Sankaran, arXiv:0810.1614v1, §1, eq. (2)) —
**[quoted]**, pdftotext of the arXiv PDF, `scratch/ghs.txt` lines 95–127:
* `O~(L) = ker(O(L) → O(D(L)))` ("stable orthogonal group");
* `O⁺(L) = O(L) ∩ ker sn_R`, `O~⁺(L) = O~(L) ∩ O⁺(L)`, `O′(L) = SO(L) ∩ ker sn_Q`
  ("spinorial kernel"), with `sn_K(σ_{v₁}…σ_{v_m}) = Π (−(v_i,v_i)/2)(K^×)²`.
So the problem's `ṼO(N)` = `O~(N)` and "real spinor kernel" = `O⁺(N)`, and
`ker(O⁺(N) → O(A_N)) = O~⁺(N)` **[quoted]**, and "reflections in `(−2)`-vectors lie in `O~⁺(L)`" **[quoted]** (same page).

**Source B** (the vendored text, `references/vendor/arxiv/2302.01679/Enriques_compu_rev.tex`
of project p-165a6922b36b40789ddc90db34bb23c7, read directly):
* 280/283: `N = U + U(2) + E_8(-2)`, "`U(2)` and `E_8(-2)` means that the bilinear forms are multiplied by `2`".
* 1347: **Alg 3** "Compute the right cosets of `G∩GL_n(Z)` in `G`"; 1349: **Alg 1** "Compute a generating set of the intersection `G ∩ GL_n(Z)`".
* 1428–1430: Lemma ("if `L` is an integral non-degenerate even lattice, then `U+U+L` has an approximate model").
* 1436: "we can take a suitable subgroup of the group `Orth(U+U)` together with the Eichler transvections".
* 1442–1445: "the Eichler transvections `E_{e_i,x}` … for `e_i` with `1≤i≤4` one of the 4 canonical isotropic vectors coming from the two hyperbolic planes `U` and `x` a vector orthogonal to `e_i`".
* 1446–1447: "`E_{e,x}E_{e,y} = E_{e,x+y}` for `e` isotropic and `x,y` orthogonal to `e`".
* 1448–1451: "According to [Proposition 3.7.3]{scattone} we simply need the generators of `SL_2(Z)^2` and the transvections `E_{e_i,v_{i,j}}` … forming a Z-basis of `e_i^⊥`. Thus, if the dimension of `U+U+L` is `n`, we need 4 generators … and `4(n−1)` from the transvections and so `4n` together."
* 1456–1461: "**The group provided by the Eichler algorithm acts trivially on the discriminant.** For a case such as `U+U+E_8(-2)` this gets us `2^8` orbit representatives. By adding the isometries of the `E_8` component … `W(E_8)` has 3 orbits in its action on `E_8/2E_8`, their sizes being `1`, `120` and `135`."
* 1463–1475: Theorem (descent) + proof: "We can compute **the stabilizer `S` of `L'` under `Ap(L)`** by Alg 1 and this gets us an approximate subgroup `Ap(L')`. By using Alg 3 we compute the right coset decomposition of `Ap(L)` under `S` with coset representatives `g_1,…,g_m`."
* 1477–1482: "any lattice `cU + dU + W` … via the following embedding in `U+U+W`: `(x₁,x₂,y₁,y₂,w) ↦ (c x₁, x₂, d y₁, y₂, w)`".
* 1519–1520: "the lattice `U + U(2) + E_8(-2)` can be trivially embedded into `U + U + E_8(-2)` by our previous remark **and so no additional work is needed**".
* 1169–1171: "`528` 0-dimensional cusps … Under the group `Orth⁺(F₂)` the `528` … decompose into two orbits, one of length `527` and one of length `1`".

**Source C** (the published form of the cited criterion; GHS arXiv:0810.1614v1, §3.3, pp. 10–13)
— **[quoted]** (`scratch/ghs.txt` lines 504–608), see §3.4 below for its exact hypotheses.
Scattone's memoir itself (Mem. AMS 70–374, 1987, bibitem at tex:1938–1940) is **[unverified from here]**:
I found it only as a catalogue entry (AMS bookstore / DOI 10.1090/memo/0374); no text was reachable,
so every statement I attribute to "Proposition 3.7.3" is attributed to the *quote* at tex:1448,
not to the memoir. Eichler's `[Eic]` (Springer 1952, §3 / §10) is likewise **[unverified from here]**.

---

## 1. H1 — the exact embedding. **Verdict: PROVED** (index 2; and N splits as U⊕U⊕L for *no* even L).

Work in the Q-space `V = P₁ ⊥ P₂ ⊥ W` with coordinates `(a₁,b₁,a₂,b₂,e₁…e₈)`, `P_i` hyperbolic
with basis `(a_i,b_i)`, `W = E8 ⊗ Q`. Let
`M = Za₁+Zb₁+Za₂+Zb₂+E8(−2)` and `N = Za₁+Zb₁+Z(2a₂)+Zb₂+E8(−2)`. Then `N ≅ U ⊕ U(2) ⊕ E8(−2)`
(because `q|_{⟨2a₂,b₂⟩}` has Gram `[[0,2],[2,0]]`), signature (2,10), and `N ⊂ M`.

**(a) Index.** `[M:N] = 2` (the basis matrix is `diag(1,1,2,1,…,1)`, det 2). The map
`(x₁,x₂,y₁,y₂,w) ↦ (x₁,x₂,2y₁,y₂,w)` of tex:1481 with `c=1,d=2` is an **isometry of N onto a
sublattice of index 2 of M**, not onto M. **[proved]** (and verified: `det G = 256 = |D(M)|`,
`det G_N = 1024 = |D(N)|`).

**(b) Duals and discriminants.** `D(M) = ½E8/E8 ≅ (Z/2)⁸`, `D(N) ≅ (Z/2)¹⁰`, and
`N ⊂ M ⊂ M^∨ ⊂ N^∨` with
`[M:N] = 2`, `[M^∨:M] = 2⁸`, `[N^∨:M^∨] = 2` (so `2 · 2⁸ · 2 = 2¹⁰ = [N^∨:N]`).
Moreover the extra two layers are the **U(2)-plane's discriminant** and they are *orthogonal to* `D(M)`:
`D(N) = D(U(2)) ⊥ D(M)` as quadratic spaces, `q_N = q_{U(2)} ⊥ q_{E8(−2)}`, with
`q_N([a₂]) = q_N([½b₂]) = 0`, `q_N([a₂+½b₂]) = ½`, `(a₂,½b₂) = ½` on `D(N)`.
**[proved]** (verified on all 1024 classes: exactly 1024 classes, values of `2q_N` in {0}, and 528 isotropic classes).

**(c) No splitting `N ≅ U ⊕ U ⊕ L`.** If `N ≅ U⊕U⊕L` then rank `L = 8` and `D(L) = D(N)` of order
`2¹⁰`. But for an even lattice `L` the mod-2 reduction of its Gram matrix is alternating, hence
`|D(L)|₂ ≤ 2^{rank L} = 2⁸ ≤ 2¹⁰`. Contrapositive: **no such even `L` exists**. More generally for any
`N ⊂ U⊕U⊕L'` of finite index `k` we have `k² |D(L')| = |D(N)| = 2¹⁰` with `|D(L')|₂ ≤ 2⁸`, so `k ≥ 2`
and `k = 2` forces `L'` of maximal 2-discriminant. **[proved]**

**(d) Arithmetic corroboration of the target group.** `q_N` is the split (Arf 0) nondegenerate
2-elementary form of dimension 10: 528 isotropic classes `= 2⁹ + 2⁴`. Hence `D(N) ≅ D(U(2)⁵)`, and
the recursion `|O⁺(2m,2)| = (2^m−1)(2^{m−1}+1)2^{2m−2}|O⁺(2m−2,2)|` at `m=5` gives
`46998591897600 = 2²¹·3⁵·5²·7·17·31` — the value measured in the repo
(`tests/test_finite_form_groups.py:3–4,16–20`, which computes it for `D(U(2)⁵)` with the same form).
**[proved]** (my own recursion + factorization + zero count). The 528 also matches Source B 1169–1171,
and the `1, 120, 135` of tex:1461 are reproduced exactly as the `W(E8)`-orbits on `D(E8(−2))`
**[proved]** (script, third block from the end).

---

## 2. H2 — which subgroup the descent induces. **Verdict: the STABILIZER, by restriction; PROVED as a reading, and the quotations support nothing about `D(N)`.**

* The descent is stated exactly at tex:1468–1469: `Ap(L') := Stab_{Ap(L)}(L')`, computed by Alg 1
  (= `G ∩ GL_n(Z)`, tex:1349), and Alg 3 (right cosets, tex:1347) is used only to transport the
  *orbit oracle*. So for `L' = N ⊂ L = M`:

  **E′ := Stab_E(N) = E ∩ O(N), acting on N by restriction.** **[proved as a reading of 1463–1475]**

  It is *not* a conjugate, and it is *not* obtained by the Alg 3 cosets. It is a subgroup of finite
  index in `E`, since `E` acts on the finite set of index-2 sublattices of `M` (`2¹²−1` of them).

* What tex:1457 supports: for `L = U+U+L₀` the named generators *fix the lattice pointwise modulo
  itself*, so the group they generate is contained in `O~(L)` — see Lemma 1 below, which proves this
  elementarily. Scattone 3.7.3 is used in the quoted block for **generation / orbit finiteness**
  (tex:1448–1452), not for triviality on the discriminant. **[proved]**

* What the quotations do **not** support: any statement that `Stab_E(N)` acts trivially on `D(N)`.
  tex:1457 speaks of "the discriminant" of the lattice to which the Eichler algorithm is applied
  (`U+U+L`); tex:1519–1520 asserts only the *existence* of the embedding ("no additional work is
  needed"), which is a claim about the embedding, not about the action on `D(N)`. **The inference
  "trivial on `D(M)` ⇔ trivial on `D(N)`" is not made anywhere in the quoted text — and it is false**
  (§3). Whether the authors *intended* that inference is **[unverified from here]**.

---

## 3. H3 — the equality. **Verdict: REFUTED.** `E′ = Stab_E(N)` is not even contained in `O~(N)`, hence `E′ ≠ ker(O⁺(N) → O(A_N))`.

### Lemma 1 (Eichler transvections act trivially on `D(L)`). **[proved]**
Let `e,x ∈ L` with `q(e) = 0` and `(e,x) = 0`, and put
`t(e,x)(y) = y + (y,e)x − (y,x)e − q(x)(y,e)e`.
Then `t(e,x)` is an isometry of `L ⊗ Q`; for `y ∈ L^∨` one has
`t(e,x)(y) − y = (y,e)x − ((y,x) + q(x)(y,e))e ∈ L`;
hence `t(e,x) ∈ O(L)` and `t(e,x)|_{D(L)} = id`, i.e. `t(e,x) ∈ O~(L)`. If moreover `q(x) ≠ 0`
then `t(e,x) ∈ O~⁺(L)` (Lemma 3).
*Proof of the isometry:* put `u = (y,e)`, `v = (y,x) + q(x)(y,e)`; then
`t(y) = y + ux − ve` and, using `q(e) = (e,x) = 0`, 
`q(t(y)) = q(y) + u²q(x) + v²q(e) − uv(e,x) + u(y,x) − v(y,e) = q(y) + u²q(x) − q(x)u² = q(y)`. (Verified on spanning
sets; the hypothesis `(e,x) = 0` is genuinely needed: `t(a₁, b₁+a₂+r₀)` is *not* an isometry.)
This is the `⊆`-half of GHS's "we have seen that `E(L)` is a subgroup of `SO~⁺(L)`" **[quoted]**, and it
proves tex:1457 for the ambient lattice without any appeal to Scattone.

### Lemma 2 (which reflections act trivially on `D(L)`). **[proved]**
Let `v ∈ L`, `q(v) ≠ 0`, `σ_v(y) = y − (y,v)v/q(v)`.
(i) `σ_v ∈ O(L)` iff `(L,v) ⊆ q(v)Z`. (ii) Then `σ_v|_{D(L)} = id` iff `v/q(v) ∈ L`.
Consequently: for `(v,v) = ±2` (`q(v) = ±1`) every reflection is trivial on `D(L)`; for `(v,v) = ±4`
(`q(v) = ±2`) `σ_v` is trivial on `D(L)` **iff** `v ∈ 2L`. Also `sn(σ_v) = −q(v) = −(v,v)/2`, so
`(v,v) = −2 ⇒ σ_v ∈ O~⁺`, while `(v,v) = +2` gives `sn = −1` and `(v,v) = ±4` gives `sn = ∓2`.

### The counterexample. **[proved]**
Take `e = a₂` (a canonical isotropic vector of the ambient `U+U`, tex:1444) and `x = r₀`,
a root of `E8(−2)`, `(r₀,r₀) = −4`, `q(r₀) = −2`. Then `(e,x) = 0`, `q(e) = 0`, and
`div_M(a₂) = 1`, so `t(a₂,r₀) ∈ E(M) = ⟨t(e,a) : e,a ∈ M, (e,e) = (e,a) = 0, div(e) = 1⟩`
(GHS §3.3) — i.e. it is one of the paper's own named generators (tex:1448–1449, with `a₂` an `e_i`
and `r₀` a member of a Z-basis of `e_i^⊥ ∩ M`, since `E8(−2)` is a direct summand of `a₂^⊥ ∩ M`).

1. `t(a₂,r₀)` **preserves M**, trivially: it acts as the identity on `D(M)` (Lemma 1).
2. `t(a₂,r₀)` **preserves N**: on the basis of `N` it sends
   `a₁ ↦ a₁`, `b₁ ↦ b₁`, `2a₂ ↦ 2a₂`, `b₂ ↦ b₂ + r₀ + 2a₂ ∈ N`, and `w ↦ w + 2(w,r₀)_{E8}·a₂ = w + k·(2a₂) ∈ N`
   for `w ∈ E8(−2)`, `k = (w,r₀)_{E8} ∈ Z`; and `t(a₂,−r₀)` is its inverse
   (tex:1446 additivity). Hence `t(a₂,r₀) ∈ Stab_E(N) = E′`.
3. It acts **non-trivially on `D(N)`**: `½b₂ ∈ N^∨` (`(½b₂, 2a₂) = 1`, `(½b₂,b₂) = 0`) and
   `t(a₂,r₀)(½b₂) − ½b₂ = ½r₀ + a₂ ∉ N` (coefficient of `a₂` is odd). So `t(a₂,r₀) ∉ O~(N)`.
4. It lies in `O⁺`: `t(a₂,r₀) = σ_{r₀} σ_{r₀−2a₂}` and `sn = q(r₀)·q(r₀−2a₂) = (−2)(−2) = 4 ≡ 1`.

So `E′ ⊄ O~(N)` and, since `ker(O⁺(N) → O(A_N)) = O~⁺(N) ⊆ O~(N)`,

> **`E′ ≠ ker(O⁺(N) → O(A_N))`; indeed `E′ ∩ O~⁺(N) ≠ E′`.** The claim "the group provided by the
> Eichler algorithm acts trivially on the discriminant", transferred from `M` to `N` (the reading
> needed for "no additional work is needed", tex:1519–1520), is **false**.

Remarks. (i) This is exactly the obstruction the question conjectured: `(a₂, N^∨) = ½Z` (verified:
`(a₂,½b₂) = ½`) — the two extra layers `M/N ≅ Z/2` and `N^∨/M^∨ ≅ Z/2` sit orthogonally to `D(M)`
(§1b), so triviality on `D(M)` says nothing about them. (ii) Nothing goes wrong on the *approximate
model* statement of tex:1463–1475, which only needs `Stab_E(N)`; what fails is the *discriminant*
argument used to reduce `2¹⁰` to `2⁸` orbit representatives (tex:1457–1460) when applied to `N`.
(iii) The repo's own polarised-case numbers (tex:1164–1166: stabilizer images of index `527` and
`23715`) are of the same nature: images of stabilizers in `O(D(N))` are proper subgroups in general.

### 3.4 Hypothesis audit of the cited theorem (the part the adjudication demands). **[quoted]**
The published form of the criterion the vendored text cites (it cites `[Ei, §3]` for "Eichler's
criterion" at tex:1432 and `[scattone, Prop 3.7.3, §3.7]` at tex:1443,1448) is GHS §3.3:

* `div(l)` = positive generator of `(l,L)`; "one can complete an isotropic element `e` to an
  integral isotropic plane `U = Ze ⊕ Zf ⊂ L` if and only if `div(e) = 1`. We call such an isotropic
  vector **unimodular**. For a unimodular isotropic vector `e` we have `L = U ⊕ L₁`."
* `E(L) := ⟨{t(e,a) | e,a ∈ L, (e,e) = (e,a) = 0, div(e) = 1}⟩`.
* **Prop 3.3**: "Let `L = U ⊕ U₁ ⊕ L₀`, where `U = Ze ⊕ Zf`, `U₁` is the second copy of the integral
  hyperbolic plane in `L` and `L₁ = U₁ ⊕ L₀`." Then (i) [Eichler criterion, `[Ei, Satz 10.4]`]
  primitive `u,v` with `(u,u) = (v,v)`, `u* ≡ v* mod L` are `E_U(L₁)`-equivalent;
  (ii) `E(L) = E_U(L₁)`; (iii) `O(L) = ⟨E_U(L₁), O(L₁)⟩`; (iv) for a `(−2)`-vector `r`,
  `σ_r = ρ·σ_{e−f}` with `ρ ∈ E_U(L₁)`.
* **Prop 3.4**: "Let `L = U ⊕ U₁ ⊕ L₀` be an even lattice with two hyperbolic planes, such that
  `rank₃(L) ≥ 5` and `rank₂(L) ≥ 6`. Then `SO~⁺(L) = O′(L) = E(L) = E_U(L₁)`" and
  `O~⁺(L) = ⟨Γ_J(L₀), σ₁⟩`.
* **Theorem 1.1** (Kneser, `[Kn1, Satz 4]`): for even `L` with Witt index ≥ 2 over R, representing
  `−2`, `rank₃(L) ≥ 5`, `rank₂(L) ≥ 6`: `O′(L)` is generated by the products `σ_aσ_b` of `(−2)`-reflections.
* `rank_p(L)` = max rank of a sublattice with `det` coprime to `p`.

Applicability to our lattices (**proved** here, from the definitions):
* `M = U⊕U⊕E8(−2)` has the two hyperbolic planes of Prop 3.3/3.4 **[proved]**, but
  `rank₂(M) = 4 < 6`: the mod-2 Gram form of `M` has rank 4 (only the two `U`'s contribute;
  `E8(−2)/2` is totally isotropic and radical), and `U⊕U ⊂ M` has `det = 1`. Hence
  **Prop 3.4 does not apply to M**; only **Prop 3.3(ii),(iii)** do, giving
  `O(M) = ⟨E_U(U⊕E8(−2)), O(U⊕E8(−2))⟩` and `E(M) = E_U(U⊕E8(−2))`.
* `N = U⊕U(2)⊕E8(−2)` does **not** have two hyperbolic planes: for `0 ≠ e ∈ N ∩ U(2)` isotropic,
  `div_N(e) = 2` (e.g. `e = 2a₂`, `(2a₂,b₂) = 2`), so `e` is *not* unimodular and cannot be completed
  to a `U` inside `N`. Also `rank₂(N) = 2 < 6`, `rank₃(N) = 12 ≥ 5`. Hence **no part of Prop 3.3,
  Prop 3.4 or Kneser's Theorem 1.1 applies to N** — in particular the "reflection generation" route
  is unavailable for lack of `rank₂ ≥ 6`, and the two-plane generation route for lack of a second
  hyperbolic plane.

---

## 4. H4 — spinor norms of the named generators. **Verdict: all named generators lie in `O~⁺` of the ambient lattice; reflections in `(v,v) = ±4` vectors do not; and the H3 failure survives inside `O⁺`.**

### Lemma 3. **[proved]**
Let `q(e) = 0`, `(e,x) = 0`, `q(x) ≠ 0`. Then `q(x+q(x)e) = q(x)` and
`t(e,x) = σ_x ∘ σ_{x+q(x)e}`, so `sn(t(e,x)) = (−q(x))(−q(x)) = q(x)² ∈ Q^{*2}` and
`t(e,x) ∈ O⁺(L)`. If `q(x) = 0`, use tex:1446 additivity with any `z ∈ L` such that `q(z) ≠ 0` and
`(z,e) = (z,x) = 0`: `t(e,x) = t(e,x+z)t(e,z)^{−1}` gives `sn = q(x+z)²/q(z)² ≡ 1` again (such a `z`
exists in every case used here, e.g. `z = r₀`). **Hence every named Eichler transvection lies in
`O~⁺`** (Lemma 1 + Lemma 3), consistent with GHS's `E(L) ⊆ SO~⁺(L)` **[quoted]**.

### Block maps. **[proved]**
In the determinant model (`X ↦ A X C^{ad}` on `M_{2,2}(Z)`, tex:1437–1439) with
`a₁ = E₁₁`, `b₁ = E₂₂`, `a₂ = E₁₂`, `b₂ = −E₂₁`, the four elementary block matrices are *single*
Eichler transvections:
`A=[[1,1],[0,1]]` left `= t(a₁,a₂)`, `A=[[1,0],[1,1]]` left `= t(b₂,b₁)`,
`A=[[1,1],[0,1]]` right `= t(a₂,b₁)`, `A=[[1,0],[1,1]]` right `= t(a₁,b₂)` (all with `q(x) = 0`),
hence in `E(U⊕U) ⊆ O~⁺(U⊕U) ⊆ O~⁺(M)`. Note they do **not** individually preserve `N`
(e.g. `t(a₁,a₂)(b₁) = b₁+a₂ ∉ N`); only suitable words do.

### Reflections (the "reflection generation" alternative). **[proved]**
* `v = 2a₂+b₂ ∈ N`, `(v,v) = 4`, `q(v) = 2`: `σ_v ∈ O(N)` but
  `σ_v(½b₂) − ½b₂ = −a₂ − ½b₂ ∉ N`, so `σ_v ∉ O~(N)`; and `sn(σ_v) = −2 ∉ Q^{*2}`.
* `r₀ ∈ E8(−2)`, `(r₀,r₀) = −4`, `q(r₀) = −2`: `σ_{r₀} ∈ O(N)`, but for the adjacent simple root
  `r` (`(r₀,r) = 2`), `σ_{r₀}(½r) − ½r = ½r₀ ∉ N`, so `σ_{r₀} ∉ O~(N)`; and `sn(σ_{r₀}) = 2 ∉ Q^{*2}`.
* Only `(v,v) = −2` reflections are safe: `σ_v ∈ O~⁺(N)` for those (Lemma 2 + GHS **[quoted]**),
  and `N` has such vectors (e.g. `a₁ − b₁`, `(a₁−b₁,a₁−b₁) = −2`) — but their generation theorem
  (Kneser's Theorem 1.1) needs `rank₂ ≥ 6`, which fails.

So the alternative suggested in the question — "reflection generation by norm ±2, ±4 vectors" — is
**refuted in the `(v,v) = ±4` case** (those reflections are not even in `O~(N)`), and **unavailable in
the `(v,v) = −2` case** for want of Kneser's rank condition.

---

## 5. The sharpest maintained theorem (what does generate, with exact hypotheses and counts)

**(T1) [proved here]** For any even `L` and `e,x ∈ L` with `(e,e) = (e,x) = 0`:
`t(e,x) ∈ O~⁺(L)` (Lemma 1 + Lemma 3). For `L = N` this yields the **22 explicit generators**
`t(e,x)` with `e ∈ {a₁,b₁}` (unimodular isotropic vectors of `N`, `div_N(a₁) = div_N(b₁) = 1`) and `x`
running over a Z-basis of `e^⊥ ∩ N` (rank 11 each; `11 + 11 = 22`), and for `L = M` the **20**
generators `t(e,x), t(f,x)` with `x` in a basis of `U ⊕ E8(−2)` (rank 10, GHS's `E_U(L₁)`).
All of them lie in `O~⁺(L)`; by (T1) they are legitimate.

**(T2) [quoted, GHS Prop 3.3(ii),(iii)]** For `L = U ⊕ U₁ ⊕ L₀` (two hyperbolic planes, no rank
condition): `E(L) = E_U(L₁)` and `O(L) = ⟨E_U(L₁), O(L₁)⟩`. This *does* apply to `M`
(`L₁ = U ⊕ E8(−2)`, `O(L₁)` = the finite group generated by `W(E8)` and the `U`-symmetries).
This is the correct, citable content behind the "approximate model" the vendored paper needs for
`U+U+L`; its generator count is `2(n−2) = 20`, not the `4n = 48` of tex:1450.

**(T3) [quoted, GHS Prop 3.4 / Kneser Thm 1.1]** The equalities
`SO~⁺(L) = O′(L) = E(L)` (and the reflection generation of `O′(L)`) require `rank₂(L) ≥ 6`.
They fail hypothesis for `M` (`rank₂ = 4`) and for `N` (`rank₂ = 2`). Consequently the quoted
"`4n` generators generate" statement, read as a statement about `O~⁺`, is **[unverified from here]**
for these lattices; what survives is the finite-index/approximate-model reading.

**(T4) [unverified from here]** A generation theorem for `O~⁺(N)` itself, `N` 2-elementary with
`(l,a) = (2,10)` and only one hyperbolic plane, is not available in the sources I could read.
The honest statement is: `O~⁺(N) ⊇ ⟨t(e,x) : e ∈ {a₁,b₁}, x ∈ e^⊥ ∩ N⟩` (22 generators), and equality
is open from here. What is *not* open is the negative side: the ambient descent gives elements of
`O~⁺(M) ∩ Stab(N)` that do not lie in `O~(N)` (§3).

---

## 6. Verdict table

| H | verdict | reason |
|---|---|---|
| H1 | **proved** | `N = U⊕U(2)⊕E8(−2) ⊂ M = U⊕U⊕E8(−2)` with index 2 (tex:1481 with `c=1,d=2`; tex:1519); `[N^∨:M^∨] = 2`; `D(N) = D(U(2)) ⊥ D(M)`; no even `L` has `N ≅ U⊕U⊕L` (`|D(L)|₂ ≤ 2^{rk}`). |
| H2 | **proved as a reading; the quotations are silent on `D(N)`** | descent = `Stab_E(N) = E ∩ O(N)` (tex:1468–1469, Alg 1/3 = 1349/1347); tex:1457 concerns `D(U+U+L)` and is provable elementarily (Lemma 1). |
| H3 | **refuted** | `t(a₂,r₀) ∈ E(M) ∩ Stab(N)`, trivial on `D(M)`, moves `[½b₂]` by `½r₀ + a₂ ∉ N`; so `E′ ⊄ O~(N) ⊉/≠ ker(O⁺(N)→O(A_N))`. Additionally the cited theorem's hypotheses (`rank₂ ≥ 6`; two hyperbolic planes) fail for `N` and `rank₂` fails for `M`. |
| H4 | **proved** | all named generators ∈ `O~⁺` (Lemma 1 + Lemma 3; block maps = single transvections; verified exactly); the witness `t(a₂,r₀)` has `sn = 4 ≡ 1`, so the failure survives in `O⁺`; `(v,v) = ±4` reflections are ∉ `O~` and have `sn = ∓2`. |

**Bottom line.** The quoted route is *sound for the ambient lattice* `U+U+L` (both tex:1457 and the
generation, in the citable form GHS Prop 3.3) and *unsound for `N`*: the descent to `N` produces
elements outside `O~(N)`, so it cannot produce `ker(O⁺(N) → O(A_N))`, and no reading of the quoted
block yields that kernel. The maintainable alternatives are (T1) (22 transvections, proved to lie in
the kernel but not proved to generate it) and, for the ambient lattice only, (T2).

---

## 7. Reproduction

* `scripts/verify.py` — pure Python 3, exact `Fraction` arithmetic, no external libraries.
  Run: `python3 scripts/verify.py` (≈17 s). Output frozen in `scripts/verify.out`.
* It builds `M` (Gram `diag(U,U,−2·Cartan(E8))`), `N` (a₂-coordinate doubled), enumerates
  `D(N)` (1024 classes) and checks: index and discriminant orders; `D(N) = D(U(2)) ⊥ D(M)`;
  528 isotropic classes; `|O(q_N)|` recursion and factorisation; Lemmas 1–3 on spanning sets
  (including the failure when `(e,x) ≠ 0`); the counterexample `t(a₂,r₀)` (isometry, `N`-stability,
  triviality on `D(M)`, non-triviality on `D(N)`, factorisation into two reflections, `sn = 4`);
  the two reflection witnesses; `rank₂(M) = 4`, `rank₂(N) = 2`; the `W(E8)`-orbits `1, 120, 135`;
  and the four elementary block maps as single transvections.
* Sources: `references/vendor/arxiv/2302.01679/Enriques_compu_rev.tex` (line numbers above);
  GHS arXiv:0810.1614v1 (`.scratch` copy `scratch/ghs.pdf`, text `scratch/ghs.txt`,
  §1 eq. (2) at lines 95–127, §3.3 at lines 504–608).
