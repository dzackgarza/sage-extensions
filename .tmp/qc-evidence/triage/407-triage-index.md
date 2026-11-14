# #407 — triage of `tests/groups` on `main`
The slice is `tests/groups`, files up to `test_group_adjunctions.sage` alphabetically: 39
files, 156 tests.  Files after it are #411's and are not triaged here.

The run is the repository's own invocation, one file at a time, in the published image, on
`main` at `9b29712` (2026-11-14):

    just test --no-time-gates --no-test-lint <file>

with the addopts this venv needs (`pytest-timeout` and `pytest-reportlog` are absent from
the image, so `-o addopts=` and the two repository plugins
`sage_extensions.testing.suite_budget` and `sage_extensions.testing.test_lint` are passed
explicitly).  **62 of the 156 fail**: 60 in the 38 files that finish, and 2 of the 3 tests
in the file that does not.  Each failed test below is in exactly one cause.

## Causes

| # | issue body | failing tests | state on `main` |
| --- | --- | --- | --- |
| A | `triage/407-owned-algebraic-closure-is-built-without-its-base-field.md` | 14 | `4706e99` and its replacement `525dd1b` (no test flips; the next defect on the path is B) |
| B | `triage/407-engine-identity-asks-a-coercion-map.md` | 4 | `fa7553e` and its replacement `c17910a` (3 tests green, nothing new red) |
| C | `triage/407-modules-of-a-bare-set.md` | 4 |  |
| D1 | `triage/407-conjugation-morphism-supplies-a-gap-whole-group-map.md` | 2 |  |
| D2 | `triage/407-abelianization-supplies-a-gap-whole-group-map.md` | 4 |  |
| E | `triage/407-session-namespace-omits-the-owned-group-categories.md` | 17 | `eb203aa` (8 tests green, nothing new red) |
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
| Q | `triage/407-enriques-line-stabilizer-generators-do-not-return.md` | 2 |  |

Already filed, not filed again:

| issue | tests of this slice |
| --- | --- |
| #399 — ten failing tests of the flag-orbit, parabolic-restriction and finite-index-closure modules | the 4 failing tests of `tests/groups/test_finite_index_closure_401.sage` |
| #384 — `_GapWordSection.permutation_group` rebuilds `Group(gens)` | none, **not** the file that does not finish: its red test, `test_discriminant_lifts_of_o_plus_8_2.sage`, passes on `main` at `9b29712` (53 s), and the instrumented probe of cause Q shows no `_GapWordSection` is entered on the path that hangs |

## What the bisect says

Fifteen of the seventeen causes carry the same answer, and it is not a commit that changed
behaviour: the line that raises (or the line whose absence raises) is the text of the
initial import `c731175` (Zack Garza, 2026-10-26, *Initial import of the mathematical
library from dzack-research's preamble*) or of the two commits of the same day that brought
the namespace and these tests, `14b9cc1` and `544d940`, and `git log -S` on the offending
call returns that commit alone.  The tests arrived in the same commits, so `git bisect` on
`main` has no green commit to find: the failure set is already red at `14b9cc1`, the
earliest commit that carries the tests (`issue407-legacy-14b9cc1.log`: 83 of 83 tests red
there -- for these causes, and for namespace gaps this tree has since closed).

Two tests arrived later than the rest, and their bisect is bounded below by their arrival
commit rather than by the imports: `O` (`fd5ab11`, 2026-11-02) and the file of cause `Q`
(`e87f372`, 2026-11-11).  The library they exercise is still the import's.

## The repairs in this workstream

| commit | cause | what it does |
| --- | --- | --- |
| `eb203aa` | E | binds the six owned group categories in `sage_extensions.all` |
| `4706e99`, replaced by `525dd1b` | A | builds the closure as `GF(p).algebraic_closure()` |
| `fa7553e`, replaced by `c17910a` | B | decides an engine identity by its two ends, and only then asks the engine |

Each repair is the owner's operation, not a guard:

* **E** — the repository's own test lint states the rule this repairs: `TL13` ends the run
  red on "a name that is neither bound in the file, a session name, nor an allowed
  builtin: the test reaches outside the session" (`sage_extensions/testing/test_lint.py`,
  `_session_names`).  At `14b9cc1` the lint reports `TL13 Subgroups`, `TL13 Torsors`,
  `TL13 SymmetricGroups` (17), `TL13 GeneralLinearGroups` (17), `TL13 FreeGroupQuotients`
  (14) -- and, in passing, `TL13 OwnedGroups` (45) and `TL13 FiniteGSets` (3), which later
  commits had already added, so this is a repair of a namespace that was being restored
  name by name (`issue407-lint-names-before.log`).  On this tree the same three files carry
  0 `TL13` findings and their other findings unchanged (`issue407-lint-names-after.log`).
  `CoxeterGroups` is the one name the lint cannot catch, because Sage has a category of
  that name: it resolved to Sage's, which is why those three tests failed with
  `NotImplementedError` rather than `NameError`.
* **A** — the closure of `F_p` is the prime field's own `algebraic_closure()`, the operation
  the field supplies and the one the library uses everywhere else
  (`absolute_galois_group.py:889`, `galois_characters.py:139`).  The base is `GF(p)` and
  not the owned prime field `Z/p` because the pseudo-Conway closure is implemented for
  prime fields only; that is measured, not asserted
  (`issue407-probe-closure.log`).  The first form of this repair passed the field and a
  name to the raw factory; it is superseded because the factory's own docstring says the
  method is the recommended route.
* **B** — an identity is an endomorphism, so `_engine_is_identity` answers `False` for a map
  whose two ends are not the same parent before it asks the engine anything.  The first
  form consulted `getattr(engine, "is_identity", None)`; it is superseded because that is
  the dynamic peeking `AGENTS.md` forbids and the red-flag table's
  `hasattr/getattr/isinstance to discover owned structure` (CONTRIBUTING.md), and the
  decision was available from the definition.

Neither the closure nor the identity repair changes a test assertion: 13 causes are filed
and not patched, either because the repair is not local to the cause or because the
operation it needs does not exist yet (see each issue body's `## Cause`).
