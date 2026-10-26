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
