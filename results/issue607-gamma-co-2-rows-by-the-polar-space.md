# `Gamma_{Co,2}`'s rows on `T_Co`: the double cosets in `O(q) = O^+_{10}(2)`

Answers `#607` items 1 and the 527/`P_0` paragraph of the review quoted there.

## The finite geometry

`A_{T_Co} = <w> perp w^perp`, `w = [h/2]`, `q(w) = 1/2`; every element of
`O(q)` fixes the characteristic class `w` (prop:gamma-co-images(2)), so
`O(q) = O(w^perp)`.  `w^perp = A_{U(2)} perp A_{E_8(2)}` is `F_2^{10}` with the
`Z/2`-valued form `q`, of plus type (it is the orthogonal sum of the hyperbolic
plane `A_{U(2)}` and `A_{E_8(2)}`, which is `E_8/2E_8` with `q(x) = x^2/2`,
plus type).  Hence `O(q) = O^+_{10}(2)`, of order
`2 * 2^{20} * (2^5 - 1) * prod_{i=1}^{4} (2^{2i} - 1) = 46998591897600`, which is
the order the library computes (`probe log` below, line 1).  Point counts in
`O^+_{2m}(2)` are standard (Taylor, *The Geometry of the Classical Groups*,
Heldermann 1992, Ch. 11; Kleidman-Liebeck, *The Subgroup Structure of the
Finite Classical Groups*, LMS LN 129, 1990, Prop. 2.5.x):

| object | count | the `T_Co` datum |
| --- | ---: | --- |
| singular points, `(2^5 - 1)(2^4 + 1)` | 527 | nonzero isotropic classes |
| totally singular lines, `527 * 135 / 3` | 23715 | liftable `J = [P/2]` |
| hyperbolic lines, `|O^+_{10}| / (|O^+_2| |O^+_8|)` | 67456 | the `O(q)`-orbit of `A_{U(2)}` |

so `P_0 = Stab_{O(q)}(A_{U(2)}) = O^+_2(2) x O^+_8(2)`, order `2 * 348364800 =
696729600`.  `A_{U(2)}` is a hyperbolic line, not a totally singular one: this is
the lemma of `results/issue286-the-base-point-is-not-a-plane-class.md`, now with
its reason (`q(ep/2 + fp/2) = 1`).  The group of
`results/issue286-the-gamma-co-2-distribution-measured.md:30` ("`P_0 =
Stab([P/2])`", order 1981808640, six orbits) is the stabilizer of a totally
singular line, the **wrong group**; that note's distribution is withdrawn and
replaced by the one below.

## The reduction (proof)

`Gamma = rho^{-1}(P_0)` (`results/issue286-gamma-co-2-is-the-discriminant-preimage.md`)
contains `ker rho`, and `rho: O(T_Co) -> O(q)` is onto (Nikulin, Math. USSR-Izv.
14 (1980), Thm. 3.6.3: an even indefinite 2-elementary lattice of rank `>= 3`).
For one `O(L)`-orbit `X = O(L) x_0`,

    Gamma \ X  =  Gamma \ O(L) / Stab(x_0)  =  P_0 \ O(q) / rho(Stab(x_0)),

because `Gamma ⊇ ker rho`; and `P_0 \ O(q) / R` is the set of `R`-orbits on
`O(q)/P_0`, the 67456 hyperbolic lines.  The `O` row has one line orbit, one
plane orbit and one flag orbit, so each of the three rows of `Gamma_{Co,2}` is a
count of orbits of one subgroup `R` of `O^+_{10}(2)`:

| row | `R` |
| --- | --- |
| lines | `rho(Stab(v)) = Stab_{O(q)}(p)`, `p = [v/2]` singular (index 1, below) |
| planes | `rho(Stab(P))`, index 8 in `Stab_{O(q)}(J)` |
| flags | `rho(Stab(v, P))` |

## Lines: 4, by hand

`rho(Stab(v))` is `Stab(p)`: it lies in `Stab(p)`, and its kernel orbits are
the 527 classes, one each (research#667's integral certificate; the lower bound
527 is `results/issue286-which-group-the-otilde-plus-row-builds.md:52-58`), so
`[O(q) : rho(Stab v)] = 527 = [O(q) : Stab p]`.  The line row is then the
`P_0`-orbits on singular points `x = a + b`, `a in H = A_{U(2)}`,
`b in W = A_{E_8(2)}`, `q(a) = q(b)`.  `O^+_2(2)` swaps the two singular
points of `H`; `O^+_8(2)` is transitive on the 135 singular and on the 120
nonsingular points of `W` (Witt).  So:

| `a` | `b` | orbit size |
| --- | --- | ---: |
| `0` | singular | 135 |
| singular (2) | `0` | 2 |
| singular (2) | singular | 270 |
| `ep/2 + fp/2` | nonsingular | 120 |

`135 + 2 + 270 + 120 = 527`: **four** line orbits, the driver's 4.

## Planes: the `P_0`-orbits of `J`, by hand, and the split by the probe

`P_0`'s orbits on the 23715 totally singular lines `M`, by the projection
`pi: M -> H`:

| `pi(M)` | form of `M` | size |
| --- | --- | ---: |
| `0` | t.s. line of `W` | 1575 |
| `H` | graph of a hyperbolic pair of `W` | 135 * 64 = 8640 |
| a singular point `a` | `<a, b>`, `b` singular in `W` | 2 * 135 = 270 |
| a singular point `a` | `<a + c, b>`, `<b, c>` t.s. in `W` | 2 * 1575 * 3 = 9450 |
| `<ep/2 + fp/2>` | `<a + c, b>`, `c` nonsingular in `b^perp/b` | 135 * 28 = 3780 |

sum 23715, **five** orbits (each by Witt in `O^+_8(2)` and its point
stabilizer).  The plane row is `sum_i n_i` over these five orbits, `n_i` the
number of `Stab_{P_0}(J_i)`-orbits on the eight cosets `Stab(J_i)/rho(Stab P_i)`.
So `7 = 1+1+1+1+1 + 2`, i.e. exactly two of the five pieces split once, or one
piece splits into three; the run's 7 (`#391`) is a record, not this proof.

## R_P from the Levi quotient

`S = Stab_{O(q)}(J)` acts on `J^perp/J` (128 cosets; `O(q)` fixes `w`) through
`O^+_6(2) = S_8`, image of order 40320, with kernel `K_0` of order 49152 (the
unipotent radical and the `GL(J)` Levi factor).  `[S : R_P] = 8`
(`#360`: 1981808640 / 247726080).

**Lemma (proved).** If `R_P ⊇ K_0`, then `R_P` is the preimage of a point
stabilizer `S_7`: the image of `R_P` then has index 8 in `S_8`, and for
`n != 6` every subgroup of index `n` in `S_n` is a point stabilizer
(J. D. Dixon and B. Mortimer, *Permutation Groups*, GTM 163, Springer 1996,
Thm. 5.2B and the remark after it), one conjugacy class.  The `Gamma_{Co,2}`
counts depend only on the conjugacy class of `R_P` in `O(q)`.

**The candidate, computed** (`results/issue607-the-levi-candidate.py`, log
`results/issue607-the-levi-candidate.log`, 346 s of which 335 s is building
`O(q)` and `J^perp`; the orbit counts are 3 s each):

| quantity | value |
| --- | --- |
| `|R|` | 247726080, equal to `#360`'s `|rho(Stab P)|` |
| `R` on `J \ 0` | one orbit of 3 |
| plane row: orbits of `R` on the 67456 hyperbolic lines | **7**: 26880, 24576, 8064, 3360, 2688, 1120, 768 |
| flag row: orbits of `R cap Stab(p)` (order 82575360) | **13** |
| line row: orbits of `Stab(p)` | **4**: 34560, 17280, 15360, 256 |

The 4, 7 and 13 agree with the `#391` run record.  The flag row uses
`rho(Stab(v, P)) = R_P cap Stab(p)`, whose order 82575360 equals
`|O(q)| / 569160`, the kernel edge count of research#667's certificate.

## R_P ⊇ K_0, proved

**The radical.** For `e in P` and `a in L^# cap P^perp`, the Eichler transvection
`t(e, a)(v) = v - (a, v) e + (e, v) a - (1/2)(a, a)(e, v) e` is an isometry of
`L ⊗ Q` (Gritsenko-Hulek-Sankaran, arXiv:0810.1614, section 3.1, equation (4),
printed p. 8).  It fixes `P` pointwise, so it lies in `Stab_{O(L)}(P)` whenever
it is integral.  With `e` and `a` both in `L` its discriminant action is trivial
(`t - 1` maps `L^#` into `Ze + Za`), so the generators use `a` in the dual.
`results/issue607-the-radical-is-in-the-image.py` takes `e` in `{e_1, e_2,
e_1 + e_2}`, a basis of `P`, and `a` over a basis of `L^# cap P^perp` and its pairwise sums.
It keeps the 108 of 135 matrices that are integral, each checked to preserve the
Gram matrix, and computes their action on `A_L`.  `A_L = Z^11/Gram Z^11 = (Z/2)^11` in
pairing coordinates, tied to the library's classes of `b_i/2`.
Log: `results/issue607-the-radical-is-in-the-image.log`.

| quantity | value |
| --- | --- |
| `T = <rho t(e, a)>` | order 8192 |
| `U` = kernel of `S = Stab(J)` on `J` and on `J^perp/J` | order 8192, `= O_2(S)` |
| `T = U` | true |
| `S/U` | order 241920 = 6 * 40320; images on `J` and `J^perp/J` of orders 6 and 40320 |

So `rho(Stab P) ⊇ T = U`.  `S/U` embeds in `GL(J) x O(J^perp/J) = S_3 x S_8`,
because `U` is the kernel of the two actions, and the orders are equal, so
`S/U = S_3 x S_8`.

**The rest, by group theory alone.**  `R_P/U` has order
`247726080 / 8192 = 30240` (`#360`: the parabolic family is certified complete,
#331, #366, so `|R_P|` is the order its images generate).  By Goursat,
`|D| = |pi_2(D)| * |D cap (S_3 x 1)|` for `D = R_P/U`, so `|pi_2(D)| = 30240/k`
with `k` in `{1, 2, 3, 6}`.  `S_8` has no subgroup of index `4/3`, `8/3` or `4`.
A subgroup of index at most 4 contains `A_8`, since `A_8` is simple and the action
on its cosets gives a homomorphism to `S_4`.  So `k = 6`, and `pi_2(D)` has index 8, a point stabilizer
`S_7` (Dixon-Mortimer, GTM 163, Thm. 5.2B).  Hence `R_P/U = S_3 x S_7`:
`R_P` contains `K_0` (`K_0/U = S_3 x 1`) and is the `S_7` preimage of the
previous section.  That excludes the `S_8`/index-8 and `A_8`/index-4 shapes.

**Conclusion (item 1).** `Gamma_{Co,2}` on `T_Co` has **4** line, **7** plane and
**13** flag orbits.  These are the orbit counts of `Stab(p)`, of `R_P` and of
`R_P cap Stab(p)` on the 67456 hyperbolic lines, 3 s each in GAP
(`results/issue607-the-levi-candidate.log`).  The flag group is
`rho(Stab(v, P)) = R_P cap Stab(p)`, which uses research#667's three line
classes per plane; the line row uses its 527 classes.
