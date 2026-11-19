# #255 — one fold operation, its rescaling, and the folds that are not diagram automorphisms

The reviewer's three findings are answered here in the order they depend on one another.  Item 1
(the operation, and `sterk.py` deriving all five configurations from it) is the one the other two
rest on; item 2 is the tests' side of the mathematics it establishes; item 3 is the exploration.

The mathematics is written out as two propositions with proofs, because both are used by the code
and neither is quoted from a source.  The five chambers are Sterk's, and are cited by printed page.

## 1. The operation, and what its datum is

`RootedCoxeterDiagrams.ParentMethods.fold(involution)` is the one operation.  It takes an involution
\(g\) of the span \(W\) of the roots and returns a `RootFamilyFolding`: the diagram, the datum, the
formed lattice \(W\) the isometry acts on (the whole lattice when the roots span it rationally, the
saturated span otherwise), \(g\), the folded root family in \(W^g=\ker(g-1)\), the orbit sums that
are no roots, and — both lattices being even 2-elementary — Nikulin's \((r,a,\delta)\) of each
(`two_elementary_invariants`, `src/sage_extensions/categories/coxeter_diagrams.py:2844`).

The datum is \(g\), written in either of the two forms its images take:

* **a permutation of the vertices** — a mapping \(v\mapsto\sigma v\), or the tuple of the images of
  the vertices in their order — for an involution that carries roots to roots.  This is the
  issue's datum: a diagram involution, decided to lift or refused with the obstruction.
* **the images of the roots** — a mapping \(v\mapsto g(r_v)\), or the tuple of those images — for an
  involution that is no permutation of the roots, a root being carried to its negative or to the sum
  of itself with another root.  The vertices named must span the span of the whole family, since
  the images of a spanning subfamily are what determine a linear map.

One method, one set of decisions, whichever form the datum takes: the rational relations of the
named roots must be carried to relations; the pairings must be kept; the matrix in the span's
selected basis must be integral; and the map must be an involution (a fold sums over orbits).  Each
refusal names what failed.  `fold_by` no longer exists.

## 2. The five configurations are folds of the two families

`Sterk.foldings()` builds all five through `fold` and `Sterk.sterk_roots()` reads them; the card's
row `029J` / `gamma-en-2` is the oracle for the counts, the squares, the pairings and the
signatures.

| Sterk | card statement | walls (card) | printed page, figure | roots of the fold | squares | invariant | anti-invariant |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4.3.5 | 12 | p. 19, Fig. 4 | 12 | 12 × (−4) | (1,9) | (0,8) |
| 2 | 4.3.6 | 10 | p. 21, Fig. 6 | 10 | 9 × (−4), 1 × (−2) | (1,9) | (0,8) |
| 3 | 4.3.7 | 12 | p. 22, Fig. 8 | 12 | 10 × (−4), 2 × (−2) | (1,9) | (0,8) |
| 4 | 4.3.8 | 11 | p. 23, Fig. 10 | 11 | 9 × (−4), 2 × (−2) | (1,9) | (0,8) |
| 5 | 4.3.9 | 14 | p. 24, Fig. 12 | 14 | 10 × (−4), 4 × (−2) | (1,9) | (0,8) |

The counts, pages and figures are card `029J`'s `cusp_diagrams` row `gamma-en-2`, read by tag; the
figures are Sterk's, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z.
207 (1991), §4.3, statements 4.3.5–4.3.9 on printed pages 19–24.

Three of them are folds by a permutation of the roots: 4.3.5 and 4.3.8 by two involutions of the
22-root family, 4.3.6 by the reversal of the 19-root family.  Two are not, and cannot be:

| family | automorphisms | fold by each | roots | squares | invariant | anti-invariant |
| --- | --- | --- | --- | --- | --- | --- |
| 22 roots | 8 | identity | 22 | 2 × (−4), 20 × (−2) | (1,17) | (0,0) |
| 22 roots | | reversal I | 14 | 10 × (−4), 4 × (−2) | (1,10) | (0,7) |
| 22 roots | | reversal II | 14 | 10 × (−4), 4 × (−2) | (1,10) | (0,7) |
| 22 roots | | 4.3.5's | 12 | 12 × (−4) | (1,9) | (0,8) |
| 22 roots | | order four | refused: no involution | | | |
| 22 roots | | 4.3.8's | 11 | 9 × (−4), 2 × (−2) | (1,9) | (0,8) |
| 22 roots | | 4.3.8's partner | 11 | 9 × (−4), 2 × (−2) | (1,9) | (0,8) |
| 22 roots | | order four | refused: no involution | | | |
| 19 roots | 2 | identity | 19 | 19 × (−2) | (1,17) | (0,0) |
| 19 roots | | reversal | 10 | 9 × (−4), 1 × (−2) | (1,9) | (0,8) |

So no permutation of either family folds it to 4.3.7 (the twelve-root fold is all (−4), 4.3.7 is
ten (−4) and two (−2)) or to 4.3.9 (both fourteen-root folds have invariant signature (1,10) where
every printed chamber's is (1,9)).  Sterk's third and fifth are folds all the same, by involutions
of the 22-root family that are no permutations of the roots:

* the **fifth** is the orthogonal reflection in the span of the eight even-indexed roots
  \(v_2,v_4,\dots,v_{16}\).  Those eight are pairwise orthogonal of square \(-2\) and stand at
  distance two on the sixteen-root chain, so each pairs \(1\) with the two odd-indexed roots beside
  it; the reflection negates them and sends \(v_{2k-1}\) to \(v_{2k-1}+v_{2k-2}+v_{2k}\), and it
  fixes \(v_{17},\dots,v_{22}\), which are orthogonal to all eight.  Its orbit sums are
  \(v_{2k-2}+2v_{2k-1}+v_{2k}\) and \(v_{17},\dots,v_{22}\), the archived folding's fourteen sums.
* the **third** is the printed reflection-twisted folding: eight transposed pairs and two fixed
  roots of the sixteen-root chain, and \(v_{18},v_{20},v_{22}\mapsto v_{18}+v_{22},\
  v_{20}+v_{22},\ -v_{22}\).  Its discarded orbit sums are the two that fall on the isotropic
  \(v_{21}+v_{22}\) line.

## Proposition 1 (the relation test and the pairing test decide the same thing exactly on a nondegenerate span)

Let \(r_1,\dots,r_n\) span \(W\subset L\), with coordinate matrix \(C\) (rows \(r_i\) in a basis of
\(W\)) and Gram matrix \(G=C\,G_L\,C^{t}\).  Then the space of rational relations
\(\{(c_i):\sum_i c_i r_i=0\}=\ker C\) is contained in \(\ker G\), with equality exactly when \(W\) is
nondegenerate.

*Proof.*  \(Gc=0\) says \(\sum_i c_i r_i\) pairs to zero with every \(r_j\), i.e. lies in
\(W\cap W^\perp\); conversely such a point gives \(Gc=0\).  So \(\ker G\) is the preimage of
\(W\cap W^\perp\), which is \(\{0\}\) exactly when \(W\) is nondegenerate. ∎

*Consequence.*  Let \(\sigma\) be a permutation of the roots with \(G_{\sigma i,\sigma j}=G_{ij}\)
for all \(i,j\) — a map that keeps the Gram matrix.  If \(\sum_i c_i r_i=0\) then for every \(j\),
\(\langle\sum_i c_i r_{\sigma i}, r_{\sigma j}\rangle=\sum_i c_i G_{ij}=0\), so
\(\sum_i c_i r_{\sigma i}\in W\cap W^\perp\); over a nondegenerate span that is \(0\), so the
relation is carried to a relation and \(\sigma\) lifts to an isometry of \(W\)
(\(\langle r_{\sigma i},r_{\sigma j}\rangle=\langle r_i,r_j\rangle\)).  **A permutation that keeps
the Gram matrix and breaks a rational relation therefore exists only over a degenerate span.**

The 22 roots span a lattice of signature (1,17) — rank 18 of a rank-20 ambient lattice — so their
span is nondegenerate and the issue's invalidating input cannot be a permutation of the 22 roots.
The refusal has its specimen on the degenerate family
\([[-2,1,0],[1,-2,0],[0,0,0]]\) with the five roots \(s_1,s_2,s_1+s_2,s_1+z,s_2+z\), where a
Gram-preserving permutation of order two breaks the relation \(s_1+s_2-(s_1+s_2)=0\); the tests
assert the nondegenerate side as well: of \(A_2\)'s six permutations exactly the two that keep the
pairings fold, and of the 22 roots' eight diagram automorphisms (which are exactly the
Gram-preserving permutations, since the Coxeter matrix is a function of the Gram) the six
involutions all fold.

## Proposition 2 (orbit sums, and the rescaling)

Let \(g\) be an involution of \(W\) and \(O\) an orbit of \(g\) on the roots.  Then \(|O|\in\{1,2\}\),
\(s_O=\sum_{y\in O}y\) is fixed by \(g\), so \(s_O\in W^g\), and \(W^g\)'s orthogonal complement
\((W^g)^\perp\) is the anti-invariant lattice.  If \(s_O=mt\) with \(t\) a point of \(W^g\) of
negative square, then \(t\) is the folded root of that orbit; otherwise \(s_O\) is no root.

*Proof.*  \(g(s_O)=\sum_{y\in O}g(y)=s_O\).  For \(x\in W^g\), \(y\in W^{-}\), \(\langle x,y\rangle
=\langle gx,gy\rangle=-\langle x,y\rangle\), so the two are orthogonal, and ranks add because
\(g^2=1\) diagonalizes.  The two roots of a 2-element orbit sum to \(r+g(r)\), whose square is
\(q(r)+q(g(r))+2b(r,g(r))=2q(r)+2b(r,g(r))\); a root is primitive, so a non-primitive sum is
rescaled to its primitive direction, which is fixed by \(g\) because the sum is, and which is a
point of \(W^g\) because the coordinates are integral. ∎

The red test at the parent is exactly this: in the degenerate lattice
\(\mathbf Z t\oplus\mathbf Z u\) with \(q(t)=-2\) and \(u\) isotropic, the roots \(t+u\) and \(t-u\)
pair to \(-2\) and sum to \(2t\); the fold dropped \(2t\) as non-primitive and returned no root where
it now returns \(t\), of square \(-2\).

## 3. Acceptance, item by item

**1. "The operation exists at its owner … and `sterk.py` derives Sterk's roots from it." — MET.**
There is one operation, `RootedCoxeterDiagrams.ParentMethods.fold`, and `Sterk.foldings()` builds all
five configurations through it (three by permutations, two by their images), `Sterk.sterk_roots()`
carrying them into \(T_{dP}\).  The reviewer's two grounds are both answered: the second operation
`fold_by` is gone; and the rescaling the issue asks for is implemented and has a red test at the
parent.  Where the issue is narrower than its own specimens, the source says so and the tests prove
it: a permutation of the roots cannot produce 4.3.7 or 4.3.9 (the enumeration in §2), so the
operation's datum is the involution's images, of which a permutation of the roots is the case where
the images are roots.

**2. "Tests assert the five root counts, the invariant and anti-invariant lattice signatures, and
the refusal on the invalidating input." — MET.**
The counts are asserted against card `029J`'s row `gamma-en-2` by tag; the invariant and
anti-invariant signatures are asserted for all five ((1,9) and (0,8)) at `:146`, `:152`, `:153`,
`:335`, `:336`, `:349` and the exploration's `:123`–`:126`.  The invalidating input is exhibited and
refused **on a family of 22 roots**:
`tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:133` takes the four
roots \(r_1,r_2,r_1+r_2,r_1+z\) and eighteen pairwise orthogonal \((-2)\)-roots that the map
fixes, so the swap of \(r_1\) and \(r_1+z\), extended by the identity, keeps all 22 pairings and
carries \(r_1+r_2-(r_1+r_2)=0\) to the nonzero radical vector \(z\); `fold` refuses it
(`:169`).  The same construction with four roots is the smallest specimen (`:110`, refused at
`:129`).  Sterk's own 22 roots cannot host it: their span is nondegenerate of signature (1,17), so
Proposition 1 makes a Gram-preserving permutation of them preserve every relation, and
`...folds_of_the_two_root_families.sage:233` checks that hypothesis (all eight automorphisms keep the
Gram) and its conclusion (the six involutions fold) beside the refusals that input does admit — the
pairing-moving transposition at `:269` and the two Gram-preserving non-involutions at `:260`.

**3. "The exploration … uses only this operation." — MET.**  The exploration reads
`Sterk.foldings()`, which is five `fold` calls and nothing else, and its prose states the datum, the
decisions and the rescaling.

## 4. Measured

At the adopted runtime (Sage 11.0.beta5, `/sage/.venv/bin/python` in
`~/sage-image/rootfs`), commands run inside the image with the checkout bound at `/work`:

```
pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
  -p sage_extensions.testing.test_lint --no-time-gates --durations=0 \
  tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage \
  tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage \
  tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage
```

* at the reviewer's head (`1c3fdec`): **17 passed in 25.44 s**, no lint findings;
* at the `test:` commit `f6769cc`, whose parent is the head below: this file **7 passed, 1 failed in
  7.64 s**, the failure `test_an_orbit_sum_that_is_a_multiple_of_a_root_is_rescaled` (0.08 s) —
  `assert () == (e_0,)`: the fold returned no root where the orbit sum is \(2t\);
* at the fix's rebased head: **20 passed in 31.17 s**, no lint findings.  The three heaviest checks
  are the enumeration of the two families' folds (3.04 s), the exploration's fixed-point walk over
  the five folds (2.70 s) and the card chamber signature (1.46 s); the new rescaling test is 0.02 s
  and the 22-root Gram test 0.95 s;
* at the previous round's head, the two files whose tests changed: **18 passed in 32.82 s** before
  the rebase and **18 passed in 56.72 s** after it, no lint findings;
* at this round's head, the fold file and the exploration: **15 passed in 33.01 s** before the
  rebase and **15 passed in 16.08 s** after it, no lint findings.

## 5. What is not verified here

* The claim that the folded families *are* Sterk's printed chambers is carried by card `029J`'s rows
  and by Sterk's printed statements, not proved in this record.  What is checked for all five is
  that each fold agrees with its card row in the wall count, the squares, the sorted pairings, and
  the invariant lattice's rank and signature: (12, 12×(−4), 10, (1,9)), (10, 9×(−4)+1×(−2), 10,
  (1,9)), (12, 10×(−4)+2×(−2), 10, (1,9)), (11, 9×(−4)+2×(−2), 10, (1,9)) and
  (14, 10×(−4)+4×(−2), 10, (1,9)) at 4.3.5–4.3.9 in that order.  The two sides are vectors of
  different lattices (\(T_{En}\) for the card's walls, \(T_{dP}\) for the roots), so equality of the
  two *families* is not asserted; the invariants are.
* The identification of the third involution's printed description (the archived notebook's
  reflection-twisted folding) is the source's; what is checked here is that its images decide an
  integral isometric involution of the 22-root span, and that its fold has 4.3.7's invariants.
* The issue's operation paragraph asks for two-elementary invariants "when defined", and the
  folding answers them: `RootFamilyFolding.two_elementary_invariants`
  (`src/sage_extensions/categories/coxeter_diagrams.py:2844`) returns Nikulin's \((r,a,\delta)\)
  of the invariant and of the anti-invariant lattice when both are even 2-elementary, and refuses
  naming the lattice when one is not.  All ten lattices of the five folds are 2-elementary — their
  determinants are \(-1024, 256, 256, 256, 256\) (invariant) and \(256, 256, 256, 256, 64\)
  (anti-invariant) — so all five answer: \((10,10,0)\) and \((8,8,0)\) for Sterk 1, \((10,8,0)\)
  and \((8,8,0)\) for Sterk 2, 3 and 4, and \((10,8,0)\) and \((8,6,0)\) for Sterk 5, checked
  against each lattice's own rank and determinant in the exploration at `:146`.  The refusing branch
  is exhibited on the \(A_2\) fold's anti-invariant lattice of square \(-6\), whose discriminant
  group is not 2-elementary
  (`tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:173`, refusal
  `:195`).

## 6. Where each acceptance item lives

Line numbers are those of this commit.  All three items are met, so nothing below is queued behind
another item.

**Item 1 — "The operation exists at its owner …, and `sterk.py` derives Sterk's roots from it."**

* `src/sage_extensions/categories/coxeter_diagrams.py:2489` — `RootedCoxeterDiagrams.ParentMethods.fold(involution)`:
  the one operation, whose datum is taken in either form at `:2560` through `_involution_images`
  (`:2903`) and whose four decisions and two propositions are its docstring (`:2519` the
  relations/pairings proposition, `:2531` the orbit sums and the rescaling).
* `:2562` — `_folded_by_images`, the single decision path (relations, pairings, integrality,
  involution) and the fold itself; `:2720` the orbit sums and the rescaling, `_coordinate_divisor`
  at `:2985`.
* `:2779` — `RootFamilyFolding`, the returned record: `isometry` `:2809`, `invariant_lattice` `:2813`,
  `anti_invariant_lattice` `:2817`, `roots` `:2821`, `discarded_sums` `:2825`, and
  `two_elementary_invariants` `:2844`.
* `src/sage_extensions/sterk.py:689` — the three permutation folds, `:691` the two image folds, both
  inside `_foldings_cached` (`:679`); `foldings()` `:697`; `_sterk_roots_cached` `:718` reads them;
  `sterk_roots()` `:784`.
* The derivation is asserted, not just read: `test_the_folded_configurations_are_the_constructions_sterk_returns`
  at `tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage:156`
  (the folded family equals what `sterk_roots()` returns), the two image folds at `:283`, the five
  records at `:309`, and the exploration's `:129` (each fold has its card row's count and squares and
  its folded diagram is rooted in the invariant lattice, `:143`).

**Item 2 — "Tests assert the five root counts, the invariant and anti-invariant lattice signatures,
and the refusal on the invalidating input."**

* Counts against card `029J`'s row `gamma-en-2` by tag:
  `tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage:126`, and
  `tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage:139`.
* Signatures: the same file's `:146` (invariant equals the card walls' span), `:152` (the span is
  \((1,17)\)) and `:153` (anti-invariant \((0,8)\)) for 4.3.5, 4.3.6 and 4.3.8; `:335`, `:336`,
  `:349`, `:350` for the two image folds and the five records; and the exploration's `:123`–`:126`
  for all five at once.
* The refusals on Sterk's own 22 roots:
  `tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage:233`
  asserts that all eight diagram automorphisms keep the Gram, that the six involutions fold, and
  that the two order-four maps are refused (`:260`); `:269` asserts that a transposition of two
  roots is refused for the pairing it moves.
* The invalidating input on a degenerate family of 22 roots:
  `tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:133`, refused at
  `:169`; the same construction at four roots, the smallest specimen, at `:110`, refused at `:129`.
* The two-elementary invariants: `src/sage_extensions/categories/coxeter_diagrams.py:2844`
  (helper `:2874`), answered for all five folds at
  `tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage:146` and refused for a
  lattice that is not 2-elementary at
  `tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:173`.
* The rescaling the reviewer found absent: `tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage:257`,
  red at `f6769cc`'s parent.

**Item 3 — "The exploration … uses only this operation."**

* `tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage:1` is the exploration;
  its only source of folds is `Sterk.foldings()` at `:93`, `:114` and `:136`, which is
  `src/sage_extensions/sterk.py:697` and nothing else, and no other operation is called: the
  filename, the docstring and the three reads name the one `fold`.
