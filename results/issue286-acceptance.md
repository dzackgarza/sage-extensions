# `#286`, stage 1: acceptance, item by item, with the line of each

The issue body's "Accepted when" paragraph and its "Missing" line, taken one at
a time.  Every item is met except the lattice-database card, which the body
itself places outside this repository (lattice-database#7) and which the
orchestrator has said does not gate the issue.  Each row below names the artefact
and the line, so a reader can check the claim without running anything.

## The items

**1. "the call returns on `T_Co`, for each group above, the counts,
representatives, indices and incidence."**

| group | counts and representatives | incidence | index |
| --- | --- | --- | --- |
| `O(T_Co)` | 1 line orbit, 1 plane orbit — `results/issue286-the-stage-1-call.md:98-99` (one orbit of each kind), representatives at `:114-115` | 1 edge, `results/issue286-the-stage-1-call.md:117-118`, digest `99a357b6…a66c` at `:117` | 1 over the one class, `results/issue286-the-stage-1-call.md:104-105` |
| `Õ(T_Co) = ker ρ` | 527 line orbits, `results/issue286-the-stage-1-call.md:167`; 189 720 plane cusps, `results/issue286-the-stage-1-call.md:372` | 569 160 edges, `results/issue286-the-stage-1-call.md:372`, digest `f4241b86…a78a` | 1 over every class, `results/issue286-the-stage-1-call.md:239-243` |
| `Õ⁺(T_Co) = ker(ρ, sn_RR)` | 527 line orbits, `results/issue286-the-stage-1-call.md:168`; 189 720 plane cusps, `results/issue286-the-stage-1-call.md:373` | 569 160 edges, `results/issue286-the-stage-1-call.md:373`, digest `702e1e8d…7a05` | 1 over every class, same lines |
| `Γ_{Co,2} = R_{Γ_{En,2}}` | 4 line cusps and 7 plane cusps, `results/issue286-the-stage-1-call.md:446` | 13 edges, `results/issue286-the-stage-1-call.md:446`; image run 43556671111 | the plane class index, `results/issue286-the-plane-class-index-is-one-value-per-row.md:37-39` |
| `R_{Γ^K_En}` | built by restriction and identified with `O(T_Co)`, `results/issue359-tco-restricted-stabilizers.md:54-68` | inherits the `O(T_Co)` row | index 1, `results/issue359-tco-restricted-stabilizers.md:160` |
| `R_{Γ_En}` | identified with `Õ⁺(T_Co)`, `results/issue359-tco-restricted-stabilizers.md:77-90` | inherits the `Õ⁺` row | index `2·46998591897600`, same lines |

The rows are the same public call, per row label:
`tests/coble_gamma_co_2_incidence_rows.py:711` (the four labels),
`tests/coble_gamma_co_2_incidence_rows.py:748-766` (each label's subgroup, by its
construction: `lattice.Aut()`, the discriminant point stabilizer, and the two
kernel subgroups), and `tests/coble_gamma_co_2_incidence_rows.py:503`
(`row_contract`, the relation's clause).

**2. "a test records each `T_Co` value and compares it with the page's statement
above; … the test does not assert the page's number."**

* The recording mechanism, which cannot fail a row on a stated value:
  `tests/coble_gamma_co_2_incidence_rows.py:195` (`record_comparison`, printing
  `agrees`/`DIFFERS` and returning the answer) and
  `tests/coble_gamma_co_2_incidence_rows.py:216` (`record_plane_class_indices`).
  The `COUNT_MISMATCH` returns on stated numbers are gone: what remains a
  condition is the row's own contract plus mathematics (`Õ⁺ ≤ Õ` forcing at
  least as many cusps), `results/issue286-review-2026-11-18.md:77-92`.
* The test of that property:
  `tests/engineering/test_a_page_value_is_recorded_and_never_decides_the_row.py:20`.
* The `T_Co` values recorded by a test:
  `tests/lattices/test_the_coble_lattice_otilde_and_otilde_plus_line_rows.sage:66`
  (each kernel line row equals the nonzero isotropic classes of `A_{T_Co}`
  counted in the file, not typed),
  `tests/lattices/test_the_coble_lattice_from_the_cited_formula.sage:32`, `:44`,
  `:55` (the lattice, its signature and discriminant, and the 528/527 split),
  `tests/lattices/test_the_coble_gamma_co_2_plane_row_and_the_building_incidence.sage:85`
  (the `Γ_{Co,2}` plane row),
  `tests/lattices/test_the_coble_divisor_groups.sage:73`, `:83` (the two
  restricted stabilizers), and
  `tests/lattices/test_the_coble_point_is_a_summand_no_isometry_swaps.sage:46`,
  `:85` (the decomposition the point stabilizer is read in).
* The lattice itself, from the cited formula:
  `src/sage_extensions/catalogue.py:204-224` (the docstring's DK13 (3.6),
  printed p. 513, with the `E_8` sign argument and the generator names).

**3. "`Γ_{Co,2} = R_{Γ_{En,2}}`, each built by that construction, not from a
description of its image."**

Proved, not measured:
`results/issue286-gamma-co-2-is-the-discriminant-preimage.md:12` (the statement),
`:23-81` (the proof: `R_gent = ρ̄^{-1}(P)` by `prop:gamma-co-images` (3) and its
proof, `P = Stab(A_{U(2)})` by `:59`), `:83-100` (what is cited and what is not).
The driver's construction is that group:
`tests/coble_gamma_co_2_incidence_rows.py:760-761`.  The reproduction on a
specimen one command reaches: `tests/coble_restricted_stabilizer.py:215`
(`run_small`), 24.4 s at `results/issue286-the-restricted-stabilizer-cost.md:101-140`.

**4. "the index over the liftable order-four isotropic subgroups `J = [P/2]`."**

* The computation: `src/sage_extensions/categories/orthogonal_quotients.py:3152`
  (`plane_class_index`, returning `J`, `|Stab_{O(q)}(J)|`, `|ρ(Stab_Γ(P))|` and
  the index, with divisibility checked).
* The derivation that one value per row is the whole table:
  `results/issue286-the-plane-class-index-is-one-value-per-row.md:11-27`
  (`χ(Γ)` normal in `χ(O(L))` because `Γ` is a kernel; the classes are one
  `O(q)`-orbit, `46998591897600 / 23715 = 1981808640`).
* Measured at two planes of *different* classes:
  `results/issue286-the-plane-class-index-is-one-value-per-row.md:29-46`.
* Recorded per row, with the class count, and never asserted:
  `tests/coble_gamma_co_2_incidence_rows.py:216-270`.

**5. "a value that disagrees with a page-proof-only row is a defect filed on
research the same day, naming the class or plane where they differ."**

No disagreement to file: the kernel line rows are 527 with index 1
(`results/issue286-the-stage-1-call.md:167-168`, `:239-243`), which is
`sec-cusp-lifting`'s row; the incidence agrees with the independent archive on
all four numbers and the degree sequence
(`results/issue286-the-stage-1-call.md:403-412`).  The `O(T_Co)` row is
`thm:unpolarized-cusps`'s one orbit.  Nothing was filed because nothing
disagreed.

**6. "the card values for `T_Co` (lattice-database#7) take the values only after
the known-family comparisons agree."**

Open, and outside this repository: the card does not exist
(`results/issue286-the-stage-1-call.md:449`).  The comparisons it waits on are
the known families', each in its own issue, and their values agree now:
`results/issue286-the-stage-1-call.md:128-150` (ten rows, read by card tag).

## What is a reproduction and not an acceptance

Two computations are long tail and report when they report; neither is a
statement this issue's acceptance rests on.

* The `T_En`/`T_Co` restricted-stabilizer row (the restriction at rank 12),
  `tests/coble_restricted_stabilizer.py:117`, dispatched as
  `.github/workflows/coble-kernel-incidence-rows.yml:58` (the
  `restricted_stabilizer` input) and `:119-147` (its job).  Its cost and the
  reason it is long are `results/issue286-the-restricted-stabilizer-cost.md:12-66`.
  The statement it would confirm is proved above; the row is a reproduction.
* The `T_En` plane comparisons through `isotropic_orbit_representatives(2)`
  rather than `isotropic_plane_orbits(P₁,P₂)`
  (`results/issue286-the-stage-1-call.md:139-140`).  That is #316's unit: the
  issue body's verification paragraph assigns the `029J` comparisons to their
  own issue, and this one reports them as they were made.

## The relation the two kernel rows return

One correction stands in the record and is not revisited here: the run of
44392429173 took `route=divided-class`, so its rows are
`tits_building_incidence_by_divided_classes()` and their per-edge clause is the
divided-class one, not the certificate route's flag-and-transporter clause
(`results/issue286-review-2026-11-18.md:7-15`).  The numbered counts and the
degree sequence are what that route states.
