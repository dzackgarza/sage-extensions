# The Scattone plane rows of `6JRX` and `6JRY` (#335, stage 1 of #317)

`isotropic_orbit_representatives(2)` on Scattone's degree-4 lattice returns the `O`
row of card `6JRY` (nine primitive isotropic plane orbits) and on the degree-2 lattice
the `O` row of `6JRX` (four). This note records what the cards say, the route the call
now takes, the nine classes the row is made of, and the runs.

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
`tests/lattices/test_scattone_plane_orbits.sage` reads them by tag through
`card_plane_orbit_row("6JRY", "O")` and `card_plane_orbit_row("6JRX", "O")`.

## 2. The candidate route the call now takes

The rank-2 branch reads the planes from the lines, exactly as Scattone 5.4.7 does: it
classifies the `O(L)`-orbits of primitive isotropic lines (one class on both lattices,
the port's marking classes), and then, per line, reads the planes through it. The
certified split of `_hyperbolic_completion` — `L = ⟨v, f⟩ ⊕ M` at index one — makes the
plane classes through `v` the `O(K_v)`-orbits of primitive isotropic lines of the
reduction `K_v`, and that is where the old route lost the row: its candidates were the
port's `isotropic_vector_classes(K_v)`, the Lorentzian perfect-cell traversal of the
rank-19 Witt-index-one reduction, which passes the 6144 MiB tree guard at 84 s without
returning.

The candidates now come from the library's own chamber classification
`_chamber_genus_records` (`categories/lattices.py`), the walk #334 introduced for the
definite genus and closed with the Siegel mass. When the certified split's complement
`M` splits off one of `L`'s own generators as a summand `⟨g⟩` of square `−|det M|` at
index one — so `M = ⟨g⟩ ⊕ T` with `T = ⟨v, f, g⟩^⊥` even unimodular of signature
`(1, 17)`, hence `II_{1,17}` — the walk is run on the definite summand
`E8(−1)² ⊕ ⟨−|det M|⟩`, and each of its records supplies one candidate:

    E_u = ⟨v, φ(u) + g⟩,   φ : model → T the isometry the library's Isom constructs.

The vector is isotropic — `q(φ(u)) = |det M| = −q(g)` with `φ(u) ∈ T` orthogonal to
`g` — and its quotient is the record's own class: writing `x = a v + b f + t + μ g`
(`t ∈ T`), the conditions `b(x, v) = 0` and `b(x, φ(u) + g) = 0` force `b = 0` and
`t = μ φ(u) + s` with `s ∈ φ(u)^⊥` (the functional `b(−, φ(u))` is surjective with that
kernel because `φ(u)` is primitive in the unimodular `T`), so

    E_u^⊥ = ⟨v⟩ ⊕ ⟨φ(u) + g⟩ ⊕ φ(u)^⊥,   E_u^⊥/E_u ≅ φ(u)^⊥ ≅ u^⊥,

the record's complement. By Scattone 5.4.7 with 5.4.8(2) the candidates are therefore
one per plane class, and the walk's mass certificate — the class masses close on the
Siegel mass of the genus — is the completeness certificate of the plane family. No
coordinate box and no norm floor enters: the walk's bound is the one #334 proved from
the three hyperbolic walls, and the class the bounded sweeps of §4 could never reach
(544 roots, `|Aut| = 46620662575398912000`) is the ninth chamber vector of the
`k = 2` walk.

The identification is unchanged: the caller still collapses the candidates through
`_isotropic_equivalence_witness`, the exact plane equivalence, and §5's measurements of
that decision stand. A lattice whose complement exhibits no such `g` — or whose summand
the chamber walk does not serve — keeps the port's classification, which never returns
a partial family.

## 3. The nine classes of the row

`6JRY`'s `O` row is the class set of the genus of `N = ⟨−4⟩ ⊕ E8(−1)²` (rank 17, det 4,
negative definite), by Scattone 5.4.7 + 5.4.8(2). The chamber walk closes that genus
with the mass formula, so the following nine classes are complete and not a truncation:
the sum of `1/|Aut|` equals the mass `642332179/18881368343036559360000` exactly.

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

## 4. The bounded sweeps this route replaces

Two probes of the previous turn enumerated the planes by hand, over a coordinate box
in `(c, d, z)` and a norm floor in the `E8` blocks. With `|c|, |d| ≤ 3`, `|z| ≤ 2` and
norm `≥ −24` the enumeration exhibits five of the nine classes
(`.tmp/qc-evidence/issue335-probe4.log`); widened to `|c|, |d| ≤ 10` and norm `≥ −40` it
exhibits the classes of roots 244 and 304 as well and nothing of roots 544 before its
own cap stops it (`issue335-probe7.log`: 1525 candidates examined through `c = −6`,
`launcher exit: 124`, peak tree RSS 1307 MiB). Those truncations are what the chamber
route replaces: its bound is proved from the chamber's own walls (#334), and the height
walk ends at the Siegel mass, so no class is left behind and none is truncated.
`.scratch/issue335_probe9.py` checked the correspondence before it was wired in: for
every chamber vector `u` of both walks, the plane `⟨e₁, u + g⟩` has `E^⊥/E` of exactly
the record's `(roots, |Aut|)` — nine of nine at `k = 2`, four of four at `k = 1`, mass
exact, peak tree RSS 631 MiB (`issue335-probe9.log`).

## 5. The equivalence is not the defect

`.scratch/issue335_probe8.py` (`issue335-probe8.log`) takes five of those planes, whose
`E^⊥/E` classes are pairwise distinct (`|Aut|` 49662885888000, 106542032486400,
809053559193600, 129448569470976000, 1941728542064640000), and asks the call's own
identification `_isotropic_equivalence_witness` for each of the ten pairs: all ten
distinct, each pair 0.4–50 s. The call does not merge two classes; the loss, when there
was one, was in the classification that supplies the candidates, and that
classification is the chamber walk's now.

## 6. The runs

Every run below is one process in the adopted runtime (`~/sage-image/run.sh` with the
worktree at `.scratch/wt335` as the provider, the port bound at `/work` with its `src`
ahead, `peakrss` `PEAKRSS_LIMIT_MIB=6144`, `PYTHONPATH` set inside the inner shell).
The tree is the commit this turn pushes.

- **The correspondence, checked before it was wired in.** `.scratch/issue335_probe9.py`
  runs #334's walk by hand on both summands and asks, for every chamber vector `u`,
  whether the plane `⟨e₁, u + g⟩` has `E^⊥/E` of the record's own `(roots, |Aut|)`:
  nine of nine at `k = 2` — the ninth is the 544-root class the bounded sweeps never
  reached — and four of four at `k = 1`, mass exact in both, peak tree RSS 631 MiB
  (`.tmp/qc-evidence/issue335-probe9.log`).
- **The public call on both lattices.** `.scratch/issue335_probe10.py` calls
  `isotropic_orbit_representatives(2)` on the two card lattices and asserts every
  returned plane primitive of rank two and totally isotropic: `6JRX` four planes in
  946.1 s, `6JRY` nine planes in 1334.5 s, both equal to the cards' `O` rows read by
  tag, peak tree RSS 806 MiB (`.tmp/qc-evidence/issue335-probe10.log`,
  `issue335-probe10b.log`).
- **The genus regression.** `tests/lattices/test_genus_of_the_scattone_summands.sage`
  with the test lint: `8 passed in 542.44 s` (`.tmp/qc-evidence/issue335-genus-test.log`)
  — the walk refactor that exposes the chamber vectors leaves #334's module green.
- **The plane rows.** `tests/lattices/test_scattone_plane_orbits.sage` with the test
  lint, selected `-k 'orbits_under_o and not plus'`: `2 passed, 3 deselected in
  1298.46 s (0:21:38)`, peak tree RSS 881 MiB — both `O`-row tests green
  (`.tmp/qc-evidence/issue335-plane-o-test.log`).
- **The `O+` stop.** The full module in one process is killed by the standing
  6144 MiB tree guard during the `O+` tests: peak tree RSS 6179 MiB at 3253 s
  (`.tmp/qc-evidence/issue335-plane-test.log`). The `O+` route's own cost, measured
  alone on the degree-2 lattice (`.scratch/issue335_probe11.py`), is 5099 MiB at
  3600 s without completing — the subgroup machinery
  (`_subgroup_isotropic_orbit_representative`: per-plane stabilizer generators and
  splitting isometries) is the consumer, not the candidate route, which the `O`-row
  runs above carry at 881 MiB. Repairing that cost is #317's, not this stage's.


## 7. What this tree now does

`tests/lattices/test_scattone_plane_orbits.sage` reads both cards' `O` and `O+` rows by
tag and asserts the public calls against them; every returned plane is asserted
primitive of rank two and totally isotropic through the lattice's own pairing. The
`O+` rows go through `_subgroup_isotropic_orbit_representatives`, which starts from the
ambient `orthogonal_group.isotropic_orbit_representatives(rank)`, so the same candidate
route carries them.
