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
