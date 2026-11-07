# Proposed issue for the orchestrator: the cold reflective-root enumeration exceeds the test-call ceiling

The #291 repair is pushed (`240cd3f`) and its mathematical assertions pass; the declared
gate is **not** green, and the reason is a cost, not a wrong answer. No existing issue owns
it: of the last hundred issues in this repository, the only one naming the reflective root
system is #291 itself, and the closed #273 is about a stabilizer enumeration on a torsion
module. Please file this and order it after the missing-result units.

Suggested title:

> `reflective_root_system_components()` costs 28 s cold on E8, over the 20 s test-call ceiling

Body:

```
Measured on 240cd3f with the repository's own gate (`just test`, addopts intact, nothing
blanked):

  5 passed in 29.71 s, recipe exit 1 by the test-call performance gate
    tests/lattices/test_reflective_root_system_components_of_definite_lattices.sage::
      test_the_negative_definite_e8_lattice_has_root_scale_minus_one      28.11 s > 20 s
    ...::test_the_positive_definite_e8_lattice_has_root_scale_one          0.43 s
    ...::test_a2_has_one_reflective_component_of_type_g2                    0.36 s
    ...::test_the_even_rank_one_root_lattice_has_root_scale_one             0.14 s
    ...::test_the_odd_unimodular_line_has_half_root_scale                   0.11 s

The first E8 call enumerates the 240 minimal vectors through `_square_shell`
(definite_lattices.py) and extracts the simple roots; the second E8 call in the same
process is 0.43 s, so the cost is a cold enumeration and not a per-call one.

Not resolved by, and not to be resolved by: dropping one of the two E8 signs, raising
SUITE_BUDGET's TEST_CALL_CEILING, or warming the enumeration before the assertion.
The unit is to make the cold enumeration cheaper -- the E8 shell is the 240 roots, and the
current route enumerates the coordinate box and then reduces -- or to state a heavy lane
whose ceiling is written down, as #296's T_Co specimen already needs.

Acceptance: the module above runs under the declared gate with all five assertions and no
call over the recorded ceiling.
```

Evidence: `.tmp/issue291_gate_green4.log` (the run quoted), and `TRAPS.md`'s #291 entry.

## The same family, measured again on #296's small-lattice module

`tests/lattices/test_isotropic_subobjects_of_small_finite_quadratic_modules.sage`
(`issue296_small_gate2.log`, same gate):

```
4 passed in 39.40 s, recipe exit 1 by the performance gate
  test_the_four_dimensional_two_elementary_form_has_a_non_trivial_stabilizer  37.96 s > 20 s
  test_the_even_plane_summand_gives_a_trivial_stabilizer                       0.58 s
  test_an_anisotropic_form_refuses_the_isotropic_subobject_call                0.42 s
  test_the_hyperbolic_plane_has_no_nonzero_class_at_all                        0.10 s
```

`A_{U(2)+U(2)}` is a sixteen-element form with `|O(q)| = 72`; the 37.96 s is the one-time
OSCAR/Julia startup charged to whichever test first builds an engine group in the session,
not the specimen -- the next engine-touching test is 0.58 s.  So the ceiling is exceeded by
*the first engine call of a session*, on both this module and the reflective one.  If that
is chosen as the unit rather than a per-operation cost, the acceptance should say what the
first-call budget is, because no test can both start the bridge and stay under 20 s today.

## Another selection-size cost on the same ceiling, recorded under #306 (#307)

`tests/modules/` — 79 files, 283 tests — aborts in collection before any test runs, on the
collection ceiling rather than on a test call:

```
collected 283 items
============================ no tests ran in 16.14s ============================
! _pytest.outcomes.Exit: collection took 15.80 s; the measured ceiling is 6 s !!
```

The same command on the unchanged base `7494af73`, same runtime, same interpreter wrapper,
same selection (`SAGE_PYTHON_BIND` pointing at a clean `git archive` export of that commit):

```
collected 283 items
============================ no tests ran in 16.17s ============================
! _pytest.outcomes.Exit: collection took 15.85 s; the measured ceiling is 6 s !!
```

15.80 s against 15.85 s: the cost is the size of the selection, not the tree. `suite_budget`
calibrated `COLLECTION_CEILING = 6.0` against "the current 26-test default tree" (its own
docstring, measurements 2.69–3.81 s), so a 283-test directory cannot be collected inside it
at any commit. No gate was changed, warmed, reordered or suppressed for this; the wider
affected set was run with the plugin's own `--no-time-gates` one-off *measurement* option,
which still reports every call over `TEST_CALL_CEILING` in its terminal summary.

The unit, if this is worth one: either a collection ceiling that scales with the selected
item count, or a written heavy lane for directory-sized selections. It is not evidence of a
regression in any test file, and a per-file selection collects far below the ceiling.

## A second measured call over the same ceiling (#307's affected set)

`tests/lattices/test_norm_two_root_types.sage::test_two_copies_of_e8_and_a_norm_minus_two_line_give_e8_e8_a1`,
gate on, same runtime and wrapper:

```
current tree : 21.95 s > 20 s   (in a six-module run: 3 failed, 29 passed in 35.03 s)
base 7494af73: 20.90 s > 20 s   (that module alone: 9 passed in 26.50 s, recipe exit 1 on the gate)
```

Pre-existing and unchanged by #307: the ceiling is exceeded at the base already, and the
1.05 s difference is cold-cache noise of the same family as the reflective E8 call above, not
a new unit.
