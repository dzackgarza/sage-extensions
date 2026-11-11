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
