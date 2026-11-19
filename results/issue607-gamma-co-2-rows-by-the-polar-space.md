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

## What is still missing: one subgroup

The plane and flag rows need `R_P = rho(Stab_{O(L)}(P))`, the index-8 subgroup of
`Stab_{O(q)}(J)` (orders 247726080 in 1981808640, `#360`).  Everything else is
in `O(q)`.  The probe `results/issue607-gamma-co-2-double-cosets.py` builds an
explicit plane `<ep, 2h + a_i + a_j>` (`is_parabolic_complete()` True at 50 s)
and then asks `parabolic_stabilizer_generators()`, which does not return inside
the ten-minute limit (`results/issue607-gamma-co-2-double-cosets.log`, exit 124
after line 5).  With `R_P` in hand the plane row is `#Orbits(R_P, H)` and the
flag row `#Orbits(R_P cap Stab(p), H)` on the 67456 hyperbolic lines, seconds
in GAP.  The precise missing construction is therefore a description of `R_P`
inside `Stab(J) = 2^{1+8+?}:(GL_2(2) x O^+_6(2))` without the integral
parabolic: the Levi image of `Stab(P)` in `GL(P) x O(P^perp/P)` reduced mod 2.
`O^+_6(2) = S_8` has a unique class of index-8 subgroups (`S_7`), which is the
candidate; it is not proved here.
