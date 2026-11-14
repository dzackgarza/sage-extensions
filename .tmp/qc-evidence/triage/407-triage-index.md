# #407 — triage of `tests/groups` on `main`
The slice is `tests/groups`, files up to `test_group_adjunctions.sage` alphabetically (39
files, 1 of which does not finish; see below). Files after it are #411's and are not triaged
here.

The run is the repository's own invocation, one file at a time, in the published image, on
`main` at `9b29712` (2026-11-14):

    just test --no-time-gates --no-test-lint <file>

with the addopts this venv needs (`pytest-timeout` and `pytest-reportlog` are absent from the
image, so `-o addopts=` and the two repository plugins `sage_extensions.testing.suite_budget`
and `sage_extensions.testing.test_lint` are passed explicitly). The 39 files collect 156 tests
(153 in the 38 files that finished, 3 in the one that does not); **60 fail**, each in exactly
one cause below.

Evidence:
`issue407-sweep-tests-groups.log` (the 77-file per-file summary of the whole directory),
`issue407-failing-tests-slice.log` (the 60 failing ids with their last error line),
`issue407-repair1.log`, `issue407-repair2.log` (the repaired tree re-run),
`issue407-legacy-14b9cc1.log` (the same files at `14b9cc1`, the commit that brought them),
`issue407-stabilizer-file.log` (the file that does not finish).

## Causes

| # | issue body | failing tests | repaired by |
| --- | --- | --- | --- |
| A | `triage/407-owned-algebraic-closure-is-built-without-its-base-field.md` | 14 | the algebraic-closure commit on `main` (no test flips: the next defect on the same path is B) |
| B | `triage/407-engine-identity-asks-a-coercion-map.md` | 4 |  |
| C | `triage/407-modules-of-a-bare-set.md` | 4 |  |
| D1 | `triage/407-conjugation-morphism-supplies-a-gap-whole-group-map.md` | 2 |  |
| D2 | `triage/407-abelianization-supplies-a-gap-whole-group-map.md` | 4 |  |
| E | `triage/407-session-namespace-omits-the-owned-group-categories.md` | 17 | the namespace commit on `main` (8 tests green, no regression) |
| G | `triage/407-sets-parameterized-by-a-group.md` | 2 |  |
| H | `triage/407-group-algebra-functor-hands-a-module-arrow-to-the-algebra-mor.md` | 1 |  |
| I | `triage/407-the-regular-representation-asserts-a-rank-it-does-not-have.md` | 1 |  |
| J | `triage/407-free-group-images-are-keyed-by-generators-not-letters.md` | 1 |  |
| K | `triage/407-named-matrix-group-degree-is-an-assertion.md` | 1 |  |
| L | `triage/407-galois-group-of-a-number-field-has-no-engine-realization.md` | 1 |  |
| M | `triage/407-decomposition-group-class-has-no-image.md` | 1 |  |
| N | `triage/407-cardinality-of-a-mor-set-of-g-sets.md` | 1 |  |
| O | `triage/407-character-quotient-witness-search-assumes-a-generator-inside.md` | 1 |  |
| P | `triage/407-cardinality-of-a-finitely-presented-group.md` | 1 |  |

Already filed, not filed again:

| issue | failing tests here |
| --- | --- |
| #399 (ten tests of the flag-orbit, parabolic-restriction and finite-index-closure modules) | the 4 failing tests of `tests/groups/test_finite_index_closure_401.sage` |
| #384 (`_GapWordSection.permutation_group` rebuilds `Group(gens)`) | none: `tests/groups/test_discriminant_lifts_of_o_plus_8_2.sage`, its red test, passes on `main` at `9b29712` (53 s) |

## What the bisect says

Every cause but two carries the same answer, and it is not a commit that changed behaviour:
the code that raises is the text of the initial import `c731175` (Zack Garza, 2026-10-26,
*Initial import of the mathematical library from dzack-research's preamble*), or of the
namespace/test import `14b9cc1`/`544d940` of the same day, and `git log -S` on the offending
call returns that commit alone. The tests arrived in the same two commits, so `git bisect` on
`main` has no green commit to find: the failure set is red at `14b9cc1`, the earliest commit
that carries the tests (`issue407-legacy-14b9cc1.log`: 83 of 83 tests red there, for these
causes and for the namespace gaps the current tree has since closed).

The two exceptions are `O` (`fd5ab11`, 2026-11-02) and the stabilizer file (`e87f372`,
2026-11-11), whose tests arrived later; their libraries are still the import's.

## The file that does not finish

`tests/groups/test_a_stabilizers_generators_generate_a_subgroup.sage` (#341's acceptance file)
does not finish in 600 s under this invocation: 1 of its 3 tests passes, the second does not
return in 40 minutes, the third never starts. It is filed separately.
