# #17 stage 1, method 2: Dutour Sikirić–Hulek's approximate model gives a finite family and an oracle, but not the index of that subgroup in Õ⁺(N)

Batch item 1 is the mathematics, and it decides the unit. The paper does contain the
existence theorem for `N = U ⊕ U(2) ⊕ E8(−2)`, does name `N`, and does produce from it an
explicit finite family together with an oracle over orbits of vectors — but no numbered
statement of it gives `[Õ⁺(N) : H]` or coset representatives of `H` in `Õ⁺(N)`, and the
paper says in one sentence that it does not use the finite-index property at all
(Definition 4.1's remark, p. 28). Under item 4 of the batch the unit stops there. Items 2
and 3 are therefore not started, and no call is written: a family plus a claim that the
union generates `Õ⁺(N)` is exactly what #17 forbids without a source.

Source read: M. Dutour Sikirić and K. Hulek, *Moduli of polarized Enriques surfaces —
computational aspects*, arXiv:2302.01679v2 [math.AG] 26 Sep 2023, 39 pages, text
extracted (no scan, no figure reading). Page numbers below are the preprint's printed
pages, which coincide with the PDF's. Nothing was downloaded into the repository; the
extraction lived in `.scratch/`.

## 1. The statements, with their pages

**The group being asked about, pp. 2–3.** p. 2: "the stable orthogonal group `Õ(N)`, which
is defined as the group of all elements in `O(N)` acting trivially on the discriminant
`D(N) = N^∨/N`. We set `Õ⁺(N) := O⁺(N) ∩ Õ(N)` and note that this is an index 2 subgroup
since the reflection with respect to a vector of length 2 in the summand `U` of `N` gives an
element in `Õ(N)` with real spinor norm −1." This is the library's `ṼO⁺(N) = ker(O⁺(N) →
O(A_N))`; `D(N) = A_N` up to the standard identification. p. 3, equation (2):
`O(D(N)) ≅ O⁺(F₂^10)` of order `2^21·3^5·5^2·7·17·31`, and `O(D(N)) ≅ O(N)/Õ(N) ≅
O⁺(N)/Õ⁺(N)`, citing [Nik1, Thm 3.6.3].

**Definition 4.1, p. 28** — an approximate model of an integral lattice `L` is:

- "A set of generators `{g_1, …, g_m}` of a subgroup `Ap(L)` of `O(L)` named approximate
  subgroup."
- "An oracle function `Ap(L, β)` that, given a `β ≠ 0`, returns a finite list `v_1, …,
  v_k(β)` such that any vector of norm `β` is equivalent by `Ap(L)` to one of the `v_i`. For
  `β = 0` the oracle function returns a list of primitive vectors of norm 0 such that any
  primitive vector of norm 0 is equivalent to one such vector by an element of `Ap(L)`."

**The sentence that decides item 1, p. 28**, immediately after Definition 4.1: "It is
important to note that a lattice can potentially have an infinite number of approximate
models and that we do not claim that every lattice has an approximate model. The
approximate subgroup is a finite index subgroup of `O(L)` in all cases considered, here but
we do not know if that is always the case **and we do not use this property here**."

**Lemma 4.2 and its proof, pp. 28–29** — `U + U + L` (L integral, non-degenerate, even) has
an approximate model, with the family *counted*: generators of `SL₂(Z)²` acting on `U + U`
via the identification `U + U = M_{2,2}(Z)` with its determinant form (4 generators, since
`SL₂(Z)` needs 2), together with the Eichler transvections `E_{e_i, v_{i,j}}` for
`1 ≤ i ≤ 4`, `1 ≤ j ≤ n − 1`, `(v_{i,j})_j` a `Z`-basis of `e_i^⊥`, per [Sca, Prop. 3.7.3]:
"if the dimension of `U + U + L` is `n`, we need 4 generators from `SL₂(Z)²` and `4(n−1)`
from the transvections and so `4n` together. The proof of Proposition 3.7.3 in [Sca]
provides an explicit way of computing a set of possible vector representatives and so the
oracle function."

**The discriminant remark, p. 29.** "The group provided by the Eichler algorithm acts
trivially on the discriminant. For a case such as `U + U + E8(−2)` this gets us 28 orbit
representatives. By adding the isometries of the `E8` component to the approximate subgroup,
we are reduced to just 3 representatives … `W(E8)` has 3 orbits in its action on
`E8/2E8`, their sizes being 1, 120 and 135."

**Theorem 4.3 and its proof, p. 29** — the transport that produces an approximate model of a
sublattice: "Suppose `L′` and `L` are two integral lattices of rank `n` with `L′ ⊂ L` and we
have an approximate model for `L`. Then we have an approximate model for `L′`." Proof: "We
can compute the stabilizer `S` of `L′` under `Ap(L)` by Alg 1 and this gets us an
approximate subgroup `Ap(L′)`. By using Alg 3 we compute the right coset decomposition of
`Ap(L)` under `S` with coset representatives `g_1, …, g_m`. … We then considers all the
elements of the form `g_j x_i` and keep the ones that are contained in `L′`." So
`Ap(L′) = S = Ap(L) ∩ O(L′)`, and the coset representatives `g_j` are used only to move the
oracle's vector representatives into `L′`.

**Theorem 4.4, pp. 29–30** — existence, and `N` inside its scope: "Let `L` be an integral
lattice of signature `p, q ≥ 2` of dimension at least 7. Then `L` has an approximate model."
The proof's final embedding is
`U(αc) + U(αd) + K^∨(α) ⊂ U + U + K^∨(α)`, with the previous remark's map
`(x_1, x_2, y_1, y_2, w) ↦ (c x_1, x_2, d y_1, y_2, w)`. p. 30 then says, of our lattice:
"the lattice `U + U(2) + E8(−2)` can be trivially embedded into `U + U + E8(−2)` by our
previous remark and so **no additional work is needed**" — "no additional work" for the
orbits they compute, not for generating the kernel.

**The algorithms that turn a model into orbits and stabilizers for the full group.**
Theorem 4.5, pp. 30–31: "There exist algorithms solving the equivalence and automorphism
group problems for integral non-degenerate lattices with `r(L) ≥ 5`", by induction on
`s(L) = min(p,q)`: `Orth(s)` computes a generating set of `O(L)` from `O(v_1^⊥)` plus the
oracle's vector representatives `Ap(L, β)` and Alg 1/Alg 2/`Equi(s−1)`. p. 30 states the
scope honestly: "The solutions that we provide are effective in the sense that they can be
computed on computers, but we do not make any claim on complexity". Theorem 4.8, p. 32:
exact orbit representatives of vectors of a given norm for `O(L)`, the approximate list being
made exact by Theorem 4.5. Theorem 4.9, pp. 33–35: (i) given an isotropic `k`-plane `Is`,
computes `Stab(L, Is)` and a finite set `(g_i)` with
`O(Is^⊥) = ∪_i g_i · Stab(L, Is)|_{Is^⊥}`; (ii) decides equivalence of two isotropic
`k`-planes. p. 35 warns that the covering "is only a covering and not a decomposition since
some of the cosets may coincide". Theorem 4.10, p. 35: orbits of isotropic `k`-planes.

**Why the paper never needs a generating set of the kernel, p. 22.** In §3.6 the orbit
splitting for `Γ_h` is done by Lemma 3.6 with `U = Õ(N)`: "We can apply the above lemma to
our case with `U = Õ(N)` the kernel of the action of `O(N)` on the discriminant, `K = Γ_h`
and `H = G_x`. The second key ingredient is that the quotient `O(N)/Õ(N) ≅ O⁺(F₂)` is
finite. We can apply the existing approach for finite groups, as implemented in [GAP], and
thus reduce the orbit splitting from `O(N)` to the group `Γ_h`." The 87 tables are computed
on the *finite* quotient; the kernel enters only as a normal subgroup one quotients by.

## 2. What the model gives for `N`, exactly

`N = U ⊕ U(2) ⊕ E8(−2)` satisfies Theorem 4.4's hypotheses (rank 12, signature (2,10),
dimension 12 ≥ 7), and Theorem 4.3 transports the model along the index-2 inclusion
`N ⊂ M := U ⊕ U ⊕ E8(−2)`.

- **A finite family: yes.** `Ap(N) = Ap(M) ∩ O(N)`, computable in principle by Alg 1 (p. 26)
  as the stabilizer of `N` in `Ap(M)`. On `M` the count is explicit: `4n = 4·12 = 48`
  generators (4 from `SL₂(Z)²`, `4·(12−1) = 44` Eichler transvections), Lemma 4.2, pp. 28–29.
  **No count and no bound is given for `Ap(N)`.**
- **An oracle: yes**, and stronger than asked: equivalence and orbit representatives of
  vectors of a given norm under `Ap(N)` (Definition 4.1); exact orbit representatives for
  `O(N)` (Theorem 4.8), stabilizers of isotropic `k`-planes plus a coset covering modulo them
  (Theorem 4.9(i)), and orbits of isotropic `k`-planes (Theorem 4.10) — the last three by
  passing through Theorem 4.5's inductive `Orth`/`Equi`, whose base case `s = 1` is the
  perfect-form/Coxeter algorithm of §4.2.
- **`H ≤ Õ⁺(N)`: not stated.** The only discriminant-triviality sentence is p. 29, and it is
  about the lattice the Eichler algorithm is built on, `M`, whose discriminant group has order
  `2^8 = 256`. `N` is an index-2 sublattice of `M` with `|A_N| = 2^10 = 1024`, so acting
  trivially on `D(M)` is a strictly weaker condition than acting trivially on `D(N)`, and the
  triviality does not descend. Verified below that this is the actual configuration of
  lattices: DSH's own map is an isometry of `M` into `N`-coordinates with cokernel `Z/2`, and
  the two discriminant orders are 256 and 1024.
- **`[Õ⁺(N) : H]` and coset representatives: no.** Not stated, and not implied by the oracle.
  The oracle decides equivalence of *vectors* under `Ap(L)`; membership of an isometry `g` in
  `Ap(N)`, and cosets of `Ap(N)` in `Õ⁺(N)`, are neither computed nor claimed. Alg 3 (p. 26)
  computes right cosets of `G ∩ GL_n(Z)` in a rational group `G` — a different pair, and the
  one Theorem 4.3 uses for vectors. Theorem 4.5 computes a generating set of `O(L)` in
  principle but gives no index of a subgroup inside an infinite group and carries no
  complexity claim; and the paper's own disclaimer (p. 28) is that the finite-index property
  is one it does not use. The only indices anywhere in the paper are `[Γ⁺_h : Õ⁺(N)] = |Γ̄_h|`
  from Tables 1–2 (pp. 13–14), `[O⁺(F₂^10) : Γ̄_h]` (same), and the two stabilizer-image
  indices `527` and `23715` on p. 22 — none of them an index of `Ap`.

## 3. The missing step, named

Two, and the batch's item 2 needs both:

1. **The descent to the kernel.** A statement that `Ap(N) ≤ Õ⁺(N)`, i.e. that the elements of
   `Ap(M)` preserving `N` act trivially on `A_N` (and have real spinor norm 1). DSH prove the
   analogous statement for `D(M)` only (p. 29), and `A_N` is four times larger than `D(M)`.
2. **The index and the cosets.** A statement giving `[Õ⁺(N) : Ap(N)]` and representatives of
   `Õ⁺(N)` modulo `Ap(N)`. Definition 4.1 supplies generators and a vector-equivalence
   oracle; Lemma 3.6 and §3.6 need only the finite quotient `O(N)/Õ(N)`; the paper's
   disclaimer on p. 28 rules out reading finite index as an available fact.

With (1) and (2), item 2's union would be `Ap(N)`'s family plus the coset representatives,
and item 3's `ρ(Γ_h)` comparison would be the ordinary one. Without them the union is a
family of unknown index in an unknown subgroup, which is precisely the unverified generation
claim #17 refuses.

## 4. Items 2 and 3, and why they are not done

- **Item 2 is not done** and the family was not built. Its condition — "if DSH give a
  computable index and coset representatives" — fails on §3 item 2 above.
- **Item 3 is not done.** Its content is the *kernel* part of the family: the lifts of
  generators of `ρ(Γ_h)` under `subgroup_generator_lifts()` generate a complement inside
  `Γ_h`, and their discriminant image equals `ρ(Γ_h)` by the construction of the lift, so the
  mutual-membership-and-equal-order check on them alone is vacuous for the group `Γ_h` itself.
  The comparison becomes a real check exactly when the kernel family exists. Nothing in
  `PredicateSubgroups.ParentMethods.discriminant_image()` changes here: it already answers
  `ρ(Γ)` exactly for a retained subgroup without a generating family, as #17 records.

## 5. What would change the answer

- A published statement that `Ap(N) = Õ⁺(N)`, or that `Ap(N) ⊇ Õ⁺(N)` with the quotient
  identified — DSH do not claim it, and their `Ap(N)` is deliberately chosen small ("we are
  reduced to just 3 representatives", p. 29, is the opposite direction of a generation
  statement).
- A published index `[Õ⁺(N) : Ap(N)]` with coset representatives.
- The owner commissioning the Tits-building generation step instead of a citation: `Õ⁺(N)`
  generated by the parabolic at one primitive isotropic plane together with one transporter
  per class of primitive isotropic planes. DSH's Theorem 4.9 now supplies, in principle, the
  two ingredients that argument needs — generators of `Stab(N, P)` for a plane `P`, and the
  test for whether two planes are equivalent — but glueing them into a generation statement
  for `Õ⁺(N)` is a piece of mathematics, not a code change and not a citation.

## 6. Numbers checked here

Script `.scratch/issue17b/dsh_arith.py` (sympy, no Sage container needed), output
`.scratch/issue17b/dsh_arith.log`. It builds `N` and `M` from their summands and compares to
the Gram matrix `results/issue17-generation-blocker.md` records from this library, and it
checks the paper's equation (2) against the library's measured `|im ρ|`:

```
det(E8 Cartan) = 1
det(E8(-2)) = 256
N built from summands == library Gram: True
N: rank 12  |det| 1024  mod-2 rank 2  rad2 dim 10  rank_2 2
M: rank 12  |det| 256  mod-2 rank 4  rad2 dim 8  rank_2 4
[M:N] from determinants = 4 -> index 2
DSH embedding diag(I2,[[2,0],[0,1]],I8): isometry M->N ? True  index of image in M = 2
|O+(F2^10)| = 46998591897600
528 = 1+527: True   24242 = 527+23715: True   527*45 = 23715   23715 = 3^2*5*17*31: True
Lemma 4.2 family for M: 4 + 4*(n-1) = 48 = 4n = 48
```

Three consequences used above: `|O⁺(F₂^10)| = 46 998 591 897 600` is exactly the
discriminant-image order `N.Aut().discriminant_image()` returned on this tree, so DSH's
equation (2) and this library's `A_N` are the same quotient; the inclusion `N ⊂ M` has index
2 with `|D(M)| = 256` and `|D(N)| = 1024`, so p. 29's triviality does not reach `A_N`; and
`rank₂(M) = 4` against `rank₂(N) = 2`, which is why the earlier note's rank argument against
GHS/Scattone/Kneser does not touch DSH's theorem — DSH's hypothesis is signature `p,q ≥ 2`
and dimension ≥ 7, which `N` meets.

`TRAPS.md` is not touched: this records a missing published statement, not a defect in this
repository's code.
