# #359 — the restricted stabilizers of the Coble divisor on `T_Co`

Stage 1 of the `F_Co` pipeline (sub-issue of #286). The lattice is
`T_Co = <2> + U(2) + E8(-2)` (Dolgachev–Kondō, Izv. Math. 77:3 (2013), §3
eq. (3.6), printed p. 513). `delta` is the `(-2)`-vector of
`T_En = U + U(2) + E8(-2)` whose perpendicular is `T_Co` (same source, the
sentence after Prop. 3.2, p. 513), and the two groups are the images in
`O(delta^perp)` of `Stab_Gamma(delta)` for `Gamma = O(T_En)` (`R_{Gamma^K_En}`)
and `Gamma = Otilde^+(T_En) = ker rho ∩ ker sn_RR` (`R_{Gamma_En}`).

Everything below is measured in the adopted runtime (Sage 11.0.beta5, Python
3.14) at the fetched `main` `7d785fc`, the port bound at `991b88b0`. All numbers
are measurements, not card values, and no page statement is used as an expected
value: the page's two rows (`prop:gamma-co-images`) are compared with, and the
comparison is stated.

## The construction, as the issue states it

`delta = e_e - e_f`, `q(delta) = -2`, `delta^perp` rank 11, determinant `-2048`,
signature `(2, 9)`, `is_isometric(NamedLattices.Tco) = True` (3 s). The image is
built by restricting the stabilizer's own generators to `delta^perp`
(`perp.O()({label: inclusion.lift(isometry(inclusion(vector)))})`); nothing is
read from a description of the image.

## The index, and why the finite index is the integral one

Write `rho` for the discriminant representation of `T_Co` and `sn_RR` for the
real spinor norm. `psi = (rho, sn_RR)` maps `O(T_Co)` **onto**
`O(q) × {±1}`: `|rho(O(T_Co))| = 46998591897600` measured here
(`perp.discriminant_image()`, 24.1 s), and both spinor signs occur among the
restricted generators below. So `Otilde^+(T_Co) = ker psi` has index
`2 · 46998591897600 = 93997183795200` in `O(T_Co)`.

Both images contain the kernel of their group's `psi`:

* `R_{Gamma^K_En} ⊇ Õ(T_Co) = ker rho`: for `h` there, `h ⊕ 1` acts trivially
  on `A_{T_Co} ⊕ A_<delta>`, hence trivially on the subquotient
  `A_{T_En} = c^perp/<c>` (the glue class `c` of the index-two overlattice
  `T_En ⊃ T_Co ⊕ <delta>`), so `h ⊕ 1 ∈ Õ(T_En)`; and `sn(h ⊕ 1) = sn(h)`.
* `R_{Gamma_En} ⊇ Õ⁺(T_Co) = ker psi`: the same `h` has `sn(h) = 1` by
  hypothesis.

So `[O(T_Co) : R_Gamma] = |psi(O(T_Co))| / |psi(R_Gamma)|` in both rows, and the
index below is the index in `O(T_Co)`, computed from the images of the
constructed generators under `rho` and the real spinor norm.

For `R_{Gamma_En}` the character to evaluate is `psi` on the `T_En` side:
`R_{Gamma_En} = {h : rho_{T_En}(h ⊕ 1) = 1, sn(h) = 1}`. Because the first row
below measures `R_{Gamma^K_En} = O(T_Co)`, the correspondence `h ↔ h ⊕ 1` is a
bijection `O(T_Co) → Stab_{O(T_En)}(delta)`, and `h ↦ rho_{T_En}(h ⊕ 1)` is the
stabilizer's own discriminant image on the `T_En` side — which is what the
stabilizer's generators compute, with no second construction.

## Row 1: `R_{Gamma^K_En}` (`Gamma = O(T_En)`)

| step | value | time |
| --- | --- | --- |
| `Stab_{O(T_En)}(delta).group_generators()` | 330 generators | 352.3 s |
| restriction of each to `delta^perp` | 330 isometries of `T_Co` | 40.6 s |
| the generated subgroup | built | 1.2 s |
| `rho` on the 330 | 330 images | 24.7 s |
| `\|<rho(g)>\|` | **46998591897600** | 0.2 s |
| `\|rho(O(delta^perp))\|` | **46998591897600** | 24.1 s + 0.1 s |
| `sn_RR` on the 330 | 297 with `+1`, 33 with `-1` | 11.8 s |
| index `2·46998591897600 / 93997183795200` | **1** | |

The finite image is the whole discriminant image and both sign labels occur, so
`|psi(R)| = |psi(O(T_Co))|` and the index is `1`: **`R_{Gamma^K_En} = O(T_Co)`**.

The page (`prop:gamma-co-images`) states exactly this. It is also settled
without the page: `main`'s
`tests/lattices/test_the_coble_divisor_groups.sage` check — every generator of
`O(delta^perp)` lies in the constructed image (3.5 s in the record,
`.tmp/p286e-coble-groups.log`) — is the same statement on the integral side, and
the new test below compares the two computations with each other.

## Row 2: `R_{Gamma_En}` (`Gamma = Õ⁺(T_En)`)

The same stabilizer family, with the discriminant image taken on the `T_En` side
(the map `h ↦ rho_{T_En}(h ⊕ 1)` of the section above):

| step | value | time |
| --- | --- | --- |
| `Stab_{O(T_En)}(delta).group_generators()` | 331 generators | 287.1 s |
| `rho_{T_En}` on the 331 | 331 images | 35.7 s |
| `\|psi(O(T_Co))\|` | **46998591897600** | 0.1 s |
| index `2·46998591897600` | **93997183795200** | |

`R_{Gamma_En} = ker psi` has index `93997183795200 = 2·|O(q)|`, which is the
index of `Õ⁺(T_Co) = Õ ∩ O⁺` — **`R_{Gamma_En} = Õ⁺(T_Co)`**, the page's second
row, and therefore (as #286 states it) the `Õ⁺(T_Co)` row of #357.

A control that is *not* a row of this issue, run first because it was built with
the spinor kernel of `T_En` alone: with `Gamma = O⁺(T_En) = O(T_En) ∩ ker sn`
(no discriminant kernel), the image is `O⁺(T_Co)`, index **2**:
348 generators in 476.8 s, `sn` on `T_En` 309 `+1` / 39 `-1` (23.1 s), the
spinor-kernel family 348 elements, the restrictions all `+1` (18.0 s),
`|<rho(g)>| = 46998591897600` (0.3 s), index `2·46998591897600/46998591897600 =
2`. It shows that the `2^10`-fold factor between index 2 and index 93997183795200
is the discriminant kernel on the `T_En` side, which is what makes row 2 a
different group from the control.

## The public call on each constructed group

**The constructed group cannot be asked the row, because a generated subgroup has
no such operation.** Both groups are generated subgroups
(`perp.O().subgroup(restricted)`); `isotropic_orbit_representatives`, `cusps` and
`tits_building_incidence` are absent from them (measured,
`.tmp/p359-probe0.log`: `False` for each, `group_generators` `True`), and the
same call on a *stabilizer* subgroup — which has the operation — stops in
`_assert_isotropic_splitting_has_character_data`, because neither carries
complete character data. That assertion belongs to the owner and is right:
listing such a subgroup instead of describing it is finite only for a definite
lattice, and a definite lattice has no isotropic vector.

**Row 1 returns, on the character group the computed image describes.** That
group is `rho^{-1}(rho(O(T_Co)))` with no sign condition (both spinor labels
occur among the generators), i.e. all of `O(T_Co)` as a character subgroup, and
it is `R_{Gamma^K_En}` itself because the index is one. On
`NamedLattices.Tco`:

| call | value | time |
| --- | --- | --- |
| `Tco.Aut().isotropic_orbit_representatives(1)` (ambient) | **1 orbit** | 1451.4 s |
| the same on `rho^{-1}(rho(O(T_Co)))` | **1 orbit** | 56.0 s |
| `rho(O(T_Co))` | order 46998591897600 | 280.8 s |

Representative: `-e_ep`, `q = 0`, `div = 2` — the class `[v/2] = -[2]` of the
`O(T_Co)` row (#292's `75197171a51`, issue286's `probe26` record
`(-e_1, -[2], 2)`). The single orbit covers the 527 nonzero isotropic classes,
so the fibre over each finite class is one class: **index 1 over every class**,
which is the group's index 1 in `O(T_Co)` read on the finite side.

**Row 2 is the `Õ⁺(T_Co)` row.** Its character group is
`rho^{-1}(1) ∩ ker sn = Õ⁺(T_Co)`, which does carry complete character data
(7.7 s to build), and the row on it **does not return in 1800 s**
(`.tmp/p359-otildeplus-row.log`, inner cap of the launcher, faulthandler dumps at
600 s and 1200 s): it is still in the ambient `O(T_Co)` enumeration, in exactly
the frames the ambient row above spends 1451.4 s in —

```
isotropic_lifts.py:584 lifts_integrally -> :586 integral_parameter_classes
  -> :234 _integral_lift_locus -> :278 integral_members
  -> port recursive.py:1720 _isotropic_pointed_isometry
  -> ... marked_lattices.py:195 primitive_marking_classes
  -> isotropic_orbits.py:1626 _isotropic_orbit_representatives
  -> orthogonal_quotients.py:2318 _subgroup_isotropic_orbit_representatives
```

— so the subgroup stage that follows it was never reached, and the recorded stop
of this row (#286 at `a8f95b60c2`: 6150 MiB inside the quotient's permutation
group `splitting_isometries -> permutation_group`) is downstream of what this cap
reached. Both stops are the row's own cost, not a result this issue needs; the
row is #357's.

## Comparison with the page (`prop:gamma-co-images`, page proof only)

| page statement | index it implies | computed index | outcome |
| --- | --- | --- | --- |
| `R_{Gamma^K_En} = O(T_Co)` | 1 | **1** | agrees |
| `R_{Gamma_En} = Õ⁺(T_Co)` | `2·46998591897600 = 93997183795200` | **93997183795200** | agrees |

No mismatch is filed: both computed indices are the page's. The comparison is
stated, not asserted — the test module compares computed values with each other
and names no page number.

## What is not measured

* The rows do not run *on the constructed groups*: the operation is not there
  (above). Row 1's count is the row of the character group the computed image
  describes, which is `R_{Gamma^K_En}` itself because the index is 1. Row 2's row
  was capped before its subgroup stage; the group it is a row of is identified by
  its computed index, not by running its row to a count.
* The two constructions differ in generator count between processes (330, 331,
  335, 343, 348 observed): the port's stabilizer generator search is not
  deterministic. Every row above is stated with the count of the run it came
  from; the index did not depend on it.
* The 6144 MiB memory guard was never reached this turn. The one silent death
  (`R_{Gamma^K_En}`'s row asked on `delta^perp` rather than on `T_Co`, 4306 MiB
  peak) happened with the VM's own available memory at 773 MiB while three other
  chats' probes were running; the same row on `T_Co` returns in 56.0 s.

## Files

* `tests/lattices/test_the_restricted_stabilizer_rows_on_tco.sage` — the test
  that compares computed values only. Run: **1 passed in 339.86 s** through
  `.scratch/sage-python-port` with `--no-time-gates --timeout=0`
  (`.tmp/p359-test2.log`); `just test-lint` on it: `1 files, 0 findings`.
* `results/issue359-tco-restricted-stabilizers.md` — this record.
