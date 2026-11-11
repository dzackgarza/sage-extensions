# #331 — does the parabolic at a plane that does not split generate the whole stabilizer?

$T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$, rank 12, signature $(2,10)$.  Two
primitive isotropic planes, both Sterk's (*Compactifications of the period space of
Enriques surfaces, Part I*, Math. Z. 207 (1991), Proposition 4.6, p. 29):

$$P_1 = \mathbb{Z}e_1 + \mathbb{Z}e_3, \qquad
  P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3,\quad q(w) = -8 .$$

$P_1$ splits off the lattice, $P_2$ does not.  This note records the two routes the
issue names, what each one yields, and the exact point at which the second stops.

## Route (a): a cited generation statement

Read in the arXiv source of the cited version (D. Dutour Sikirić, K. Hulek, *Moduli of
polarised Enriques surfaces — computational aspects*, J. London Math. Soc. 110 (2024),
arXiv:2302.01679v2, `Enriques_compu_rev.tex` of the eprint):

* **§3.6 "The Tits building", printed p. 22.**  What is stated about the two planes is
  the *index* of their stabilizer images in the discriminant group: "the stabilizer of
  the plane $P_1$ has an image of index $527$ while the image of the stabilizer of $P_2$
  has an image of index $23715 = 3^2\cdot5\cdot17\cdot31$", and the $24242$ planes split
  "in two orbits, of lengths $527$ and $23715$".  No generating set.
* **§4, Theorem 4.9 (`theorem_isotropic_k_planes`), printed p. 22**, with its proof.
  The theorem is an *algorithm*: "(i) Given an isotropic $k$-plane $Is$, we can compute
  the stabilizer $\mathrm{Stab}(L,Is)$".  The proof solves the block equations for an
  isometry of $L$ extending an isometry $Q$ of $Is^\perp$: "The second equation
  determines $P_1\in GL_k(\mathbb{Q})$ uniquely.  Then the third equation will determine
  $P_3\in M_{k,n-2k}(\mathbb{Q})$ uniquely."  On integrality: "if we force $Q_1$ to
  preserve the lattice $L_{J^T}$ spanned by the rows of the matrix $J^T$, then $P_1$ is
  integral ... So, we obtain a finite index subgroup $G_2$ of $G_1$ that preserves
  $L_{J^T}$", and, in the paragraph closing the proof, "It would have been simpler if we
  had a sublattice $L'$ of $L$ such that for any $f\in O(Is^\perp)$ there exists an
  extension that preserves $L'$.  Unfortunately, we could not find a universal
  construction of such a lattice.  However, in all the cases we considered, a practical
  algorithm allowed us to solve this problem."  This is an algorithm for the group and an
  explicit statement that no uniform integral model exists; it does not name a generating
  set, so it cannot be used to *prove* that a given family generates.
* **Scattone, Mem. Amer. Math. Soc. 374 (1987), §3.7 Proposition 3.7.3**, in the form the
  paper itself uses it (Lemma `sublattice_approx_model`, §"Approximate models and the case
  of signature $p,q\geq 2$, printed p. 18): "According to [Scattone, Proposition 3.7.3] we
  simply need the generators of $SL_2(\mathbb{Z})^2$ and the transvections
  $E_{e_i,v_{i,j}}$ ... Thus, if the dimension of $U+U+L$ is $n$, we need $4$ generators
  from $SL_2(\mathbb{Z})^2$ and $4(n-1)$ from the transvections and so $4n$ together."
  What that generates is an **approximate subgroup**, and the paper says what that is: "a
  set of generators $\{g_1,\dots,g_m\}$ of a subgroup $\mathcal{A}p(L)$ of
  $\mathrm{Orth}(L)$", "a finite index subgroup of $\mathrm{Orth}(L)$ in all cases
  considered here".  Two consequences: the statement is about a *finite-index* subgroup of
  $O(U+U+L)$, not about the setwise stabilizer of a plane; and its lattice is of the shape
  $U+U+L$, which $T_{\mathrm{En}} = U \oplus \big(U(2)\oplus E_8(-2)\big)$ is not.
* **Sterk 1991, §4.**  Not read in the original: Math. Z. 207 (1991) is behind the
  publisher's paywall and this session did not obtain the text.  The statements of it that
  the two accessible sources reproduce are the cusp diagram and the *line* stabilizer
  quotients: DH §3.6 (p. 22) cites Propositions 4.5/4.6 for the orbit counts, and
  Alexeev–Engel–Garza–Schaffler, arXiv:2312.03638, Lemma 3.8 with Corollary 3.12 states
  that Sterk's Coxeter diagrams are the diagrams of the reflection groups
  $W(\Gamma_{\mathrm{En},2,e})$ for the isotropic *vectors* $e$, obtained by Vinberg's
  algorithm.  Neither attributes a generating set of a *plane* stabilizer to Sterk.
  **Unverified**, not a negative: the original was not read.

Route (a) therefore does not close, and the reason is not a gap in the search but the
content of the sources: the published statements are (i) indices of the stabilizer images,
(ii) an algorithm whose own text says the integral model is found case by case, (iii) a
generating set for a finite-index approximate subgroup of a lattice of another shape, and
(iv) a Coxeter-diagram computation for line stabilizers.

## Route (b): the computation, one factor at a time

The parabolic fits in $1 \to U_I \to \mathrm{Stab}_{O(L)}(I) \to \Gamma \to 1$ with
$\Gamma \subseteq GL(I)\times O(K)$, $K = I^\perp/I$ (rank 8, negative definite here, so
$O(K)$ is finite and $GL(I) = GL_2(\mathbb{Z})$ is the infinite factor).  The returned
family of `parabolic_stabilizer_generators` has, at these planes,

```
                 P2     what it is
  radical         21     Eichler transvections E_(p,x), p in the plane's basis, x over a ZZ-basis of p^perp
  half-vector     19     E_(e,w), w in the metric dual, 2w in L, b(e,w) = 0 (#325)
  quotients       64     reflections in the root shells of K, lifted into I^perp
  plane lifts     18     integral lifts of plane actions by the block equations of Thm 4.9
  total          122

  at P1 the same construction returns 164 generators (13 plane lifts, the rest
  radical, half-vector and quotient reflections); the four-way split at P1 was
  not measured in this session.
```

### The $GL(I)$ factor is closed

`levi_plane_action_index()` computes
$[\mathrm{GL}_2(\mathbb{Z}) : \langle g|_I\rangle]$ from a certificate whose every input
is checked at run time:

* $\Gamma(2) = \ker(\mathrm{GL}_2(\mathbb{Z}) \to \mathrm{GL}_2(\mathbb{F}_2))$ is generated
  by the two shears $A = \binom{1\ 2}{0\ 1}$, $B = \binom{1\ 0}{2\ 1}$ and $-1$ (Sanov
  1947: $\Gamma(2)/\{\pm1\}$ is free on the two shears), and each of the three is exhibited
  as a product of at most four of the returned plane actions;
* $|\mathrm{GL}_2(\mathbb{F}_2)| = 6$ is computed, and so is the image of the actions
  there.

Then $[\mathrm{GL}_2(\mathbb{Z}) : H] = 6/|H \text{ in } \mathrm{GL}_2(\mathbb{F}_2)|$.
Measured:

```
  P1: 14 distinct plane actions, Gamma(2) inside them, image in GL_2(F_2) of order 2  -> index 3
  P2: 19 distinct plane actions, Gamma(2) inside them, image in GL_2(F_2) of order 6  -> index 1
  P2: the same, restricted to the 58 returned generators that act trivially on K      -> index 1
  P1: the same restriction gives all 14 actions there as well
```

Both are what the block equation of Theorem 4.9 predicts.  The equation is
$P_1 = J Q_1^{-t} J^{-1}$ with $J = b(U,I)$:

* at $P_1$, $J = \mathrm{diag}(1,2)$, so $Q_1$ must preserve the row lattice
  $\mathbb{Z}e_1 + \mathbb{Z}2e_2$: the condition $c \equiv 0 \pmod 2$, i.e.
  $\Gamma^0(2)$, of index $6/2 = 3$ — the family fills exactly that;
* at $P_2$, $J = 2\cdot 1_2$, so $P_1 = Q_1^{-t}$ is integral for **every**
  $Q_1 \in \mathrm{GL}_2(\mathbb{Z})$: no congruence condition at all, index $1$.

So at $P_2$ the finite-index subgroup of plane actions that the paper's caveat leaves
open is the whole of $\mathrm{GL}_2(\mathbb{Z})$, and every plane action admits an
integral lift inside the returned family.  That is the plane half of route (b) settled
with a proof, not a measurement.

### What follows for the Levi image, and what is still missing

Because the family contains an isometry with trivial $K$-action for every one of its
plane actions, $\Gamma_1 = \{M : (M,1) \in \Gamma\}$ is all of $\mathrm{GL}_2(\mathbb{Z})$,
and then $\Gamma = \mathrm{GL}_2(\mathbb{Z}) \times H_0$ with
$H_0 = \{N \in O(K) : (1,N) \in \Gamma\}$: for $(M,N) \in \Gamma$ one has
$(M^{-1},1) \in \Gamma$, hence $(1,N) = (M,N)(M^{-1},1) \in \Gamma$.  So the Levi image
is the full product, and

$$\mathrm{Stab}_{O(L)}(P_2) = \langle \text{returned family}\rangle
  \iff \langle N_j\rangle = H_0 \ \text{and}\ \langle \text{radical part}\rangle = U_I .$$

That is the reduction this unit establishes; the two remaining factors are the ones below.

At the split plane the quotient factor is not open at all: $K = b(U,K) = 0$, so the third
block equation reads $0 = P_3 A Q_3^t$, hence $P_3 = 0$ for every quotient action, and the
first two equations do not involve $Q_3$.  The admissible pairs are then the product
$A \times O(K)$ with $A$ the plane actions admitting a lift, so every isometry of $K$ lifts
with a trivial plane action and $H_0 = O(K)$.  That is what makes #295's `True` at a
splitting plane stand, and what fails at $P_2$.


Two factors are not decided, and neither is a plane action:

1. **The quotient factor $H_0 \subseteq O(K)$.**  The family's 64 quotient reflections
   give elements $(1, s_w)$ with $s_w$ a reflection in a root of $K$, so
   $\langle N_j \rangle \subseteq H_0 = \{N \in O(K) : (1,N) \text{ admits an integral
   lift}\}$, and what is missing is (i) the order of $O(K)$ for $K = P_2^\perp/P_2$ — a
   rank-8 negative definite lattice whose Gram has Smith normal form
   $(1,1,2,2,2,2,2,2)$, and no method here computes its isometry group — and (ii) the
   congruence description of $H_0$ inside it, which is what the block equations decide and
   which no method here computes.  The reflections alone are not enough to conclude: a
   root of $K$ need not lift with trivial plane action, and the identity isometry of $K$
   need not lift at all is exactly the question.
2. **The radical $U_I$.**  From the block form, $U_I$ is a lattice of rank
   $2\cdot 8 + 1 = 17$: $\mathrm{Hom}(K,I)$ contributes $2\cdot 8$, and the skew part of
   $\mathrm{End}(I)$ one.  The returned transvections are *not* all of $U_I$: an Eichler
   transvection $E_{p,x}$ acts on $I$ by the unipotent matrix fixing $p$, so it is in the
   parabolic but not in the kernel; the kernel is generated by the ones that also fix $I$
   pointwise together with their composites.  Nothing here shows that those generate
   $U_I$: that is a rank statement about a torsion-free nilpotent lattice, and it has not
   been made.

## What the code now answers

`is_parabolic_complete()` stays `False` at $P_2$ — the two factors above are open, and the
issue's acceptance is a generation statement, not an index statement.  What changed is
that the refusal can now be precise, and one of its three factors is closed:

* `levi_plane_action_generators()` — the plane actions $g|_I$ of the returned family,
  computed on the plane's own basis (not read off a block of an auxiliary matrix);
* `levi_plane_action_index()` — $[\mathrm{GL}_2(\mathbb{Z}) : \langle g|_I\rangle]$ by the
  $\Gamma(2)$ certificate above: $1$ at $P_2$, $3$ at $P_1$;
* `parabolic_obstruction()` — names the quotient factor and the radical as the missing
  statements, and says the plane action is not one of them.

## Evidence

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates tests/lattices/test_the_parabolic_completeness_of_an_enriques_plane.sage \
  tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage

6 passed in 194.06s (0:03:14)
  test_the_plane_actions_at_p2_are_all_of_the_general_linear_group   83.09 s
  test_the_split_plane_action_has_index_three                        30.97 s
  test_the_plane_classes_and_their_cusp_count_are_card_029J_s_rows   58.27 s
```

Run with `--no-time-gates`: the three calls above exceed the suite's 20 s call gate, and the
first two build the 122- and 164-generator families.  The shared VM carried six other
sessions' jobs during the run, so the durations are upper bounds.

The per-orbit plane lengths are read from card `029J` by tag; the row to file upstream and
why it is not filed from here are in
`results/issue331-lattice-database-029J-orbit-lengths.md`.
