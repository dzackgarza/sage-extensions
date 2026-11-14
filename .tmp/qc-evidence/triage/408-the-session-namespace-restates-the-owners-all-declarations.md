The session namespace restates the owners' `__all__` declarations

`sage_extensions/all.py` publishes a hand-written list of names, and every area package already declares its own public surface: `sage_extensions/groups/__init__.py` states 65 names in `__all__`, `sage_extensions/categories/modules/__init__.py` states 82. Two lists, one authority: they drifted, and the drift is what the namespace cause below surfaced. When this closes, the session publishes the owners' declarations, so a constructor an owner declares is a session name by construction and the test lint's TL13 cannot report one again. The repair reaches the `__all__` lists, the import order `all.py` protects for the catalogue, and every test that resolves a name through the session, so it is filed with that scope: on this workstream's tree the tree-wide lint reports 117 TL13 findings over 41 distinct names.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):


Defective call: .

Introduced by: not bisected: no failing test of the slice reaches it; the count that states the defect is the tree-wide lint's (117 TL13 findings over 41 distinct names).

Scope: 0 files:  of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C36 of the triage in results/issue408-triage.md.
