C16: A ring morphism built inside a native computation is refused as an arrow of another Mor

Every Galois-group computation over `F_5` that names the Frobenius or a cyclotomic correspondence raises `TypeError: Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`, so the open subgroups of `Gal(F_5bar/F_5)` and the finite Galois groups it generates cannot be formed.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_open_absolute_galois_subgroups_archive.sage::test_the_open_subgroup_of_the_galois_group_of_f5_fixing_f25_has_index_two`
  `Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`
  at `src/sage_extensions/categories/rings/ring_foundation.py:573: in _ringlike_mor_element`
- `tests/groups/test_open_absolute_galois_subgroups_archive.sage::test_open_subgroups_of_the_abelian_galois_group_of_f5_are_their_own_conjugacy_classes`
  `Defn: z3 |--> z3 is an arrow of another Mor; native ring computations use the protected engine crossing`
  at `src/sage_extensions/categories/rings/ring_foundation.py:573: in _ringlike_mor_element`
- `tests/groups/test_profinite_groups_archive.sage::test_frobenius_generates_each_finite_galois_group_of_f5`
  `Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`
  at `src/sage_extensions/categories/rings/ring_foundation.py:573: in _ringlike_mor_element`

Defective call: src/sage_extensions/categories/rings/ring_foundation.py:573 (_ringlike_mor_element), reached while a native ring computation builds a ring morphism.

Introduced by: not bisected: the refusal is in root commit c731175 (2026-10-26, Zack Garza); the line was blamed there. The same refusal is reached in tests/objects after #408's closure repair, so it is filed there too; the two slices share the owner.

Scope: the ring-morphism boundary of a native computation; three tests. Until it is repaired the algebraic closure these tests need is available (dda0328 landed on main), so the closure is no longer the obstruction and this is.

Triage record: `results/issue411-triage.md` (C16), slice of #411.
