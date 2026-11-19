# `#286`: items 4, 2, 1 and 5, by argument and by smallest test

Answers to the review of 2026-11-19 in its own order.  Each of the four items is
restated as the claim it really is, with the derivation that establishes it and
the smallest test that decides it; where a number cannot be reached without a
long run, the derivation is given and the run is left as the record it is.

## Item 4 — the index over every liftable `J = [P/2]`

### The claim, restated

For a subgroup `Gamma <= O(L)` and a plane `P` of an `O(L)`-orbit, the number of
`Gamma`-orbits inside the `O(L)`-orbit of `P` is

$$
\bigl[\mathrm{Stab}_{O(q)}(J) : \rho(\mathrm{Stab}_\Gamma(P))\bigr],
\qquad J = [P/2],
$$

which is the index the issue asks for, for **every** group.  Two things were
wrong in the earlier round and are corrected here.

**Correction 1: the ambient row has the index, and now records it.**  The driver
had excluded `O(T_Co)` because it retains no character quotient.  It does not
need one: the plane's own parabolic states `|Stab_{O(q)}(D(P))|` as the bound its
generators' discriminant images are compared with
(`stabilizer_discriminant_image_orders`, `isotropic_parabolics.py:4381`) and
their quotient (`:4445`).  `record_plane_class_indices` now takes that route
where there is no quotient, and says which route it read.

**Correction 2: the constancy is proved only where `chi(Gamma)` is normal.**
The earlier note said the index is one value per row because `chi(Gamma)` is
normal in `chi(O(L))`.  That is right, and it is not available for every row:
`chi(Gamma)` is normal when it is **trivial** (`Õ` and `Õ⁺`, whose `chi` is the
discriminant representation and the real spinor norm) and when it is **all of**
`chi(O(L))` (`O(L)` itself).  It is *not* normal for `Gamma_{Co,2}`, whose
`chi(Gamma) = Stab_{O(q)}(A_{U(2)})` is the stabilizer of a point of an
`O(q)`-orbit of 23715 classes, hence of index 23715.  So:

| row | `chi(Gamma)` | index per class | state |
| --- | --- | --- | --- |
| `O(T_Co)` | `chi(O(L))` | `|Stab(J)| / |rho(Stab_{O(L)}(P))| = 1981808640 / 247726080 = 8` | constant by normality; the two orders measured at a `T_Co` plane (`results/issue360-coble-plane-row.md:48`, `:138`); recorded by the driver's parabolic route |
| `Õ(T_Co)` | `1` | `|Stab(J)| = |O(q)| / 23715 = 46998591897600 / 23715 = 1981808640` | constant by normality; measured at two planes of *different* classes (`results/issue286-the-plane-class-index-is-one-value-per-row.md:29-46`) |
| `Õ⁺(T_Co)` | `1` | `1981808640`, the same | same |
| `Gamma_{Co,2}` | `Stab_{O(q)}(A_{U(2)})`, not normal | `|Stab(J)| / |P_0 cap rho(Pi_P)|`, which the normality argument does **not** make constant | **the per-class table is owed**, and it is the only row that needs one |

So the index over every liftable `J` is settled for three rows and owed for
`Gamma_{Co,2}`.  What the earlier note got right is that the table is one value
per class for the two kernels; what it got wrong is treating that as available
for `Gamma_{Co,2}`, where the stabilizer of `A_{U(2)}` is not normal.  The
`Gamma_{Co,2}` row's per-class values are `|Stab(J)| / |P_0 cap rho(Pi_P)|`, and
the honest statement is that they must be computed, not derived.

### The smallest deciding test

`tests/lattices/test_the_plane_class_index_by_two_routes.sage` asks `|Stab(J)|`
at one plane of `U + U(2)` three ways, none of which feeds the others:

* the plane's parabolic bound (`stabilizer_discriminant_image_orders`);
* the character quotient's meet (`plane_class_index`);
* the setwise stabilizer of the class set inside `O(q)` itself
  (`stabilizer_of_classes`), with `J` built from the plane's own divided
  classes through the lattice's `divided_discriminant_class`.

The test asserts the three orders equal, that the quotient's index is the
parabolic's image order, and that the two multiply to the stabilizer's order.
The earlier test checked only the `divmod` the quotient had already done, which
it cannot do now: the third reading is a different group computation.
Measured 3.53 s and 10.63 s on two runs of the file.

## Item 2 — record the values, never assert them

### What was wrong

The earlier test called the comparison helper and re-checked a `RowOutcome` it
had itself computed.  A page-value gate reintroduced in `main` would have left
it green.

### The repair

* The driver now keeps what it compared: `RECORDED_COMPARISONS`, appended by
  `record_comparison` (`tests/coble_gamma_co_2_incidence_rows.py:195-213`), so a
  run's comparisons are data and not only a printed line.
* `tests/engineering/test_a_row_whose_counts_differ_from_the_archive_still_decides.py`
  runs the driver's `main` through `incidence_rows_run` and asks two questions of
  the *run*: the `Õ` row of `U + U + <-4>` -- one edge over one line cusp and
  one plane cusp, against the archive's `(569160, 527, 189720)` -- decides, and
  the process exits with the decided row's status; and the run records **no**
  comparison, because the archive's numbers are `T_Co`'s.  An unguarded gate in
  `main` fires on that run and the status is no longer zero, which is the
  property the earlier test lacked.
* The driver's own comparison helper keeps its test
  (`tests/engineering/test_a_page_value_is_recorded_and_never_decides_the_row.py`),
  which is where a *disagreeing* comparison is decided on data.

**What the run cannot show, and why.** A disagreement through `main` needs a
`T_Co` row, because the archive's numbers apply to `T_Co` and the driver
correctly compares nothing on another lattice; a `T_Co` row is hours.  So the
disagreement is decided at the helper and the *decided-run* property at `main`,
and the two together are what the item needs.  Stated, not glossed.

**The recorded numbers are not page numbers.**  `528` and `527` are this
lattice's computed invariants (`A_{T_Co}`'s isotropic classes), not a
page-proof-only row, so a test that asserts them asserts the computation.  The
card's two orbit fields now state the same two numbers
(`tests/cards/lattice-database-enriques.json`, `discriminant_forms.6JRR`), and
comparing against the card instead of typing them is item 6's own unit.

## Item 1 — the counts for every group, by derivation

The counts are not four independent run outputs; they follow from three proved
statements and two computed orders.

* **527 line orbits.**  `A_{T_Co}` has 528 isotropic classes, 527 of them
  nonzero (computed: `results/issue286-the-stage-1-call.md:60`); `O(q)` acts
  transitively on the nonzero ones --- Witt's theorem, the page's
  `thm:coble-isotropic-class-orbits`, and the same transitivity the `O(T_Co)`
  row exhibits (`:104-105`).  A kernel `Gamma` has `rho(Gamma) = 1`, so its
  orbits of lines inside one `O(L)`-orbit are the classes themselves: 527, with
  index 1 over each (`:239-243`).
* **189720 plane cusps.**  `23715 = |O(q)| / |Stab(J)| =
  46998591897600 / 1981808640` is the number of liftable `J`
  (`results/issue286-the-plane-class-index-is-one-value-per-row.md:11-27`), and
  the index of item 4 is 8 for the ambient group and 1981808640 for the kernels;
  `23715 * 8 = 189720` is the plane count of every kernel row.
* **569160 edges.**  Three line classes lie in every plane class (the page's
  `thm:plane-fibre`, *the incidence*: each liftable `J` has three nonzero
  classes), so `189720 * 3 = 569160`, which is also `527 * 1080`.

So the four numbers the issue tabulates are derivable from the two computed
orders, the transitivity of Witt, and one page proof of three line classes per
plane class.  The runs of 2026-11-18 are the *record* of the same numbers; under
the owner's rule they are not the evidence, and this paragraph is.

The two restricted stabilizers inherit their rows by proof, not by assumption:
`R_{Gamma^K_En} = O(T_Co)` (`results/issue359-tco-restricted-stabilizers.md:54-68`)
and `R_{Gamma_En} = Õ⁺(T_Co)` (`:77-90`) are identifications of groups, so the
`O` and `Õ⁺` rows *are* their rows.

## Item 5 — the comparison with the page-proof-only rows

The comparison that carries this item is the one against the cards, in the
smallest tests, not against the `T_Co` runs:

* `tests/lattices/test_the_stable_plus_line_row_is_the_card_row.sage` reads
  `plane_orbits["029J"]`'s `O` and `Õ⁺` line rows by tag;
* `tests/lattices/test_the_enriques_line_rows_by_card.py` reads `029J`'s line
  rows by tag;
* `tests/lattices/test_discriminant_form_of_the_coble_lattice.sage:102-107`,
  `:161`, `:220` reads card `6JRR` by tag;
* `tests/lattices/test_the_coble_lattice_from_the_cited_formula.sage:32`, `:44`,
  `:55` computes `T_Co`'s invariants and compares them with the cited formula.

None of them disagrees, which is why nothing was filed.  The `T_Co` rows
themselves have no card to disagree with: `6JRR` carries the lattice's
invariants and, by design
(`results/issue296-the-plane-count-is-not-on-a-card.md:35`), not the orbit rows.
