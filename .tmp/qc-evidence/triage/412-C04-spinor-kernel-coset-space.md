C04: The spinor kernel's preimage is refused for the group ring it is taken in

`lattice.spinor_kernel()` refuses with `the preimage ... needs Subgroup of Fraction Field of Integer Ring^x / (...)^2 cap ...`, because the subgroup it must precompute lives in a coset space the library has not realized as finite. A user cannot compute the spinorial kernel of an integral lattice, which is the group the theory of the orthogonal group's double cover is stated in.

Failing tests (1, all in `tests/objects`), recorded on main `c8a3ced` (2026-11-14) with the repository's own `just test` and its `addopts` blanked:

- `tests/objects/test_orthogonal_group_of_a2.sage::test_the_spinor_kernel_of_a2`
  `AssertionError: the preimage {g in Orthogonal group O(Integral lattice of rank 2 and signature (0, 2)) : sn(g) = 1} needs Subgroup of Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2 cap Subgroup of Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2 generated through the finite coset space Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2/Subgroup of Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2, but Subgroup of Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2 is not known to have finite index in Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2: realize Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2/Subgroup of Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2 as a finite Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2-set and select it with Fraction Field of Integer Ring^× / (Fraction Field of Integer Ring^×)^2.select_left_cosets(...)`

Defective call: `src/sage_extensions/categories/group/predicate_subgroups.py:1181`, the preimage of a predicate subgroup.

Introduced by: not bisected to a commit: the test does not finish inside the per-step cap at the older trees, so `git bisect` is left with skipped candidates and names none. The runs do establish that the test fails at `14b9cc1` earlier, with `the spinor norm of Integral lattice of rank 2 and signature (0, 2) is computed here over represented absolute number fields, but Frac(R) = Fraction Field of Integer Ring`; the refusal this cause reports is in the tree from the initial import `c731175` (2026-10-26, Zack Garza; `git log -S 'is not known to have finite index'`), and the test has never been green on main.

Scope: the predicate-subgroup preimage, so it reaches every spinorial-kernel and preimage computation, not this lattice.

Repair: filed and not repaired in this workstream. Evidence: still red at `415c2b4`.

Triage record: `.tmp/qc-evidence/triage/412-index.md` (#412, cause C04).
