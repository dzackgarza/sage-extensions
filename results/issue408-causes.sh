#!/bin/bash
# File the causes of #408 as sage-extensions issues.
#
# Slice: the 26 files of tests/objects up to test_isomorphisms_of_a_two_element_set.sage;
# the files after it are #412. #403 is already filed and is not among these causes.
#
# The connected GitHub app reads issues and pushes commits but cannot create an issue, and
# gh on this VM is unauthenticated, so the bodies are staged here. Review, then run from
# the repository root: bash results/issue408-causes.sh
set -euo pipefail
repo=dzackgarza/sage-extensions

gh issue create --repo "$repo" \
  --title "C01: The session namespace does not publish the constructors the suite names" \
  --body "\`from sage_extensions.all import *\` binds a namespace that omits nineteen owned constructors the suite names: \`AbsoluteGaloisGroup\`, \`AbsoluteGaloisGroups\`, \`AbsoluteGaloisGroupsOfFiniteFields\`, \`FinitelyGeneratedGroups\`, \`FinitelyPresentedGroups\`, \`ProfiniteGroups\`, \`AlternatingAlgebras\`, \`SymmetricAlgebras\`, \`TensorAlgebras\`, \`StrictlyGradedCommutativeAlgebras\`, \`FractionalIdeals\`, \`ModulesWithConnection\`, \`ModulesWithFlatConnection\`, \`FinitelyGeneratedModules\`, \`FinitelyPresentedModules\`, \`ProjectiveModules\`, \`TorsionModules\`, \`TensorProductModules\`, \`SymmetricBilinearFormModules\`. A user who writes the session-standard import gets \`NameError\` for a constructor the library owns, and the repository's own test lint reports the same names as TL13.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_the_categories_of_the_absolute_galois_group\`
  \`NameError: name 'AbsoluteGaloisGroup' is not defined\`
- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_of_a_finite_field_is_zhat\`
  \`NameError: name 'AbsoluteGaloisGroup' is not defined\`
- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_frobenius\`
  \`NameError: name 'AbsoluteGaloisGroup' is not defined\`
- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_the_finite_quotients\`
  \`NameError: name 'AbsoluteGaloisGroup' is not defined\`
- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_the_absolute_galois_group_has_one_endomorphism_category\`
  \`NameError: name 'AbsoluteGaloisGroup' is not defined\`
- \`tests/objects/test_cyclic_module_zz6.sage::test_the_categories_of_zz6\`
  \`NameError: name 'FinitelyPresentedModules' is not defined\`
- \`tests/objects/test_exterior_algebra_of_qq2.sage::test_the_categories_of_the_exterior_algebra\`
  \`NameError: name 'AlternatingAlgebras' is not defined\`
- \`tests/objects/test_fractional_ideal_2z.sage::test_the_category_construction_agrees\`
  \`NameError: name 'FractionalIdeals' is not defined\`
- \`tests/objects/test_fractional_ideal_2z.sage::test_the_categories_of_2z\`
  \`NameError: name 'FractionalIdeals' is not defined\`
- \`tests/objects/test_free_group_of_rank_two.sage::test_the_categories_of_f2\`
  \`NameError: name 'FinitelyGeneratedGroups' is not defined\`
- \`tests/objects/test_free_module_of_rank_three.sage::test_the_categories_of_zz3\`
  \`NameError: name 'FinitelyGeneratedModules' is not defined\`

The same defect also fails \`tests/objects/test_root_lattice_a2.sage::test_the_categories_of_a2\`, \`tests/objects/test_symmetric_algebra_of_qq2.sage::test_the_categories_of_the_symmetric_algebra\`, \`tests/objects/test_tensor_algebra_of_qq2.sage::test_the_categories_of_the_tensor_algebra\`, \`tests/objects/test_tensor_product_of_zz2_and_zz3.sage::test_the_categories_of_the_tensor_product\`, \`tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_categories_of_the_module_with_connection\`, \`tests/objects/test_trivial_connection_on_the_affine_line.sage::test_every_connection_on_a_line_over_a_curve_is_flat\`, \`tests/objects/test_trivial_connection_on_the_affine_line.sage::test_the_module_with_connection_has_one_endomorphism_category\`, which are files of #412.

Defective call: /repos/sage-extensions/tests/objects/test_absolute_galois_group_of_f5.sage:5, /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:29, /repos/sage-extensions/tests/objects/test_exterior_algebra_of_qq2.sage:20, /repos/sage-extensions/tests/objects/test_fractional_ideal_2z.sage:13, /repos/sage-extensions/tests/objects/test_fractional_ideal_2z.sage:9, /repos/sage-extensions/tests/objects/test_free_group_of_rank_two.sage:15, /repos/sage-extensions/tests/objects/test_free_module_of_rank_three.sage:37.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 6 files of the #408 slice.
Triage record: results/issue408-triage.md (C01)."

gh issue create --repo "$repo" \
  --title "C02: The owned ring adapter has no constructor for the symbolic ring" \
  --body "Any construction whose coefficient ring is \`SR\` -- \`PolynomialRing(SR)\`, \`LaurentPolynomialRing(SR)\`, the character and translate families built over it -- raises \`TypeError: cannot raise Symbolic Ring through an owned ring constructor\` from \`_owned_engine_ring\`. A user cannot build the symbolic-coefficient rings the session namespace publishes names for.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_fourier_characters.sage::test_the_characters_are_indexed_by_the_integers\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`
- \`tests/objects/test_fourier_characters.sage::test_the_categories_of_the_characters\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`
- \`tests/objects/test_fourier_characters.sage::test_the_characters_are_countably_many_and_distinct\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`
- \`tests/objects/test_hermite_polynomials.sage::test_the_polynomials_are_indexed_by_the_naturals\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`
- \`tests/objects/test_hermite_polynomials.sage::test_the_categories_of_the_hermite_polynomials\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`
- \`tests/objects/test_hermite_polynomials.sage::test_the_hermite_polynomials\`
  \`TypeError: cannot raise Symbolic Ring through an owned ring constructor: no constructor for this native ring family has been selected\`

The same defect also fails \`tests/objects/test_laurent_monomials.sage::test_the_monomials_are_indexed_by_the_integers\`, \`tests/objects/test_laurent_monomials.sage::test_the_categories_of_the_laurent_monomials\`, \`tests/objects/test_laurent_monomials.sage::test_the_laurent_monomials_multiply_by_adding_exponents\`, \`tests/objects/test_sinc_translates.sage::test_the_translates_are_indexed_by_the_integers\`, \`tests/objects/test_sinc_translates.sage::test_the_categories_of_the_sinc_translates\`, \`tests/objects/test_sinc_translates.sage::test_the_translates_are_countably_many_and_distinct\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/rings/ring_foundation.py:7534.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: \`test_fourier_characters.sage\`, \`test_hermite_polynomials.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C02)."

gh issue create --repo "$repo" \
  --title "C03: The algebraic closure of a finite field is raised with the wrong constructor arity" \
  --body "\`GF(p).algebraic_closure()\` raises \`TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'\`, because the owned adapter calls Sage's \`AlgebraicClosureFiniteField(base_ring, name)\` with a characteristic. A user cannot take the algebraic closure of a finite field at all.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_absolute_galois_group_of_f5.sage::test_the_field_construction_agrees\`
  \`TypeError: AlgebraicClosureFiniteField() missing 1 required positional argument: 'name'\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/rings/ring_foundation.py:7608.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_absolute_galois_group_of_f5.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C03)."

gh issue create --repo "$repo" \
  --title "C04: The owned parent and element classes do not carry `is_isomorphic_to`" \
  --body "\`is_isomorphic_to\` -- the spelling \`ring_foundation\` already installs as an alias of \`is_isomorphic\` -- is absent from the owned parent and element classes of modules, schemes and sets, so \`A.is_isomorphic_to(B)\` raises \`AttributeError\` and Sage itself answers \`Did you mean: 'is_isomorphic'?\`. A user of the public spelling gets an attribute error on objects that do support the relation.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_an_affine_line\`
  \`AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'is_isomorphic_to'. Did you mean: 'is_isomorphic'?\`

The same defect also fails \`tests/objects/test_projective_plane_over_qq.sage::test_the_projective_plane_is_glued_from_its_charts\`, \`tests/objects/test_projective_plane_over_qq.sage::test_the_standard_affine_charts\`, \`tests/objects/test_projective_plane_over_qq.sage::test_the_picard_group_and_the_canonical_bundle\`, \`tests/objects/test_regular_module_of_c2.sage::test_the_permutation_module_is_the_regular_module\`, \`tests/objects/test_regular_module_of_c2.sage::test_the_coinduced_module_is_the_regular_module\`, \`tests/objects/test_symmetric_group_s3.sage::test_the_automorphisms_of_a_three_element_set\`, which are files of #412.

Defective call: sage/cpython/getattr.pyx:357.

Introduced by: \`git bisect\` in the image on the signature \`object has no attribute 'is_isomorphic_to'\`; the first commit where it appears is \`55927425bcff\` -- fix: let the cached quotient-by-relations constructor read its keyword defaults (Zack Garza <dzackgarza@gmail.com>), in 12 bisect steps.

Scope: 1 file: \`test_a_coordinate_line_in_the_affine_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C04)."

gh issue create --repo "$repo" \
  --title "C05: `Rings()` does not carry `initial_object`" \
  --body "\`Rings().initial_object()\` raises \`AttributeError\`; \`initial_object\` is written for \`OwnedSemirings\` (returning \`NN\`) and not for \`OwnedRings\`, so the initial ring \`ZZ\` cannot be named through the category that owns it.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_integers.sage::test_the_integers_are_the_initial_ring\`
  \`AttributeError: 'OwnedRings_with_category' object has no attribute '_structured_category'\`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_integers.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C05)."

gh issue create --repo "$repo" \
  --title "C06: The owned subscheme surface does not carry `scheme`/`ambient_scheme`" \
  --body "A subscheme's \`scheme()\` and \`ambient_scheme()\` are absent from the owned subscheme parent (and its element class), so a user cannot ask a closed subscheme or a Cartier divisor which scheme it sits in.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_is_a_closed_subscheme_of_codimension_one\`
  \`AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'ambient_scheme'\`
- \`tests/objects/test_divisors_on_three_points.sage::test_the_cartier_divisor_group_on_three_points\`
  \`AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'scheme'\`

Defective call: sage/cpython/getattr.pyx:357, sage/cpython/getattr.pyx:362.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: \`test_a_coordinate_line_in_the_affine_plane.sage\`, \`test_divisors_on_three_points.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C06)."

gh issue create --repo "$repo" \
  --title "C07: The owned free-algebra parent does not carry `domain`" \
  --body "\`Spectrum\`'s functor asks its source for \`domain\` and the owned free-algebra parent does not carry it, so the spectrum functor cannot be applied to a ring.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_affine_plane_over_qq.sage::test_the_spectrum_functor_agrees\`
  \`AttributeError: 'Owned_NativeFreeAlgebraParent_with_category' object has no attribute 'domain'\`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_affine_plane_over_qq.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C07)."

gh issue create --repo "$repo" \
  --title "C08: The augmented simplex category's parent class does not carry `codomain`" \
  --body "A functor out of the augmented simplex category raises \`AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'\`.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_free_module_of_rank_three.sage::test_the_module_category_applied_to_a_basis_set_agrees\`
  \`AttributeError: 'AugmentedSimplexCategory.parent_class' object has no attribute 'codomain'\`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_free_module_of_rank_three.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C08)."

gh issue create --repo "$repo" \
  --title "C09: Module elements do not carry `is_isometric`" \
  --body "\`L.is_isometric(M)\` on the elements of an indefinite lattice's module raises \`AttributeError\` (the library writes \`is_isometric\` with no \`_to\`).

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_hyperbolic_plane.sage::test_the_invariants_of_u\`
  \`AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' object has no attribute 'is_isometric'. Did you mean: 'is_symmetric'?\`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_hyperbolic_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C09)."

gh issue create --repo "$repo" \
  --title "C10: An isomorphism category does not carry `order`" \
  --body "\`Isomorphisms(X, Y).order()\` raises \`AttributeError\`, so the cardinality of the isomorphism set cannot be read as a group order.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_isomorphisms_of_a_two_element_set.sage::test_the_isomorphisms_are_the_automorphism_group\`
  \`AttributeError: 'FixedIsoCategory_with_category' object has no attribute 'order'\`

Defective call: sage/cpython/getattr.pyx:362.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_isomorphisms_of_a_two_element_set.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C10)."

gh issue create --repo "$repo" \
  --title "C11: `NumberFields()` does not carry `ring_of_integers`" \
  --body "\`NumberFields().ring_of_integers()(QQ)\` raises \`AttributeError\`; the functor that sends a number field to its ring of integers is not published on the category.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_integers.sage::test_the_integers_are_the_ring_of_integers_of_the_rationals\`
  \`AttributeError: 'NumberFields_with_category' object has no attribute 'ring_of_integers'\`

Defective call: /repos/sage-extensions/tests/objects/test_integers.sage:13.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_integers.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C11)."

gh issue create --repo "$repo" \
  --title "C12: `cardinality` refuses for the embedding set `Emb(L, L')`" \
  --body "\`Emb(L, L').cardinality()\` raises \`AssertionError: cannot compute the cardinality of Emb(...)\` where the number is finite and computable (the isometric embeddings of one positive-definite rank-one lattice into a root lattice), so \`roots()\` and the orthogonal-group count cannot be read.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_hyperbolic_plane.sage::test_the_vectors_of_square_minus_two\`
  \`AssertionError: cannot compute the cardinality of Emb(Integral lattice of rank 1 and signature (0, 1), Integral lattice of rank 2 and signature (1, 1)): its construction supplies no exact value or decided finite enum\`

The same defect also fails \`tests/objects/test_root_lattice_a2.sage::test_the_roots_and_isometries_of_a2\`, \`tests/objects/test_root_lattice_e8.sage::test_the_invariants_of_e8\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/sets/set_categories.py:2503.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_hyperbolic_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C12)."

gh issue create --repo "$repo" \
  --title "C13: `cardinality` refuses for a group whose finiteness is a `Predicate`" \
  --body "\`Group.cardinality()\` raises \`AssertionError: cannot compute the cardinality of the group ... : its finiteness is is_finite(...)\` for a finitely presented group of known finite order (Q_8, S_3, Aut of a ring), so the order of a finitely presented group cannot be read.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_integers.sage::test_the_automorphisms_of_the_integers\`
  \`AssertionError: cannot compute the cardinality of the group Aut_Category of modules over Integer Ring(Integer Ring): its finiteness is is_finite(Aut_Category of modules over Integer Ring(Integer Ring)), it has no cho\`

The same defect also fails \`tests/objects/test_quaternion_group.sage::test_the_presentation_of_q8\`, \`tests/objects/test_symmetric_group_s3.sage::test_the_coxeter_presentation\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/group/groups.py:459.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_integers.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C13)."

gh issue create --repo "$repo" \
  --title "C14: A `Predicate` is evaluated as a Python truth value" \
  --body "\`is_finite(...)\`, \`is_subset(...)\` and friends answer a \`Predicate\`, and \`bool()\` on it raises \`TypeError: the proposition ... has no Python truth value\`. Every user who writes \`if X.is_finite():\` fails, and the suite's assertions on those propositions fail.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_free_group_of_rank_two.sage::test_the_automorphism_group_of_f2\`
  \`TypeError: the proposition is_finite(Set of Morphisms from Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] to Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] in Core of Category of groups) has no\`
- \`tests/objects/test_free_module_of_rank_three.sage::test_the_automorphisms_of_zz3_are_infinite\`
  \`TypeError: the proposition is_finite(Aut_Category of modules over Integer Ring(Free module on {[0], [1], [2]} over Integer Ring)) has no Python truth value, because it may be undecided; call ask(...) on it to ge\`

The same defect also fails \`tests/objects/test_standard_triangle.sage::test_the_order_of_the_vertices_does_not_matter\`, \`tests/objects/test_two_hyperbolic_planes.sage::test_the_orthogonal_group_is_infinite\`, \`tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_plane_and_its_stabilizer\`, \`tests/objects/test_two_hyperbolic_planes.sage::test_an_isotropic_flag_and_its_stabilizer\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/logic.py:44.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: \`test_free_group_of_rank_two.sage\`, \`test_free_module_of_rank_three.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C14)."

gh issue create --repo "$repo" \
  --title "C15: `module_rank` refuses for a module over a non-field base" \
  --body "\`M.module_rank()\` raises \`AssertionError: the rank of ... is computed over a finite field for a finite module, or from a chosen basis\`, for \`QQ\` over \`ZZ\`, for a fractional ideal, and for an exterior algebra's graded piece.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_exterior_algebra_of_qq2.sage::test_the_graded_pieces_of_the_exterior_algebra\`
  \`AssertionError: the rank of Lambda(Free module on {[a], [b]} over Fraction Field of Integer Ring) over Fraction Field of Integer Ring is computed over a finite field for a finite module, or from a chosen basis or pre\`
- \`tests/objects/test_fractional_ideal_2z.sage::test_2z_is_principal_and_free_of_rank_one\`
  \`AssertionError: the rank of Fractional ideal (2) of Integer Ring over Integer Ring is computed over a finite field for a finite module, or from a chosen basis or presentation, and Fractional ideal (2) of Integer Ring\`

The same defect also fails \`tests/objects/test_tensor_algebra_of_qq2.sage::test_the_centre_of_the_tensor_algebra\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/pure/modules.py:2466.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: \`test_exterior_algebra_of_qq2.sage\`, \`test_fractional_ideal_2z.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C15)."

gh issue create --repo "$repo" \
  --title "C16: A cone or cocone morphism is constructed with one cone" \
  --body "The cone (and dually cocone) morphism constructor demands two cones for a morphism out of the identity cone, so \`Cone(X).identity()\` and the endomorphism category of a cone raise \`TypeError\`.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_identity_cocone_is_initial_among_cocones_on_itself\`
  \`TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets and Cocone with ap\`
- \`tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_has_one_endomorphism_category\`
  \`TypeError: a morphism in Category of _ cocone category needs two cocones under its diagram, but got Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets and Cocone with ap\`
- \`tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_identity_cone_is_terminal_among_cones_on_itself\`
  \`TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets and Cone with apex {0,...,\`
- \`tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_has_one_endomorphism_category\`
  \`TypeError: a morphism in Category of _ cone category needs two cones over its diagram, but got Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets and Cone with apex {0,...,\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/abstract_categories/products.py:1541, /repos/sage-extensions/src/sage_extensions/categories/abstract_categories/products.py:1622.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: \`test_cocone_under_a_one_object_diagram.sage\`, \`test_cone_over_a_one_object_diagram.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C16)."

gh issue create --repo "$repo" \
  --title "C17: `GL` of a torsion module is refused" \
  --body "\`GL(M)\` raises \`AssertionError: GL(...) is realized as a matrix group only for a free module with a finite selected basis\`, so the automorphisms of \`Z/6\` or \`F_3\` have no group.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_cyclic_module_zz6.sage::test_the_endomorphisms_and_automorphisms_of_zz6\`
  \`AssertionError: GL(Finitely presented module on 1 module generators over Integer Ring with invariant factors Invariant-factor family: [0 ↦ 6]) is realized as a matrix group only for a free module with a finite select\`

The same defect also fails \`tests/objects/test_prime_field_f3.sage::test_the_automorphisms_of_f3\`, which are files of #412.

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:4032.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_cyclic_module_zz6.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C17)."

gh issue create --repo "$repo" \
  --title "C18: The metric dual is refused for a degenerate lattice" \
  --body "\`L.dual_lattice()\` raises on the degenerate plane although the test asks for the radical; the refusal message states the form is degenerate, which is the hypothesis the caller is testing.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_degenerate_plane.sage::test_the_radical_is_the_line_through_e0_minus_e1\`
  \`AssertionError: Integral lattice of rank 2 and signature (1, 0) has no metric dual: the dual lattice is defined for a nondegenerate form, and Integral lattice of rank 2 and signature (1, 0) is not known to be nondege\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/lattices.py:6838.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_degenerate_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C18)."

gh issue create --repo "$repo" \
  --title "C19: The whole-algebra map of an infinite-rank free algebra is refused" \
  --body "\`ValueError: the whole-algebra map for Free module on Coproduct ... over Fraction Field ...\`, raised when the endomorphism category of a coordinate-ring algebra is formed.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_axis_has_one_endomorphism_category\`
  \`ValueError: the whole-algebra map for Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring/(x) -> Free module on Coproduct of the family over NN = {0, 1, 2, ...} ove\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/algebras/algebras.py:4631.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_a_coordinate_line_in_the_affine_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C19)."

gh issue create --repo "$repo" \
  --title "C20: `WeilDivisorGroups._call_` is called without its defining data" \
  --body "\`WeilDivisorGroups._call_() missing 1 required positional argument: 'prime_divisors'\`, so the divisor group of three points cannot be constructed.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_divisors_on_three_points.sage::test_the_weil_divisor_group_on_three_points\`
  \`TypeError: WeilDivisorGroups._call_() missing 1 required positional argument: 'prime_divisors'\`

Defective call: /sage/.venv/lib/python3.14/site-packages/sage/categories/category.py:592.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_divisors_on_three_points.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C20)."

gh issue create --repo "$repo" \
  --title "C21: A cardinal sum over `ZZ` is not decided" \
  --body "\`AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite\`, raised while the centre of an exterior algebra is formed.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_exterior_algebra_of_qq2.sage::test_the_centre_of_the_exterior_algebra\`
  \`AssertionError: cannot decide whether the cardinal sum_{i in Integer Ring} kappa_i is finite: it is not a finite sum, product, or supremum of known cardinals\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/sets/cardinals.py:732.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_exterior_algebra_of_qq2.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C21)."

gh issue create --repo "$repo" \
  --title "C22: Isomorphism of two free groups is undecided" \
  --body "\`AssertionError: whether <F_2> is isomorphic to <F_2>\` is undecided, so the free-group functor's agreement cannot be asserted.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_free_group_of_rank_two.sage::test_the_free_group_functor_agrees\`
  \`AssertionError: whether Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is isomorphic to Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined for every pair of groups, but the current preamble d\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/group/groups.py:6778.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_free_group_of_rank_two.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C22)."

gh issue create --repo "$repo" \
  --title "C23: The abelianization of a finitely presented group is refused" \
  --body "\`AssertionError: the abelianization of the finitely presented group ... is defined, but the carrier ...\`, so \`F_2^ab\` cannot be formed.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_free_group_of_rank_two.sage::test_the_abelianization_of_f2\`
  \`AssertionError: the abelianization of the finitely presented group Group generated by Group generators: [0 ↦ g_0, 1 ↦ g_1] is defined, but the current preamble has no presentation-quotient route for G/[G,G]; add it a\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/functors/abelianization.py:52.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_free_group_of_rank_two.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C23)."

gh issue create --repo "$repo" \
  --title "C24: A GAP element index is out of range" \
  --body "\`IndexError: index out of range\` from GAP while the isotropic lines of \`U\` are enumerated.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_hyperbolic_plane.sage::test_the_isotropic_lines_of_u\`
  \`IndexError: index out of range.\`

Defective call: sage/libs/gap/element.pyx:3170.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_hyperbolic_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C24)."

gh issue create --repo "$repo" \
  --title "C25: `O(L)` of an indefinite lattice is refused" \
  --body "\`AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice\`, so \`O(U)\` has no arithmetic.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_hyperbolic_plane.sage::test_the_orthogonal_group_of_u\`
  \`AssertionError: cannot compute O(Integral lattice of rank 2 and signature (1, 1)) as a finite group: that computation is supplied for a definite lattice of finite rank over ZZ, and Integral lattice of rank 2 and sign\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/lattice_morphisms.py:4531.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_hyperbolic_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C25)."

gh issue create --repo "$repo" \
  --title "C26: A base ring is refused as a field" \
  --body "\`ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring\`, raised on the base change of a free module to \`QQ\`.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_free_module_of_rank_three.sage::test_the_base_change_to_the_rationals\`
  \`ValueError: base must be a field or a subcategory of Fields(); got Fraction Field of Integer Ring\`

Defective call: /sage/.venv/lib/python3.14/site-packages/sage/categories/vector_spaces.py:70.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_free_module_of_rank_three.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C26)."

gh issue create --repo "$repo" \
  --title "C27: `/` is applied to owned module elements" \
  --body "The tests write \`M / N\` and \`ZZ / I\`, which the owned modules do not support; the library spells these \`quotient_module\` and \`quotient_ring\`, and \`Modules.__truediv__\` is absent. (Whether the operator should exist is a design question, not a test bug: \`AGENTS.md\` bans \`__truediv__\` on modules, so the suite and the policy disagree.)

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_cyclic_module_zz6.sage::test_the_cokernel_and_the_quotient_agree\`
  \`TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'\`
- \`tests/objects/test_cyclic_module_zz6.sage::test_the_quotient_of_the_regular_module_by_the_ideal\`
  \`TypeError: unsupported operand type(s) for /: '_OwnedRingParent_with_category' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'\`
- \`tests/objects/test_free_module_of_rank_three.sage::test_a_quotient_of_zz3\`
  \`TypeError: unsupported operand type(s) for /: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType' and 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'\`

Defective call: /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:16, /repos/sage-extensions/tests/objects/test_cyclic_module_zz6.sage:20, /repos/sage-extensions/tests/objects/test_free_module_of_rank_three.sage:70.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: \`test_cyclic_module_zz6.sage\`, \`test_free_module_of_rank_three.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C27)."

gh issue create --repo "$repo" \
  --title "C28: Two constructions of one lattice do not compare equal" \
  --body "\`Lattices(ZZ)(\"A1\") + Lattices(ZZ)(\"A2\")\` and the block-Gram construction of the same lattice do not compare equal, and neither do the catalogue and Gram constructions of \`A_2\`, \`E_8\` and \`U + U\`.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a1_plus_a2.sage::test_the_sum_and_the_block_gram_agree\`
  \`assert: Integral latt...gnature (0, 3) == Integral latt...gnature (0, 3)\`
- \`tests/objects/test_degenerate_plane.sage::test_the_lattice_and_the_form_module_constructions_agree\`
  \`assert: Integral latt...gnature (1, 0) == Free module o...r Integer Ring\`

The same defect also fails \`tests/objects/test_root_lattice_a2.sage::test_the_named_and_the_gram_constructions_agree\`, \`tests/objects/test_root_lattice_e8.sage::test_the_catalogue_entry_agrees\`, \`tests/objects/test_two_hyperbolic_planes.sage::test_the_sum_and_the_block_gram_agree\`, which are files of #412.

Defective call: /repos/sage-extensions/tests/objects/test_a1_plus_a2.sage:9, /repos/sage-extensions/tests/objects/test_degenerate_plane.sage:12.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 2 files: \`test_a1_plus_a2.sage\`, \`test_degenerate_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C28)."

gh issue create --repo "$repo" \
  --title "C29: A direct sum is not an object of `DirectSumObjects(Lattices(ZZ))`" \
  --body "\`L in DirectSumObjects(Lattices(ZZ))\` answers false for a lattice built as a sum, so a user cannot test the decomposition it was constructed with.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a1_plus_a2.sage::test_the_categories_of_a1_plus_a2\`
  \`assert: Integral lattice of rank 3 and signature (0, 3) in Category of objects of lattices with a chosen direct-sum decomposition\`

The same defect also fails \`tests/objects/test_two_hyperbolic_planes.sage::test_the_categories_of_u_plus_u\`, which are files of #412.

Defective call: /repos/sage-extensions/tests/objects/test_a1_plus_a2.sage:16.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_a1_plus_a2.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C29)."

gh issue create --repo "$repo" \
  --title "C30: A cone or cocone is not an object of its cone category" \
  --body "\`cone in Cones(F)\` and \`cocone in Cocones(F)\` answer false for the cone built by the category's own constructor.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_cocone_is_an_object_of_the_cocone_category\`
  \`assert: Cocone with apex {0,...,2} under Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cocone category\`
- \`tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_cone_is_an_object_of_the_cone_category\`
  \`assert: Cone with apex {0,...,2} over Functor: Discrete category on {0,...,0} -> Category of sets in Category of _ cone category\`

Defective call: /repos/sage-extensions/tests/objects/test_cocone_under_a_one_object_diagram.sage:19, /repos/sage-extensions/tests/objects/test_cone_over_a_one_object_diagram.sage:19.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: \`test_cocone_under_a_one_object_diagram.sage\`, \`test_cone_over_a_one_object_diagram.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C30)."

gh issue create --repo "$repo" \
  --title "C31: Two constructions of one functor do not compare equal" \
  --body "\`cone.apex_and_leg(...)\` and the functor rebuilt from its data do not compare equal.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_cocone_under_a_one_object_diagram.sage::test_the_apex_and_the_leg\`
  \`assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets\`
- \`tests/objects/test_cone_over_a_one_object_diagram.sage::test_the_apex_and_the_leg\`
  \`assert: Functor: Discrete category on {0,...,0} -> Category of sets is Functor: Discrete category on {0,...,0} -> Category of sets\`

Defective call: /repos/sage-extensions/tests/objects/test_cocone_under_a_one_object_diagram.sage:26, /repos/sage-extensions/tests/objects/test_cone_over_a_one_object_diagram.sage:26.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 2 files: \`test_cocone_under_a_one_object_diagram.sage\`, \`test_cone_over_a_one_object_diagram.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C31)."

gh issue create --repo "$repo" \
  --title "C32: The assertion at `test_a_coordinate_line_in_the_affine_plane.sage:23` does not hold: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction " \
  --body "The proposition asserted at \`/repos/sage-extensions/tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23\` is false on main: \`Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction \`. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_a_coordinate_line_in_the_affine_plane.sage::test_the_categories_of_the_axis\`
  \`assert: Closed subscheme of Spectrum of Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring defined by x in Category of smooth schemes over Fraction Field of In\`

Defective call: /repos/sage-extensions/tests/objects/test_a_coordinate_line_in_the_affine_plane.sage:23.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_a_coordinate_line_in_the_affine_plane.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C32)."

gh issue create --repo "$repo" \
  --title "C33: The assertion at `test_affine_plane_over_qq.sage:15` does not hold: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring" \
  --body "The proposition asserted at \`/repos/sage-extensions/tests/objects/test_affine_plane_over_qq.sage:15\` is false on main: \`Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring\`. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_affine_plane_over_qq.sage::test_the_affine_plane_is_the_spectrum_of_its_coordinate_ring\`
  \`assert: Spectrum of F...f Integer Ring == Spectrum of F...f Integer Ring\`

Defective call: /repos/sage-extensions/tests/objects/test_affine_plane_over_qq.sage:15.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_affine_plane_over_qq.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C33)."

gh issue create --repo "$repo" \
  --title "C34: `module_morphisms.py:1978` raises ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:" \
  --body "The call at \`/repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978\` raises \`ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:\`. A user reaching that operation through the public API gets the exception instead of the documented object.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_discriminant_quadratic_form_of_a1.sage::test_the_brown_invariant_of_q_a1\`
  \`ValueError: [(1)/(2)] in Fraction Field of Integer Ring / (1)Integer Ring is not in the image of Generic morphism:\`

Defective call: /repos/sage-extensions/src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py:1978.

Introduced by: not bisected; at main's root commit the same test fails through an earlier error, so bisecting this signature reports the commit that unmasked the defect.

Scope: 1 file: \`test_discriminant_quadratic_form_of_a1.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C34)."

gh issue create --repo "$repo" \
  --title "C35: The assertion at `test_integers.sage:28` does not hold: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring" \
  --body "The proposition asserted at \`/repos/sage-extensions/tests/objects/test_integers.sage:28\` is false on main: \`Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring\`. The test states the contract; the construction it names does not meet it.

Failing tests, on main 9b29712 (2026-11-14) in the published image:

- \`tests/objects/test_integers.sage::test_the_integers_as_an_algebra_over_themselves\`
  \`assert: Generic endomorphism of Integer Ring == Generic endomorphism of Integer Ring\`

Defective call: /repos/sage-extensions/tests/objects/test_integers.sage:28.

Introduced by: main's root commit \`c731175\` (2026-10-26, Zack Garza <dzackgarza@gmail.com>): the file was run there and the same failure appears.

Scope: 1 file: \`test_integers.sage\` of the #408 slice.
Triage record: results/issue408-triage.md (C35)."

