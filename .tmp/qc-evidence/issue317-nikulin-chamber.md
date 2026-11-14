# issue 317: the genus as `v^perp` in II_{1,17}, through Nikulin and the chamber

## 1. The correspondence, against Nikulin 1980

Source read: `research/tmp/sources/nikulin-1980-integral-symmetric-bilinear-forms.pdf`
(V. V. Nikulin, *Integral symmetric bilinear forms and some of their applications*,
Izv. Akad. Nauk SSSR 43 (1979); Math. USSR Izv. 14 (1980)), extracted with
`pdftotext -layout`.

- **Theorem 1.14.2, p. 125.** "Let T be an even, indefinite lattice satisfying …
  Then the genus of T contains only one class, and the homomorphism
  `O(T) → O(q_T)` is surjective."  The hypotheses are `rg T ≥ l(Δ_T) + 2` for
  `p ≠ 2` and a 2-adic alternative.  Applied to `T = ⟨2k⟩` (rank 1, unique in its
  genus; `O(T) = {±1}` maps onto `O(q_T) = {±1}`), which is the lattice whose
  orthogonal complement is wanted.
- **Proposition 1.15.1, p. 128.** "The primitive embeddings of S into an even
  lattice with invariants `(m₊, m₋, q)` are determined by the sets
  `(H_S, H_q, γ; K, γ_K)` … For the primitive embedding of S determined by
  `(H_S, H_q, γ; K, γ_K)`, the lattice `K` is isomorphic to the orthogonal
  complement of `S`."
- **Its proof, p. 129**, gives exactly the statement the method needs, for
  `T` unique in its genus with `O(T) → O(q_T)` onto and `q_T = -q`: "all
  lattices of genus `(m₊, m₋, q)` are obtained as orthogonal complements to `T`
  in primitive embeddings of `T` into an even unimodular lattice `L` of signature
  `(t₊ + m₊, t₋ + m₋)`.  Here, if `M ⊂ L` and `M′ ⊂ L` are two sublattices of `L`
  of genus `(m₊, m₋, q)`, then all isomorphisms between `M` and `M′` extend to
  automorphisms of `L`."  Hence the classes of the genus are the `O(L)`-orbits of
  primitive `v` with `q(v) = 2k`, the class being `v^⊥`.

With `T = ⟨2k⟩` (signature `(1,0)`) and `L = II_{1,17}` (signature `(1,17)`), the
complement genus has signature `(0,17)` and determinant `2k`: the genus of
`⟨−2k⟩ ⊕ E8(−1)²`.

**Computational check of the correspondence:** the first chamber vector found,
`v = (−1,−1,0,…,0)` with `q(v) = 2`, has `v^⊥` of rank 17 with
`|Aut| = 1941728542064640000` and `conway_mass()` =
`2499347/9440684171518279680000` — the mass of the k = 1 genus, independently
obtained from the class enumeration in the earlier commits.  And
`v = (−1,−2,0,…,0)` with `q(v) = 4` gives `v^⊥` with the same `|Aut|` and
`conway_mass()` = `642332179/18881368343036559360000`, the k = 2 mass.  So the
complement of a primitive `v` of square `2k` really is a class of the wanted
genus, in both genera, with the right masses.

## 2. The chamber

    HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("E8") + Lattices(ZZ)("E8")).fundamental_chamber()

returns **19 wall roots in 76–83 s** (three runs: 82.6 s, 76.9 s, 75.9 s), i.e.
the Vinberg diagram of II_{1,17} has 19 simple roots.  The cone it returns is
`{x : b(r,x) ≥ 0 for every accepted wall r}` and has a `complete` flag which is
not exposed as a readable attribute through this call (`n/a`).

## 3. Where the class enumeration stops

The chamber vectors of square `2k` are enumerated by `v = (a, b, x, y)` with
`2ab + q(x) + q(y) = 2k`, `x, y` in the two `E8(−1)` blocks.  The run reaches
**1 of 4** classes for k = 1 and **1 of 9** for k = 2:

    k = 1: v = [-1,-1,0,...], |Aut| 1941728542064640000, roots 482   (mass 1/1941728542064640000)
    k = 2: v = [-1,-2,0,...], |Aut| 1941728542064640000, roots 480   (mass 1/1941728542064640000)

**The stop, with its stack:** the wall vectors read from `chamber.wall_roots()`
via `root.to_vector().to_vector()` do not act as the chamber's inequalities
against vectors written in the `U ⊕ E8 ⊕ E8` coordinate basis — filtering with
`b(r,v) ≥ 0` and with `b(r,v) ≤ 0` returns the *same* candidates
(`issue317-probe35-s1.log`, `issue317-probe35-s-1.log`), so the wall roots are
carried in a different framing than the one my candidates use.  The chamber call
itself returns; the translation between `wall_roots()`' framing and the lattice's
own coordinates is the missing step, and until it is exact the enumeration is a
hand-written family of candidates (the `[:3]`, `[:8]`, `[:8]` slices) rather than
"the vectors of the closed chamber", which is why the mass does not close.

## 4. The plane rows

Not reached: they follow the class set through `E ↦ E^⊥/E` (Scattone, Mem. AMS
374, Prop. 5.4.7 with Cor. 5.4.8(2), p. 78) once the classes are complete.

## The frame, resolved

`fundamental_chamber()` stores the cone as `correlation(root) = b(root, .)` for the
roots `wall_roots()` returns, so a wall root's vector is a **lattice element**, and
membership of the closed chamber is `b(r, x) >= 0` in the lattice's own form.  Read
through `model.framing_morphism().lift(root)`, every one of the 19 wall roots has
`q(r) = -2` in the model's Gram, and the model's Gram is `U` at `[0:2]`
orthogonal to two `E8` Cartans at `[2:10]` and `[10:18]`.  So the earlier "different
framing" reading was wrong: my hand-built Gram agreed, and the reason both wall
signs gave the same candidates was that the candidate family then in use had
`x = y = 0` for almost every member, which no wall can discriminate.

## The bound

Every wall of square `-2` inside an `E8` block is that block's simple root, so
`b(r, x) >= 0` puts each `E8` part in the dominant chamber.  `E8` is unimodular, so
its dominant vectors are the nonnegative integral combinations of the fundamental
weights (the columns of the inverse Cartan matrix), with `q(x) = c^T M c`; those of
norm at least `-40` are collected, and the hyperbolic coordinates are bounded by
`|a|, |b| <= 10`.  Both are truncations of a definite region, and the mass
assertion is what decides: a class they hide leaves the mass short and the route
declines (`_genus_classes_through_the_chamber` returns `None`).

## The classes (`issue317-probe37.log`)

    k = 1: 6 chamber vectors, 4 classes, mass 2499347/9440684171518279680000   EQUAL
    k = 2: 14 chamber vectors, 9 classes, mass 642332179/18881368343036559360000 EQUAL

The k = 2 nine include the 544-root class with |Aut| = 46620662575398912000, i.e.
`D_17(-1)` -- the class the four turns of neighbour walking never reached.  The
eight others are the 204/224/244/264/304/384/480/480-root classes found before.

## What is shipped

`src/sage_extensions/categories/lattices.py`: `_unimodular_complement_frame`
(cached: model, walls, dominant pool) and `_genus_classes_through_the_chamber`,
called first from `_genus_classes`'s definite branch.  Through it,
`(E8(-1)^2 + <-2>).genus().representatives()` returns the card's 4 classes in
116.8 s.  For k = 2 the shipped route does not return inside 1080 s, although the
same algorithm in the probe closes in 30 s: the shipped path admits far more
chamber candidates for `order = 4` than the probe did, so the per-candidate exact
test dominates.  That is the next unit; the k = 2 class set is measured, not yet
shipped.

## The truncations, after this turn

`sage-extensions` on main at `0721851728` (a #310 commit, which carried these two
functions in from the shared tree) had three truncations. One is now gone:

- **`[:40]` per norm bucket — removed.** The nineteen wall tests run *before* the
  exact isometry test, so every vector of both buckets is now tried and the
  expensive part still sees only the chamber's vectors. Measured cost of removing
  it: the module's class enumeration is 106.08 s against 110.39 s with the slice,
  so the slice was buying nothing. `issue317-bound-full-buckets.log`.
- **`coordinate_bound = 10` and the norm floor `-40` — still there.** They are
  truncations, not proved bounds. What a proof needs, in the coordinates the code
  uses (`v = (a, b, x, y)`, `q(v) = 2ab + q(x) + q(y) = 2k`, `x, y` in the two
  `E8(-1)` blocks):
  - the sixteen walls inside the blocks are the E8 simple roots, so `b(r, x) >= 0`
    is `B x >= 0` componentwise — dominance, already used as the enumeration's
    restriction;
  - the three remaining walls carry the hyperbolic coordinates. For such a wall
    `r = (alpha, beta, p, q)` one has `q(r) = -2 = 2 alpha beta + q(p) + q(q)` with
    `q(p), q(q) <= 0`, so `alpha beta <= -1`: the two signs are opposite, and
    `b(r, v) >= 0` reads `alpha a + beta b + b(p,x) + b(q,y) >= 0`, where the two
    last terms are bounded by Cauchy--Schwarz in the definite blocks,
    `|b(p,x)| <= sqrt(|q(p)| |q(x)|)` and likewise for `y`, with
    `|q(x)| + |q(y)| = 2ab - 2k`.
  - Composing one wall with `alpha > 0 > beta` and one with `beta > 0 > alpha`
    bounds the ratio of `a` and `b`, not their size; closing the argument needs
    those three walls' actual coordinates and the resulting linear system in
    `(a, b)`. That is the remaining step, and until it is written the two bounds
    stay and the mass assertion stays as the guard.
  - What the closing runs actually needed, for calibration: `|a|, |b| <= 2` with
    E8 norms down to `-6` for k = 1, and `|a|, |b| <= 6` with E8 norms down to
    `-36` for k = 2, so the bound to prove is of that shape and much tighter than
    `10` and `-40`.
