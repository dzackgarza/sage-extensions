# #255: the issue body as the amendment leaves it, for one paste

`results/issue255-amended-invalidating-input.md` gives the two changed blocks as old-to-new.  This
file is the whole body with them applied, so that the owner can replace #255's body in one paste.
Everything outside the two blocks is the issue's own text, unchanged except where it states what
the tree holds, which is stated as of this head; the two blocks are marked *[amended]*.  Its
references are to the tree at this commit.

The connection this repository is worked through cannot edit an issue body, so this is a proposal,
not an edit.

---

Sterk's five root configurations were stored as hard-coded orbit sums; they are folds now,
`Sterk.foldings()` (`sterk.py:697`), built at `sterk.py:689` and `:691` and carried into the Del
Pezzo lattice by `Sterk.sterk_roots()` (`sterk.py:784`). The mathematics behind them is a folding: a diagram involution σ of the Coxeter diagram of a root family
R in a lattice L lifts to an isometry of L, and the orbit sums (or projections) of R span the
σ-invariant lattice L^σ and form the root family of the folded diagram. The retired notebooks
"Lattices and Coxeter Diagrams DZG" (folding cells), "Sterk IAS Plotting" (cells 14-17) and "Coble
Lattice Invariants" chapter 8 all compute this by hand. The pieces are the library's:
`LatticeMorphisms.invariant_lattice` (`lattice_morphisms.py:2002`), `formed_coinvariants` (`:2012`),
`CoxeterDiagrams.Aut` (`coxeter_diagrams.py:1445`), `CoxeterDiagrams.from_roots` (`:2179`), and the
operation itself, `RootedCoxeterDiagrams.ParentMethods.fold` (`coxeter_diagrams.py:2489`).

## Operation *[amended: the datum is the involution's images, of which a permutation of the roots is
the case where the images are roots; and two of Sterk's five need the images]*

Given a root family R in L and an involution \(g\) of its span that is an isometry of it:

- the datum of \(g\) is its images: a permutation σ of R that is an automorphism of the Coxeter
  diagram `from_roots(R)` when it carries roots to roots, or the images of the roots when it does not
  — a root negated, or carried to the sum of itself with another root;
- decide whether \(g\) extends to an isometry of the span of R, and of L when R spans L rationally,
  and refuse with the obstruction when it does not;
- return that isometry, its invariant lattice L^σ and anti-invariant lattice (L^σ)^⊥ as formed
  subobjects, with signatures and two-elementary invariants when defined;
- return the induced root family on L^σ (orbit sums of R, rescaled where the orbit is not
  orthogonal) and its Coxeter diagram.

Sterk's roots become the output of this operation applied to the 22-root (18,2,0) family
(`Sterk._roots_18_2_0_cached`, `sterk.py:562`) and the 19-root (18,0,0) family (its roots at
`sterk.py:641`), and `sterk.py` no longer stores orbit sums.  Three of the five configurations are folds by a permutation of the roots
(4.3.5 and 4.3.8 of the 22, 4.3.6 of the 19); 4.3.7 and 4.3.9 are folds by involutions of the
22 roots' span that are no permutations of them, since the 22-root diagram has eight automorphisms
and folding by the six that are involutions gives 4.3.5, 4.3.8, the identity's own family and two
fourteen-root families of invariant signature (1,10) --- not the printed (1,9) --- while the other two
are no involutions.

## Specimens

| Fact | Source |
| --- | --- |
| The 22 roots of the (18,2,0) configuration have norms: 20 of −2 and two (v21, v22) of −4; the 19 roots of (18,0,0) have norm −2 | DZG, CLS |
| The 22 roots satisfy 4 rational relations and span rank 18 | Coble ch. 8 |
| The permutation `(1,13)(2,12)(3,11)(4,10)(5,9)(6,8)(14,16)(17,20)(18,19)(21,22)` is in `Aut` of the 22-root diagram | DZG |
| The root-swap involution has a 10-dimensional invariant subspace; the Coxeter-graph involution has vertex orbits {0,2},{1,4},{3,6},{7,10},{8,9},{5} | Coble ch. 8 |
| Folded root counts 12, 10, 12, 11, 14 for Sterk 1-5 | `sterk.py`, Sterk 1991 |
| Folding ranks 12, 12, 12, 14 with image rank 10 (one IAS cell prints 11 against an assertion of 10: the discrepancy is to be settled by the operation) | DZG, Sterk IAS cell 17 |

*[amended]* Invalidating inputs, and the refusals they must meet:

- a permutation of the 22 roots that is no isometry of their span, refused for the pair it moves —
  the transposition of \(v_1\) and \(v_2\), since \(v_1\) pairs 1 with \(v_{17}\) and \(v_2\) pairs 0
  with it;
- a permutation of the 22 roots that keeps the Gram matrix but is no involution, refused because a
  fold takes the orbit sums of an involution — the two order-four automorphisms of the 22-root
  diagram;
- a permutation that keeps the Gram matrix but breaks a rational relation.  The 22 roots span a
  nondegenerate lattice of signature (1,17), so their rational relations are exactly the kernel of
  their Gram matrix and no such permutation of them exists.  The refusal this clause is for is
  exhibited where a degenerate span leaves room: on the four roots \(r_1,r_2,r_1+r_2,r_1+z\), whose
  swap of \(r_1\) and \(r_1+z\) carries the relation \(r_1+r_2-(r_1+r_2)=0\) to the nonzero radical
  vector \(z\), and on the 22-root family built from it by eighteen pairwise orthogonal
  \((-2)\)-roots that the map fixes.

## Acceptance criteria

- The operation exists at its owner (a method on the root family, or on `LatticeMorphisms` with the
  diagram as input) and `sterk.py` derives Sterk's roots from it.
- *[amended]* Tests assert the five root counts, the invariant and anti-invariant lattice signatures,
  and each of the three refusals above: the pairing-moving transposition of two of the 22 roots, the
  two Gram-preserving permutations of them that are no involutions, and the relation-breaking
  permutation on the four-root degenerate family and on the 22-root family built from it.
- The exploration "Semantic exploration: Sterk's five root configurations as foldings" uses only this
  operation.

---

The assertions that meet the amended acceptance criteria are tabulated in
`results/issue255-amended-invalidating-input.md`, and the record `results/issue255-the-fold-of-a-root-family.md`
states item 2 both ways: not met while the issue stands unamended, met under this wording.
