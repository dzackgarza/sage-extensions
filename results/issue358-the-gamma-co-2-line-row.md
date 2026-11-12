# #358 — the `Gamma_{Co,2} = R_{Gamma_{En,2}}` line row on `T_Co`

Parent `#286` (stage 1).  The row is `isotropic_orbit_representatives(1)` on
`Gamma_{Co,2} = rho^{-1}(P)`, `P` the stabilizer in `O(q)` of the decomposition
`A_{U(2)} + A_{E8(-2)}` of `[h/2]^\perp` (research `prop:gamma-co-images`, `38fa09935a`).
Everything below was measured on the adopted runtime (Sage 11.0.beta5, source pin
`9f1680d2a7bcf001e50714768e6066e6652d1708`) in a worktree of `omm/main = 7ef38d52cf`.

**Result.** The row returns: **4 line orbits**, 265.8 s, with the repairs below.  Two of the
route's stages do not realize at `T_Co`'s size and are reported as stops, not worked around:
`Gamma_{Co,2}`'s Schreier family (`|S| * 67456 - 67455` members, ~2.3e7) and
`discriminant_lift` of one generator of `P`.

## 1. The reproduction: `O(A_{T_Co})`'s order returns; the recorded stop does not occur

`#358` recorded a stop before the call: the order of `O(A_{T_Co})` does not return
(`groups.py:540` -> `fqf_orthogonal._isom_fqf`, `results/issue286-tco-run.md` row 3, tree
`a8f95b60c2`).  On current main it does:

| quantity | value | time |
| --- | --- | --- |
| `A_{T_Co}` | 2048 classes, exponent two, two-primary invariants all `2` (rank 11) | 6.0 s to build |
| `A_{T_Co}.orthogonal_group().cardinality()` | **46 998 591 897 600** | **4.0 s** |
| GAP `HasSize` on that engine group | `True` | — |

The branch: `_engine_orthogonal_group` (`torsion_form_modules.py:2778`) sends an elementary
two-primary part with a half-integral `q` value to
`_engine_two_primary_odd_orthogonal_generators` (`:2884`, sage-extensions `#323` at `177fb6a3`),
which splits off the half-integral direction, reads `O(q_0)` of the integral rank-10 remainder
through GAP's `GO`, and **sets the size** (`group.gap().SetSize(order)`); the general route through
Sage's `TorsionQuadraticModule.orthogonal_group()` — the one that built `_isom_fqf` and whose
`.order()` enumerated — is not entered.  So `groups.py:540`'s matrix-group order adapter is never
reached for this group, and the value agrees with card `6JRR`.  Log: `p358-p1.log`
(`.tmp/qc-evidence/`).

## 2. `P` and `|P|` two ways, all computed

Built from `T_Co`'s own Gram data (`NamedLattices.Tco`: `<2> + U(2) + E8(-2)`, module generators
`h, ep, fp, a1..a8`; Dolgachev--Kondo, Izv. Math. 77:3 (2013), (3.6), printed p. 513, `E8`
negative definite).  Classes are the primitive duals' classes; `A_{U(2)} = <[ep/2], [fp/2]>`.

| statement | measured |
| --- | --- |
| `A_{T_Co} = A_{U(2)} + A_{E8(-2)} + <[h/2]>` | orders 4, 256, 2; product 2048 = `|A|`; pairwise orthogonal; the spans are the whole group |
| `[h/2]^\perp` | 1024 classes, exactly `A_{U(2)} + A_{E8(-2)}`; its radical is trivial, so `<[h/2]>` is a separate nondegenerate summand |
| `q([h/2])`, `b([h/2],[h/2])` | `1/2`, `1/2` (the library's `q(x) = (x,x)` normalization) |
| `q` on `A_{U(2)}` | `{0, 0, 1/2, 1/2}`, `b([ep/2],[fp/2]) = 1/2` |
| `\|O(q_{U(2)})\|` | **2** (the two `q = 1/2` classes may be interchanged) |
| `\|O(q_{E8(-2) + <2>})\|` | **348 364 800** |
| `\|P\|`, first route: the product | **696 729 600** |
| orbit of `A_{U(2)}` under `O(q)` | **67 456** = `2^7 * 17 * 31` |
| `\|P\|`, second route: `\|O(q)\| / 67 456` | **696 729 600** |
| setwise stabilizer in the permutation model of `O(q)` (GAP, `OnSets`) | **696 729 600** |
| `\|O(q)\|` divided by the character quotient's index `[O(T_Co) : Gamma_{Co,2}] = 67 456` | 696 729 600 |
| public call `group.discriminant_point_orbit(point)` | 67 456 points, 318.9 s |

So `|P| * 67 456 = |O(q)|` (index--stabilizer), `|P|` agreeing across four constructions: the two
summands' orthogonal groups, the engine's setwise stabilizer, `|O(q)|/index`, and the character
quotient's joint discriminant image `subgroup_image_order() = 696 729 600`.  `rho_L` is onto
(`lattice.discriminant_image().cardinality() = 46 998 591 897 600`), which is what makes the
preimage's image `P` itself.  Log: `p358-p10.log`.

## 3. The stop inside the row, and its repair at the owner

On `a8f95b60c2` the row stopped *before* the call because `P` could not be built.  On current
main it stops *inside* it: `P` was handed over as a bare `PredicateSubgroups` predicate, and
`O(A_{T_Co})` is a finite group, so this library's canonical free cover of a finite group — the
one on *all* of its elements (`groups.py:6755`, `Finite.ParentMethods.selected_group_resolution`)
— turned every generator request on `P` into a filter over `4.7e13` elements:

```
orthogonal_quotients.py:706   _joint_discriminant_image_gap      (target.group_generators())
groups.py:5763                group_generators
groups.py:6755                selected_group_resolution
sets/set_categories.py:4482   _points_satisfying
torsion_form_modules.py:2250  _from_engine per listed element
```

Killed at **4282 MiB** without returning in 2400 s (`p358-p2.log`), reached from
`_subgroup_isotropic_orbit_representatives` through `splitting_isometries`.

Repair, at the two owners involved:

- `TorsionFormOrthogonalGroup.stabilizer_of_classes(classes)`
  (`torsion_form_modules.py`): the engine's own setwise stabilizer of a finite class set, with
  generators — GAP's `Stabilizer` on the engine's elementwise action, Holt--Eick--O'Brien,
  *Handbook of Computational Group Theory*, Chapman & Hall/CRC, 2005, Section 4.1, p. 79.
  `stabilizer(subgroup)` is the same body on a submodule's embedded classes.
- `LatticeIsometryMor.discriminant_point_stabilizer` (`lattice_morphisms.py`): the stabilizer it
  hands over keeps its defining predicate *and* gets that family as its selected generating
  morphism, so `P` is generated as well as decidable.

Cost, measured: **87 s** for the 67 456-point orbit with GAP's own `OnSets` action, against
**307 s** for the `Set(List(x, y -> ImageElm(g, y)))` set-image function that the same body used
first — the function rebuilt the set at every step.  GAP's built-in orbit walk alone is 2.89 s for
the same 67 456 points.  With the repair the quotient's orders are immediate:
`image_order = 46 998 591 897 600` (55.4 s, one sweep of `rho` over the 346 generators),
`subgroup_image_order = 696 729 600` (0.7 s), `index = 67 456` (0.1 s).

Regression: `tests/lattices/test_the_decomposition_preimage_returns_generators.sage` (card `0125`,
`#354`) passes with the repair, and the engine's own action brings it back down: **1 passed in
151.83 s** (call 151.83 s) with `libgap.OnSets`, against **1 passed in 320.85 s** (call 318.45 s)
with the `Set(List(...))` set-image function — its recorded 53.88 s before this repair did not
build `P`'s family at all, which is the defect this unit repairs (`p358-regress354.log` and
`p358-tests.log`).

## 4. The row

```
Tco.Aut().discriminant_point_stabilizer(point)          # Gamma_{Co,2}
   .isotropic_orbit_representatives(1)                  # 4 orbits, 265.8 s
```

`4` line orbits.  The four representatives, their vectors in the named basis of `T_Co`, their
divided class, and the index `[Stab_{O(q)}(v_bar) : rho(Stab_{Gamma}(v))]` per class:

| orbit | vector | `div` | divided class `c` | `\|Stab_{O(q)}(c)\|` | `\|rho(Stab_Gamma(v))\|` | index | classes in the orbit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `-ep` | 2 | `-[fp]` | 89 181 388 800 | 348 364 800 | **256** | 2 |
| 1 | `44168457980 h + 1820311546 ep + 28029145070 fp + 30120546496 a1 + 74620371507 a2 + 65644225591 a3 + 125373851653 a4 + 93881685920 a5 + 49779389922 a6 + 31226948905 a7 + 7801536729 a8` | 2 | `44168457980[h] + 28029145070[ep] + 1820311546[fp] + 5403132599[a1] - 23866891361[a2] + 24205946967[a3] - 16601420288[a4] - 12610130265[a5] + 25549854981[a6] - 4872971159[a7] + 15623875447[a8]` | 89 181 388 800 | 5 160 960 | **17 280** | 135 |
| 2 | `4 h - ep - 4 fp + 2 a1 + 5 a2 + 5 a3 + 7 a4 + 4 a5 + a7 + a8` | 2 | `4[h] - 4[ep] - [fp] + [a1] - 3[a2] - [a3] - [a5] + 5[a6] - [a7] - [a8]` | 89 181 388 800 | 2 580 480 | **34 560** | 270 |
| 3 | `-12563877094386 h + 1972188049887 ep - 2958671514421 fp - 4739366612966 a1 - 11144527454303 a2 - 11048550525707 a3 - 22422059246811 a4 - 13569369774452 a5 - 2402950410106 a6 - 1502118700382 a7 - 71496532492 a8` | 2 | `-12563877094386[h] - 2958671514421[ep] + 1972188049887[fp] - 1569817299775[a1] - 133004338205[a2] - 5064324808363[a3] + 9081670739160[a4] + 2313729891987[a5] - 10265587654622[a6] + 529790458166[a7] - 1359125635398[a8]` | 89 181 388 800 | 5 806 080 | **15 360** | 120 |

Every representative has `q = 0` and `div = 2`, so all four lie at divisor `2`, and their divided
classes are read from the vector's own coefficients (the row's printed class is reproduced exactly
by rebuilding the vector from those coefficients: `p358-p12.log`).  The last column is
`|P| / |rho(Gamma) cap Stab_{O(q)}(c)|`, computed as `696 729 600 / |rho(Stab_Gamma(v))|`, and

    2 + 135 + 270 + 120 = 527

is the number of nonzero isotropic classes of `A_{T_Co}`, which is the number of primitive
isotropic line classes of `T_Co` (`O(T_Co)` is transitive on the lines: one ambient line orbit).
So the four `Gamma_{Co,2}`-orbits partition the 527 classes, and the indices are their fibres over
one class each.  `|rho(Stab_Gamma(v))|` is `|P| ∩ |Stab_{O(q)}(c)|`; the class stabilizer's order
`89 181 388 800` is the same for all four because `O(q)` is transitive on the classes.

`p358-p11.log` is the row, and `p358-p12.log` the index table; the row's own run in `p358-p10.log`
returned the same count `4` in 265.8 s on an idle machine (the two runs differ only in the ambient
stage's cost, 265.8 s against 1917.5 s, which is the lift-locus search of `isotropic_lifts.py:586`
under contention).

## 5. What does not realize: `Gamma_{Co,2}`'s Schreier family and the lift search

Both are stops, recorded rather than routed around:

| stage | state |
| --- | --- |
| `preimage.group_generators()` (the Schreier family of the orbit) | `|S| * 67456 - 67455` members with `|S|` = 329, 339, 344, 345, 346 across runs (the ambient family is not deterministic, sage-extensions `#289`), i.e. 2.2e7 to 2.3e7 members; its realization was **killed at 5484 MiB** (`p358-p6.log`, no stack: the process was reaped, `MemAvail` 764 MiB) |
| `group.discriminant_lift(p)` for one generator `p` of `P` | **killed at 6254 MiB** (`p358-p9.log`); the lift searches the ambient family's products for a word with the prescribed discriminant image |

The card-`0125` route avoids both because there the ambient family has 15 letters
(`15 * 67456 - 67455 = 944 385` members) and `discriminant_point_stabilizer_image_generators`
selects nine.  At ~340 letters the same construction is 24 times larger and does not fit the
guard; what is missing is the cheap walk representation that sage-extensions `#296` names (point
indices and generator words, transversals evaluated on demand), not a different argument.  So the
order the test pins is `rho(Gamma_{Co,2})`'s, read as the owned subgroup `discriminant_image()` of
`O(q)` and from the character quotient's joint discriminant image — the two-order argument
`stabilizer_discriminant_image_orders` (`isotropic_parabolics.py:2366`) uses for a parabolic's
image.

## 6. The test, the gate, and the push

`tests/lattices/test_the_coble_gamma_co_2_line_row_returns_generators.sage`: the decomposition by
construction from `T_Co`'s Gram data, `|P|` three ways (summand orders, the engine's setwise
stabilizer, `|O(q)|/index`), the index, `rho(Gamma_{Co,2})`'s order as an owned subgroup of `O(q)`
and from the character quotient's joint discriminant image, and that every generator of the
stabilizer fixes the point.  Every number on the right of an assertion is computed; nothing is
typed.  The row's own count is *not* asserted there: it costs minutes and is recorded in §4.

Measured (`p358-tests.log`, `.tmp/qc-evidence/issue358-tests.log`), both tests in one session with
`-p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint
--no-time-gates`:

```
2 passed in 541.79 s (0:09:01)
  test_the_coble_gamma_co_2_line_row_returns_its_stabilizer_image   391.07 s
  test_the_decomposition_preimage_returns_generators                150.14 s
```

no lint findings, peak tree RSS 4381 MiB.  Both calls are over the local 20 s call ceiling, which
this run reports and does not enforce.

Logs (`issue358-*.log`) and the probes behind them (`issue358-probe-*.py`) are committed under
`.tmp/qc-evidence/` with their `SHA256SUMS` rows.
