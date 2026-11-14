# Triage of the failing tests of `tests/objects` on sage-extensions main (#408)

**Slice.** The 26 files of `tests/objects` up to and including
`test_isomorphisms_of_a_two_element_set.sage`, alphabetically. The files after it belong
to #412 and are not triaged here; the full-directory run recorded 136 failing tests, of
which 61 are in this slice's 26 files and 75 are in
#412's.

#403 (an `OwnedJoinCategory` has no `base_ring` for a join over a base ring) is already
filed. No failing test of this slice is that cause: no record of the slice names
`base_ring`, in the error or in the call that raised it.

## The run

One run on main `9b297125b3726d6e6b5f548f2ad3ef01c7933029` (2026-11-14) in the published
image, one file per pytest process, since other triage sessions were running other
slices of the same suite on this VM at the same time.

`just test <path>` is the repository's own invocation (`justfile`, delegating to
`~/ai-review-ci/justfiles/sage.just`). Inside the image it is run as

```
~/sage-image/run.sh -w /work -b <port repo>:/work -b ~/ai-review-ci:/ci \
  -b <worktree>:/repos/sage-extensions -b <repo>/.git:<repo>/.git -- \
  /bin/sh -c 'export HOME=/root;
    export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src;
    cd /repos/sage-extensions; exec just test "$@"' sh \
  -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates --no-test-lint -q --tb=line <test file>
```

`addopts` is blanked and the two plugins reselected by hand because the image's virtual
environment has neither `pytest-timeout` nor `pytest-reportlog`, so the repository's own
`addopts` stop the run at `unrecognized arguments: --timeout=60
--timeout-method=signal --report-log=tests/.report/run.jsonl`. That is a defect of the
image, recorded so the invocation is reproducible. `--no-time-gates` and
`--no-test-lint` are the flags the issue records for the original run.

**Result.** 61 failing tests in 19 of the 26 files, assigned to 35 causes; every failing test of the slice is in exactly one cause.

| exception | tests |
| --- | --- |
| `TypeError` | 17 |
| `NameError` | 11 |
| `assert` | 10 |
| `AssertionError` | 10 |
| `AttributeError` | 9 |
| `ValueError` | 3 |
| `IndexError` | 1 |

## The causes

A cause is one defect of one call: tests are grouped when they fail at the same call
with the same error, not when they share a file. `also in #412` counts the failing tests
of the same defect that sit in files now belonging to #412.

| cause | defect | tests | also in #412 | introduced by | repair |
| --- | --- | --- | --- | --- | --- |
| C01 | The session namespace does not publish the constructors the suite names | 11 | 7 | `c731175` | repaired |
| C02 | The owned ring adapter has no constructor for the symbolic ring | 6 | 6 | `not bisected` | filed |
| C03 | The algebraic closure of a finite field is raised with the wrong constructor arity | 1 | 0 | `c731175` | repaired |
| C04 | The owned parent and element classes do not carry `is_isomorphic_to` | 1 | 6 | `55927425bcff` | filed |
| C05 | `Rings()` does not carry `initial_object` | 1 | 0 | `c731175` | filed |
| C06 | The owned subscheme surface does not carry `scheme`/`ambient_scheme` | 2 | 0 | `c731175` | filed |
| C07 | The owned free-algebra parent does not carry `domain` | 1 | 0 | `not bisected` | filed |
| C08 | The augmented simplex category's parent class does not carry `codomain` | 1 | 0 | `not bisected` | filed |
| C09 | Module elements do not carry `is_isometric` | 1 | 0 | `not bisected` | filed |
| C10 | An isomorphism category does not carry `order` | 1 | 0 | `not bisected` | filed |
| C11 | `NumberFields()` does not carry `ring_of_integers` | 1 | 0 | `c731175` | filed |
| C12 | `cardinality` refuses for the embedding set `Emb(L, L')` | 1 | 2 | `not bisected` | filed |
| C13 | `cardinality` refuses for a group whose finiteness is a `Predicate` | 1 | 2 | `c731175` | filed |
| C14 | A `Predicate` is evaluated as a Python truth value | 2 | 4 | `not bisected` | filed |
| C15 | `module_rank` refuses for a module over a non-field base | 2 | 1 | `c731175` | filed |
| C16 | A cone or cocone morphism is constructed with one cone | 4 | 0 | `not bisected` | filed |
| C17 | `GL` of a torsion module is refused | 1 | 1 | `not bisected` | filed |
| C18 | The metric dual is refused for a degenerate lattice | 1 | 0 | `not bisected` | filed |
| C19 | The whole-algebra map of an infinite-rank free algebra is refused | 1 | 0 | `not bisected` | filed |
| C20 | `WeilDivisorGroups._call_` is called without its defining data | 1 | 0 | `c731175` | filed |
| C21 | A cardinal sum over `ZZ` is not decided | 1 | 0 | `not bisected` | filed |
| C22 | Isomorphism of two free groups is undecided | 1 | 0 | `not bisected` | filed |
| C23 | The abelianization of a finitely presented group is refused | 1 | 0 | `not bisected` | filed |
| C24 | A GAP element index is out of range | 1 | 0 | `not bisected` | filed |
| C25 | `O(L)` of an indefinite lattice is refused | 1 | 0 | `not bisected` | filed |
| C26 | A base ring is refused as a field | 1 | 0 | `c731175` | filed |
| C27 | `/` is applied to owned module elements | 3 | 0 | `c731175` | filed |
| C28 | Two constructions of one lattice do not compare equal | 2 | 3 | `c731175` | filed |
| C29 | A direct sum is not an object of `DirectSumObjects(Lattices(ZZ))` | 1 | 1 | `c731175` | filed |
| C30 | A cone or cocone is not an object of its cone category | 2 | 0 | `not bisected` | filed |
| C31 | Two constructions of one functor do not compare equal | 2 | 0 | `not bisected` | filed |
| C32 | The assertion at `test_a_coordinate_line_in_the_affine_plane.sage:23` does not hold: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction  | 1 | 0 | `not bisected` | filed |
| C33 | The assertion at `test_affine_plane_over_qq.sage:15` does not hold: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring | 1 | 0 | `not bisected` | filed |
| C34 | `module_morphisms.py:1978` raises ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism: | 1 | 0 | `not bisected` | filed |
| C35 | The assertion at `test_integers.sage:28` does not hold: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring | 1 | 0 | `c731175` | filed |

## Each cause

### C01 — The session namespace does not publish the constructors the suite names

`from sage_extensions.all import *` binds a namespace that omits nineteen owned constructors the suite names: `AbsoluteGaloisGroup`, `AbsoluteGaloisGroups`, `AbsoluteGaloisGroupsOfFiniteFields`, `FinitelyGeneratedGroups`, `FinitelyPresentedGroups`, `ProfiniteGroups`, `AlternatingAlgebras`, `SymmetricAlgebras`, `TensorAlgebras`, `StrictlyGradedCommutativeAlgebras`, `FractionalIdeals`, `ModulesWithConnection`, `ModulesWithFlatConnection`, `FinitelyGeneratedModules`, `FinitelyPresentedModules`, `ProjectiveModules`, `TorsionModules`, `TensorProductModules`, `SymmetricBilinearFormModules`. A user who writes the session-standard import gets `NameError` for a constructor the library owns, and the repository's own test lint reports the same names as TL13.

Failing tests (11, 6 files):

- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_categories_of_the_absolute_galois_group`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_of_a_finite_field_is_zhat`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_frobenius`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_finite_quotients`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_has_one_endomorphism_category`
  `NameError: name 'AbsoluteGaloisGroup' is not defined`
- `tests/objects/test_cyclic_module_zz6.sage::test_the_categories_of_zz6`
  `NameError: name 'FinitelyPresentedModules' is not defined`
- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_categories_of_the_exterior_algebra`
  `NameError: name 'AlternatingAlgebras' is not defined`
- `tests/objects/test_fractional_ideal_2z.sage::test_the_category_construction_agrees`
  `NameError: name 'FractionalIdeals' is not defined`
- `tests/objects/test_fractional_ideal_2z.sage::test_the_categories_of_2z`
  `NameError: name 'FractionalIdeals' is not defined`
- `tests/objects/test_free_group_of_rank_two.sage::test_the_categories_of_f2`
  `NameError: name 'FinitelyGeneratedGroups' is not defined`
- `tests/objects/test_free_module_of_rank_three.sage::test_the_categories_of_zz3`
  `NameError: name 'FinitelyGeneratedModules' is not defined`

The same defect also fails 7 test(s) in files now belonging to #412: `tests/objects/test_root_lattice_a2.sage::test_the_categories_of_a2`, `tests/objects/test_symmetric_algebra_of_qq2.sage::test_the_categories_of_the_symmetric_algebra`, `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_categories_of_the_tensor_algebra`, `tests/objects/test_tensor_product_of_zz2_and_zz3.sage::test_the_categories_of_the_tensor_product`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_categories_of_the_module_with_connection`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_every_connection_on_a_line_over_a_curve_is_flat`, `tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_module_with_connection_has_one_endomorphism_category`.

- Defective call: `tests/objects/test_absolute_galois_group_of_f5.sage:5`, `tests/objects/test_cyclic_module_zz6.sage:29`, `tests/objects/test_exterior_algebra_of_qq2.sage:20`, `tests/objects/test_fractional_ideal_2z.sage:13`, `tests/objects/test_fractional_ideal_2z.sage:9`, `tests/objects/test_free_group_of_rank_two.sage:15`, `tests/objects/test_free_module_of_rank_three.sage:37`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: repaired in `57208eb`; tree-wide the session-namespace repair publishes nineteen constructors. In this slice's files: `test_fractional_ideal_2z`, `test_free_group_of_rank_two`, `test_free_module_of_rank_three`, `test_cyclic_module_zz6` and `test_absolute_galois_group_of_f5` go from failing to passing for this cause; `test_exterior_algebra_of_qq2` now fails at its next defect.

### C02 — The owned ring adapter has no constructor for the symbolic ring

Any construction whose coefficient ring is `SR` -- `PolynomialRing(SR)`, `LaurentPolynomialRing(SR)`, the character and translate families built over it -- raises `TypeError: cannot raise Symbolic Ring through an owned ring constructor` from `_owned_engine_ring`. A user cannot build the symbolic-coefficient rings the session namespace publishes names for.

Failing tests (6, 2 files: `test_fourier_characters.sage`, `test_hermite_polynomials.sage`):

- `tests/objects/test_fourier_characters.sage::test_the_characters_are_indexed_by_the_integers`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_fourier_characters.sage::test_the_categories_of_the_characters`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_fourier_characters.sage::test_the_characters_are_countably_many_and_distinct`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_polynomials_are_indexed_by_the_naturals`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_categories_of_the_hermite_polynomials`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`
- `tests/objects/test_hermite_polynomials.sage::test_the_hermite_polynomials`
  `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected`

The same defect also fails 6 test(s) in files now belonging to #412: `tests/objects/test_laurent_monomials.sage::test_the_monomials_are_indexed_by_the_integers`, `tests/objects/test_laurent_monomials.sage::test_the_categories_of_the_laurent_monomials`, `tests/objects/test_laurent_monomials.sage::test_the_laurent_monomials_multiply_by_adding_exponents`, `tests/objects/test_sinc_translates.sage::test_the_translates_are_indexed_by_the_integers`, `tests/objects/test_sinc_translates.sage::test_the_categories_of_the_sinc_translates`, `tests/objects/test_sinc_translates.sage::test_the_translates_are_countably_many_and_distinct`.

- Defective call: `src/sage_extensions/categories/rings/ring_foundation.py:7534`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C03 — The algebraic closure of a finite field is raised with the wrong constructor arity

`GF(p).algebraic_closure()` raises `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'`, because the owned adapter calls Sage's `AlgebraicClosureFiniteField(base_ring, name)` with a characteristic. A user cannot take the algebraic closure of a finite field at all.

Failing tests (1, 1 file: `test_absolute_galois_group_of_f5.sage`):

- `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_field_construction_agrees`
  `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'`

- Defective call: `src/sage_extensions/categories/rings/ring_foundation.py:7608`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: repaired in `6df56ad`; `GF(5).absolute_galois_group()` constructs, five of the six tests of `test_absolute_galois_group_of_f5.sage` pass, and the sixth fails at `ring_foundation.py:562` (its own next defect).

### C04 — The owned parent and element classes do not carry `is_isomorphic_to`

`is_isomorphic_to` -- the spelling `ring_foundation` already installs as an alias of `is_isomorphic` -- is absent from the owned parent and element classes of modules, schemes and sets, so `A.is_isomorphic_to(B)` raises `AttributeError` and Sage itself answers `Did you mean: 'is_isomorphic'?`. A user of the public spelling gets an attribute error on objects that do support the relation.

Failing tests (1, 1 file: `test_a_coordinate_line_in_the_affine_plane.sage`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_an_affine_line`
  `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?`

The same defect also fails 6 test(s) in files now belonging to #412: `tests/objects/test_projective_plane_over_qq.sage::test_the_projective_plane_is_glued_from_its_charts`, `tests/objects/test_projective_plane_over_qq.sage::test_the_standard_affine_charts`, `tests/objects/test_projective_plane_over_qq.sage::test_the_picard_group_and_the_canonical_bundle`, `tests/objects/test_regular_module_of_c2.sage::test_the_permutation_module_is_the_regular_module`, `tests/objects/test_regular_module_of_c2.sage::test_the_coinduced_module_is_the_regular_module`, `tests/objects/test_symmetric_group_s3.sage::test_the_automorphisms_of_a_three_element_set`.

- Defective call: `sage/cpython/getattr.pyx:357`.
- Introduced by: `git bisect` in the image on the signature `object has no attribute 'is_isomorphic_to'`; the first commit where it appears is `55927425bcff` -- fix: let the cached quotient-by-relations constructor read its keyword defaults (Zack Garza <dzackgarza@gmail.com>), in 12 bisect steps.
- Repair: open; filed as this cause.

### C05 — `Rings()` does not carry `initial_object`

`Rings().initial_object()` raises `AttributeError`; `initial_object` is written for `OwnedSemirings` (returning `NN`) and not for `OwnedRings`, so the initial ring `ZZ` cannot be named through the category that owns it.

Failing tests (1, 1 file: `test_integers.sage`):

- `tests/objects/test_integers.sage::test_the_integers_are_the_initial_ring`
  `AttributeError: 'OwnedRings_with_category' object has no attribute '_structured_category'`

- Defective call: `sage/cpython/getattr.pyx:362`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C06 — The owned subscheme surface does not carry `scheme`/`ambient_scheme`

A subscheme's `scheme()` and `ambient_scheme()` are absent from the owned subscheme parent (and its element class), so a user cannot ask a closed subscheme or a Cartier divisor which scheme it sits in.

Failing tests (2, 2 files: `test_a_coordinate_line_in_the_affine_plane.sage`, `test_divisors_on_three_points.sage`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_a_closed_subscheme_of_codimension_one`
  `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'ambient_scheme'`
- `tests/objects/test_divisors_on_three_points.sage::test_the_cartier_divisor_group_on_three_points`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'scheme'`

- Defective call: `sage/cpython/getattr.pyx:357`, `sage/cpython/getattr.pyx:362`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C07 — The owned free-algebra parent does not carry `domain`

`Spectrum`'s functor asks its source for `domain` and the owned free-algebra parent does not carry it, so the spectrum functor cannot be applied to a ring.

Failing tests (1, 1 file: `test_affine_plane_over_qq.sage`):

- `tests/objects/test_affine_plane_over_qq.sage::test_the_spectrum_functor_agrees`
  `AttributeError: 'Owned_NativeFreeAlgebraParent_with_category' object has no attribute 'domain'`

- Defective call: `sage/cpython/getattr.pyx:362`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C08 — The augmented simplex category's parent class does not carry `codomain`

A functor out of the augmented simplex category raises `AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'`.

Failing tests (1, 1 file: `test_free_module_of_rank_three.sage`):

- `tests/objects/test_free_module_of_rank_three.sage::test_the_module_category_applied_to_a_basis_set_agrees`
  `AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'`

- Defective call: `sage/cpython/getattr.pyx:362`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C09 — Module elements do not carry `is_isometric`

`L.is_isometric(M)` on the elements of an indefinite lattice's module raises `AttributeError` (the library writes `is_isometric` with no `_to`).

Failing tests (1, 1 file: `test_hyperbolic_plane.sage`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_invariants_of_u`
  `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'is_isometric'. Did you mean: 'is_symmetric'?`

- Defective call: `sage/cpython/getattr.pyx:362`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C10 — An isomorphism category does not carry `order`

`Isomorphisms(X, Y).order()` raises `AttributeError`, so the cardinality of the isomorphism set cannot be read as a group order.

Failing tests (1, 1 file: `test_isomorphisms_of_a_two_element_set.sage`):

- `tests/objects/test_isomorphisms_of_a_two_element_set.sage::test_the_isomorphisms_are_the_automorphism_group`
  `AttributeError: 'FixedIsoCategory_with_category' object has no attribute 'order'`

- Defective call: `sage/cpython/getattr.pyx:362`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C11 — `NumberFields()` does not carry `ring_of_integers`

`NumberFields().ring_of_integers()(QQ)` raises `AttributeError`; the functor that sends a number field to its ring of integers is not published on the category.

Failing tests (1, 1 file: `test_integers.sage`):

- `tests/objects/test_integers.sage::test_the_integers_are_the_ring_of_integers_of_the_rationals`
  `AttributeError: 'NumberFields_with_category' object has no attribute 'ring_of_integers'`

- Defective call: `tests/objects/test_integers.sage:13`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C12 — `cardinality` refuses for the embedding set `Emb(L, L')`

`Emb(L, L').cardinality()` raises `AssertionError: cannot compute the cardinality of Emb(...)` where the number is finite and computable (the isometric embeddings of one positive-definite rank-one lattice into a root lattice), so `roots()` and the orthogonal-group count cannot be read.

Failing tests (1, 1 file: `test_hyperbolic_plane.sage`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_vectors_of_square_minus_two`
  `AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 2 and signature (1, 1)): its construction supplies no exact value or decided finite enum`

The same defect also fails 2 test(s) in files now belonging to #412: `tests/objects/test_root_lattice_a2.sage::test_the_roots_and_isometries_of_a2`, `tests/objects/test_root_lattice_e8.sage::test_the_invariants_of_e8`.

- Defective call: `src/sage_extensions/categories/sets/set_categories.py:2503`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C13 — `cardinality` refuses for a group whose finiteness is a `Predicate`

`Group.cardinality()` raises `AssertionError: cannot compute the cardinality of the group ... : its finiteness is is_finite(...)` for a finitely presented group of known finite order (Q_8, S_3, Aut of a ring), so the order of a finitely presented group cannot be read.

Failing tests (1, 1 file: `test_integers.sage`):

- `tests/objects/test_integers.sage::test_the_automorphisms_of_the_integers`
  `AssertionError: cannot compute the cardinality of the group Aut_Category of modules over Integer Ring(Integer Ring): its finiteness is is_finite(Aut_Category of modules over Integer Ring(Integer Ring)), it has no cho`

The same defect also fails 2 test(s) in files now belonging to #412: `tests/objects/test_quaternion_group.sage::test_the_presentation_of_q8`, `tests/objects/test_symmetric_group_s3.sage::test_the_coxeter_presentation`.

- Defective call: `src/sage_extensions/categories/group/groups.py:459`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C14 — A `Predicate` is evaluated as a Python truth value

`is_finite(...)`, `is_subset(...)` and friends answer a `Predicate`, and `bool()` on it raises `TypeError: the proposition ... has no Python truth value`. Every user who writes `if X.is_finite():` fails, and the suite's assertions on those propositions fail.

Failing tests (2, 2 files: `test_free_group_of_rank_two.sage`, `test_free_module_of_rank_three.sage`):

- `tests/objects/test_free_group_of_rank_two.sage::test_the_automorphism_group_of_f2`
  `TypeError: the proposition is_finite(Set of Morphisms from Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] to Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] in Core of Category of groups) has no`
- `tests/objects/test_free_module_of_rank_three.sage::test_the_automorphisms_of_zz3_are_infinite`
  `TypeError: the proposition is_finite(Aut_Category of modules over Integer Ring(Free module on {[0], [1], [2]} over Integer Ring)) has no Python truth value, because it may be undecided; call ask(...) on it to ge`

The same defect also fails 4 test(s) in files now belonging to #412: `tests/objects/test_standard_triangle.sage::test_the_order_of_the_vertices_does_not_matter`, `tests/objects/test_two_hyperbolic_planes.sage::test_the_orthogonal_group_is_infinite`, `tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_plane_and_its_stabilizer`, `tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_flag_and_its_stabilizer`.

- Defective call: `src/sage_extensions/logic.py:44`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C15 — `module_rank` refuses for a module over a non-field base

`M.module_rank()` raises `AssertionError: the rank of ... is computed over a finite field for a finite module, or from a chosen basis`, for `QQ` over `ZZ`, for a fractional ideal, and for an exterior algebra's graded piece.

Failing tests (2, 2 files: `test_exterior_algebra_of_qq2.sage`, `test_fractional_ideal_2z.sage`):

- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_graded_pieces_of_the_exterior_algebra`
  `AssertionError: the rank of Lambda(Free module on {[a], [b]} over Fraction Field of Integer Ring) over Fraction Field of Integer Ring is computed over a finite field for a finite module, or from a chosen basis or pre`
- `tests/objects/test_fractional_ideal_2z.sage::test_2z_is_principal_and_free_of_rank_one`
  `AssertionError: the rank of Fractional ideal (2) of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or presentation, and Fractional ideal (2) of Integer Ring`

The same defect also fails 1 test(s) in files now belonging to #412: `tests/objects/test_tensor_algebra_of_qq2.sage::test_the_centre_of_the_tensor_algebra`.

- Defective call: `src/sage_extensions/categories/modules/pure/modules.py:2466`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C16 — A cone or cocone morphism is constructed with one cone

The cone (and dually cocone) morphism constructor demands two cones for a morphism out of the identity cone, so `Cone(X).identity()` and the endomorphism category of a cone raise `TypeError`.

Failing tests (4, 2 files: `test_cocone_under_a_one_object_diagram.sage`, `test_cone_over_a_one_object_diagram.sage`):

- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_identity_cocone_is_initial_among_cocones_on_itself`
  `TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets and Cocone with ap`
- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_has_one_endomorphism_category`
  `TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets and Cocone with ap`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_identity_cone_is_terminal_among_cones_on_itself`
  `TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets and Cone with apex {0,...,`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_has_one_endomorphism_category`
  `TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets and Cone with apex {0,...,`

- Defective call: `src/sage_extensions/categories/abstract_categories/products.py:1541`, `src/sage_extensions/categories/abstract_categories/products.py:1622`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C17 — `GL` of a torsion module is refused

`GL(M)` raises `AssertionError: GL(...) is realized as a matrix group only for a free module with a finite selected basis`, so the automorphisms of `Z/6` or `F_3` have no group.

Failing tests (1, 1 file: `test_cyclic_module_zz6.sage`):

- `tests/objects/test_cyclic_module_zz6.sage::test_the_endomorphisms_and_automorphisms_of_zz6`
  `AssertionError: GL(Finitely presented module on 1 module generators over Integer Ring with invariant factors Invariant-factor family: [0 ↦ 6]) is realized as a matrix group only for a free module with a finite select`

The same defect also fails 1 test(s) in files now belonging to #412: `tests/objects/test_prime_field_f3.sage::test_the_automorphisms_of_f3`.

- Defective call: `src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:4032`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C18 — The metric dual is refused for a degenerate lattice

`L.dual_lattice()` raises on the degenerate plane although the test asks for the radical; the refusal message states the form is degenerate, which is the hypothesis the caller is testing.

Failing tests (1, 1 file: `test_degenerate_plane.sage`):

- `tests/objects/test_degenerate_plane.sage::test_the_radical_is_the_line_through_e0_minus_e1`
  `AssertionError: Integral lattice of rank 2 and signature (1, 0) has no metric dual: the dual lattice is defined for a nondegenerate form, and Integral lattice of rank 2 and signature (1, 0) is not known to be nondege`

- Defective call: `src/sage_extensions/categories/lattices.py:6838`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C19 — The whole-algebra map of an infinite-rank free algebra is refused

`ValueError: the whole-algebra map for Free module on Coproduct ... over Fraction Field ...`, raised when the endomorphism category of a coordinate-ring algebra is formed.

Failing tests (1, 1 file: `test_a_coordinate_line_in_the_affine_plane.sage`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_has_one_endomorphism_category`
  `ValueError: the whole-algebra map for Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring/(x) -> Free module on Coproduct of the family over NN = {0, 1, 2, ...} ove`

- Defective call: `src/sage_extensions/categories/algebras/algebras.py:4631`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C20 — `WeilDivisorGroups._call_` is called without its defining data

`WeilDivisorGroups._call_() missing 1 required positional argument: 'prime_divisors'`, so the divisor group of three points cannot be constructed.

Failing tests (1, 1 file: `test_divisors_on_three_points.sage`):

- `tests/objects/test_divisors_on_three_points.sage::test_the_weil_divisor_group_on_three_points`
  `TypeError: WeilDivisorGroups._call_() missing 1 required positional argument: 'prime_divisors'`

- Defective call: `/sage/.venv/lib/python3.14/site-packages/sage/categories/category.py:592`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C21 — A cardinal sum over `ZZ` is not decided

`AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite`, raised while the centre of an exterior algebra is formed.

Failing tests (1, 1 file: `test_exterior_algebra_of_qq2.sage`):

- `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_centre_of_the_exterior_algebra`
  `AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite: it is not a finite sum, product, or supremum of known cardinals`

- Defective call: `src/sage_extensions/categories/sets/cardinals.py:732`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C22 — Isomorphism of two free groups is undecided

`AssertionError: whether <F_2> is isomorphic to <F_2>` is undecided, so the free-group functor's agreement cannot be asserted.

Failing tests (1, 1 file: `test_free_group_of_rank_two.sage`):

- `tests/objects/test_free_group_of_rank_two.sage::test_the_free_group_functor_agrees`
  `AssertionError: whether Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is isomorphic to Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined for every pair of groups, but the current preamble d`

- Defective call: `src/sage_extensions/categories/group/groups.py:6778`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C23 — The abelianization of a finitely presented group is refused

`AssertionError: the abelianization of the finitely presented group ... is defined, but the carrier ...`, so `F_2^ab` cannot be formed.

Failing tests (1, 1 file: `test_free_group_of_rank_two.sage`):

- `tests/objects/test_free_group_of_rank_two.sage::test_the_abelianization_of_f2`
  `AssertionError: the abelianization of the finitely presented group Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined, but the current preamble has no presentation-quotient route for G/[G,G]; add it a`

- Defective call: `src/sage_extensions/categories/functors/abelianization.py:52`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C24 — A GAP element index is out of range

`IndexError: index out of range` from GAP while the isotropic lines of `U` are enumerated.

Failing tests (1, 1 file: `test_hyperbolic_plane.sage`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_isotropic_lines_of_u`
  `IndexError: index out of range.`

- Defective call: `sage/libs/gap/element.pyx:3170`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C25 — `O(L)` of an indefinite lattice is refused

`AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice`, so `O(U)` has no arithmetic.

Failing tests (1, 1 file: `test_hyperbolic_plane.sage`):

- `tests/objects/test_hyperbolic_plane.sage::test_the_orthogonal_group_of_u`
  `AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice of finite rank over ZZ, and Integral lattice of rank 2 and sign`

- Defective call: `src/sage_extensions/categories/lattice_morphisms.py:4531`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C26 — A base ring is refused as a field

`ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring`, raised on the base change of a free module to `QQ`.

Failing tests (1, 1 file: `test_free_module_of_rank_three.sage`):

- `tests/objects/test_free_module_of_rank_three.sage::test_the_base_change_to_the_rationals`
  `ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring`

- Defective call: `/sage/.venv/lib/python3.14/site-packages/sage/categories/vector_spaces.py:70`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C27 — `/` is applied to owned module elements

The tests write `M / N` and `ZZ / I`, which the owned modules do not support; the library spells these `quotient_module` and `quotient_ring`, and `Modules.__truediv__` is absent. (Whether the operator should exist is a design question, not a test bug: `AGENTS.md` bans `__truediv__` on modules, so the suite and the policy disagree.)

Failing tests (3, 2 files: `test_cyclic_module_zz6.sage`, `test_free_module_of_rank_three.sage`):

- `tests/objects/test_cyclic_module_zz6.sage::test_the_cokernel_and_the_quotient_agree`
  `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`
- `tests/objects/test_cyclic_module_zz6.sage::test_the_quotient_of_the_regular_module_by_the_ideal`
  `TypeError: unsupported operand type(s) for /: '_OwnedRingParent_with_category' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`
- `tests/objects/test_free_module_of_rank_three.sage::test_a_quotient_of_zz3`
  `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'`

- Defective call: `tests/objects/test_cyclic_module_zz6.sage:16`, `tests/objects/test_cyclic_module_zz6.sage:20`, `tests/objects/test_free_module_of_rank_three.sage:70`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C28 — Two constructions of one lattice do not compare equal

`Lattices(ZZ)("A1") + Lattices(ZZ)("A2")` and the block-Gram construction of the same lattice do not compare equal, and neither do the catalogue and Gram constructions of `A_2`, `E_8` and `U + U`.

Failing tests (2, 2 files: `test_a1_plus_a2.sage`, `test_degenerate_plane.sage`):

- `tests/objects/test_a1_plus_a2.sage::test_the_sum_and_the_block_gram_agree`
  `assert: Integral latt...gnature (0, 3) == Integral latt...gnature (0, 3)`
- `tests/objects/test_degenerate_plane.sage::test_the_lattice_and_the_form_module_constructions_agree`
  `assert: Integral latt...gnature (1, 0) == Free module o...r Integer Ring`

The same defect also fails 3 test(s) in files now belonging to #412: `tests/objects/test_root_lattice_a2.sage::test_the_named_and_the_gram_constructions_agree`, `tests/objects/test_root_lattice_e8.sage::test_the_catalogue_entry_agrees`, `tests/objects/test_two_hyperbolic_planes.sage::test_the_sum_and_the_block_gram_agree`.

- Defective call: `tests/objects/test_a1_plus_a2.sage:9`, `tests/objects/test_degenerate_plane.sage:12`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C29 — A direct sum is not an object of `DirectSumObjects(Lattices(ZZ))`

`L in DirectSumObjects(Lattices(ZZ))` answers false for a lattice built as a sum, so a user cannot test the decomposition it was constructed with.

Failing tests (1, 1 file: `test_a1_plus_a2.sage`):

- `tests/objects/test_a1_plus_a2.sage::test_the_categories_of_a1_plus_a2`
  `assert: Integral lattice of rank 3 and signature (0, 3) in Category of objects of lattices with a chosen direct-sum decomposition`

The same defect also fails 1 test(s) in files now belonging to #412: `tests/objects/test_two_hyperbolic_planes.sage::test_the_categories_of_u_plus_u`.

- Defective call: `tests/objects/test_a1_plus_a2.sage:16`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

### C30 — A cone or cocone is not an object of its cone category

`cone in Cones(F)` and `cocone in Cocones(F)` answer false for the cone built by the category's own constructor.

Failing tests (2, 2 files: `test_cocone_under_a_one_object_diagram.sage`, `test_cone_over_a_one_object_diagram.sage`):

- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_is_an_object_of_the_cocone_category`
  `assert: Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cocone category`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_is_an_object_of_the_cone_category`
  `assert: Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cone category`

- Defective call: `tests/objects/test_cocone_under_a_one_object_diagram.sage:19`, `tests/objects/test_cone_over_a_one_object_diagram.sage:19`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C31 — Two constructions of one functor do not compare equal

`cone.apex_and_leg(...)` and the functor rebuilt from its data do not compare equal.

Failing tests (2, 2 files: `test_cocone_under_a_one_object_diagram.sage`, `test_cone_over_a_one_object_diagram.sage`):

- `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_apex_and_the_leg`
  `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets`
- `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_apex_and_the_leg`
  `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets`

- Defective call: `tests/objects/test_cocone_under_a_one_object_diagram.sage:26`, `tests/objects/test_cone_over_a_one_object_diagram.sage:26`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C32 — The assertion at `test_a_coordinate_line_in_the_affine_plane.sage:23` does not hold: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction 

The proposition asserted at `/repos/sage-extensions/tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23` is false on main: `Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction `. The test states the contract; the construction it names does not meet it.

Failing tests (1, 1 file: `test_a_coordinate_line_in_the_affine_plane.sage`):

- `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_categories_of_the_axis`
  `assert: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring defined by x in Category of smooth schemes over Fraction Field of In`

- Defective call: `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C33 — The assertion at `test_affine_plane_over_qq.sage:15` does not hold: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring

The proposition asserted at `/repos/sage-extensions/tests/objects/test_affine_plane_over_qq.sage:15` is false on main: `Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring`. The test states the contract; the construction it names does not meet it.

Failing tests (1, 1 file: `test_affine_plane_over_qq.sage`):

- `tests/objects/test_affine_plane_over_qq.sage::test_the_affine_plane_is_the_spectrum_of_its_coordinate_ring`
  `assert: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring`

- Defective call: `tests/objects/test_affine_plane_over_qq.sage:15`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C34 — `module_morphisms.py:1978` raises ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:

The call at `/repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978` raises `ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:`. A user reaching that operation through the public API gets the exception instead of the documented object.

Failing tests (1, 1 file: `test_discriminant_quadratic_form_of_a1.sage`):

- `tests/objects/test_discriminant_quadratic_form_of_a1.sage::test_the_brown_invariant_of_q_a1`
  `ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:`

- Defective call: `src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978`.
- Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.
- Repair: open; filed as this cause.

### C35 — The assertion at `test_integers.sage:28` does not hold: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring

The proposition asserted at `/repos/sage-extensions/tests/objects/test_integers.sage:28` is false on main: `Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring`. The test states the contract; the construction it names does not meet it.

Failing tests (1, 1 file: `test_integers.sage`):

- `tests/objects/test_integers.sage::test_the_integers_as_an_algebra_over_themselves`
  `assert: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring`

- Defective call: `tests/objects/test_integers.sage:28`.
- Introduced by: main's root commit `c731175` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.
- Repair: open; filed as this cause.

## Repairs landed in this workstream

- `6df56ad` fix: The algebraic closure of GF(p) is raised through the field's closure (#408)
- `57208eb` fix: The session namespace publishes the constructors the suite names (#408)
- `9b29712` Merge remote-tracking branch 'origin/main' into perf/correctness-sample
- `0ee5ad5` perf: definite Aut and isometry on the indecomposable decomposition
- `484e4c5` perf: one engine sift per coset of the kernel image; the 4.3.8 chamber from a vertex (#402)
- `bbb6608` perf: finite G-set stabilizers by GAP; integer point lookup by engine key

Both are commits on main whose subject names #408; the two causes above are the only
ones repaired here. Red tests: the failing tests listed under C01 and C03, which fail on
main and pass after the corresponding commit. Per file, before -> after:

| file | in this slice | failing on main | after |
| --- | --- | --- | --- |
| `test_absolute_galois_group_of_f5.sage` | yes | 6 | 1 |
| `test_cyclic_module_zz6.sage` | yes | 4 | 3 |
| `test_free_group_of_rank_two.sage` | yes | 7 | 3 |
| `test_fractional_ideal_2z.sage` | yes | 3 | 2 |
| `test_free_module_of_rank_three.sage` | yes | 6 | 4 |
| `test_exterior_algebra_of_qq2.sage` | yes | 3 | 3 |
| `test_trivial_connection_on_the_affine_line.sage` | no, #412 | 3 | 0 |
| `test_tensor_product_of_zz2_and_zz3.sage` | no, #412 | 1 | 0 |
| `test_root_lattice_a2.sage` | no, #412 | 6 | 5 |
| `test_symmetric_algebra_of_qq2.sage` | no, #412 | 1 | 1 |
| `test_tensor_algebra_of_qq2.sage` | no, #412 | 2 | 2 |
| `test_symmetric_group_s3.sage` | no, #412 | 6 | 6 |
| `test_square_integrable_functions.sage` | no, #412 | 4 | 4 |

Fifteen tests of the directory turn green, ten of them in this slice's files. The rows
that do not move fail for other causes. `python -m sage_extensions.testing.test_lint
tests/objects` reports 18 -> 0 TL13 findings; the 16 TL01/TL02/TL04/TL11 findings in the
same files are untouched.

## What is not done

1. **The causes are not filed as issues.** This session's GitHub connection reads issues
   and pushes commits; it has no operation that creates an issue, and `gh` on the VM is
   unauthenticated. `results/issue408-causes.sh` holds one reviewed `gh issue create` per
   cause, with the failing tests, the error, the introducing commit and the scope in the
   body, so filing is one run of that script.
2. **The other causes are not repaired.** They are filed with their evidence. The two
   repaired ones are the two whose defect was one wrong call at one owner.
3. **The session-namespace cause reaches beyond this slice.** Tree-wide
   `python -m sage_extensions.testing.test_lint` still reports 21 distinct names as TL13
   outside `tests/objects`: `GeneralLinearGroups`, `FreeGroupQuotients`,
   `ModulesOverCommutativeRings`, `AdditiveMonoids`, `Subgroups`, `BilinearMap`,
   `ModulesOverIntegralDomains`, `Grp`, `DifferentialGradedAlgebras`,
   `CommutativeGradedIntegralDomains`, `NondegenerateGenericFibreFormModules`,
   `ModuleSubobjects`, `GroupsWithChosenFinitePresentation`,
   `FinitelyGeneratedFreeModules`, `Torsors`, `SymmetricGroups`, `PairedModules`,
   `OrdinaryCharacterRepresentations`, `ModuleBaseRingProjection`,
   `GeneratedSubgroups`, `FramedFreeModules`. The same repair publishes them; this
   slice's run does not exercise them, so they are not claimed.
4. **`just test` never ran as one suite.** The image cannot run it as written (above),
   and per-file runs are what this triage measures.
5. **The whole-directory run is not re-run after the repairs.** The per-file table above
   is the measurement.

## Appendix: every failing test of the slice

| test | site | error |
| --- | --- | --- |
| `tests/objects/test_a1_plus_a2.sage::test_the_categories_of_a1_plus_a2` | `tests/objects/test_a1_plus_a2.sage:16` | `assert: Integral lattice of rank 3 and signature (0, 3) in Category of objects of lattices with a chosen direct-sum decomposition` |
| `tests/objects/test_a1_plus_a2.sage::test_the_sum_and_the_block_gram_agree` | `tests/objects/test_a1_plus_a2.sage:9` | `assert: Integral latt...gnature (0, 3) == Integral latt...gnature (0, 3)` |
| `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_has_one_endomorphism_category` | `src/sage_extensions/categories/algebras/algebras.py:4631` | `ValueError: the whole-algebra map for Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring/(x) -> Free module on Co` |
| `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_a_closed_subscheme_of_codimension_one` | `sage/cpython/getattr.pyx:357` | `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'ambient_scheme'` |
| `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_an_affine_line` | `sage/cpython/getattr.pyx:357` | `AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?` |
| `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_categories_of_the_axis` | `tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23` | `assert: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring defined by x in Ca` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_frobenius` | `tests/objects/test_absolute_galois_group_of_f5.sage:5` | `NameError: name 'AbsoluteGaloisGroup' is not defined` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_has_one_endomorphism_category` | `tests/objects/test_absolute_galois_group_of_f5.sage:5` | `NameError: name 'AbsoluteGaloisGroup' is not defined` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_of_a_finite_field_is_zhat` | `tests/objects/test_absolute_galois_group_of_f5.sage:5` | `NameError: name 'AbsoluteGaloisGroup' is not defined` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_categories_of_the_absolute_galois_group` | `tests/objects/test_absolute_galois_group_of_f5.sage:5` | `NameError: name 'AbsoluteGaloisGroup' is not defined` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_field_construction_agrees` | `src/sage_extensions/categories/rings/ring_foundation.py:7608` | `TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'` |
| `tests/objects/test_absolute_galois_group_of_f5.sage::test_the_finite_quotients` | `tests/objects/test_absolute_galois_group_of_f5.sage:5` | `NameError: name 'AbsoluteGaloisGroup' is not defined` |
| `tests/objects/test_affine_plane_over_qq.sage::test_the_affine_plane_is_the_spectrum_of_its_coordinate_ring` | `tests/objects/test_affine_plane_over_qq.sage:15` | `assert: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring` |
| `tests/objects/test_affine_plane_over_qq.sage::test_the_spectrum_functor_agrees` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'Owned_NativeFreeAlgebraParent_with_category' object has no attribute 'domain'` |
| `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_apex_and_the_leg` | `tests/objects/test_cocone_under_a_one_object_diagram.sage:26` | `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets` |
| `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_has_one_endomorphism_category` | `src/sage_extensions/categories/abstract_categories/products.py:1622` | `TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category o` |
| `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_is_an_object_of_the_cocone_category` | `tests/objects/test_cocone_under_a_one_object_diagram.sage:19` | `assert: Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cocone category` |
| `tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_identity_cocone_is_initial_among_cocones_on_itself` | `src/sage_extensions/categories/abstract_categories/products.py:1622` | `TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category o` |
| `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_apex_and_the_leg` | `tests/objects/test_cone_over_a_one_object_diagram.sage:26` | `assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets` |
| `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_has_one_endomorphism_category` | `src/sage_extensions/categories/abstract_categories/products.py:1541` | `TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...` |
| `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_is_an_object_of_the_cone_category` | `tests/objects/test_cone_over_a_one_object_diagram.sage:19` | `assert: Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cone category` |
| `tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_identity_cone_is_terminal_among_cones_on_itself` | `src/sage_extensions/categories/abstract_categories/products.py:1541` | `TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...` |
| `tests/objects/test_cyclic_module_zz6.sage::test_the_categories_of_zz6` | `tests/objects/test_cyclic_module_zz6.sage:29` | `NameError: name 'FinitelyPresentedModules' is not defined` |
| `tests/objects/test_cyclic_module_zz6.sage::test_the_cokernel_and_the_quotient_agree` | `tests/objects/test_cyclic_module_zz6.sage:16` | `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFre` |
| `tests/objects/test_cyclic_module_zz6.sage::test_the_endomorphisms_and_automorphisms_of_zz6` | `src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:4032` | `AssertionError: GL(Finitely presented module on 1 module generators over Integer Ring with invariant factors Invariant-factor family: [0 ↦ 6]) is realized as a matrix` |
| `tests/objects/test_cyclic_module_zz6.sage::test_the_quotient_of_the_regular_module_by_the_ideal` | `tests/objects/test_cyclic_module_zz6.sage:20` | `TypeError: unsupported operand type(s) for /: '_OwnedRingParent_with_category' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'` |
| `tests/objects/test_degenerate_plane.sage::test_the_lattice_and_the_form_module_constructions_agree` | `tests/objects/test_degenerate_plane.sage:12` | `assert: Integral latt...gnature (1, 0) == Free module o...r Integer Ring` |
| `tests/objects/test_degenerate_plane.sage::test_the_radical_is_the_line_through_e0_minus_e1` | `src/sage_extensions/categories/lattices.py:6838` | `AssertionError: Integral lattice of rank 2 and signature (1, 0) has no metric dual: the dual lattice is defined for a nondegenerate form, and Integral lattice of rank` |
| `tests/objects/test_discriminant_quadratic_form_of_a1.sage::test_the_brown_invariant_of_q_a1` | `src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978` | `ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:` |
| `tests/objects/test_divisors_on_three_points.sage::test_the_cartier_divisor_group_on_three_points` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'scheme'` |
| `tests/objects/test_divisors_on_three_points.sage::test_the_weil_divisor_group_on_three_points` | `/sage/.venv/lib/python3.14/site-packages/sage/categories/category.py:592` | `TypeError: WeilDivisorGroups._call_() missing 1 required positional argument: 'prime_divisors'` |
| `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_categories_of_the_exterior_algebra` | `tests/objects/test_exterior_algebra_of_qq2.sage:20` | `NameError: name 'AlternatingAlgebras' is not defined` |
| `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_centre_of_the_exterior_algebra` | `src/sage_extensions/categories/sets/cardinals.py:732` | `AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite: it is not a finite sum, product, or supremum of known cardinals` |
| `tests/objects/test_exterior_algebra_of_qq2.sage::test_the_graded_pieces_of_the_exterior_algebra` | `src/sage_extensions/categories/modules/pure/modules.py:2466` | `AssertionError: the rank of Lambda(Free module on {[a], [b]} over Fraction Field of Integer Ring) over Fraction Field of Integer Ring is computed over a finite field ` |
| `tests/objects/test_fourier_characters.sage::test_the_categories_of_the_characters` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_fourier_characters.sage::test_the_characters_are_countably_many_and_distinct` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_fourier_characters.sage::test_the_characters_are_indexed_by_the_integers` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_fractional_ideal_2z.sage::test_2z_is_principal_and_free_of_rank_one` | `src/sage_extensions/categories/modules/pure/modules.py:2466` | `AssertionError: the rank of Fractional ideal (2) of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or pres` |
| `tests/objects/test_fractional_ideal_2z.sage::test_the_categories_of_2z` | `tests/objects/test_fractional_ideal_2z.sage:13` | `NameError: name 'FractionalIdeals' is not defined` |
| `tests/objects/test_fractional_ideal_2z.sage::test_the_category_construction_agrees` | `tests/objects/test_fractional_ideal_2z.sage:9` | `NameError: name 'FractionalIdeals' is not defined` |
| `tests/objects/test_free_group_of_rank_two.sage::test_the_abelianization_of_f2` | `src/sage_extensions/categories/functors/abelianization.py:52` | `AssertionError: the abelianization of the finitely presented group Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined, but the current preamble has no` |
| `tests/objects/test_free_group_of_rank_two.sage::test_the_automorphism_group_of_f2` | `src/sage_extensions/logic.py:44` | `TypeError: the proposition is_finite(Set of Morphisms from Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] to Group generated by Group generators: [0 ↦ g` |
| `tests/objects/test_free_group_of_rank_two.sage::test_the_categories_of_f2` | `tests/objects/test_free_group_of_rank_two.sage:15` | `NameError: name 'FinitelyGeneratedGroups' is not defined` |
| `tests/objects/test_free_group_of_rank_two.sage::test_the_free_group_functor_agrees` | `src/sage_extensions/categories/group/groups.py:6778` | `AssertionError: whether Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is isomorphic to Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined fo` |
| `tests/objects/test_free_module_of_rank_three.sage::test_a_quotient_of_zz3` | `tests/objects/test_free_module_of_rank_three.sage:70` | `TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFre` |
| `tests/objects/test_free_module_of_rank_three.sage::test_the_automorphisms_of_zz3_are_infinite` | `src/sage_extensions/logic.py:44` | `TypeError: the proposition is_finite(Aut_Category of modules over Integer Ring(Free module on {[0], [1], [2]} over Integer Ring)) has no Python truth value, beca` |
| `tests/objects/test_free_module_of_rank_three.sage::test_the_base_change_to_the_rationals` | `/sage/.venv/lib/python3.14/site-packages/sage/categories/vector_spaces.py:70` | `ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring` |
| `tests/objects/test_free_module_of_rank_three.sage::test_the_categories_of_zz3` | `tests/objects/test_free_module_of_rank_three.sage:37` | `NameError: name 'FinitelyGeneratedModules' is not defined` |
| `tests/objects/test_free_module_of_rank_three.sage::test_the_module_category_applied_to_a_basis_set_agrees` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'` |
| `tests/objects/test_hermite_polynomials.sage::test_the_categories_of_the_hermite_polynomials` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_hermite_polynomials.sage::test_the_hermite_polynomials` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_hermite_polynomials.sage::test_the_polynomials_are_indexed_by_the_naturals` | `src/sage_extensions/categories/rings/ring_foundation.py:7534` | `TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected` |
| `tests/objects/test_hyperbolic_plane.sage::test_the_invariants_of_u` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'is_isometric'. Did you mean: 'is_symmetric'?` |
| `tests/objects/test_hyperbolic_plane.sage::test_the_isotropic_lines_of_u` | `sage/libs/gap/element.pyx:3170` | `IndexError: index out of range.` |
| `tests/objects/test_hyperbolic_plane.sage::test_the_orthogonal_group_of_u` | `src/sage_extensions/categories/lattice_morphisms.py:4531` | `AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice of finite ran` |
| `tests/objects/test_hyperbolic_plane.sage::test_the_vectors_of_square_minus_two` | `src/sage_extensions/categories/sets/set_categories.py:2503` | `AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 2 and signature (1, 1)): its construct` |
| `tests/objects/test_integers.sage::test_the_automorphisms_of_the_integers` | `src/sage_extensions/categories/group/groups.py:459` | `AssertionError: cannot compute the cardinality of the group Aut_Category of modules over Integer Ring(Integer Ring): its finiteness is is_finite(Aut_Category of modul` |
| `tests/objects/test_integers.sage::test_the_integers_are_the_initial_ring` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'OwnedRings_with_category' object has no attribute '_structured_category'` |
| `tests/objects/test_integers.sage::test_the_integers_are_the_ring_of_integers_of_the_rationals` | `tests/objects/test_integers.sage:13` | `AttributeError: 'NumberFields_with_category' object has no attribute 'ring_of_integers'` |
| `tests/objects/test_integers.sage::test_the_integers_as_an_algebra_over_themselves` | `tests/objects/test_integers.sage:28` | `assert: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring` |
| `tests/objects/test_isomorphisms_of_a_two_element_set.sage::test_the_isomorphisms_are_the_automorphism_group` | `sage/cpython/getattr.pyx:362` | `AttributeError: 'FixedIsoCategory_with_category' object has no attribute 'order'` |

