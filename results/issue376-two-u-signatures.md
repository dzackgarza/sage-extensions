# #376 — the two models of `2U ⊕ E8(-1)²` and `2U ⊕ D16⁺(-1)` differ in signature

Stage 1, under #280.  Measured on the adopted runtime (Sage 11.0.beta5, source pin
`9f1680d2a7bcf001e50714768e6066e6652d1708`), in the worktree `.scratch/wt376` of
`omm/main = 4c9b5158`.

**Result.** `tests/lattices/test_two_u_recursive_isometry.sage::test_2U_plus_E8_squared_is_isometric_to_2U_plus_D16_plus_with_nonisometric_complements`
failed because its *construction* of the source complement had the wrong sign — not because of
`twist` or `two_u_eichler_model()`.  The catalogue's named `E8` is already the negative-definite
root lattice `E8(-1)`, so `Lattices(ZZ)("E8").twist(-1)` is `E8(+1)`: the test built
`2U ⊕ E8(+1)²`, of signature (18, 2), against `2U ⊕ D16⁺(-1)`, of signature (2, 18), and
`LatticeIsometryMor._isometry_decision` rejects that pair at the signature test
(`lattice_morphisms.py:5131`) before any classification runs.  With the construction repaired the
decision answers `True`; the module's remaining cost is the isometry *witness*, section 5.

## 1. The signatures, from the Gram matrices

`signature_pair()` is the library's own exact inertia; the eigenvalues of the same integer Gram
are an independent check (numpy, float, and far from zero here).

| lattice | Gram | `signature_pair()` | eigenvalues `(t⁺, t⁻, t⁰)` | rank, det, even, unimodular |
| --- | --- | --- | --- | --- |
| `Lattices(ZZ)("E8")` | `-C(E8)` | **(0, 8)** | (0, 8, 0), λ ∈ [-3.9890, -0.0110] | 8, 1, True, True |
| `Lattices(ZZ)("E8").twist(-1)` | `C(E8)` | (8, 0) | (8, 0, 0) | 8, 1, True, True |
| `Lattices(ZZ)(_d16_plus_gram())` | the test's rows | **(16, 0)** | (16, 0, 0), λ ∈ [0.0009, 5.7365] | 16, 1, True, True |
| `Lattices(ZZ)(_d16_plus_gram()).twist(-1)` | the negated rows | (0, 16) | (0, 16, 0) | 16, 1, True, True |

The test's two lattices and the two `two_u_eichler_model().lattice()` of them, again from the
Gram matrices:

| object | `signature_pair()` | eigenvalues `(t⁺, t⁻, t⁰)` |
| --- | --- | --- |
| `e8_squared = E8.twist(-1) + E8.twist(-1)` (as written) | (16, 0) | (16, 0, 0) |
| `d16_plus = _d16_plus_gram().twist(-1)` | (0, 16) | (0, 16, 0) |
| `e8_squared.two_u_eichler_model().lattice()` | **(18, 2)** | (18, 2, 0) |
| `d16_plus.two_u_eichler_model().lattice()` | **(2, 18)** | (2, 18, 0) |

The models' own biproduct factors are `[(1,1), (1,1), (16,0)]` and `[(1,1), (1,1), (0,16)]`:
`two_u_eichler_model()` contributed two hyperbolic planes of signature (1, 1) to each model and
changed neither complement.  Probe `probe376_signatures.py`; both `is_isometric_to` calls answered
`False` in 0.0 s on that pair, from the signature test alone.

## 2. The step with the wrong sign, read at its definition

- **`_d16_plus_gram()` is right.**  Its sixteen rows are the inner products of
  `2e₁, e₂-e₁, …, e₁₅-e₁₄, h` in the Euclidean form `x·x = Σ xᵢ²` on `ℤ¹⁶`.  Checked symbolically
  (sympy): the Gram of those sixteen vectors, `2V·(2V)ᵀ/4` for the rows `2V`, equals
  `_d16_plus_gram()` entry for entry; its determinant is 1 and every diagonal entry is even; and
  each of the sixteen has even coordinate sum after doubling, so all lie in
  `D₁₆⁺ = D₁₆ ∪ (D₁₆ + h)`.  A rank-16 unimodular sublattice of `D₁₆⁺` is `D₁₆⁺` itself, so the
  measured inertia (16, 0) is that of `D₁₆⁺(+1)`, and the `.twist(-1)` after it is what makes it
  `D₁₆⁺(-1)`, the measured (0, 16).
- **`twist` is right.**  `Lattices.ParentMethods.twist` (`lattices.py:10173`) is
  `FormValueScalings(R)(self, s)`, whose `_scaled_form_module` (`form_modules.py:4454`) rebuilds
  the form with `scaled_gram = s * form.gram_tensor()`, and the inertia of a scaled form swaps the
  pair at a negative scalar (`_lattice.py:778-786`: `signature_pair(scaled.second(),
  scaled.first())`).  Measured: `E8` (0, 8) → `E8.twist(-1)` (8, 0).
- **`two_u_eichler_model()` is right.**  `TwoUEichlerModel.__init__` (`eichler_criterion.py:78-83`)
  is `category.orthogonal_sum((plane, plane, orthogonal_complement))` with `plane = category("U")`;
  the measured factor signatures above are `(1,1), (1,1)` plus the complement unchanged.
- **`Lattices(ZZ)("E8")` is `E8(-1)`, so the source's `.twist(-1)` is the wrong sign.**  The
  root-lattice recipe returns "the exact negative-definite root lattice" (`lattices.py:3156`);
  `Lattices.IIPQ` states the same thing from the other side, reaching `II_(p,q)` for `q > p` with
  `E8` and for `p > q` with `E8.twist(-1)` (`lattices.py:3224-3243`); and `NamedLattices.Tco`
  fixes it with its source and its proof: "`E8` is the negative definite one, `E8(-1)`, and that is
  forced by the source's own signature (2, 9)" (Dolgachev–Kondo, *Enriques surfaces and
  Borel–Weil–Bott type duality*, Izv. Math. 77:3 (2013), §3, eq. (3.6), printed p. 513),
  `catalogue.py:204-214`.  Measured: the catalogue's Gram is `-C(E8)`, of inertia (0, 8).  The
  repository spells `E8(-1)²` with no twist elsewhere too, e.g. the K3 lattice
  `tests/objects/test_k3_lattice.sage:10` as `Lattices(ZZ)("U") ^ 3 + Lattices(ZZ)("E8") ^ 2`.

So `E8(-1)²` here is `Lattices(ZZ)("E8") + Lattices(ZZ)("E8")`, and the test's
`E8.twist(-1) + E8.twist(-1)` is `E8(+1)²`.

## 3. The repair

In the test only; its three assertions are unchanged and no library code changed.

- `e8_squared = Lattices(ZZ)("E8") + Lattices(ZZ)("E8")` — the two `.twist(-1)` calls removed.
- `d16_plus = Lattices(ZZ)(_d16_plus_gram()).twist(-1)` stays: that Gram is the Euclidean model,
  positive definite, so it needs the twist.
- Both docstrings now state the convention, where the repository fixes it, and that
  `_d16_plus_gram()` is the Euclidean model.

## 4. The decision, measured

`e8_squared` and `d16_plus` are both of signature (0, 16) and both even unimodular, so the pair is
now in one genus and the decision goes past the signature test.

| call | answer | cost |
| --- | --- | --- |
| the complements: `e8_squared.is_isometric_to(d16_plus)` | `False` | 43.3 s |
| the models: `source.is_isometric_to(target)` | **`True`** | 126.1 s |

Of the 126.1 s, 68.0 s and 56.6 s are the same step twice: `_isometry_decision` compares
`discriminant_module().invariant_factors()` of the two endpoints (`lattice_morphisms.py:5182`), and
`_descended_quadratic_gram` (`discriminant_modules.py:960-967`) evaluates the owned pairing on all
`rank²` pairs of the dual basis.  Both answers are `[]`, correctly, since determinant 1 forces a
trivial discriminant group.  That is a performance defect of a different owner and is not repaired
here.

## 5. The witness, and what is still open

The third assertion asks for a witness, `source.isometry_to(target)`, whose route for an indefinite
pair of rank at least three is the port's Eichler recursion
(`lattice_morphisms.py:5333` -> `sage_indefinite_port.indefinite.marked_lattices.isometry` ->
`EichlerRecursion.isometry` -> `_indefinite_isometry` -> `OrbitCoverModel.covering_vectors`).
Measured on the target model `2U ⊕ D16⁺(-1)`, whose signature (2, 18) has positive index two so the
`case _` branch of `_indefinite_isometry` runs:

| step | cost |
| --- | --- |
| `OrbitCoverModel(target)` | 0.08 s |
| `_engine_component_matrix` of the model's Gram tensor (a `_BiproductGram`) | 0.00 s |
| 5 owned pairings `b()` on the model basis | 0.01 s |
| `source_easy_generators(model)` -> 8 generators | 4.3 s |
| `covering_vectors(0, 1)` -> one covering vector | 37.2 s |

so one covering step of one level costs tens of seconds and the recursion visits a level per
hyperbolic pair. `source.isometry_to(target)` did not return inside a 2400 s run, and the stacks
taken during it sat in `OrbitCoverModel._computed_easy_generators`
(`eichler.py:532`, the model's Gram built entry by entry) and in
`primitive_covering_vectors -> right_coset_transversal -> stabilizer_of_lattice ->
source_generator_matrices`, i.e. inside the pinned port's own covering machinery, not in this
library's decision.

The decision itself is not the cost: with the repair, assertion 1 takes 43.3 s and assertion 2
126.1 s. What the module's third assertion needs is the port's witness, and that is what this issue
cannot yet deliver.

### The witness is blocked at both ranks

One Witt cancellation reduces the pair to positive index one, `U + E8(-1)^2` against
`U + D16^+(-1)`, since `2U + K = U + (U + K)` and an isometry of the complements extends by the
identity on the remaining plane (Witt cancellation, Milnor--Husemoller, *Symmetric Bilinear Forms*,
Ch. I, Thm. 3.2 and Ch. II, Sec. 4).  Measured on that pair:

| call | answer | cost |
| --- | --- | --- |
| `(U + E8^2).is_isometric_to(U + D16^+)` | `True` | 28.4 s |
| `(U + E8^2).isometry_to(U + D16^+)` | no answer | killed at 300 s, stack in `lorentzian_cells.py` |

The stack of the killed call is the port's cell traversal: `lorentzian_isometry`
(`lorentzian_cells.py:495`) -> `LorentzianPerfectComplex.isometry_to` (:2723) ->
`_expand_traversal_once` (:2641) -> `_facet_mask_data` (:1512) -> `facet_keys` (:1437) ->
`_iter_cell_halfspace_pairing_rows` (:1110) -> `_normaliz_cell_h_presentation` (:1058).  So the
positive index two pair at rank 20 needs the covering machinery (`_indefinite_isometry`, case `_`)
and the positive index one pair at rank 18 needs the perfect-cell traversal; neither returns inside
the runs above.  Both are the pinned port's own computation; this library's decision is fast (its
`discriminant_module()` step aside) and, with the repair, correct.

**Status.** Assertions 1 and 2 of the test hold with the repair; assertion 3, the witness
`source.isometry_to(target)`, does not return.  The module is therefore still red — on the witness
rather than on the signature — and the issue stays open on that.
