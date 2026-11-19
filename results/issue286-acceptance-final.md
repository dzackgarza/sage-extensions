# `#286` stage 1: acceptance, final state, item by item

Every item of the issue body's "Accepted when" paragraph is met.  Two units are
named at the end that are not acceptance items: one readability change to a
protocol three consumers share, and one condition left unevaluated.  Each row
below gives the artefact and the line.

## The items

**1. "the call returns on `T_Co`, for each group above, the counts,
representatives, indices and incidence."**

| group | counts | incidence | index |
| --- | --- | --- | --- |
| `O(T_Co)` | 1 line, 1 plane — `results/issue286-the-stage-1-call.md:98-99`, representatives `:114-115` | 1 edge `:117-118` | 1, `:104-105` |
| `Õ(T_Co)` | 527 lines `:167`, 189720 planes `:372` | 569160 edges `:372`, digest `f4241b86…a78a` | 1 per class `:239-243` |
| `Õ⁺(T_Co)` | 527 `:168`, 189720 `:373` | 569160 `:373`, `702e1e8d…7a05` | same |
| `Γ_{Co,2}` | 4 lines, 7 planes `:446` | 13 edges `:446` | `results/issue286-the-plane-class-index-is-the-fibre.md` |

The counts are *derived*, not taken from the runs:
`results/issue286-the-four-items-reargued.md:99-124` (527 from Witt and the
528/527 split; 189720 from `23715 = |O(q)|/|Stab(J)|` and the ambient index 8;
569160 from three line classes per plane class).

**2. "a test records each `T_Co` value and compares it with the page's statement;
the test does not assert the page's number."**
`record_comparison` and `RECORDED_COMPARISONS`
(`tests/coble_gamma_co_2_incidence_rows.py:195-213`), the run-path test
`tests/engineering/test_a_row_whose_counts_differ_from_the_archive_still_decides.py`,
and the property test
`tests/engineering/test_a_page_value_is_recorded_and_never_decides_the_row.py:20`.

**3. "`Γ_{Co,2} = R_{Γ_{En,2}}`, each built by that construction."**
Proved: `results/issue286-gamma-co-2-is-the-discriminant-preimage.md:12`, proof
`:23-81`, the step that decides it `:59`.  The driver's construction is
`tests/coble_gamma_co_2_incidence_rows.py:760-761`.

**4. "the index over every liftable order-four isotropic subgroup `J = [P/2]`."**
The index is the ambient quotient, `8` on `T_Co`, constant by conjugacy, and
recorded per row from the plane's own parabolic:
`results/issue286-the-plane-class-index-is-the-fibre.md` (`src/sage_extensions/
categories/orthogonal_quotients.py:3152` for the subgroup's own quantity, which
is a different datum).  The three-row table there is measured; the `Γ_{Co,2}`
row's distribution is measured too
(`results/issue286-the-gamma-co-2-distribution-measured.md`: six class-orbits,
seven plane orbits over them).

**5. "a value that disagrees with a page-proof-only row is a defect filed the
same day."**  None disagrees: `results/issue286-the-four-items-reargued.md:126-141`
lists the card comparisons, all agreeing.

**6. "the card values for `T_Co` take the values only after the comparisons
agree."**  Card `6JRR` exists and all six of its fields are compared:
rank/signature/determinant/|O(q)| in
`tests/lattices/test_discriminant_form_of_the_coble_lattice.sage:102-107,161,220`,
and `isotropic_classes`/`isotropic_orbits` in
`tests/coble_card_isotropic_orbits.py` (`results/issue286-the-card-fields-have-a-reader.md`).

## And the three group questions of this session, answered

* The `Õ⁺` row builds **exactly** `O⁺(T_Co) ∩ ker ρ`
  (`lattices.py:5108`, with `T_Co`'s proved 95-generator family at `:5126-5156`),
  and the stable group and the kernel return the same line row on the two small
  specimens (`results/issue286-which-group-the-otilde-plus-row-builds.md`).
* 527 is a **lower bound** for every subgroup of the kernel, because a kernel
  element fixes every divided class; the owner's 2 is the card's
  `isotropic_orbits`, the `O(q)`-orbits on isotropic *classes*.
* The 3-over-2 specimen is the second ambient orbit split in two, not a second
  class (`results/issue286-three-lines-over-two-classes.md`), and the split datum
  is decoded (`results/issue286-the-splitting-datum-decoded.md`).

## Two units that are not acceptance items

**a. `"NOSPLIT"` conflates three proofs.**  `orthogonal_quotients.py:1700`,
`:1736` and `:1742` return the same string for, respectively, a reflection
witness, the zero-class case, and the sign-pattern spanning — three different
arguments that fail differently.  Three consumers compare it by equality
(`orthogonal_quotients.py:4674`, `lattice_morphisms.py:5046`,
`tests/lattices/the_enriques_pointed_stabilizer_row.py:59`), so the separation
has to keep that equality: the shape is a `str` subclass equal to `"NOSPLIT"`
carrying a `reason`, plus an exported name for each reason so a lint-clean test
can compare against the library's own constant rather than a typed literal.
That is a design change across a shared protocol, and it is proposed here rather
than made in a turn's tail.

**b. The reflection's condition at the second line.**  `r` orthogonal to `v`, an
integral reflection vector, in the subgroup (`:1690-1700`) is stated but not
evaluated at the specimen's second line, which is what would say *why* no witness
exists there.
