# Adjudication of H1–H4 for N = U ⊕ U(2) ⊕ E8(−2)  (member m2, direction d5)

Labels used throughout:
- **(V)** verified here by an exact script in `scripts/` (outputs in `results/`).
- **(P)** proved here, proof written out.
- **(Q)** quoted from the vendored primary text `references/vendor/arxiv/2302.01679/Enriques_compu_rev.tex`
  (project p-165a6922b36b40789ddc90db34bb23c7, worktree c68f101e), exact line numbers given.
- **(U)** not verifiable from here (source not reachable / argument not found).

---

## 0. The primary text, read directly (all line numbers exact)

| line | content |
|---|---|
| 302 | `O(N)`, `O⁺(N)` = "the orthogonal group of transformations with real spinor norm 1" |
| 315–317 | `Õ(N)` := all `g ∈ O(N)` acting trivially on `D(N) = N^∨/N` ("stable orthogonal group") |
| 319–321 | `Õ⁺(N) := O⁺(N) ∩ Õ(N)`; "**index 2** subgroup since the reflection with respect to a vector of length 2 in the summand U of N gives an element in `Õ(N)` with real spinor norm −1" |
| 1429–1430 | Lemma: "If L is an integral non-degenerate even lattice, then U+U+L has an approximate model" |
| 1432–1436 | proof invokes "Eichler's criterion [§3]{eichler}"; "we can take a suitable subgroup of Orth(U+U) together with the Eichler transvections" |
| 1437–1440 | Scattone *Example 3.7.2*: `U+U` ≅ determinant form on `M₂,₂(Z)`; `SL₂(Z)×SL₂(Z) ≤ Orth(U+U)`, 4 generators |
| 1442–1447 | "the Eichler transvections `E_{e_i,x}` … for `e_i` one of the **4 canonical isotropic vectors** coming from the two hyperbolic planes `U` and `x` a vector orthogonal to `e_i`"; `E_{e,x}E_{e,y} = E_{e,x+y}` |
| 1448–1451 | by Scattone *Prop 3.7.3*: generators of `SL₂(Z)²` plus `E_{e_i,v_{i,j}}`, `1≤i≤4`, `1≤j≤n−1`, `(v_{i,j})` a Z-basis of `e_i^⊥`; count `4 + 4(n−1) = 4n` |
| 1456–1457 | "**The group provided by the Eichler algorithm acts trivially on the discriminant.**" (stated for `U+U+L`) |
| 1457–1460 | for `U+U+E₈(−2)`: "`2^8` orbit representatives", improved to 3 using `W(E₈)` on `E₈/2E₈` |
| 1466–1470 | descent theorem: L' ⊂ L: "compute the **stabilizer S** of L' under `Ap(L)` by **Alg 1**"; "by **Alg 3** we compute the right coset decomposition of `Ap(L)` under S" |
| 1345 / 1347 | Alg 1 := "generating set of the intersection `G ∩ GL_n(Z)`"; Alg 3 := "right cosets of `G ∩ GL_n(Z)` in `G`" |
| 1424–1426 | "the approximate subgroup is a finite index subgroup of `Orth(L)` **in all cases considered, here**, but **we do not know if that is always the case and we do not use this property here**" |
| 1477–1481 | "**any lattice `cU + dU + W`** with `c,d ∈ ℕ` and `W` integral and even has an approximate model via the … embedding in `U+U+W`: `(x₁,x₂,y₁,y₂,w) ↦ (c x₁, x₂, d y₁, y₂, w)`" |
| 1518–1520 | "In our application we are in the fortunate situation that the lattice `U+U(2)+E₈(−2)` can be trivially embedded into `U+U+E₈(−2)` by our previous remark and so no additional work is needed." |

Note what the quoted block at 1429–1460 is **about**: it is a proof that `U+U+L` (L even) *has an
approximate model* (Definition at 1412–1421: a finite generating set of a subgroup `Ap(L) ≤ O(L)`
**plus an oracle function**). It is not a statement that the generated group equals any kernel.
The only generation assertion in the block is the **generator count `4n`**, and the only
discriminant assertion is 1456–1457, which is about the discriminant of the *ambient* `U+U+L`.

---

## 1. H1 — exact embedding.  VERDICT: **PROVED** (Q + P + V)

* Existence and shape: (Q) 1477–1481 gives exactly the map named in the question, with `c=1`, `d=2`,
  `W = E₈(−2)` (even); (Q) 1518–1520 applies it to `U+U(2)+E₈(−2)` explicitly.
* **(P)** Let `Φ(x₁,x₂,y₁,y₂,w) = (x₁,x₂,2y₁,y₂,w)`. In the U(2)-plane with basis `a=(2,0)`, `b=(0,1)`
  of `U = ⟨u,v⟩` (`q=2x₁x₂`): `q(a) = 0, q(b) = 0, b(a,b) = 2`, i.e. the image of U(2) *is* `⟨2u, v⟩`,
  a primitive (=saturated) sublattice of `U`, and `U/⟨2u,v⟩ ≅ Z/2`.
  Verified: `Φᵀ G_M Φ = G_{U⊕U(2)}` and `[M:N] = √(det N/det M) = 2` **(V** `results/step1…`)**
  (`M = U⊕U⊕E₈(−2)`, `N = U⊕U(2)⊕E₈(−2)`).
* Duals/discriminants **(P + V)**: with `H = M/N ≅ Z/2`, `|A_N| = |A_M|·[M:N]² = 2^10 = 4·2^8`, and
  `A_M = H^⊥/H` (order `2^8`) sits in `A_N` modulo the gluing class. The gluing class is the class of
  `u = (1,0)` in the second U, it is a 2-torsion class with `q_A(u) = 0`; `A_{U(2)} ≅ (Z/2)²` is the
  hyperbolic 2-plane with `q(1,0)=q(0,1)=0, b((1,0),(0,1)) = 1/2` **(V** step1 §2–3**)**.
* Consequence: `A_N = A_{U(2)} ⊕ A_{E₈(−2)}` and **(V** step3**)** `q` on `A_N` is 2-elementary of
  dimension 10 with **528 zeros**, hence of **plus type** `q₁₀⁺`; therefore `O(A_N) ≅ O⁺(10,2)` and
  `|O(A_N)| = 2·2^{20}·31·(2²−1)(2⁴−1)(2⁶−1)(2⁸−1) = 46998591897600 = 2²¹3⁵5²·7·17·31`,
  matching the number recorded in-repo. The `O^±(2m,2)` order formula was independently checked by
  brute force in dimension 4 (`|O⁺(4,2)|=72`, `|O⁻(4,2)|=120`) **(V** step3/step4**)**.
* So: yes, N embeds into `U⊕U⊕E₈(−2)` with index 2; and by 1477–1481 into `cU+dU+W` more generally.
  There is **no** even unimodular ambient of rank 12 (12 ≢ 0 mod 8), so `M` is the natural maximal
  ambient here.

---

## 2. H2 — which subgroup descends.  VERDICT: **the stabilizer** (Q), with the triviality step
   *not* given by the quotation but provable (P + V).

(Q) 1466–1470 says literally: `Ap(L') := S = Ap(L) ∩ O(L')`, computed by Alg 1, and Alg 3 is used only
to get coset representatives for the oracle. Hence:

* **E′ = S = Ap(M) ∩ O(N)** — the *stabilizer*. It is **not** a restriction `E ∩ O(N)` for an abstract
  reason worth recording: `Ap(M) ⊄ O(N)`, so "restriction" is not even defined; and it is **not a
  conjugate**, since conjugating `Ap(M)` by an element of `O(N)` that does not preserve `M` gives a
  different subgroup.
* **What is not in the text**: that S acts trivially on `D(N)`. Line 1456–1457 asserts triviality on
  `D(M)` for the ambient lattice `M = U+U+L` only. The inference `trivial on D(M) ⟹ trivial on D(N)`
  is **not valid in general** and I verified a counterexample inside the same construction:
  for `N(c,d) = cU ⊕ dU ⊂ U⊕U` the SL₂(Z)²-stabilizer acts **non-trivially** on `A_{N(c,d)}` when
  `(c,d) = (1,3)` (10 of 20 stabilizer elements tested) and `(c,d) = (2,2)` (50 of 70)
  **(V** `results/step2…` §3**)**. So triviality on `D(N)` is a genuine extra step. For the lattice of
  interest it happens to be **true**:
  - *local rank-4 model* `N₄ = U ⊕ U(2) ⊂ M₄ = U⊕U`: the SL₂(Z)²-stabilizer of `N₄` is the
    congruence subgroup of index 9, cut out by `(p,q,s) ≡ (1,0,1) mod 2` (i.e. `q` even) on each
    factor; it acts **trivially** on `A_{N₄}` (all 36 stabilizer elements with `|entries| ≤ 2`
    tested) **(V** step2 §2–3**)**. Reason **(P)**: in the determinant model `(M₂,₂(Z),2det)`, a
    left/right multiplier preserving `N₄` has `q₁₂` even, whence `q₁₁q₂₂ ≡ 1 mod 2` (det = 1), and the
    induced map on `A_{N₄} = ⟨ē, f̄⟩` is `ē ↦ q₂₂ē`, `f̄ ↦ q₁₁f̄` = identity.
  - *E₈(−2)-summand*: fixed pointwise by these block maps, so its part of `D(N)` is fixed **(P)**.
* **Quantitative correction to the `4n` count** (Q, 1448–1451) after descent to `N` **(V** step1 §5,
  step6**)**:
  - of the 4 canonical isotropic vectors `e₁,e₂,e₃,e₄` of `M₄ = U⊕U`, **`e₃` (the `u`-vector of the
    scaled plane) does not lie in `N₄`** (`u₂ ∉ N₄`, `u₂ ∈ N₄^∨`); only 3 directions survive;
  - testing a generating set `{S, S^T, T} × {left, right}` of `SL₂(Z)²`, only `left S^T` and
    `right S^T` preserve `N₄`; `S` and `T` on either side do not (so at most a proper subgroup, of
    index ≥ 4 in the ambient `SL₂(Z)²` modulo the kernels, descends).
  Hence the paper's `4n = 48` (for `n = 12`) is an ambient count; on `N` the same recipe yields
  `2 + 3(n−1) = 35` generators, and the transvections along `e₃` that do preserve `N` are
  all **trivial on `N`** (computed: for `x` with τ_{e₃,x}(N₄) ⊆ N₄ one gets τ_{e₃,x}|_{N₄} = id,
  `|coords| ≤ 2`) **(V** step1 §5**)**.

---

## 3. H3 — equality with `ker(O⁺(N) → O(A_N)) = Õ⁺(N)`.  VERDICT: **NOT SUPPORTED by the quoted
   route; the specific obstruction candidate is REFUTED; equality remains CONDITIONAL on a separate
   Eichler-type generation theorem.**

### 3a. The named obstruction candidate (`(eᵢ,N^∨) = ½Z` on U(2), `F(e,x)` with `e` in the U(2)-factor)
**REFUTED as an obstruction.** **(P) Lemma.** Let `L` be an even integral lattice, `e ∈ L` isotropic,
`x ∈ L` with `(e,x) = 0`. Then
`τ_{e,x}(v) = v − (v,e)x + (v,x)e − ½(x,x)(v,e)e`
is an integral matrix (`e,x ∈ L`, `(v,e),(v,x) ∈ Z` for `v ∈ L`, `(x,x)` even), it is an isometry
(verified by the exact cancellation `a²(x,x) + 2[−aβ + βa − ½(x,x)a²] = 0` with `a=(v,e)`, `β=(v,x)`),
and for `v ∈ L^∨` one has `τ_{e,x}(v) − v = −(v,e)x + (v,x)e − ½(x,x)(v,e)e ∈ L`, because
`(v,e) ∈ Z` for **every** `v ∈ L^∨` and `e ∈ L` (definition of the dual lattice) — **primitivity of
`e`, the scale of U(2) and the value of `(e,e)` are irrelevant**. Same for every reflection in a
vector of norm 2: `τ_e(a) − a = −(a,e)e ∈ L`.

Verified numerically on `N₄ = U⊕U(2)` (6041 admissible pairs), `M₄ = U⊕U` (3097) and
`N₆ = U⊕U(2)²` (4130): every tested `τ_{e,x}` is integral, an isometry, and trivial on `A_L`
**(V** `results/step1…` §4**)**. So "the transvections act trivially on the discriminant" is true for
`N` — and it is not where the gap is. This also matches the paper's own use of the same fact at
319–321 (a norm-2 reflection lies in `Õ(N)`, with spinor norm ≠ 1).

### 3b. What is missing
The quoted route produces a subgroup `S = Ap(M) ∩ O(N) ⊆ Õ(N)`; the claim `S = Õ⁺(N)` (or `= Õ(N)`)
is nowhere in the text: (Q) 1424–1426 explicitly declines to assert even finite index, and 1466–1470
only asserts that `S` *is* an approximate subgroup (i.e. that some finite-index subgroup exists).
Provable pieces assembled here:
`⟨transvections τ_{e,x} with e,x ∈ N⟩ · ⟨norm-2 reflections⟩ · ⟨SL₂(Z)²-stabilizer⟩ ⊆ Õ(N)` **(P+V)**,
and `Õ⁺(N)` is index 2 in `Õ(N)` (Q, 319–321; consistent with **(V)** `θ(reflection in norm-2 vector)
= 2 ∉ Q*²`, and **(V)** `θ(−1_N) = det N = 1024 = 32² ≡ 1`, so `−1_N ∈ O⁺(N)` while `−1_N` acts
trivially on `D(N)`).
Unproved (U): that these generators exhaust `Õ⁺(N)`. That is exactly Eichler's criterion, quoted at
1432–1434 as `[§3]{eichler}` — **the hypotheses of Eichler's §3 could not be checked here** (the book
is not reachable from this VM), so this step stays conditional. In particular I do **not** claim the
equality, and I do **not** claim its negation.

### 3b′. The "±2 versus ±4 vector" refinement **(V + P)**
The hint "reflection generation by norm-(±2,±4) vectors" needs a correction: a reflection in a
vector of norm **2** always lies in `Õ(L)` **(P** as in 3a**)**; but a reflection in a vector of norm
**−4** need not. Concretely, `E₈(−2)` has 240 vectors of norm `−4` (= the roots of `E₈` scaled), and
for **every** one of them `(v, L^∨) ⊄ 2Z` (`L^∨ = ½E₈`), so its reflection acts **non-trivially** on
`A_{E₈(−2)}`, hence is not in `Õ(N)`: computed for the 148 representatives inside `|coords| ≤ 2`,
0 of 148 act trivially **(V** `results/step_roots.out`**)**; `W(E₈)` is transitive on the roots, so all
240 behave the same. Consequently a reflection-generation statement for `Õ(N)` may use norm-2
vectors only (its reflection group), not the norm-4 root system of the `E₈(−2)` summand.

### 3c. Sharpest maintained statement that DOES hold (the alternative theorem to state)
For **definite** 2-elementary lattices the analogue is provable *and* computationally confirmed here
**(V** `results/step4…`**)**:
`K := ker(O(L) → O(A_L)) = W(L) = ⟨reflections in norm-2 vectors⟩` and `K` is generated by its own
reflections for `L = D₄` (`|O|=1152`, `|K|=192`), `A₁⁴` (`|O|=384`, `|K|=16`), `A₁²` (`|O|=8`,`|K|=4`).
The indefinite statement that the evidence supports is:
> **Maintained theorem (conditional).** Let `L` be even, `rank ≥ 3`, indefinite. Then
> `Õ⁺(L) = ⟨ τ_{e,x} : e ∈ L primitive isotropic, x ∈ e^⊥ ∩ L ⟩ · ⟨ τ_e : (e,e) = ±2 ⟩` intersected
> with `O⁺(L)`; for `L = N = U⊕U(2)⊕E₈(−2)` every listed generator lies in `Õ(N)` (proved above), so
> the only missing ingredient is the *generation* half, which is Eichler's criterion
> (`[§3]{eichler}`, cited at line 1432) and remains (U) here.
Expected generator counts on `N` (rank 12): transvections along isotropic directions of the
`U ⊕ U(2)` part only (the `E₈(−2)` summand is negative definite and contributes no isotropic vector),
i.e. a set of size `2 + 3(n−1) = 35` rather than `4n = 48` (see H2), plus **pairs** of norm-2
reflections because a single one lies in `Õ(N) ∖ O⁺(N)`.

---

## 4. H4 — spinor.  VERDICT: **PARTIAL** (proved: `−1`, norm-2 reflections; undetermined: some
   transvections)

* `θ(−1_L) = det(Gram_L) mod Q*²` **(P)**, so `−1_{N} ∈ O⁺(N)` since `det N = 1024 = 32²`;
  likewise `−1_{N₄} ∈ O⁺(N₄)` (`det = 4`); `−1_{N₆} ∉ O⁺(N₆)` (`det = −16`) **(V** step5b §1**)**.
* Reflection in a norm-2 vector: `θ = 2 ∉ Q*²` ⟹ it lies in `O^−(N)`, i.e. in `Õ(N) ∖ Õ⁺(N)`; this
  is exactly the argument the paper gives at 319–321 for `Õ⁺(N)` having index 2 in `Õ(N)` **(Q+P)**.
* One Eichler transvection with `q(x) = 2` was factorised as `τ_{[−3,−3,0,−3]} · (reflection, q = 2)`,
  giving `θ = 1`, hence **that** transvection is in `O⁺` **(V** step5b**)**.
* Transvections with `e, x` both isotropic **and orthogonal** (the "Lagrangian pair" case, which is
  the case of the canonical `E_{e_i,v_{ij}}` whenever `v_{ij}` is isotropic) are **not products of
  two reflections** **(P)**: if `g = τ_u τ_w` then `Fix(g) ⊇ w^⊥ ∩ u^⊥` (dim ≥ n−2); here
  `Fix(τ) = ⟨e,x⟩^⊥ = ⟨e,x⟩` is a maximal isotropic subspace, of dimension `n−2` in the rank-4 model,
  so `w^⊥ ∩ u^⊥ = ⟨e,x⟩`, hence `⟨u,w⟩ = (w^⊥ ∩ u^⊥)^⊥ = ⟨e,x⟩`, so `u,w` are isotropic and no
  reflection in them exists. Their `θ` therefore needs a factorisation of length ≥ 3 and was
  **not determined here (U)** for the rank-4 model.
* Everything in H4 is compatible with the paper's assertion that `Õ⁺(N)` has index 2 in `Õ(N)`
  and with the generator statement being inside `Õ(N)`; it is *not* compatible with claiming that
  *all* named generators lie in `O⁺`.

---

## 5. Reproduction

| script | what it establishes |
|---|---|
| `scripts/lat.py` | exact lattice/discriminant machinery (Fractions only): `A_L = Z^n/GZ^n`, `y ↦ GMG^{-1}y`, `trivial_on_A`, transvections, reflections |
| `scripts/step1_h1_and_transvections.py` | H1 index/duals/gluing; the transvection lemma checked on 13k+ pairs; which canonical isotropic vectors survive on `N₄` |
| `scripts/step2_sl2_descent.py` | the `SL₂(Z)²` stabilizer of `cU+dU` and its induced action on `A`; counterexamples at `(c,d)=(1,3),(2,2)` |
| `scripts/step3_order_OAN.py` | Arf type of `A_N` (528 zeros ⟹ `q₁₀⁺`), `|O(A_N)| = 46998591897600`; `4n = 48` |
| `scripts/step4_definite_controls.py` | definite controls: `K = W(L)` for `D₄, A₁⁴, A₁²`; `|O^±(4,2)| = 72, 120` |
| `scripts/step5_spinor_and_H3.py`, `scripts/step5b_spinor.py` | spinor norms; the no-two-reflection lemma in practice |
| `scripts/step6_quotient_gap.py` | which ambient generators survive on `N₄` (2 of 4 `SL₂`, 3 of 4 isotropic directions) |

Run from `.ultramath/smvzznqcw/m2`: `python3 scripts/stepK_*.py` (each terminates in seconds).
Outputs captured in `results/`.
