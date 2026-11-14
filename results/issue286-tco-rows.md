# #286: the group rows on T_Co, on the indexed lift locus

The lattice is `NamedLattices.Tco` = `<2> + (U + E8(-1))(2)`, Dolgachev--Kondō, Izv. Math.
77:3 (2013), §3 eq. (3.6), printed p. 513 (built at `611f7c8ba6`).  The call is the
existing public one: `subgroup.isotropic_orbit_representatives(1)` for the line rows,
`(2)` and `tits_building_incidence()` for the plane rows and the incidence.  Each row
below was run on the repaired tree (the indexed lift locus,
`results/issue286-locus-index.md`) with the port bound at `991b88b0`.

The page statements each row is compared with are the issue's own table: `O(T_Co)`
transitive on primitive isotropic vectors (`thm:unpolarized-cusps` via
`prop:tco-split-maximal`, page proof only); `Õ(T_Co)` and `Õ⁺(T_Co)` with 527 line orbits,
index 1 over every class (`sec-cusp-lifting`, research `3077f6789c`, page proof only);
`R_{Γ^K_En} = O(T_Co)` and `R_{Γ_En} = Õ⁺(T_Co)` (`prop:gamma-co-images`, page proof
only).  None of these numbers is asserted by a test; a computed row that disagrees with a
page-proof-only row is a defect filed on research the same day.

Rows are appended as they return; wall times are load-inflated (three foreign heavy jobs
on the 4-CPU VM during the runs below; the peakrss headers of the logs record the
available memory at the time).

## `O(T_Co)` (`R_{Γ^K_En}`, page (2) states this row is `O(T_Co)`)

The call `Tco.Aut().isotropic_orbit_representatives(1)`, the row of
`tests/lattices/test_the_coble_lattice_line_orbit_call_returns.sage` (#292).  The row
returns: **1 orbit**, the recorded representative `-e_1` with `[v/2] = -[2]`,
`div = 2` (#292's record at `7519715a51`, `results/issue322-locus.md`'s
`probe26`: `(-e_1, -[2], 2)`); the count is pinned by the locus test's ground-truth
comparison (`test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`,
131072 = 131072 on `T_Co`, 16 = 16 and 4 = 4 on the controls), not by a page number.
This turn's gate run of the row (`.tmp/p286-gate2.log`: 8 passed in 783.30 s, the row
itself 770.73 s, the machine's load falling from 7.5 to 2.5 during the run) is its
evidence on the repaired tree.  The page's `thm:unpolarized-cusps` via
`prop:tco-split-maximal` states transitivity (1 orbit); the row agrees with it.

The plane row and the incidence do not return on this tree:
`isotropic_plane_orbits` raises on `T_Co` (its docstring names `T_Co` as the motivating
refusal), so the incidence stops at its first plane cusp.

## `Õ(T_Co)` (the kernel row, `ker rho`)

The call `Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)`, the row #310's
`96d8373` wires through `_line_orbit_from_divided_classes`.  **It does not return within
the adopted runtime's 6144 MiB memory guard.**  Two probes, one load window each:

1. `.tmp/p286-row-otilde.log` (14:47-16:15, load 5-19): the machine's own free memory was
   the killer — the process peaked at 4911 MiB RSS while the VM's available memory fell
   to 903 MiB, and the probe died silently inside the residue loop.  Its stacks show the
   row had already passed the ambient `O(T_Co)` stage and the character-image sweep.
2. `.tmp/p286-row-otilde2.log` (16:17-17:28, load 1-7): the peakrss guard itself fired at
   **6155 MiB peak single VmHWM** (`launcher exit: 143`), the stop line being

```
  lattices.py:9988 in is_primitive
  lattices.py:6730 in isotropic_lines_by_divided_class
  orthogonal_quotients.py:2159 in _line_orbit_from_divided_classes
  orthogonal_quotients.py:2205 in _subgroup_isotropic_orbit_representatives
```

after passing the ambient stage and the character-image sweep, so the residue loop's
own per-candidate primitive check (`is_primitive` -> `is_injective`) drives the row past
the guard.  No count, representative or index is therefore stated for this row: the page
states 527 line orbits, index 1 over every class (`sec-cusp-lifting`, research
`3077f6789c`, page proof only), and nothing this turn computed can be compared with it.
The row's stop is the memory ceiling, not the mathematics: the same construction on
`T_En` measured 5 lines in 113.7 s (`.tmp/p286f-gamma-line2.log`) and the `T_Co` case of
the divided-class construction ran at 59.86 s at `6db8551ae9`
(`.tmp/p310-construction.log`).

## `Õ⁺(T_Co)` (`R_{Γ_En}`, page (1) states this row is `Õ⁺(T_Co)`)

The call `Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)`.
**It does not return within the adopted runtime's 6144 MiB memory guard either.**  The probe
(`.tmp/p286-row-otildeplus2.log`, run on the current main `9e19dda` with #339's repair
`6d486c210f` in its history) was killed by the guard at **6150 MiB tree RSS** (`launcher
exit: 143`, `STOPPED_AT_MEMORY_LIMIT`), after passing the ambient `O(T_Co)` stage and the
class-route refusal, the stop line being

```
  orthogonal_quotients.py:143 in permutation_group
  orthogonal_quotients.py:150 in _to_permutation
  orthogonal_quotients.py:1345 in splitting_isometries
  orthogonal_quotients.py:2286 in _subgroup_isotropic_orbit_representatives
```

so the character image's own permutation group is what drives the row past the guard: the
ambient `O(T_Co)` row peaks at ~530 MiB (`.tmp/p286-row-otildeplus.log`), and the blowup
happens in the quotient's `permutation_group`.  The page states 527 line orbits, index 1
over every class (`sec-cusp-lifting`, research `3077f6789c`, page proof only); no count,
representative or index is stated for this row either.

The row was run twice on this tree with the same outcome: an earlier probe
(`row_otildeplus_diag.py`, `.tmp/p286-row-otildeplus-diag.log`) was killed at its own
900 s cap while still inside the ambient stage, confirming the row's ambient stage alone
exceeds 900 s and the memory stop is the quotient's, not the ambient row's.

## The restricted stabilizers `R_Γ` (not run this turn)

- `R_{Γ_{En,2}} = ρ̄^{-1}(P)`: `P` is a stabilizer inside `O(A_{T_Co})`, whose own order
  does not return (`groups.py:540` -> `fqf_orthogonal._isom_fqf`,
  `results/issue286-tco-run.md`'s row 3), so this row stops before the call is reached.
- `R_{Γ^K_En} = O(T_Co)` and `R_{Γ_En} = Õ⁺(T_Co)`: the restricted-stabilizer construction
  itself (`Stab_Γ(δ)` restricted to `δ^⊥`, δ the `(-2)`-vector of `T_En` with
  `δ^⊥ ≅ T_Co`) is measured at 252 s for the stabilizer's 339 generators plus 277 s for
  the restriction (`p286e-coble-groups.log`), and the page's containment
  (`R_{Γ^K_En} = O(T_Co)`) checked `True` on all 339 — but no row through the public
  call was run this turn.

The machine's memory ceiling (the `Õ` and `Õ⁺` rows' 6150-6155 MiB against the 6144 MiB
guard) and the time budget are what stopped this turn at three rows of six (the `O` row
returned; the two kernel rows stopped at the guard); the remaining three are each a next
unit's run, not a mathematical obstruction.
