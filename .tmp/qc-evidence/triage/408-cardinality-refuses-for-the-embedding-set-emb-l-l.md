`cardinality` refuses for the embedding set `Emb(L, L')`

`Emb(L, L').cardinality()` raises `AssertionError: cannot compute the cardinality of Emb(...)` where the number is finite and computable (the isometric embeddings of one positive-definite rank-one lattice into a root lattice), so `roots()` and the orthogonal-group count cannot be read.

Failing tests, on main 9b29712 (2026-11-14) in the published image, one file per
pytest process (`just test -o addopts= -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates --no-test-lint -q --tb=line
<file>`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_vectors_of_square_minus_two`
  `AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 2 and signature (1, 1)): its construction supplies no exact value or decided finite enum`

The same defect also fails `tests/objects/test_root_lattice_a2.sage::test_the_roots_and_isometries_of_a2`, `tests/objects/test_root_lattice_e8.sage::test_the_invariants_of_e8`, in files that #412 now owns.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/sets/set_categories.py:2503.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: `test_hyperbolic_plane.sage` of the #408 slice (tests/objects up to
test_isomorphisms_of_a_two_element_set.sage).

Repair: open; this issue is its record.

Cause C12 of the triage in results/issue408-triage.md.
