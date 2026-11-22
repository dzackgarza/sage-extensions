# #616: the stabilizer's image at a primitive isotropic plane of `T_En`

**Result of this turn.** The image `M` the acceptance asks for is *not* the product
`GL(I) x O(I^perp/I)`, and three numbered statements of Sterk fix it. The tree's
completeness test asks for the product, so on every plane whose image is a proper
congruence subgroup the test answers `False`, and the dispatch then refuses the
plane's own block construction. Measured at `e366ec5`: on one such plane the block
family's plane-action image has index 3 in `GL_2(ZZ)` — the index Sterk's statement
gives the stabilizer's image — while the test reports it as a proper subgroup, and
the public call that takes over does not return. No red test landed this turn; the
repair and its test are stated at the end.

The research volume (`writing/`) is not checked out on this machine and the GitHub
connection reads this repository only, so the page proof the acceptance names
(`prop:coble-flag-orbits-and-edges`) could not be read here; nothing below depends
on it.

## 1. The statement of `M`

`P_I = Stab_{O(L)}(I)` maps onto `M <= GL(I) x O(I^perp/I)` with kernel the
unipotent radical. For `T_En = U + U(2) + E8(-2)`:

* H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
  Math. Z. 207 (1991), **(4.3.16)**: for an isotropic plane `E = Z e + Z v` with
  `(v, L_-) = 2Z`, the image of the normalizer in `SL(E)` is
  `Gamma^1(2) = { (a, c; b, d) in SL_2(ZZ) : b even }`. The argument is the
  divisibility: `(e, L_-) = Z` and `(v, L_-) = 2Z` force `a` odd and `b` even.
* **(4.3.17)**, stated conclusion for the five remaining plane types of
  `Gamma_{En,2}`: `Gamma(2) <= Gamma(F) cap SL(F) <= Gamma^1(2)`, and

  | type of `F` | `Gamma(F) cap SL(F)` |
  | --- | --- |
  | `{2,4,5}` | `Gamma(2)` |
  | `{4,5}` | `Gamma^1(2)` |
  | `{3,5}` | `Gamma^1(2)` |
  | `{3,4}` | `Gamma^1(2)` |
  | `{5,5}` | `Gamma L_2(ZZ)` (as printed) |

  Worked case `{3,4}`: `F = Z v + Z omega` with `v = e' + f' + alpha-bar_8` and
  `omega = alpha_9 + alpha_12 + alpha_1 + alpha_3 + alpha_4 + alpha_5 + alpha_6 +
  alpha_7 + alpha_13`; `g(v) = a v + b omega` forces `b` even, and the
  Siegel-Eichler transformation `E_{v, (e'-f')/2}` lies in the normalizer and
  sends `omega` to `omega - v`, which realizes the class of `b` even modulo
  `Gamma(2)`.
* **(4.6), (4.7)**: over `O(L_-)` there are two classes of primitive isotropic
  rank-2 sublattices; if `F` is equivalent to `Z e + Z e'` then the image of the
  normalizer in `SL(F)` is `Gamma^1(2)`, and otherwise it is `SL(F)`.

So `M` is a proper subgroup of the product on the planes of (4.7) with `F`
equivalent to `Z e + Z e'`, and its plane projection has index 3 there. On the
`Gamma_{En,2}` types of (4.3.17) every entry except `{5,5}` is a proper congruence
subgroup as well.

## 2. What the tree decides, and the gap

`parabolic_completeness_decision` returns complete exactly when all three of
`unipotent_radical_index`, `levi_plane_action_index(trivial_on_quotient=True)` and
`levi_quotient_image_index(trivial_on_plane=True)` equal 1 — that is, exactly when
the family's image is the **whole product**. The docstring states the equivalence it
relies on: "With all three the image is the whole product, hence `M`". The second
"hence" is the gap: it holds only when `M` *is* the product, and Section 1 says it is
not, on exactly the planes this issue is about. The obstruction message draws the
unsupported conclusion explicitly — "The family's image is then a proper subgroup of
`M`" — from the index alone.

The dispatch is where that becomes a wrong answer: `_isotropic_plane_parabolic_generators`
returns `None` unless `is_parabolic_complete()`, so a plane whose image is a proper
congruence subgroup never gets its own block family, and the caller keeps another
route.

The split case is the mirror image of the same gap: `parabolic_completeness_decision`
returns `True` for a plane with a splitting complement **without computing any of the
three factors**, on the argument that the block equations make every pair admissible.
That argument is about `M`, not about the returned family, and it too is only sound
when `M` is the product.

## 3. Measured at `e366ec5` (Sage 11.0.beta5, `T_En`)

One process per row; `plane` is `T_En.primitive_isotropic_subobject(v, w)`.

| plane | splitting complement | radical index | plane index (trivial on quotient) | quotient index (trivial on plane) | complete |
| --- | --- | --- | --- | --- | --- |
| `v = e`, `w = e'` | present | 1 | 3 | 1 | True |
| `v = Sterk_1`, `w = Sterk_3` | present | 1 | 3 | 1 | True |
| `v = Sterk_1`, `w = Sterk_4` | none | 1 | 3 | 1 | **False** |
| `v = Sterk_2`, `w = Sterk_5` | none | 1 | 1 | 1 | True |

* On `Z e + Z e'` the block family is 181 elements in 5.8 s, its plane actions
  generate a subgroup of index 3 with 14 distinct actions, and the public
  `T_En.Aut().stabilizer(plane, action="setwise").group_generators()` returns 168
  elements in 1.6 s — the block family, since the split shortcut answers `True`.
  Index 3 is what (4.7) gives the stabilizer's own image, and the family's image is
  contained in it, so here the family's plane projection is the stabilizer's.
* On `Z e + Z Sterk_4` the three factors are `1, 3, 1`, the predicate reports the
  family as a proper subgroup, and
  `T_En.Aut().stabilizer(plane, action="setwise").group_generators()` did not return
  inside 540 s (killed; the fallback route is the one `TRAPS.md` records as not
  returning on `T_En`). Its plane basis is `(e, Sterk_4)`, and `Sterk_4` is a
  primitive isotropic vector of divisibility 2, so this plane contains a
  divisibility-one isotropic line and is Sterk's `Z e + Z e'` class by (4.6)/(4.7):
  the stabilizer's image there is `Gamma^1(2)`, of index 3.

At `Z e + Z e'` the gap of Section 2 closes, and the calculation is worth recording
because it is the shape the repair needs. In the block basis `(U | P | K)` the Gram is
`((H, J, Kblk), (J^t, 0, 0), (Kblk^t, 0, A))` with `H = 0`, `J = diag(1, 2)` and
`Kblk = 0` (Dutour Sikirić--Hulek, Theorem 4.9, the block equations `(E2)` and `(E3)`).
`(E2)` reads `J = g11^t J g22`, so `g11 = J^{-1} g22^{-t} J` must be integral, which for
`g22 = (a, b; c, d)` is `((d, -2b), (-c/2, a)) / det`: integral exactly when `b` is
even. Conversely, for every such `g22` the matrix `diag(g11, g22, 1)` is an integral
isometry -- `H = 0` kills the first block equation and `Kblk = 0` kills the third -- so

```
M = Gamma_J x O(E_8(-2)),   Gamma_J = { M in GL_2(ZZ) : M_12 even },   [GL_2(ZZ) : Gamma_J] = 3,
```

and the family's plane actions generate `Gamma_J` (index 3, 14 distinct actions) while
its quotient actions fill `O(E_8(-2))` (index 1). At this plane the family is therefore
the whole stabilizer, and `Gamma_J` is Sterk's `Gamma^1(2)` in the basis his statement
uses.

What the rows above show is narrower and sharper than "the predicate is too strict":
`Z e + Z e'` and `Z e + Z Sterk_4` are two primitive isotropic planes of `T_En` with the
same block data `J = diag(1,2)`, the same plane index 3 and the same quotient index 1,
and the predicate answers `True` for one and `False` for the other, decided only by
whether `splitting_complement()` happens to find a complement whose pairing with `K`
vanishes. Both contain a divisibility-one isotropic vector, so by (4.6) and (4.7) they
are the one `O(L_-)`-class whose image is `Gamma^1(2)`; at most one of the two answers
can be the truth about that class, and the `False` one is the answer that discards the
block family.

## 4. What is open, and the next two steps

1. **The five planes are not constructed in this repository.** (4.3.17) states the
   `{3,4}` member in full and summarises the other four; nothing in `src/` builds
   them, and the search for a plane of the listed types by null vectors of the
   chamber's parabolic subdiagrams found members for the third and fifth cusp
   chambers but none whose type could be *named* rather than guessed — a guessed type
   is not a specimen. The first step of the next turn is to build the `{3,4}` member
   from (4.3.17)'s printed vectors and identify the other four by the invariant that
   (4.3.16) uses, the divisibilities of the plane's own isotropic lines.
2. **The repair goes at the decision, not at the family.** The family already
   realizes the plane action: on both index-3 planes above the block family's plane
   actions have index 3, which for the `Z e + Z e'` class *is* the stabilizer's image
   by (4.7) — containment plus equal index. What is missing is the comparison with
   `M`: the decision has to be stated against the cited image (`Gamma(2)` and
   `Gamma^1(2)` of (4.3.16), (4.3.17), `SL(F)` and `Gamma^1(2)` of (4.7)), not
   against the product, and the split branch has to compute the factors instead of
   returning `True`. The red test is then at the public call: on the `{3,4}` member,
   `is_parabolic_complete()` is `True` and the returned family's plane actions have
   index 3, the index (4.3.17) gives the stabilizer.

Nothing in this note is a claim that the block family *is* `M`: the two projections
are shown, the sub-direct-product question is not, and a family whose image agrees
with `M` in both projections can still be smaller than `M`. That question is what
the `{3,4}` member is for.

## 5. Commands

```
~/sage-image/run.sh -w /work -b <worktree>:/work -b <repo>/.git:/work/.git \
  -b ~/ai-review-ci:/ci -- /bin/sh -c 'export HOME=/root;
    export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src;
    /sage/.venv/bin/python -u /work/.scratch/616/<probe>.py'
```
