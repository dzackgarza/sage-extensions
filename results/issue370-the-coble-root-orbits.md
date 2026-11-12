# #370 — the `Gamma_{Co,2}`-orbits of the admissible roots of `K_I` at a marked 0-cusp of `T_Co`

Stage 2, named by research#760 (the dr2i turn of 2026-11-12).  The first part of this file was
measured on the adopted runtime (Sage 11.0.beta5, source pin `9f1680d2a7bcf001e50714768e6066e6652d1708`)
in a worktree of `omm/main = 8e88c6a1c5`; sections 5 and 6 were added on `omm/main = f7eaa5d976`
(sage-extensions#298's isometry in it) in a worktree of that head.

**Result.** The call exists and returns: `IsotropicVectorReductionImage.root_class_orbits` with
`root_class`.  At `T_Co`'s cusp **3** the boundary lattice `K_I` has **one** root class and its orbit
is itself, the transporter being the identity; the acting family is `Gamma_{Co,2}`'s own line
stabilizer, 16 of whose 31 generators are certified in `G_v`, and it does act non-trivially on that
class.  Cusps **4** and **5** were blocked in the first part by missing input: the printed root
families of Sterk's diagrams 4.3.8 and 4.3.9 were not in the library in `T_En`/`T_Co` coordinates.
Section 5 carries both families into `T_En`, section 6 runs the orbits: at `T_En`'s cusps 4 and 5 the
eleven and fourteen printed roots give eleven and fourteen distinct classes of `K_J`, of which two
and four are roots, and `Gamma_{En,2}`'s stabilizer returns them as two and four orbits with their
transporters; at `T_Co`'s cusp 5 eleven of the fourteen lie in `T_Co`, three are roots, and
`Gamma_{Co,2}` returns three orbits.  `T_Co`'s cusp 4 is the one place where the printed family's
identification with `K_I` is **not** pinned by anything the library holds (§5), so its root count and
orbits are reported as one identification's and are not asserted.

## 1. The call

`src/sage_extensions/categories/isotropic_orbits.py`, on `IsotropicVectorReductionImage`:

- **`root_class(vector)`** — the class in `K_I = v^perp/ZZ v` of a root written in the *ambient*
  lattice, computed by writing the vector in the reduction's own frame together with `v` and
  projecting, with the remainder checked to be an integral multiple of `v`.  This is what lets
  Sterk's printed cusp roots, which are ambient vectors, be fed to the orbit call.
- **`root_class_orbits(roots, *, stabilizer_generators=None)`** — the orbits of a finite family of
  **root classes** of `K_I` under the certified action, each with a **transporter**: one isometry of
  `K_I` per class, carrying the orbit's representative to it and checked by re-application.  The
  acting family is the certified reductions of `stabilizer_generators` (the family
  `supergroup().isotropic_stabilizer_generators(line)` returns — the action of the stabilizer of
  `ZZ eta_I` this issue asks for) together with the certified reflections of the given classes;
  membership is decided by `contains`, the discriminant criterion of #312, never by listing `G_v`.
  A class that is not a root (square not `-2`) is **refused**, so a `(-4)`-wall cannot enter a root
  family.

What a returned orbit proves: an orbit with more than one class is a proof that the two roots are
`Gamma_{Co,2}`-equivalent, by an exhibited transporter.  A singleton is *not* a proof of
inequivalence, because the acting family is not certified to generate `G_v` at a primitive isotropic
line (`generators_are_certified_complete()` is `False`, #312).  The call says so in its docstring;
research's question ("whether two roots that cut the same object are inequivalent") is therefore
answered positively by an identification and only negatively once a generating family of `G_v` is
certified.

## 2. The known family and the card
Card `029J`, row `integral.cusp_chambers.gamma-en-2`, read by tag (digest pin
`dbc9fc6add622459d60dba3dc62d3e4be6b903d7` of `dzackgarza/lattice-database`): Sterk's diagrams
4.3.5–4.3.9 (Math. Z. 207 (1991), pp. 19, 21, 22, 23, 24) with **12, 10, 12, 11, 14** walls.  The
first part of this file read the last count as 13; the digest at the pin above states 14, and the test
reads the row by tag, so the card wins.

| cusp | card walls | printed roots as `T_En` vectors | distinct classes of `K_J` (computed) | of square `-2` |
| --- | --- | --- | --- | --- |
| `Sterk_1` (4.3.5) | 12 | 12 (`Sterk.sterks_in_TEn`, hand-read) | **12** | 0 |
| `Sterk_2` (4.3.6) | 10 | 10 | **10** | 2 (`±delta`, not in `T_Co`) |
| `Sterk_3` (4.3.7) | 12 | 12 | **12** | 1 (`delta`-orthogonal: the `T_Co` root) |
| `Sterk_4` (4.3.8) | 11 | 11 (`Sterk.cusp_roots_in_TEn`, §5) | **11** | 2 |
| `Sterk_5` (4.3.9) | 14 | 14 (§5) | **14** | 4 |

So the reduction merges no two printed walls at any of the five cusps, and the class count equals the
card's wall count — a computed value compared with a card value read by tag.  `root_class` and
`class_lift` are checked against each other on the chamber wall family of `K_J` at the first cusp.

**The missing card.**  No lattice-database card holds the **orbit counts** of the root classes.  The
row that would carry them, and that this unit's values would fill, is
`029J.cusp_root_orbits.gamma-en-2` — per cusp: the number of `Gamma_{Co,2}`-orbits of the root
classes, one representative per orbit, and the order of the transporter group — plus the same row on
the `T_Co` card for cusps 3–5.  It is named here for filing on `dzackgarza/lattice-database`; the
agent's GitHub connection reads issues and cannot create them.

## 3. `K_I` at `T_Co`'s cusps 3–5, and why the chamber is not the root family

The cusp representatives are `Sterk.selected_isotropic_vectors()`', read in `T_Co`: they have equal
`e` and `f` coefficients, hence lie in `T_Co = delta^\perp` with that coefficient on `h`.  All three
are primitive isotropic of divisibility 2.  At cusps 3 and 5 the library's vector is the card's row
too; at cusp 4 it is not — §5.

| cusp | `K_I` | `O(K_I)`'s fundamental chamber | `(-2)`-walls | line stabilizer of `G_v` |
| --- | --- | --- | --- | --- |
| 3 | rank 9, det 512, signature (1,8) | 9 walls | 1 | 31 generators, 16 certified (`19 s` + `159 s`) |
| 4 | rank 9, det 512, signature (1,8) | 9 walls | 1 | 37 generators (25.0 s, §6) |
| 5 | rank 9, det 512, signature (1,8) | 9 walls | 1 | 65 generators (38.5 s, §6) |

The chamber of `K_I` has nine walls — eight of square `-4` and one of `-2` — at each of the three
cusps, re-measured at the library's cusp vectors (22 s for all three), so it does **not** supply the
admissible roots: those are the `(-2)`-classes.  That is why the root family has to come from the
cusp's printed diagram, and why the refusal in §1 matters.

## 4. The run at `T_Co`'s cusp 3

`Gamma_{Co,2} = R_{Gamma_{En,2}}` built by #358's construction (`discriminant_point_stabilizer` at
`A_{U(2)}`), 122–160 s.  Its line stabilizer at the cusp returns 31 generators in 21.5 s, of which
**16** are certified in `G_v` in 159 s (`rho(K_v)` is trivial at this cusp, so one lift decides
membership).

Of Sterk's twelve printed roots at cusp 3, **nine** are orthogonal to `delta`: eight of square `-4`
and **one** of square `-2`.  That one — the record's `cusp 3: 12` — is the single root class of
`K_I` that `T_Co` sees, and

```
root_class_orbits((class,), stabilizer_generators=the line stabilizer)  ->  1 orbit
    orbit: {class -> identity transporter}
```

with the identity checked to carry the class to itself.  The action is not vacuous: some certified
generator moves the class on `K_I`, and it is dropped from the walk only because its image leaves
the given family of one class.  At cusps 4 and 5 the record's `T_Co` roots are one and three
classes (`cusp 4: 10`; `cusp 5: 12, 13, 14`); §5 finds the printed families that give them and §6
runs the orbits there.

## 5. Cusps 4 and 5: the printed roots carried into `T_En`, and the two identifications

`Sterk.cusp_roots_in_TEn(name)` (`src/sage_extensions/sterk.py`) returns the printed roots of all
five diagrams as vectors of `T_En`.  The first three are the hand-read table `sterks_in_TEn`; the
other two are printed in coordinates of a *model* of `K_J`, and each is carried over by an
identification of lattices that the method checks rather than assumes.

**Cusp 5 (4.3.9, p. 24) — an isometry of lattices, and sage-extensions#298's statement.**  The
fourteen roots are printed in `U + E8(-2)` (`sterk5_in_U_E8_2`), a lattice of rank 10, determinant
`-256`, signature `(1, 9)`, even — the same as `K_J` at that cusp.  So the model *is* the boundary
lattice, which is an isometry question, and the library's own call decides it:
`is_isometric_to` answers `True` in **9.0 s**, and `isometry_matrix_to` returns the witness in
**3.14 s** (and **6.19 s** in a second run) with determinant `±1`.  The library also holds a specific
map, `Embeddings.U_E8_2_into_TEn`, whose image lies in `eta^perp` (all fourteen pairings with the cusp
vector are zero) and whose `14 x 14` Gram matrix is the model's (asserted in `cusp_roots_in_TEn`), so
composing it with `K_J`'s projection is an isometry onto `K_J`.  That map is the one used: it is a
single map the library states, not one of the `O(K_J)`-many the isometry call may return.

**Cusp 4 (4.3.8, p. 23) — an embedding, not an isometry.**  The eleven roots are printed in
`II_{18,2}` coordinates (`Sterk.sterk_roots()["Sterk_4"]`), and no map into `T_En` carries them.
Their span is a rank-ten lattice of determinant `-1024` (`TdP.sublattice_from`, 0.13 s), signature
`(1, 9)`, even: an **index-two** sublattice of `K_J` (determinant `-256`).  So the identification is
an isometric *embedding*, and the isometry call correctly reports the two lattices as not isometric
(`False`, 0.0 s).  The embedding is the lattice embedding Mor's own: `span.Emb(K_J)` is nonempty in
**181.6 s / 189.6 s / 248.3 s** across runs, its witness comes in **2.2 s**, and its matrix has
determinant `2`.  The eleven transported classes keep the printed roots' pairwise pairings (asserted)
and are all orthogonal to the cusp vector.

**The two lines at 4.3.8, and which one carries the diagram.**  Card `029J`'s `cusp` field for that
row is `(0, 0, 2, 1, -4, -5, -7, -10, -8, -6, -4, -2)`, while the library's
`Sterk.selected_isotropic_vectors()["Sterk_4"]` is `(0, 0, 1, 2, -4, ...)`: two isotropic vectors of
`T_En` whose pairing is `2`, so they span **different** lines.  Of the two only the library's carries
the diagram: the eleven printed roots pair with the card's line as
`[-6, 14, -8, 14, 6, 8, 12, 0, -6, -6, -12]` and with the library's line as all zeros.  The wall
counts read by tag do not depend on it, but the reading of the roots does, so `Sterk.cusp_roots_in_TEn`
uses the library's cusp vector and `_coble_cusp_image` in the test does too.  (This is the discrepancy
already recorded for card 4.3.8; it is still undecided, and what is missing is whether the two lines
are `Gamma_{En,2}`-equivalent.)

**What the identification does not fix.**  Any element of `O(K_J)` composes with the identification,
and the classes it produces need not be conjugate under the acting group.  For cusp 5 the map is a
single library-stated embedding, so its classes are determined.  For cusp 4 the embedding is one of
`O(K_J)`-many, and the two runs this unit measured did not agree: one gave **9** of the eleven roots
lying in `T_Co` with **1** root class of `K_I`, the other **8** with **2**.  So at cusp 4 the number
of printed *classes* of `K_J` (11, card-compared) is a statement about the diagram, while the number
of root classes of `K_I` and their orbits are statements about the identification.  What would pin it
is not in the library: either Sterk's figure 10 read into `T_En` coordinates by hand, as figures 8
are for `sterks_in_TEn`, or a certificate that the identified roots are the chamber's walls
(`admits_root` for all eleven), which an arbitrary index-two embedding does not satisfy.

## 6. The runs at cusps 4 and 5

**In `K_J`, under `Gamma_{En,2}`'s line stabilizer.**  The classes of the printed family, and the
`(-2)` ones among them, are identification-free counts:

| cusp | `K_J` | classes of the printed roots | roots of `K_J` | stabilizer generators | `root_class_orbits` |
| --- | --- | --- | --- | --- | --- |
| 4 | rank 10, det `-256` | **11** | **2** | 34 (39.6 s) | **2** orbits, one class each (168.6 s) |
| 5 | rank 10, det `-256` | **14** | **4** | 45 (41.6 s) | **4** orbits, one class each (12.8 s) |

Two and four orbits of one class each: the printed walls are pairwise inequivalent under the acting
family, which is what a chamber's walls are expected to be — but a singleton is **not** a proof of
inequivalence, since `generators_are_certified_complete` is `False` at a primitive isotropic line
(sage-extensions#312).  No orbit count is asserted anywhere, and no lattice-database card holds one.

**In `K_I`, under `Gamma_{Co,2}`.**  At cusp 5 the boundary lattice is rank 9, determinant `512`,
signature `(1, 8)`; **11** of the fourteen roots lie in `T_Co`, **3** of the classes are roots of
`K_I`, the line stabilizer returns **65** generators (38.5 s), and `root_class_orbits` returns **3**
orbits of one class each (25.6 s).  Those three are the record's `cusp 5: 12, 13, 14`.  At cusp 4
(identification as in §5) **8** of the eleven lie in `T_Co`, 2 are roots, the stabilizer returns 37
generators (25.0 s) and the call returns 2 orbits of one class each (143.7 s) — the numbers of one
identification, and §5 is why they are not asserted.

`root_class_orbits` refuses a class of square other than `-2`, so the `(-4)`-walls of the printed
diagrams never enter a root family: the counts above are counts of roots, not of walls.

## 7. The test, the gate and the push

`tests/lattices/test_the_coble_root_orbits_at_a_marked_cusp.sage`, five tests:

1. the card comparison of §2 at all five cusps (12, 10, 12, 11, 14 distinct classes, read by tag);
2. the refusal of a `(-4)`-wall and the `root_class`/`class_lift` round trip;
3. the run of §4 at `T_Co`'s cusp 3, with its transporter and its non-vacuous action;
4. the orbits of the printed roots of 4.3.8 and 4.3.9 in `K_J` at `T_En`'s cusps 4 and 5, where the
   root count is compared with the number of `(-2)` printed roots and the orbits are checked to
   partition the classes with form-preserving transporters;
5. the orbits at `T_Co`'s cusp 5, the cusp whose identification is a single map the library states.

`results/issue298-the-lattice-isometry-matrix.md` states the isometry call the identification of
4.3.9 uses.

Measured, one session, with `-p qc_sage_session -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates` on both files of this batch:

```
8 passed in 906.94s (0:15:06)
  the printed cusp walls are distinct classes (five cusps)       213.60 s
  the coble cusp three has one root class                        359.16 s
  cusps four and five in K_J                                     243.86 s
  the coble cusp five in K_I                                      61.73 s
  the indefinite rank-eleven isometry matrix (#298)               23.91 s
```

and the #298 file alone: `3 passed in 28.42 s`.  No lint findings; both calls over the local 20 s call
ceiling are reported by the gate and not enforced.

**The missing card.**  No lattice-database card holds the **orbit counts** of the root classes.  The
row that would carry them, and that these values would fill, is `029J.cusp_root_orbits.gamma-en-2` —
per cusp: the number of orbits of the root classes, one representative per orbit, and the order of the
transporter group — plus the same row on the `T_Co` card for cusps 3–5.  It is named here for filing
on `dzackgarza/lattice-database`; the agent's GitHub connection reads issues and cannot create them.
