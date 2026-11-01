# Engine traps

Measured facts about the engines this repository delegates to, kept because each one is the product of the work and costs an afternoon to rediscover (`CONTRIBUTING.md`: *The artifacts are instruments; the product is a map of Sage*; `DEV-63` owns this file).
A row is a finding, never a hypothesis: it records the operation, the spelling measured, the specimen and its size parameter, the wall times, the version, the command that reproduces it, and the route chosen.
A cost is a curve in the size parameter, or it is a single data point and says so.
The [native issue tree](https://github.com/dzackgarza/research/issues/46) holds unresolved needs; this file holds measured facts.

Read this file before choosing any engine route.
Write to it in the turn the measurement is made.

## Sage

### PARI overflows on groups and isometry witnesses for a line plus E8

On SageMath 11.0.beta1 with Python 3.14, the orthogonal group of the positive
definite lattice `<18> + E8` reaches PARI `qfauto` and raises a stack overflow
at its 1 GiB limit. The independent mathematical example is
`tests/lattices/test_orthogonal_group_semantic_api.sage::test_e8_with_a_norm_eighteen_line_has_the_product_orthogonal_group`.
Its expected order is twice the E8 Weyl-group order: the norm-two vectors
span the characteristic E8 summand, and the perpendicular line permits two
signs. The selected test failed in 36.99 seconds on 2026-10-26; that includes
test setup and is one data point.

The [PARI qfisominit contract](https://pari.math.u-bordeaux.fr/dochtml/html-stable/Vectors,_matrices,_linear_algebra_and_sets.html#qfisominit)
requires all vectors up to the largest diagonal entry. The norm-18 basis
vector therefore forces enumeration of long E8 shells as well.
[OSCAR 1.8.2 isometry_group](https://github.com/oscar-system/Oscar.jl/blob/v1.8.2/src/Groups/matrices/isometry_group.jl)
supplies a complete computation by decomposition into invariant sublattices.
On Julia 1.12.5 it returned the required order. Julia's timing report
attributes almost all of the first call to compilation.

| Direct OSCAR call on `<18> + E8` | Observed value |
| --- | ---: |
| Group order | 1393459200 |
| First `isometry_group` call, excluding `using Oscar` | 267.750760 s |
| Compilation share | 99.89% |

Reproduce in the bridge's Julia project with `using Oscar`,
`G = diagonal_matrix(matrix(QQ,1,1,[18]), gram_matrix(root_lattice(:E,8)))`,
`L = integer_lattice(; gram=G)`, `@time A = isometry_group(L)`, and
`order(A)`. This is a cold-call data point, not a throughput comparison.
The owned group-order and generator checks above also verify the adapter's
basis transport.

The definite witness operation has the same enumeration limit. The unchanged
port degree-18 vector-orbit and reflected-vector `r_0` consumers overflow
in `QuadraticForm.is_globally_equivalent_to`, which calls PARI `qfisom`.
The owner test
`tests/lattices/test_lattice_isometry_semantic_api.sage::test_e8_with_a_norm_eighteen_line_has_integral_change_of_basis_witnesses`
reproduces the overflow on `<18> + E8` and the unimodular shear with
`change[0,1] = 1`. Its red run took 35.82 seconds, including setup, on
2026-10-26 with the same Sage runtime and 1 GiB PARI limit.
OSCAR's `is_isometric_with_isometry` uses invariant-sublattice decomposition
in the same source file, lines 645-844. The adapter transposes its row-action
witness to the owned column-image convention. Its mathematical verification
must cover both definite signs and an empty isometry set.

### Algebraic-real `QuadraticForm.rational_diagonal_form` rejects even a diagonal plane

Measured 2026-10-23 with SageMath 11.0.beta1 and Python 3.14: `QuadraticForm(AA, matrix(AA, [[1, 0], [0, -1]])).rational_diagonal_form(return_matrix=True)` raises `TypeError: Illegal initializer for algebraic number` while assigning a diagonal matrix entry in `quadratic_form__local_field_invariants.py`. This is one rank-two data point, not a timing curve. Reproduce with `sage -python -c 'from sage.all import AA, matrix; from sage.quadratic_forms.quadratic_form import QuadraticForm; print(QuadraticForm(AA, matrix(AA, [[1,0],[0,-1]])).rational_diagonal_form(return_matrix=True))'`. Sage's documented transformation contract is `T.transpose() * G * T == D.matrix()`; the call fails before it returns that data. Route chosen: `lattice_engines._exact_real_diagonalization` uses the existing exact formed-module arithmetic for AA and retains the forward and inverse maps. Depends on this: AA lattice diagonalization, Witt decomposition and Witt index.

### The mixed-rank integral embedding route did not finish at the first Julia call

Measured 2026-10-23 on a 7.8 GiB host with Julia 1.12.5: after a fresh preamble import, `L = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])`; `L.hyperbolic_index()` entered `sage_julia_bridge` for OSCAR's `primitive_embeddings` on the rank-two source and rank-three target. No embedding decision returned after 250 seconds; the Julia process used about 95% of one CPU and reached 38% of host RAM, and this probe was terminated. A second rank-three specimen, `U + <1>`, did not return from the same decision in 90 seconds. These are lower bounds from two runs, not completed operations or a size curve. Reproduce with `SAGE_JULIA_COMMAND=/home/dzack/.julia/juliaup/julia-1.12.5+0.x64.linux.gnu/bin/julia PYTHONPATH=/home/dzack/research/src sage -python`, import the preamble and run either specimen. The juliaup launcher could not read its root-owned `juliaupself.json`, so the direct installed binary was used. Route chosen composes primitive isotropic-vector, integral hyperbolic-partner and orthogonal-splitting constructions in even and odd lattices. Discriminant-length and parity bounds exclude larger impossible ranks before classification; genuinely unresolved candidates still use `Emb.is_empty()`. The rank-three specimens, `U^2 + <2>`, `U^2 + <1>` and `U + U(2)` passed index, Gram pullback and inverse-law checks on 2026-10-23. Depends on this: integral `hyperbolic_index` and `maximal_hyperbolic_index_splitting` for mixed rank.

### Sage's `orthogonal_group()` of a finite quadratic module searches the whole module; GAP's `forms` package is absent

Measured 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`). `TorsionQuadraticForm(diagonal_matrix(QQ, [2/3]*6)).orthogonal_group()` (no generators, so `sage.groups.fqf_orthogonal._isom_fqf` on all of `T`) did not finish within 40 minutes (`timeout 2400`, exit 124; probe sage-indefinite-port `.tmp/probe/o3_6.py`); on `(Z/3)^4` it takes 3.6 s. GAP `GO(-1, 6, 3)` (order 26127360) conjugated onto the form gives generators in 0.9 s (probe `.tmp/probe/fastO.py`, which also checks equal orders with brute force on `(Z/3)^2`, `(Z/3)^4` and `A2+A2+<2>`: 8, 1152, 8). `LoadPackage("forms")` prints `#I forms package is not available`, so `BilinearFormByMatrix`/`BaseChangeToCanonical` cannot be used.
Route chosen: `torsion_form_modules._engine_orthogonal_group`.

### Sage multiplies an element of a ZZ-span in QQ^n by a matrix not through its ambient entries

Measured 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`): `V = (QQ**4).span([e_i/3], ZZ)`, `u = V([0, 1/3, 0, 2/3])`, `G` the integer Gram matrix of sage-indefinite-port centralizer case `oscar_lattices_with_isometry_110`: `u * G` is `(-51, -27, -12, -27)` while `vector(QQ, u.list()) * G` is `(-11, -6, -3, -6)`. Lifts of finite-quadratic-module elements (`x.lift()`) are such elements.
Probe: sage-indefinite-port `.tmp/probe/submul.py`. Route chosen: `hermitian_miranda_morrison._ambient` reads lifts as ambient rational vectors before any product.

### Sage's `Matrix_cyclo_dense` returns stale products after in-place row operations

Measured 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`): for `S`, `F` 3x3 over `CyclotomicField(4)`, after one product `S * F`, `S.set_row(1, S.row(1) - (zeta4/3) * S.row(0))` leaves `S * F` different from `matrix(E, 3, 3, S.list()) * F` (row 1 of the product is the old one), while `S.list()` and `S.row(1)` are updated.
The same matrix in `MatrixSpace(E, 3, 3, implementation="generic")` gives the correct product.
Probe: sage-indefinite-port `.tmp/probe/cyclo_bug2.py`. Route chosen: `hermitian_miranda_morrison` mutates only generic matrices (`copy_matrix`, `_mutable_matrix`).

### Sage's `PointConfiguration(..., projective=True)` accepts only points with last coordinate one

Measured 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`): `PointConfiguration([[1,0,1],[0,1,2]], projective=True).triangulate()` raises `NotImplementedError` from `sage/geometry/triangulation/base.pyx` `_init_points` (`raise NotImplementedError  # TODO`) unless every point's last coordinate is 1. Probe: sage-indefinite-port `.tmp/probe/tri.py`. Route chosen: `polyhedral_cones._engine_ray_triangulation` scales the rays onto `c(x) = 1` with `c` the sum of the dual cone's rays and triangulates the affine points; for the rays e1, e2, e3, e1+e2+e3 of the positive orthant it gives three triangles.

### Sage's echelonized basis of a ZZ-submodule is its Hermite normal form, equal for equal submodules

Measured 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`). In `FreeModule(ZZ, 3)`, the submodules generated by ((2,4,6), (0,3,9), (12,0,0)) and by ((2,7,15), (0,3,9), (22,20,30)) are equal, and their `echelonized_basis_matrix()` are equal, with rows (2,1,33), (0,3,9), (0,0,36). Probe: sage-indefinite-port `.tmp/probe/hnf.py`. Route chosen: `_GeneralPresentedModule._submodule_key` reads it for submodules of finitely presented modules over ZZ only.

### Sage orders the factors of a join category by creation order, so an unrelated factor can shadow a formed override

Observed 2026-10-15, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`). Contract (`sage/categories/category.py`, `Category._sort`, and `sage/misc/c3_controlled.pyx`, `_cmp_key`): a join's factors are sorted by decreasing `_cmp_key`, which is the category's flags and a counter fixed when the key is first computed, and the parent class is the C3 merge in that order; the order of two factors unrelated in the declared graph therefore follows construction history, not inheritance.
Specimen: the discriminant bilinear module of the odd lattice ((-1,-3,-1),(-3,14,8),(-1,8,11)) and the discriminant quadratic module of ((2,1),(1,-4)). Probe (sage-indefinite-port `.tmp/probe/mro3.py GRAM`, lists methods of `_SelectedFinitePresentationModules.ParentMethods` repeated by a later formed `ParentMethods` in `type(A_L).__mro__`): before, `invariant_factor_form` (FormModules.FinitelyPresented.Torsion) and `base_change` (FormModules.FinitelyPresented, FormModules) were shadowed for both specimens, and for the odd one `invariant_factor_form()` returned an isomorphism to an unformed module (`O(A_L).from_morphism` -> `_engine_module` -> `_representative_gram`: `AttributeError: ... object has no attribute 'form'`). Route chosen: the two operations live on `ModulesWithChosenFinitePresentation`, the data they consume; after the move the probe lists nothing.
The formed levels still win only by the join order ([#565](https://github.com/dzackgarza/research/issues/565)).

### Sage's `GroupOfIsometries` cannot be formed on an empty generating family

Observed 2026-10-14, SageMath 11.0.beta1 (container `sagemath/sagemath-dev:develop`), through `IntegralLattice(G).orthogonal_group()` for the rank-0 lattice that `sage-indefinite-port` reaches as the isotropic reduction `J-perp/J` of `J = span(e_1, e_2)` in `2U`: `sage/groups/matrix_gps/isometries.py:128` calls `libgap.Group(gap_gens)` with no generators and raises `GAPError: Error, usage: Group(<gen>,...), Group(<gens>), Group(<gens>,<id>)`. Route chosen: `O(0)` is the trivial group, generated by the empty family and of cardinality 1; `LatticeIsometryMor` answers it before reaching the engine.
Reproduce: `sage-indefinite-port/.tmp/probe/plane.py` before the rank-0 branch.

### Sage's `lcm` takes two arguments or one iterable, never several positional arguments

Measured 2026-10-14, SageMath 10.10.beta8 (container `sagemath/sagemath-dev:develop`). `sage.arith.functions.lcm(1, 2, 3)` raises `TypeError: lcm() takes at most 2 positional arguments (3 given)`; `lcm([1, 2, 3])` returns `6`. Specimen: `tensors/tensor.py:_engine_quotient_form_family_contractions` on the discriminant module of Gram `[[2,-1,0],[-1,-2,0],[0,0,-10]]` (OSCAR spinor-norm specimen `from_sage_0`), reached by `L.discriminant_module().isotropic_subgroups()`, called `lcm(1, *denominators)` with nine denominators.
Route chosen: pass one list.
Reproduce: `direnv exec /home/dzack/research python3 -c "from sage.arith.functions import lcm; print(lcm([1,2,3])); lcm(1,2,3)"`.

### The declared-graph subcategory decision is the hot path of an indefinite edgewalk; decide each pair once

Measured 2026-10-14 with `cProfile` (single process, first call) on `sage-indefinite-port`'s frozen `ListReflect_0` edgewalk (rank 3): `_declared_category_is_subcategory` was entered about 830,000 times, reached from Sage `Category.__contains__` and the owned join normalization (`_owned_join_as_tuple`, `_owned_sort_uniq`) across roughly 300,000 category-membership tests.
Each call reads a fixed pair of unique-representation categories in the declared graph, which does not change once built, so `@cached_function` decides each pair once.
Wall time of `HyperbolicLattices(ZZ)(L).allcock_edgewalk()` (`.tmp/probe/edge2.py` in `sage-indefinite-port`, one fresh process each, together with lazy `Hom` framing sources): rank 3 `ListReflect_0` 32.4 s before (research `704da2562a`), 24.2 s after; rank 4 `ListSimpleRootSystem_0` 47.8 s before, 39.6 s after.
Two data points: the saving is roughly constant (about 8 s) across these two sizes, not a change of growth rate.
The remaining time is spread across the categorical framework with no single dominant entry.

### Sage twists a rank-28 lattice in milliseconds; owned form scaling was reconstructing its Gram through the Mor

Measured 2026-10-12, SageMath 10.10.beta8, one process and one first call per entry, excluding startup.
The specimens are the *stored Gram matrices* of lattice-db `3ICT` (rank 23, odd unimodular), `3ICU` (rank 22, discriminant 3), and `3ICV` (rank 28, even unimodular).
Construct Sage's `IntegralLattice(G)` directly, then call `.twist(2)`; construct the preamble's `Lattices(ZZ)(rows)` on those same rows, then call `.twist(2)` on the preamble object.
The former measures the engine, the latter the owned constructor.
These are individual data points, not an inferred asymptotic curve.

| card, rank | Sage `IntegralLattice(G).twist(2)` | owned before repair | owned after repair |
| --- | ---: | ---: | ---: |
| `3ICT`, 23 | 0.00747 s | 16.2713 s | 0.0280 s |
| `3ICU`, 22 | 0.00335 s | 6.7617 s after reusing the source form, before retaining its Gram | 0.0253 s |
| `3ICV`, 28 | 0.00461 s | 17.5700 s after reusing the source form, before retaining its Gram | 0.0383 s |

Source tracing identified **two** redundant object constructions.
`_scaled_form_module` in `categories/modules/framed/formed/form_modules.py` first used `source._formed_form()`, rebuilding the form on the already formed source object instead of reading the original selected form `source.form()` and reusing its actual Hom parent.
Then `forms(scalar * form.gram_tensor())` received the complete scaled tensor but discarded that knowledge: `scaled.gram_tensor()` derived it again by evaluating pairs through the Mor.
On rank 23, a timed first call to `scaled.gram_tensor().is_symmetric()` cost 8.1743 s; an immediate subsequent `_form_module(scaled, ...)` took 0.0062 s. Thus **recovering the Gram**, not the intrinsic symmetry equality, incurred almost all of that first-call cost.
This was preamble overhead, not Sage's twisting algorithm.

The scalar-change route reads `source.form()` and uses its existing `form.parent()` as the Hom.
A later construction-level audit found the underlying cause that the earlier cache workaround did not eliminate: `TensorProductModuleMor._element_constructor_` converted the **supplied finite covariant tensor** into rows, then a generator-image closure, but did not retain the tensor; `BilinearFormMors.gram_tensor` reconstructed it by evaluating all generator pairs.
The repaired generic Hom constructor retains the actual supplied tensor as the one selected generator-image datum, and the Gram accessor returns that identical tensor.
Rectangular W-valued finite pair coordinates are similarly retained as an indexed family; the generator-image map reads the same datum.
`_form_of_gram` now constructs `forms(gram)` directly and scalar change constructs `forms(scaled_gram)` without setting a redundant Gram cache.
Scalar change transports symmetry, finite generation, and unit-scalar unimodularity through the relevant category inclusions; parity of a scaled lattice is determined from the already selected diagonal.
No category check reconstructs the Hom or re-evaluates all generator pairs.

The mathematical point also applies to integrality.
On a finite chosen generating family, `b` is constructed from its tensor of values `b(m_i,m_j)`; testing `b(M,M) ⊆ R` is exactly testing those tensor values for membership in `R`. Before fixing `PairingObjects.is_base_ring_valued`, lattice-db `derive` spent **6.675 s** testing the rank-28 `3ICV` Gram through 784 bilinear evaluations, with rank-23 `3ICT` at **4.064 s** and rank-22 `3ICU` at **2.854 s** (single measurements).
With the generic form owner reading `form.gram_tensor()` directly, the *same* check completed in **0.0357 s** (`3ICV`), **0.0242 s** (`3ICT`), and **0.0222 s** (`3ICU`) in one fresh preamble process; a rational Gram with an entry `1/2` is still rejected as nonintegral.
The lattice-db consumer can therefore retain its original public `formed.is_base_ring_valued()` request instead of attempting construction as a substitute for the property.

An infinite-rank separating specimen revealed that `scaled.gram_tensor()` cannot reconstruct a pairing rule from infinitely many basis pairs, and the owned ring-element **left** product `scalar * source.gram_tensor()` attempted to construct the zero element of an infinite coordinate-tensor module (which has no component-array realization).
Scaling through the tensor's **right** product, `source.gram_tensor() * scalar`, calls the pairing-rule tensor's already implemented `scaled_by` construction and also works on finite tensors.
On the countable-rank diagonal lattice `Lattices(ZZ)(ZZ**NN)`, the repaired `twist(2)` ran in 0.0107 s in one fresh process, retained the original underlying module, and evaluated norms 2 and 6 after successive twists.
The generic `FreeFormModules.is_unimodular()` instead tried to construct an infinite correlation cokernel; the lattice specialization now calls the previously existing `_gram_is_unimodular` criterion, which correctly returns `False` for this infinite free diagonal lattice.
This leaves general formed-module unimodularity to its own owner and does not attempt to enumerate an infinite basis.

The same investigation found `FreeFormModules.is_unimodular()` computing the full algebraic correlation and testing its injectivity/surjectivity instead of using the finite-free determinant criterion.
On the rank-28 even unimodular orthogonal sum `2U+3E_8(-1)`, the old `L.twist(2).is_unimodular()` cost 10.6852 s; reading the Gram determinant in the existing matrix owner gives `False` in 0.0233 s. This route applies to a finite free scalar-valued form over a commutative ring, where the correlation is an isomorphism exactly when its determinant is a unit.
It is not applied to arbitrary unframed or non-scalar-valued forms.

Reproduce native timings with `direnv exec /home/dzack/research python3`, `sage.modules.free_quadratic_module_integer_symmetric.IntegralLattice`, and `sage.all.matrix(ZZ, frontmatter.load('/home/dzack/gitclones/lattice-database/lattices/3ICT.md').metadata['gram_tensor'])`. Reproduce owned timings by passing the `gram_tensor` **rows**, not a raw Sage matrix, to `sage_extensions.categories.lattices.Lattices(ZZ)`, timing `L.twist(2)` with `time.perf_counter`. Do not time `L.twist(2).level()` as one operation: after the repair the twist takes milliseconds and the level itself is a separate exact matrix computation.

Depends on this: all lattice twists, formed-module value scalings, lattice levels of twists, signatures, Gram-based categorizations, and repeated form constructions throughout the preamble.

### A rank-28 unimodular discriminant group takes 0.05 s in Sage; the former owned presentation expanded a zero divided square

Observed 2026-10-12, SageMath 10.10.beta8, on the actual Gram matrix of lattice-db card `029K`, `II_{2,26}=2U+3E_8(-1)`. `IntegralLattice(G).discriminant_group()` uses `TorsionQuadraticModule(self.dual_lattice(), self)` (`sage/modules/free_quadratic_module_integer_symmetric.py`, `discriminant_group`), and computes the *trivial* discriminant group directly.
It does not spend minutes constructing the discriminant module.

| lattice (Gram data from `029K`) | rank | Sage `IntegralLattice(G).discriminant_group()` | invariant factors |
| --- | ---: | ---: | --- |
| first hyperbolic block `U` | 2 | 0.0579 s | `()` |
| one `E_8(-1)` block | 8 | 0.0210 s | `()` |
| full `029K` | 28 | 0.0477 s | `()` |

One invocation and one timing per size, excluding Sage startup and lattice construction.
Earlier owned-first-call probes on this rank-28 lattice had reported `is_p_elementary(2)` at 88.28 s (`029K`) and 91.30 s (`3ICV`), and `discriminant_module()` at 243.3 s (`029K`, separate run); the latter figure was supplied by the interrupted probe, not reproduced in this investigation.
After the first call, the cached `discriminant_module()` made repeated `is_p_elementary(2)` instantaneous.

The preamble's `L.discriminant_module()` instead constructs the *selected* cokernel `coker(L -> L^#)` and forms it over `Q/2Z`. The original quadratic-form classifier expands `Gamma^2(A_L)` using the 28 selected generators and relations even when `A_L=0`. Profiling rank 8 gave 3.70 s cumulative in `module.divided_square()` out of 5.94 s under cProfile.
Avoiding this zero-module expansion, while retaining the selected 28-generator cokernel, reduced the rank-28 discriminant construction to 10.758 s. The residual 9.276 s was in `correlation_morphism().cokernel()`: its lazy generator map evaluated all 784 pairings separately, each rebuilding the Gram's engine matrix in `tensor.contract` (rank-12 cProfile: 144 pairings, 0.93 s out of 1.53 s cokernel time).

The selected route now forms `Gamma^2(0)=0`, uses the zero quadratic form on a zero quotient, and constructs the finite-rank correlation morphism by *currying the Gram tensor once*, through the tensor owner's `curry_bilinear` and the existing `Mor.from_rows`. On `029K` in one fresh preamble process: correlation construction 0.331 s, subsequent `discriminant_module()` 0.834 s, total 1.165 s (one run, excluding preamble startup and lattice construction).
This preserves the literal selected cokernel, 28 named quotient generators, the form and the correlation/projection maps.
It does **not** replace the owned discriminant module with Sage's normalized finite quadratic module: Sage's normalized presentation does not retain the selected cokernel data.

Reproduce native measurements with `direnv exec /home/dzack/research python3` in `/home/dzack/research`, reading the `gram_tensor:` rows of `/home/dzack/gitclones/lattice-database/lattices/029K.md` using `ast.literal_eval`, making `sage.all.matrix(ZZ, rows)` and `sage.modules.free_quadratic_module_integer_symmetric.IntegralLattice(G)`, then timing `discriminant_group()`. Reproduce the owned measurements in a separate process on the same **nested list** rows (`Lattices(ZZ)(rows)`, since Sage matrices have tensor type `(1,1)`), timing `L.correlation_morphism()` and `L.discriminant_module()` with `time.perf_counter()`. The rank-28 row is deliberately one data point per route, not an inferred asymptotic cost curve.

Depends on this: discriminant modules and forms, `L.is_p_elementary(p)`, and through them lattice-db `delta` and other discriminant-dependent certifications.
The separate missing-`delta()` category-join regression is recorded in [#573](https://github.com/dzackgarza/research/issues/573).

### Lazy Taylor series do not implement `is_field()`

On SageMath 10.10.beta10, the lazy Taylor series parent used for `QQ[[t]]` raises `NotImplementedError` from `is_field()` rather than returning a Boolean.
This is a single capability probe with no size parameter.
Reproduce with the repository's selected full Sage driver:

```bash
/home/dzack/gitclones/sage-dev-allopts/sage -python -c \
  "from sage.all import QQ; from sage.rings.lazy_series_ring import LazyPowerSeriesRing; print(LazyPowerSeriesRing(QQ, 't').is_field())"
```

Route chosen: the private ring-classification boundary treats this as an unrepresented field decision and retains only category facts the engine does establish.
Depends on this: owned formal power-series/adically-complete ring construction.

### Importing `sage.all` costs about a second; one module costs a tenth of that

Per-invocation tooling that needs one Sage module pays for the whole library when it imports `sage.all`, and almost nothing when it imports the module.
Single data points, not a curve: there is no size parameter.

| import | wall time, three runs |
| --- | --- |
| bare interpreter (`python -c pass`) | 0.74 s, 0.44 s, 0.46 s |
| `import sage.all` | 1.59 s, 1.11 s, 1.02 s |
| `from sage.graphs.graph import Graph` | 0.58 s, 0.53 s, 0.72 s |
| `from sage.topology.simplicial_complex import SimplicialComplex` | 0.48 s, 0.53 s, 0.50 s |
| `import sage.all`, then `Graph` | 1.34 s, 1.21 s, 1.22 s |
| `sage -c pass` (the launcher) | 1.02 s, 1.04 s, 0.93 s |

Sage 10.10.beta8, Python 3.14.7, the `.envrc` interpreter `/home/dzack/gitclones/sage-dev-allopts/.venv/bin/python`, 2026-09-16. The first run of a set is slower; the steady value is the last two.
Reproduce with:

```bash
PY=/home/dzack/gitclones/sage-dev-allopts/.venv/bin/python
for i in 1 2 3; do /usr/bin/time -f '%e s' $PY -c 'from sage.graphs.graph import Graph'; done
```

Route chosen: a tool that runs once per invocation imports the module it computes with, never `sage.all`. Spawning one Sage process per item is a design defect at either import.
Depends on this: the `category-graph` recipes (TODO node `category-graph-engine`).

The `sage` on `PATH` is a symlink to `sage-dev-allopts/.venv/bin/sage`, a Python script that accepts `-c` and rejects `-python`; time module imports with the venv's `python` directly.

Importing `sage.topology.simplicial_complex` without `sage.all` prints `UserWarning: Resolving lazy import ... during startup` three times on first use.
The results are unaffected; loading `sage.all` first silences it and costs the second above.

### `Graph.minimum_cycle_basis()` takes integer vertices only, and costs seconds on a few hundred vertices

The default route is `sage.graphs.base.boost_graph.min_cycle_basis`. On string vertices it raises `TypeError: an integer is required` (the edge set is a `pair<int,int>`); relabel first with `relabel(return_map=True)` and map back.
Each returned cycle is a vertex set, not in cyclic order (its own docstring); order it with `subgraph(cycle).cycle_basis()`.

Wall time on the declared category graph, 312 vertices, 397 edges, 88 independent cycles, one 2-connected block of 135 vertices holding 86 of them:

| call | wall time |
| --- | --- |
| `minimum_cycle_basis()` default, whole graph | 30.3 s |
| `minimum_cycle_basis(algorithm='NetworkX')`, whole graph | 8.2 s |
| `minimum_cycle_basis()` default, block by block | 6.6 s |
| `minimum_cycle_basis(algorithm='NetworkX')`, block by block | 1.8 s |
| `cycle_basis()` (spanning tree, not minimum) | milliseconds |
| `blocks_and_cut_vertices()`, `transitive_reduction()`, `level_sets()` | milliseconds |
| `SimplicialComplex(edges).homology(reduced=False)` default `'pari'` / `'dhsw'` | 0.19 s / 0.02 s |

Single graph, one run each, Sage 10.10.beta8, 2026-09-16; the shape of the cost in the vertex count is not measured.
Reproduce with `just category-graph cells` (whole run about 9 s) and the calls above on `_graph(_declared_edges(...))` from `dzack_research.utilities.category_graph`.

Route chosen: the cycle space is the direct sum over 2-connected blocks, so the `cells` view computes the default basis per block and reports the blocks; a large block is the audit finding, not an obstacle.
The per-block cost is paid once per run.

### An axiom applies to every declared supercategory, so a base-restriction edge asserts descent of every property

`CategoryWithAxiom.super_categories` (sage/categories/category_with_axiom.py, `def super_categories`, Sage 10.10.beta8) returns the join of the base category, `category._with_axiom_as_tuple(axiom)` for every supercategory of the base, and `extra_super_categories()`. `_with_axiom_as_tuple` (category.py) applies the axiom to any category whose class hierarchy defines it, and `Modules(ZZ)` defines the same axioms as `Modules(QQ)`. Consequence, read from source on 2026-09-16 and not executed: if `Modules(QQ)` declared `Modules(ZZ)` (restriction of scalars), then `Modules(QQ).FinitelyGenerated()` would have `Modules(ZZ).FinitelyGenerated()` as a supercategory, which is false; the same for every property stated relative to the base (finite type, smooth, projective, free of finite rank).
Absolute properties (commutative, associative, finite) descend truly, but the mechanism cannot tell the two apart.

Route chosen: no owned category declares itself over a lower base.
Restriction of scalars is a functor obtained from the category, and a preservation theorem on that functor states which properties descend.
Depends on this: the `Modules`, `Algebras` and `Schemes` bases (AGENTS.md, *Red flags*).

### A Python subclass of a category class loses its axiom classes

A nested axiom class such as `MagmaticAlgebras.Unital` is bound to its base class by `CategoryWithAxiom.__classget__` (sage/categories/category_with_axiom.py, `def __classget__`, Sage 10.10.beta8): it asserts that `_base_category_class_and_axiom[0]` is the class the attribute is read from.
`Category._with_axiom_as_tuple` (category.py) reads the axiom with `getattr(self.__class__, axiom)`, so a category whose class is a Python subclass of the base class raises on every axiom.
Reproduction, 2026-10-07, no preamble in the process:

```bash
/home/dzack/gitclones/sage-dev-allopts/.venv/bin/python3 -c "
from sage.all import QQ
from sage.categories.magmatic_algebras import MagmaticAlgebras
class MagmaticAlgebrasSubclass(MagmaticAlgebras):
    pass
print(MagmaticAlgebras(QQ).Unital())
print(MagmaticAlgebrasSubclass(QQ).Unital())
"
```

The first line prints `Category of unital algebras over Rational Field`; the second raises `AssertionError: base category class for <class 'sage.categories.unital_algebras.UnitalAlgebras'> mismatch; expected <class 'sage.categories.magmatic_algebras.MagmaticAlgebras'>, got <class '__main__.MagmaticAlgebrasSubclass'>`. The preamble meets it at `ModulesOverGroupAlgebra(Modules)` (`modules/group_modules/group_modules.py`): `Modules(ZZ[C2]).Free()` raises the same assertion for `Modules.Free`.

Consequence: a category class whose objects use Sage's axiom classes cannot be refined by a Python subclass.
Route chosen: none yet; the owner rules (`TODO.md`, `modules-over-a-group-algebra-keep-the-module-axioms`).

### An axiom that no class on the path implements returns the category itself

`Category._with_axiom_as_tuple` (sage/categories/category.py, Sage 10.10.beta8) returns `(self,)` when `getattr(self.__class__, axiom)` is `None`. When the attribute exists but the base class does not hold it in its own `__dict__`, it returns `self` joined with the same axiom applied to each supercategory.
A `SubcategoryMethods.Commutative` that calls `self._with_axiom("Commutative")` satisfies the first test, because the dynamic class inherits that method.
So if no category on the path declares a nested `Commutative(CategoryWithAxiom)`, `C.Commutative()` is `C`, and nothing warns.

Observed 2026-10-07 in a preamble session: `Magmas().Commutative() is Magmas()` was `True`. `Magmas.ParentMethods.is_commutative` answers `True` on membership in `Magmas().Commutative()`, so every owned magma that does not override `is_commutative` answered `True`. This was observed on `T(QQ^2)`. For `End(QQ^2)` and `S_3` it follows from the same membership test and was not run.
`_algebra_from_native_ring` then placed the tensor algebra in the commutative algebras on that answer.

Consequence: a category that introduces a law must declare the nested axiom class for every axiom its `SubcategoryMethods` names.
Route chosen: `Magmas.Commutative(CategoryWithAxiom)` and `AdditiveMagmas.AdditiveCommutative(CategoryWithAxiom)` in `categories/group/magmas.py`. Sage joins each into every category with its axiom whose path reaches the base.
A 2026-10-07 probe over the 204 owned categories that construct with no parameter or with `ZZ`, `QQ` or `Groups.C(2)` found no other accessor that returns its own category for an axiom outside `axioms()`, except the group shorthands `FinitelyGenerated` and `FinitelyPresented`, which name `FinitelyGeneratedAsMagma` and `FinitelyPresentedAsGroup`.

### Conjugacy in a free group: `FreeGroup` elements have `is_conjugate`, `IndexedFreeGroup` elements do not

An element of a finite-rank `FreeGroup` inherits `ElementLibGAP.is_conjugate` (`sage/groups/libgap_wrapper.pyx`, line 747), which is GAP's `IsConjugate`. On a free group GAP dispatches it to the FGA package method "RepresentativeActionOp for conjugation of elements in a free group" (`/usr/share/gap/pkg/fga/lib/ReprAct.gi`, line 14, FGA 1.5.0), which compares cyclically reduced words.
An `IndexedFreeGroup` element has no `is_conjugate` and no GAP model.

Measured on SageMath 10.10.beta8, 2026-10-07, Sage alone, in `FreeGroup(2)`: `w = (a b a^-1 b^2)^(n/5)` against `v = g w g^-1` with `g = (b a^2)^(n/3)` (conjugate), and against `w a` (not conjugate).

| length of `w` | length of `v` | `w.is_conjugate(v)` | `w.is_conjugate(w*a)` |
| --- | --- | --- | --- |
| 10 | 28 | 0.79 ms (first call) | 0.06 ms |
| 100 | 298 | 0.03 ms | 0.02 ms |
| 1000 | 2998 | 0.10 ms | 0.02 ms |
| 10000 | 29998 | 0.91 ms | 0.05 ms |

The cost grows about linearly in the word length.
Reproduce: in Sage, `F = FreeGroup(2); a, b = F.gens(); w = (a*b*a^-1*b^2)^200; g = (b*a^2)^333; timeit('w.is_conjugate(g*w*~g)')`.

Route chosen: `_free_group_conjugacy` in `categories/group/groups.py` reads both reduced words, renames the finitely many letters they use to the generators of a finite-rank `FreeGroup`, and asks `is_conjugate` there.
The retraction of `F(S)` onto the free group on those letters makes the answer the same in `F(S)`, so the route serves `IndexedFreeGroup` and an infinite basis.
Depends on this: `GroupsWithChosenFreeBasis._conjugacy_decision`, hence `conjugation_g_set().in_same_orbit` and conjugacy classes of free groups.

### `DiGraph.longest_path()` is a MILP by default; a DAG's longest chain is `level_sets()`

`longest_path(algorithm='MILP')` is the default and `'heuristic'` the only alternative (its docstring).
For an acyclic digraph, `level_sets()` puts a vertex in level `k` exactly when its longest path from a source has `k` edges, in `O(n + m)` (its docstring and body).
The longest chain is `len(level_sets()) - 1`, and the longest chain *from* each vertex to a sink is its level in `reverse().level_sets()`. Verified on a seven-vertex DAG with a shortcut edge; used by the `shape` view.

### `==` between symbolic variables is a proof attempt, and costs a coercion search

`SR.var("e_0") == SR.var("e_1")` is a symbolic equation, not a boolean.
Asking its truth (`bool`, `any`, `in` over a list of symbols) makes Sage try to prove it, and one route evaluates the difference at random points of `ComplexIntervalField` (`complex_interval_field.py`, `random_element`). A membership test that scanned a list of symbolic labels with `==` made each Gram entry of a lattice cost milliseconds and the star import take 460 s on 2026-09-23 (rank 4: 0.44 s, rank 8: 3.3 s per lattice, cubic).

Route chosen: decide membership of hashable points by hashing (`sage.sets.set.Set`, a `frozenset`), never by comparing a candidate with every point.
Symbols hash consistently with identity of name.

Measured again on SageMath 10.10.beta8, 2026-10-07, Sage alone, over all `n^2` ordered pairs of `n` distinct `SR.var`s (host load average about 7; the `n = 2` row includes first-call warm-up):

| n | `bool(a == b)` per pair | `a.is_trivially_equal(b)` per pair | `a is b` per pair |
| --- | --- | --- | --- |
| 2 | 21.6 ms | 7.3 µs | 1.7 µs |
| 4 | 1.41 ms | 3.3 µs | 0.44 µs |
| 8 | 1.76 ms | 1.6 µs | 0.16 µs |
| 16 | 1.29 ms | 1.5 µs | 0.14 µs |

The cost per pair does not fall with `n`, so a scan that identifies `k` points pairwise costs on the order of `k^2` ms. The scan still stands in `FiniteOrderedSets._on_points` (`point is present or point == present`), which every `support()` of a framed-free element reaches through `finite_subsets()`. On a catalogue lattice, whose basis labels are `SR` symbols, one `L.b(x, y)` with full-support `x`, `y` on `E_8` cost 0.24 s; deleting a second identical scan in `Subsets._from_finite_members` took it to 0.07 s. Reproduce: `/home/dzack/gitclones/sage-dev-allopts/sage -python -c "from sage.all import SR; import timeit; a, b = SR.var('e_0'), SR.var('e_1'); print(timeit.timeit(lambda: bool(a == b), number=100) / 100)"`.

### pytest-timeout's `SIGALRM` inside Cython code stops the whole run

With `--timeout-method=signal`, the alarm that pytest-timeout raises can land inside a Sage `sig_on()` block.
cysignals then raises `cysignals.signals.AlarmInterrupt`, which pytest treats as an interrupt: the run stops with "!!! cysignals.signals.AlarmInterrupt !!!" and the remaining tests never execute.
Observed on the 2026-09-23 triage run with `--timeout=1`, at 84% of 16,311 tests.
With the default per-test timeout (`func_only` false) the alarm can also fire while pytest builds a failure report, and pytest aborts with `INTERNALERROR ... Failed: Timeout`; `-o timeout_func_only=true` confines the alarm to the test function.

Route chosen: a triage catalogue run resumes after the interrupted file; the gated default run treats any test at its time limit as a failed run anyway.

### `Localization.is_unit` answers True for any nonzero element of a number-field order

`Localization(O, S).is_unit` returns `_cut_off_extra_units_from_base_ring_element(numerator).is_unit()`, whose first test is `x.numerator().is_unit()` (`sage/rings/localization.py` 448, 872). For an element of a number-field order, `numerator()` is an element of the field, where every nonzero element is a unit, so the localization reports every nonzero numerator a unit.
Specimen, Sage alone (no preamble): `QuadraticField(-1, "a").maximal_order().localization((2,))(3).is_unit()` is `True`, although 3 is prime in `Z[i]` and `S = {2^k}`; `ZZ.localization((2,))(3)` answers `False` correctly.
Sage 10.10.beta8, 2026-09-25.

Route chosen: a localization of a number-field order decides units from the definition in the source ring -- `a/s` is a unit exactly when saturating `(a)` by the inverted elements gives the unit ideal (`LocalizationRings.ElementMethods.is_unit`). Other sources keep the engine's decision, which is exact when numerators lie in the source ring; the owned ideal machinery cannot yet saturate in every such ring (`Z[1/2][x]`).

### Sage's default conversion into a parent needs the source in Sage's categories

`SR(x)` for an element of a parent whose category is not one of Sage's own (the owned `ZZ`) fails with `ValueError: Integer Ring is not in Category of sets with partial maps`. `Parent._internal_convert_map_from` finds no registered map and falls back to `_generic_convert_map`. That builds `DefaultConvertMap_unique(S, self)`, whose homset is `S.Hom(self, category=self.category()._meet_(S.category()))`. The meet of the symbolic ring's category and an owned category is Sage's `SetsWithPartialMaps`, and `Hom` asserts that both endpoints lie in it (`sage/structure/parent.pyx` 1963, `sage/categories/homset.py` 449). The coercion model's `bin_op` does not reach the element's `_symbolic_`, so `1/2 + pi` and `binomial(5, 2)` fail the same way.
Observed with Sage 10.9 (`sage-dev-allopts`) on 2026-09-23.

Sage's `ZZ` and `QQ` fail the same way on an owned element: `SageZZ(n)`, `SageQQ(n)`, `CartanType(["A", n])` raise, and `n in SageZZ` is False, for the session literal `n`. Sage's `ZZ` alone has a way around the default map: its `_convert_method_name` is `_integer_`, so it converts any element whose class has an `_integer_` method (`parent.pyx` 1958, `convert_method_map`). `QQ._convert_method_name` is `None`. Observed 2026-09-25.

Route chosen: owned numbers never enter `SR`, and owned code lowers a session value to the engine itself before calling Sage (`_engine_element`), never relying on Sage to convert it.
The preamble owns `pi`, `e` and the elementary functions over its exact real field (`rings/real.py`), and the owned rings declare their coercions among themselves (`_coerce_map_from_`).

A related fact: under the `sage` command a script runs in `sage.all`'s own namespace (`globals() is vars(sage.all)`), so a star import rebinds the attributes of `sage.all`. Owned code that falls back to a Sage function takes it from its defining module (`sage.functions.trig`, `sage.misc.functional`), never through `sage.all`.

### A class-body alias of a `cached_method` discards the original's cache

`h = g` for a `@cached_method g` does not share `g`'s cache.
Reached through `h`, `CachedMethod.__get__` looks for an existing caller only in `inst._cached_methods`, builds a fresh caller with an empty cache, and stores it under the function's own name with `setattr(inst, "g", caller)` (`sage/misc/cachefunc.pyx`, `CachedMethod.__get__`). So `x.h()` replaces the cache of `x.g()`, and a later `x.g()` recomputes and returns a different object.
Reproducer, Sage 10.9 (`sage-dev-allopts`), 2026-09-24:

```python
class P(Parent):
    @cached_method
    def g(self): return object()
    h = g
p = P(); a = p.g(); p.h(); p.g() is a   # False
```

Observed as `ToricSchemes.weil_divisor_group = torus_invariant_divisor_group`: a divisor built in `Div_T(X)` stopped belonging to `Div_T(X)` after the alias was called.
Route chosen: an alias of a cached method is a method that calls it.

### `krull_dimension` is missing on generic quotients of multivariate polynomial rings

`R.quotient(I)` for `R = PolynomialRing(QQ, ['x','y'])` is a `QuotientRing_generic` whose `krull_dimension` is the `CommutativeRings` category default, which raises `NotImplementedError` (`sage/categories/commutative_rings.py`). There `I.dimension()` (Singular) gives the answer.
Every other engine measured has its own method: `Zmod(6)` and `ZZ.quotient(2)` give 0 (`IntegerModRing_generic`), `ZZ['x'].quotient(x^2+1)` gives 1 (`PolynomialQuotientRing_generic`), and `QQ['x']`, `ZZ` and `ZZ.localization(2)` give 1. `Zmod(n)` is itself a `QuotientRing_generic`, over `ZZ`, whose ideals have no `dimension`, so a dispatch on `QuotientRing_generic` alone sends it to the wrong route.
Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: the defining-ideal route applies only when the cover ring is an `MPolynomialRing_base`.

### `is_maximal` raises on multivariate polynomial ideals, and univariate ideals have no `dimension`

Over `S = PolynomialRing(QQ, ['x','y'])`, `S.ideal(x, y).is_maximal()` and `S.ideal(x).is_maximal()` raise `NotImplementedError`, as does `ZZ['x'].ideal(2, x).is_maximal()`. `MPolynomialIdeal.dimension()` answers (`S.ideal(x).dimension() == 1`). Over `QQ['x']` the opposite holds: `Ideal_1poly_field` has no `dimension`, and `is_maximal()` answers (`(x^2+1)` gives `True`). Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: multivariate ideals over a field use Zariski's lemma, prime with quotient of dimension zero; every other ideal asks Sage's `is_maximal`.

### `QuotientRing_generic` has no `is_finite`, and its `characteristic` raises

Over `S = PolynomialRing(QQ, ['t','u'])`, `Q = S.quotient(t*u - 1)` is a `QuotientRing_generic` with no `is_finite` attribute, and `Q.characteristic()` raises `NotImplementedError` (`sage/rings/quotient_ring.py:777`). The same holds over `GF(3)`. `PolynomialQuotientRing_generic` (one variable) has `is_finite`. Measured on SageMath 10.10.beta8 (`sage-dev-allopts`), 2026-10-16. Route chosen: for `k[x_1..x_n]/I` over a field, the unit ideal (`I.dimension() == -1`) gives the zero ring; otherwise the ring is finite exactly when `k` is finite and `I.dimension() == 0`.

### Sage's localizations of polynomial rings decide units on only one shape

`L(e).is_unit()` measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25, for `e` in `x, 2, 3, x+1, 2x`:

| engine | nonconstant `e` | constants |
| --- | --- | --- |
| `ZZ['x'].localization((2, x))` | `TypeError: cannot convert nonconstant polynomial` | correct |
| `ZZ['x'].localization(2).localization(x)` | same `TypeError` | correct |
| `PolynomialRing(ZZ, 'x,y').localization((2, x))`, nested or flat | same `TypeError` | correct |
| `ZZ.localization(2)['x'].localization(x)` | correct (`x`, `2x` units; `x+1` not) | correct |
| `PolynomialRing(ZZ.localization(2), 'x,y').localization(x)` | `NotImplementedError` | `NotImplementedError` |

So a localization that inverts a constant in a polynomial ring over `ZZ` cannot decide units of nonconstant elements, and only the univariate ring over Sage's own `ZZ.localization(2)` answers.
Route chosen: a univariate polynomial algebra over a localized base keeps that engine; flattening is used only in several variables, where no engine answers and the gap is still open.

### `x in RealBallField(p)` is not "the field can enclose x"

`pi^2 in RealBallField(64)` and `sqrt(2) in RealBallField(64)` are both `False`, while `RealBallField(64)(pi^2)` returns `[9.8696... +/- 3.20e-18]`. Conversion succeeds for every closed real symbolic expression measured (`pi^2`, `sqrt(2)`, `e + log(3)`, `sin(1)`, `3/7`) and raises `TypeError` for `x + 1`, `I` and `I*pi`. `expression.variables() == ()` together with `expression.is_real()` separates the two.
`pi^2 in AA` is `False` and `sqrt(2) in AA` is `True`, so `AA` membership does test algebraicity.
Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: the ball-sign certificate is attempted on closed real expressions.

### `FreeAlgebra.__contains__` rejects constants

`ZZ(2) in FreeAlgebra(QQ, 2, 'x,y')` and `QQ(2) in FreeAlgebra(QQ, 2, 'x,y')` are `False`, and so is `ZZ(2) in FreeAlgebra(ZZ, 2, 'x,y')`, although the coercion exists and `F(2)` is twice the unit.
`ZZ(2) in QQ['x,y']` is `True`. Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: an owned ring decides membership of another owned ring's element by the canonical map first, then by the engine's `in`.

### Over `ZZ`, Sage's multivariate ideals decide neither primality nor maximality, and have no `syzygy_module`

For `R = PolynomialRing(ZZ, ['x','y'])`, `R.ideal(...).is_prime()` and `is_maximal()` raise `NotImplementedError`, and `syzygy_module()` raises `ValueError: Coefficient ring must be a field`. Singular answers all three over `ZZ`: `minAssZ` from `primdecint.lib` gives the minimal primes (`(6, x, y)` gives `(2, x, y)` and `(3, x, y)`; `(2, x^2+1, y)` gives `(2, x+1, y)`), `syz` gives the syzygies (`(2, x, y)` gives `(y, 0, -2)`, `(x, -2, 0)`, `(0, -y, x)`), and a Groebner basis over `ZZ` exposes `I cap ZZ` as its constant.
Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: primality by `minAssZ`, maximality by `I cap ZZ = (p)` and Zariski's lemma in `F_p[x_1, ..., x_n]`, syzygies by Singular `syz`.

### Over `AA`, multivariate ideals have no primality test

`PolynomialRing(AA, ['x','y']).ideal(x, y).is_prime()` raises `TypeError: cannot call Singular function 'primdecSY'`: Singular has no algebraic-real coefficients, and Sage has no other primary decomposition over `AA`. Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: whether such a quotient is a field is left undecided (`Unknown`), so it is not placed in fields.
Over `Zmod(n)` the question reduces to `ZZ`, because `(Z/n)[x]/I = Z[x]/(n, I)`.

### `Qp(p).quotient(I)` invents an invalid generator name

`Qp(3, 20).quotient(Qp(3, 20).ideal(3))` raises `ValueError: variable name '3bar' does not start with a letter`: Sage names the quotient's generator after the field's generator, which is `3`. With `names=('u',)` it returns the zero ring.
Measured on Sage 10.9 (`sage-dev-allopts`), 2026-09-25. Route chosen: a field engine's quotient is built with an explicit private name.

### `IntegralLattice(G).orthogonal_group().order()` recomputes in GAP the order that PARI already returned

For a definite lattice, `IntegralLattice.orthogonal_group()` takes its generators from PARI's `qfauto` (through `QuadraticForm.automorphism_group()`), which returns `|O(L)|` with them, and discards the order.
`.order()` then asks GAP for `Size` of the matrix group, which GAP computes from the generators by an orbit algorithm.
`QuadraticForm(ZZ, 2*G).number_of_automorphisms()` reads the PARI order.
Best of three runs, except the GAP order and the group construction (one run each, since both are cached), SageMath 10.10.beta8, 2026-10-07, `G = CartanMatrix(['E', n]).change_ring(ZZ)`:

| n | `pari(G).qfauto()` | `number_of_automorphisms()` | `orthogonal_group()` | `.gens()` | `.order()` from GAP | `.order()` after `gap().SetSize(...)` | order of O(L) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 1.26 ms | 1.44 ms | 489 ms (first call, includes warm-up) | 24.8 ms | 771 ms | 0.008 ms | 103680 |
| 7 | 1.06 ms | 2.03 ms | 47.6 ms | 24.5 ms | 1760 ms | 0.008 ms | 2903040 |
| 8 | 2.58 ms | 3.55 ms | 34.9 ms | 20.3 ms | 8366 ms | 0.008 ms | 696729600 |

Reproduce with `~/.local/bin/sage probe.sage`, where the probe times the calls above for `n = 6, 7, 8`. Route chosen: the private engine of `O(L)` (`LatticeIsometryMor._engine_group`, `sage_extensions/categories/lattice_morphisms.py`) records the PARI order on the GAP model with `SetSize`, so the group's cardinality is the engine's order and never a GAP orbit computation.
Depends on this: `O(L).cardinality()` for every definite lattice.

### `TorsionQuadraticModule.orthogonal_group()` enumerates isometries by brute force in `_isom_fqf`

With no generators given, `TorsionQuadraticModule.orthogonal_group()` calls `sage.groups.fqf_orthogonal._isom_fqf`, which its own docstring calls "a slow brute force approach", and caches the generators on the module as `_orthogonal_group_gens`. At `n = 6` almost all of the time is in `_isom_fqf`: 394 calls of `fgp_module.submodule` take 2.49 s cumulative, `free_quadratic_module.span` and `FreeModule.__init__` about 2.3 s, `TorsionQuadraticModule._mul_` 1.40 s, and `matrix_space._element_constructor_` 1.02 s of own time.
`.order()` after construction costs 0.001 s. The first GAP call in a process costs about 0.6 s; the times below exclude it, because the probe calls `libgap.eval("1")` first.
First call, minimum of three fresh processes, SageMath 10.10.beta8, 2026-10-07, specimen `IntegralLattice(2*identity_matrix(n)).discriminant_group()`, the discriminant form of `A1^n`:

| n | `orthogonal_group().order()` | order |
| --- | --- | --- |
| 2 | 0.113 s | 2 |
| 3 | 0.197 s | 6 |
| 4 | 0.356 s | 24 |
| 6 | 4.90 s | 1440 |

Reproduce with `sage -python probe.py n`, where the probe warms GAP, builds the specimen and times `orthogonal_group().order()`. Route chosen: the private engine of the orthogonal group of a torsion form (`_engine_group` in `sage_extensions/categories/modules/framed/formed/torsion_form_modules.py`) calls this method on the engine module of the invariant-factor form, so its first `cardinality()` is bounded below by this curve.
Sage ships no other route to the full orthogonal group of a torsion quadratic form; whether Hecke/Oscar's `orthogonal_group(::TorQuadModule)` is faster is untested.
Depends on this: `D.orthogonal_group()` for every discriminant form `D`, and through it `rho_L` and the stable orthogonal group.

### PARI's definite isometry test costs the number of vectors up to the largest diagonal entry, and Sage has no other route

Sage's `QuadraticForm.is_globally_equivalent_to` calls PARI `qfisom`, so PARI is the only definite isometry test Sage ships.
`qfisominit(G)` and `qfauto(G)` enumerate every vector of norm at most the largest diagonal entry of `G`, so their cost follows that vector count, not the rank.
`qfisom(init, G')` against a stored `qfisominit` costs about a tenth of the init, and `qfauto(init)` on the same structure reuses its enumeration.
`D_n^+` with an LLL-reduced Gram matrix needs a vector of norm `n/4` among its basis vectors, which is what makes `D_20^+` expensive; its `qfisominit` needs more than 1 GiB of PARI stack, so with Sage's default stack it raises a stack overflow.
`qfrep(G, 4, 0)`, the numbers of vectors of norm 1 to 4, costs under 1 ms on every specimen.
The mass of a definite genus is a closed formula and costs a few ms. SageMath 10.10.beta8, PARI stack set to 8 GiB by `pari.allocatemem(2^33, 2^34)`, 2026-10-07, one run each; `D_n^+` is `span(ZZ, rows)` of `D_n` and the glue vector `(1/2, ..., 1/2)`, reduced by `LLL_gram`:

| lattice | vector pairs up to the largest diagonal entry | `Genus(G)` | `.mass()` | `qfauto(G)` | `qfisominit(G)` | `qfauto(init)` | `qfisom(init, G)` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `E7` | not measured | 63.8 ms | 8.2 ms | 6.6 ms | 3.1 ms | 0.7 ms | 0.9 ms |
| `E8` | not measured | 26.8 ms | 8.6 ms | 10.5 ms | 5.8 ms | 2.0 ms | 1.1 ms |
| `D12^+` | 1,156 | 23.5 ms | 3.6 ms | 42.3 ms | 24.8 ms | 15.1 ms | 4.8 ms |
| `D16^+` | 31,200 | 25.3 ms | 6.3 ms | 2838.8 ms | 2374.6 ms | 565.9 ms | 262.8 ms |
| `D20^+` | 301,304 | 32.2 ms | 6.1 ms | 78055.9 ms | 73099.5 ms | not measured | 6768.1 ms |

The `qfauto(init)` column comes from a second run, in which `qfisominit` took 2.8, 2.6, 26.3 and 2899.6 ms; the `D20^+` row ran beside another Sage process, and alone `qfisominit` took 31.07 s and `qfisom` 3.30 s.

Sage's `GenusSymbol_global_ring.__eq__` compares the local symbols and never the signature, and the class defines no `__hash__`, so genera cannot key a dictionary.
Sage decides neither which spinor genus of a genus a lattice lies in nor isometry of indefinite lattices of rank at least 3 when the genus has more than one spinor genus; `Genus.spinor_generators(proper=False)` only says whether it has more than one.
Sage's `Genus` exposes the group of spinor operators and the improper spinor kernel only through the private `_improper_spinor_kernel()` (`sage/quadratic_forms/genera/genus.py`, line 2586 in `sage-dev-allopts`); `spinor_generators(proper)` returns primes whose operators generate the quotient and cannot decide whether a given prime's operator lies in the kernel.
`_genus_classes` in `lattices.py` calls the private method to choose a neighbour prime whose operator lies in the kernel, so that `QuadraticForm.neighbor_iteration` stays in one spinor genus.
Hecke's `is_isometric(::ZZLat, ::ZZLat)` decides every case, the indefinite one by `p`-adic approximation and the spinor operators.

Reproduce with `~/.local/bin/sage probe.sage`, where the probe builds the specimens above and times each call.
Route chosen: `_isometry_class_representatives` in `sage_extensions/categories/lattices.py` computes each lattice's rank, determinant, signature and `qfrep(G, 4, 0)` once and groups by them, then groups by the owned genus `L.genus()`, whose equality compares the signature, the determinant and the canonical local symbols, and decides only inside a genus with more than one member.
A definite genus of three or more members with `mass · |O(L)| = 1` is one class and needs no comparison; otherwise `qfisominit` runs once per class representative and `qfisom` tests each member against them.
An indefinite genus of rank at least 3 with one spinor genus is one class; otherwise each member goes to Hecke `is_isometric` through `_OscarLatticeAdapter.integer_lattices_are_isometric` in `lattice_engines.py`. The PARI stack is left at Sage's default, so a lattice like `D_20^+` that reaches a comparison raises PARI's stack error rather than growing a process-wide setting.
The wall time of the whole partition as a function of the number of lattices is untested.
Depends on this: `Lattices(ZZ).isometry_classes`, and through it lattice-db duplicate detection.

### `IntegralLattice.short_vectors` enumerates a rank-8 shell of 66,805 vectors in about a second; a preamble element per vector costs about 2 ms

`IntegralLattice(G).short_vectors(n)` returns every vector of norm below `n`, grouped by norm, through fplll.
On `K8` (lattice-db record `0096`: rank 8, minimum 4, discriminant group `(Z/2)^2 + (Z/12)^2`), SageMath 10.10.beta8, 2026-10-08, one run each:

| bound `n` | vectors of norm below `n` | `short_vectors(n)` |
| --- | --- | --- |
| 9 | 1,153 | 0.09 s |
| 13 | 5,101 | 0.16 s |
| 25 | 66,805 | 1.34 s |

The preamble's cost is above the engine.
Raising one engine vector into the lattice by `_element_from_coordinates` costs about 1.8 ms (132, 828 and 2,796 vectors in 0.27, 1.24 and 5.04 s). The element predicate `is_root()` costs about 32 ms, most of it in the pairings `b(v, e_i)` against each generator, each a separate form evaluation.
`reflective_roots` asks every vector of norm dividing `2 exp(A_L)`, up to norm 24 on `K8`, so testing each element took about 35 min.
Sage ships no reflective-root routine: `free_quadratic_module_integer_symmetric.py` has no root method.

Reproduce with `.tmp/`-local probes that build `Lattices(ZZ)(G)` from the card and time `short_vectors`, `vectors_of_square` and `is_root`. Route chosen: `_roots_of_square` in `sage_extensions/categories/definite_lattices.py` takes the shell from `short_vectors`, pairs it against the basis in one product with the symmetric Gram matrix, keeps the rows where `b(v,v)` divides `2 b(v,w)`, and raises only the roots.
`reflective_roots` on `K8` then takes 5.3 s, and its derive 11.9 s. Depends on this: `reflective_roots`, `reflective_root_system_components`, and through them the lattice-db `root_system` of a definite card.

### PARI forqfvec imposes a fixed floating-point bound

`forqfvec(v, M, B, ...)` enumerates the ball `M(v) <= B` from a floating-point Cholesky reduction of `M`, and raises `precision too low in forqfvec` once the entries outgrow it; no `default(realprecision)` change reaches that iterator.
Measured 2026-10-20, PARI 2.17.1 through Sage's `sage.libs.pari`, counting `forqfvec(v, 2^k [2,-1;-1,2], 2^(k+1))`: `k = 20, 26, 30, 31, 32` each visit 3 vectors; `k = 33, 34` raise the error.
The former annular root search (`_ROOTS_IN_ANNULUS`), which doubled its radius until the roots spanned `L`, raised it on `U(2)` (lattice-db card `0013`, certify run 39460366651), where `ZPhi(L)` has index 2 and the radius grows without end; the error ended the whole certification worker.
Reproduce with `sage-docker-python -c 'from sage.libs.pari import pari; f = pari("(m,b)->my(c=0); forqfvec(v,m,b,c++); c"); print(f(pari("[2^34,-2^33;-2^33,2^34]"), 2^35))'`. Route chosen: `_roots_generating_lattice` in `sage_extensions/categories/lattice_engines.py` runs `_root_generators.gp`, which enumerates `ZZ^n` with exact `forvec(v = vector(n), ...)` in increasing L1 degree and keeps a root when `matinverseimage` shows it outside the integral span held by `mathnf`; on `U(2)` it runs until the job ends, as a semi-decision may.

The definite fixed-square enumerator now uses Hecke 0.39.22
`short_vectors(L, a, a)` through the shared OSCAR adapter instead of
`forqfvec`. The maintained route uses rational pseudo-Cholesky enumeration
and transports vectors back from the Gram LLL basis; the adapter restores
both signs. This is a source repair, with the scaled A2 and empty-shell
runtime specimens still pending under DEV-58. It does not change the
unbounded root-generation semi-decision described above.

### Two distinct symbolic variables take about 0.3 ms to compare, so a lattice basis label comparison is a symbolic decision

The basis labels of a preamble lattice are the symbolic variables `e_i = SR.var("e_i")` (`_formal_symbol` in `sage_extensions/categories/_lattice.py`). `bool(e_0 == e_1)` decides a symbolic relation, and for two distinct symbols Sage runs its numerical test with random interval values before it returns `False`; `bool(e_0 == SR.var("e_0"))` returns at once.
SageMath 10.10.beta8, no preamble in the process, 2026-10-08:

| comparisons | distinct symbols | equal symbols |
| --- | --- | --- |
| 100 | 0.038 s | 0.000 s |
| 1,000 | 0.289 s | 0.012 s |

`_finite_support_labels` (`framed_free_modules.py`) took the union of the supports of the spanning vectors by comparing labels pairwise, and each `support()` built its finite subset by the same comparisons.
On `E8` (lattice-db record `0094`) with its 240 roots, `L.subobject_on(roots)` took 5.9 s, almost all of it in those comparisons.
Route chosen: a finite framing is its own finite coordinate window, so its labels are taken whole and none are compared.
`subobject_on` then takes 0.36 s. A framing of infinite cardinality still forms the union, and still pays per comparison.
Depends on this: every span, saturation and sublattice of a finite-rank lattice, and through them the lattice-db `root_sublattice` field.

### The rational spinor norm costs nothing per isometry; reaching it through OSCAR costs about 25 s once per process

Sage has no spinor norm of an isometry of a rational quadratic space: `sage/quadratic_forms/genera/spinor_genus.py` and `genus.py` hold only spinor operators and the spinor kernel of a genus, and `sage/groups/matrix_gps/` has nothing.
PARI has no spinor norm function.
GAP's `SpinorNorm` (`grp/classic.gi`) covers only finite fields of odd characteristic, but the `WallForm(form, m)` it calls works over any field, `QQ` included.
The Wall form of `g` on `W = im(1 - g)` has discriminant the Zassenhaus spinor norm (Taylor, *The Geometry of the Classical Groups*, p. 163); with `form = 2G`, `DeterminantMat(WallForm(2G, g).form)` is in the square class of OSCAR's `rational_spinor_norm(...; b = 1)`, which is `b(v_1, v_1) ... b(v_m, v_m)` for `g = s_{v_1} ... s_{v_m}`. For `g = 1`, `WallForm` returns an empty form whose `DeterminantMat` raises; the spinor norm is 1, as GAP's own `SpinorNorm` returns.
GAP and the preamble's isometry matrices both act on rows.

Per-isometry cost, in ms per isometry, isometries of the Gram matrix by row action (`g G g^T = G`), SageMath 10.10.beta8 with GAP 4.16dev, Julia 1.10.11 with Oscar 1.7.1 through `sage-julia-bridge` 6625927, 2026-10-07, second of two runs:

| specimen | rank | isometries | Sage, Wall form by hand | libgap `WallForm` | OSCAR through the bridge |
| --- | --- | --- | --- | --- | --- |
| `A1+A1` | 2 | 8 | 1.44 | 0.70 | 1.12 |
| `U+A1` | 3 | 8 | 0.37 | 0.71 | 0.81 |
| `A1+A1+A1` | 3 | 48 | 0.12 | 1.61 | 0.62 |
| `E8` (reflection words) | 8 | 48 | 0.51 | 1.92 | 1.70 |
| `U+U+E8` | 12 | 48 | 0.17 | 1.65 | 6.48 |

The three routes agree on the square class of all 160 isometries.
The first libgap `WallForm` call took 595 ms and 246 ms in two runs; starting Julia and defining the adapter module took 36.55 s and 29.37 s. Engine alone, OSCAR: Julia process start 1.76 s, `using Oscar` 21.50 s, the adapter module 1.64 s, the first call 1.43 s. Through the preamble, `L.spinor_kernel().cardinality()` for `L = NamedLattices.A1 + NamedLattices.A1` took 29.36 s after a 2.47 s session import; `|spinor kernel| = 4`; the first of eight spinor-norm calls took 27.08 s, of which the bridge's `eval` loading Oscar took 23.16 s, and the other seven took 0.80 s together; `O(L)` through GAP took 0.57 s.

Reproduce with `direnv exec /home/dzack/research /home/dzack/gitclones/sage-dev-allopts/sage -python probe.py sage_extensions/categories/lattice_engines.py --oscar`, where the probe enumerates the isometries of the specimens above and times the three routes on each.
Route chosen: `_gap_rational_spinor_norm_class` in `sage_extensions/categories/lattice_engines.py` computes the rational spinor norm by libgap `WallForm`; the number-field spinor norm stays on OSCAR, since GAP has no general number fields.
On that route, one run each, `L.spinor_kernel().cardinality()` took 1.87 s for `A1+A1` (`|spinor kernel| = 4`, the eight spinor-norm calls 0.10 s together) and 1.74 s for `A1+A1+A1` (`|spinor kernel| = 24`, the 48 calls 0.85 s together), with no Julia process started.
Depends on this: `spinor_norm`, `spinor_norm_class`, `spinor_kernel` and `spinorial_kernel` of a lattice over `ZZ` or `QQ`.

### `QuadraticForm.siegel_product` is correct in ranks 4 and 8, halves the value in rank 2, and raises or is wrong in odd rank

By the Siegel–Weil formula, the coefficient of `q^m` in the genus theta series `theta_gen = sum theta_{L_i}/|O(L_i)| / sum 1/|O(L_i)|` equals the Siegel product of the real density and the local densities.
`siegel_product(m)` should therefore agree with `theta_gen`, which the probe computes from `Genus(G).representatives()`, `theta_series` and `number_of_automorphisms()`. The forms are `QuadraticForm(ZZ, 2*G)`, so `Q(x) = x^T G x`, for `m = 1, ..., 32`, SageMath 10.10.beta8, 2026-10-09:

| `G` | rank | classes | agreement with `theta_gen` | time of `siegel_product`, `m` up to 8 / 16 / 32 |
| --- | --- | --- | --- | --- |
| identity | 4 | 1 | every `m`; equals `r_4(m)` | 0.049 s / 0.113 s / 0.236 s |
| identity | 8 | 1 | every `m`; equals `r_8(m)` | 0.776 s for 32 |
| `[[2,-1],[-1,2]]` (`A_2`) | 2 | 1 | exactly half at every represented `m`: `m = 2` gives 3 for 6, `m = 6` 3 for 6, `m = 14` 6 for 12 |  |
| `diag(1,1,1)` | 3 | 1 | most `m` raise `TypeError: unable to convert 1/32*sqrt(2) to a rational`; the rest are wrong: `m = 2` gives 9/4 for 12, `m = 8` 9/8 for 12, `m = 18` 9/2 for 36, `m = 32` 9/16 for 12 |  |
| `diag(1,1,16)` | 3 | 2 | the same `TypeError` for most `m`; `m = 2` gives 3/16 for 4, `m = 8` 3/32 for 4, `m = 18` 3/8 for 12, `m = 32` 9/64 for 12 |  |

The source divides by 2 when `n == 2`, which accounts for the binary case.
`theta_gen` of `diag(1,1,16)` through `q^16` is `1, 2, 4, 0, 4, 8, 0, 0, 4, 10, 8, 0, 0, 8, 0, 0, 6`, in 1.18 s; since `r_L(1) = 4`, its cuspidal component is nonzero.
Reproduce with `sage probe.sage`, where the probe computes `theta_gen` from the genus representatives and compares `siegel_product(m)` with it for each specimen.
Route chosen: the preamble forms Siegel's product itself in `Genus.siegel_eisenstein_coefficient` (`sage_extensions/categories/lattices.py`), and no route uses `siegel_product`. The factors at `p | 2 m det L` are `Genus.local_density`; the product of the remaining factors is a quotient of the exact values of `quadratic_L_function__exact` and `zeta__exact` (`sage.quadratic_forms.special_values`) with their Euler factors at `2 m det L` removed; the real density is Siegel's Hilfssatz 26; and the product is halved in rank 2. The whole product is formed in `SR` before `QQ(...)`, so the square roots and powers of `pi` cancel: on 2026-10-09 the conversion succeeded for `A_2`, `-A_2`, `diag(1,1,1)`, `diag(1,1,16)` and the identity of rank 4 at every `m` up to 12, and each value equals `theta_gen`, in 0.1 s to 0.26 s per specimen for the 12 coefficients.
Depends on this: `Genus.siegel_eisenstein_coefficient`, and `definite.siegel_eisenstein_coefficients` in lattice-db.

### `QuadraticForm.local_density(p, m)` drops the factor `p^v` of the content

For `Q = p^v f` with `f` primitive at `p`, the local density is `beta_p(Q, m) = lim p^{k(1-n)} #{x mod p^k : Q(x) = m mod p^k} = p^v beta_p(f, m/p^v)`. `local_density` returns `beta_p(f, m/p^v)`: it divides out the content and does not multiply back.
Against a direct count of solutions modulo `p^k`, forms `QuadraticForm(ZZ, 2*G)`, SageMath 10.10.beta8, 2026-10-09:

| `G` | `(p, m)` | `local_density` | count modulo `p^k` |
| --- | --- | --- | --- |
| `diag(1,1,16)` (content 1) | `(2, 1)`, `(2, 2)`, `(3, 2)`, `(2, 17)` | 2, 2, 4/3, 2 | 2 (`k = 5`), 2 (`k = 5`), 4/3 (`k = 3`), 2 (`k = 6`) |
| `A_2` (content 2 at `p = 2`) | `(2, 2)` | 3/2 | 3 (`k = 5`) |

Reproduce with `sage probe.sage`, where the probe counts `x` in `(Z/p^k)^n` with `x^T G x = m mod p^k` and divides by `p^{k(n-1)}`. Route chosen: `Genus.local_density` in `sage_extensions/categories/lattices.py` multiplies Sage's value by `p^v`, with `v` the `p`-adic valuation of the content of `x^T G x`. Depends on this: `integral.local_densities` in lattice-db.

### `QuadraticForm.is_locally_represented_number` contradicts `local_representation_conditions` on an imprimitive form

For `E_8` with `QuadraticForm(ZZ, 2*G)`, so `Q(x) = x^T G x` takes only even values, `is_locally_represented_number(m)` answers `True` for `m = 21` and `m = 31` among `m < 40`. The same form's `local_representation_conditions()` says, at `p = 2`, that the classes `1, 3, 5, 7` are represented only from valuation 2, so no odd `m` is represented.
On the primitive form `QuadraticForm(ZZ, G)`, `Q(x) = x^T G x / 2`, every `m` is answered `True`, which is correct; on `A_2` with `2*G` the answers are correct.
SageMath 10.10.beta8, 2026-10-09.

`local_representation_conditions()` returns, for each exceptional prime, one entry per square class of `Q_p^x`, in the order `1, 3, 5, 7, 2, 6, 10, 14` for `p = 2` and `1, u, p, u p` for odd `p` with `u` the least quadratic nonresidue.
An entry is not a valuation: entry `e` means the class is represented by `r p^{2e}` and every `r p^{2(e+j)}`, where `r` is the listed representative, so the least represented valuation is `v_p(r) + 2e`; `+Infinity` means no element of the class.
Specimens, conditions at `p = 2`, with times: `x^2 + y^2 + 16 z^2` `[0, 2, 0, +Inf, 0, 1, 0, 1]` (0.19 s); `A_2` `[+Inf, +Inf, +Inf, +Inf, 0, 0, 0, 0]` and at `p = 3` `[+Inf, 0, +Inf, 0]` (0.13 s); `E_8` `[1, 1, 1, 1, 0, 0, 0, 0]` (0.41 s). Reproduce with `sage probe.sage`, where the probe compares the values represented by `x^T G x` below 40 with both methods.
Route chosen: `_least_represented_valuations` in `sage_extensions/categories/lattices.py`, behind `Genus.local_representations`, reads `local_representation_conditions()` at each prime where Sage records a condition, converts each entry to the least valuation `v_p(r) + 2e`, and omits the classes marked `+Infinity`; no route calls `is_locally_represented_number`. Depends on this: `integral.local_representations` in lattice-db.

### `anisotropic_primes` and `local_representation_conditions` inspect only the primes dividing `2 det`, which is wrong below rank 3

For rank at least 3 a form unimodular at `p` is isotropic over `Q_p` and represents every `p`-adic integer, so every anisotropic or exceptional prime divides `2 det`. For a binary form this fails: `x^T G x` for `A_2` is twice the norm form of `Q(sqrt(-3))`, anisotropic at every prime inert in it, such as 5, and representing only elements of even valuation there.
`QuadraticForm(ZZ, 2*G).anisotropic_primes()` returns `[2, 3, -1]` for `A_2`, and `local_representation_conditions()` lists only 2 and 3. Other specimens, `-1` standing for the real place: `x^2 + y^2 + 16 z^2` `[2, -1]` in 0.0078 s; `E_8` `[-1]`. SageMath 10.10.beta8, 2026-10-09.

The class `QuadraticFormLocalRepresentationConditions` (`sage/quadratic_forms/quadratic_form__local_representation_conditions.py`, Sage checkout `4b7841fd01a`) has three further defects below rank 3. They were read in the source and not measured.

- In dimension 1, `__init__` stores only the coefficient (lines 132--134). `local_conditions_vector_for_prime(p)` builds the vector at lines 346--353 and does not return it, so every call reaches `raise RuntimeError("the stored dimension should be a nonnegative integer")` at line 360. The built vector also marks the represented class `None`, not `0`.

- In dimension 2, at a prime outside `exceptional_primes`, `local_conditions_vector_for_prime` returns `[p, 0, 0, +Inf, +Inf]` at odd `p` and `[2, 0, 0, 0, 0, +Inf, +Inf, +Inf, +Inf]` at 2 (lines 341--344). That is the answer of a unimodular anisotropic form.
  At a prime where the form is isotropic it is wrong, because there the form represents every class from valuation `v_p(r)`.

- In dimension at least 2, a prime of the level is omitted from `exceptional_primes` when every entry it computed is `0` or `None` (lines 189--198). In dimension 2 such a prime then receives the wrong vector of the previous item.

`is_anisotropic(p)` (`quadratic_form__local_field_invariants.py`, lines 662--682) decides each dimension at any `p` from the determinant and the Hasse invariant.
`anisotropic_primes` is wrong below rank 3 only because it tests `prime_divisors(2 * det) + [-1]` (lines 757--758).

The preamble route was measured on 2026-10-09:

| Specimen | Anisotropic, among 2, 3, 5, 7, 11, 13 | Least valuations | Time for all calls |
| --- | --- | --- | --- |
| `A_2` | 2, 3, 5, 11 | at 2: `2, 6, 10, 14` from 1; at 3: `2` from 0 and `6` from 1; at 5 and 11: `1, 2` from 0 | 0.24 s |
| `<1>` | every listed prime | at every listed prime: `1` from 0 | 0.02 s |
| `x^T G x` with `G = diag(2, 6)` | 2, 3, 5, 11 | the same as `A_2` | 0.07 s |

In all three specimens the primes of the level of `QuadraticForm(ZZ, 2*G)` are the primes of `2 det G`.

Route chosen: `Genus.anisotropic_primes` in `sage_extensions/categories/lattices.py`:

- In rank at least 3, it returns the finite set from `anisotropic_primes()`.

- In rank 1 and 2, it returns the condition set of primes `p` of `ZZ` at which `is_anisotropic(p)` holds.

`Genus.local_representations` reads, through `_least_represented_valuations`:

- in rank 1, the class of the coefficient `c`, from `v_p(c)`;

- in rank 2, at a prime that Sage omits and that does not divide the level, the classes `1, u` from valuation 0 when the form is anisotropic there, and every class from `v_p(r)` otherwise (Serre, *A Course in Arithmetic*, Ch. IV, 1.7, Prop.
  4; Ch. II, 2.2, Cor.
  2 of Thm.
  1);

- in rank 2, at an omitted prime of the level, every class from `v_p(r)`;

- otherwise, Sage's stored vector.

In rank 1 and 2 the index set is the condition set of primes at which some class is not represented from `v_p(r)`. lattice-db stores both fields at the primes dividing `2 det L`. Its schema states the rule at the other primes.
Depends on this: `integral.anisotropic_primes` and `integral.local_representations` in lattice-db.

### Isotropy through the Witt index starts Julia; PARI's `qfsolve` decides it in hundredths of a second

At the time of this measurement, `witt_index()` over `QQ` called OSCAR's `rational_witt_index` through `sage-julia-bridge`. A nonzero rational isotropic vector exists exactly when the Witt index is positive, so `is_isotropic()` routed through `witt_index()` paid the Julia start-up on its first call. The current QQ Witt decomposition splits planes recursively using the exact rational isotropy decision and witness.
In a fresh process after the session import, `(Lattices(ZZ)("U") + Lattices(ZZ)("U")).represents(0)` on that route took 48.59 s and 45.19 s in two runs, and a later isotropy call in the same process took 2.58 s. PARI's `qfsolve`, which the preamble already calls for an isotropic vector (`_isotropic_vector_witness` in `lattice_engines.py`), returns a zero or an obstruction and decides the same question (Serre, *A Course in Arithmetic*, Ch. IV, 3.2, Thm.
8). `is_isotropic()` on that route, one run each, 2026-10-09:

| Gram matrix | rank | answer | time |
| --- | --- | --- | --- |
| `diag(1, -1)` | 2 | True | 0.063 s |
| `diag(1, 1, -3)` | 3 | False | 0.019 s |
| `diag(1, 1, 1, 1, -7)` | 5 | True | 0.032 s |
| `U + U` | 4 | True | 0.02 s, with `U + U + U` 0.02 s |

Reproduce with `direnv exec /home/dzack/research env PYTHONPATH=<worktree>/src sage -python probe.py`, where the probe times `is_isotropic()` on the specimens above in a fresh process.
Route chosen: `is_isotropic` in `sage_extensions/categories/lattices.py` decides isotropy over `ZZ` and `QQ` from `_isotropic_vector_witness`; over number fields it keeps `witt_index()`. Depends on this: `is_isotropic`, `isotropic_vector`, `represents(0)` and `representation_vector(0)` of a lattice over `ZZ` or `QQ`.

## mypy

### A star import that rebinds a name is rejected, and the first binding wins

A Sage session file that loads the preamble rebinds Sage names on purpose: the lowered file starts with `from sage.all_cmdline import *`, and `from dzack_research.preamble.all import *` then rebinds `Integer` and `RealNumber` to the preamble's own constructors.
Python binds the later import.
mypy 2.4.0 reports `Incompatible import of "Integer"` at the second import, and `reveal_type(Integer)` after it is still the first module's class, so every later use is checked against the wrong type.
Neither `--allow-redefinition` nor `--allow-redefinition-new --local-partial-types` changes either result.
This is upstream python/mypy#16972, open on 2026-10-02; Pyright takes the later binding.
Three-file specimen:

```bash
printf 'class Integer: ...\n' > a.py
printf 'def Integer(value: int = 0) -> int:\n    return value\n' > b.py
printf 'from a import *\nfrom b import *\nreveal_type(Integer)\n' > c.py
uvx mypy@2.4.0 --no-incremental c.py
```

Route chosen: none in this repository.
The rebinding is the design of the session, and a suppression would hide the wrong inferred type as well as the error.
The two errors stay on the lowered `sage-init.sage` until mypy models the later binding.

### mypy cannot see `sageparse` through a default editable install

`tree-sitter-sage` maps two package roots in `setup.py`: `bindings/python` for `tree_sitter_sage` and `src/sageparse` for `sageparse`. The default editable install of setuptools puts an import-hook finder in site-packages; Python imports `sageparse` through it, but mypy reads only the paths of `.pth` files and reports `Cannot find implementation or library stub for module named "sageparse"`. `editable_mode=compat` writes one `.pth` line, the first root `bindings/python`, so `sageparse` is not importable at all after it.
Checked with setuptools in the Sage venv on 2026-10-02 by `sage -pip show -f tree-sitter-sage` and the `.pth` contents.

Route chosen: `editable_mode=strict`, which builds a tree of symbolic links under `build/__editable__.*` and puts that tree on a `.pth` line.
Edits to existing files are live; a new module needs the install again.

```bash
direnv exec ~/research "$SAGE_BIN" -pip install --no-deps \
  --config-settings editable_mode=strict -e ~/gitclones/tree-sitter-sage
```

### Ideal saturation is Singular-backed and has no route over `AA`, `QQbar` or `CC`

`I.saturation(J)` for ideals of a multivariate polynomial ring goes through Singular, which accepts only its own coefficient fields.
Over `AA`, `QQbar` and the MPFR `CC` there is no saturation, so a localization `K[x, y]_f` could not decide whether a denominator `d` becomes a unit.
Exact divisibility `d.divides(g)` works over all three.
Measured on 2026-10-16 with Sage 10.x in `R = K['a,b']`: `(a^2).divides(a^3*b)` takes 0.23 s over `AA` on the first call and 0.02 s over `QQbar`.

Route chosen: for a principal ideal `(d)` in a polynomial ring over a field, `inverted_submonoid_meets` decides `(d)` meets `S` by `d | f^deg(d)`, where `f` is the product of the inverted elements.
Other ideals keep the saturation route.

### Multivariate `divides` raises `NotImplementedError` over `Qp`, and Sage's `Localization` calls it

`CommutativeRingElement.divides` has no implementation for `MPolynomial_polydict` over a `p`-adic field.
Sage's `Localization._cut_off_extra_units_from_base_ring_element` calls it on every division, so `x^-1` fails in `Qp(3)['x,y'].localization(x)`. Observed on 2026-10-16 on the standard charts of `P^2` over `Qp(3, 20)`.

Route chosen: the owned localization inverts a unit `a/s` as the fraction `s/a`, without the engine.
For a submonoid generated by monomial terms, `(d)` meets `S` exactly when `d` is a term whose variables divide the product of the generators; this reads the terms and needs no division.

### R-valued dual values are module elements when the ring is not placed as a module over itself

`Modules.ParentMethods.dual_module` returns `Hom_R(M, R.regular_module())`, and `FreeFormModules` used to replace that linear dual with `R.free_module(labels)` — a second free module of the same rank, carrying no pairing, so a functional could not be applied to a vector.
The dual is now the linear dual: a Mor parent whose elements are morphisms, with its selected resolution indexed by the primal's basis labels and `e_s^*` the matrix functional sending `e_s` to `1`.
`Lattices(ZZ)("U").metric_map()(e)(e)` evaluates the pairing, and `_matrix_coefficients` reads a one-row dual by the domain's labels.
Checked on Sage 11.0.beta5 at `sage-extensions` 2fd11ac on 2026-10-31.

Two claims about the *infinite-rank rational* dual remain open, and both are construction gaps rather than presentation choices:

* `R.regular_module()` is a substitute rank-one free module for every ring whose coefficient ring is smaller (`QQ`, `ZZ/n`, `ZZ['x']`, `QQbar`), because `_owned_ring_category` claims `FinitelyGeneratedFreeModules(R)` only when the constructor selects no scalar base, and a ring carries one native module presentation — over its coefficient ring. So an `R`-valued functional over `QQ` publishes an element of that free module rather than an element of `QQ`.

  Fixing that at the ring owner does **not** work by refining the ring into a module category. Installing the self-module datum (`_preamble_regular_module_base = R`, the unit framing on `R.free_module(1)`, `_fix_selected_module_resolution(R, R, …)`) plus `FinitelyGeneratedFreeModules(R)` gives the right identities — verified for `ZZ`, `QQ`, `ZZ/6`, `GF(5)`, `Qp`, `AA`: `R.regular_module() is R`, `R in Modules(R)`, and `R.scalar_action()` the multiplication — but the category refinement takes over the *ring's own presentation*: `str(QQ)` becomes `Free module on {1} over Integer Ring`, and `QQbar` fails to construct with `RecursionError` in `_OwnedRingParent.__hash__` through `_preamble_is_number_field_order`. A ring refined into a module category is presented as that module, which is the substituted object the architecture forbids. The self-module structure needs a read path at the module owner that does not refine the ring's category (a module-level accessor for the ring's regular module), not a category claim on the ring. Attempted and reverted 2026-10-31.

  A second attempt installs the datum without refining the ring into a free-module category — only into `Modules(R)`, which leaves `str(R)` and `hash(R)` alone — and then reads the self base through `Modules.ParentMethods._module_base_ring`, used by `module_category`, `scalar_action`, `extension_ring` and `_apply_pointwise_scalar`. That gives `R.regular_module() is R`, `R in Modules(R)`, the multiplication action with domain `R`, and ring-valued functionals on `Lattices(QQ)(QQ**NN)` — `c(e0) = 1`, `c(e1) = 0` — for `ZZ`, `QQ`, `QQbar`, `ZZ/6`, `GF(5)`, `Qp`, `AA`, with every ring's string and hashing unchanged. It still fails as a global read path, because one object then has to report two scalar rings and `base_ring()`/`module_category()` give one answer:

  * `Lattices.dual_lattice` builds `Res_{ZZ->QQ}(QQ)` and identifies it with `QQ`; `extension_ring` reading the self base makes `regular_module_identification` demand `QQ.regular_module()` where the construction has `QQ` as a `ZZ`-module, and `SemilinearModuleMorphism` then refuses the identity `ZZ -> ZZ` map into a codomain whose base it reads as `QQ`;
  * `_apply_pointwise_scalar` compares the Mor's centre with the codomain's self base, so a `QQ`-module morphism's scalars are read as `QQ` where the construction states `ZZ`.

  The read path therefore has to be per use, not per object: `Modules` needs the module structure keyed by the base ring (`M.module_structure(R)`), with the existing `base_ring()` left as the coefficient base. Reverted with no change committed; the previous state is `a1ebba9`.
* There is no cokernel algorithm for a morphism of infinite-rank modules, so `correlation.is_surjective()` on `Lattices(QQ)(QQ**NN)` raises instead of answering.

  The endpoints, read off the objects: the domain is `Lattices(QQ)(QQ**NN)`, the direct sum `QQ^{(NN)}` on the selected framing; the codomain is `Mor(L, QQ.regular_module())`, a Mor parent with no chosen resolution (asking `module_generating_set()` raises `… has no chosen resolution relative to Category of modules over Fraction Field of Integer Ring`). A missing resolution is **not** evidence that the codomain is not the product: `Hom_R(R^(S), R)` is `prod_S R`, given by its projections and universal property, and a product needs no basis. The product owner does supply it — `Modules(QQ)._categorical_product_construction(IndexedFamily(NN, QQ.regular_module()))` is `Module over QQ on Product of the family over NN` — but `product_element`/`product_component` reject the section whose parent is the *set* product (`Section of Product … is an element of Product …, not of the product Product …`), so the correlation's images cannot yet be assembled through it and the dual stays the Mor. That identity at the product owner is the next step; it is not an obstacle to the mathematics. The correlation is injective and not surjective: for `v = sum_{i in F} c_i e_i` with `F` finite, `b(v,e_s) = c_s`, which vanishes for `s` outside `F`, while `L.linear_dual()(lambda _: 1)` is the constant functional — so no finite-support `v` maps to it. Stating that as `not is_surjective()` needs the product presentation of `Hom_R(QQ^{(NN)}, QQ)` and the cokernel map on it; a general infinite-rank cokernel algorithm is not the answer and is not written.

`tests/lattices/test_lattice_semantic_api.sage` records them in the test that states them; it is red for the assertions it cannot decide and green for the finite pairing.

**Correction, 2026-10-31.** An earlier revision of that test was rewritten to drop `assert not correlation.is_surjective()`, `assert lattice.is_nondegenerate()` and `assert not lattice.is_unimodular()` while adding projection/evaluation witnesses, and the resulting pass was reported as an improvement in the failure count. That was a weakened acceptance: the three public obligations are restored in the test, `is_nondegenerate()` and `is_unimodular()` now answer through the correlation (nondegenerate because it is injective, not unimodular because it is not onto), and `is_surjective()` remains the one open assertion — it raises `cannot compute the cokernel ... no algorithm is available for these modules` for a morphism from the direct-sum lattice to the product module. Deciding it needs the comparison of the direct-sum image with the product (the constant family lies outside the finite span), which is not a general infinite-rank cokernel. Any count that improves because an assertion was deleted is not an improvement.

`is_surjective()` for that correlation is now decided at the morphism owner, from a retained witness rather than a cokernel: the construction of the correlation knows each generator image is the coordinate functional `e_s^*`, supported on the singleton `{s}`, so every value of the correlation is supported on the finite set of its argument's indices; the product's constant family with a nonzero component is not, and the index set is infinite. `ModuleMorphismMethods.non_surjectivity_witness()` returns that element and `is_surjective()` reads the retained refutation. No general infinite-rank cokernel is invented and no specimen is hardcoded.

**Settled, 2026-10-31: the metric dual's value module is the restricted regular module.**
`CONTRIBUTING.md:5613` (owner ruling 2026-10-16) requires identifying an algebra with its restricted regular module by a *morphism*, never by collapsing scalar structures through `base_ring`; commit `17a8390` selects restricted regular-module values deliberately, and issue #1 and `Lattices.dual_lattice` (`lattices.py:5450`-`5523`) agree. `RestrictedScalarsModules.regular_module_identification()` returns the actual Mor `Res_f(S^1) -> S`; it is not Python identity and does not make `Res_f(S^1)` be `S`.
There is therefore no contract conflict to arbitrate. `tests/lattices/test_catalogue.sage::test_tdp_metric_dual_is_the_formed_linear_dual` was reconciled through that identification: it now asserts the value module *is* `Res_{ZZ->QQ}(QQ.regular_module())`, that the identification's domain is that module and its codomain is `QQ`, and it keeps every scalar-action, pairing, coefficient-base, inverse-Gram and correlation equation, exactly as `test_the_dolgachev_pinkham_dual_lattice_retains_its_metric_form` requires. The earlier text here (that the two catalogue requirements conflicted, and that the resolution was to make the restriction *be* the ring) was wrong and is withdrawn.

### The named-coinvariant consumer is blocked by the port's pre-move imports, and the pair must be republished together

`LatticeIsom.an_element` (`lattice_morphisms.py:4199`) routes indefinite isometry searches through `sage_indefinite_port.indefinite.marked_lattices`, which imports the pre-move research preamble:

```text
sage_indefinite_port/indefinite/marked_lattices.py:18  from dzack_research.preamble.all import ZZ, Cat, Lattices
sage_indefinite_port/indefinite/marked_lattices.py:19  from dzack_research.preamble.categories.abstract_categories.arrow_categories import CosliceCategory
sage_indefinite_port/indefinite/marked_lattices.py:20  from dzack_research.preamble.categories.abstract_categories.products import FiniteOrdinalCategory
sage_indefinite_port/indefinite/marked_lattices.py:21  from dzack_research.preamble.categories.lattice_morphisms import LatticeIsometryMethods
```

Those modules do not exist: the preamble lives in `sage_extensions`. The shared image carries the port at `86d860a`, where eight modules import `dzack_research` (`indefinite/edgewalk.py`, `edgewalk_extensions.py`, `eichler.py`, `isotropic_induction.py`, `lorentzian_cells.py`, `marked_lattices.py`, `recursive.py`, `invariants.py`); the maintainers report ten at current port main, so updating the embedded checkout alone does not repair the consumer.

The port's existing acceptance pair pins the old research `064cd6e8`, which cannot be the permanent dependency of current `sage-extensions` without putting two library identities in one process. So this is not a defect of either repository's source at its own revision: it is a dependency-pair mismatch.

Consequence here: `tests/lattices/test_catalogue.sage::test_named_invariant_and_formed_coinvariant_lattices_are_exact` cannot run its isometry witness and fails at the import, not on a lattice computation. It stays explicitly open until the port publishes a coherent pair — its imports and contracts migrated to canonical `sage_extensions`, with the minimal `LatticeIsom.an_element`/named-coinvariant consumer and the bounded port acceptance green against it. Do not install the old research provider beside this library and do not patch the port from here.

### A raw rootfs launcher drops the image's Julia depot, and every Julia consumer then reports a missing package

The shared image declares `JULIA_DEPOT_PATH=/opt/julia-depot:` and preinstalls JSON and Oscar there (`sage/docker/research-environment.Dockerfile`). A launcher that only sets `HOME`, `PATH` and `TMPDIR` leaves Julia with its default depot, so the bridge's own `import JSON` at `sage_julia_bridge/julia_bridge.jl:2` fails:

```text
ERROR: LoadError: ArgumentError: Package JSON [682c06a0-de6a-54ab-a142-c8b1cf79cde6] is required but does not seem to be installed:
in expression starting at /repos/sage-julia-bridge/src/sage_julia_bridge/julia_bridge.jl:2
```

That is a false missing-package error: nothing is missing from the image. Checked in the shared image on 2026-10-31 by running the same probe with and without the variable.

Route chosen here: the launcher passes the image's environment through to every Sage/Julia subprocess, `JULIA_DEPOT_PATH=/root/.julia:/opt/julia-depot:` (the writable user depot first, then the image depot) with `JULIA_CPU_TARGET=generic`, and creates the guest's `/root/.julia` once. Then `julia("1+1")` is `2`, `using Oscar; 2+2` is `4`, and the Oscar-backed lattice consumer answers (`E8.is_isometric_to(E8)` is `True`). No Julia package is installed by this project; a missing package is the image's to provision.

### A lattice isometry built by a public homset had no formed-module datum, and its hash fell back to the repr

Both halves are the same shape: an arrow placed in a class by inheritance while the initializer that defines that class's state never ran (``sage-extensions#5``).

`LatticeIsometryMethods.__init__` hands its retained forward/inverse pair to `CategoricalIsomorphism.__init__` through `super()`. Since `LatticeEmbeddingMethods` defines no `__init__`, that is the very next initializer in the linearization, so `LatticeMorphismMethods.__init__` and `FormedModuleMorphism.__init__` never run. The arrow is then a `ModuleMorphismMethods` by placement and has none of its state:

```python
L = Lattices(ZZ)([[0, 1], [1, 0]])
images = tuple(L.module_generators())
L.Isom(L)(images).module_morphism()
# AttributeError: 'OwnedLatticeIsometryMor...ArrowType' object has no attribute '_form_module_morphism'
```

The same object lacks `_element_function`, so `ModuleMorphism.__mul__`'s identity question raised on every composition of a module morphism with an isometry, e.g. the `prescribed = ... * self` line of `witt_extension_locus`. Fixed at the constructor: `_initialize_formed_module_arrow` runs `LatticeMorphismMethods.__init__` on the already retained module map (the module Mor constructor returns an arrow of its own parent unchanged, so nothing is rebuilt), and the isomorphism contract is built afterwards from the same map.

The hash failure is worse than an error. `LatticeIsometryMethods.__hash__` hashed `self._coordinate_tensor()`, whose `_tensor_hash` hashes components that are owned module elements without `__hash__`, so `hash(isometry)` raised `TypeError: unhashable type: 'OwnedJoinCategory.element_class'`. Sage's `cached_method` then keys the call on the argument's `repr`, and every lattice isometry between fixed endpoints has the same `repr`:

```python
group = V.O().subgroup((exchange, transvection, reflection))   # three distinct isometries
group.selected_group_resolution().augmentation()(free_generator_i)  # the first element, for every i
```

The first computed value is returned for every later argument, silently. It surfaced in the migrated port as `assert 2 == 48` in `test_isotropic_plane_and_flag_automorphism_generators_preserve_their_marks` — the plane-stabilizer generators had all collapsed onto the summand swap — and as `test_vector_stabilizer_has_oscars_order` returning the identity matrix alone. `__hash__` now uses the coordinate tensor's own designated `_cache_key`, which the tensor owner already provides for unhashable scalars. Checked on the two specimens the library uses for this: separately built isometries from the same images are equal and hash equally (a set of the two has one element, and a dict lookup by the rebuilt arrow answers), distinct isometries hash apart, and `O(V).subgroup(...)` returns its supplied generators, pairwise distinct, with a subgroup of it doing the same. Hashing delegates the scalar comparison to the tensor owner, so a scalar the library cannot compare by value still keys on identity.

Rule: a class placed in a category by inheritance must run that category's initializer, and a method that takes library arrows must have a working `hash` or the cache it is keyed on is silently wrong. `tests/lattices/test_isometry_arrow_state.sage` states both, and fails at `ce855c6` on all three cases.

### The coinvariant discriminant transport now reuses its pair; the presentations it builds still scale with the group order

`research#621` priced one invariant-to-coinvariant discriminant conversion at 21 s on an order-1024 form, with four presented-module morphisms per conversion: the conjugated map, its generic inverse, and the two transports `_from_engine` raised. The delta that fixes this lived only in research's vendored fork of this library (`5cf90d9b`); it is ported here, at the canonical owner, not re-implemented:

- `IsometryPrimitiveExtension._full_discriminant_glue_data` and the new `_coinvariant_glue_inverse_maps` are cached: the two full-glue inclusions' inverses are built once from codomain generator preimages and checked on those generators.
- `_coinvariant_discriminant_from_invariant` conjugates the invariant automorphism *and its stored inverse* to build both arrows on selected generators, instead of constructing one map and asking the generic solver for its inverse.
- `TorsionFormOrthogonalGroup._from_engine` accepts an owned forward/inverse pair (both or neither), `_normalized_form_automorphism` passes the pair it already holds, and `TorsionFormAutomorphism.inverse()` reverses its own stored pair rather than conjugating `a^{-1}` back through normalization.

Measured on the canonical pair's own specimens, one process at a time.  The host is shared (four CPUs, 16 GB, no swap) and other projects' Sage jobs were **not** controlled during these runs, so the seconds below are indicative, not an idle-machine benchmark: the pre-port steady figure alone moved between 11.7 s and 26.3 s across two runs.  What the measurement is meant to establish is the per-conversion ratio and the construction counts within one run, both of which are stable, not the absolute wall time.  The first conversion pays the one-off setup of the fixed glue data, the coinvariant module's presentation and the finite engine; every later conversion on the same fixed forms is the steady cost the consumer repeats (the port performs 19 per form):

| case | invariant form | coinvariant form | before the port (`7b222e8`) | after the port (`297bf69`) |
| --- | --- | --- | --- | --- |
| `U + U` specimen | order 4, 2 generators | order 4, 2 generators | 0.211 s per conversion, 13.0 presentations | 0.014 s per conversion, 0 presentations |
| `I_En` on the K3 lattice | order 1024, 10 generators | order 1024, 12 generators | 11.7-26.3 s per conversion (two runs), 30.7 presentations | 0.193 s per conversion, 0 presentations |

Each figure is a steady per-conversion cost on already warm fixed data (one untimed conversion first), in its own process on an otherwise idle VM; the first conversion on a form pays a one-off 25-38 s at order 1024 and 0.7-0.8 s at order 4, in both revisions.  Reading the earlier numbers straight off three unwarmed conversions prices that setup as if it were per-conversion: that is where an earlier revision of this entry reported "8.71 s per conversion", and why the revision before it reported 12.0 presentations per conversion when the twelve belong to the first conversion only.

What is established, with `tests/lattices/test_discriminant_transport_inverse_reuse.sage` counting `_presented_module_from_morphism`: after the port a conversion constructs **no** presented module (the test fails at `7b222e8` with twelve constructions for the second conversion), and the steady cost follows the coinvariant form's generator count rather than its order — 0.131 s at 12 generators against 0.012 s at 2 generators with an elementwise variant, 0.193 s against 0.014 s as ported, while the order differs by 256.  The generic inverse solve is gone, the glue inverses are built once, and the converted action reuses its stored pair.

One further variant was measured and not taken: building both conjugated arrows with `_from_constructed_element_map` over the retained glue maps (no generator images at all) costs 0.131 s against 0.193 s at order 1024 and removes the last per-conversion crossing.  It reproduces the same automorphisms (equal engine elements, images agreeing on every coinvariant generator) but it would make this arrow elementwise rather than the fork's, for about 0.06 s on a path the consumer calls 19 times per form — not worth diverging from the ported construction.  Re-measured 2026-11-01.

Boundary of the measurement: the frozen `O(L^f)`-generator route for `I_En` (`LatticeIsom.an_element` through `sage_indefinite_port`) is not reachable in this image — it dies in `sage.graphs.bliss`, the same image defect recorded above — so the conversions were priced on `O(A_{L^f})`, which is finite data.  The invariant form, coinvariant form and glue are the frozen ones (both order 1024); the conversion's cost depends on the fixed forms and glue, not on which automorphism is fed in.

### Maximal elliptic subdiagrams enumerated every induced subdiagram before deciding anything

`maximal_elliptic_subdiagrams(connected=False)` called `elliptic_subdiagrams(connected=False)`, which materialises **all** \(2^n\) induced subdiagrams as owned rooted diagrams with their root Grams and inclusion arrows, and filters them afterwards.  For Sterk's five diagrams (10-14 roots) that is 27,648 diagram constructions at roughly 83 ms each: the ten-root `Sterk_2` alone took 85 s to build its 1024 subdiagrams while the ellipticity filter over them took 0.09 s, and a consumer's first run over all five had not finished after half an hour.

Maximality is a property of vertex sets, and the Schlaefli form of an induced subdiagram is the principal submatrix of the parent's form on that subset, so both decisions belong on subsets.  `_inertia_matrix` (the matrix `_inertia_counts` already built) is factored out, `_principal_inertia_counts` reads its principal submatrix, and `maximal_elliptic_subdiagrams(connected=False)` now enumerates subsets by cardinality and lexicographically (the order `induced_subdiagrams` uses), keeps those whose submatrix is positive definite, drops the non-maximal ones, and constructs only the survivors.  `_inertia_counts` itself is unchanged in behaviour: the Sylvester loop is now the module function `_inertia_of_entries`, shared by both readers.

Measured on `Sterk.diagrams()`: `Sterk_2` 52.7 s → 1.4 s with an element-for-element identical list of maximal vertex sets in identical order; all five diagrams 40 s in total, where the previous owner implementation needed roughly 38 min.  Counts and ranks: `Sterk_1` 44 (30 of rank 8, 14 of rank 9), `Sterk_2` 9 (1 of rank 8, 8 of rank 9), `Sterk_3` 34 (5, 29), `Sterk_4` 29 (8, 21), `Sterk_5` 132 (30, 102) — every diagram has a rank-9 maximal elliptic subdiagram, which a Type III ray needs.  `tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage` holds the owner to those counts and to what the consumer reads off them: ellipticity, retained vertex labels and vertex names, retained roots and root Gram, the inclusion arrow's codomain, and the connected components of a disconnected member.

**Correction, 2026-11-01.** The first revision of that file checked maximality against every single added vertex for only the first two surviving subdiagrams of each diagram, and the report of it described the coverage as exhaustive. It was not: 10 of the 248 returned maximal subdiagrams were tested that way. The record is corrected here and the case now runs over every returned maximal subdiagram and every vertex it omits, through the public `induced_subdiagram(...).is_elliptic()` decision (2,430 checks over the five diagrams). No other assertion was relaxed.

Boundary: the equality against the previous implementation was checked element-for-element on `Sterk_2`; for the other four diagrams the acceptance is the invariant set above plus the shared code path, not a second full old-code run (each of those costs tens of minutes by construction).

### The session export never bound the library's group owner, so `Groups` was Sage's category in every test

`sage_extensions.all` exported `AdditiveGroups`, `Modules`, `Lattices`, `Sets` and `CoxeterDiagrams`, but neither `Groups` nor `OwnedGroups` from `sage_extensions.categories.group.groups`, where `Groups = groups = OwnedGroups` is the library's group owner.  A `.sage` test that writes `from sage_extensions.all import *` therefore still saw Sage's `sage.categories.groups.Groups`, which has no `S`, `C`, `V4`, `Free` or `Coxeter`:

```text
tests/lattices/test_coxeter_subdiagrams.sage:53: AttributeError: type object 'Groups' has no attribute 'S'
```

Both names are now exported.  Checked on the five files that use the bare name most heavily (`test_adjunctions`, `test_selected_pullbacks_and_pushouts`, `test_group_algebras`, `test_isotropic_binary_orthogonal_groups_are_finite`, `test_rational_definite_orthogonal_groups`): **20 failed / 13 passed before, 14 failed / 19 passed after, with no test newly failing** — the six that changed are the ones that had aborted at `Groups.S(...)`.

Two follow-on items this exposed, neither repaired here:

- `tests/categories/test_group_owned_meets.sage` now reaches `s3.cardinality() / subgroup.cardinality()` and fails with `TypeError: unsupported operand type(s) for /: 'Cardinalities.parent_class' and 'Cardinalities.parent_class'` — owned cardinalities have no division.  That is a cardinal-arithmetic gap, not a group one.
- The Coxeter contract itself used `Aut().is_isomorphic(...)`, and no group parent has ever had that name (the owner has `is_isomorphic_to` since the initial import); `Groups` was equally wrong there.  The test now states the owner's method and keeps a negative case (`not ... is_isomorphic_to(Groups.C(6))`) so the decision cannot be vacuous.

### The Sterk archive type table was right; the comparison made its two scales unequal

`tests/lattices/test_sterk_elliptic_population_archive.sage` compared the computed type multiset to the recorded one through `Set(...)`.  The recorded table states the scale as an integer and the test's own `scaled_type` states it as `Fraction(...)`, and the owned set decides a tuple's element identity by its entries, so `(5, 'D', 2)` and `(5, 'D', Fraction(2, 1))` did not meet even though the numbers agree.  The failure was a representation artefact: recomputing the multiset key-for-key gives `missing {}` and `extra {}` for all five diagrams (`Sterk_1` 120, `Sterk_2` 64, `Sterk_3` 66, `Sterk_4` 77, `Sterk_5` 118 entries, each equal to `sum(_CONNECTED_ELLIPTIC_TYPES[...])`).  The test now compares `Counter` multisets with both sides in one representation, which states the same numbers more exactly than the set comparison did; the recorded table is unchanged.

### The Bliss repair is already deployed in this rootfs, and the v1 script correctly refuses to touch it

`/opt/bliss-repair.json` records `base_revision b0cd7d86e21eb450ed90e4c83707920e1d5d429a`, the v1 patch digest `baf4b826e8093c7891de3650789c7f1e13c7d9e82de362a124486956e53f32b3`, the v2 patch digest, and the installed module's digest `d941337e3a69b8256771c2fbbff5c2604e724b717dcc41352e12a3f7f9b75a75` — the owner's v1 module hash.  The installed `sage/graphs/bliss.cpython-314-x86_64-linux-gnu.so` hashes to that value, and the script's own smoke tests pass against it (both `canonical_label` backends on the labelled case, `K4` of order 8, `PetersenGraph` of order 120).  So the deployment is a no-op verified by artifact identity, and the published image is not rebuilt.

Running the v1 script against this copy stops at its own guard, which is correct: this copy carries the **v2** source, whose `meson.build` hunk differs from v1's, so `git apply --reverse --check` cannot recognise the patch and the pre-patch cleanliness check then reports `src/sage/graphs/meson.build has local changes; this copy is not the published image`.  Nothing was patched, rebuilt, installed or re-stamped by that run.  Do not "make it pass" by rewriting the script or the source: that would be the library-local variant the deployment forbids.

### With Bliss repaired, the frozen Enriques consumer reaches the owner and stops on QQ not being placed in `PrimeFields`

`tests/acceptance/test_boundaries.sage::test_enriques_modular_groups_match_dutour_sikiric_hulek[case_1]` no longer dies in the automorphism search.  It now runs `_gamma_h` through `lattice(_E10["gram"]).twist(2).Isom(invariant).an_element()`, `polarized(...)`, `coinvariant_extension_subgroup()` and stops at

```text
sage_extensions/categories/lattices.py:4110  O_plus
AssertionError: O^+(Integral lattice of rank 12 and signature (2, 10)) is the kernel of the real
spinor norm at the real place of Frac(R); QQ has exactly one, but Frac(R) = Fraction Field of
Integer Ring: pass a real embedding of it to spinor_kernel
```

The guard reads `field in PrimeFields() and field.characteristic() == 0`.  For the owned rational field the second half holds (`characteristic()` is 0) and the first does not: `QQ in PrimeFields()` is `False`.  The placement is *declared* — `_rational_placements()` in `ring_foundation.py` is documented as "the prime field of characteristic 0, ordered, and the number field of degree 1" and returns `*_field_placements(), PrimeFields(), OwnedOrderedRings(), OwnedNumberFields(), CountablyInfiniteSets()` — but it is never applied: `_owned_rationals()` is `_owned_integers().fraction_field_localization()`, a localization object whose category join is "local nontrivial localization rings, commutative algebras, owned ordered rings, fields, modules over the fraction field", with no `prime fields`.  The same guard appears at `lattices.py:9189` and `9250`, so three owner entry points depend on the placement.

That is the next owner repair for this consumer: give the rational field its declared placement at the construction that produces it (or have the localization carry the named placements for `Frac(ZZ)` specifically), not at the three guards.

Separately: a whole-directory `tests/groups` run still dies at 69% with no pytest summary, with the repaired module installed, so that crash is not the Bliss ABI one and the directory scan remains unavailable; the five-file before/after comparison is the regression evidence for the group-export change.

### A boundary ray of Type II is a union of affine components, which `is_parabolic()` does not name

`is_parabolic()` means negative inertia index 0 and radical of dimension **one**, and it keeps that documented meaning. The nullity of a disjoint union is the sum of its components' nullities, so affine \(E_7\) together with affine \(A_1\) has radical of dimension two and is not parabolic by that predicate; neither is affine \(B_4\) with affine \(B_4\). Rather than reinterpret the existing predicate for its callers, the owner now states the union explicitly:

- `is_parabolic_union()` — at least two connected components, each parabolic, decided by `induced_subdiagram(component).is_parabolic()` on the components `connected_component_vertex_sets()` reports. Finite components are excluded, a single affine component is excluded (it is not a union), and the empty diagram is excluded (no components).
- `maximal_subdiagrams(predicate, *, max_rank=None)` — the general query; `predicate` is decided on a **vertex tuple**, so the owner enumerates subsets and constructs only the survivors, the same route `maximal_elliptic_subdiagrams` takes.
- `maximal_parabolic_union_subdiagrams(*, max_rank=None)` — the Type II query.
- `maximal_elliptic_subdiagrams(*, connected=False, max_rank=None)` — the existing query, now with the same optional cap.

`max_rank` caps the **returned** subdiagrams after maximality is decided over every subset (`_maximal_vertex_sets`), so a capped query is exactly the uncapped one filtered by rank; it can never promote a subdiagram contained in a larger accepted one. The survivors are the induced subdiagrams, with labels, vertex names, roots, root Gram and the inclusion arrow.

Cost is the subset route: the five Sterk diagrams give their whole inventory in about 38 s, the fourteen-root `Sterk_5` alone taking 24 s for its 16,384 subsets.

Inventory of maximal affine unions on the five Sterk diagrams as this owner computes it: `Sterk_1` 3, `Sterk_2` 0, `Sterk_3` 3, `Sterk_4` 1, `Sterk_5` 9 (two of rank 11, the rest rank 10) — 16 in total. If a consumer's "five Type II cases" is a different count, the distinguishing condition is not part of the contract stated here; the named examples affine \(E_7\) + affine \(A_1\) and affine \(B_4\) + affine \(B_4\) are both recognised.

### `Frac(ZZ)` did not carry the placement that names it, so `QQ in PrimeFields()` was false

`_rational_placements()` documents the named rational field as "the prime field of characteristic 0, ordered, and the number field of degree 1" and returns exactly those categories, but nothing applied it: `_owned_rationals()` is `_owned_integers().fraction_field_localization()`, and the localization construction supplied only `LocalizationRings()`, the field placements, and the algebra categories.  Consequently

```python
QQ.characteristic()            # 0
QQ in PrimeFields()            # False
QQ.category()                  # local nontrivial localization rings, commutative algebras,
                               # owned ordered rings, fields, modules over the fraction field
```

and every guard of the form `field in PrimeFields() and field.characteristic() == 0` rejected the rational field — `Lattices.O_plus` at `lattices.py:4110`, `9189` and `9250`, which is where the frozen Enriques consumer stopped with "QQ has exactly one, but Frac(R) = Fraction Field of Integer Ring: pass a real embedding of it to spinor_kernel".

The placement is now applied at the construction that produces the field: `_fraction_field_localization` adds `_rational_placements()` when the source is the owned integers, so `Frac(ZZ)` carries the categories its own name declares, and `QQ in PrimeFields()` is `True`.  No guard was relaxed.  Other fraction fields are untouched, and the three ring files that exercise this construction (`test_fraction_field_localization`, `test_commutative_algebra`, `test_elementary_arithmetic_of_owned_rings`) have an identical failure set before and after (24 failed / 19 passed, no test changed).

**Correction, 2026-11-01.** An earlier report here said that the rerun of the frozen Enriques case "passed the 3.5-minute point where it previously died on `O_plus`". Elapsed time past the earlier stop is not evidence of that: the case was killed by its own 40-minute limit with no verdict and no output, and it says nothing about which call it was in. What establishes the repaired condition is the targeted regression `tests/rings/test_rational_field_placement.sage`, which drives `Lattices.O_plus` at the real place of `Frac(ZZ)` on the hyperbolic plane directly, in about a second, and fails at `d58660c` with the reported assertion. The consumer's own verdict is still outstanding, and until its log reaches that call or it returns, only that regression is evidence.

The maximal elliptic family is now audited independently of itself as well: `tests/lattices/test_coxeter_maximal_subdiagram_audit.sage` enumerates every subset of four small fixtures, decides each induced subdiagram with the public `is_elliptic()`, derives the maximal family by inclusion, and compares it to the owner's query; it checks every survivor against every vertex it omits, and it pins that `max_rank` and `max_form_rank` are applied after maximality (the capped answer is the uncapped family filtered, at every threshold) and that the generic predicate receives every subset as labels.

### A lattice display computed an index of inertia before deciding to show it

Research issue 614, display clause only. `_lattice_latex` built its signature pair at the top and then chose the invariants line; for a base whose fraction field is not represented as ordered, that first line raised `AssertionError: the signature pair (p, q) needs a chosen ordering ...` (`_lattice.py`, `_ordered_fraction_field`) before the branch that would have omitted it. The display now computes the signature only when the fraction field is the rational field — the ordering the library represents — and otherwise shows rank, discriminant and the Gram matrix, inventing no ordering. `signature_pair()` itself still requires one, and the rational display is unchanged.

Reproduction: the issue's specimen is cells 13, 16 and 20 of `computations/notebooks/lattices/integral-lattices/preamble-lattices.ipynb` — a rank-two lattice over `QuadraticField(2, "a")`, over its maximal order, and over `QuadraticField(-1, "i").maximal_order()`. Those three cells cannot run here: `QuadraticField(2, "a")` itself fails during construction, before any display, when its repr is hashed for a cache key —

```text
File ".../categories/rings/number_fields.py", line 344, in QuadraticField
File ".../categories/rings/ring_foundation.py", line 5551, in __hash__
File ".../categories/rings/ring_foundation.py", line 6059, in _repr_
    f"{self.defining_polynomial()}"
AttributeError: '_OwnedAlgebraParent_with_category' object has no attribute 'defining_polynomial'
```

— that is, `_preamble_is_number_field()` answers true for the algebra wrapper while the category that defines `defining_polynomial` is not in its placement. It is present unchanged at `d58660c`, so it is not a consequence of any change recorded here, and it is a different clause of the issue (a number-field construction/placement defect, not the display of a lattice), so it was not repaired here.

The display clause was therefore reproduced on a lattice over `GF(5)`, whose fraction field is likewise not ordered, where it raised the identical assertion: `tests/lattices/test_lattice_display_without_ordering.sage` (3 cases; the display case fails at `d58660c` with the reported message, the ordering requirement and the rational display pass there unchanged). The three notebook cells remain blocked on the number-field defect above, not on the display.

### A number field could not be constructed: its own hash formatted it before its placement existed

`QuadraticField(2, "a")` failed during construction, so the three number-field specimens of research issue 614 could not even be built:

```text
number_fields.py:344 QuadraticField → :151 _number_field_of
algebras.py:4879 _OwnedAlgebraParent.__init__ → ring_foundation.py:5797 __init__
ring_foundation.py:6660 _install_self_module_placement → modules.py:303 __classcall__
ring_foundation.py:5551 __hash__ → :6059 _repr_  f"{self.defining_polynomial()}"
AttributeError: '_OwnedAlgebraParent_with_category' object has no attribute 'defining_polynomial'
```

The ring installs its self-module membership at the end of `Parent.__init__`, which hashes the ring; `CategoryObject.__hash__` formats it; the number-field branch of `_repr_` reads `defining_polynomial`; and that method arrives with `_number_field_placements`, which the algebra constructor installs only *after* the first initialization by design ("install the complete stated placement only after the selected resolution and native module datum are available"). So the ring formatted itself through a placement it did not yet have.

The owning repair is in the ring's identity contract, where the same recursion was already handled for orders: `__hash__` returns `id(self)` for number fields as well as for orders. Owned parents are identity-bearing, so this agrees with their identity equality, and it removes nothing: the repr, the predicates and the placement are untouched. `tests/rings/test_number_field_construction_and_display.sage` states it — the field constructs, `defining_polynomial()` answers `a^2 - 2`, the generator squares to 2, the field is in `OwnedNumberFields()`, and it hashes — and then runs the three original specimens (over `QQ(sqrt 2)`, over its maximal order, over `Z[i]`'s maximal order) through `repr` and `latex`, with the ordering guard still refusing `signature_pair()` on each.

Bounded regression over the five number-field test files: `test_embeddings_of_quadratic_fields`, `test_number_field_archive`, `test_number_field_arithmetic_archive`, `test_number_field_base_change_archive`, `test_ideal_extension_and_contraction` — **15 failed / 3 passed before, 9 failed / 9 passed after, no test newly failing**.

Residual, recorded and not repaired: a number field still displays as `Free module on {1, a} over Fraction Field of Integer Ring` rather than the "Number field defined by a^2 - 2" that `_number_field_of` sets, because its regular-module presentation overrides the ring display. That is a display-text defect of the ring, not the construction blocker and not the lattice clause.

### Number-field identity hashing, verified; and a proposition cannot be coerced by `in`

**Identity hashing is justified by the measured contract, not assumed.** `QuadraticField(2, "a")` twice returns the same object (`_number_field_of` is cached on the polynomial), equal and equal-hashed; a *renamed* construction `QuadraticField(2, "b")` is a distinct object (the polynomial lives in `QQ[b]`, a different ring, so a different cache key), it compares **unequal**, and its hash differs; `QuadraticField(8, "c")` likewise. Across `(K, K)`, `(K, renamed)`, `(K, QQ(√8))`, `(K, QQ)`, `(K, ZZ)`, "equal" held exactly when "identical", so equal-implies-equal-hash holds for identity hashing and no equal pair is split by it. The residual is a *uniqueness* question, not a hashing one: two names give two owned fields for the same abstract field, which is the identity-bearing convention this library states for parents, and `OWN-02`'s "one object for `f`" is read per polynomial object rather than per abstract field.

**Triage of the nine remaining number-field failures**, by exact assertion: two are `TypeError: the proposition is_parent_of(...) has no Python truth value` (conjugation restricted to an order; base-change functor on a nonidentity order map); two are `AssertionError: the rank of Free module on {1, a} over QQ ... is computed over a finite field for a finite module, or from a chosen basis or presentation` (element multiplication endomorphism; order tensored with QQ); one `KeyError: 'index_in'` (index of a non-maximal order); one `RecursionError` in a principal quotient; one `assert Order of rank 2 ... in Category of ... principal ideals ...` (the class-number-one specimen); one `AttributeError: ... has no attribute 'embeddings'` (Frobenius); one `assert -1 == -1` (norm-minus-one unit).

The first one is a plain coercion bug at an owner boundary: membership in an owned ring is a **proposition**, and `x in ring` makes Python call `bool()` on it before anything can ask, so `algebras._element_constructor_` raised on `value in ring` and `OrderEmbedding` raised on `image not in codomain`. Both sites now read the predicate and decide it with `ask(...)`, the library's own idiom; an undecided answer does not take the branch.

That repair does not close its test: with the coercion fixed, `integers.Mor(integers)(conjugation)` proceeds and recurses, `scalar_multiple → _ring_morphism_defining_module_action → elementwise ring morphism → algebras._element_constructor_ (unit branch) → unit_morphism → scalar action → ...`, 1003 frames. The five number-field files are unchanged at 9 failed / 9 passed, so this is recorded as the next unit rather than claimed as a repair of the specimen: the unit-morphism branch fires for an order element read inside the coefficient field and cycles through the order's scalar action.

### The restricted-conjugation recursion is a knot, not an ingress bug: what four layers of it showed

`integers.Mor(integers)(conjugation)` for `QQ(sqrt 5)` now passes the two membership repairs and then recurses, 1003 frames. Traversed in order, each repair moved the failure one layer and closed nothing:

1. `algebras._element_constructor_` and `OrderEmbedding.__init__` coerced a membership proposition with `in` — repaired (`ask(...)`), published at `fdd9bb3`;
2. the coordinate element re-entered `algebras._element_constructor_` with `source is self`, so an identity ingress was added — the cycle simply moved to
3. `modules.scalar_multiple → scalar_action → _ring_morphism_defining_module_action`, the construction of `rho_M : R -> End(U(M))`; preferring the retained native scalar operation moved it again to
4. `native_modules.scalar_multiple → _native_scalar_action → _lmul_ → ring __call__ → algebras._element_constructor_ → set_categories.__call__ → algebras.py:641 <lambda> → modules.scalar_multiple`: element construction calls the algebra structure morphism `r |-> rho(r)(1)`, which calls the scalar action, which constructs an element again.

That last loop is the actual defect: element construction, the structure morphism and the scalar action are mutually recursive for a ring that is a module over its prime ring, and breaking it is a structural change to the algebra construction, not an ingress repair. Layers 2 and 3 were tried, moved the exception without closing it, and were reverted rather than published as progress; the tree at `fdd9bb3` carries only layer 1, which is a genuine bug fix but does not close the specimen. The five number-field files remain 9 failed / 9 passed, and the conjugation case is **not** accepted.

The next owner task is that knot. A repair should make the algebra structure morphism and the module scalar action read one retained datum instead of constructing each other.

### The scalar-action cycle is repaired at its primitive boundary, and three specimens close

The knot diagnosed in the previous entry is repaired where the contract already said it should be. `_OwnedRingElement._lmul_` documents that "the engine presents this ring over its base, so `r` enters through the engine's map from its base and multiplies `a` there", but its body was `parent(parent.base_ring()(scalar)) * self`: it constructed `r * 1` through the unital scalar constructor, whose structure map is defined from the module action, which constructs an element again. `_lmul_` now evaluates the engine's base action directly (`self._backend() * _engine_element(parent.base_ring(), scalar)`), so the native presentation's product/unit/scalar-action datum precedes the algebra classifier instead of depending on it. `_native_scalar_action` delegates to that and needed no change; no ingress special case and no unit-morphism bypass was added, and `unit_morphism` still answers the same morphism for its callers.

Two adjacent defects in the same acceptance then had to be stated rather than patched: the order embedding's linear map is the composite of the two order inclusions with the field embedding, which is linear and injective *by its factors*, so `OrderEmbedding` now records the construction's linearity (`_from_constructed_element_map(..., premises=())`, the library's "linear by this construction" idiom) and retains `_injectivity_premise = True`, which `is_injective()` reads instead of asking for a kernel algorithm these modules do not supply.

Evidence, ten files over the ring chain (embeddings, number-field archives, base change, ideal extension, elementary arithmetic, rational placement, commutative algebra, module products, lattice display) compared at `ef3c900` and after: **31 failed / 35 passed → 28 failed / 38 passed, no test newly failing**, and three newly passing — the focused `test_conjugation_restricts_to_the_ring_of_integers`, `test_maximal_order_principal_quotient_has_the_norm_cardinality` (formerly the RecursionError), and `test_number_field_base_change_functor_acts_on_a_nonidentity_order_map` (formerly the proposition truthiness error). `tests/rings/test_order_conjugation_restriction.sage` pins the scalar boundary against repeated addition and the restricted conjugation's ring equations.

Queue after this dependency: the PID placement assertion (`test_maximal_order_is_a_pid_exactly_in_the_class_number_one_specimen`) and the norm-minus-one unit assertion (`test_one_plus_root_two_is_a_unit_of_norm_minus_one_with_inverse_root_two_minus_one`), then the `index_in` and `embeddings` gaps.

### PID placement from the exact class number, and a localization equality that refused its own elements

Two assertions from the recorded queue, repaired at their owners.

**PID placement.** A maximal order is a principal ideal domain exactly when its field has class number one (Neukirch I.6: the ideal class group is the Picard group), yet `_order_placements` said outright that "no class-number computation participates in this placement", so `O in PrincipalIdealDomains()` was `False` for the Gaussian integers.  `_order_in` now takes that exact owned decision once, `field.class_number() == 1`, and places the order in `OwnedPrincipalIdealDomains()` only when it holds — and only for the integral closure, since `h = 1` alone does not make a non-maximal order a PID.  The negative case is preserved: `QQ(sqrt -5)`, class number 2, stays unplaced.

**Localization equality.** `test_one_plus_root_two_is_a_unit_of_norm_minus_one...` failed on `assert -1 == -1`: the norm was arithmetically right and the comparison was a representation mismatch.  The owned rational field's `equality_status` realized only Python `int`/`Fraction` operands and returned `False` for anything carrying a Sage `Parent` — including the preparsed literals of a `.sage` file and elements of its own subring `ZZ`.  It now realizes the other operand through the localization's own construction, which admits it exactly when its denominator is admitted: a rational outside a proper localization is still refused.  Measured after: `QQ(-1) == ZZ(-1)`, `QQ(-1) == Sage(-1)` and `QQ(1) == Sage(1)` are all true; a non-integral Sage literal (`QQ(1/2) == Sage(1/2)`) is still false, which is a separate coercion gap in that boundary and is recorded rather than papered over.

Evidence over the same ten ring-chain files: 28 failed / 38 passed before this pair, 25 failed / 41 passed after, none newly failing, three newly passing — the PID assertion, the norm-minus-one unit, and `test_x_squared_minus_two_is_irreducible_over_the_rationals`, which the equality repair also released.  Queue after this: `index_in` (the non-maximal order's index), then `embeddings`, then the rank-of-module assertion that still blocks the multiplication endomorphism.

### An order's index, and the field hom-set's embeddings, were on the wrong owners

Two more from the queue, both pure owner gaps rather than arithmetic.

`index_in`. `[O_K : ZZ[sqrt 5]] = 2` (Neukirch I.2.10) was unanswerable: the order carried no `index_in`, although both orders retain their integral bases and the retained realizations answer the change-of-basis determinant exactly. `OrdersWithChosenIntegralBasis` now states it — the two endpoints must both carry an integral basis and lie in one number field, and the answer is the owned integer the engine computes.

`embeddings`. `GF(4).Mor(GF(4)).embeddings()` raised `AttributeError`, because `Mor(K, K)` for a field *is* the graded algebra Mor, which is the stronger structure, while `embeddings` was defined only on the ring Mor. The algebra Mor now delegates to that one owner when its endpoints are fields — a ring map between fields is injective, so the enumeration is the ring `Mor`'s, and no second enumeration was written.

Ten ring-chain files: 25 failed / 41 passed before this pair, 23 failed / 43 passed after, none newly failing, the two specimens newly passing. Queue after this: the rank-of-module assertion, which is the last block on the multiplication endomorphism and the order-tensored-with-QQ specimens, then the non-integral literal coercion gap in the rational field's equality boundary.

### An algebra arrow is linear, not merely injective; and the rank, reflection and rational-literal owners behind that queue

Four owner repairs, the first of which corrects the previous entry's own reasoning.

**The field hom-set's embeddings.** The previous entry delegated `embeddings` on the algebra Mor to the ring Mor because "a ring map between fields is injective, so there is one enumeration". Injectivity is not \(R\)-linearity. An arrow of a Mor of algebras over \(R\) is \(R\)-linear, hence satisfies \(f \circ \rho_A = \rho_B\), and that square is the whole of the extra condition: for multiplicative \(f\), \(R\)-linearity at \(a = 1\) is the square, and the square with multiplicativity gives it back for every \(a\). `embeddings` now keeps exactly the ring embeddings whose square with the retained structure maps commutes, decided as an equality of ring arrows \(R \to B\) — not sampled on generators, which was the first draft and is wrong for a base ring that is not generated by the probes one guesses.

The reachable instances are the ones that expose the difference. `GF(4)` is presented as `F_2[z_2]/(z_2^2 + z_2 + 1)`, so its recorded algebra base ring is `F_2[z_2]` and its structure map is the quotient map: `rho(z_2)` is the class of `z_2`, which generates the field, so only the identity fixes it. Frobenius — a ring automorphism, the test's original subject — sends that class to `z_2 + 1` and fails the square. `GF(8)` behaves the same way (3 ring automorphisms, 1 algebra endomorphism). The K-over-K specimen the owner named is not constructible yet: `QQ(sqrt 5)` is not an object of `Algebras(QQ(sqrt 5))`, so no algebra Mor over a field base exists; these presented fields are the same phenomenon, a structure map whose image generates the algebra. Each survivor is an arrow of the algebra Mor by its elementwise action, retaining the square and the ring map's own multiplicativity as the construction's equations, and no linearity is claimed beyond them; a survivor that is the identity ring map is returned as `identity()`, whose laws the Mor already states.

The GF(4) expectation of 2 was not a wrong answer, only a wrong hom-set: it is the ring Mor's answer, and it is kept there. `tests/rings/test_embeddings_of_quadratic_fields.sage` now asserts both counts, plus the Frobenius action on the structure-bearing element and the failure of its square, and adds the `GF(8)` instance: 5 passing → 7.

**A framed free algebra states its rank.** `module_rank` of `QQ(sqrt 5)` over `QQ` asserted: it is computed over a finite field for a finite module, or from a chosen basis or presentation, and the module supplied none of these. The presentation *is* retained — the object is `Free module on {1, a} over QQ`, framed free, `module_generating_set()` of cardinality 2 — but on an algebra's class `Modules.ParentMethods` precedes every specific module category in the MRO (measured: positions 20 against 21, 22 and 23), so the generic rank never reached the framed-free `module_rank` or the presentation `_rank_decision`. As with the earlier `_cardinality_decision` repairs, the realization supplies the hook instead: `_OwnedAlgebraParent._rank_decision` answers the frame's cardinality when the algebra is framed free and leaves the generic cases otherwise. `test_number_field_element_retains_its_multiplication_endomorphism` passes; `test_root_five_order_tensored_with_the_rationals_is_the_number_field` moves past `module_rank` to a different, unowned operation — rings have no `is_isomorphic` at all (the implementations are form-module, scheme and fan ones) — so that specimen is **not** closed and is recorded as the next owner rather than counted.

**Reflection is a function of the rational line.** `reflection(e - f)` on `U` worked while `reflection(2(e - f))` was refused "because `2 b(x,r)/b(r,r)` is not in `ZZ`": for \(r = 2a\) with \(a^2 = -2\) the coefficients are half-integral although the images are the same integers, since \(s_{\lambda r} = s_r\). The coefficients belong to the representative; the isometry belongs to the line. For a lattice over `ZZ` the reflection now reads the line's primitive vector (`primitive_part()`) and asks the same integrality question there, so `2(e-f)`, `3(e-f)` and `e-f` all give the swap, while a line with no integral reflection vector (`2e + f` on `U`) is still refused. `is_integral_reflection_vector` keeps its meaning (the coefficients of the representative it is given) and its docstring no longer claims to decide lattice preservation for non-primitive vectors, which was the mismatch. `tests/lattices/test_reflection_rational_line.sage` pins the four cases.

**A raw Sage rational denotes its own fraction.** `QQ(1/2) == 1/2` was false because the localization's `_element_constructor_` read an element of Sage's rational field through the *source* ring, where `ZZ(1/2)` is `1`: the value denoted a different element, and both sides of the comparison were then wrong in the same way. The constructor now splits such a value into its own numerator and denominator and admits the denominator through the selected submonoid, so `QQ(1/2)` is `1/2` and `ZZ[1/2](1/3)` is still refused. The reverse comparison (`1/2 == QQ(1/2)`) remains `False` and is Sage's answer, not this boundary's: Sage's own rational field does not admit a session element. `tests/rings/test_localizations_of_the_integers.sage` 8 passing → 9.

Evidence. Thirty-one files whose subjects call `module_rank` (rings, algebras, modules, objects), compared at `f7db965` and after: identical failed/passed counts on thirty of them, and `tests/rings/test_number_field_archive.sage` 1 failed / 2 passed → 3 passed. Thirteen ring-chain files: identical counts, none newly failing. `tests/rings/test_embeddings_of_quadratic_fields.sage` 5 → 7 passing. Reflection set, compared cleanly per file at `f7db965` and after — 15 files, **every existing file identical**: `test_definite` 13 failed / 12 passed on both, `test_reflection_hyperbolic` 4 failed / 1 passing on both (its four failures are the missing `edgewalk_is_reflective`), `test_cyclotomic_centralizer` 7 passing on both, `test_orthogonal_reduction_sequences` 7 failed / 9 passing on both, and the one difference is the new `tests/lattices/test_reflection_rational_line.sage`, 4 passing. So the reflection repair changed no existing file's outcome, and its evidence is that file and its specimens, not a movement in the suite. **Correction:** an earlier draft of this entry reported `test_definite` as 14 failed / 11 passed before and 13 failed / 12 passed after — two regression runs started concurrently shared one temp file, so each read the other's tail; that table was contaminated and is withdrawn. Timings on this run are **not** idle-VM measurements: other projects' jobs held the machine throughout, which is why the same file took 279 s in one run and 932 s in the other.


Queue after this: (1) `dual_module()` points share one hash — the port-blocking defect, next; (2) a ring-level `is_isomorphic` owner for the order-tensored-with-QQ specimen; (3) `ZZ[1/2](QQ(1)/QQ(3))` raises `TypeError` from the source-ring conversion where it should raise the localization's own refusal.

### A point of a dual module hashed by its parent, so `finite_ordered_set` was quadratic there

The port reported this against `7b222e8` (`sage-indefinite-port` @ `9152a7db`, `.tmp/provider-report-dual-point-hash.md`) as the block on cone construction: 570 covectors did not finish `finite_ordered_set` in 560 s, and `RationalPolyhedralCone.__init__` inherited it. Reproduced here on the library as reported: the points of `Lattices(ZZ)(identity_matrix(6)).dual_module()` — which is the Mor `Hom_R(M, R)`, so a point of it is an arrow — all hashed alike, 1 distinct hash for 64 distinct points, because both arrow classes hashed their *parent* (`hash(id(self.parent()))`) or their endpoint pair. `_on_points` is `tuple(dict.fromkeys(supplied))`, so every insertion compared the new point with every extant key by extensional arrow equality, ~17 ms each.

The repair is one owner for both arrow classes: `arrow_hash` in `set_categories.py`, used by `OwnedSetMorphism.__hash__` and `ModuleMorphismMethods.__hash__`. It hashes the arrow's values on one canonical finite probe of the *domain* — the domain's chosen module generating set when it has a finite one, otherwise its elements when it is a finite enumerated set, at most 8 of them from the front of the canonical order — and falls back to the endpoints when there is no such family. Values, not presentation, because equality is extensional: a map given by generator images, the same map built as a difference, and the same map with the zero added all read the same values and so hash alike, which the regression test asserts directly. The probe is a property of the domain alone and both classes read the same rule, so a set map and a module map with the same endpoints are no longer hashed by different formulas. An unevaluable or unhashable probe leaves the endpoint hash in force rather than raising; an infinite frame (`ZZ[x]`) has no probe and keeps the endpoint hash.

Measured on the current tree (`I6`'s dual, coordinate boxes):

| family | before | after |
| --- | --- | --- |
| 64 distinct dual points, distinct hashes | 1 | 64 |
| `dict.fromkeys`, 64 dual points | 22.9 s (report) | 0.163 s |
| `finite_ordered_set`, 64 dual points | 49.8 s (report, larger family) | 0.385 s |
| 570 distinct dual covectors, distinct hashes | 1 | 570 |
| `finite_ordered_set`, 570 dual covectors | not finished in 560 s, ≈1800 s extrapolated | 4.22 s |
| `_rational_polyhedral_cone(lattice, 570 covectors)` | not finished in 779 s (report) | 7.09 s |
| 570 primal points, `finite_ordered_set` | 0.01 s | 0.01 s |

The residual seconds are the per-point evaluation the probe reads (≈6 values of ≈1 ms each); the quadratic term is gone, and the primal side that already worked is untouched. These are **not** idle-VM numbers: other projects' pytest runs held the machine during them, so they are indicative, while the distinct-hash counts — the load-independent part of the claim — are exact.

`tests/modules/test_dual_point_hash.sage` (6 tests) pins the contract without timing it: 64 distinct dual points give 64 distinct hashes; `finite_ordered_set` returns the same 64; equal points share a hash across presentations (`e*` rebuilt as `2e* - e*`, and `e* + 0`); the zero and the scalars keep distinct hashes; the primal family keeps its distribution; and an infinite frame falls back to the endpoint hash instead of trying to read an infinite probe.

Queue after this: a ring-level `is_isomorphic` for the order-tensored-with-QQ specimen, and `ZZ[1/2](QQ(1)/QQ(3))` raising the source-ring `TypeError` where the localization's own refusal belongs.

#### Evidence for the arrow hash, complete

The modules/sets sweep finished: `tests/modules` and `tests/sets`, 95 files, one pytest per file, compared at `f7db965` and at `69907ae`. Per-file failed/passed counts are identical on 94 of them (176 failed / 222 passed before, 176 failed / 228 passed after) and the one difference is the new `test_dual_point_hash.sage`, 0 → 6 passing. No test in that sweep newly fails, and no test there other than the new file changes state.

#### The probe's bound was on the slice, not on the read

`arrow_probe` documented "at most eight points" and then wrote `tuple(generating_set)[:8]` and `tuple(domain)[:8]`: it materialized an arbitrarily large finite family before slicing, so one hash cost the whole domain whenever the domain was finite and big — a million-element finite set, or a frame with a thousand labels, paid a million or a thousand reads per insertion. The bound was on what the *slice* kept, not what the probe read.

Both branches now read their prefix through `_probe_prefix`, which is `tuple(islice(family, 8))`: the read stops at the bound, and the finiteness predicates (`is_finite()` for a frame, `is_provably_finite` with `EnumeratedSets()` for a domain) are the same ones as before. Reading lazily also removes the hang risk a family that is finite only by its own claim used to carry. Equality still implies equality of hash, because both branches read the same canonical prefix of the same domain through the same function.

`test_the_probe_reads_at_most_eight_elements_of_a_finite_family` proves the bound instead of timing it: a family whose iterable raises when a ninth element is requested and counts every read, asked through `_probe_prefix` and through `arrow_probe` on a framed domain of ten thousand labels — eight reads in both, and the framing accessor is asked for exactly eight generators. Materializing first fails that test rather than slowing it. The dual-side acceptance is unchanged after the change: 64 distinct points give 64 distinct hashes with `dict.fromkeys` at 0.145 s, and the owned cone from 570 halfspace covectors returns in 5.10 s.

### Two fields are isomorphic when their realizations say so, and not otherwise

`test_root_five_order_tensored_with_the_rationals_is_the_number_field` ended on `extended.is_isomorphic(field.as_algebra())`, an operation no ring level owned — `is_isomorphic` existed for torsion forms, schemes and fans, and for groups under `is_isomorphic_to` — so the last assertion of that spec could not be asked. The two operands are the same field in two presentations: the order's base change to `QQ` and the field "as an algebra", whose defining polynomials are what a presentation comparison would refuse.

`OwnedRings.ParentMethods.is_isomorphic` now decides it, `is_isomorphic_to` aliased. The decision is what the operands state and never an inference from shared invariants: being a field is isomorphism-invariant, so a field and a ring decided not to be one are not isomorphic; characteristic and cardinality refute; two number fields are decided by the realizations they already retain (Sage's number-field test), which is what separates `Q(sqrt 5)` from `Q(sqrt 20)` — isomorphic, same degree, different defining polynomial — from `Q(sqrt 2)` — same degree and characteristic, not isomorphic. Everything else states the proposition: `QQ` against `Q(sqrt 5)` is undecided here rather than `False`, because `QQ`'s retained realization is not a number field, and answering `False` would assert a theorem about all fields that this owner has not established.

`tests/rings/test_field_isomorphism_decisions.sage` (8 tests) pins all of it: the order-tensored-with-`QQ` specimen in both directions, one field in two presentations, same degree and characteristic yet non-isomorphic, a field against `ZZ`, finite fields refuted by characteristic and by cardinality, the undecided pair as a proposition, the non-ring operand refused, and the alias.

Two things worth recording for whoever touches this next.

**Placement.** Declaring the method on `Division.Commutative.ParentMethods` — the fields category, where it belongs mathematically — left `QuadraticField(5)` without the attribute: the class attached to that category is a synthesized `ParentMethods` carrying number-field methods with only `object` as a base, and the method never reached an object's class. The same body on `OwnedRings.ParentMethods` is reached by `QuadraticField(5)`, `extended` and `QQ` at once, so it is there, gated to fields. The mechanism was not investigated further; the observation is what a reader needs, since the "obvious" owner silently does nothing.

**Evidence.** Targeted set: the pinned spec's file 1 failed / 2 passed → 3 passed, and the new file 8 passing. `test_number_field_archive_reconciliation.sage` keeps its 2 pre-existing failures at `f7db965` and after; `test_quadratic_and_cyclotomic_field_invariants.sage` its 3; `test_fraction_field_localization.sage` its 2; `test_localizations_of_the_integers.sage` 9 passing and `test_embeddings_of_quadratic_fields.sage` 7 passing, both unchanged. Queue after this: `ZZ[1/2](QQ(1)/QQ(3))` raising the source-ring `TypeError` where the localization's own refusal belongs.

### A localization refuses a denominator it does not invert, and reads a value, not its stated presentation

`ZZ[1/2](QQ(1)/QQ(3))` raised `TypeError: no conversion of this rational to integer` from the *source* ring: the constructor sent an element of an owned field down `source(value)`, i.e. through `ZZ`, where the rational has no image. Two owners were confused — the conversion error named `ZZ` for a decision the localization owns. `_element_constructor_` now splits any value carrying a numerator and denominator whose parts read into the source, whether the value belongs to Sage's own field or to an owned one, and admits the denominator through the selected submonoid: `ZZ[1/2](QQ(1)/QQ(2))` is `fraction(1, 2)` and `ZZ[1/2](QQ(1)/QQ(3))` raises the localization's own refusal.

Writing that test surfaced the adjacent defect, which is the one worth keeping: an owned element of a fraction field retains the numerator and denominator it was *given*, so `QQ(6)/QQ(3)` is `(6)/(3)` and its stated denominator, `3`, is not inverted by `ZZ[1/2]` — the constructor refused a value that belongs to the ring. Membership is decided by the value, not by its presentation: `(3):(6) = (1)` meets the inverted set. `_fraction_denotations` therefore yields the retained realization's *reduced* pair first (`QQ(6)/QQ(3)` is `2`) and the stated pair as the fallback, so the value decides and the admitted form is constructed. A value with no fraction-field realization, or without numerator and denominator, contributes only what it states, which is the previous behaviour.

`tests/rings/test_localizations_of_the_integers.sage` 9 → 10 passing: admitted halves and quarters, an integral value, the unreduced `6/3`, and the refused third. Targeted neighbours keep exactly their pre-existing failures, checked per file at `f7db965`: `test_fraction_field_localization.sage` 2 (the recursion in the maximal-adic datum, and `VectorSpaces(QQ)` refusing the owned rational field as a base), `test_localization_restrictions.sage` 1, `test_localized_fraction_equality_from_the_presentation.sage` 3 — identical before and after — while `test_rational_field_placement.sage` (5), `test_field_isomorphism_decisions.sage` (8) and `test_number_field_archive.sage` (3) pass.

#### The five Sterk diagrams' maximal affine unions, measured

The Type II inventory is recorded above as a count; here is the decomposition the count comes from, so a consumer's condition can be checked against data rather than guessed at. Every maximal affine union on the five diagrams, with its connected components (all components affine, so `is_componentwise_affine()` holds and `is_parabolic_union()` reports the at-least-two meaning):

| diagram | unions | component ranks |
| --- | --- | --- |
| `Sterk_1` | 3 | (8, 2), (8, 2), (8, 2) |
| `Sterk_2` | 0 | — |
| `Sterk_3` | 3 | (7, 3), (7, 3), (8, 2) |
| `Sterk_4` | 1 | (5, 5) |
| `Sterk_5` | 9 | (8, 2), (7, 3), (5, 5), (7, 3), (7, 3), (5, 5), (7, 3), (4, 4, 3), (4, 4, 3) |

Sixteen in total, and the two of rank eleven are exactly the two whose components are three rather than two. The filters give 16 for "any union", 14 for "exactly two components", 2 for "three components", and four distinct component-rank shapes `(8,2)`, `(7,3)`, `(5,5)`, `(4,4,3)`. None of those is five, so a consumer's "five Type II cases" is not any of these conditions, and it is not the library's count under a different reading of the same partition: the distinguishing condition is the consumer's to state. Nothing here needs a new owner method — `connected_component_vertex_sets()`, `is_componentwise_affine()`, `is_parabolic_union()` and `is_parabolic()` compose to every one of those filters already.

The archive test that compares the recorded type multiset is green after the later Coxeter edits: `tests/lattices/test_sterk_elliptic_population_archive.sage` 3 passing in 41 s, so the `Counter`-multiset comparison recorded earlier still holds.

### The prime localization's fraction field, and the circle its field decision closed

`test_the_fraction_field_of_a_prime_localization_of_the_integers_is_the_rationals` died in `RecursionError` at `construction.maximal_ideal()`. The cycle was exact and is worth writing down, because every step is individually correct:

1. placing a module asks whether its coefficient ring is a field — `_finitely_generated_free_placement` tests `ring in OwnedFields()`;
2. the field decision of a local ring asks whether its maximal ideal is zero — `_field_decision` reads `construction.maximal_ideal()`;
3. that ideal for a prime localization is the extension `p R_p`, built by `prime.extension_to_localization(self)`;
4. the extension is a localized ideal, which needs `localization_ring.regular_module()`;
5. a regular module is `self.free_module(1)`, which is placed as a module — back to step 1.

`R_(p)` is local, so its fieldhood is the single question "is `p R_p` zero", and the construction knows it without building the ideal: `p R_p = 0` exactly when `p` lies in the kernel of `R -> R_p`, which is asked generator by generator in the localization, whose equality is decided there. `LocalRingConstruction` now accepts that decision (`maximal_ideal_is_zero`, or a factory), and `_field_decision` reads it first and returns it when stated; a construction that states nothing leaves the previous ideal route in force, so nothing else moves. The prime localization supplies it from its own datum, so the circle stays open at step 2 and steps 3–5 are never the price of asking whether `R_p` is a field.

The test is the general one rather than the domain special case: with nilpotents `p R_p` can vanish while `p` does not, as for `ZZ/6` at `(2)`, where `3 * 2 = 0` with `3` outside `p`. That instance is deliberately **not** claimed: the localization of a quotient has its own `zero()` cycle through `quotient_source()`, which fails before this decision is reached, and it is recorded below rather than papered over.

Evidence, per file at `f7db965` and after. `test_commutative_algebra.sage` and `test_fraction_field_localization.sage` together: **19 failed / 11 passed → 18 failed / 12 passed**, the single movement being the recursion test, with the other eighteen unchanged; the remaining `test_fraction_field_localization` failure is `VectorSpaces(QQ)` refusing the owned rational field as a base, which is Sage's category and unrelated. `test_localizations_of_the_integers.sage` 10 passing, `test_rational_field_placement.sage` 5, `test_prime_and_maximal_ideals.py` passing, `test_localization_restrictions.sage` 1 pre-existing failure, all unchanged. Directly after the fix, `ZZ_(3)`: `is_field()` is `False` (was `RecursionError`), `maximal_ideal()` is non-zero, `residue_field()` is `ZZ/(3)`, `fraction_field_map()` sends `1/2` to `1/2`, and `fraction_field()` is `QQ`; `ZZ_(0)` reports `is_field()` `True`, which is right because localizing at the zero prime is the fraction field.

Queue after this: the localization of a quotient, whose `zero()` re-enters through `quotient_source()` — `ZZ/6` at `(2)` does not get as far as its own field decision.

### A field decision may not be asked through element equality

The previous entry closed the *domain* case of the prime-localization field decision by stating `p R_p = 0` at the construction — but it stated it as `self.fraction(g) == self.zero()`, which is element equality in the localization. Over a quotient that is the wrong question to ask, and the 1111-frame cycle shows why: `_finitely_generated_free_placement → OwnedFields() membership → _field_decision → maximal_ideal_is_zero → element equality → _fraction_equality_status →` the localization functor on the **regular module** `→ free_module → placement →` back to the membership test. Equality of fractions over a non-domain source is decided by localizing the regular module, and a free module's placement asks whether its coefficient ring is a field. Asking fieldhood through equality therefore closes the circle one turn later, with the same radius.

The decision is now made in the source ring, where the criterion lives: `g/1 = 0` in `S^{-1}R` exactly when some `s ∈ S = R \ p` kills `g`, that is when the annihilator `(0 : (g))` is not contained in `p`. Both sides are ideals of `R`, so it costs `colon` (which this ideal owner already has), the prime's membership predicate on the annihilator's generators, and nothing else — no element of the localization is constructed, and no regular module is built. Per-generator answers are combined with `conjunction`, so an undecided killer membership stays a proposition instead of becoming `False`.

Both cases now behave, over the domain and over the quotient:

| ring | `is_field()` | `maximal_ideal().is_zero()` |
| --- | --- | --- |
| `ZZ_(3)` | `False` | `False` |
| `ZZ_(0)` | `True` | `True` (zero generators) |
| `(ZZ/6)_(2)` | `True` | `True` |

`(ZZ/6)_(2)` is the case that separates the general criterion from the domain special case: `(0 : (2)) = (3)` is not contained in `(2)` because `3 · 2 = 0` and `3 ∉ p`, so `p R_p = 0` although `p ≠ 0`, and the localization is `FF_2`. A decision that read `p = 0` would answer `False` there.

`tests/rings/test_prime_localization_field_decisions.sage` pins the three cases and the three-valued combination. Targeted run: that file plus `test_fraction_field_localization.sage`, `test_localizations_of_the_integers.sage`, `test_field_isomorphism_decisions.sage` and `test_prime_and_maximal_ideals.py` — **29 passed, 1 failed**, the failure being the pre-existing `VectorSpaces(QQ)` refusal of the owned rational field as a base. One correction recorded while writing it: `ZZ_(0).fraction_field()` is `ZZ_(0)` itself, not the interned `QQ` — a field's fraction field is itself, and the two are equal fields with different constructions, so the test asserts the former rather than object identity with `QQ`.

### `group_generators` is not where Γ_h's time goes, and the retained family is what it reads

The reported blocker was `target.subgroup_on(tuple(g.discriminant_morphism() for g in group.group_generators()))` spending 300–1680 s, with whole-group enumeration in `group_generators` named as the defect. Measured on the library at the port's own scale, the enumeration does not happen, and the phases separate as follows.

| phase | measurement |
| --- | --- |
| Γ_h build (`_gamma_h`, *outside* the timed line) | 172–201 s over three runs |
| `target = O(A_N)` | 0.00 s (cached from Γ_h) |
| `O(A_N)` engine parent for N, `_engine_orthogonal_group` | 0.06 s (OSCAR) + 0.03 s (`FqfOrthogonalGroup(gens=…)`) + 0.00 s (GAP) |
| `group_generators()` on `O(A_N)`, order 46 998 591 897 600 | 0.26 s, four supplied generators |
| `group_generators()` on a generated subgroup of it | 0.08 s, the same four |
| `subgroup_on(supplied).cardinality()` | 0.01 s, equal to the group's order |
| `Γ_h.selected_group_resolution()` | exceeded the remaining 700 s of a 900 s cap |

So `Finite.ParentMethods.selected_group_resolution`'s canonical `F(U(G))` cover — the whole underlying set, which would cost Γ_h's 696 729 600 elements — is **not** reached by either route a consumer uses: the torsion-form orthogonal group carries the generators its finite-form engine was built from, a generated subgroup carries `selected_subgroup_generators`, and both reported resolutions were already selected before any generator was requested. A rank-4 form's OSCAR cost (31.7 s of 34 s on `U+U`) does not transfer either: at rank 12 with invariants `(2,…,2)` the same call is 0.06 s, so that was OSCAR's behaviour on a particular form, not a scaling law.

Γ_h's cost is in its **retained** datum, materialised: the intersection of a preimage subgroup `ρ_L(g) ∈ K` with the character subgroup `sn_RR(g) = 1` installs `_restricted_character_generating_morphism`, whose Schreier restriction asks the preimage subgroup for *its* generators. That subgroup's generating family is the Eichler/orbit-cover construction, which this library dispatches to the port by design — `eichler_criterion.py:332`, `:351`, `:357` call `OrbitCoverModel.split_generating_family` / `split_covering_vectors` / `split_full_generating_data` — and a run of that path also raised, inside the port, `TypeError: int() argument must be … not 'OwnedJoinCategory.element_class'` at `sage_indefinite_port/indefinite/recursive.py:154` (`int(coordinates(label))`) while `Γ_h.order()` was being computed. Both facts are the port's to act on: its orbit-cover conversion does not accept the owned coordinate elements the library hands it, and its generator search is what the 300–1680 s is spent in.

**What was not done, deliberately.** No substitute generating set, no change to `selected_group_resolution`'s universal construction, and no fast path on `subgroup_on` — the owner's caution, and the measurements give no basis for one.

**What was published instead** is the guard for the route that does work: `tests/groups/test_group_generators_use_the_supplied_family.sage`, four tests, all passing in 60 s. The small specimen (`O(A)` of `U+U`, order 72) states generators equal in number to the engine's supplied ones, checks that they generate the whole group (`subgroup_on(generators).cardinality() == 72`), and checks each one acts as an isometry on the form. A generated subgroup is checked to return exactly the generators it was given. A **fresh** group — the same Gram with explicit module-generator labels is a distinct object, while the same Gram alone is interned — is checked with whole-group iteration poisoned *before* the first generator read, so the assertion covers first materialisation and not a warmed read. The large specimen is **`O(A_N)`**, order 46 998 591 897 600, with `type(group).__iter__` patched to refuse around `group_generators()`, `group_generating_set()` and `group_generator_morphism()`, and its supplied generators confirmed to generate a subgroup of the full order.

Two scope corrections to the numbers above, from readback. First, the large specimen is `O(A_N)`, the orthogonal group of the discriminant form — **not** Γ_h; nothing measured here is about the arithmetic subgroup Γ_h, whose order is not established by anything in this entry. Second, 696 729 600 is the **frozen port test's recorded `group_order` for case 1** — the cardinality of a discriminant-image subgroup in that fixture, as consumed by `test_boundaries.sage` — and is not an established order for Γ_h; no computation of Γ_h's order appears in these measurements. **These tests do not establish Γ_h acceptance.** What they do establish is that `group_generators` reads the supplied family on a fresh finite group without enumerating its underlying set, at both orders above.


### The quotient localization's characteristic, and `(ZZ/6)_(2) = FF_2` exactly

The field decision for a prime localization is now made in the source ring (previous entry). Two things it left open are closed here, and both are the same lesson: a localization's arithmetic is the source's, modulo what the inverted set kills.

**Characteristic.** `characteristic()` was unavailable for `(ZZ/6)_(2)` — the generic method asserts that no computation of the natural-number kernel exists. The naive repair is wrong: delegating to the source answers 6, while the localization's characteristic is 2, because `3 · 2 = 0` and `3` is inverted. `LocalizationRings.ParentMethods.characteristic` now answers the least `n` dividing the source's characteristic whose multiple of one the inverted set kills, decided as `n · 1` vanishing **or** its annihilator `(0 : (n·1))` meeting `S` — ideals and submonoid membership of the source, no element of the localization. An undecided membership returns `None` (the construction does not decide) rather than a wrong value; the first attempt raised on `0 ∈ ⟨2⟩`, whose membership in a finitely generated submonoid is undecided, and that case now stays unknown while the decided ones answer.

**The specimen, exactly**, in `tests/rings/test_prime_localization_field_decisions.sage`:

| assertion | value |
| --- | --- |
| residues `0, 2, 4` of the source | the localization's zero |
| residues `1, 3, 5` | the localization's one |
| `fraction(1, d)` for `d ∈ {1, 3, 5}` | admitted, equal to one |
| `fraction(1, d)` for `d ∈ {2, 4}` | refused with `ValueError` |
| source characteristic / localization characteristic | `6` / **`2`** |
| residue field | a field; `residue_map(1) = 1`, `residue_map(0) = 0`, `residue_map(3) = 1` |
| `is_field()`, `maximal_ideal().is_zero()` | `True`, `True` |

Together the six residues collapsing onto `{0, 1}` with `2` and `4` killed *is* the statement that the localization is `FF_2`; it is asserted as arithmetic rather than inferred from a count.

**One dependency that had to be repaired rather than assumed.** `is_isomorphic` read `characteristic()` and `_engine_ring()` unconditionally, so this field raised two different `AssertionError`s instead of answering. Both reads now leave an invariant the operands do not supply **unknown** — a skipped refutation, never a false decision — and the specimen asserts the shape of that answer: `(ZZ/6)_(2).is_isomorphic(GF(2))` is a proposition, not an exception and not `False`. It is not established as `True` here either, because this ring selects no executable model and its cardinality is undecided; saying so is the point.

Targeted run: `test_prime_localization_field_decisions.sage`, `test_field_isomorphism_decisions.sage`, `test_fraction_field_localization.sage`, `test_localizations_of_the_integers.sage` — **27 passed, 1 failed**, the failure being the pre-existing `VectorSpaces(QQ)` refusal of the owned rational field as a base.

Recorded, not fixed: `cardinality()` of a finite localization is also unavailable (`(ZZ/6)_(2)` supplies no exact value and no decided enumeration), and the residue field's cardinality likewise. That is the next contract in this family.

### A finite localization's cardinality, and the owner I nearly shadowed

`(ZZ/6)_(2).cardinality()` was unavailable — "its construction supplies no exact value or decided finite enumeration" — although the ring is `FF_2`. `LocalizationRings.ParentMethods._cardinality_decision` handled a zero source, and an integral-domain source (where `R -> S^{-1}R` is injective, so `|S^{-1}R| = |R|`), and fell through to `super()` otherwise. A quotient source is exactly the "otherwise".

For a finite source the map is **surjective** — `a/s` is `a · s^{-1}` — so the localization is the quotient of `R` by the ideal of elements that some inverted element kills, and `|S^{-1}R| = |R| / |{a : a/1 = 0}|`. That branch is now in the same owner, counting the killed elements by asking the localization's own equality once per element of the finite source, returning `None` rather than a value when an equality is undecided. `(ZZ/6)_(2)` is 2 (6 killed by 3 elements), `ZZ[1/2]` keeps `ℵ_0`, `QQ[x]`'s fraction field keeps its `ℵ_0`, and `ZZ_(3)` is untouched as an integral-domain source.

**The trap worth recording**: `LocalizationRings.ParentMethods` already had a `_cardinality_decision`, and the first version of this repair *added a second one* to the same class two hundred lines lower. Python takes the last definition, so my new method silently replaced the domain/infinite logic — `test_fraction_fields_of_countable_polynomial_domains_remain_countable` failed immediately. The repair is a branch in the existing owner, not a new method beside it; a duplicate of a hook in one class body is not an override, it is an erasure.

Targeted: `test_prime_localization_field_decisions`, `test_localizations_of_the_integers`, `test_fraction_field_localization`, `test_field_isomorphism_decisions`, `test_cardinality_and_exponent_over_any_pid` — **29 passed, 2 failed**, both pre-existing and unrelated: the `VectorSpaces(QQ)` refusal, and `test_F5t_mod_t_squared_has_25_elements_and_exponent_t_squared` failing at the *previous* commit too with `'Owned_NativeFreeAlgebraParent' object has no attribute 'gen'` (checked by stashing the change and re-running).

Still open, same family: the **residue field** of `(ZZ/6)_(2)` — which is `ZZ/6` modulo `(2)`, a quotient ring, not a localization — still has no cardinality decision, so the owner there is `QuotientRings`. That is the next contract.

### Correction: the localization cardinality branch was announced but not shipped

`d1908c9` claimed the finite-kernel cardinality branch for localizations. It did not contain it: that commit changed `TRAPS.md` and a test, and `LocalizationRings.ParentMethods._cardinality_decision` still had only the zero-source and integral-domain branches, with the non-domain case falling to `super()`. The branch had been lost in a `git stash push` / `pop` round trip used to check whether an unrelated failure pre-existed; the stash was popped, and the pop put back the older copy of the file. **A commit message is not evidence that a branch shipped**: the check is `git show <sha>:<path>` on the remote tree plus a targeted run with a clean working tree, both of which the owner's readback applied and neither of which I had.

The branch is now in `9fd2357` and verified there (`1` occurrence in the committed `ring_foundation.py`, `ZZ/6` with `2` inverted → cardinality 3), together with the quotient branch in the committed `commutative_algebra.py` (`(ZZ/6)/(2)` → 2).

**Three further corrections to `characteristic`, all from readback, all soundness.**

*Meets, not generators.* The scan tested whether individual generators of `(0 : (n·1))` lie in `S`. That is not the annihilator meeting `S`: an ideal can meet `S` through a combination of generators that no single generator witnesses, so "no generator in `S`" was not evidence of "no meeting". It now calls this ring's own `inverted_submonoid_meets(ideal)`, whose contract already distinguishes the prime-complement, the nonzero-elements and the finitely-generated cases (for `S = <f>` it decides `1 ∈ I : f^∞`).

*Minimality under an undecided smaller candidate.* The scan returned the first divisor it saw kill one, even when a smaller divisor had been undecided. That asserts the minimum without establishing it: the undecided smaller candidate might also kill one. An undecided smaller candidate now keeps the answer unknown even when a later one is seen to kill.

*The trivial localization first.* A localization that inverts `0` is the trivial ring, whose characteristic is `1`; the characteristic-zero shortcut is taken only after that, because a characteristic-zero source localized at a set containing zero is not a characteristic-zero ring. The instance is constructible — the zero quotient ring localized at its own one — and is now a regression: `one == zero`, characteristic `1`, cardinality `1`.

**Residue field versus localization versus quotient** stays explicit in `test_the_residue_field_is_a_quotient_with_its_own_cardinality`: the residue field is *not* the localization, its `quotient_source()` is `ZZ/6`, its `defining_ideal()` is `(2)`, its cardinality is `2` decided at the quotient owner from the finite source and the killed ideal (no owned ideal supplies a cardinality of its own), and the maps that identify the three objects are asserted rather than used implicitly: `localization_map: ZZ/6 -> (ZZ/6)_(2)` and `residue_map: (ZZ/6)_(2) -> ZZ/6/(2)`.

Evidence at `9fd2357`, working tree clean and the in-image checkout at the same revision: `test_prime_localization_field_decisions.sage` 8 passed; with `test_localizations_of_the_integers.sage` 18 passed; the wider targeted set 32 passed / 19 failed, of which 17 are `test_commutative_algebra.sage`'s pre-existing seventeen (identical at baseline), one is the `VectorSpaces(QQ)` refusal and one the `F5[t]/t^2` test that fails at the previous commit too.

### `characteristic` over a non-domain, and the generator contract polynomial rings were missing

**Two general defects in the localization characteristic**, both from readback, both soundness rather than coverage.

A characteristic-zero source does **not** give a characteristic-zero localization when the source is not a domain. The shortcut `char R = 0 and 0 ∉ S ⟹ char = 0` is valid only when `R → S^{-1}R` is injective, and injectivity is what a domain supplies. Without it the answer can be positive: localizing `ZZ × FF_2` at the idempotent `(0, 1)` gives `FF_2`, of characteristic 2, and `2 · 1` dies there because `(0,1) · (2,0) = 0`. The shortcut is now taken only for a source in `OwnedIntegralDomains()`, and a characteristic-zero non-domain answers `None` — unknown, not zero. That branch is deliberately not a new algorithm: bounding the natural-number kernel over an arbitrary non-domain would be a different unit.

Second, `one == zero` is three-valued, and reading only `is True` treated an **undecided** triviality as proved non-triviality. An undecided comparison now returns `None` before any scan.

**The char-zero collapse instance is not constructible in this tree**, so the guard is defensive and I am not claiming a regression for it: `ZZ.localization(ZZ(0))` dies in the engine (`factorization of 0 is not defined`), the ring product `OwnedRings().product((ZZ, GF(2)))` builds but refusing an owned tuple as its element (`is not in Category of sets with partial maps`), a predicate submonoid containing zero routes to `_finite_generated_localization`, which demands monoid generators, and `QQ[x]/(x^2)` fails to build at all (`Ideal_1poly_field` has no `syzygy_module`). Two of those four are themselves owner gaps.

**`gen` and `gens` on the free-algebra owner.** `GF(5)["t"].gen()` raised `AttributeError: 'Owned_NativeFreeAlgebraParent_with_category' object has no attribute 'gen'`, although the retained generator contract was there all along: `algebra_generating_set()` names the generators (`{'t'}`) and `algebra_generator(label)` raises a name to the element (`t ↦ t`). `FreeAlgebras.ParentMethods` now states `gen(index=0)` and `gens()` on that datum — a position in the retained ordered family, so `gen()` and `gen(0)` agree on a one-generator ring and `QQ["x,y"]` answers `gen(0) = x`, `gen(1) = y`. No host-Sage accessor is consulted; the element returned is the one this construction selected.

`tests/algebras/test_free_algebra_generators.sage` (4 tests) pins the single-generator case, the multivariate order, that the generator is the construction's own element (`parent() is` the ring, squaring it gives `t²`, and `t² ≠ 0`), and that an out-of-range index is refused.

**Measured, and not closure.** The `F5[t]/(t^2)` specimen no longer dies at `.gen`; it now stops at `module.cardinality() == 25`, with the `AssertionError` that the finitely presented module over `GF(5)[t]` supplies no exact cardinality. That is the next owner gap, and it is a different one — a presented module over a polynomial ring, where the `.gen` failure could not be reached before. In the four algebra files that call `.gen()`, the failing set is **identical** at `117b222` and with this change (8 failed, same names, verified by running both trees), so those tests have moved to a later exception without closing.

### `k[t]/(f)` is `|k|^deg f`, decided from the coefficient field

The `F5[t]/(t^2)` module cardinality was the last piece of that specimen, and it is not a module-theoretic fact but a *ring* one: `QuotientRings._cardinality_decision` had no branch for a quotient of a polynomial ring. The division algorithm in one variable gives the basis `1, t, …, t^(d-1)` of `k[t]/(f)` when `f` is monic of degree `d`, so the cardinal is the **coefficient field's**, raised to the degree — not the polynomial ring's, which is infinite and uninformative.

`_monic_quotient_cardinality` checks every hypothesis before applying it: the source is the free algebra on one generator over a field of decided cardinality, the defining ideal has exactly one generator, that generator's degree is positive, and it is monic, tested as `(f - t^d)` having degree below `d` — ring arithmetic and the degree alone. No engine accessor is consulted. Results: `FF_5[t]/(t²)` 25, `FF_5[t]/(t³+t+1)` 125, `FF_4[t]/(t²)` 16 (the field's base, not 2), `QQ[t]/(t²)` `aleph_0`, and the presented module `F5[t]/(t²)` — the original specimen — 25 with `exponent = t²` and `annihilator = (t²)` unchanged. `tests/modules/test_cardinality_and_exponent_over_any_pid.sage` is untouched and now passes in full.

**One finding that corrects my own test expectation.** Over a field `(2t²) = (t²)`, and the owned ideal *normalizes* its generator: `polynomials.ideal(2·t²)` retains `t²`. So a non-monic presentation never reaches this branch as non-monic, and answering 25 for it is right rather than a leak. The refusal is therefore asserted where the hypotheses genuinely fail — a ring with more than one generator (`QQ[x,y]/(x²)`, where this branch returns `None` while another owner correctly answers `aleph_0`) — and the normalization itself is asserted, rather than a refusal that cannot occur.

**Evidence.** `tests/rings/test_monic_polynomial_quotient_cardinality.sage` (6 tests) plus the original acceptance, the free-algebra generator file and the prime-localization file: 21 passed. Regression over four quotient-heavy files across `117b222` and here: 26 failed / 8 passed → **25 failed / 9 passed**, no new failure and one newly passing — `test_polynomial_prime_localization_has_expected_residue_field` — which the coefficient-field branch released.

### The Hermite-form failure was vocabulary, and the normal form is sound

`test_the_relations_2x_and_4x_have_hermite_form_2x` died on its first two lines, not in the normal form: `F.submodule([...])` and `F / S` raised `AttributeError: ... has no attribute 'submodule'`. This library's names for those are `subobject_on(...)` and the cokernel of the retained inclusion, and neither `submodule` nor `__truediv__` nor `quotient` exists on a module — no `def submodule` appears anywhere in `src/`, while 31 archive call sites still spell it that way and 41 spell `subobject_on`.

Restated at the owner, the Hermite contract holds as Cohen 2.4.2 states it, and the checks are now explicit rather than implied:

| claim | evidence |
| --- | --- |
| the relation span is `2Zx` | the subobject's single generator maps to `2x` under `inclusion()` |
| redundant relations change nothing | `subobject_on([2x, 4x, 6x])` is the same subobject domain |
| reordered relations change nothing | `subobject_on([4x, 2x])` has the same quotient cardinality 2 |
| the quotient map kills the relation and keeps the generator | `cokernel_projection()(2x) = 0`, `cokernel_projection()(x) ≠ 0` |
| the normal form's relation column is `2x` | `relations(gen) = 2 · relations.codomain().module_generator(0)` |
| the normalization is an isomorphism | the returned arrow is a `CategoricalIsomorphism`; there is no `is_isomorphism` predicate to ask |
| the quotient invariant | `M.cardinality() = 2` and `normalized.cardinality() = 2` |

The companion specimen in the same file (`ZZ^2/(2x+4y) = Z/2 ⊕ Z`, Smith form `(2,0)`) had the same two vocabulary failures plus `hermite_form().is_isomorphism()`; restated the same way it passes with torsion cardinality 2, vector-space rank 1, and the invariant-factor form carrying the same torsion.

`tests/modules/test_finitely_presented_module_archive.sage` 2 passed. No library source changed: the normal form, the inclusion, the projection and the quotient invariants were already correct, and adding a `submodule` alias to satisfy a stale spelling would have been a consumer workaround rather than an owner repair.

### A presented algebra was repr'd before it had a presentation

`QQ[x,y]/(x² − y³)` could not be constructed at all: `AttributeError: '_WordFramedPresentedAlgebra_with_category' object has no attribute 'relations'`. The stack is an ordering defect, and every step of it is ordinary:

1. `_PresentedAlgebraParent.__init__` calls the lower constructor,
2. which installs this algebra's module placement — `_install_self_module_placement`,
3. which builds `Modules(self)`, whose interning key includes the algebra,
4. so the algebra is **hashed**, and `CategoryObject.__hash__` is `hash(repr(self))`,
5. so `_repr_` runs — and it formatted `self.presentation_ring()` and `self.relations()`,
6. neither of which exists yet: the selected presentation is fixed *after* the lower constructor returns.

So the name of an object was asked for before the object had the datum its name states. `_PresentedAlgebraParent` now records `presentation_ring` as `_preamble_presentation_ring` in its first instant, and `_repr_` reads the relations only when they are installed, stating `P/(presented quotient)` in the window before that. Nothing else about the presentation changed, and the name is stable once the object is complete (`QQ[x,y]/(-y^3 + x^2)`).

**Result: five tests released by one ordering fix**, measured across `117b222` and after on the same two files — 7 failed → **2 failed / 5 passed**, no new failure:

- `test_the_cusp_is_generated_as_an_algebra_by_a_module_of_rank_two` — the assertion of record: `generating_module()` is the free module on `{[x], [y]}` over `QQ`, rank **2**;
- `test_the_cusp_retains_its_presentation` and `test_the_presentation_ideal_of_the_cusp_contains_its_relation`;
- `test_an_algebra_over_a_field_is_torsion_free` and `test_the_gaussian_integers_are_torsion_free_over_z`.

A wider algebra regression across five files: 17 failed / 2 passed → **16 failed / 3 passed**, no new failure and one more released (`test_a_morphism_out_of_a_polynomial_ring_is_a_choice_of_images`).

The two failures left in those files are the same vocabulary split as the Hermite specimen: `test_z_t_mod_two_t_has_two_torsion` and `test_swapping_the_axes_is_an_involutive_automorphism_of_qq_xy_mod_xy` call `ring.quotient(...)`, which no algebra exposes — the owner's constructor is `quotient_by_relations(...)` (or `quotient_ring(ideal)`). That is the next thing to restate and verify.

### An engine that cannot decide primality is not a crash

`ZZ[t]/(2t)`'s torsion test died in `NotImplementedError` from Sage: `is_torsion_free` → `_torsion_freeness_decision` → `is_integral_domain()` → `_integral_domain_decision` → `self._engine.is_integral_domain()` → Sage's quotient `defining_ideal().is_prime()`, which refuses for a multivariate ideal over `ZZ`. An engine that cannot decide a question states nothing, and this library's three-valued contract already has the answer for that — the proposition, exactly as `_finiteness_decision` right beside it does. `_integral_domain_decision` now catches the refusal and returns `AtomicProposition("is_integral_domain", self)` instead of letting it escape.

That is a strict improvement and it is *not* closure of the specimen: `is_torsion_free()` now answers the **proposition** `is_torsion_free(ZZ[t]/(2t))` rather than `False`, and the test asserts `not algebra.is_torsion_free()`, which a proposition refuses to answer (`ask(...)` is required). The library cannot yet decide torsion-freeness for a presented algebra over a non-PID: `2 · t = 0` with both nonzero settles it mathematically, but the generic presented-module torsion decision does not use a relation that is a nonzero multiple. That is a new algorithm and is recorded rather than improvised.

Evidence over four files across `117b222` and after: 15 failed / 3 passed → **10 failed / 8 passed**, five released and none added — the three cusp tests, `test_an_algebra_over_a_field_is_torsion_free`, and `test_the_gaussian_integers_are_torsion_free_over_z`.

### A one-term relation *is* a torsion witness, and that closes `Z[t]/(2t)`

The previous entry left `Z[t]/(2t)` at the proposition because the generic presented-module decision does not read relations. It does not have to be read there: a defining relation that is a single term `c w` with `c` a nonzero non-unit of the coefficient ring and `w` a word whose class in the algebra is nonzero *is* a torsion element with its scalar, `c * (w mod I) = 0`. `AlgebrasWithChosenFinitePresentation._torsion_freeness_decision` now asks `_represented_relation_torsion_witness()` before falling through to the generic module predicate, and answers `False` when that returns a pair.

Everything the witness needs was already maintained; nothing was invented and no normal form is recomputed:

1. `self.relations()` gives the relation as an element of the presentation ring `P`;
2. `P._native_basis_coefficients(relation)` decodes it in the word framing that `P` already uses for its own basis — for `2 t` that is exactly `{ι₁(t): 2}`, one term, so the relation has the shape the witness reads;
3. `P._native_basis_image(label)` is the inverse evaluation, giving the word back as an element `w` of `P`;
4. `self.algebra_presentation_morphism()(w)` is the class of `w` in `A`.

Then the pair is *checked*, not assumed: `(c == 0) is False`, `c.is_unit() is False`, `(w̄ == 0) is False`, `(c * w̄ == 0) is True`. Every one of these has to be decided; an undecided comparison skips the relation, so an undecided word class cannot be turned into a false torsion claim. A positive answer is never produced here — the field branch, the framed-free branch and the integral-domain-kernel branch keep their own proof conditions, and this branch only ever returns `False`.

Measured decisions (probe, and asserted in `tests/algebras/test_finite_presentations_of_commutative_algebras.sage`):

| algebra | relation | decision | why |
| --- | --- | --- | --- |
| `Z[t]/(2t)` | `2t`, non-unit `2` | `False` (witness `(2, t̄)`) | `2 t̄ = 0`, `t̄ ≠ 0` |
| `Z[t]/(2)` | `2·1` | `False` (witness `(2, 1)`) | `2 · 1 = 0`, `1 ≠ 0` — the word is the unit |
| `Z[t]/(4t)` | `4t`, non-unit `4` | `False` (witness `(4, t̄)`) | the scalar need not be prime |
| `Z[x,y]/(2xy)` | `2xy` | `False` (witness `(2, x̄ȳ)`) | the word may have length two |
| `Z[t]/(t)` | `t`, unit coefficient | `True` | `Z[t]/(t) = Z`, freed by the framed-free/integral-domain branch |
| `Z[t]/(t²+1)` | two terms | `True` | the Gaussian integers are a domain |
| `Z[t]/(2t−2)` | two terms | **undecided** | `2(t−1) = 0` is real torsion, but no single term carries both a non-unit coefficient and a nonzero word class |

The last row is the honest boundary and is asserted as an `AtomicProposition`, not papered over: the witness reads one-term relations only, and a multi-term relation would need coefficient elimination (a normal form) that this branch deliberately does not implement.

**Vocabulary, again.** `test_swapping_the_axes_is_an_involutive_automorphism_of_qq_xy_mod_xy` had never run: `ring.quotient(ideal)` does not exist on an algebra, and its `axes(plane.gen(0))` spelling assumed a coercion form the owner does not offer. Restated as `plane.quotient_by_relations([x*y])` + `axes.algebra_generator(...)` it still did not construct the morphism, because a presented-algebra `Mor` takes its generator images **keyed by generator label** — `axes.Mor(axes)({x: y, y: x})` fails with "the images ... must be given for every generator, but ['x', 'y'] are missing", the dict keys being elements rather than labels. `axes.Mor(axes)({"x": y, "y": x})` is the owner's spelling, and all five assertions (generator images, `σ(x²+y) = y²+x`, `σ(xy) = 0`, `σ²(x³+2y) = x³+2y`, `σ(x) ≠ x`) hold.

Also checked because the superclass already uses those getters: `algebra_generator(label)` is defined once, on `Algebras.ParentMethods`, and reads the selected resolution's generator, so a presented algebra returns an element of *itself* — `A.algebra_generator("t").parent() is A` for `Z[t]/(2t)`. What looks wrong in that specimen is only the **name**: a presented algebra reprs as `Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Integer Ring/(2*t)`, because the presentation ring's own repr is module-flavoured. It is cosmetic and not touched here.

**Evidence.** `tests/algebras/test_finite_presentations_of_commutative_algebras.sage` 9 passed (three new tests: the unit-word witness, the two-generator product witness, and the undecided two-term boundary); `tests/algebras/test_finitely_presented_algebras_archive.sage` 1 passed; `tests/modules/test_finitely_presented_module_archive.sage` and `tests/modules/test_cardinality_and_exponent_over_any_pid.sage` 5 passed, so `module.exponent()` still reads from the annihilator. Regression against `f01a702` in a clean worktree, same invocation both sides: `tests/algebras tests/modules` **230 failed / 164 passed → 228 failed / 166 passed**, and the difference is exactly the two intended files — `test_z_t_mod_two_t_has_two_torsion` and `test_swapping_the_axes_...` — with no new failure. `tests/rings/test_commutative_algebra.sage` is 16 failed / 9 passed on both sides with identical failure sets (the earlier "17" in this file was a stale count).

**Withdrawn before it shipped.** An in-flight edit had made `Modules.ParentMethods._torsion_freeness_decision` consult `self.exponent()`. It was reverted rather than repaired: `def exponent` exists only on the finitely-presented-module class, whose own `_torsion_freeness_decision` answers first, so the hook could not fire for any object, and it would not have closed this specimen anyway (a presented algebra has no `exponent`; `annihilator()` asserts). Its witness filter was also inverted — `if (element == self.zero()) is not True: continue` skips the nonzero element instead of requiring it — a reminder that *"is not True"* and *"is False"* are not interchangeable when the comparison can be undecided. The patch is kept at `.scratch/torsion-inflight.patch`.

### Two orbit routes, and only one of them has the retained finite action

A finite formed module's `orbits()` and a hand-built action on part of it do **not** take the same route, and the difference is whether the orbit relation is decided or left `Unknown`.

**Route A, the owner's.** `D.orbits()` dispatches to `QuadraticFormModules.FinitelyPresented.Torsion.orbits` (also on `FormModules.FinitelyPresented.Torsion`), which is `@cached_method`, and goes `_finite_form_orbits` -> `_torsion_form_element_action` -> `FiniteGSets(acting)(form.elements(), ...)` -> `_finite_g_set_from_action`. The object is a `FiniteGSets` parent, whose `ParentMethods` precede `GObjects.ParentMethods` in the MRO, so `_orbit_relation_decision` resolves to `FiniteGSets`' label hook — **not** to the `RealizationHook` default that answers `Unknown`. Verified on real discriminant forms `⟨8⟩` and `⟨32⟩`: the winner is `FiniteGSets.ParentMethods._orbit_relation_decision` and it returns a `bool`. `_orbit_labels()` is `@cached_method` and computes the whole partition once from the retained generators through the permutation representation (GAP orbit per point).

**Route B, a hand-built action.** `GObjects(G, Sets()).on_set(points, action)` without `orbit_relation` stores `lambda left, right: Unknown`. Then `GObjects.in_same_orbit` takes its finite-group branch, `conjunction(negation(self.act(element, source) == target) for element in self.acting_group())`, and `OwnedGroup.__iter__` is `(self._from_engine(element) for element in self._engine)`: one engine element lowered per element, for **every** element of the group, **per pair**. That is the only place a pairwise orbit decision resolves group elements, and for `O(D)` of a 2048-element discriminant form it cannot finish. Measured on `⟨32⟩` with the 3 nonzero isotropic elements: route A decides (`True`) and returns 2 orbits in 0.11 s; route B returns `Unknown` from `_orbit_relation_decision`, which is precisely the observable that selects the fallback.

So the maintained construction for a `G`-invariant **subset** of a finite formed module is `FiniteGSets(acting)(subset, lambda automorphism, element: automorphism(element))`, the same construction `_torsion_form_element_action` uses internally; `on_set` is the trap. There is no owner entry point `orbits_on(subset)` for elements, which is why a consumer acting on `isotropic_elements()` filtered to the nonzero ones has to construct the action itself.

**Cost inside route A is quadratic, and independent of the group's order.** Measured per relation call on `⟨32⟩`: `in_same_orbit` 80.6 µs, `_orbit_relation_decision` 72.2 µs, two `ranking_map` evaluations 74.8 µs, element equality alone 35.1 µs — so the constant is the element coercion inside `ranking_map`'s `position_of`, not the label comparison. `_OrbitSet._orbits` builds one `_Orbit` per point and deduplicates by `orbit not in found`, which is one relation call per comparison: |X|(|X|+1)/2 of them, so 2.1 million at |X| = 2048 ≈ **170 s** at the measured constant, before `points()` rescans X once per orbit. `_orbit_labels` itself scales with |generators| x |X| (0.17 s at 32 points). The first generator resolution in a process pays the Oscar/Julia initialisation, measured at **35.6 s** on `⟨8⟩` with every individual step at ~0.0 s.

The partition is therefore computed twice: once exactly by `_orbit_labels`, and then again point by point through the relation by the orbit-set engine. An owner-level repair would let `_OrbitSet._orbits` use a partition the g-set already supplies (and let `_Orbit._richcmp_` compare labels rather than coerce elements), falling back to the pairwise scan otherwise. That is not implemented here: no semantics were changed while the consumer's exact specimen is still outstanding.

**Caching is per retained identity, and interning already covers the equal-form case.** `automorphism_group` is `@cached_method` on the form; `TorsionFormOrthogonalGroup.__init__` calls `select_group_generators(self._computed_group_generators)`, a deferred supplier, and `_computed_group_generators` -> `_engine_group()` -> `_engine_orthogonal_group` are each `@cached_method`. Measured: `Lattices(ZZ)([[32]]).discriminant_quadratic_form()` twice in one process gives the *same* object (`is` true), hence the same group, hence 0.00 s for a second generator resolution. The documented hazard remains for objects that are only *equal* — `Of` caches between endpoints by identity, since two equal torsion forms are two objects — but it does not reproduce by rebuilding the form the same way.

**Open, and settled only by the consumer's specimen:** whether its orbit computation goes through route A at all. `g_set._orbit_relation_decision(x, y)` answering `Unknown` selects route B; answering a `bool` selects route A, and then the cost is the quadratic dedup above rather than generator resolution.

### A group's name is not its presentation: `Sym(Omega)` now names only the degree

`_symmetric_group` built its description as `f"Symmetric group on {points}"`. That interpolation is not free: `str(points)` runs the point set's `_repr_`, and a coset set's `_repr_` materializes and form-validates every representative. So *constructing* `Sym(Omega)` cost as much as presenting `Omega`, which is the port's Enriques case 1: `_symmetric_group` at the description, 1800 s without returning, 29 stack dumps, process gone.

The description is now degree-based — `f"Symmetric group S_{size}"` when the points are the standard `{1..n}`, else `f"Symmetric group on {size} points"` — which is exactly the data `_own_group` retains anyway: the points remain the separately supplied `symmetric_points`, returned by `natural_points()` and used by the action and its validation. Nothing about the group, its engine, its action or its validation changed; only the string. No lambda or pseudo-lazy description was introduced: `_GroupEngine` keeps a string contract, so `_repr_` returns it and `_latex_` replaces into it.

Measured on the Coble discriminant form `D` (`B = <1> + U + E8(-1)`, `T = B.twist(2)`, `|D| = 2048`): `SymmetricGroups()(D.elements())` **1.03 s -> 0.0246 s**, the description **63 KB -> 30 chars**, `repr(S)` 6 us, and `natural_points() is D.elements()` still true. `_catalogue_group_description` needed no change: it formats integer degrees only, and the remaining `{points}` interpolations in this file are inside assertion messages, built only when an assertion fails.

Regression: `tests/groups/test_free_and_catalogued_groups.sage::test_a_symmetric_group_is_named_by_its_degree_and_never_presents_its_point_set` replaces the point-set class's `_repr_`, and then its `__iter__`, with raising ones: construction and display must both succeed, the description must be degree-based, `natural_points()` must be the retained set, and the action must still be exact (`group((1,2))(w) = x`, and the reverse under the action). Construction legitimately iterates the point set three times — comparing it with the standard one — but must never render it.

**Not the same boundary, recorded so it is not conflated.** With the description fixed, the Coble permutation *build* still hangs, in a different place: `Symmetric groups -> _from_engine` (`groups.py:1359`) -> Sage `permgroup.py:932`, the membership test `x.gap() in self.gap()`; for the non-standard point set the engine is `PermutationGroup((transposition, 2048-cycle))`, and that check on degree 2048 ran past 360 s. The owner's own `_permutation_from_point_map` and `S(images)` are cheap (1 ms at degree 2048 on a cyclic form), and the retained-action path resolves generators once and caches them (`group_generators()` 4 generators in 0.3 s, same family on re-read; `_orbit_labels` cached per action object, which `element_action()` also caches). The next instrumented run for the orbit partition should look at that membership test, not at the description.

Evidence files: `.scratch/coble-stack2.log` (the faulthandler stacks naming `_from_engine` -> `permgroup.py:932`), `.scratch/probe-sym-coble.py` (the timing above).

### `Sym(Omega)`'s engine is the symmetric group, and that is a performance boundary

The engine of `Groups.S(points)` was `SymmetricGroup(degree)` only for the standard points; other labelled point sets got `PermutationGroup((transposition, degree-cycle))`. Those are the same group with the same generators — Sage's own `SymmetricGroup(n).gens()` is that transposition and that cycle — but not the same *knowledge*: `PermutationGroup._element_constructor_` admits an element through the symmetric-group parent without a membership test, and through a generic permutation group with `x.gap() in self.gap()`. That test is a GAP membership computation over the whole group, and at degree 2048 it had not returned after 360 s, so nothing downstream of the permutation representation could run.

The engine is now `SymmetricGroup(degree)` for every point set. Measured on the Coble discriminant form `D` (`<1> + U + E8(-1)`, `twist(2)`, `|D| = 2048`): admitting one generator permutation of degree 2048 (`_permutation_from_point_map`, the ingress the orbit computation performs) went from **>360 s, never returning** to **0.00 s**; the whole description-plus-construction of the symmetric group on those 2048 points is 0.02 s.

Identity survives the sharing. Sage caches `SymmetricGroup(n)`, so both point sets of a given size now have the *same* engine object; the owned groups are nevertheless distinct and keep their own retained points, because `_symmetric_group` is keyed by the point set and the retained `symmetric_points` distinguish the objects. Pinned by a regression that builds two different 4-element labelled point sets and asserts equal engines, distinct groups, each `natural_points()` equal to its own set, and elements that refuse a point of the other set.

No validation was weakened. Membership and form checks still run where they are the answer: the symmetric-group parent's own constructor is what admits the permutation, an invalid non-bijective point map still raises "not represented by a permutation", and an element still refuses a point outside its selected permutation domain. Nothing was made `check=False`.

**The Coble materialization now completes.** `D.orbits()` returns in **72.1 s** (of which ~40 s is the one-time Oscar/Julia initialisation) with **6 orbits of sizes [527, 527, 496, 496, 1, 1]**, summing to 2048.

**Corrected reading of those sizes.** Sizes alone do not classify the orbits, and my first statement that *both* 527s are the isotropic classes was wrong: the `q = 0` fibre has 528 elements in total, independently counted, so only one 527 orbit can be its nonzero part. Measured by quadratic value, the six orbits are

| orbit size | 1 | 527 | 496 | 1 | 527 | 496 |
| --- | --- | --- | --- | --- | --- | --- |
| `q` | 0 | 0 | 1 | 1/2 | 1/2 | 3/2 |

so the fibres are `q = 0` 528 (the isotropic set: `{0}` plus one 527), `q = 1/2` 528 (a singleton plus the second 527), `q = 1` 496 and `q = 3/2` 496. The value partition `528, 528, 496, 496` is what the orbit decomposition must reproduce, and it is now asserted exactly, point by point, in `tests/lattices/test_coble_discriminant_orbit_values.sage`. `_orbit_labels` on the 2048 points costs 0.0 s once the four generator permutations exist (one `_permutation_from_point_map` per generator, counted). The generator resolution itself is unchanged and cached: `_engine_group()` through Oscar once (41.8 s), `group_generators()` 0.3 s, the same family on re-read.

Evidence: `.scratch/coble-after-engine.log` (the `D.orbits()` run and orbit sizes), `.scratch/probe-coble-stack2.py` (the ingress timing), `.scratch/eng-base.txt` and `.scratch/eng-after.txt` (targeted before/after: 22 failed / 20 passed -> 22 failed / 21 passed, identical failure sets, the extra pass being the new regression).

The exact Sage condition is worth naming, because it is the difference between admission and bypass. `PermutationGroup._element_constructor_` first checks that the element's domain is compatible, then admits when `isinstance(self, SymmetricGroup) or x.gap() in self.gap()`. Using the maintained `SymmetricGroup(degree)` therefore selects Sage's own full-symmetric admission semantics — the same constructor, the same domain check — and not an unchecked path; nothing is passed `check=False`. On the ownership side the sharing is safe because `_own_group`'s key includes `id(symmetric_points)`: one internal Sage `S_n` per degree, still one owned group per retained labelled point set. The regression pins these directly: the same point set gives the same group object, the engine labels are the point ranks raised by one (`(1, 2, 3, 4)` for four labelled points), the engine permutation `(1, 2)` swaps exactly the two points of least rank, and a permutation outside the degree — `(1, 2, 3, 4, 5)` or `(0, 1)` in a degree-4 group — is refused rather than truncated.

### Where the Coble orbit time actually goes, and the one uncached crossing left

Measured in one process on the exact `D` (`|D| = 2048`), in order:

| phase | time |
| --- | --- |
| `D.automorphism_group()` | 0.0 s |
| `group_generators()` — the Oscar/Julia engine | 45.0 s |
| `element_action()` — building the represented `G`-set | 14.5 s |
| `_orbit_labels()`, first call (4 generators + 2048 GAP orbits) | 12.9 s |
| `_orbit_labels()`, second call | 0.000001 s |
| `action.orbits()` object, iterating it, `points()` per orbit | 1.5 s total |

So the quadratic concern recorded above is **refuted at this size**: the orbit-set engine's pairwise part is ~1.5 s, not a blocking term. What dominates is the one-time Oscar initialisation and, per generator, the isometry applied to all 2048 points (~3.1 s each). Both are inherent to the maintained construction rather than defects.

The one crossing that is not cached is the elementwise group morphism: `mor.elementwise(rule)(generator)` recomputes the rule on every evaluation — the same generator costs 3.08 s again on a second call, and the returned permutation is a new object. `_orbit_labels` evaluates each generator once, so nothing pays twice *today*; the hazard is any future consumer that asks for the same permutation twice. The fix that would not disturb semantics is a cache at the g-set, where the permutation is a function of the retained action, rather than in the generic `P`-valued `Mor` — and it should wait for a consumer that actually pays twice, since no current path does.

**The next blocking items are not in this library's orbit machinery.** The port's `recursive.py:154` owned-element crossing and its `OrbitCoverModel` generator search remain port-side, as recorded earlier.

### Research issue 614, the three notebook specimens, checked one at a time

The `preamble-lattices.ipynb` cells 18, 21 and 24 state the original acceptance. Reproduced on this main with focused probes, no sweeps:

| specimen | acceptance | current state |
| --- | --- | --- |
| cell 18 — `Lattices(O)([[2, a], [a, 2]])` over `QuadraticField(2, "a").maximal_order()` | `u*u == 2`, `u*v == a`, `v*v == 2`, and `gram_tensor()` displays | **passes** |
| cell 21 — `Lattices(Oi)(Oi^2)` over `QuadraticField(-1, "i").maximal_order()` | `ei*ei == 1`, `ei*fi == 0`, `fi*fi == 1` | **passes** |
| cell 24 — `R = Zp(5)`, `Lattices(R)(R^2)` | the ring constructs, then `ep*ep == 1`, `ep*fp == 0`, `fp*fp == 1` | **fails at `Zp(5)` itself** |

The two passing specimens were closed by the earlier number-field and display repairs; nothing in them needed changing, and they are now recorded as verified rather than assumed.

`Zp(5)` raises `RecursionError` before any lattice exists: `Zp` -> `AdicCompletions()(ZZ, (5))` -> `_adic_completion_from_owned_data` -> `_AdicCompletionAlgebraParent(...)`. The cycle in the traceback is

`algebras._mul_` -> multiplication bilinear map -> `domain().pure_tensor(...)` -> `tensor_quotients.pure` -> `reduced_terms` -> `module(value)` -> `algebras._element_constructor_` -> `self.algebra_base_ring()` -> `self.base_ring()` -> back to `_mul_`.

So an element coercion inside the completion's own construction asks an algebra for its base ring, and answering that question re-enters the algebra's multiplication through the tensor construction. `_AdicCompletionAlgebraParent.__init__` does pass a base (`source if algebra_base is None else algebra_base`, i.e. `ZZ` here) to `_OwnedAlgebraParent`, so the base is retained in principle; which of the coerced factors recomputes it by arithmetic is the open question, and the repair belongs there — not in a memoization layer. No arithmetic was reimplemented and no assertion was weakened; the specimen stays open until that is settled.

### Research issue 614: the acceptance matrix, family by family

Seven families from `preamble-lattices.ipynb`. Status is exact, with the regression that carries it; a failing family is named as failing, not folded into an unrelated repair.

| family | notebook cell | acceptance | status | carried by |
| --- | --- | --- | --- | --- |
| lattice over an order | 18 | `Lattices(O)([[2,a],[a,2]])` builds; `u*u = 2`, `u*v = a`, `v*v = 2` | **accepted** | `.scratch/probe-614-A.py`; display half in `tests/rings/test_number_field_construction_and_display.sage` |
| multiplication over `Z[i]` | 21 | `ei*ei = 1`, `ei*fi = 0`, `fi*fi = 1` | **accepted** | `.scratch/probe-614-B.py` |
| the 5-adic completion and a lattice over it | 23, 24 | `Zp(5)` constructs; `ep*ep = 1`, `ep*fp = 0`, `fp*fp = 1`; repr and latex render | **accepted** | `tests/rings/test_five_adic_completion_and_its_lattice.sage` (10 tests) |
| discriminant normal form | 57 | `TEn.discriminant_group().normal_form()` is an isomorphism, 12 -> 10 generators, both round trips | **accepted** | `tests/lattices/test_discriminant_normal_form.sage` |
| isotropic reduction | 58 | `E8.is_elliptic()`, `U.q(e0) = 0`, `e0.e1 = 1`, `e0.e_perp_mod_e()` | **accepted** | `tests/lattices/test_isotropic_reduction_and_correlation.sage` |
| correlation isomorphism | 63 | valence `(1,1)`, `lower_index` returns the Gram, both inverse identities on their own generator families | **accepted** | same file |
| free algebras | 61, 84 | tensor and divided-power algebra identities; infinite symmetric-algebra substitution | **accepted** | `tests/algebras/test_free_algebra_issue614_cells.sage` (5 tests); the repairs are below |

**Cell 61 fails at both constructions, and the failures are the chosen-resolution contract, not the module.** With `M = coker(2: ZZ -> ZZ)` built exactly as the notebook builds it:

- `M.tensor_algebra()` raises `ValueError: Integer Ring as an algebra over Integer Ring has no chosen resolution relative to Category of modules over Integer Ring` (from `modules.py`'s tensor-algebra route);
- `M.divided_power_algebra()` raises `ValueError: Direct sum over Integer Ring has no chosen resolution relative to Category of modules over Integer Ring` (`power_algebras.py`'s `PowerAlgebra(module, "divided")`).

`M` itself is fine — a finitely presented module on one generator with invariant factor 2, and `M.module_generating_set()` already fails the same way, so the demand is made before either power algebra is reached. The repair is to make the maintained chosen-resolution contract supply the resolution `M`'s own presentation states; inventing a resolution in the constructor, or substituting a free module, would be exactly the substitution the owner forbids.

**Cell 84 fails at one assertion, about placement.** Building `ZZ.free_module(NN).symmetric_algebra()` raises in `_algebra_on_module`: "an algebra on the Integer Ring-module Module of symmetric words on Free module on NN = {0, 1, 2, ...} over Integer Ring must be placed in categories of algebras over Integer Ring, but got (Category of symmetric algebras over Integer Ring, Category of integer graded modules, Category of free algebras over Integer Ring, Category of graded free algebras over Integer Ring, Category of projective modules over Integer Ring)". One entry in that placement, the integer graded *module* category, is not a subcategory of `Algebras(ZZ)`, so the all-algebra guard rejects the list. Whether a graded algebra's placement legitimately carries its graded-module refinement is the question to settle; it must be settled by reading that guard's contract, not by dropping the assertion.

### The sparse free algebra's placement, split correctly, and what it exposed

`_algebra_on_module` distinguishes `placement` (categories of algebras) from `categories` (further, non-algebra data), documented at 3187–3194 and enforced at 3208. `_sparse_free_algebra_of` built `flavor_category`, `IntegerGradedModules(ring)`, `FreeAlgebras(ring)`, `GradedFreeAlgebras(ring)` and `Modules(ring).Projective()` into one tuple and passed all of it as `placement`, so the guard rejected the graded module entry. The call site now sends the algebra categories as `placement` and the module refinements through `categories`; `realization_owner` (still the meet including `GeneralModules`, `GradedModules`, `ModulesWithChosenComponentPresentation`, `Algebras` and every refinement), `construction_data` and the grading are unchanged, so the module structure is retained rather than dropped.

That correction lets construction past the guard and exposes the next defect, which is a different one and is **not** fixed: `sparse_free_algebras.py:344`, inside `SparseFreeAlgebraMor._call_`, does `self.domain().framing_morphism().lift(element)` and `framing_morphism` is `None`, so the morphism cannot evaluate at the zero test. Cell 84 therefore remains unaccepted, now at the morphism's framing rather than at placement.

### Cell 61: the frame is retained; the lookup is what fails

The represented cokernel does retain the endpoint's presentation — `ModuleMorphismMethods.cokernel` dispatches to `_presented_module_from_morphism`, which keeps the codomain's generators and relations and adds the map's images, and `_GeneralPresentedModule.__init__` passes that to `_SelectedFinitePresentationModules.__init__`, which fixes the selected presentation and resolution. `Mor(F, F)` alone invents no frame.

The error names `Integer Ring as an algebra over Integer Ring`, not the quotient, which is the tell: the frame that `native_modules.py` installs for the regular module is recorded on the ring, and the demand arrives from the algebra realization wrapped around that ring. `selected_resolution(owner)` is a registry lookup keyed by the owner category, and the wrapper asks under its own identity. So the datum is not missing — the lookup is at the wrong owner. Repairing it means making the algebra realization read the frame its endpoint retained, which is where the next attempt belongs; the alternative, choosing another basis for `ZZ` or substituting `ZZ^1` for `M`, is exactly what the ruling forbids.

### Cells 61 and 84 accepted: seven owners, named exactly

Both notebook cells now run as written. Nothing invented a basis, substituted a free module, or fabricated a resolution; each repair is at an owner that was asked a question it could not answer, or answered from data another owner held.

**Cell 84 was not a framing defect at all.** `SparseFreeAlgebraMorphism.__init__` builds its elementwise module map *before* `CategoricalMor.__init__` installs the arrow's endpoints, and `elementwise` runs its zero check as it builds the map, so that evaluation re-entered `_call_`, which reads `self.domain()`. The attribute was still `None`, so `self.domain()` was a call on `None`: `TypeError: 'NoneType' object is not callable`, which looked exactly like a missing framing. The evaluator now takes its endpoints as arguments (`_evaluate_element(domain, codomain, element)`, with `_image`, `_basis_image`, `_component_map` threaded the same way); `_call_` supplies the installed pair. Binding `self.domain = domain` first is *not* the fix: `domain` is a method on that class, and shadowing it makes `self.domain()` call the algebra parent instead.

**Cell 61's tensor half was `T^0`.** `_tensor_power(module, 0)` returned `R.regular_module()._with_structure(...)`, and a ring's `_with_structure` is the *algebra* level: it reconstructs on the ring's unformed module, so the result was `Integer Ring as an algebra over Integer Ring` with an empty selected-resolution registry. `graded_piece(0)` reads that piece's frame, so every differential graded construction lost its degree-zero piece. The repair routes degrees 0 and 1 through the module owner (`_module_with_structure`), which keeps the regular module's canonical `{1}` frame.

**A tensor-product module morphism refused its own framing.** `_framing_morphism` always states `surjectivity_premise=True`, and `TensorProductModuleMorphismMethods.__init__` did not accept that keyword, so `M^{⊗2}`'s framing morphism could not be constructed at all. Both it and `QuadraticModuleMorphism` now accept and forward `surjectivity_premise`, as the base `ModuleMorphismMethods` declares it.

**The graded direct sum's frame was decided by the wrong caller.** `_direct_sum_of_modules` decides "every summand carries a chosen frame" by visiting the summands, which is impossible over an infinite grading set, where its own docstring says the caller must state the fact with `componentwise_framing=True`. Two callers could not: `GradedModules.__call__` had no way to pass it, and `_FramedDirectSumOfModules._module_with_structure` dropped it when adding structure to an already-framed sum. Both now state it; `_power_algebra_of` supplies `componentwise_framing=True` because every piece is a `divided_power_module`/`exterior_power`, which retains a frame in every degree.

**The algebra resolution was built during construction.** `_install_selected_algebra_generators` built the free algebra source eagerly (`module.symmetric_algebra()`) only to re-read its generator labels, which contradicts `_fix_selected_algebra_resolution`'s own contract ("an algebra whose construction registers its resolution must not build a tensor algebra while it is constructed"). For `Γ(M)` the generating family is infinite, so that eager build was a sparse commutative word algebra on every divided power of the frame, built and discarded at construction time. The free module's label set is the free algebra's label set (verified: the same object), so the labels come from the module and the source is a factory.

**An augmentation built one category weaker than the slice it enters.** `_constructed_algebra_morphism` used `Algebras(R).Unital()`, while the scalar slice `AugmentedAlgebras(R)` is `SliceCategory(Algebras(R).Associative().Unital(), R)`, so `_augmented_algebra` refused the arrow with `CON-17` even though both sides print as `Mor_Alg(Γ(M), ZZ)`. The constructed morphism now refines to the associative family when both endpoints are associative: associativity is a law of the endpoints, so the stronger placement asks nothing more of the map.

**A multiset on a coproduct had no construction.** `Sets().coproduct` over an infinite index set is not `EnumeratedSets`, so `multisets_of_size` fell off the `FixedSizeSelections` path, and the symmetric word basis of a free algebra over the graded frame could not be built. `FixedCardinalityMultisetSets` (`Sets().ParentMethods.multisets_of_size` for a set that states no enumeration, `src/sage_extensions/categories/sets/set_categories.py`) states a multiset by its multiplicity map, which needs no ranking, and `Cardinalities().set_multiset_category` states its count from the same classification as the fixed-size selections. Enumerated alphabets keep the combinadic construction.

**Three places asked `is_finite()` of an unevaluated cardinal.** The free module's `_repr_`, `_coordinate_framed_free_module` and `_finite_source_elements_for_verification` each read `cardinality().is_finite()` on a cardinal that is `sum_{i in ZZ} kappa_i`, which asserts rather than answering. Each now requires the expression to be in normal form first, and answers "not a finite basis" (or names the label set) otherwise: a representation never decides a cardinality, and a finite matrix calculation needs a finite basis, not a proposition.

**`Γ(M)`'s generator label, and why `algebra_generator(0)` is a degree-one name.** Over `ZZ`, `γ_2(x)` is not a polynomial in `x`, so `Γ(M)`'s selected algebra generating family is the positive-degree frames, not `M`'s frame; that is what the library's own `test_gamma_2_of_x_is_not_in_the_subalgebra_generated_by_x_over_the_integers` states. The notebook asks for `Γ.algebra_generator(0)`, the label `M`'s frame carries, so a power algebra resolves a label of `M`'s chosen frame to the degree-one generator that is its image (`_PowerAlgebra.algebra_generator`), asking the selected family first and never renaming a label it already states.

### The divided power algebra after the repairs: 4 of 5, and one genuine gap (2026-11-01)

`tests/algebras/test_power_algebras.sage` had 0 of 5 passing before the cell-61/84 work: every one of them failed earlier, at the graded sum's missing frame. With the frame, the resolution and the augmentation repaired, **4 of 5 pass**, and the two failures that were recorded here as library defects were not defects at all. Both are corrected call sites, and the correction is the acceptance, not a weakening:

- `test_integral_divided_power_laws_on_two_generators` failed at its **last** assertion, `divided.augmentation(divided.one() + x + gamma2y) == 1` — not at the divided power of a sum, which the earlier entry in this file wrongly named. The three identities really do hold (`x*x = 2γ_2(x)`, `γ_2(x)x = 3γ_3(x)`, `γ_2(x+y) = γ_2(x) + xy + γ_2(y)`). The failure was the accessor's spelling: `augmentation` is a `@cached_method` returning the arrow — every other call site in the library and in the tests writes `algebra.augmentation().codomain()`, `algebra.augmentation()(element)` — and the test alone called the method with an element. It now calls `divided.augmentation()(…)`, and the assertion is unchanged.
- `test_exterior_and_divided_power_algebras_preserve_composition_on_torsion_modules` failed at `functor(first)(e0 * e1) == 2 f_0 f_1`. The library computed `2 f_0 f_1 + 4 γ_2(f_1)`, and **that is the correct value**: over `ZZ`, `f_1·f_1 = 2 γ_2(f_1)` (the corpus's `dp_mul`, `DividedPowers/DPAlgebra/Init.lean:192`, states `dp R n m * dp R p m = (n + p).choose n • dp R (n + p) m`), and `4 γ_2(f_1)` is nonzero in `Γ²((ZZ/4)²)`, whose invariant factors the library itself reports as `[4, 8, 8]` — sharp, because `(4 f_1)·f_1 = 8 γ_2(f_1)` and the divided power algebra of `ZZ/4` in degree two is `ZZ/8`. The test had written the *exterior* expectation for a divided power functor. It now asserts the exact image `2 f_0 f_1 + 4 γ_2(f_1)` and the multiplicativity `functor(first)(e0·e1) = functor(first)(e0)·functor(first)(e1)` — a stronger statement than the one it replaced.

**The remaining failure is a genuine missing construction, and it is not invented here.** `test_gamma_2_of_x_is_not_in_the_subalgebra_generated_by_x_over_the_integers` calls `divided.subalgebra([x])` and the library has no `subalgebra` at all (`AttributeError: … has no attribute 'subalgebra'`). The notion is the corpus's `Algebra.adjoin` (`Subalgebra`, `Algebra.adjoin R s` = the subalgebra generated by a set), and this library states no such construction for any algebra: the closest existent thing is `predicate_subring`, which decides a *predicate*, not generation by a set. Building it means the image of `T(F(S)) → A` on a chosen finite `S` and an exact membership decision in that image, which is a construction this session did not write. The test's own statement therefore cannot be expressed until that construction exists; the requirement is recorded here rather than approximated by a one-generator special case.

### The corpus on the two contracts these cell-61/84 repairs decided (2026-11-01)

Searched before deciding, not after: `lean-reference-corpus` at `formalization-corpus.dzackgarza.com/api/search`, plus the pinned Mathlib checkout at `/opt/mathlib`. Queries run: `structure Sym (α : Type*) (n : ℕ) file:\.lean$`, `Sym α n multiset quotient file:\.lean$`, `TensorPower zero equiv file:\.lean$`, `divided power algebra file:\.lean$`; the local files were then read rather than trusted by name. Access note, corrected 2026-11-01: an earlier version of this entry said `lean-categories` "could not be inspected here" and called that an access failure. That was wrong. It is not checked out locally, which says nothing about access, and its public repository is reachable through the ordinary interfaces: `https://api.github.com/repos/dzackgarza/lean-categories` answered `200` with the repository metadata (public, not private), `https://github.com/dzackgarza/lean-categories` answered `200`, and `https://raw.githubusercontent.com/dzackgarza/lean-categories/main/README.md` answered `200` with its text: "The centralized Lean baseline of categorical constructions. Downstream projects require this package and import the trees they need; no construction is duplicated downstream." What was actually attempted and what came back is the record; a local absence is not a search result either way. The divided-power contracts below were settled against the corpus repositories that do hold them (`AntoineChambert-Loir/DividedPowers4`, fetched `200` at `DividedPowers/DPAlgebra/{Init,Free,Graded/Basic,Graded/GradeOne}.lean`), and `lean-categories` remains the owner for any notion this project would request from it.

**Multisets of size \(k\) on a set are `Sym X k`, and their datum is a multiplicity map.** `Mathlib/Data/Sym/Basic.lean:43` states `Sym (α : Type*) (n : ℕ) := { s : Multiset α // Multiset.card s = n }` and its docstring calls it "the nth symmetric power … n-tuples up to permutation … a subtype of `Multiset`"; `Multiset.count` and `Multiset.toFinset` are the multiplicity and support. `Mathlib/Data/Sym/Card.lean:46,48` states `card (Sym α k) = multichoose (card α) k` and `= choose (card α + k - 1) k`, both under `[Fintype α]`, and `card (Sym α 0) = 1`. So `FixedCardinalityMultisetSets` implements `Sym X k` with the multiset as the datum and no ranking of `X`, and its `_cardinality_decision` is the corpus's stars-and-bars theorem. The corpus states no infinite-\(X\) cardinality there; that case is the library's existing classification, which `Cardinalities().set_multiset_category` delegates to rather than a theorem this session invented.

**The graded divided power's basis is the multisets, and `Γ(M)`'s basis is all of `ι →₀ ℕ`.** The corpus holds `AntoineChambert-Loir/DividedPowers4`; reading `DividedPowers/DPAlgebra/Free.lean` gives `noncomputable def basis (b : Basis ι R M) : Basis (ι →₀ ℕ) R (DividedPowerAlgebra R M)` (line 516), `Int.basis_grade (d) : Basis {n : ι →₀ ℕ // n.sum = d} ℤ (Γ^d)` (line 450), and `basis_eq' … (x : Sym ι n)` (line 574), which indexes its graded part by `Sym ι n` directly. Two decisions of this session are therefore the corpus's, not local choices: the frame of `Γ^d(M)` is the \(d\)-element multisets of a frame of `M` (which is exactly what `_free_degree_labels(..., "divided")` already said at `powers.py:672` by calling `multisets_of_size`), and `γ_2(x)` is a basis element rather than a polynomial in `x`, so the selected generating family of `Γ(M)` carries the positive-degree frames and `algebra_generator(0)` is the degree-one image of `M`'s label.

**`T^0(M)` is the rank-one free module.** `Mathlib/LinearAlgebra/TensorPower/Basic.lean:38` defines `TensorPower R n M := ⨂[R] _ : Fin n, M`, and `Mathlib/LinearAlgebra/PiTensorProduct/Basic.lean:779` states `isEmptyEquiv [IsEmpty ι] : (⨂[R] i : ι, s i) ≃ₗ[R] R`. Degree zero is `R` — the thing `_tensor_power` now returns with the regular module's canonical frame, rather than an `R`-shaped object with no frame.

**Where the open divided-power product defect is owned.** `DividedPowers/DPAlgebra/Graded/Basic.lean` and `Graded/GradeOne.lean` in that repository are the corpus's owners of the graded law, to be read before repairing `_divided_power_product`; the Stacks citation in the code is not a substitute for reading them.

### Hashing a torsion-form automorphism: the digest is retained, and the crossing is gone (2026-11-01)

Consumer: `sage-indefinite-port` `fc6a022f` (`handoff-owner-torsionform-hash.md`). Its instrumented 3600 s Enriques `case_1` run put 14 of 16 complete stack dumps in `_permutation_from_point_map` -> `act` -> `TorsionFormAutomorphism.__hash__` -> `_engine().matrix()` -> GAP. The eager-description fix is confirmed gone; this is the next cost, and it is a cost question, not a correctness one.

The chain is now read in full: `_TransversalCosets._multiplier` is a `@cached_method` **keyed by the acting element**, so a left-coset action hashes its element once per point, and `TorsionFormAutomorphism.__hash__` rebuilt the engine coordinate matrix on every call.

Measured on the port's own specimen (`B = <1> + U + E8(-1)`, `D = B.twist(2).discriminant_quadratic_form()`, `|D| = 2048`, 11 x 11 engine matrices, 121 entries), same process, before and after:

| operation | before | after |
| --- | --- | --- |
| `g._engine().matrix()` | 0.64 ms | 0.72 ms (not called by a hash any more) |
| `hash(g)`, 200 calls | 0.86 ms each | 0.0001 ms each |
| `{g: 1}[g]` | 1.12 ms each | 0.0001 ms each |

The fix keeps the *same* digest expression — `(id(parent), engine matrix entries)` — and retains it on the immutable element (`_hash_digest`, `None` until the first hash, which is a safe absence marker because `hash` never returns `None`). The value is unchanged, so no dictionary is rehashed, no equality changes, no representation is invented and no validation is skipped; what disappears is the repeated GAP conversion. Construction stays cheap: an element nobody hashes converts nothing.

A detail that matters for reading the storage: iterating the group raises *fresh* element objects from the engine each time, so the retention pays where one object is reused — exactly the cached-multiplier case — and not across two iterations of the group.

Correctness, `tests/lattices/test_torsion_form_automorphism_hashing.sage` (4 tests, passing): the digest is absent until the first hash and is that hash afterwards; an equal automorphism built as another object hashes equally and finds its dictionary key; across `O(D_4)` (six elements) equal elements hash equally and the six digests are distinct; and a cache keyed by automorphisms answers a rebuilt-but-equal key.

**Provider pin: not updated.** A pin names a published `sage-extensions` commit, and this session's commits are local only — see the push blocker below.

### A subgroup acts through its inclusion, and a group has no action of its own (2026-11-01)

Consumer: `sage-indefinite-port` `5b7b72382c`. Its Coble polarization stabilizer `H` (`q(h) = 1`, `|H| = 94755225600`, 1984 generators) is a subgroup of `G = D.orthogonal_group()`, and the run called `H.orbits()`. That call cannot work at any size: `orbits()` is an operation of the `G`-*set* (the coequalizer of the action and the projection), and `H` is a group. The action is a datum of the object being acted on, not of a group.

The maintained route, verified on a small form and stated as `tests/groups/test_a_subgroup_acts_through_its_inclusion.sage` (4 tests, passing):

```python
G = form.automorphism_group()
elements = G.element_action()                 # the retained G-set on form.elements()
H = G.subgroup_on(generators)                 # the subgroup keeps its ambient automorphisms
inclusion = H.inclusion()                     # the retained H -> G
restricted = elements.restrict_action(inclusion)   # the H-set on the same points
restricted.act(h, x) == elements.act(inclusion(h), x)

isotropic = form.isotropic_elements()         # an invariant point set
on_isotropic = FiniteGSets(H)(isotropic, lambda h, x: h(x))   # what _torsion_form_element_action does
# or, keeping the restricted functor and stating the points:
GObjects(H, Sets()).on_set(isotropic, restricted.act)
```

`GObjects.restriction` is the functor behind `restrict_action`, and `H.inclusion()` is the morphism it is applied to; `lattices.py:7334` already restricts a vector-fibre action along a subgroup's inclusion this way. Both presentations of the isotropic points agree point for point with the ambient action through the inclusion, and `validate_point_closure` refuses a stated action whose points leave the set.

For the orbit count at `|H| = 94755225600`, `orbits()` cannot enumerate the group; the maintained presentation is `restricted.orbits_presented_by(covering)` with a stated finite covering meeting every orbit (the route `lattices.py:7300` uses), whose `section` is the orbit-to-representative map.

Two facts a consumer should not have to rediscover: `_GroupEngine` subgroups do not carry `coset_space()` (only predicate subgroups — kernels, stabilizers, preimages — have the data a coset space needs), and the orbit set's orbits are keyed by their parent, so two orbit sets are compared by the partition of the points they induce, not by orbit equality.

**Genuine gap, named and not worked around:** a `G`-set has no construction for its restriction to an invariant *subset* (a `G`-subobject retaining the action functor). Today the subset action is presented afresh by `on_set` or `FiniteGSets`, so the resulting object is a new `H`-set on those points rather than the subobject of the restricted one. Nothing about that is wrong for orbit computation, but the subobject arrow is missing from the G-set vocabulary.

### Blocker: this session could not push (2026-11-01)

`git push --dry-run origin main` answers `fatal: could not read Username for 'https://github.com': No such device or address`; the platform's GitHub connection reports `github_not_connected`; there is no credential helper and no stored credential (and storing one is not permitted). The commits below are on this checkout's `main` and verified by the tests quoted with them, but `origin/main` is still `6b10b0854b3b2a4faf454de23f865993ab066215`. A provider pin that names a published commit — including the one the port's handoffs ask for — therefore cannot be produced until the repository is connected or a push credential is supplied out of band.

### Published: `c546077`, and the provider pin consumers should use (2026-11-01)

The three commits of this session (`7ff4302` cells 61/84, `207ba52` retained hash digest, `d718fe7` subgroup-action tests) are published on `main` as **`c546077dce79a76eb32e92d080aa9c44e4c67552`**, whose parent is `6b10b0854b3b2a4faf454de23f865993ab066215` and whose complete tree is `81151a4450f26184c7f59a691dd924cc7d41d8da` — the tree of local `d718fe7`, verified identical (`git diff d718fe7 c546077` empty), with all 19 published blobs and their modes re-checked against the transfer manifest and matching. The tree was transferred rather than re-authored, byte for byte, and the message preserves the three original SHAs and their messages.

Reconciliation left the worktree and the index untouched: local `main` was moved onto the published commit with `git reset --soft` only after the tree equality and the clean-status checks, no force push and no new branch. The original local commits are preserved in `../sage-extensions-original-commits-d718fe7.bundle` (`git bundle verify`: complete history, head `d718fe7`).

**Provider pin for consumers: `c546077`.** The pin a port records must name a published commit, and that is this one; `6b10b085` is superseded and the local `d718fe7` names nothing on the remote. The push blocker recorded below is closed by the transfer, not by a credential.

### Issue 614 re-run on the published tree: all seven families, one selection (2026-11-01)

The earlier family passes were recorded on revisions before the cell-61/84 repairs, and those repairs cross several constructors (`_tensor_power`, the graded direct sum, `_install_selected_algebra_generators`, `_constructed_algebra_morphism`, `SparseFreeAlgebraMorphism`, the multiset construction). So the matrix was re-run once, as a targeted selection, on the **published tree itself** rather than on a working copy:

- provider: `sage-extensions` pin **`c546077dce79a76eb32e92d080aa9c44e4c67552`**, tree `81151a4450f26184c7f59a691dd924cc7d41d8da`, checked out in a separate worktree (`accept-wt`) so no local edit could contribute;
- runtime: Sage **11.0.beta5** on Python **3.14.10** (the development image's `/sage/.venv`, not a host Sage);
- runner: the project's pytest harness with `-o addopts="" -p qc_sage_session`.

| family | cells | carried by | result on `c546077` |
| --- | --- | --- | --- |
| lattice over an order | 18 | `tests/rings/test_number_field_construction_and_display.sage` (3 passed) plus `.scratch/probe-614-A.py` | **pass** — `Lattices(O)([[2, a], [a, 2]])` builds, `u*u = 2`, `u*v = a`, `v*v = 2`, `gram_tensor()` prints |
| multiplication over `Z[i]` | 21 | same file (3 passed) plus `.scratch/probe-614-B.py` | **pass** — `Lattices(Oi)(Oi^2)` builds, `ei*ei = 1`, `ei*fi = 0`, `fi*fi = 1` |
| the 5-adic completion and a lattice over it | 23, 24 | `tests/rings/test_five_adic_completion_and_its_lattice.sage`, 10 passed | **pass** |
| discriminant normal form | 57 | `tests/lattices/test_discriminant_normal_form.sage`, 1 passed | **pass** |
| isotropic reduction | 58 | `tests/lattices/test_isotropic_reduction_and_correlation.sage`, 2 passed | **pass** |
| correlation isomorphism | 63 | same file, second test | **pass** |
| free algebras | 61, 84 | `tests/algebras/test_free_algebra_issue614_cells.sage`, 5 passed | **pass** |

All 21 committed tests pass on that tree, and the two probes reproduce the notebook's own multiplication identities for cells 18 and 21 with the notebook's objects. The probes are probes: cells 18 and 21 have no committed regression of their own beyond the display half, and that gap is stated here rather than papered over by counting the display test as the multiplication one.

Disposition: research issue 614's seven notebook families are accepted on `c546077`. The three open defects below are the divided power algebra's own laws, reached only by `tests/algebras/test_power_algebras.sage`; none of them is one of the notebook's assertions, and none is counted against this acceptance.

### The generated subalgebra: `Algebra.adjoin` decided from the graded words (2026-11-01)

The corpus states the notion exactly: `Algebra.adjoin R s = Subsemiring.closure (Set.range (algebraMap R A) ∪ s)` (`Mathlib/Algebra/Algebra/Subalgebra/Lattice.lean:35`, fetched `200`), with the universal property `Algebra.gc : GaloisConnection (adjoin R) (↑)` and the closure induction `adjoin_induction`. Its points are the `R`-span of the words in `s`, together with `1`. In a graded algebra with homogeneous generators of positive degree the degree-`d` part of that span is spanned by the *finitely many* products of generators whose degrees sum to `d`, which is what makes the construction decidable — no new linear algebra is needed, because membership in their span is `is_in_image` of one module morphism `F(words_d) -> A_d`, decided by the graded piece's selected Smith normal form.

So `Algebras.ParentMethods.subalgebra(elements)` (`categories/algebras/subalgebras.py`) returns the ambient algebra's predicate subring over the algebra's own base ring — `_predicate_subring` gained a `base_ring` keyword, defaulting to `ZZ`, so every existing caller is unchanged — with membership decided degree by degree. It states its domain and refuses the rest: a nonhomogeneous generator is refused by assertion, a degree-zero one by `NotImplementedError`, rather than approximated. The words are deduplicated (in a commutative algebra `(x,y)` and `(y,x)` multiply equally), and the construction checks closure on the degrees it enumerates: each pair of words of generator degrees multiplies into the span of the summed degree, or the construction refuses itself.

**A defect it depended on, found and fixed: a slice object was not a member of itself.** Every power algebra is returned as the *augmented* algebra, i.e. an object of the slice `AugmentedAlgebras(R)`, and `SliceCategory.ParentMethods.__contains__` asked only the underlying object: `x in Gamma(M)` was `False` for an `x` the slice itself had constructed, because the underlying algebra is a different parent. Any membership question about an element of a slice was wrong, and `_predicate_subring.__contains__` opens with exactly that question. The slice now answers `True` for an element whose parent is the slice and asks the underlying object otherwise.

**Result: the fifth power-algebra test passes, and the file is green for the first time.** `tests/algebras/test_power_algebras.sage` is 5 of 5 (0 of 5 at the start of the session). `tests/algebras/test_generated_subalgebras.sage` states the construction directly: over `ZZ`, `x`, `x*x = 2 gamma_2(x)` and `x^3 = 6 gamma_3(x)` are generated by `x` while `gamma_2(x)` and `3 gamma_3(x)` are not (no integer `c` solves `2c = 1` or `6c = 3`); over `QQ` the same `gamma_2(x)` *is* generated, because `2` is a unit — the decision is arithmetic, not the element's name.

**Fixed since: the multiset-framed integral preimage, and `adjoin` with several generators.** The blocker recorded here was real and is now repaired at its own owner. `QuadraticModuleMor._element_constructor_` (the Mor class of every divided square, `powers.py`) accepted *any* iterable as a quadratic lift datum, and `MatrixSpaces.from_rows` hands a module morphism its **dict of generator images** — a dict is iterable, so the rows were read as a quadratic lift, its *keys* (the generator labels) were iterated as values, and each label was coerced into the codomain. That is the `TypeError: 2*['x'^2] does not describe an element of Free module on {['x'^2], ['x' 'y], ['y'^2]}` seen from `smith_form` -> `invariant_factor_presentation` -> `_morphism_from_engine_matrix` -> `from_rows`. A dict is the linear generator-image datum everywhere in this library, so it is now routed to the linear constructor before the quadratic reading is considered; the quadratic reading keeps its `IndexedFamily` and row-of-values forms, and `zero()` still uses `_from_coordinate_datum` directly.

With that, membership with several generators is decided: in `Gamma(ZZ[x, y])`, `x`, `y`, `x*y`, `x*x` and `x^2 y` are in the subalgebra generated by `x` and `y`, while `gamma_2(x)` and `gamma_2(x) + gamma_2(y)` are not (a degree-two word is a multiple of `2 gamma_2(x)`, `x*y` or `2 gamma_2(y)`); over `QQ` both divided powers *are* generated. `tests/algebras/test_generated_subalgebras.sage` carries both fields, and the file's tests plus `tests/algebras/test_power_algebras.sage` pass together (11 passed).

**Not introduced:** a `Subalgebras(A)` category. The generated subalgebra is the existing predicate-subring vehicle over `R`, so its points are ambient elements and its inclusion is the ambient embedding; a first-class `Subalgebras(A)` whose inclusion is an *algebra* morphism, and which can carry the induced multiplication as its own datum, is the next owner step and is not faked here by a special object.

### Towards a first-class `Subalgebras(A)`: what is verified, and where it stops (2026-11-01)

The categorical contract is the reason this is not finished: a subobject is an object of the ambient category carrying its inclusion as data (`ARC-07`, `OWN-15`) — `Subgroups(G)` returns a group with `inclusion(): H -> G`, `ModuleSubobjects(R)` a module with an inclusion — so `Subalgebras(A)` must return an object of `Algebras(R)` whose `inclusion()` is an element of `Algebras(R).Mor(sub, A)`. The accepted arithmetic membership is a *consequence* of that object, not a predicate carrier standing in for it.

**Reused, and verified on the specimen.** The degree pieces are the **images** of the word morphisms, taken through the maintained `ModuleMorphismMethods.image_factorization()`: `F(words_d) -> A_d` factors as an epimorphism onto `W_d` and an inclusion `W_d -> A_d`, and `W_d` is a genuine `ModuleSubobjects` object for the free, the ideal (degree zero) and the presented cases alike. With `W = GradedModules(R)(family, componentwise_framing=True)` and the product transported through those inclusions,

```python
component_product(i, x, j, y) = read_into(i+j, A(i,x) * A(j,y) at degree i+j)
```

`_algebra_on_module` builds the algebra, `W.graded_piece(1)` is the rank-one image of `⟨x⟩`, and `inclusion()` — built by `_constructed_algebra_morphism` — has domain the subalgebra and codomain `Γ(ℤ[x])` exactly. Membership through the retained inclusions reproduces the accepted answers (`x*x ∈`, `2γ₂ ∈`, `γ₂ ∉`, `0, 1 ∈`).

**Where it stops.** Coercing an element of a degree piece into the algebra's own `graded_piece(d)` — the graded sum's element constructor path — rejects the image element: `TypeError: [0] does not describe an element of Free module on {[x]}` raised from `graded_direct_sums.py:34` in `GradedDirectSumElement.__init__`. The piece the algebra exposes and the piece the *ambient* component constructor expects are two different modules here: `A.from_component(i, ·)` wants an `A_i` element, while the value reaching it is a `W_i` element, so the transport has to pass through `inclusion_i` at exactly the point the graded sum re-coerces, and that crossing is not yet stated. This is a construction-order defect, not a mathematical one: every mathematical fact above is already decided.

**State of the tree.** The accepted `subalgebra` remains the predicate-subring vehicle, and its tests pass (6 tests). The prototype of the first-class object is kept out of the tree (`.scratch/subalgebra-firstclass-prototype.py`) rather than left half-wired, because a `subalgebra` that returns an object whose own `from_component` is broken would be worse than the accepted one. The next unit picks up exactly the crossing above: the graded sum's `graded_piece` and the subalgebra's per-degree image must be *the same object* at the point of coercion, and `inclusion_i` must be the transport.

### First-class `Subalgebras(A)`: the integral crossing solved, the rational one open (2026-11-01)

The graded-component crossing recorded above is solved for the integral specimens by using the inclusion explicitly at the boundary, exactly as the contract requires: `_graded_multiplication_from_components` hands `component_product(i, x, j, y)` elements of the *subalgebra's* pieces `W_i`, `W_j` and expects an element of `W_{i+j}`, so the factors are placed in the ambient algebra by `inclusion_i`, multiplied there, and the product's `(i+j)`-component is read back through `inclusion_{i+j}`. The two carriers are never identified and no coercion is widened.

Verified on `Gamma(ZZ[x])`, through `GeneratedSubalgebras(ZZ)` (tracked in `categories/algebras/subalgebras.py`, not yet wired): `inclusion()` is an algebra morphism with domain the subalgebra and codomain the ambient algebra, `inclusion(1_W) = 1_A`, `inclusion(a*a) = inclusion(a)*inclusion(a) = 2 gamma_2(x)`, `1_W * a = a`, and membership through the retained inclusions answers `x*x in`, `2 gamma_2 in`, `gamma_2 not in`, `0,1 in`.

**What remains open is the rational degree-zero piece.** Over `QQ` the degree-zero image is a finitely presented module where the integral case yields the ideal `(1)`, and membership then raises `[0] does not describe an element of Ideal (1) of Integer Ring`; the rational specimens fail through the first-class object while they pass through the accepted one. So `Algebras.ParentMethods.subalgebra` still returns the accepted predicate subring — no specimen loses its acceptance — and both builders are tracked in the same module, the first-class one named `_generated_subalgebra_first_class` with this state in its docstring, so the source cannot die in scratch. The next step is the rational degree-zero image: the same `is_in_image` decision has to be reached through the presented piece rather than through an ideal, and then the two builders collapse into one.

### First-class `Subalgebras(A)` accepted: both characteristics (2026-11-01)

The rational crossing is closed, and with the retained base-ring and image-factorization contracts rather than around them. `ModuleMorphismMethods.image()` sends the image of a map into the regular module of a commutative ring to that ring's `ideal(...)`; over `QQ` the degree-zero piece is instead a **localization** of a `ZZ` module, whose element constructor takes elements of its numerator module (`Ideal (1) of Integer Ring`), not of the rational piece. Reading the ambient `1` into it was therefore a carrier identification the two objects do not have — `TypeError: [0] does not describe an element of Ideal (1) of Integer Ring` from `read_into(0, ...)`.

The repair keeps the carriers distinct: the unit is `W_0`'s own canonical generator (the image of the empty word), never an ambient element read back, and every other read-back goes through `inclusion_{i+j}` as before. With that, `Algebras.ParentMethods.subalgebra` returns the first-class object for both characteristics, the superseded predicate builder is gone, and the two builders are one.

Accepted on four specimens — `ZZ` and `QQ`, one and two generators — with the inclusion an algebra morphism in every case: `inclusion(1_W) = 1_A`, `inclusion(a*a) = inclusion(a)*inclusion(a) = 2 gamma_2(x)`, `1_W * a = a`, and membership answers `gamma_2(x) not in` over `ZZ` and `in` over `QQ`, with `x*y in` and `gamma_2(x)+gamma_2(y) not in` (`ZZ`) / `in` (`QQ`) for two generators. `tests/algebras/test_generated_subalgebras.sage` (7 tests, both characteristics) and `tests/algebras/test_power_algebras.sage` (5 tests) pass together: 12 passed, test lint clean.

### Cells 18 and 21 now have their multiplication regressions (2026-11-01)

The gap recorded with the acceptance matrix is closed: the display tests state how these lattices print, not the products the cells assert, and those were verified only by probes. `tests/lattices/test_issue614_products_over_orders.sage` states them with the notebook's own objects and unchanged assertions — `K = QuadraticField(2, "a")`, `a = K.algebra_generator("a")`, `O = K.maximal_order()`, `L = Lattices(O)([[2, a], [a, 2]])` with `u*u = 2`, `u*v = a`, `v*v = 2` and the Gram tensor's type; `Lattices(O)(O**2)` with `e*e = 1`, `e*f = 0`, `f*f = 1`; and `Lattices(Oi)(Oi**2)` over `ZZ[i]` with `ei*ei = 1`, `ei*fi = 0`, `fi*fi = 1`. The same gap covered the notebook's earlier identity lattices, so cells 7, 11 and 14 are stated there too: `Lattices(ZZ)(ZZ**2)` with the chosen frame (`linear_combination({0: 1}) = e`, `linear_combination({1: 1}) = f`) and the three products; `Lattices(QQ)(QQ**2)`; and `Lattices(K)(K**2)` over `QQ(sqrt 2)`. Six tests, passing, test lint clean. The two display regressions are unchanged and still carry the display half.

### The ordinary and the divided-power ideal of a graded power algebra (2026-11-01)

`tests/algebras/test_free_algebra_archive_reconciliation.sage` — imported from the research archive at `14b9cc1`, so not a test written for this tree — had two failures on `a0890d7`, and both were owner defects.

**1. `Gamma(M)` had no ideal at all.** `divided.ideal([2*x])` reached `OwnedRings.Commutative.ParentMethods._ideal_generated_by` → `_commutative_ideal` → `_placed_commutative_ideal`, whose identity-source branch asserts the source is a quotient ring and died with

```
AssertionError: cannot construct a presented ideal of Gamma(Free module on {[x]} over Integer Ring): no selected exact source algorithm supplies its ordered relations
```

That owner needs the ordered relations of a quotient source; `Gamma(M)` is assembled from its graded pieces and has none. The earliest correct owner is the graded structure itself: an ideal generated by *homogeneous* elements is graded, `I_d = sum_{i+j=d-1} A_i K A_j`, so each degree is the **image** of the retained products and membership is the maintained `is_in_image` of a framed module morphism — no second normal-form algorithm. `categories/algebras/algebra_ideals.py` states the object (`GeneratedAlgebraIdeals`, super-category `GradedModules(R)`: `ambient_algebra`, `generators`, `degree_inclusion(d)`, `inclusion()`, `in`), `_PowerAlgebra._ideal_generated_by` supplies it for both `Gamma` and `Lambda`, and the graded sum is built exactly as `GeneratedSubalgebras` builds its pieces (`GradedModules(R)(family, componentwise_framing=True)`, one cached subobject per degree, because the graded sum re-coerces into `graded_piece(d)`).

Two smaller facts this needed. An element of the ideal is not an ambient element: `piece.module_generator(label)` is the *subobject's* element and reaches `A_d` only through `degree_inclusion(d)` (`TypeError: [0] does not describe an element of Free module on {['x'^2]} over Integer Ring` if it is passed to `from_component` directly). And `inclusion()` is built with `from_maps(ambient, indexed_family(monoid, degree_component_inclusion))`, i.e. as the unique map whose restriction to each summand is that degree's inclusion followed by the ambient placement.

**2. The divided-power ideal is a strictly larger ideal and had no name either.** `Gamma` is not `Sym` and its presentation states divided relations, so the ideal generated by `2x` in `Gamma(ZZ x)` is two different objects:

| degree | ordinary `(2x)` | divided-power ideal `(2x)` |
|---|---|---|
| 1 | `2 ZZ x` | `2 ZZ x` |
| 2 | `4 ZZ gamma_2(x)` | `4 ZZ gamma_2(x)` |
| 3 | `6 ZZ gamma_3(x)` | `2 ZZ gamma_3(x)` |

`gamma_3(2x) = 8 gamma_3(x)` is a divided power of the generator, so it is in the second and not the first; `6 gamma_3(x) = 2x * gamma_2(x) = x * 2x * x` is in both; `4 gamma_3(x)` is in the divided-power ideal and not the ordinary one; `7 gamma_3(x)` is in neither. `DividedPowerAlgebras.ParentMethods.divided_power_ideal` names it, `ideal` is the ordinary one, and `is_divided_power_ideal()` distinguishes the two objects because `repr` would otherwise be the graded sum's own "Direct sum over Integer Ring" for both (the repr now states the flavor, the generators and the ambient algebra).

The separation is arithmetic, and `QQ` proves it: there `2` is a unit, `8 gamma_3(x) = 2 (4 gamma_3(x))`, and the two ideals agree in every degree — asserted in the same file so the specimen cannot pass for a construction that just differs by name.

**Misses, stated as scoped and dated.** `ideal_generators_in_degree` exists only on `GradedFreeAlgebras.ParentMethods` and is *not* reachable on `Gamma(M)` (`AttributeError: ... has no attribute 'ideal_generators_in_degree'. Did you mean: 'divided_power_module'?`): the two families are the presented free algebra on a module presentation (which carries `relations`) and the graded sum of module powers (which carries frames). The new module states the degreewise family for the second and does not call the first. Also not decided here, and refused rather than approximated: a generator outside degree one (`NotImplementedError`, naming its degree), and reading an ambient element *into* the ideal without deciding its membership (elements of the ideal come from `from_component`; `in` is the membership question, as for every other subobject).

**3. A dictionary of generator images keyed by the generators themselves.** The archive test writes the universal property of `Sym` literally — `x |-> v, y |-> w` on the elements — and `FramedFreeAlgebraMorphism.__init__` read a dict only by *label*: `ValueError: the images of the algebra generators of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring must be given for every generator, but ['x', 'y'] are missing`, although the dict held exactly those two generators. The selected generating family stores labels (`{'x', 'y'}`) for the same generators `algebra_generator(label)` returns, and a caller must not have to know which vehicle the chosen family uses. `_generator_images_by_label` (shared by `FramedFreeAlgebraMorphism` and `SparseFreeAlgebraMorphism`, in this order: labels first and free of charge, then a generator-to-label map, and anything else left to the missing-generator diagnostic) accepts both keyings, and two different images for one generator are refused. A dict keyed by `Gamma`/`Lambda` elements cannot arise — those element classes are unhashable — so the element keying is the native free algebra's, and the label path is unchanged for every existing caller.

**Tests.** `tests/algebras/test_generated_ideals_of_graded_algebras.sage` (9 tests): the `2x` specimen over `ZZ` and over `QQ`, the ordinary ideal's degree pieces read through the retained inclusions, the inclusion being the identity on its elements in degrees 1, 2 and 3, `(x)` in `Lambda(ZZ x, y)` being two-sided (`x wedge y` in, `y` not), a degree-two generator refused, the empty family giving the zero ideal, and the element-keyed/label-keyed/mixed generator images of a `QQ[x, y] -> QQ[u, v, w]` map agreeing on `x^2 y + 3`.

**A display trap this cost one round of debugging: `Gamma` and `Gamma^d` print alike.** `gamma_2(x)` as an element of the algebra and `gamma_2(x).homogeneous_component(2)` as an element of `Gamma^2` both print `['x'^2]`, and they are different parents, so `piece_element == algebra_element` is `False` while both sides of the assertion look identical in the message. A graded sum and its summand are not identified: compare in the piece (`homogeneous_component(d)`) and place through `degree_inclusion(d)` or `from_component(d, ·)`.

**Pre-existing failure in the same group, not this unit's and not repaired here.** `tests/algebras/test_sparse_algebra_module_construction.sage::test_generators_of_orders_two_and_three_multiply_to_zero` fails on a clean worktree at `a0890d7` (verified in `../head-wt`, `1 failed in 3.11s`), so the repair above neither caused nor fixed it: for `torsion = coker(diag(2,3))`, `torsion.tensor_algebra()` and `torsion.symmetric_algebra()` are `Owned_WordFramedPresentedAlgebra`, which has `algebra_generator('x')`, `graded_piece(1)` and `from_component(1, ·)` but no `degree_one_generator` (`AttributeError: ... has no attribute 'degree_one_generator'. Did you mean: 'degree_on_module_generator'?`). Beyond the missing accessor — which the power algebras state, and which `GradedFreeAlgebras.ParentMethods` could state as `from_component(1, generating_module().module_generator(label))` — the test asks for labels `0` and `1` while this algebra's selected frame is `{'x', 'y'}` (`ValueError: 0 is not a selected generator label of ...`). So the README-level question is the label vocabulary of a word-framed presented algebra, not the arithmetic: a rank the frame does not state, or the labels it does. That decision is left open, dated 2026-11-01, with both readings written down rather than one guessed.

### The polynomial ring and the symmetric algebra of the plane are two objects (2026-11-01, pre-existing, open)

`tests/objects/test_symmetric_algebra_of_qq2.sage` fails 5 of its tests, and the same identity breaks 13 tests across six files. The specimen is one line:

```python
assert symmetric() == QQ.polynomial_ring(("x", "y"))   # False
```

Both sides are the *same* construction from the same datum: `type(...)` is `Owned_NativeFreeAlgebraParent_with_category` for both, `generating_module()` is the same `Free module on {[x], [y]} over Fraction Field of Integer Ring`, the selected frame is the same `{'x', 'y'}` for both, and `x*y` prints `x*y` on both sides. They are still two parents, `a is b` and `a == b` both `False`, because the native free algebra is built per call instead of being cached by its datum -- the rule `_placed_commutative_ideal` already states ("two calls that write the same generators in the same placement name one subobject and get one object"). The same defect makes `QQ.polynomial_ring(("x", "y"))` and `Modules(QQ).free_module(("x", "y")).symmetric_algebra()` mutually unusable as one object in the coproduct, endomorphism and graded-piece tests of `test_symmetric_algebra_of_qq2.sage`, `test_morphisms_of_presented_commutative_algebras.sage`, `test_tensor_and_symmetric_algebras_of_the_plane.sage` and `test_functor_adjunctions.sage`.

A second symptom of the same construction: both print as `Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring`, i.e. the algebra's display is the coproduct frame's, not the `QQ[x, y]` that `_set_owned_ring_display` sets for the finite-label path.

Pre-existing and scoped: the FAILED set on a clean worktree at `a0890d7` is byte-identical to the set with `da2cd8a` applied (13 failed, 13 passed, same test ids, compared as sorted lines), so this unit's graded-ideal work neither caused it nor is blocked by it. Not repaired here; the owner fix is to cache the native free algebra by its datum so one construction is one object.

### A supplied stable containing bound made the finiteness query dead (2026-11-01)

Two consumers asked whether their group is finite although the conjunction's *other* operand already decided the branch, so with a stable containing bound supplied the answer was computed and thrown away.  Both sites, before:

```python
# categories/rational_integral_stabilizers.py, invariant_module_construction
if group.is_finite() is not True and containing is None:      # <- asked first
    assert False, "…requires a known finite group or a justified finite stable containing module…"
return GObjects(group, Modules(ring)).orbit_generated_submodule(..., containing=containing)

# categories/modules/orbit_spans.py, OrbitSpanConstructions._call_
if group.is_finite() is True and containing is None:          # <- asked first
    span = ambient.subobject_on(...)                          # finite fast path
else:
    if containing is None: raise NotImplementedError(...)     # bounded ascending chain
```

Python evaluates left to right, so the finiteness query runs before the operand that decides it.  With a bound the result is `False` at both branches whatever the group's order is, and the bounded `else` branch is taken either way.  Without a bound the query is *required*: it decides between unbounded orbit closure and refusing.

**Why this hurts.** `_finiteness_decision` returns the retained `OwnedFiniteGroups()` / `OwnedInfiniteGroups()` placement when one exists and otherwise falls through to `_engine_finiteness(_engine_group(self), compute=True)`, i.e. GAP `IsFinite` over the group's generators.  For the indefinite orthogonal groups a lattice consumer works with that is not cheap: the port's `cProfile` of one pointed-isometry unit measured **27.44 s of a 56.12 s unit** inside this one query (`libgap_mixin.py:181 is_finite` <- `_engine_finiteness` <- `_finiteness_decision` <- `is_finite` <- `invariant_module_construction`), for an answer the branch above discards.  That is the port's measurement of one unit, and it is *not* evidence that this query alone causes a larger run's memory failure; the defect recorded here is the lost premise, not a diagnosis of that run.

**Repair: evaluation order, not assumption.**  Both sites now read `if containing is None and <the finiteness test>`.  The truth value of a conjunction of two pure predicates does not depend on their order, both branches stay as they were, and the query still runs wherever it can change the result.  No finiteness assumption is introduced, `IsFinite` is not bypassed, and the caller's responsibility -- supplying a justified stable containing bound -- is unchanged.

**Verified independently of the port's profile**, on `U` over `QQ`, the isotropic line `ZZ e_0`, the supplied subgroup `⟨swap⟩` and the stable bound `ZZ e_0 + ZZ e_1` (a call counter on `is_finite`):

| call | `is_finite` queries before | after |
|---|---|---|
| `invariant_module_construction()` with the bound (both sites on the path) | 2 | **0** |
| `invariant_module_construction()` with no bound | 2 | 2 |
| `orbit_generated_submodule(..., containing=bound)` alone | 1 | **0** |
| `orbit_generated_submodule(...)` with no bound | 1 | 1 |

and the answer provably cannot matter: with the bound attached, forcing `is_finite` to `True` and then to `False` builds the *same* span (compared on the orbit images, since elements are unhashable and two separately built spans are different parents), while with no bound and `is_finite` forced `False` the construction still refuses with "requires a known finite group or a justified finite stable containing module".  `tests/lattices/test_finiteness_premise_under_a_containing_bound.sage` states all of that, five tests.

**Two stale-test facts this surfaced, both pre-existing.**  `tests/lattices/test_integral_stabilizers.sage` was failing on `space.submodule(...)`, which no module has (the maintained name is `subobject_on`), and on `O({e0: e1, e1: e0})`, whose keys are unhashable lattice elements -- an owned isometry is written as a function on the lattice's module generators, `O(lambda label: ...)`.  It also built the *whole* rational `O`, which supplies no finite generating set: `stabilizer()` needs one and the integral generator algorithm asserts instead (`the indefinite orthogonal-group algorithm computes O(L) for integral lattices over ZZ, but Lattice of rank 2 and signature (1, 1) is over Fraction Field of Integer Ring`).  The file is rewritten in that vocabulary with its four assertions unchanged -- supplied subgroups, `subobject_on`, isometries as functions on labels, `(QQ(1)/QQ(2)) * e1` rather than `e1 / 2` -- and passes, 2 tests.

**Repaired (2026-11-01, commit on top of `00bcc86`): the label set is interned, so the tower is one object.**  The owner of the identity is the *set* constructor, not the module constructor: `_owned_free_module_on` keys on the identities of the ring and the label set, and the polynomial route already interned its variables by ordered names (`_named_polynomial_variables`) while the free-module route built a fresh `finite_ordered_set` per call.  `sets.finite_ordered_sets.interned_finite_ordered_set` is now the single intern (by the ordered tuple of labels), `interned_labels` guards it for unhashable points, both routes call it, and `QQ.polynomial_ring(("x","y")) is Modules(QQ).free_module(("x","y")).symmetric_algebra()` is `True`.  Measured on nine files that build these algebras: 24 failed / 22 passed before, 20 failed / 35 passed after (the extra 9 are the new test), **four fixed and none introduced** — `test_polynomial_ring_qq_x::test_the_polynomial_ring_is_the_symmetric_algebra_of_a_line`, `test_symmetric_algebra_of_qq2::{test_the_symmetric_algebra_is_the_polynomial_ring, test_the_graded_pieces_of_the_symmetric_algebra, test_the_functor_and_the_object_constructions_agree}`.  The remaining six in that group (categories, endomorphism category, the points over `QQ`, de Rham) are a different defect and stay open.  Interning is by ordered labels, never by extensional equality: a family of unhashable points keeps its own identity (two such modules stay two), and an ordinal card `2` is not the explicit tuple `(0, 1)`, because the selected basis is the set object; `tests/algebras/test_one_construction_per_label_set.sage` pins all of it, four tests.

### The graded identity, and the name `Algebras` in a `.sage` test (2026-11-01)

Two evaluator-visible defects, both reached from `test_the_categories_of_qq_x` and the two `..._has_one_endomorphism_category` tests.

**1. `id * id` was a fresh morphism, in a graded algebra.** `GradedAlgebraMorphism.__mul__` composed through `MultiplicativeAlgebraMorphism.__mul__` — which already returns the other factor when one is the unit — and then re-lifted that answer into a new graded morphism. So `identity * identity` was a *different* object, and `==` on it produced `equal(Generic endomorphism of …, Generic endomorphism of …)`, a proposition with no truth value: `TypeError: the proposition equal(...) has no Python truth value`. The unit law is a theorem, not a comparison; the composite is returned as it is when the shared composition already answered with a factor, and `_from_degree_preserving_underlying_morphism` no longer drops `_preamble_is_identity` when it lifts one (an unmarked lift of the identity was the reason `GradedAlgebraMor.identity()` came back unmarked at all). `identity * identity is identity` is `True` for `QQ[x]`, `Sym(QQ^2)` and `T(QQ^2)`.

**2. A bare `Algebras` in a `.sage` test is Sage's class, not this library's.** The pytest plugin `qc_sage_session` (`tool-artifacts/pytest_plugins/qc_sage_session.py:39`) injects every non-private name of `sage.all_cmdline` into the test module's scope, and this session deliberately does not export catalogue constructors. So `Algebras(QQ)` in such a file constructed **Sage's** `Algebras` with this library's owned `QQ` as base, and Sage rejects it: `ValueError: base must be a ring or a subcategory of Rings()` (checked with `base in sage.categories.rings.Rings()`; the owned `Fraction Field of Integer Ring` is not a Sage ring). The same statement failed as `KeyError: ((<class 'sage.categories.magmatic_algebras.MagmaticAlgebras'>, Fraction Field of Integer Ring), ())` when Sage's `Category.__classcall__` cache missed instead — one cause, two symptoms, depending on what ran before in the session. The repair is vocabulary, not modelling: the file imports the owned `Algebras` explicitly, so the assertion states what it means (this library's `QQ[x]` is an algebra over this library's `QQ`), and nothing makes an owned ring pretend to be a Sage ring. Other archive-imported tests using bare base-parameterized Sage categories have the same latent defect; only the two files this unit touches are corrected here.

Measured on the seven files that build these algebras (`tests/objects/test_polynomial_ring_qq_x.sage`, `test_symmetric_algebra_of_qq2.sage`, `test_tensor_algebra_of_qq2.sage`, `test_exterior_algebra_of_qq2.sage`, `tests/algebras/test_morphisms_of_presented_commutative_algebras.sage`, `test_one_construction_per_label_set.sage`, `tests/rings/test_commutative_algebra.sage`) against a clean worktree at the published `cdafca8`: **33 failed / 32 passed → 29 failed / 36 passed, four fixed, none introduced** (`test_qq_x_has_one_endomorphism_category`, `test_the_categories_of_qq_x`, `test_the_symmetric_algebra_has_one_endomorphism_category`, `test_the_tensor_algebra_has_one_endomorphism_category`). The other 29 failures in that set — the localization, Fitting, Nakayama, fiber-rank, coproduct and pushout tests in `test_commutative_algebra.sage` among them — are unchanged by this work and stay open.

**Open naming question this raised, recorded rather than decided.** The test lint asks for `TL01 from … import …: take every name from the session`, i.e. it wants tests to use the session names — but this session deliberately exports no catalogue constructors, so the only way two files can state the *owned* `Algebras` is an explicit import, which TL01 flags. Exporting `Algebras` in `all.py` would make the bare name in every `.sage` file mean this library's category instead of Sage's (today the pytest plugin supplies Sage's), which is a suite-wide semantic change and is not made here on the back of a two-file vocabulary repair. Recorded as the decision it is: local explicit imports now, one session-export question for the owner.

### The affine line's de Rham cohomology is past a stated owner limit (2026-11-01, open, not a defect to guess at)

`tests/objects/test_polynomial_ring_qq_x.sage::test_the_de_rham_cohomology_of_the_affine_line` asserts `de_rham.cohomology(0).module_rank() == 1` and `cohomology(1).cardinality() == 1` for `QQ[x]`, and fails further down than the de Rham algebra itself:

```
cohomology(0) -> _cohomology_along -> cycles(0) -> differential_component(0).kernel()
AssertionError: cannot compute the kernel of Free module on {[0]} over
  Free module on Coproduct of the family over NN = {0, 1, 2, ...} over QQ
  restricted to Fraction Field of Integer Ring
-> Free module on {[('d', 'x')]} over the same restricted module:
  no algorithm is available for these modules
  (domain and codomain both in Join of restricted-scalars modules over QQ and vector spaces over QQ)
```

The algebra and its Kähler differentials are fine — `test_the_kahler_differentials_of_qq_x` passes (`module_rank() == 1`, `d(x^3) = 3 x^2 dx`). What fails is the **cohomology owner**, and the library already says why, in `DeRhamAlgebras.an_object`'s own docstring: "A polynomial algebra over `R` is infinite as an `R`-module, while the current cohomology owner retains finite presentations of cycles and boundaries. The selected quotient `R[x]/(x^2)` is still nontrivial Kähler calculus and is finite free over `R`."

So this is a stated boundary, not a mis-construction: `QQ[x]` is infinite-dimensional, its graded pieces are not finitely presented, and `ModuleMorphismMethods.kernel` has no algorithm for the restricted-scalars modules they become. Two honest routes exist and neither is taken here: extend the cohomology owner to non-finitely-presented pieces (a feature, with its own design and acceptance), or state a finite specimen — but `H^0_{dR}(A^1) = QQ`, `H^1_{dR}(A^1) = 0` is the mathematical claim the test makes, and replacing `QQ[x]` by `QQ[x]/(x^2)` would change what it asserts, so it is left failing rather than rewritten. Recorded as the next unit in this file with its exact chain.

**The same bare-`Algebras` vocabulary defect in `tests/rings/test_commutative_algebra.sage` (2026-11-01).** Three sites there write `Algebras(QQ).Associative().Unital().Commutative()` for a spectrum, a pushout and a coproduct; under pytest the name is Sage's class (`qc_sage_session` injects `sage.all_cmdline`) and each site constructed Sage's `MagmaticAlgebras` over the owned `QQ`, failing as `KeyError: ((<class 'sage.categories.magmatic_algebras.MagmaticAlgebras'>, Fraction Field of Integer Ring), ())` — the cache-miss variant of the pair recorded above. With the owned `Algebras` imported the file goes 16 failed / 9 passed → **15 failed / 10 passed**, one fixed (`test_commutative_algebra_pushout_imposes_common_source_relations`), none introduced; the spectrum and coproduct tests at the other two sites keep failing for their own reasons.

**Next defect in that file, named with its owner: `direct_sum_of_cyclics` is on the torsion branch only.** Five tests fail with `AttributeError: 'Modules_with_category' object has no attribute 'direct_sum_of_cyclics'`. The construction exists — `categories/modules/pure/modules.py:3245`, on `Modules(R).FinitelyPresented().Torsion()` — and the library itself calls it through that path (`discriminant_modules.py:653`, `module_morphisms.py:1394`), while the tests call it on `Modules(R)` directly. Whether the method belongs on the general module category (a direct sum of cyclics is built from orders, not from a presentation) or the tests should state the torsion refinement is an owner decision, not a guess: it is recorded here rather than moved, because widening a construction's placement changes what every caller may ask of it.

**Recursion broken: a local construction must state that its maximal ideal is nonzero (2026-11-01).** `test_formal_power_series_ring_is_complete_local_over_a_field` died with `RecursionError` and a 69-deep `KeyError: (<id>, <id>)` chain, whose innermost frame is the real story:

```
_maximal_ideal_over_local_base
 -> algebra.completion_map().extension_of_ideal(source_ideal)
   -> _flat_extension_commutative_ideal -> source_ideal.base_change(morphism)
     -> _framed_free_base_change -> target_ring._fresh_free_module_on(...)
       -> _new_sparse_free_module -> _finitely_generated_free_placement
         -> `if ring in OwnedFields():`          # the power series ring
           -> OwnedRings.Division.__contains__ -> candidate._field_decision()
             -> construction.maximal_ideal()     # back to the first line
```

Choosing a placement for a free module asks whether its coefficient ring is a field; for a local ring that decision asks whether the maximal ideal is zero; the power series ring's maximal ideal is built by extending an ideal along the completion map, which builds a free module over the same ring. The library already has the seam for this — `LocalRings._field_decision` reads `construction.maximal_ideal_is_zero_decision()` first, and its docstring states the circle for prime localizations — but the two constructions over a *local base* stated nothing, so they fell to the ideal route. They now state `maximal_ideal_is_zero=False`: the formal parameters and the dual-number `epsilon` generate the maximal ideal and are not zero. `tests/rings/test_commutative_algebra.sage` goes 15 failed / 10 passed → **14 failed / 11 passed**, that test fixed, none introduced.

**Next in that file, named not guessed.** `test_quotient_residue_field_dual_numbers_and_adic_completion` fails on `tbar**2 == 0` in `(Z/5)[t]/(t^2)`: the class of `t` squares to something printing `t mod Ideal (t^2) of Free module on Coproduct … over Integer Ring / Ideal (5) of Integer Ring ** 2`, i.e. the reduction by `t^2` does not reach zero in this two-step quotient — quotient arithmetic, a different owner from the local-ring construction above.

**A quotient element is not equal to a scalar zero of its coefficient tower (2026-11-01, open, reproduced).** `test_quotient_residue_field_dual_numbers_and_adic_completion` fails on `tbar**2 == 0` in `(Z/5)[t]/(t^2)`, and the whole file's arithmetic is fine. Inside the pytest `.sage` environment the two sides are:

```
POWER is zero            True
POWER == quotient.zero() True
POWER == 0               False          # <- the assertion
EXPONENT type            _OwnedRingParent_with_category.element_class
```

The Sage preparser turns the literal `0` in a `.sage` file into this library's `ZZ(0)` (`Integer` in the module's builtins is Sage's, but the preparsed literal goes through the session's `ZZ`), so the comparison is **quotient element vs an owned element of `ZZ`, one step up the coefficient tower** — not vs a host `int`. The minimal reproduction, provider-only, no pytest:

```python
quotient = GF(5).polynomial_ring("t").quotient_ring(t**2)
quotient.zero() == 0        # True   (host int coerces)
quotient.zero() == ZZ(0)    # False  (owned ZZ zero does not)
quotient.zero() == QQ(0)    # False
quotient(5) == 0            # True
```

So `ZZ -> ZZ/5 -> (Z/5)[t] -> (Z/5)[t]/(t^2)` is a chain of maps the ring carries, but the comparison against an element of its *bottom* ring answers `False` instead of coercing along it — the same family as the exact-literal comparison recorded for `ZZ[x]` at `(x)`, where an exact operand from another owned ring stops the numeric route. Nothing here is a preparation artefact to be worked around in the test: `t**2 = 0` in that quotient is the assertion's mathematical content, and the comparison is what is wrong. Not repaired here: the owner is the ring comparison across the registered scalar tower (coerce the exact scalar, then compare classes), which needs its own change and its own regression rather than a test-side `== quotient.zero()`.

**The scalar tower does not reach a quotient ring at all (2026-11-01, open, localized).** The `tbar**2 == 0` failure is a coercion defect, not arithmetic, and it is sharper than "comparison against a scalar":

```
quotient = GF(5).polynomial_ring("t").quotient_ring(t**2)
quotient.has_coerce_map_from(polynomial)   False      # its own source
quotient.has_coerce_map_from(GF(5))        False      # its base ring
quotient.has_coerce_map_from(ZZ)           False      # the bottom of the tower
quotient.quotient_map()                    A -> A/(t^2), endpoints correct
quotient(ZZ(1))                             works      # explicit ingress only
tbar + 1                                   TypeError: unsupported operand type(s) for +: '...element_class' and 'int'
tbar + ZZ(1)                               TypeError: unsupported operand parent(s)
quotient.zero() == 0                       True       # host int: comparison path
quotient.zero() == ZZ(0)                   False      # owned scalar: no map, so "not equal"
```

So a quotient ring carries its quotient map and its explicit ingress, but registers **no coercion from its source**, and therefore none from anything its source coerces from: `ZZ -> ZZ/5 -> (Z/5)[t] -> (Z/5)[t]/(t^2)` is a chain the mathematics has and the coercion graph does not. `(Z/5)` alone shows the same (`GF(5).has_coerce_map_from(ZZ)` is `False`), so this is the quotient owner in general, not the two-step case: `QuotientRings` must coerce from its source along the retained quotient map, and then Sage's transitivity carries the rest. Nothing is repaired here — the change is central enough (every scalar operation on every quotient) to need its own unit and its own regression set — and the original `tbar**2 == 0` assertion is left exactly as written, since it is the comparison that is wrong.

### The quotient coercion seam: measured, with the two rules and why neither ships alone (2026-11-01)

The seam is exactly here: `QuotientRings.ParentMethods` declares **no** `_coerce_map_from_` — `[c.__name__ for c in type(quotient).__mro__ if "_coerce_map_from_" in vars(c)]` is `['Parent']`, the Sage default — while the native ring realization's `_OwnedRingParent._coerce_map_from_` answers `True` (the "the coercion exists, construct through the element constructor" convention). So `GF(5) = ZZ/(5)` reports `has_coerce_map_from(ZZ)` `False`, and `(Z/5)[t]/(t^2)` reports `False` for its source, its base and `ZZ`.

Two rules were written and measured, and **neither ships alone**:

| rule | `q == ZZ(0)` | `tests/rings tests/objects tests/algebras` |
|---|---|---|
| `source is self.quotient_source()` only | still `False` — Sage does **not** compose our `True`-style declarations into a `ZZ -> polynomial -> quotient` path | no change |
| that plus transitive `quotient_source().has_coerce_map_from(source)` | `True`, and `tbar**2 == 0` passes | **323 failed → 326 failed**: `test_localizations_of_the_integers::test_inverting_two_in_z_mod_six_leaves_z_mod_three` and `test_prime_localization_field_decisions::{test_a_generated_submonoid_localization_states_its_own_characteristic_and_size, test_the_localization_of_a_quotient_is_a_field_without_a_zero_prime}` regress, each as `localized.characteristic()` answering `None` where it used to answer `3`, `2`, … |

So admitting `ZZ` into a quotient is right, and it is not free: `LocalizationRings` decides a localization's characteristic from its source's tower, and once `ZZ` reaches a quotient the decision no longer reaches its answer (`AssertionError`/`None` at `tests/rings/test_prime_localization_field_decisions.sage` and `test_localizations_of_the_integers.sage`). The unit that lands the coercion must land the localization characteristic decision with it, under the same measurements; shipping the coercion alone would trade one visible defect for three, so the edit was reverted rather than committed. The `tbar**2 == 0` assertion remains as written and still fails; `has_coerce_map_from` remains `False` on every quotient.

**Placement of `(f)` in `k[t]`: the rule is right, the residue-field route is not ready (2026-11-01, measured, not shipped).** `test_quotient_residue_field_dual_numbers_and_adic_completion` now fails at `assert residue in LocalRings()` for `(Z/5)[t]/(t)`, and the library's own rule says why it is not there: `_quotient_ring` inherits a field placement *only from the ideal's construction category* ("never selected by asking its maximality/primality predicate", CON-07/ARC-08), and `polynomial.ideal(t)` places its ideal as a plain ideal. The theorem that would place it is one variable up from the rule already implemented for `ZZ`: for a field `k` and `0 != f` in `k[t]`, `(f)` is maximal exactly when `f` is irreducible (`k[t]` is a PID, `k[t]/(f)` a field exactly for a prime `(f)`; and `k[t]` is factorial, so the ideal's own generator is the normalized gcd of any written family).

That rule was implemented in `_commutative_ideal` and it works: `(Z/5)[t]/(t)` lands in `Local()` **and** `Division()`, cardinality 5, and `(Z/5)[t]/(t^2+t)` stays unplaced because `t(t+1)` is reducible. Measured on the same 158-file set against the published `c94af7b`: **324 failed / 450 passed** against 323 / 445, with one regression —

```
tests/rings/test_local_module_maps_frontier.sage::test_prime_local_units_and_residue_map_use_the_selected_local_ring
  point.residue_map()(x) == point.residue_field().zero()
  KeyError: 'quotient_map'
```

— i.e. a residue-field route that expects the placed ideal's construction data changed under it. One rule written in the wrong order cost a first measurement of 16 failures (`source.variable_names()` asked of rings that are not polynomial rings); that was fixed before the number above, and is recorded so the next attempt starts from the right guard order. The edit was reverted rather than shipped: the placement theorem and that residue-field route have to land in one unit, and the assertion `residue in LocalRings()` stays as written meanwhile.
