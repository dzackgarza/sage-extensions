# The restricted-stabilizer call of #286: what it spends, and the row it needs

`Gamma_{Co,2}` is `R_{Gamma_{En,2}}`, the image in `O(delta^perp)` of
`Stab_{Gamma_{En,2}}(delta)` for `delta` the `(-2)`-vector of `T_En` whose
perpendicular is `T_Co` (Dolgachev–Kondō, Izv. Math. 77:3 (2013), p. 513,
the sentence after Prop. 3.2).  `gamma.stabilizer(delta)` did not return in
260 s on this VM.  This note is the triage the always-on performance rules ask
for (AGENTS.md, "Performance claims" and "What optimization is for"): the
construction against the computation, the wall time as a function of the
lattice, and whether the cost is waste or the mathematics.

## Construction against computation

`PredicateSubgroups.stabilizer` is `self.intersection(self.supergroup().stabilizer(v))`,
so the row pays two things: the ambient vector stabilizer, and the meet.

| step, `T_En` | wall |
| --- | ---: |
| `T_En`, `delta = e - f`, `delta^perp` (isometric to `T_Co`, checked) | 2.66 s |
| `Gamma_{En,2} = Polarized.coinvariant_extension_subgroup()` | 6.84 s |
| **`delta` in `Gamma_{En,2}`'s own lattice** (the supergroup's, not the catalogue object) | 0.04 s |
| `gamma.stabilizer(delta)` (object) | 0.00 s |
| its generators | **no return in 260 s** (stopped) |

Everything that *constructs* is instant or seconds; the whole cost is the
generators.  The same split holds at every size below: the stabilizer object is
0.00–0.01 s at ranks 3, 5 and 12, and its generation is the number.

## Wall time as a function of the lattice

`O(L).stabilizer(v).group_generators()` at a non-isotropic vector, one process,
`.scratch/w286-review/.tmp/probe-vector-stabilizer.py`
(`.scratch/w286-probes/vecstab.log`, load 4.7–5.9):

| lattice | rank | object | generators |
| --- | ---: | ---: | ---: |
| `U + <-2>` | 3 | 0.01 s | 0.22 s (2 generators) |
| `U + U + <-2>` | 5 | 0.00 s | 1.80 s (22) |
| `U + U(2) + <-2>` | 5 | 0.00 s | 3.40 s (62) |
| `T_En` | 12 | 0.00 s | no return in 45 s (no return in 260 s for the meet) |

Three sizes, and the shape is a factor of about 8 per two ranks — `2^{1.5·rank}`
— from 0.22 s at rank 3 through 1.8–3.4 s at rank 5 to a projected
`0.22 · 8^{4.5} ≈ 2.5 · 10^3` s at rank 12.  That is the growth of a
short-vector enumeration over the marked diagram, not a repetition over elements
already processed: it is a function of the lattice, and it is monotone in the
rank with no term that redoubles on the same input.

## Is the meet the waste?

If the intersection re-derived the ambient family or enumerated a coset space,
the meet would cost about what the ambient side costs and the repair would be
ours.  It does not: at the two sizes where both sides return
(`.scratch/w286-review/.tmp/probe-intersection.py`, `.scratch/w286-probes/meet.log`),

| lattice | ambient stabilizer's generators | the meet's generators |
| --- | ---: | ---: |
| `U + U + <-2>` | 3.04 s | **0.93 s** |
| `U + U(2) + <-2>` | 6.44 s | **4.81 s** |

so the meet is cheaper than the ambient side it is cut from, and the library's
own intersection route is doing its job.  The one number on that path larger
than the ambient side is the kernel subgroup's own generating family
(17.76 s against 6.44 s at `U + U(2) + <-2>`), and it is the family the meet
selects from, not a second derivation of the ambient one.

## The verdict: correct and long, so a named run and a driver option

Nothing here is waste that a repair would remove: the construction is instant,
the meet is cheaper than its operand, and the growth is the indefinite port's
marked-diagram decision at a non-isotropic vector — whose algorithm is not this
repository's.  So the call goes to the image, as its own row with its own
input, and the numbers it must produce are fixed here:

* `Stab_{Gamma_{En,2}}(delta)`'s generators and count;
* the restrictions of those generators to `delta^perp`, as a subgroup `R` of
  `O(T_Co)`;
* `|rho(R)|` and the spinor signs of the restricted family;
* the comparison with the driver's `rho^{-1}(Stab_{O(q)}(J))`, whose
  discriminant image has order `|Stab_{O(q)}(J)| = 1981808640` at a `T_Co`
  plane (#360).

The disagreement case is live and is the reason the row exists: `Gamma_{En,2}`
carries the real spinor norm on the `T_En` side, so if every restricted
generator has `sn = +1`, the restricted image is an index-two subgroup of the
preimage the driver uses, and the `Gamma_{Co,2}` row is that subgroup's row.

**The dispatch.** `results/coble-kernel-incidence-rows.yml` gains a job
`restricted-stabilizer` and the input

| input | value | why |
| --- | --- | --- |
| `restricted_stabilizer` | `"true"` | runs `tests/coble_restricted_stabilizer.py` |
| `cap` | `21600` | the row's own cap, at the six hours a GitHub-hosted job allows; the projection is ~2.5·10^3 s, so 10800 s is inside the error bar and 21600 s is the ceiling the runner has |
| `rows` | `"Otilde,Otilde+"` (default) | unchanged; the restricted row is its own job and not a matrix row |

The driver's exit status says what happened: 0 the restricted image is the
preimage group's discriminant image with both spinor signs, 1 the row did not
return inside its cap, 2 the row returned and *differs*.

## The smallest case: the two descriptions agree there

The Coble statement is `Gamma_{Co,2} = R_{Gamma_{En,2}}` against the driver's
`rho^{-1}(Stab_{O(q)}(J))`.  Its shape at the smallest size one command reaches
is `L = U + U(2) + <-2>` (rank 5) with `delta` the `(-2)` generator, so
`delta^perp = U + U(2)`:

* the subgroup on `L` is the discriminant preimage `rho_L^{-1}(Stab(J_L))`,
  `J_L` the `U(2)` block's classes — the driver's own kind of object;
* the construction is the restriction of `Stab_Gamma(delta)` to `delta^perp`;
* the driver's description on the perpendicular is `rho_M^{-1}(Stab(J_M))`.

`tests/coble_restricted_stabilizer.py --lattice small --cap 200`
(`.scratch/w286-probes/small-driver2.log`, adopted runtime, load 6.8, tree
`f6c4f9c`; the same numbers at load 4 took 24 s in
`.scratch/w286-probes/smallest2.log`):

```
[R-small] delta q = -2, perp rank 4, isometric to U + U(2): True
[R-small] 144 generators of the subgroup, 61 restrictions to the perpendicular
[R-small] |rho(R)| = 2; the driver's |Stab(J)| = 2; spinor signs 40 of +1, 21 of -1
[R-small] agrees: the two descriptions have the same discriminant image
[R-small] the row returned in 81.0 s
```

So at the smallest case the two descriptions **agree in the finite image**: the
restricted image's discriminant order is the stabilizer of the class set, and
both spinor signs occur among the restricted generators, so the restriction is
not confined to `O^+(delta^perp)` — the property the `T_Co` comparison turns on.
What this does not settle is equality of the two infinite groups: equal
discriminant order and both signs present are *necessary* conditions, and the
decisive comparison is the `T_En` row's, whose exit status distinguishes
`agrees` from `DIFFERS`.  The value of the smallest case is that the
construction runs end to end in one command, so a defect of the construction
itself would surface here rather than after hours at rank 12.
