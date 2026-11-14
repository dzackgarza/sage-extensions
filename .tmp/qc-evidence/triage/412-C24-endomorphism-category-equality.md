C24: Two constructions of one endomorphism category do not compare equal

`lattice.Mor(lattice)` is compared with `Free module on {Generic endomorphism of ...} over Integer Ring` and `Aut_Category(...)` with `Aut_Category(...)`: the same endomorphism category built twice does not compare equal, so `Mor(A, A) is endomorphisms` -- the session's own identity test for a hom category -- cannot be checked.

Failing tests (2, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_root_lattice_a2.sage::test_a2_has_one_endomorphism_category`
  `assert Free module on {Generic endomorphism of Integral lattice of rank 2 and signature (0, 2), Generic endomorphism of Integ...rank 2 and signature (0, 2), Generic endomorphism of Integral lattice of rank 2 and signature (0, 2)} over Integer Ring is LatticeMor(Integral lattice of rank 2 and signature (0, 2), Integral lattice of rank 2 and signature (0, 2))`
- `tests/objects/test_symmetric_group_s3.sage::test_the_set_category_automorphism_group_agrees`
  `assert Aut_Category ...ets({0,...,2}) == Aut_Category ...ets({0,...,2})`

Defective call: the equality of an owned hom/Aut category.

Introduced by: present at `14b9cc1` (2026-10-26, Zack Garza <dzackgarza@gmail.com>, "Move the session namespace and the mathematics test suite from research"), the commit that imported `tests/objects`: the same assertion fails there (`assert Free module on {{Generic endomorphism ...}} over Integer Ring is LatticeMor(...)`), so the endomorphism category has never compared equal to the one belonging to it.

Scope: the hom-category equality, so it reaches every `Mor(A, A) is ...` test in the suite.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C24).
