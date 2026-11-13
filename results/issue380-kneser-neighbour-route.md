# #380 — The Kneser 2-neighbour route returns the isometry

Continues `results/issue380-neighbour-source-and-search.md` and
`results/issue380-port-free-isometry-routes.md`.  Branch `issue380`, worktree
`.scratch/wt380`, based on `omm/main = a5fa20dc63`.

**Status.** `isometry_to` returns the isometry
`2U ⊕ E8(−1)² → 2U ⊕ D16⁺(−1)` through a route of this library, and the test
`tests/lattices/test_two_u_recursive_isometry.sage` passes unchanged, its
third assertion green for the first time
(`.tmp/qc-evidence/issue380-test.log`: **3 passed in 423.56 s**, the target
test 422.68 s under `--no-time-gates`, at 611 MiB peak).

## 1. The route

The route lives in `LatticeIsometryMor._kneser_neighbour_isometry`
(`lattice_morphisms.py`), called from `an_element` before the port's covering
search.  Its scope is a pair of even unimodular indefinite `ZZ`-lattices of
equal rank that both split as `U + U + K` in their represented
decompositions, with even unimodular definite complements of equal rank; the
rank-16 case is the pair `E8(−1)²` / `D16⁺(−1)` on which deciding `2U + K` by
`K` fails.  Every decision inside is a computation on the Gram matrices, and
each source statement is cited with its printed page in Conway–Sloane, *Sphere
Packings, Lattices and Groups*, 3rd ed. (`.tmp/conway-sloane-splag-3rd-ed.pdf`,
read as text):

- **Preface to the Third Edition, Notes on Chapter 17, section "Neighbours",
  printed p. lv** ([Kne4], [Ven2], [Wan96]): for `u` in a unimodular `L` with
  `½u ∉ L` and `u·u ∈ 4ℤ`, the neighbour `L″ = L_u + ℤ(½u)` is unimodular,
  all unimodular neighbours of `L` arise in this way, and `L″` is even exactly
  when `u·u ∈ 8ℤ`.  The neighbour of the source's complement along the
  diagonal `w = v + v` of one norm-`−4`, divisibility-one vector `v` of one
  `E8(−1)` summand is computed, not assumed: its Gram matrix comes from the
  sublattice `K_w = {x ∈ K : x·w even}` and the half vector `w/2`
  (`_kneser_neighbour_gram`), and the class decision compares the order of its
  orthogonal group with the target complement's.

- **Ch. 26 §1, printed p. 525**: for an isotropic `u` of divisibility one in a
  unimodular Lorentzian lattice, `(u^⊥ ∩ Λ)/u` is an integral unimodular
  Euclidean lattice.  With `u = 2f + w + 2e` in the first `U + K` (the issue's
  `c = −(w·w)/4 = 2`), the quotient is the neighbour of the previous item, so
  its class is the target complement's; the member `M₁ = u^⊥ ∩ z^⊥` of the
  split exhibits it.

- **Ch. 17 §1, printed pp. 421–422**: neighbours are the lattices whose
  intersection has index 2 in each, and the orbits of primitive norm-0 vectors
  correspond to the even unimodular lattices of the complement.  The new basis
  `(u, z, M₁, e_b, f_b)` of the source and the images
  `(e_a′, f_a′, T₁₆, e_b′, f_b′)` compose into the column matrix of the
  isometry, and its equation is verified exactly before the witness is
  returned.

## 2. The measurements

On the adopted runtime (Sage 11.0.beta5, source pin `9f1680d2a7bc…`), from the
route probe `.tmp/qc-evidence/issue380-route.log`:

- the chosen `v` is `[3, 6, 9, 8, 6, 4, 2, 4]` — the **first** candidate of
  the norm-`(−4)` shell of one `E8(−1)` summand (2160 vectors, `qfminim`);
  `w = v + v` has `w·w = −8 ∈ 8ℤ` and `½w ∉ K`;
- the neighbour `K′ = K_w + ℤ(½w)` has `|O(K′)| = 685597979049984000`, the
  target complement `D16⁺(−1)`'s order — **the class of `D16⁺(−1)`**
  (`.tmp/qc-evidence/issue380-kneser-neighbour.log`, `.tmp/qc-evidence/issue380-assembly.log`);
- `u = 2e + 2f + w` is isotropic of divisibility one in `U + K`;
- `z = z₀ − (z₀²/2)u` with `z₀² = −2` satisfies `u·z = 1`, `z² = 0`;
- `M₁ = u^⊥ ∩ z^⊥` (the second `U`'s coordinates pinned to zero) has rank 16
  and is in the class of `D16⁺(−1)` — the same order again;
- the definite isometry `M₁ → K₂` (the library's own `Isom(...).an_element()`)
  has row matrix `T₁₆` of determinant `−1`, verified exactly:
  `T₁₆ G_{K₂} T₁₆^⊤ = G_{M₁}`;
- the assembled column matrix is placed by a unimodular change of basis
  (determinant 1) and verified exactly: `placed^⊤ G′ placed = G`;
- `isometry_to` returned the witness in 450 s (308 s for the decision, 142 s
  for the witness), and the acceptance equation `M^⊤ G M = G′` held exactly
  through the public API.

## 3. What the earlier 122-vector family could not do

The earlier chat's 122 isotropic vectors of divisibility one in `L₁` all left
the quotient in the class of `E8(−1)²` — the class of the definite block the
vector was built from — because `L₁ = II_{1,17}` has Witt index one and
Eichler's criterion (which needs two hyperbolic planes) does not apply.  The
`D16⁺(−1)` class is reached only by a vector that is not written in the
coordinates of the `E8(−1)²` factor: the Kneser neighbour of the complement
along the diagonal `w = v + v`, whose half `w/2` lies in the common sublattice
that Ch. 17 §1 (printed p. 421) puts at index 2 in each of `E8(−1)²` and
`D16⁺(−1)`.

## 4. The scope guard

The route refuses a pair whose signature is definite (one part zero) — the
definite route owns those — and serves the indefinite pair the test names.  An
earlier draft of the guard refused the indefinite pair instead, and the flow
fell to the port's covering search, which does not return (measured: 30 min
without a witness, `.tmp/qc-evidence/issue380-route.log` of that run).
