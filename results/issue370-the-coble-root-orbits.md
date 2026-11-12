# #370 — the `Gamma_{Co,2}`-orbits of the admissible roots of `K_I` at a marked 0-cusp of `T_Co`

Stage 2, named by research#760 (the dr2i turn of 2026-11-12).  Everything below was measured on the
adopted runtime (Sage 11.0.beta5, source pin `9f1680d2a7bcf001e50714768e6066e6652d1708`) in a
worktree of `omm/main = 8e88c6a1c5`.

**Result.** The call exists and returns: `IsotropicVectorReductionImage.root_class_orbits` with
`root_class`.  At `T_Co`'s cusp **3** the boundary lattice `K_I` has **one** root class and its
orbit is itself, the transporter being the identity; the acting family is `Gamma_{Co,2}`'s own line
stabilizer, 16 of whose 31 generators are certified in `G_v`, and it does act non-trivially on that
class.  Cusps **4** and **5** are blocked by missing input, not by the call: the printed root
families of Sterk's diagrams 4.3.8 and 4.3.9 are not in the library in `T_En`/`T_Co` coordinates
(§5).

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

Card `029J`, row `integral.cusp_chambers.gamma-en-2`, read by tag: Sterk's diagrams 4.3.5–4.3.9
(Math. Z. 207 (1991), pp. 19, 21, 22, 23, 24) with **12, 10, 12, 11, 13** walls.

| cusp | card walls | printed roots in `T_En` coordinates | distinct classes of `K_J` (computed) | of square `-2` |
| --- | --- | --- | --- | --- |
| `Sterk_1` (4.3.5) | 12 | 12 (`Sterk.sterks_in_TEn`) | **12** | 0 |
| `Sterk_2` (4.3.6) | 10 | 10 | **10** | 2 (`±delta`, not in `T_Co`) |
| `Sterk_3` (4.3.7) | 12 | 12 | **12** | 1 (`delta`-orthogonal: the `T_Co` root) |

So the reduction merges no two printed walls, and the class count equals the card's wall count —
a computed value compared with a card value read by tag.  `root_class` and `class_lift` are checked
against each other on the chamber wall family of `K_J` at the first cusp.

**The missing card.**  No lattice-database card holds the **orbit counts** of the root classes.  The
row that would carry them, and that this unit's values would fill, is
`029J.cusp_root_orbits.gamma-en-2` — per cusp: the number of `Gamma_{Co,2}`-orbits of the root
classes, one representative per orbit, and the order of the transporter group — plus the same row on
the `T_Co` card for cusps 3–5.  It is named here for filing on `dzackgarza/lattice-database`; the
agent's GitHub connection reads issues and cannot create them.

## 3. `K_I` at `T_Co`'s cusps 3–5, and why the chamber is not the root family

The cusp representatives are card `029J`'s, read in `T_Co`: they have equal `e` and `f`
coefficients, hence lie in `T_Co = delta^\perp` with that coefficient on `h`.  All three are
primitive isotropic of divisibility 2.

| cusp | `K_I` | `O(K_I)`'s fundamental chamber | `(-2)`-walls | certified generators of `G_v` |
| --- | --- | --- | --- | --- |
| 3 | rank 9, det 512, signature (1,8) | 9 walls | 1 | 16 of 31 (`19 s` + `159 s`) |
| 4 | rank 9, det 512, signature (1,8) | 9 walls | 1 | — |
| 5 | rank 9, det 512, signature (1,8) | 9 walls | 1 | — |

The chamber of `K_I` has eight `(-4)`-walls and one `(-2)`-wall at each cusp, so it does **not**
supply the admissible roots: those are `(-2)`-classes.  That is why the root family has to come from
the cusp's printed diagram, and why the refusal in §1 matters.

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
the given family of one class.  At cusps 4 and 5 the record's `T_Co` roots are likewise one and
three classes (`cusp 4: 10`; `cusp 5: 12, 13, 14`); at cusp 5 the orbit question is the substantive
one, and §5 is why it cannot be run yet.

## 5. Cusps 4 and 5: the stop, and what is missing

`Sterk.sterks_in_TEn()` holds the printed roots of diagrams 4.3.5–4.3.7 in `T_En` coordinates and
nothing for 4.3.8 and 4.3.9.  What the library holds for those cusps is:

| cusp | the library's data | why the call cannot be fed |
| --- | --- | --- |
| 4 (4.3.8, p. 23) | `Sterk.sterk_roots()["Sterk_4"]`, 11 roots in `II_{18,2}` coordinates (`TdP`) | no transcription into `T_En`/`T_Co`; the roots are not vectors of `T_Co` |
| 5 (4.3.9, p. 24) | `Sterk.sterk5_in_U_E8_2()`, 14 roots in `U + E8(-2)` coordinates | that is a model of `K_J`, not of `T_En`: the isometry `K_J(Sterk_5) ≅ U + E8(-2)`, equivalently the embedding of those roots into `T_Co`, is not in the library |

The transcription is also not derivable from what the library holds: the 34 vector pairs that the
three transcribed cusps give between `TdP` and `T_En` span only rank 16 of `TdP`'s 20, and the
linear system they impose on a map `TdP -> T_En` is inconsistent, so no single linear map carries
Sterk's `II_{18,2}` roots to their `T_En` partners (`p370-p7b.log`).  The missing datum is the
transcription of figures 10 and 12 (pp. 23, 24) into `T_En` coordinates — the same kind of
hand-read table `sterks_in_TEn` is — or, for cusp 5, the isometry from its `U + E8(-2)` model to
`K_J`.

## 6. The test, the gate and the push

`tests/lattices/test_the_coble_root_orbits_at_a_marked_cusp.sage`: the card comparison of §2 (12,
10, 12 classes against card `029J`'s wall counts, read by tag), the refusal of a `(-4)`-wall and the
`root_class`/`class_lift` round trip, and the run of §4 with its transporter and its non-vacuous
action.  Every number on the right of an assertion is computed or read from the card by tag.

Measured, one session, `-p qc_sage_session -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates`:

```
3 passed in 344.08 s (0:05:44)
  test_the_printed_cusp_walls_are_distinct_classes_of_the_boundary_lattice   27.89 s
  test_the_coble_cusp_three_has_one_root_class_and_its_orbit_is_its_transporter  312.30 s
```

no lint findings, peak tree RSS 1509 MiB; both calls over the local 20 s call ceiling are reported
by the gate and not enforced.

Logs and probes are committed under `.tmp/qc-evidence/` with their `SHA256SUMS` rows and an INDEX
section.
