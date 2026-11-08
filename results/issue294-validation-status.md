# Validation status of the published known-family modules (#294)

Precise record, correcting the imprecise "red by design" wording of the commit messages
that published these modules.  A test that has not been executed is **unrun**, not red:
a meaningful failure must execute the real public call and fail on its observed result
or an actual bounded failure.  No test below uses `pytest.fail`, an unconditional
expected failure, a mocked defect, a skip, or a missing fixture.

## `tests/lattices/test_enriques_polarization_orbits.sage` (published at `cdb77ae`)

Executed and passing (observed, `just test --no-time-gates --no-test-lint -k
"dsh_fundamental or doubled_model or anti_invariant"`, 3 passed in 6.30 s):

- `test_the_dsh_fundamental_domain_model_is_the_source_lattice`
- `test_the_doubled_model_matches_the_invariant_lattice`
- `test_the_anti_invariant_lattice_is_the_029j_card_lattice`

Unrun — never executed, no observed result of any kind:

- `test_case_1_line_orbits`, `test_case_1_plane_orbits`, `test_case_1_flag_orbits`
- `test_case_2_line_orbits`, `test_case_2_plane_orbits`, `test_case_2_flag_orbits`

Each would rebuild the case group (the case-1 preimage builds in 121.7 s, measured) and
call the orbit operations; the single live case-1 computation is the running probe, and
no duplicate long call is launched.  Their first execution will observe either the cited
counts or a real bounded failure.

## `tests/lattices/test_scattone_plane_orbits.sage` (published at `0cd843d`)

Unrun — all five tests, including `test_the_card_inputs_are_the_published_rank_21_lattices`.
The module was lint-checked (0 findings) but its tests were never executed locally, and
the CI run failed before collection on the shared-driver defect (ai-review-ci#494:
unrecognized `--timeout`/`--timeout-method`/`--report-log` options), which is a driver
failure, not a mathematical result of any kind.

The Scattone rank-21 plane computations have additionally not returned inside their
stated bounds in any attempt; that missing result is recorded in #294.
