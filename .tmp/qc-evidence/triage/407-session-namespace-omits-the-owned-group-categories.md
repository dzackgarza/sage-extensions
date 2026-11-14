The session namespace omits six owned group categories, so a session gets `NameError` or Sage's homonym

`sage_extensions.all` is the surface a session and every `.sage` test reads. It exports
`Groups`, `AbelianGroups` and the rest of that block, but not `Subgroups`, `SymmetricGroups`,
`GeneralLinearGroups`, `FreeGroupQuotients`, `CoxeterGroups` or `Torsors`. Two different wrong
things follow:

* the name is in neither namespace, and the session dies with `NameError: name
  'SymmetricGroups' is not defined`, or the same for `GeneralLinearGroups`,
  `FreeGroupQuotients`, `Subgroups` and `Torsors`;
* the name *is* in Sage, with a different meaning: `CoxeterGroups` resolves to Sage's category
  of Coxeter groups, so `CoxeterGroups()([[1, 3], [3, 1]])` dies in Sage's `Category._call_`
  with `NotImplementedError` instead of building `W(A_2)`.

When this closes, `sage_extensions.all` exports those six owned categories, the library's
`CoxeterGroups` wins over Sage's homonym in a `.sage` test's own namespace, and the tests
below construct the objects they name.

Observed on `main` at `9b29712` (2026-11-14) in the published image, running the
repository's own invocation one file at a time with the gates this triage lifts:

    just test --no-time-gates --no-test-lint <file>

    NameError: name 'SymmetricGroups' is not defined
    NameError: name 'GeneralLinearGroups' is not defined
    NameError: name 'FreeGroupQuotients' is not defined
    NameError: name 'Subgroups' is not defined
    NameError: name 'Torsors' is not defined
    sage/categories/category.py:606: NotImplementedError        # CoxeterGroups()([[1, 3], [3, 1]])

## Failing tests

- `tests/groups/test_arithmetic_finite_generation_archive.sage::test_the_generators_s_and_t_of_sl2z_satisfy_the_modular_relations`
- `tests/groups/test_free_and_catalogued_groups.sage::test_a_chosen_generating_set_does_not_make_a_group_free`
- `tests/groups/test_free_and_catalogued_groups.sage::test_coxeter_group_retains_its_matrix_and_type_a2_order`
- `tests/groups/test_free_and_catalogued_groups.sage::test_free_group_quotient_retains_source_and_dihedral_relations`
- `tests/groups/test_free_and_catalogued_groups.sage::test_general_linear_arrows_are_induced_by_ring_maps`
- `tests/groups/test_free_and_catalogued_groups.sage::test_general_linear_group_retains_ring_and_rank`
- `tests/groups/test_free_and_catalogued_groups.sage::test_general_linear_rank_cannot_be_truncated`
- `tests/groups/test_free_and_catalogued_groups.sage::test_mutating_selected_coxeter_matrix_does_not_change_its_group`
- `tests/groups/test_free_and_catalogued_groups.sage::test_presentations_outside_the_computed_cases_and_foreign_relators`
- `tests/groups/test_free_and_catalogued_groups.sage::test_presented_group_arrows_are_induced_by_maps_of_presentations`
- `tests/groups/test_free_and_catalogued_groups.sage::test_quotient_descent_respects_the_selected_free_basis_labels`
- `tests/groups/test_free_and_catalogued_groups.sage::test_quotient_descent_with_identified_presenting_generators`
- `tests/groups/test_free_and_catalogued_groups.sage::test_rank_two_coxeter_infinitude_depends_on_the_bond`
- `tests/groups/test_free_and_catalogued_groups.sage::test_symmetric_group_arrows_are_induced_by_bijections`
- `tests/groups/test_free_and_catalogued_groups.sage::test_symmetric_group_of_an_infinite_set_is_outside_the_computed_cases`
- `tests/groups/test_free_and_catalogued_groups.sage::test_symmetric_group_retains_its_chosen_point_set_and_action`
- `tests/groups/test_g_sets_torsor_archive.sage::test_the_transporter_of_the_regular_c3_torsor_from_x_to_gx_is_g`

## Cause and introducing commit

The namespace came from research as `14b9cc1` (Zack Garza, 2026-10-26, *Move the session
namespace and the mathematics test suite from research*), which is also the commit that
brought these tests. `git log -S` on each of the six names over
`src/sage_extensions/all.py` returns nothing: no commit of `main` ever had them there, so the
pair has never been green on this repository.

The three `CoxeterGroups` failures are the same defect as the five `NameError` ones: one file,
one missing export list, one repair.

## Scope: filed, not patched

The repair this cause needs is not local to it, and adding the six names would be the wrong
one.  Each area package already declares its own public surface:
`sage_extensions/groups/__init__.py` states 65 names in `__all__` (including `Subgroups`,
`SymmetricGroups`, `GeneralLinearGroups`, `FreeGroupQuotients`, `CoxeterGroups`, `Torsors`),
`sage_extensions/rings/__init__.py` 81, `sage_extensions/categories/modules/__init__.py` 82,
`.../categories/sets/__init__.py` 50, `.../categories/algebras/__init__.py` 53,
`.../categories/abstract_categories/__init__.py` 39, `.../schemes/__init__.py` 86.  The
hand-written import list in `sage_extensions/all.py` is a second copy of those declarations,
and the copy has drifted.  Adding the six names the failing tests happen to use leaves the
mechanism -- two lists, one authority -- in place, and hands the next failing test the same
drift.

The correct repair is that `sage_extensions.all` publishes the owners' declared surfaces
instead of restating them: the area packages' `__all__` lists, the import order `all.py`'s
own note protects ("the catalogue constructs named lattices at import time, so it is
imported last"), and every test in the tree that resolves names through the session.  That
reaches the whole session namespace, so this cause is filed with that scope and not patched
here.

The same conclusion was reached on `main` the same day from the other direction: `50a83cb`
(#408) reverted a change that had added nineteen names to `all.py`, chosen by the failing
tests, for exactly this reason; this triage reverts its own six-name version (`eb203aa`) to
match.

One consequence worth carrying: `CoxeterGroups` cannot be caught by the lint, because Sage
has a category of that name and `sage.all_cmdline` is in a `.sage` test's builtins, so a
`.sage` test resolving it silently gets Sage's category -- `NotImplementedError` out of
Sage's `Category._call_` instead of `W(A_2)`.  A namespace that publishes each area's
declared surface binds the library's name in the test module's own globals, where it wins
over the builtin.
