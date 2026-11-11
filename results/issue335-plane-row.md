# The Scattone plane rows of `6JRX` and `6JRY` (#335, stage 1 of #317)

`isotropic_orbit_representatives(2)` on Scattone's degree-4 lattice must return the `O`
row of card `6JRY` (nine primitive isotropic plane orbits) and on the degree-2 lattice
the `O` row of `6JRX` (four). This note records what the cards say, what the call does on
this tree, the nine classes the row is made of, and why the count cannot be returned yet.

## 1. What the cards say, and which group each row counts

Read at the pin the card digest uses, `dzackgarza/lattice-database` commit
`d6a539339bac5ea0ee8d8bde5dc19564955eb152`, `lattices/6JRX.md` and `lattices/6JRY.md`
— byte-for-byte the same two cards as at `587d56febe5856d54c6bc9fc023fa5a425f76bfb`, the pin the digest carried when this
turn began, so the rows and their citations are unchanged:

| card | lattice | rank | signature | det | `A_L` | `O` | `O+` | `Otilde+` |
|---|---|---|---|---|---|---|---|---|
| `6JRX` | `Λ₂ = U ⊕ U ⊕ E8(−1)² ⊕ ⟨−2⟩` | 21 | (2, 19) | −2 | Z/2 | planes **4** | constant 1, planes 4 | constant 1 |
| `6JRY` | `Λ₄ = U ⊕ U ⊕ E8(−1)² ⊕ ⟨−4⟩` | 21 | (2, 19) | −4 | Z/4 | planes **9** | constant 1, planes 9 | constant 1 |

`Λ_k = ⟨−2k⟩ ⊕ H² ⊕ E8²` is Scattone's degree-`2k` lattice, equation (1.1.1), §1.1,
printed p. 3; in the cards' basis both `E8` summands are negative definite, so the
determinants are `−2` and `−4`.

The plane rows, with the citation as the cards give it:

* `O`: J. Scattone, *On the compactification of moduli spaces for algebraic K3
  surfaces*, Mem. AMS 374 (1987), **Proposition 5.4.7 with Corollary 5.4.8(2), p. 78** —
  `E ↦ E^⊥/E` is a bijection from the `O(L_k)`-orbits of primitive isotropic planes onto
  the classes `G(k)` of the genus of `⟨−2k⟩ ⊕ E8(−1)²`, so there are `h(k)` of them —
  with **§6.2 (Degree two), p. 97, (6.2.1)**: `G(1)` consists of four isomorphism classes
  for `6JRX`, and **§6.3 (Degree four), p. 100**: `G(2)` consists of nine for `6JRY`.
* `O+`: **§6, p. 94** — the Baily–Borel compactification of `D_k/O₋(L_k)` is
  `D_k/O₋(L_k)` plus one point and `h(k)` curves, so the plane counts equal the `O` rows.
  `O₋(L)` is the isometries of spinor norm 1 (§3.6, p. 50) and the index-two subgroup of
  `O(L)` preserving the component `D_k` of the period domain (§1, p. 3).
* `Otilde+`: **Theorem 4.0.1, p. 55** states `⌊(N+2)/2⌋` Type III components, one at
  `N = 1`, for `Γ_k = O~(L_k) ∩ O₋(L_k)` (§1, p. 4; §3.6, p. 51). The row is a **line**
  count and carries no plane row; the digest keeps only rows with a `planes` key.

The two numbers the acceptance compares against are therefore the cards' `O` rows, and
`tests/lattices/test_scattone_plane_orbits.sage` now reads them by tag through
`card_plane_orbit_row("6JRY", "O")` and `card_plane_orbit_row("6JRX", "O")` instead of
restating `4` and `9` in the test.

## 2. What the call does on this tree

Base: `7519715` (`main`), pinned port `991b88b0`, adopted runtime, `peakrss`
`PEAKRSS_LIMIT_MIB=6144`. The logs are `.tmp/qc-evidence/issue335-probe*.log`, and the
probes that produced them are `.scratch/issue335_probe*.py`.

The rank-2 branch of `_isotropic_orbit_representatives` (`categories/isotropic_orbits.py`)
reads the planes from the lines of `K_v = v^⊥/Zv` over the line classes, exactly as
Scattone 5.4.7 does. On `Λ₄` (`issue335-probe2.log`, `.scratch/issue335_probe2.py`):

```
[     0.2s] L: rank 21 det -4 signature (2, 19)
[    23.1s] 1 O(L)-orbits of primitive isotropic lines
[    23.9s]   line 0: split certified; v = [1, 0, ..., 0] plane basis -1
[peakrss] STOPPED_AT_MEMORY_LIMIT: tree RSS 6156 MiB exceeded 6144 MiB
[peakrss] issue335: child waited=143 shell_code=143 samples=43
```

The next step is `_planes_through_line`'s `INDUCTION.isotropic_vector_classes(K_v)` on the
rank-19 reduction `⟨−4⟩ ⊕ U ⊕ E8(−1)²`, signature (1, 18), the port's Lorentzian
perfect-cell route. It passes the 6144 MiB tree guard after 84 s. The same reduction in
the **card's own basis** (`.scratch/issue335_probe3.log`) costs 125.8 s for the line class
alone and the library's own classification of its isotropic vectors did not return in
fifteen minutes and was stopped; the port's perfect-cell route on the `k = 1` reduction
did not return in 2400 s at 1086 MiB in the earlier record (`results/issue286-batch.md`,
`TRAPS.md`).

**So the call does not return eight on this host; it does not return.** The `8` in #335
cannot be reproduced with the pinned port and the standing memory guard, and no list of
eight planes can be printed from it here. What can be produced is the class set itself,
by a route that does not go through the port.

## 3. The nine classes of the row

`6JRY`'s `O` row is the class set of the genus of `N = ⟨−4⟩ ⊕ E8(−1)²` (rank 17, det 4,
negative definite), by Scattone 5.4.7 + 5.4.8(2). #334's probe (`issue317-probe37.log`)
closes that genus with the mass formula, so the following nine classes are complete and
not a truncation: the sum of `1/|Aut|` equals the mass
`642332179/18881368343036559360000` exactly.

| # | roots of `E^⊥/E` | `|Aut(E^⊥/E)|` |
|---|---|---|
| 1 | 544 | 46620662575398912000 |
| 2 | 480 | 1371195958099968000 |
| 3 | 304 | 3767021862912000 |
| 4 | 244 | 334764638208000 |
| 5 | 204 | 49662885888000 |
| 6 | 224 | 106542032486400 |
| 7 | 384 | 129448569470976000 |
| 8 | 264 | 809053559193600 |
| 9 | 480 | 1941728542064640000 |

Class 9 is `N` itself, the plane `⟨e₁, e₃⟩` inside the two hyperbolic planes. For `6JRX`
the same row is the four classes of `⟨−2⟩ ⊕ E8(−1)²`: `(482, 1371195958099968000)`,
`(306, 12804747411456000)`, `(306, 5393690394624000)`, `(482, 1941728542064640000)`,
mass `2499347/9440684171518279680000` exact.

## 4. The planes themselves, and the one class a bounded search does not exhibit

`.scratch/issue335_probe4.py` and `.scratch/issue335_probe7.py` build the planes without
the port. By the certified split, every plane class is `⟨e₁, w⟩` with `w ∈ K_v` isotropic
and `w = c e₃ + d e₄ + n`, `n ∈ N`, `q(n) = −2cd`, so `E^⊥/E` is computed exactly by
integer linear algebra. Two candidates are the same class when their `LLL`-reduced Gram
matrices are equal — an equal Gram **is** an isometry, so that dedupe can never merge two
classes (`issue335-probe4.log`, `issue335-probe7.log`).

With `|c|, |d| ≤ 3`, `|z| ≤ 2` and both `E8` blocks dominant with norm ≥ −24 the
enumeration exhibits five of the nine classes and no others:

```
  class roots 204 |Aut| 49662885888000        from w = [0, 0, -3, -3, -5, -10, -15, -12, -9, -6, -3, -8, -4, -8, -12, -10, -8, -6, -3, -6, -1]
  class roots 224 |Aut| 106542032486400       from w = [0, 0, -3, -3, -4, -7, -10, -8, -6, -4, -2, -5, -6, -11, -16, -13, -10, -7, -4, -8, -1]
  class roots 264 |Aut| 809053559193600      from w = [0, 0, -3, -3, -4, -8, -12, -10, -8, -6, -4, -6, -4, -8, -12, -10, -8, -6, -3, -6, -1]
  class roots 384 |Aut| 129448569470976000   from w = [0, 0, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, -7, -14, -20, -16, -12, -8, -4, -10, -1]
  class roots 480 |Aut| 1941728542064640000  from w = [0, 0, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, -2, -4, -6, -5, -4, -3, -2, -3, -2]
k = 2: mass 657131/21359013962711040000 vs 642332179/18881368343036559360000: SHORT
```

The shortfall is exactly the sum of the four shares the enumeration does not reach,

    642332179/18881368343036559360000 − 657131/21359013962711040000
      = 6067/1864826503015956480
      = 1/46620662575398912000 + 1/1371195958099968000 + 1/3767021862912000 + 1/334764638208000,

so the five planes are of the five classes named and the four classes 1, 2, 3 and 4 of §3
— roots 544, 480 with `|Aut|` 1371195958099968000, 304 and 244 — have no plane in the box.
Widening the box to `|c|, |d| ≤ 10` with norm ≥ −40, which is the bound #317's shipped
chamber route uses, exhibits the classes of roots 244 and 304 as well
(`issue335-probe7.log`: `roots 244 rep 1` at 111.0 s, `roots 304 rep 1` at 115.0 s), and
in the 1525 candidates it examines through `c = −6` it exhibits nothing of roots 544, and
the run was then stopped by its own 3000 s inner cap (`launcher exit: 124`, peak tree RSS
1307 MiB). So the class no enumeration here reaches is the one whose `E^⊥/E` has 544
roots, `|Aut| = 46620662575398912000`, the first row of §3; a bounded sweep that reaches it
costs more than the guard allows, which is the same statement as §6 in cost form.

## 5. The equivalence is not the defect

`.scratch/issue335_probe8.py` (`issue335-probe8.log`) takes five of those planes, whose
`E^⊥/E` classes are pairwise distinct (`|Aut|` 49662885888000, 106542032486400,
809053559193600, 129448569470976000, 1941728542064640000), and asks the call's own
identification `_isotropic_equivalence_witness` for each of the ten pairs:

```
  roots 204 vs 224: distinct in 50.0s
  roots 204 vs 264: distinct in 31.4s
  roots 204 vs 384: distinct in 30.1s
  roots 204 vs 480: distinct in 30.1s
  roots 224 vs 264: distinct in 1.7s
  ... all ten distinct
```

So the call does not merge two classes; the exact plane equivalence answers correctly and
each pair costs 0.4–50 s. The loss, when there is one, is in the classification that
supplies the candidates.

## 6. What a repair needs

The candidates come from one place: `INDUCTION.isotropic_vector_classes(K_v)` — the
`O(K_v)`-orbits of the primitive isotropic vectors of a rank-19 lattice of Witt index one.
The reduction's own split is certified (`det L = det⟨v,f⟩·det⟨v,f⟩^⊥`, `−1` against
`−2k`), which is what makes the image of `Stab_{O(L)}(v)` all of `O(K_v)`, so that
classification, and only it, decides the plane count.

Neither in-tree route to it returns here: the port's Lorentzian perfect-cell traversal
passes the memory guard at 84 s on `k = 2` and did not return in 2400 s on `k = 1`, and
the library's own marking-class classification of the same rank-19 lattice did not return
in fifteen minutes. A hand-rolled enumeration is what §4 runs, and it terminates on a
coordinate bound and a norm floor — precisely the truncations #334 must replace with a
proved bound, after which the same enumeration closes the mass and the call may return the
row. Until then a plane call that returned a number would be returning either a bounded
search's partial family or a count from a classifier that does not finish.

## 7. What this tree now does

`tests/lattices/test_scattone_plane_orbits.sage` reads both cards' `O` and `O+` rows by tag
and asserts the public calls against them; it is red for `6JRY` and for `6JRX` because the
call does not return the row. The `O+` rows are split out of the same call —
`_subgroup_isotropic_orbit_representatives` starts from
`orthogonal_group.isotropic_orbit_representatives(rank)` — so they are blocked by the same
classifier. `python -m pytest tests/lattices/test_scattone_plane_orbits.sage
-k test_the_card_inputs -p sage_extensions.testing.test_lint` collects five tests, runs the
invariant-only one (1 passed, 4 deselected) and the test lint reports no findings.
