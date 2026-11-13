# #370 — the `Gamma_{Co,2}`-orbits of the admissible roots of `K_I` at a marked 0-cusp of `T_Co`

Stage 2, named by research#760 (the dr2i turn of 2026-11-12).  Measured on the adopted runtime
(Sage 11.0.beta5, source pin `9f1680d2a7bcf001e50714768e6066e6652d1708`) in a worktree of
`omm/main = a5fa20dc63`.

**Result.** `IsotropicVectorReductionImage.root_class_orbits` with `root_class` returns the orbits at
all three cusps of `T_Co` where Sterk's printed diagram meets it.  At cusp **3** `K_I` has one root
class and its orbit is itself; at cusp **4** the eleven walls of Fig. 10 give nine classes of `K_I`,
one of them a root, and `Gamma_{Co,2}`'s line stabilizer returns that class as one orbit with its
transporter; at cusp **5** eleven of the fourteen walls lie in `T_Co`, three are roots, and the
stabilizer returns three orbits with their transporters.

**Every vector is the card's, and cusp 4's is the chamber's.**  Each cusp vector and every wall is
read from card `029J`'s `integral.cusp_chambers['gamma-en-2']` row for that diagram, by tag, and
`Sterk.cusp_roots_in_TEn` reproduces the same vectors from Sterk's printed formulas; the two are
compared wall for wall by the test.  Nothing is searched for, so a run makes no choice and two runs
agree.  Cusp 4 is where that matters: the paper prints **two** vectors for that cusp — (4.2.3), p. 16,
lists `e' + 2f' + γ` among the five cusp representatives, and (4.3.8), p. 23, draws the chamber at
`2e' + f' + ᾱ₁` — and the eleven walls of Fig. 10 are orthogonal to the second only.  The card's row
stores the second, so the chamber is read there.

## 1. The call

`src/sage_extensions/categories/isotropic_orbits.py`, on `IsotropicVectorReductionImage`:

- **`root_class(vector)`** — the class in `K_I = v^perp/ZZ v` of a root written in the *ambient*
  lattice, computed by writing the vector in the reduction's own frame together with `v` and
  projecting, with the remainder checked to be an integral multiple of `v`.
- **`root_class_orbits(roots, *, stabilizer_generators=None)`** — the orbits of a finite family of
  **root classes** of `K_I` under the certified action, each with a **transporter**: one isometry of
  `K_I` per class, carrying the orbit's representative to it and checked by re-application.  The
  acting family is the certified reductions of `stabilizer_generators` (the family
  `supergroup().isotropic_stabilizer_generators(line)` returns) together with the certified
  reflections of the given classes; membership is decided by `contains`, the discriminant criterion of
  #312, never by listing `G_v`.  A class that is not a root (square not `-2`) is **refused**, so a
  `(-4)`-wall cannot enter a root family.

An orbit with more than one class is a proof that its roots are `Gamma_{Co,2}`-equivalent, by an
exhibited transporter.  A singleton is *not* a proof of inequivalence, because the acting family is
not certified to generate `G_v` at a primitive isotropic line (`generators_are_certified_complete()` is
`False`, #312); the call's docstring says so.

## 2. Sterk's coordinates are `T_En`'s

H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991),
1.2--1.4, pp. 3--4: `L = H³ ⊕ E8(-1)²` is the K3 lattice, `M = H ⊕ E8(-1)`, the covering involution is
`I:(m,m',h) ↦ (m',m,-h)`, and the anti-invariant part is `L_- ≅ H ⊕ M(2) = H ⊕ H(2) ⊕ E8(-2)` — the
library's `T_{En} = U ⊕ U(2) ⊕ E8(-2)`, with `e, f` the `H`, `e', f'` the `H(2)` and `α₁, …, α₈` the
`E8(-2)`, in the library's labels `e, f, ep, fp, a1, …, a8`.  So a vector Sterk prints in those letter
names is a vector of `T_En`, and the transcription of a printed family needs no map at all.

That is what the cusp-4 step now is.  (4.3.8), p. 23 prints, for `v = 2e' + f' + ᾱ₁`:

- a basis of `v^⊥/ℤv ≅ H ⊕ E8(-2)`: `e, f, -e' + α₁, α₂, …, α₈`;
- the eleven walls of Fig. 10 as explicit vectors of `L_-`: `α₂, …, α₈`, `α₉ = f - e`,
  `α₁₀ = ᾱ₈ + 2e'`, `α₁₁ = e + f + α₁ - e'`, `α₁₂ = 2e - 2e' + ᾱ₈ - ᾱ₁`;
- and (4.3.10, p. 25) that they span `ℤ{e + f, e - f} ⊕ E8(-2)`.

`ᾱ₁` is the `(-8)`-vector of Fig. 3, p. 19 (4.3.4), whose coefficients that figure prints node by node
— `4, 7, 10, 8, 6, 4, 2` along `α₁—α₃—α₄—α₅—α₆—α₇—α₈` and `5` on `α₂` — which in the library's
negative-definite `E8(-2)` is `-4a₁ - 5a₂ - 7a₃ - 10a₄ - 8a₅ - 6a₆ - 4a₇ - 2a₈`.  `ᾱ₈` is the one
`E8(-2)` vector the formulas name without coefficients; it is
`-2a₁ - 3a₂ - 4a₃ - 6a₄ - 5a₅ - 4a₆ - 3a₇ - 2a₈`, the only vector for which the eleven printed
vectors have the pairings Fig. 10 draws.

`Sterk._sterk4_in_TEn_cached()` is that transcription, and it checks what Sterk states instead of
assuming it: `ᾱ₁` has square `-8` and `ᾱ₈` square `-4`; `v` is isotropic and primitive and is a
different line from (4.2.3)'s representative, pairing `2` with it; all eleven walls lie in `v^⊥` with
the figure's squares; their diagram equals, as a matrix, the library's own `II_{18,2}` realization of
Fig. 10 in the vertex order the labels give it; and their span has determinant `-1024`, index two in
`K_J` (`-256`), as (4.3.10) says.

## 3. The two vectors of the fourth cusp, and the card

"The chamber is at the second vector, and the cusp is either":

| source | fourth-cusp vector |
| --- | --- |
| Sterk, (4.2.3), p. 16 | `e' + 2f' + γ`, `γ` of square `-8` — `(0, 0, 1, 2, -4, …, -2)` |
| Sterk, (4.3.8), p. 23, Fig. 10 | `2e' + f' + ᾱ₁` — `(0, 0, 2, 1, -4, …, -2)` |
| card `029J`, `cusp_chambers` row `4.3.8` | `(0, 0, 2, 1, -4, -5, -7, -10, -8, -6, -4, -2)` |

The two pair to `2` and span different lines: all eleven walls of Fig. 10 are orthogonal to
`2e' + f' + ᾱ₁`, while `α₁₀, α₁₁, α₁₂` pair `4, -2, -4` against `e' + 2f' + γ`.  The page prints the
basis of `v^⊥/ℤv` too, and it is orthogonal to `2e' + f' + ᾱ₁` alone, so the statement, its printed
basis and its figure agree.  Both vectors are representatives of one cusp — the reduction at either is
the same lattice, which `tests/lattices/test_cusp_lattices.sage` asserts — and a reduction read at
either is the cusp's; only the second carries Fig. 10.

So `Sterk.selected_isotropic_vectors()` keeps (4.2.3)'s, which is what a *cusp* is, and
`Sterk.sterk4_cusp_vector()` is the chamber's, which is what the card stores and what the tests read
for cusp 4.  Both docstrings state both vectors with their pages.  This was filed as
`dzackgarza/lattice-database` #44 and closed there.

## 4. What the identification was, and why the runs disagreed

Cusp 4's span used to be matched inside `K_J` by the lattice embedding Mor: an isometric embedding of a
rank-ten lattice of determinant `-1024` into one of determinant `-256`, i.e. one of `O(K_J)`-many maps,
chosen by the engine.  Its image depended on that choice, so two runs of the same code gave nine and
eight walls of `K_I` and two and one root classes.  The choice existed only because the anchor was
(4.2.3)'s vector, which is not the line Fig. 10 belongs to; at the correct line no embedding is needed,
since the walls are already vectors of `T_En`.

The runs now: the cusp-4 probe (`issue370-cusp-four-determinism-probe.py` in `.tmp/qc-evidence/`),
run twice in two separate processes, printed the same eleven walls, the same nine classes of `K_I` —
`[1, -2, -4, -6, -8, -10, -7, 2, 0]`, six unit vectors and `[1, -4, -7, -10, -13, -16, -11, 4, 0]` —
the same single root class `[-2, 4, 8, 12, 16, 20, 14, -5, 1]`, the same 37 stabilizer generators and
**one orbit with its transporter**, and the two logs agree line for line once their timings are
removed (`issue370-cusp-four-determinism-run1.log`, `-run2.log`).  Runs before the anchor was fixed, of
the embedding route, gave nine and eight walls; no log of theirs is kept, which is why the claim here
rests on the two runs that are.

## 5. The runs

**`K_J`, under `Gamma_{En,2}`'s line stabilizer** (rank 10, determinant `-256`):

| cusp | card walls | classes of the walls | roots of `K_J` | stabilizer generators | `root_class_orbits` |
| --- | --- | --- | --- | --- | --- |
| 4 | 11 | **11** | **2** | 34 (39.6 s) | **2** orbits, one class each (168.6 s) |
| 5 | 14 | **14** | **4** | 45 (41.6 s) | **4** orbits, one class each (12.8 s) |

**`K_I`, under `Gamma_{Co,2}`** (rank 9, determinant `512`, signature `(1, 8)` at all three cusps):

| cusp | walls in `T_Co` | roots of `K_I` | stabilizer generators | `root_class_orbits` |
| --- | --- | --- | --- | --- |
| 3 | 9 of 12 | **1** | 31, 16 certified (21.5 s + 159 s) | **1** orbit, the identity transporter |
| 4 | 9 of 11 | **1** | 37 (25.0 s / 57.5 s / 153.7 s across runs) | **1** orbit, the identity transporter (598.8 s) |
| 5 | 11 of 14 | **3** | 65 (38.5 s) | **3** orbits, one class each (25.6 s) |

The root counts are the record's `cusp 3: 12`, `cusp 4: 10` and `cusp 5: 12, 13, 14`.  Two and four
orbits of one class each in `K_J`, one and three in `K_I`: the walls are pairwise inequivalent under
the acting families — but a singleton is **not** a proof of inequivalence, since
`generators_are_certified_complete` is `False` at a primitive isotropic line (#312).  No orbit count is
asserted anywhere, and no lattice-database card holds one.

`O(K_I)`'s chamber at each of the three cusps is nine walls, eight of square `-4` and one of `-2`
(22 s for all three), so the chamber does not supply the roots: those are the `(-2)`-classes, which is
why the family comes from the printed diagram and why the call's refusal of a `(-4)`-class matters.

## 6. The test, the gate and the push

`tests/lattices/test_the_coble_root_orbits_at_a_marked_cusp.sage`, four tests:

1. the card comparison of §2 at all five cusps — 12, 10, 12, 11, 14 distinct classes against the row's
   wall counts, read by tag — with every cusp vector taken from the card's own row;
2. the refusal of a `(-4)`-wall and the `root_class`/`class_lift` round trip;
3. the orbits of the walls of (4.3.8) and (4.3.9) in `K_J`, where the card's `wall_vectors` and Sterk's
   transcription are asserted equal as sets, the root count is compared with the number of `(-2)` walls,
   and the orbits are checked to partition the classes with form-preserving transporters;
4. the orbits at `T_Co`'s cusps 3, 4 and 5 in one run — the card's cusp vector read in `T_Co`, the
   classes of the walls, the roots of `K_I`, the line stabilizer's own generators, and
   `root_class_orbits` with its transporters, plus the cusp-3 non-vacuity check.

The digest now carries each wall: `tests/cards/refresh_lattice_database_enriques.py` projects the
card's per-wall `vector` into the `cusp_diagrams` rows as `wall_vectors`, and the digest was
regenerated at the database ref it already recorded, `1e1cadcfdca4dba2c0084a0bdc095b2d691126a8`, so
nothing else in it moved.

Measured, one session of the adopted runtime with `-p qc_sage_session
-p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --no-time-gates`, on the
tree of this push:

```
4 passed in 3429.24s (0:57:09)
  the printed cusp walls are distinct classes (five cusps)       154.07 s
  the cusps four and five in K_J (T_En)                          698.21 s
  the coble cusps three, four and five in K_I (T_Co)            2557.82 s
```

No lint findings; the three calls over the local 20 s call ceiling are reported by the gate and not
enforced.  The VM was carrying several other chats' jobs throughout — the same file took 1607 s two
turns ago and this cusp-4 orbit call alone takes 408 s on an idle machine — so the wall-clock numbers
are this session's, not the calls'.  Each test also passes on its own (`-k` selections: 580.35 s,
408.73 s, 224.11 s).

The consumer files touched by the digest change both pass:

```
tests/lattices/test_cusp_lattices.sage                                              11 passed in 72.81 s
tests/lattices/test_the_isotropic_reduction_image.sage -k card_029j                  1 passed in 98.65 s
```

The first asserts that all five Sterk cusps reduce to their recorded Nikulin types and that cusps 2–5
reduce to isometric lattices, so it is where "the two vectors of the fourth cusp are one cusp" is
checked.  The second is the card comparison that must still find four agreements.  The rest of that
file is untouched by this change — it compares no card row and no synthetic `Sterk_4` — and its
Vinberg chamber test is not part of this batch.

**The missing card.**  No lattice-database card holds the **orbit counts** of the root classes.  The
row that would carry them is `029J.cusp_root_orbits.gamma-en-2` — per cusp, the number of orbits of
the root classes, one representative per orbit, and the order of the transporter group — plus the same
row on the `T_Co` card for cusps 3–5.  It is named here for filing on `dzackgarza/lattice-database`;
the agent's GitHub connection reads issues and cannot create them.
