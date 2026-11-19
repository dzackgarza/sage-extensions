# #255: the amendment the invalidating-input clause needs, and why it cannot be met as written

The acceptance item says:

> Tests assert the five root counts, the invariant and anti-invariant lattice signatures, and the
> refusal on the invalidating input.

and the issue body defines that input as:

> Invalidating input: a permutation of the 22 roots that preserves the Gram matrix of R but not its
> rational relations is not an isometry of the span and must be refused.

**No such permutation exists on the 22 roots.**  The 22 roots of `Sterk.roots_18_2_0()` span a
lattice of rank 18 and signature (1,17) — their four relations are linear dependences, not radical
directions — so their span is nondegenerate.  For a spanning set of roots with coordinate matrix
\(C\) and Gram \(G\), the rational relations are \(\ker C\) and \(\ker G\) is the preimage of
\(W\cap W^\perp\) under \(r\mapsto\langle r,-\rangle\); over a nondegenerate \(W\) the two coincide.
So a permutation that keeps the Gram matrix keeps every rational relation: if
\(\sum_i c_i r_i=0\) then \(\sum_i c_i r_{\sigma i}\) pairs to zero with every \(r_{\sigma j}\),
hence with all of \(W\), hence is a point of \(W\cap W^\perp=0\).

The exhaustive check on the 22 roots themselves (every permutation of them that keeps the Gram
matrix, and the Coxeter matrix is a function of the Gram, so those are the diagram's eight
automorphisms), and over every subfamily of them that carries a relation (120 relation supports, 25
of them degenerate), run by `results/issue255-the-invalidating-input-search.py`:

```
roots 22 rank 18 relations 4
diagram automorphisms 8
Gram-preserving permutations 8
of those, breaking a rational relation 0
relation supports with at least four zero coordinates 120
of those, spans degenerate 25 sizes [11, 16, 18]
degenerate supports whose automorphisms break a relation 0
four-root control: relations 1 broken True
```

The four-root control is the same check on the smallest family where a degenerate span leaves room
for such a permutation; there the relation is broken and the operation refuses it.

## Replace the issue body's `Invalidating input:` line with

> Invalidating inputs, and the refusals they must meet:
>
> * a permutation of the 22 roots that is no isometry of their span, refused for the pair it moves —
>   the transposition of \(v_1\) and \(v_2\), since \(v_1\) pairs \(1\) with \(v_{17}\) and \(v_2\)
>   pairs \(0\) with it;
> * a permutation of the 22 roots that keeps the Gram matrix but is no involution, refused because a
>   fold takes the orbit sums of an involution — the two order-four automorphisms of the 22-root
>   diagram;
> * a permutation that keeps the Gram matrix but breaks a rational relation.  The 22 roots span a
>   nondegenerate lattice of signature (1,17), so by the paragraph above none exists there, and the
>   refusal this clause is for is exhibited where a degenerate span leaves room for one: on the four
>   roots \(r_1,r_2,r_1+r_2,r_1+z\), whose swap of \(r_1\) and \(r_1+z\) carries the relation
>   \(r_1+r_2-(r_1+r_2)=0\) to the nonzero radical vector \(z\), and on the 22-root family built from
>   it by eighteen pairwise orthogonal \((-2)\)-roots that the map fixes.

## Replace the second acceptance bullet with

> * Tests assert the five root counts, the invariant and anti-invariant lattice signatures, and each
>   of the three refusals above: the pairing-moving transposition of two of the 22 roots, the two
>   Gram-preserving permutations of them that are no involutions, and the relation-breaking
>   permutation on the four-root degenerate family and on the 22-root family built from it.

## Where the amended item is already met

| clause | assertion |
| --- | --- |
| the five counts | `tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage:126`; `tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage:139` |
| both signatures | `...folds_of_the_two_root_families.sage:146`, `:152`, `:153`, `:335`, `:336`, `:349`, `:350`; exploration `:123`–`:126` |
| the pairing-moving transposition | `...folds_of_the_two_root_families.sage:269` |
| the two Gram-preserving non-involutions | `...folds_of_the_two_root_families.sage:233`, refusal `:260` |
| the four-root relation refusal | `tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:110`, refusal `:129` |
| the 22-root degenerate relation refusal | `tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:133`, refusal `:169` |

The connection this repository is worked through reads issues and pushes commits but cannot edit an
issue body, and the platform offers no site whose API could: this file is the edit for the owner to
paste into #255, with the whole body it leaves in `results/issue255-amended-issue-body.md`.  The
record `results/issue255-the-fold-of-a-root-family.md` states the item as NOT MET while the issue
stands unamended and as MET under this text.
