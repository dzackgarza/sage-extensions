C08: The cardinality of a homset of owned objects is not computed

`Mor_UnitalAlg(ZZ/3, ZZ/3).cardinality()` and `Emb(rank 1 lattice, rank 8 lattice).cardinality()` both raise `cannot compute the cardinality of ...: its construction supplies no exact value or decided finite enumeration`. A user cannot count the endomorphisms of a finite field, or the embeddings of a rank-one lattice into `E_8`, both of which the library's own arithmetic decides.

Failing tests (3, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_prime_field_f3.sage::test_the_quotient_of_the_integers_is_the_prime_field`
  `AssertionError: cannot compute the cardinality of Mor_UnitalAlg(Integer Ring / Ideal (3) of Integer Ring, Integer Ring / Ideal (3) of Integer Ring): its construction supplies no exact value or decided finite enumeration (it is in Join of Category of endsets and Category of homsets of sets and Category of sets)`
- `tests/objects/test_root_lattice_a2.sage::test_the_roots_and_isometries_of_a2`
  `AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 2 and signature (0, 2)): its construction supplies no exact value or decided finite enumeration (it is in Join of Category of homsets of sets and Category of sets)`
- `tests/objects/test_root_lattice_e8.sage::test_the_invariants_of_e8`
  `AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 8 and signature (0, 8)): its construction supplies no exact value or decided finite enumeration (it is in Join of Category of homsets of sets and Category of sets)`

Defective call: the homset cardinality of the owned hom categories (`Mor_UnitalAlg`, `Emb`).

Introduced by: not bisected to a commit: the homset cardinality test is too slow at the older trees for the per-step cap, so the bisect is left with skipped candidates. It fails at `14b9cc1` earlier, with `TypeError: Cannot create a consistent method resolution order (MRO) for the category graph`; the refusal this cause reports (`decided finite enumeration`) is in the tree from the initial import `c731175` (2026-10-26, Zack Garza).

Scope: the homset cardinality rule, so it reaches every `Mor`/`Emb`/`End` cardinality in the suite.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C08).
