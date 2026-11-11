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
