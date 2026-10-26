# Mathematical ownership audit for research #401

This audit covers the [issue body and all comments](https://github.com/dzackgarza/research/issues/401), including the frozen API, affine shells, and affine-line points.
It identifies the mathematical owners, hypotheses, and retained maps.

The governing rules are [mathematical dependency tracing](../CONTRIBUTING.md#mathematical-dependency-tracing), `OWN-01`, `OWN-04`, `OWN-08`, and `OWN-14`.

Source snapshot for the implementation findings: research `9e448424e5`; lean-categories `aca89befcd1ade794aa3b7a93f320de995c7a5bc`. Contract reconciliation uses research #401, updated `2026-10-08T17:38:15Z`, including its comments.
Port implementation evidence uses the previously inspected `b3fd95d` source and the local `research-401-primitives` branch.
The live [migration procedure in #396](https://github.com/dzackgarza/research/issues/396) instead pins `709f81a`, freezes names through port #33, and says to leave the port unchanged.
Those are historical migration instructions, not authority to assign specialized algorithms to research.
Current computational assignments are in [port design](../../gitclones/sage-indefinite-port/references/port-design.md#implementation-assignments) and the matching boundary section of `AGENTS.md`; the frozen API names remain, and signatures change only through port #33. The local port branch is recovery material.

## Conclusions

The issue does not call for a collection of independent lattice helpers.
Its shared constructions are:

- module morphisms, images, kernels, inverse images, and fibres;

- scalar restriction, scalar extension, and chosen integral submodules;

- bilinear and quadratic forms, restriction of forms, orthogonal complements, and isotropic quotients;

- chosen orthogonal decompositions with inclusions, projections, and comparison isometries;

- group actions, generated submodules, orbit quotients, and torsors;

- sublevel sets of positive forms and their intersections with discrete lattices.

Named lattice operations specialize these constructions.
Coordinate matrices, chosen bases, finite search bounds, and backend applicability belong to realizations.
They do not determine the mathematical domain or result type.

The definitions and counterexamples below determine the corrections to unconditional integral partners, arbitrary invariant overlattices, affine parameter kernels, lift torsors, and norm-fibre versus orbit-quotient results.
Record the resulting interface corrections through port #33. The recorded amendments specify the similarity denominator factor and the signed shell/sphere contracts.
Preserve each existing name whose mathematical meaning agrees with its operation.

## Formal dependency paths and evidence

The paths below give the shared foundation for the operation-by-operation audit.
Paths into lean-categories are relative to this document.

| Key | Formal source inspected | What it supplies; coverage limit |
| --- | --- | --- |
| F0 | [Modules/Mathlib.lean](../../gitclones/lean-categories/LeanCategories/Modules/Mathlib.lean), `ModulesOf`, `modulesToSets`; [Foundation/Sets.lean](../../gitclones/lean-categories/LeanCategories/Foundation/Sets.lean) | Fixed-ring module categories and forgetful maps to types/sets; finite, countable, and enumerated sets remain distinct. Morphisms have endpoints and composition. An enumerable presentation is additional data. |
| F1 | [Modules/Total.lean](../../gitclones/lean-categories/LeanCategories/Modules/Total.lean), `ModulesOverRings`, `fibreInclusion`, `reindex`, `reindex_eq` | The category over rings and restriction of scalars. Same-ring kernels, images, sums, and inverse images live in a fibre. Scalar extension uses the imported change-of-rings theory. This does not by itself identify a particular integral submodule of a rational space. |
| F2 | [Modules/Bilinear/Valued/Fixed.lean](../../gitclones/lean-categories/LeanCategories/Modules/Bilinear/Valued/Fixed.lean), `bilinearForms`, `BilinModuleCat`, `form`, `underlyingMap`; [Isometry.lean](../../gitclones/lean-categories/LeanCategories/Modules/Bilinear/Valued/Isometry.lean) | A form is a map from a tensor square to a value module. Its category is built from that form functor. A form-preserving arrow retains the underlying map and pairing equation. Invertibility is extra structure. This separates formed modules from their finite/projective/free refinements. |
| F3 | [Lattices/Valued/Arithmetic.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Arithmetic.lean); [Constructions.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Constructions.lean), `IsIsotropic`, `divisibility`, `scaleLattice`, `gramMatrix` | Finite/projective/free hypotheses; the zero-self-pairing predicate; divisibility as the image ideal of a pairing functional; form scaling; coordinates in a selected basis. A predicate is not an algorithm selecting a witness. |
| F4 | [OrthogonalSplitting.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/OrthogonalSplitting.lean), `isCompl_span_anisotropicComplement`; [ReflectionGeneration.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/ReflectionGeneration.lean), `extendComplementEquiv_isometry`, `extendOrthogonal` | Splitting off a nonisotropic line over a field and extending a complement automorphism while fixing that line. The inspected extension theorem fixes one ambient space and vector. The two-endpoint extension and its integral descent need their own explicit comparison with this construction. |
| F5 | [Modules/Bilinear/Valued/Witt.lean](../../gitclones/lean-categories/LeanCategories/Modules/Bilinear/Valued/Witt.lean); [Lattices/Valued/Witt.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Witt.lean), `HyperbolicSummand`, `WittDecomposition` | Orthogonal submodules, hyperbolic forms, and chosen decompositions with actual isometries. The inspected hyperbolic decomposition structures are over fields. They do not establish the integral divisibility-one splitting theorem or the full degenerate-hyperplane extension contract. |
| F6 | [Modules/Bilinear/Valued/ChangeValue.lean](../../gitclones/lean-categories/LeanCategories/Modules/Bilinear/Valued/ChangeValue.lean), `changeValue`, `changeValue_id`, `changeValue_comp` | Postcomposition of a form with a value-module map, including its functorial action. Form scaling is a specialization. A functor preserves isomorphisms; a Python return type that forgets the inverse does not express that fact. |
| F7 | [Lattices/Valued/Equivariant.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Equivariant.lean), `EquivariantLatticeCat`, `carrierRepresentation`, `groupAlgebraModule`; [Gluing.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Gluing.lean), `Overlattice`, `IsIntegralSubmodule` | Actions on formed objects, their underlying representations, and integral overlattices with inclusions. Fixed vectors and the smallest submodule generated by an orbit are different constructions. Integral-valuedness is additional to finite generation. |
| F8 | [Lattices/Valued/Signature.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/Signature.lean), `signature`, `signature_eq_of_iso`; [DefiniteIndefinite.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/DefiniteIndefinite.lean) | Inertia and definite/indefinite refinements. These sources do not alone provide the requested signed witness or affine-shell selection declaration. |
| F9 | [CategoryTheory/AffineCombinationMonad.lean](../../gitclones/lean-categories/LeanCategories/CategoryTheory/AffineCombinationMonad.lean); Mathlib [affine subspaces and inverse images](https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/AffineSpace/AffineSubspace/Basic.html) | Affine combinations are present locally; Mathlib supplies affine spaces, directions, and inverse images. An affine-combination monad is not already that construction. |
| F10 | [Lattices/Valued/IdealDual.lean](../../gitclones/lean-categories/LeanCategories/Lattices/Valued/IdealDual.lean), `idealDual`, `idealDualMap`, `idealDualInclusion`, `toRationalSpan_mem_idealDual_iff` | The ideal-valued metric dual is the kernel of the pairing map modulo the ideal. The membership theorem identifies its inverse image in the original lattice with vectors whose pairings lie in that ideal. This supplies the formal dependency for row 20. |

Each row below unfolds through these paths: a fibre uses a map and a pullback of sets; its translation action uses a kernel in the same module fibre; a formed subobject pulls back the form along its inclusion; a quotient requires the form to descend; an orbit quotient retains the action and its equivalence relation.
Finite lists are realizations of these objects only when the relevant finiteness is established.

The formal availability boundary is explicit: the files above were inspected, and declaration/name searches covered `LeanCategories/Modules` and `LeanCategories/Lattices`, with a broader search for isotropic reductions, Eichler transvections, affine subspaces, content ideals, and Witt extensions.
These searches locate partial foundations.
They do not establish global absence from Mathlib or all imported theories.

## Complete operation audit

Throughout this audit, the issue's square convention is `q(x)=b(x,x)`. Characteristic-two quadratic refinements are not interchangeable with this convention.
Choosing a witness, partner, basis, or base point is additional data, not a canonical invariant.

### 1. Isotropic witness — frozen `L.isotropic_vector()`

**Frozen-call reconciliation (2026-10-09):** Research exposes the exact frozen name.
It returns a nonzero lattice element, primitive over `ZZ`, with square zero.
When the nonzero zero-fibre is empty, it raises `ValueError("the lattice has no nonzero isotropic vector")`; a nonzero radical vector is a valid result.
The positive, anisotropic and radical cases are retained as specimens at the owning method.
The older discussion of a differently named `isotropic_vector_witness()` is historical, not the current public research call.

**Owner:** the nonzero zero fibre of a quadratic form, with a witness-selection operation on that represented locus.
Integral lattices specialize this after scalar extension to their rational quadratic space.

**Contract:** retain the quadratic space, its form, the selected nonzero vector, and the integral inclusion when an integral vector is requested.
Over a finite free integer lattice, denominator clearing followed by primitive normalization raises a rational witness.
In a degenerate space a radical vector is a valid isotropic witness, but it is insufficient for splitting off a nondegenerate hyperbolic plane.

**Trace:** F0 → F1 → F2 → F3. The zero-fibre predicate is present; the witness operation retains its failure contract.
`qfsolve` is the private realization over rational coefficients.
The local `isotropic_vector_witness()` changes both the frozen name and the anisotropic failure behavior and cannot stand as the agreed public entrypoint.

### 2. Vector content — frozen `v.content()`

**Frozen-call reconciliation (2026-10-09):** `v.content()` is available through the free-module owner and returns the nonnegative generator in `ZZ`, rather than the order-ideal object.
`v.order_ideal()` retains that intrinsic ideal separately.
The zero vector has content zero, while `primitive_part()` raises `ValueError` at zero.
On the lattice with Gram `[[0,6],[6,0]]`, the vector with chosen-frame coordinates `(2,3)` has content one (focused Sage); this operation does not depend on the form.
The earlier discussion of coordinate realization is a mathematical ownership caveat, not a missing research method.

**Owner:** the order ideal of an element of a module, obtained from evaluation `M* → R`, `f ↦ f(v)`. On a finite projective module this gives the intrinsic ideal represented by the coordinate ideal in a basis.
The nonnegative integer generator is a specialization for free integer modules.

**Contract:** separate the ideal from a normalized generator and from division by that generator.
The zero vector has content zero under the ideal convention; the literal maximum of positive divisors of zero does not exist.
Primitive normalization of zero is undefined.
A form plays no role.

**Trace:** F0/F1 → internal Hom/dual → evaluation → image ideal → normalized principal generator.
The module/dual foundations are present; the order-ideal declaration and its comparison with the free-coordinate realization remain unresolved.
The added `FramedFreeModules.ElementMethods.content()` is a coordinate realization, not evidence that framing is the semantic owner.
Infinite free modules require a separate comparison using finite support, rather than an unqualified finite-projective argument.

### 3. Bezout partner — frozen `v.bezout_partner()`

**Frozen-call reconciliation (2026-10-09):** The method is present at the lattice element owner.
On `ZZ` lattices it returns a selected lattice vector `h` with `b(v,h)=v.div()` by lifting through the pairing module morphism; zero has selected partner zero.
For Gram `[[0,6],[6,0]]` and coordinates `(2,3)`, focused Sage returns pairing six; `L.zero().bezout_partner()==L.zero()` also holds.
The full solution fibre is separately retained by `pairing.solution_fibre`, so the selected vector is not substituted for the affine locus.
The finite and finite-support infinite-rank branches are separate computational realizations.

**Owner:** lifting a generator of the image of a linear functional.
For a formed module, compose its correlation map with evaluation at `v` to obtain `b(v,-): M → R`.

**Contract:** over a PID with a selected generator `d` of the image ideal, return an element of the fibre over `d`. The full fibre is a torsor under the kernel.
Over `ZZ`, choose `d ≥ 0`. For `d=0`, zero is a permissible selected lift.
Over a nonprincipal image ideal, a single generator and hence this scalar-returning contract need not exist.

**Trace:** F1/F2/F3 → image factorization → fibre and kernel.
`divisibility` is already an image ideal in F3. Generic image lifting owns the computation; a lattice-local xgcd loop duplicates that responsibility.
The added method and the rational Witt consumer must use the same general lift construction once its presentation is available.

### 4. Integral hyperbolic partner — frozen `v.hyperbolic_partner()`

**Frozen-call reconciliation (2026-10-09):** The exact frozen name returns a selected integral element `h` satisfying `q(h)=0` and `b(v,h)=v.div()`, rather than the entire locus.
That locus with its inclusion is separately available from `v.hyperbolic_partner_locus()`. A primitive isotropic vector outside the radical is required; the caller violates the hypotheses otherwise.
A provably empty locus raises `ValueError("the integral hyperbolic partner locus is empty")`, as on Gram `[[0,2],[2,2]]`. The existing positive specimen on Gram `[[0,2,0],[2,2,0],[0,0,-2]]` has pairing two.
These owner-local positive and negative specimens are already retained; the general method does not assert primitive implies existence.

**Owner:** the integral point locus cut out by `b(v,w)=d` and `q(w)=0`, where `d` generates the pairing ideal.
This is a quadratic locus inside an affine linear fibre, not another linear solver.

**Contract:** retain that locus and distinguish an empty locus from an unavailable computation.
Primitivity alone does not imply a point exists.
In the even lattice with Gram `[[0,2],[2,2]]`, `v=e` is primitive and has divisibility two.
Minimal pairing forces `w=a e+f`, with square `4a+2`, so no integral partner exists.
For an even integer lattice and divisibility one, any Bezout partner `h` gives `w=h-q(h)v/2`.

**Trace:** row 3 → affine fibre → quadratic restriction → integral points; F2/F3/F5.
The added correction method handles a sufficient case; failure of that correction does not decide the whole locus.
The counterexample determines the required correction to the unconditional frozen row: selection requires a nonempty locus.
Record that correction through #33.

### 5. Integral hyperbolic splitting — frozen `R.integral_hyperbolic_splitting()`

**Frozen-call reconciliation (2026-10-09):** The named research method exists at the isotropic-reduction owner.
It returns the actual isometry `L -> U ⊥ R`, with the reduction object `R=I^perp/I` retained as the second orthogonal biproduct factor.
The inverse gives the selected comparison arrows, not only an abstract isometry class.
An even integral ambient lattice, rank-one isotropic line and divisibility-one generator are required; violating these hypotheses raises `ValueError`. The owner specimen checks the exact source and reduction-factor identities and the two-sided inverse on generating vectors.
The output is not a rational Witt decomposition or a pair of arbitrary bases.

**Owner:** a chosen orthogonal summand, specialized to an even integer lattice with a specified primitive isotropic line generated by `e` of divisibility one.

**Contract:** the reduction retains `I → I-perp → L`, the quotient map `I-perp → I-perp/I`, and its descended form.
A selected partner gives `L ≅ U ⊥ K`; the result must compare `K` with the given reduction and retain both summand inclusions/projections.
The frozen arrow points from `L` to `U ⊕ K`. A rational decomposition or an isomorphic abstract complement without that comparison is insufficient.

**Trace:** row 4 → formed restriction and quotient → F5 chosen decomposition → direct-sum maps.
Field-valued `HyperbolicSummand` is partial formal coverage.
The integral theorem and reduction comparison are still required.
The general owner is the chosen decomposition, with the reduction as the named entrypoint.

### 6. Recovering two hyperbolic planes

**Frozen-call reconciliation (2026-10-09):** Research `L.two_hyperbolic_plane_splitting()` returns `None` when two integral hyperbolic planes do not split off, or a chosen isometry `U⊥U⊥K -> L` with a two-sided inverse and the defining biproduct injections and quotient comparisons.
This reverses the single-reduction splitting arrow's direction because the two-plane construction presents a chosen model *into* `L`; consumers must not infer the direction from the method name.
Both scalar rank and genus conditions are checked at the owner, and the represented scrambled `2U + E8(-1)` specimen has passed an inverse-on-generators check.
An unavailable computation is not to be reported as a proved absence of planes.

**Owner:** repeated chosen orthogonal decomposition, using row 5 at each stage.
A two-plane or Eichler model contains this decomposition; it does not independently compute another lattice and attach splitting labels.

**Contract:** return a chosen isometry and its summand maps for `L ≅ U ⊥ U ⊥ K`. Finding a suitable divisibility-one isotropic vector is a separate integral existence/search problem.
A rational witness with larger divisibility does not refute the existence of a splitting.
A construction from a supplied complement is not recovery from an arbitrary Gram presentation.

**Trace:** rows 1, 4, 5, with the integral hypotheses retained at both stages.
The current `two_hyperbolic_plane_splitting()` composes two `isotropic_reduction().integral_hyperbolic_splitting()` arrows, their orthogonal-biproduct injections, and an explicit isometry from `U + U + K` to the original lattice.
Its `integral_hyperbolic_index()` existence check precedes an exhaustive divisibility-one null-vector search in each reduction when the initial witness is unsuitable.
The two summand injections and both inverse identities passed targeted execution on a nontrivial Gram presentation; the scrambled `2U + E8(-1)` specimen is additionally present at the owner.
Independent acceptance is not established by these examples.
`TwoUEichlerModel` remains a downstream consumer, not this decomposition's owner.

### 7. Affine integral solution locus — frozen `family.integral_members()`

**Frozen-call reconciliation (2026-10-09):** `AffineModuleFibres.ParentMethods.integral_members(integral_parameters)` retains the frozen name on a represented *solution fibre*, not on an arbitrary family.
The argument is the chosen integral parameter inclusion into the restricted-scalars rational parameter module.
It returns another `AffineModuleFibres` object with that inclusion, offset, full translation module and torsor action retained; it is not a single integral solution or a Boolean.
The method rejects an invalid rational ambient module, and requires the original fibre's target submodule to be zero (`ValueError`). The finite-rank matrix-fibre and affine-line specimens already exercise the integration.
A stopped port consumer that calls the method on a general parameterized family must first construct its linear solution fibre; silently treating `integral_members` as an enumeration is a contract mismatch.

**Owner:** inverse image of a chosen integral submodule under an affine map, after restricting scalars.
For `F: P → V`, `F(p)=c+A(p)`, and `j: M → Res(V)`, the object is the pullback of `F` and `j` on underlying affine sets.

**Contract:** when nonempty, retain a selected point, the homogeneous group `A^-1(M)`, its action, and the maps to parameters and integral values.
It is a coset of a module, but that module need not be a finitely generated lattice.
For `A(s,t)=s+t`, the homogeneous group is `ZZ*(1,0)+QQ*(1,-1)`. An injective rational parameter map into a finite-dimensional rational space gives the finite-lattice case.
A solver must not drop the rational kernel.

**Trace:** F0/F1/F9 → scalar restriction → inverse image → affine fibre and kernel action.
Existing single-preimage and finite-span operations are partial presentation capabilities.
A general mixed-scalar affine fibre has not been identified in the inspected sources.
Smith form/Hermite form and CRT are private realizations of the appropriate linear/integral pieces, not definitions of the object.
A named affine-family wrapper with only a particular matrix is insufficient.

### 8. Equation `XA + A-transpose X-transpose = B`

**Frozen-call reconciliation (2026-10-09):** `A.symmetrized_right_multiplication()` returns the based linear operator `X ↦ XA+(XA)^t`, not a solution set.
Its `solution_fibre(B)` returns the complete affine fibre and homogeneous translation action; `preimage(B)` selects only one solution and `kernel()` gives only homogeneous solutions.
The map is built over a commutative base ring and raises `ValueError` otherwise.
On the integral 2-by-2 identity matrix, focused Sage confirms `equation(fibre.base_point())=2I`, the skew generator belongs to the homogeneous kernel, and translating the selected origin by it remains inside the fibre.
The research result uses an explicit framing; an unframed general equation requires separate duality data.

**Owner:** a fibre of a linear map between modules of maps/forms.
With explicit finite framings, the displayed map is `X ↦ XA+(XA)^t`; without framings, use duality and a correctly typed symmetrization into bilinear forms.
An unframed map `V → W` does not canonically identify either space with its dual.

**Contract:** preserve the coefficient map, parameter module, target module, right-hand side, full affine fibre, and homogeneous kernel.
Integral solutions are the intersection of that fibre with a chosen integral parameter module, not merely the integral homogeneous kernel.
Commutativity suffices for matrix linearity; division by two is not allowed over arbitrary rings.

**Trace:** F1/F2 → Hom modules and duality → linear map → row 7. The added `symmetrized_right_multiplication()` exposes a based linear operator and is useful as a realization/composite.
It is not the shared solution-space abstraction, and `preimage(B)` returns only one point.
Matrix coordinates must remain a selected presentation of the general construction.

### 9. Invariant overlattice — frozen `G.invariant_overlattice(L)`

**Frozen-call reconciliation (2026-10-09):** The exact name is implemented at the group action owner and returns an `OrbitSpanLattices(ZZ)` object, not a matrix or an arbitrary lattice isomorphism.
It retains the orbit-generated submodule construction, its ambient inclusion and action.
The group must be included in the orthogonal group of the specified rational span; an unrelated action raises `ValueError`. The implementation rejects non-`ZZ` lattices with `TypeError`, and its finite-rank realization reports that limitation explicitly.
For a nondegenerate `L` the finite containing bound comes from the metric dual; an orbit exceeding that bound or failing integral-valuedness is rejected rather than falsely claimed to have an integral invariant overlattice.
The prior targeted `diag(2,1/2)` action on U verifies that negative boundary.
The frozen consumer must not interpret this method as always producing an overlattice for any commensurating rational group action.

**Owner:** the submodule generated by the orbit of a submodule under a represented linear group action: `sum(g(L), g in G)`, equivalently the image of the group-algebra-generated module.
The action `G → Aut(V)` and the inclusion `L → Res(V)` are required data.

**Contract:** the result has its inclusion, induced action, and least-stable-submodule property.
Finite generation is not implied by commensuration: `diag(2,1/2)` on `U_Q` generates `ZZ[1/2]^2` from `ZZ^2`. A finite group or a supplied finite stable containing module gives a finite-generation route.
Integral-valuedness of the restricted form remains a separate condition.
The order-two isometry `e ↦ 2f, f ↦ e/2` gives the finite span `ZZ*(e/2)+ZZ*f`, whose cross-pairing is `1/2`; it has no integral-valued overlattice containing it.

**Trace:** F1 → group representation/group algebra (F7) → generated submodule → formed restriction (F2) → lattice/integrality refinements (F7). The inspected equivariant lattice owner supplies an action on an already integral object; that is not this closure construction.
The frozen row needs existence and value-module hypotheses.
Repeated spans until stabilization are not a definition or a termination proof.

### 10. Nonisotropic perpendicular extension — frozen `phi.extension_across(v,w)`

**Frozen-call reconciliation (2026-10-09):** Research now exposes the exact frozen name `extension_across(source_vector,target_vector,*,source_inclusion=None,target_inclusion=None)`. It returns an isometry of the scalar-extended ambient spaces, preserving the selected perpendicular embedding squares.
Both canonical inclusions and explicitly specified noncanonical embeddings are supported, including distinct perpendicular endpoints inside one ambient lattice.
Unequal or zero vector squares and wrong embedding domains/codomains raise `ValueError`. The source docstring verifies integral descent for `diag(2,2,-2)`, while targeted prior specimens verify that the extension restricts correctly along a twisted embedding `j*(-id)`; this operation itself does not assert integral descent.
The earlier trace below describes the *superseded* local `extend_from_perpendicular` implementation and is not the current API.

**Owner:** extension of an isometry between orthogonal summands, composed with chosen orthogonal decompositions.
Over a field, a vector of nonzero square splits off its line.
An isometry of the complementary spaces together with `v ↦ w` extends uniquely when their squares agree.

**Contract:** retain both perpendicular inclusions and both ambient spaces.
The partial isometry need not have subobjects as literal Python endpoints if explicit embedding data is supplied.
Scalar extension supplies the rational ambient extension; integral descent is row 12. Definiteness belongs only to an algorithm enumerating the complement isometry torsor.

**Trace:** F2/F4 → direct-sum isometry → composition with decomposition isometries → F1 descent.
The local `extend_from_perpendicular()` uses the right formula but selects another name, requires endpoint `.inclusion()` methods, and lacks a retained general decomposition.
The inspected formal automorphism extension does not alone discharge the two-endpoint generalization.

### 11. Codimension-one Witt extension — frozen `phi.witt_extension(source_inclusion,target_inclusion)`

**Frozen-call reconciliation (2026-10-09):** Research exposes the exact frozen name on a rational lattice partial isometry.
It returns a chosen ambient isometry from `source_inclusion.codomain()` to `target_inclusion.codomain()`, preserving the restriction square.
The full extension locus is separately represented by `witt_extension_locus(source_inclusion,target_inclusion)`; the chosen point must not be confused with that fibre.
Both embedding domains must match the partial isometry endpoints (`ValueError` otherwise).
In the positive codimension-one example over `U+<2>`, the extension restricts to the partial map and has a two-sided inverse.
In the degenerate ambient example, a partial map that exchanges an ambient-radical direction with a nonradical null direction raises `ValueError` for radical incompatibility.
The owner docstring retains both cases.
The research contract does not apply nondegenerate Witt extension indiscriminately to ambient spaces with radicals.

**Owner:** extension of a partial isometry along specified formed embeddings.
The isometries of the ambient objects with the required restriction form a fibre of the restriction operation; a selected extension is a point of this fibre.

**Contract:** distinguish a degenerate hyperplane in a nondegenerate ambient quadratic space from an ambient space with radical.
Over a field of characteristic different from two, a hyperplane with one-dimensional radical inside a nondegenerate space admits the usual Witt extension.
If the ambient form is degenerate, compatibility with the ambient radicals is necessary; the former theorem must not be applied unchanged.
Preserve the square formed by the inclusions and extension.

**Trace:** F2 → restriction of isometries → orthogonal complement/radical → extension theorem.
The inspected formal sources provide vector reflection transitivity, cancellation, and nonisotropic complement extension, not an identified declaration for this full contract.
Research's `LatticeIsometryMethods.witt_extension` now retains the restriction equalizer and checks ambient-radical intersections before choosing a complementary vector.
Targeted execution on `U + <2>` over `QQ` extends the isometry fixing a null direction and negating its norm-two complement on the degenerate hyperplane, preserving both the inclusion square and inverse; on ambient Gram `diag(1,-1,0)` it rejects the partial isometry interchanging the null vector `e+f` and the ambient radical.
Both are retained at the owner.
The port's norm correction by itself requires a nonzero pairing with a complementary vector and cannot establish the unrestricted degenerate-ambient claim.
Independent acceptance remains open.

### 12. Integral descent — frozen `M.integral_isometry(phi)` and `phi.is_integral_on(L)`

**Frozen-call reconciliation (2026-10-09):** Both names exist.
`M.integral_isometry(phi, source=None)` returns an integral lattice isomorphism, not a Boolean or merely an embedding; it infers the source from the retained base-change parent, or from `M.vector_space()` for an endomorphism, and otherwise requires the caller to provide `source`. It raises `ValueError` when either direction fails to factor integrally.
`phi.is_integral_on(L, target=None)` is instead a Boolean forward-factorization test, defaulting to the same target lattice.
`phi.integral_restriction(L,M)` returns `None` on failed two-sided descent.
On U, the rational isometry `diag(2,1/2)` returns `False` for `is_integral_on(U)` and `None` for `integral_restriction(U,U)` and raises the specified `ValueError` for `U.integral_isometry(phi)` (targeted Sage).
The frozen port must distinguish these three return/failure contracts.

**Owner:** factorization through specified integral subobject inclusions under scalar extension.
For `j_L: L → V`, `j_M: M → W`, factor `phi*j_L` through `j_M`. This gives an integral map.
Factor the inverse too to obtain an isomorphism.

**Contract:** retain `j_L`, `j_M`, and the commuting square.
The source integral structure must be explicit or retained in the scalar-extension datum; a bare rational space does not determine it.
Mapping `L` into `M` and mapping `L` onto `M` are different predicates.
The frozen isometry constructor raises if equality fails.
Integrality on a lattice needs a declared target integral structure.

**Trace:** F1 → subobject factorization → F2 structured map → core/isomorphism.
The local `integral_restriction(source,target)` correctly considers both directions but is a lattice-specific coordinate implementation with another name and failure result.
General module-map descent owns the arithmetic; form preservation is transported through the commuting square.

### 13. Clearing denominators of a rational isometry — frozen `phi.integral_similarity(L,E)` and `.scale()`

**Frozen-call reconciliation (2026-10-09):** The frozen `phi.integral_similarity(L,E)` is present and returns a formed-module monomorphism, not an isometry onto `E`; `sigma.scale()` is the positive denominator generator `N`, `sigma.multiplier()` is `N^2`, and `sigma.index()` is the cokernel cardinality.
With the *actual chosen frame labels* on `U`, the rational isometry `diag(2,1/2)` gives scale `2`, multiplier `4`, and finite index `4` (targeted Sage).
Literal integer comparisons against labels construct the wrong map and cannot serve as this specimen.
A failure to clear the computed denominator raises `ArithmeticError`; the non-PID or nonprincipal denominator cases require their stated ring hypotheses rather than pretending this integral scalar is universal.

**Owner:** the denominator ideal of a rational module map relative to integral structures, followed by scalar multiplication of the map and transport of its form equation.
Over `ZZ`, this ideal has a least positive generator `N` for finite-rank full lattices.

**Contract:** retain the map `sigma=N*phi`, its finite-index image, the denominator factor `N`, and its form multiplier `N^2`. Indeed `b_E(sigma x,sigma y)=N^2*b_L(x,y)`. These are different scalars.
`sigma` is generally an embedding, not an isomorphism onto `E`. On `U`, `phi=diag(2,1/2)` has `N=2`; `sigma=diag(4,1)` has index four and form multiplier four.

**Trace:** F1 → Hom and integral subobjects → denominator ideal → F2/F6 form comparison.
The current `L.similarity_mor(E,a)=L.twist(a).Isom(E)` supplies only surjective similarities and is insufficient for this request.
The [frozen amendment](https://github.com/dzackgarza/research/issues/401#issuecomment-6065197711) specifies `.scale()` as the least denominator factor `N`; the form multiplier is `N^2`. The general denominator-ideal declaration and similarity-embedding presentation remain required.

### 14. Twist functor on isometries

**Frozen-call reconciliation (2026-10-09):** The existing `TwistFunctor` transports an isometry and its inverse, preserving isomorphism-specialized endpoints.
The lattice method `L.twist(-1)` has normalized parent identity on applying the sign twist twice.
Its result is a twisted formed object, not a new underlying abelian group chosen independently.
The prior U owner specimen tests inverse composition and literal parent identity.
A general nonunit value scaling does not acquire an inverse by virtue of this sign-twist specimen; that formal equivalence boundary remains separate.

**Owner:** change of value of a formed object, by multiplication on its value module.
Restrict this functor to the relevant lattice category and its core of isomorphisms.

**Contract:** transport both a map and its inverse; preserve composition.
Scaling twice has the comparison with scaling by the product.
For the sign twist, the requested Python identity `L.twist(-1).twist(-1) is L` additionally requires constructor normalization of this action.
Mathematical functoriality alone does not imply object identity in Python.
Nonzero versus invertible scaling must be separated when claiming an equivalence over a general ring.

**Trace:** F2 → F6 `changeValue` and its identity/composition laws → core functor → chosen presentation normalization.
`TwistFunctor._apply_morphism` now preserves the isomorphism specialization and transports its inverse pair.
Targeted Sage execution confirms that twisting the identity of U yields an isomorphism between the exact twisted endpoints with a two-sided inverse, and that `U.twist(-1).twist(-1) is U`.

### 15. Lifts through isotropic reductions — frozen `R.rational_lifts(target,psi)`

**Frozen-call reconciliation (2026-10-09):** The exact `R.rational_lifts(target,isometry)` call is implemented at the isotropic-reduction owner.
It returns an `IsotropicReductionLiftTorsors` object over the rational marked-line reduction kernel, not an affine-linear space of matrices or a list of lifts.
The selected `base_point()` is additional trivialization data; the group action and evaluation are retained.
Integral points belong to the separate `integral_members()` G-object, and parameter integrality does not identify the whole integral kernel with a finite residue quotient.
Existing `U+<2>` owner specimens verify the nontrivial integral parameter/inverse and difference actions; the rank-zero boundary has an integral base point.
A chosen lift's failure to descend integrally is not a proof that the integral-lift locus is empty.

**Owner:** a fibre of the map from isometries preserving marked isotropic data to isometries of the reductions.
When nonempty this fibre is a torsor under the kernel of the restriction/reduction action.

**Contract:** specify the map on the isotropic line as well as on the reduction.
For a marked isotropic vector in a nondegenerate rational space of dimension `n`, the relevant kernel is the additive unipotent group of dimension `n-2`. Preserving only the line leaves an additional scaling parameter.
Higher-dimensional isotropic subspaces need their own kernel group and cannot inherit the rank-one dimension formula.

The parameter space can be affine while its evaluation in the space of matrices is nonlinear.
For `U ⊥ <2>` with basis `e,f,a`, the standard transvection with parameter `t*a` sends `f` to `f+t*a-t^2*e`. The midpoint of the matrices at `t=1` and `t=-1` sends `f` to `f-e`, of square `-2`; it is not an isometry.
Thus an affine-linear expression `T0+sum(lambda_i*Ti)` does not represent this lift torsor.
The transvection formula and additive parameter law are given in [Gritsenko–Hulek–Sankaran, §3.1, equations (4)–(5)](https://archive.mpim-bonn.mpg.de/3203/1/preprint_2008_114.pdf).
The midpoint calculation is a direct consequence.

**Trace:** F2/F5 → isotropic quotient and parabolic action → kernel group → torsor and evaluation → row 12 for integral members.
A chosen `.base_point()` trivializes the torsor; it does not replace its action or parameters.
Integral members, when nonempty, are a torsor under the subgroup of integral kernel elements.
Identifying that subgroup with an additive lattice needs a theorem.
The existing finite `Torsors` constructor in `group/g_sets.py` does not yet present this rational parameter torsor.
A torsor with an empty list of directions has not supplied the requested object.

### 16. Signature-defined directions — frozen `L.positive_vector()`, `S.vector_of_sign(sign)`

**Frozen-call reconciliation (2026-10-09):** Both names exist through the formed-module owner.
`positive_vector()` is `vector_of_sign(1)`; `negative_vector()` is `vector_of_sign(-1)`. These return a vector in the *original formed parent*, or `None` if the requested strict sign does not occur.
A requested sign other than `-1` or `1` raises `ValueError`. For a formed subobject of `U`, owner specimens verify that positive and negative witnesses retain the subobject parent and their form values agree under its inclusion; a negative-definite line has no positive witness.
Neither operation returns an ambient-lattice vector after silently forgetting the selected subobject.

**Owner:** witness selection in a signed locus of an ordered-field-valued quadratic form.
For a subspace, first restrict the form along its retained inclusion.

**Contract:** a nonzero vector with the requested strict sign, or the declared absence result; return an element of the specified subspace with its ambient inclusion available.
Ordering, or a chosen real place for a number field, is part of the input.
Signature can decide existence in a finite-dimensional setting but does not itself choose a vector.

**Trace:** F1/F2 → restriction → ordered value predicate → F8 existence → witness.
Rational diagonalization is a private realization.
The local positive/negative methods expose lattice conveniences; the general signed-locus operation and the frozen subspace method still need their presentation mapping.

### 17. Binary fixed-norm representations — frozen extension of `L.vectors_of_square(n)`

**Frozen-call reconciliation (2026-10-09):** Research `vectors_of_square(n)` retains the full norm fibre rather than returning orbit representatives.
On definite lattices and nonzero split binary fibres this is a finite subset with inclusion; otherwise it retains the represented square-fibre object.
The separate `binary_fixed_norm_representatives(n)` returns the selected orbit representatives with the action/quotient data, and `reduction_cycle(bound,start)` returns a period isometry with its bounded vector subset, or `None`. A split binary zero fibre is not finite and the representative method rejects its infinitely many content classes with `ValueError`. The frozen row's interpretation of `vectors_of_square` as orbit representatives conflicts with the actual mathematical return object; the stopped port must take the orbit quotient explicitly rather than changing the norm-fibre API.

**Owner:** the norm fibre as a `G`-set, followed by its orbit quotient for an explicitly selected subgroup of the orthogonal group.
Chosen representatives and transporters are data over that quotient.

**Contract:** distinguish all vectors in the fibre from one vector in each orbit.
A definite shell currently returns vectors; replacing its meaning by orbit representatives only in the indefinite case is not a signature-based specialization of the same object.
Distinguish `O`, `SO`, primitive vectors, and all vectors.
A generator of the infinite cyclic part is not the whole automorphism group.
At norm zero a split binary lattice has infinitely many content classes unless primitivity is imposed.

**Trace:** F0/F2 → norm fibre → represented action (F7) → orbit equivalence relation and quotient → representative section.
PARI supplies ordinary binary arithmetic.
The oriented reduction cycle is a specialized edgewalk algorithm owned by port #15, even though research owns its semantic period isometry and finite subset.
The copied `lattice_engines._binary_reduction_cycle` body must move to the port; its starting, stepping and stopping rules are not a research primitive.
The added nonsplit-only `binary_fixed_norm_representatives()` neither supplies the frozen API nor the retained action/quotient/automorph data.
The norm fibre and its orbit quotient have different codomains and therefore require distinct operations (`LEX-11`). Record that correction to the frozen row through #33.

The current issue body distinguishes the cases explicitly: `vectors_of_square(n)` returns all vectors for a split binary form and `n != 0`; `primitive_isotropic_vectors()` returns the primitive vectors on its isotropic lines; `reduction_cycle(bound,start)` returns the cycle automorph as an isometry and the bounded vectors met in one period, or `None`, for an anisotropic binary form.
The older frozen table instead assigns orbit representatives to `vectors_of_square(n)`. Preserve the norm-fibre meaning of `vectors_of_square`; the quotient belongs to the group action.
The cycle operation also retains its primitive positive starting vector and the action of the returned automorph; a norm-fibre quotient alone does not specify a reduction cycle.

### 18. Affine close-vector shells — frozen shell methods with a multiplier bound

**Frozen-call reconciliation (2026-10-09):** Research exports `first_close_vector_shell(t,B,M)` and `first_close_vector_sphere(t,B,M)` with the frozen names.
Each returns `None` if no multiplier in `1..M` succeeds, or a product element `(m, finite_subset)` whose finite subset retains its inclusion into the original lattice.
Sphere selection tests the exact boundary, while shell selection tests the whole signed sublevel interval; the shared `scaled_close_vector_shells` retains the fixed-m family.
A nondefinite form or a bound of the wrong sign raises `ValueError`, and a target outside the selected rational ambient is rejected.
The observed bound-zero shell returns `None`; it is not an unbounded search.

**Owner:** intersection of an affine quadratic sublevel set with a discrete lattice, and an indexed family of such intersections.
The least successful multiplier is a selection from the index set of nonempty fibres.

**Contract:** the [shell amendment](https://github.com/dzackgarza/research/issues/401#issuecomment-6065258075) specifies a definite form of either sign, with `B` of that sign.
Retain `K`, its rational ambient space, target `t`, and the fibre `{x in K : min(0,m^2*B) <= q(x-m*t) <= max(0,m^2*B)}`. The sphere fibre has equality `q(x-m*t)=m^2*B`. `first_close_vector_shell(t,B,M)` and `first_close_vector_sphere(t,B,M)` return the least successful `1 <= m <= M` and that fibre, or `None`. Exhausting the bound decides only that bounded search.
The fixed-m shell is `close_vectors(m*t,m^2*B)`. A denominator `D` with `D*t in K` supplies an unrestricted shell point at `m=D`; it supplies a sphere point by this argument only when `B=0`.

**Trace:** F0/F1/F2/F8 → signed sublevel or level locus → lattice intersection → indexed family → bounded minimum selection.
The fixed-`m` shell is the shared operation.
The local `first_close_vectors`/`affine_close_vectors` select other names and omit the frozen search bound.
Port #15 implements both bounded selections using the fixed-m shell primitive; move the multiplier loop from `definite_lattices._pari_first_affine_cvp_shell` to the port.
Research may retain frozen public dispatch methods.
An indexed family and a minimum-selection definition do not make this algorithm-specific scaling schedule a research implementation obligation.
The signed convention is settled by the amendment; the locus and selection maps remain required.

### 19. Integral points on an affine line — frozen `L.affine_line_points(base,direction)`

**Frozen-call reconciliation (2026-10-09):** The frozen callable name is present on the research lattice.
It returns `None` for an empty fibre or an element of `Sets().product((L,L))` representing `(point, primitive_step)` for a nonempty affine rank-at-most-one integral image.
The full affine point set, translation module, and evaluation map belong to the separate `L.affine_line_fibre(base,direction)` datum; the tuple is presentation data and does not replace that object.
At zero direction and integral zero base, focused Sage verifies `(0,0)` and independently verifies the retained image has cardinality one.
An empty constant image is represented by `None`, while the parameter fibre must not be identified with its image.
The frozen consumer must not treat the pair itself as an object carrying the affine inclusion.
This is a return-object distinction to retain at port #33 when that stopped stream resumes, not a request to rename the research operation.

**Owner:** row 7 specialized to the affine map `lambda ↦ base+lambda*direction`, followed by its image in the ambient rational space.

**Contract:** with nonzero rational direction, the integral point set is empty or an affine rank-one lattice; retain its inclusion and a chosen point and primitive integral step.
For zero direction, the point set is empty or a singleton, while the parameter preimage is empty or all of `QQ`. Those are different objects.
A pair of vectors is useful presentation data only when attached to the appropriate affine point set.

**Trace:** F1/F9 → row 7 → image and retained parameterization.
This is not a separate coordinate congruence algorithm on lattices.
The affine fibre must exist first.

### 20. Divisibility sublattice — requested `L.divisible_sublattice(d)`

**Frozen-call reconciliation (2026-10-09):** Research implements the exact name as `L.ideal_dual(d).integral_pullback()` and returns a formed subobject of `L`, not an independently presented Gram matrix.
Its inclusion `i`, retained ideal-dual morphism `k=map_to_ideal_dual()`, generic-fibre inclusion `j`, and ideal-dual inclusion `u` satisfy `j*i=u*k`. On Gram `diag(0,2)` and divisor `3`, this equality passed on all generators; the divisor-zero case returns the radical with rank one and also passes the square comparison.
Divisor zero is not substituted into the nonzero-divisor expression `L intersect d*L^#`.

**Owner:** inverse image of an ideal-valued metric dual along the integral inclusion into the rational span.
For `j: L -> L_Q` and `I=(d)`, form the pullback of `idealDual(ZZ,L,I) -> L_Q` along `j`.

**Contract:** return the formed submodule `D` of `L` with its inclusion `i: D -> L`, its map `k` to the ideal dual, and the commuting equation `j*i = idealDualInclusion*k`. Its vectors satisfy `b(v,L) subset d*ZZ`, as requested in the issue body.
The ideal-dual definition permits every integer `d`; at zero its pairing condition is `b(v,L)=0`, so it selects the radical.
The expression `L intersect d*L^#` needs `d != 0`; at zero it can lose a nonzero radical.

**Trace:** F1 → F2 pairing and restriction → F10 ideal dual → inverse image.
The composite is `Submodule.comap (toRationalSpan ZZ L) (idealDual ZZ L (Ideal.span {d}))`. The theorem `toRationalSpan_mem_idealDual_iff` gives its required membership predicate; `idealDualMap` realizes the ideal dual as a kernel, and `idealDualInclusion` retains its ambient map.
Its mathematical placement is the general inverse-image construction applied to the ideal dual.
The adjacent metric-dual and rank-one-dual theories concern the general dual and rank-one modularity.

## Private API accesses

The issue's instruction to supply public operations does not authorize exporting engine accessors.
The required operation is determined by what a consumer asks the engine to compute.

| Private access | Correct abstraction and retained data | Disposition |
| --- | --- | --- |
| `_engine_polyhedron` | Facet incidence of the original ray family | At pinned `backends/polyhedral.py:36`, use `cone.facet_covectors()` and the zero evaluations of each covector on the original vectors. `cone.facets()` retains the corresponding faces. |
| `_ExactCVPEngine` | Closest-point/closest-value problems and the shell family in row 18 | At pinned `indefinite/lorentzian_cells.py:809`, form the timelike vector's perpendicular sublattice, twist its negative form, and use its public close-vector family. The inclusion and Bezout partner supply the translation. |
| `_rational_positive_vector` | Signed locus of the restricted form, row 16 | Reuse the form restriction and witness selection; no public raw Gram-to-vector function. |
| `_engine_subgroup_from_generators` | Generated subgroup of a represented group, with inclusion and generating family | Generic group owner; `OwnedGroups.ParentMethods.subgroup` is an existing presentation route. This also meets the dependency on #396. |
| `_isometry_from_column_matrix` | A formed-module morphism, and inverse data for an isomorphism; construction in the correct Mor | Construct the owned module map from generator images, then apply `source.Isom(target)` to that map or its inverse pair. |
| `_row_action_matrix` | Coordinate realization of a linear map between selected frames, with variance/convention fixed | `Modules(R).Mor(source,target)(isometry)` is the owned based matrix when the endpoints are finite free framed modules. Framing maps give its generator coordinates. Row versus column conversion stays private to the adapter. |
| `_element_from_coordinates` | Application of a selected framing isomorphism to an element of the free coordinate module | Existing module framing/linear-combination construction; not a lattice-specific public engine converter. |

## Disposition of the code already added

The source now composes the owners described below.
Targeted issue-401 engineering specimens have since executed as authorized in `HANDOFF.md`; the remaining source obligations are not thereby discharged, and no run constitutes independent correctness acceptance.

| Added surface | Required architectural disposition |
| --- | --- |
| `content`, `primitive_part` | Module elements define the evaluation-image order ideal. Free integral module elements take its nonnegative generator as content. Framed free modules compute that ideal from finite-support coordinates. The general primitive-part operation lifts through scalar multiplication; the framed realization divides coordinates. Acceptance remains. |
| `bezout_partner` and the rational Witt edit | The pairing covector lifts its image generator through the general module-map `preimage`; infinite rank uses the finite pairing support. Module morphisms also supply the complete `solution_fibre`, its translation module and its torsor. Preimage computation retains source coefficients through Smith form; it does not identify an image basis with the original generating family. |
| `isotropic_vector` and signed witnesses | The frozen isotropic-vector name raises for an empty locus. Symmetric bilinear formed modules own `vector_of_sign`; positive and negative requests consume it and retain the submodule parent. Backend rank/ring limits remain realization limits. |
| `hyperbolic_partner` | The square-zero equalizer is constructed on the pairing covector's general affine solution fibre. Both inclusions and the quadratic constraint are retained. In finite rank, the complete obstruction is the norm residue on `K/(ZZ*v+2d*K)`, where `K` is the pairing kernel. A zero residue gives an integral partner by correction along `v`; an empty residue locus proves emptiness. |
| `integral_hyperbolic_splitting`, `two_hyperbolic_plane_splitting` | The isotropic reduction supplies `L -> U + (I^perp/I)` by its orthogonal quotient section and the shared chosen orthogonal decomposition. The two-plane operation composes two reduction splittings and the orthogonal biproduct. Acceptance remains. |
| `first_close_vector_shell`, `first_close_vector_sphere` | The port owns multiplier selection, target scaling and bound scaling; research owns fixed-multiplier fibres. Frozen public methods may dispatch to port #15. Both selections have the indexed family of signed fixed-multiplier shells as their semantic domain. Sphere selection takes the boundary. The result retains the multiplier and complete finite subset with inclusion; `None` means the bounded search is empty. Acceptance remains. |
| Restricted-scalar `subobject_on` | The fractional PID span constructs a finite free module with its subobject inclusion and integral lift, using the shared module-subobject datum. General affine inverse images are separate objects at the module owner: they retain the entire rational kernel, the parameter inclusion, the target evaluation, and the pullback. Mixed-scalar point finding solves the integral image equation in the rational cokernel, then lifts its residual. |
| `extension_across`, `integral_restriction`, `integral_isometry`, `is_integral_on` | Perpendicular extension transports the direct sum of the line map and the given perpendicular map through chosen orthogonal decompositions. Integral descent factors both directions through generic-fibre inclusions after restriction of scalars. Formed scalar extension retains its source, scalar map and unit. `integral_isometry` recovers that source model for distinct rational endpoints and raises on failed descent; an unmarked rational source requires an explicit integral model. |
| `symmetrized_right_multiplication` | Its general `solution_fibre(B)` retains all solutions and the full homogeneous translation module. `integral_members(j)` intersects it with a chosen integral parameter inclusion. The nonempty fibre's torsor composes the regular-action transport at the group-action owner. |
| Binary square fibres and representatives | Symmetric formed modules own the square equalizer and orthogonal action. The selected representative set retains that action, its quotient, inclusion, projection and section. `vectors_of_square` enumerates the full nonzero split binary fibre through SymPy; `primitive_isotropic_vectors` enumerates both primitive generators of each binary null line. `reduction_cycle` returns an owned period isometry and finite vector subset, but its current private provider copies the pinned port algorithm. Move that body to port #15 and dispatch; semantic wrapping does not transfer algorithm ownership. |
| Form twists | `FormValueScalings` constructs the scaled form on its original underlying module and normalizes scalar composition. The unit action returns the original object. `TwistFunctor` transports both arrows of an isomorphism and constructs an element of the twisted lattice isometry homset. |
| Rational reduction lifts | `rational_lifts` composes chosen rational orthogonal decompositions and the reduction isometry. The full marked-line lift locus is a torsor under the target reduction kernel. Additive parameters evaluate through Eichler transvections, with a retained inverse parameter map. `integral_members` retains the exact descent locus and integral-kernel action. `integral_parameter_quotient` bounds all possible integral parameters and retains a finite-index period of integral transvections. Its complete residue locus supplies `integral_base_point` and the selected `integral_torsor`. |
| `affine_line_points` | `affine_line_fibre` specializes the affine module inverse image and retains its evaluation and image. The image translation module is the kernel of the integral target map to the rational cokernel. Its rank-one generator supplies the primitive integral step. A constant line has zero image translations. |
| `divisible_sublattice` | The bilinear formed-module owner constructs `IdealMetricDuals` through the pairing modulo the principal ideal. Its integral pullback retains the formed inclusion and `map_to_ideal_dual`, with the commuting generic-fibre square. Modulus zero selects the correlation kernel. |
| `integral_similarity` | The module-map denominator ideal is computed relative to integral bases and scalar extension. The scaled map factors through the integral target inclusion. A formed monomorphism retains its rational isometry, denominator ideal, factor `N`, and value map with multiplier `N^2`. |
| `witt_extension` | The restriction equalizer retains the given inclusions and ambient isometry locus. Codimension-one selection checks both ambient radical intersections, then selects a complementary vector through the pairing fibre and its scalar norm equation. A complementary ambient radical vector maps to a complementary radical vector. |
| `invariant_overlattice` | The group-action owner constructs and retains the orbit-generated module, seed factorization, ambient inclusion, and induced action. A finite group gives a finite orbit family. For nondegenerate integral lattices, every integral overlattice lies in `L^sharp`, hence in `L/abs(det L)`; this bounds closure for finitely generated infinite groups. A span outside the bound, or with nonintegral pairings, cannot lie in an integral invariant overlattice. |
| Local port branch `research-401-primitives` | Preserve its commits as recovery material. Current function-level assignments govern implementation; frozen API names do not require research to implement specialized port algorithms. |

## Unresolved contract work

The source rework above is committed.
Python parsing, undefined-name checks on the affected owners, and whitespace checks were engineering checks.
Subsequent targeted Sage execution verified the integral reduction-lift parameter/inverse and full integral-kernel membership on `U+<2>`, the invariant-overlattice obstruction for `diag(2,1/2)` on U, signed witnesses and the primitive null family of U, a nonzero affine-line torsor action, the integral 2-by-2 matrix symmetrization fibre and its skew translation action, similarity factor/multiplier/index `(2,4,4)`, finite orthogonal-subgroup membership on the `U(2)` discriminant form, and the period map of a binary anisotropic form with Gram `diag(2,-4)`. Direct runtime comparison with the pinned port `709f81a` now additionally agrees exactly on the ordered cycle vectors and period automorphism for `diag(2,-6)`, `[[4,2],[2,-2]]`, and `diag(2,-4)` at bound 4. The exact checks and remaining contracts are recorded in `HANDOFF.md`. These are engineering checks, not independent correctness evidence.
The M1 prerequisites and DEV-58 govern broad verification.

The listed surfaces and finite-rank point-selection constructions have implementation bodies.
This does not certify their computational ownership: the copied cycle and first-success multiplier search require migration to the port under the assignments above.
Each is accepted by true mathematical assertions at its owner; how a consumer such as `sage-indefinite-port` calls them is not part of research's acceptance.
Infinite-rank quadratic point selection and orbit spans without a finite-generation hypothesis are outside the finite realizations stated above.

The dependency traces above cover every issue item.
The remaining subjects are:

- order ideals and normalized content, and generic image-generator fibres;

- mixed-scalar affine inverse images, their rational kernels, and integral descent/denominator ideals;

- integral isotropic reduction and hyperbolic splitting, including its comparison maps;

- two-endpoint partial-isometry extension and the degenerate-hyperplane hypotheses;

- parabolic reduction maps, marked-line data, kernel torsors, evaluation, and integral subgroups;

- orbit-generated modules with finite-generation and integrality hypotheses;

- norm-fibre actions and quotient representations, signed witness selection, and affine shell families;

- similarity embeddings with separate denominator factor and form multiplier, and normalized form-change transport;

- the divisibility sublattice as the inverse-image composite in row 20, with its formed inclusion and comparison maps;

- binary reduction cycles with their starting data, period automorph, and bounded vector family.

Research runtime and correctness acceptance are separate subsequent obligations.

## Separating mathematical specimens for the remaining execution phase

These are deductions from the displayed forms and inclusions.
Some neighboring and directly matching specimens have been executed as described above and in `HANDOFF.md`; other rows remain unexecuted.
None is an independent correctness acceptance result.

| Construction | Mathematical specimen |
| --- | --- |
| Integral partner | For `[[0,2,0],[2,2,0],[0,0,-2]]`, `e` has divisibility two and `f+a` has square zero and pairing two with `e`. For `[[0,2],[2,2]]`, every minimal-pairing candidate has square `4k+2`, so the locus is empty. |
| Affine line | For `C=2ZZ*e1+3ZZ*e2` in `ZZ^2`, the line `(1/2)e1+QQ*e1` meets C in `2ZZ*e1`. The parallel line `(1/2)e2+QQ*e1` has empty intersection. The constant line at zero has one image point and all rational parameters. |
| Divisibility | For Gram `diag(0,2)`, divisor zero gives `ZZ*e1`, divisor two gives the whole lattice, and divisor three gives `ZZ*e1+3ZZ*e2`. The two pullback maps agree after inclusion into the rational span. |
| Similarity | On U, `phi=diag(2,1/2)` has denominator ideal `(2)`. The integral map `2phi=diag(4,1)` has form multiplier four and image index four. |
| Witt extension | In `U + <2>`, the partial isometry fixing e and negating a on `e^perp` extends by fixing f. In Gram `diag(1,-1,0)`, swapping `e1+e2` and `e3` on their zero-form hyperplane is a partial isometry which cannot extend: it moves the ambient radical to a nonradical vector. |
| Invariant overlattice | On U(2), the involution `e -> 2f, f -> e/2` generates the integral overlattice `ZZ*(e/2)+ZZ*f`, isometric to U. On U the same orbit span has cross-pairing `1/2`, so no integral overlattice contains it. Powers of `diag(2,1/2)` likewise admit no invariant integral overlattice of U. |
| Integral lift torsor | On `U + <2>`, transvection parameter `t*a` sends f to `f+t*a-t^2*e` and a to `a-2t*e`. Its integral automorphisms have exactly `t in ZZ`. The period `2ZZ*a` is sufficient for finite residue selection but is a proper subgroup of the complete integral kernel `ZZ*a`. |
