# Triage of the failing tests of `tests/groups` (second half) on sage-extensions main (#411)

Run on main `36e5eac` (2026-11-14) in the published image, one file per pytest process,
one process at a time:

```
~/sage-image/run.sh -w /work -b <port-repo>:/work -b ~/ai-review-ci:/ci \
  -b <worktree>:/repos/sage-extensions -b <repo>/.git:<repo>/.git -- \
  /bin/sh -c 'export HOME=/root; export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src; \
    cd /repos/sage-extensions; exec just test "$@"' sh \
  -o addopts= -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates --no-test-lint -q --tb=short --no-header <test file>
```

`just test` is the repository's own invocation (`justfile`, delegating to
`~/ai-review-ci/justfiles/sage.just`). Its `addopts` are blanked and the two plugins
reselected by hand because the image's venv has neither `pytest-timeout` nor
`pytest-reportlog`, so the unmodified `addopts` fail with `unrecognized arguments:
--timeout=60 --timeout-method=signal --report-log=tests/.report/run.jsonl`. That is an
environment gap of this host, recorded here, not a finding about the repository.
The slice is the 38 files the issue lists; they collect **148 tests**.

**Result.** On `36e5eac`, **42 failing tests** in 19 of the 38 files, assigned to **24
causes**: 2 repaired by a commit on main (one test green, and the two that C03 hands to
C04 named where they go), 22 filed. No test is unassigned and none is in two live causes.

| exception | tests |
| --- | --- |
| `TypeError` | 15 |
| `assert` | 8 |
| `AssertionError` | 7 |
| `AttributeError` | 7 |
| `NameError` | 4 |
| `Defn` | 3 |

The repaired tree is the tree of this commit (the rank repair `d0cfd20`, the class-sum
repair `dcfe72c`) on `8971654`; the same 38 files were run again on it
(`.tmp/qc-evidence/issue411-slice-final.log`), which is the state recorded here: 41
failing, 107 passing. The #407/#408/#410/#412 repairs that landed on main while this was
in flight do not change any test of this slice: the 41 failing ids on `36e5eac` with
these two repairs and on `8971654` with them are the same set.

## Causes

| cause | defect | tests | introduced by | repair |
| --- | --- | --- | --- | --- |
| C01 | The session namespace does not publish the subgroup constructors the suite names | 5 | root commit c731175 | open; filed |
| C02 | The catalogue matrix groups refuse the rank the session writes | 1 | root commit c731175 | repaired in d0cfd20 |
| C03 | The centre of a group algebra sums its class sums from the integer zero | 2 | root commit c731175 | repaired in dcfe72c |
| C04 | A reduced acted module cannot build the morphism that restricts it | 2 | not bisected | open; filed |
| C05 | The conjugation morphism hands a GAP whole-group map to the element constructor | 5 | root commit c731175 | open; filed |
| C06 | The order of a finitely presented group is refused | 2 | 42d7361 (2026-11-02, agent) | open; filed |
| C07 | An acted group module is not placed in its character-representation category | 3 | root commit c731175 | open; filed |
| C08 | A generator-image dictionary keyed by the group's generators is refused | 2 | root commit c731175 | open; filed |
| C09 | The abelian coproduct refuses its own abelian factors | 2 | root commit c731175 | open; filed |
| C10 | The free-product injection has no engine crossing | 2 | root commit c731175 | open; filed |
| C11 | The owned product construction is not placed in the categories its factors force | 2 | root commit c731175 | open; filed |
| C12 | `Groups().product` and `Groups().coproduct` answer the generic limit object | 2 | not bisected | open; filed |
| C13 | The endset of a finite group action has no cardinality | 1 | root commit c731175 | open; filed |
| C14 | `Subgroups(G)` has no cardinality | 1 | root commit c731175 | open; filed |
| C15 | A group carries no `abelianization`, and the functor refuses presented groups | 1 | root commit c731175 | open; filed |
| C16 | A ring morphism built inside a native computation is refused as an arrow of another Mor | 3 | root commit c731175 | open; filed |
| C17 | A raw Sage integer is refused at the owned integer ring | 1 | root commit c731175 | open; filed |
| C18 | The base ring's scalar action on a group-algebra module element is refused | 1 | not bisected | open; filed |
| C19 | A quotient of two cardinals is refused | 1 | root commit c731175 | open; filed |
| C20 | The session's `matrix` takes one row family, not a ring and a row family | 1 | 14b9cc1 (2026-10-26, Zack Garza) | open; filed |
| C21 | The owned quadratic field has no `gen` | 1 | not bisected | open; filed |
| C22 | Applying the identity endomorphism of a subobject set rebuilds the object | 1 | root commit c731175 | open; filed |
| C23 | A character is not a member of the set of irreducible characters | 1 | root commit c731175 | open; filed |
| C24 | The retained sweep is stored on the orbit object it describes | 1 | 55592e9 (2026-11-07, D. Zack Garza) | open; filed |

Each cause below states what a user gets when it closes, its failing tests with the error each reports, the defective call, the commit that introduced it, and its scope. The 21 open causes are also staged as paste-ready issue bodies under `.tmp/qc-evidence/triage/411-<cause>-<slug>.md`.

### C01 — The session namespace does not publish the subgroup constructors the suite names

A user who writes the session-standard import cannot name a subgroup category at all: `Subgroups(G)`, `GeneratedSubgroups(G)` and `Torsors(G, action)` raise `NameError`, so every question about a subgroup, a generating family or a torsor has to reach into a private module.

- Defective call: src/sage_extensions/all.py (the group import block); the names are defined at categories/group/groups.py:8204 (Subgroups), :8358 (GeneratedSubgroups) and categories/group/g_sets.py:1832 (Torsors).
- Failing tests (5, 3 files):
    - `tests/groups/test_g_sets_torsor_archive.sage::test_the_transporter_of_the_regular_c3_torsor_from_x_to_gx_is_g` — `NameError: name 'Torsors' is not defined`
    - `tests/groups/test_group_morphisms_archive.sage::test_noninjective_group_map_factors_through_its_proper_image` — `NameError: name 'Subgroups' is not defined`
    - `tests/groups/test_group_morphisms_archive.sage::test_generated_subgroup_finite_image_lifts_use_its_selected_generators` — `assert {1, (1 3)(2 4)} == {(1 3)(2 4), 1}`
    - `tests/groups/test_group_morphisms_archive.sage::test_generated_subgroup_map_image_uses_its_retained_generator_family` — `NameError: name 'Subgroups' is not defined`
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_group_equalizer_has_its_subgroup_inclusion_and_universal_map` — `NameError: name 'Subgroups' is not defined`
- Introduced by: not bisected: the namespace never published these names, so their absence is at main's root commit c731175 (2026-10-26, Zack Garza), which imported the suite; the file was run there and the failing tests fail there too.
- Repair: open; the session namespace itself, not three names: `all.py` restates the area packages' public surfaces by hand, and the copy has drifted. `sage_extensions/groups/__init__.py` already declares `Subgroups` and `Torsors` in its `__all__` (and does not declare `GeneratedSubgroups`, which its owner module defines), so publishing the owners' declarations and declaring the missing name is the repair; editing three names into the copy leaves the mechanism in place. That reaches every name in the session, so it is filed and not patched here. It is the same cause as #408's, whose hand-added names were reverted for this reason (`50a83cb`). Measured, not landed: adding the three names to `all.py` cleared four of these five tests and left the fifth reporting its next defect, a Python `set` of group elements whose equality disagrees with the owned set.

### C02 — The catalogue matrix groups refuse the rank the session writes

`Groups.GL(2, GF(3))`, `Groups.GU(...)`, `Groups.GO(...)`, `Groups.SO(...)`, `Groups.SU(...)` and `Groups.Sp(2, GF(3))` refuse every degree written as a session literal, with `GL_n(R) needs a rank n that is an integer n >= 0, but got 2`: no matrix group of a positive rank can be constructed from the session at all.

- Defective call: src/sage_extensions/categories/group/groups.py:2445 (_general_linear_group), :2345 (_group_over_ring), :2554 (_Sp): each tested membership in the engine's ZZ.
- Failing tests (1, one file):
    - `tests/groups/test_owned_groups.sage::test_sl2_f3_is_sp2_f3_and_modulo_its_centre_is_a4` — `AssertionError: GL_n(R) needs a rank n that is an integer n >= 0, but got 2`
- Introduced by: not bisected: the three guards test `degree in ZZ` against the engine's integer ring in the root commit c731175 (2026-10-26, Zack Garza); the hosted integer element that the session's literals produce has the owned integer ring as its parent, so the refusal is present there too. `_SL` in the same file already read its rank with `int()`.
- Repair: repaired in `d0cfd20`; the three guards in groups.py, shared by GL/GU/GO/SO/SU/Sp; the one failing test is green after the change and its five assertions run. The rank is decided once, by membership in the preamble's integers, and `_SL` (which read it with `int()` and so refused the exact rational `QQ(2)`) now shares that decision, so all six matrix families admit exactly the same values.

### C03 — The centre of a group algebra sums its class sums from the integer zero

Asking a finite group algebra for its centre raises `TypeError: unsupported operand type(s) for +: 'int' and 'OwnedJoinCategory.element_class[_SparseFreeModuleElement]'`, so no isotypic decomposition, no character table and no invariant computation that goes through `Z(R[G])` can run.

- Defective call: src/sage_extensions/categories/algebras/group_algebras.py:96 (_finite_group_algebra_center).
- Failing tests (2, one file):
    - `tests/groups/test_restricted_actions.sage::test_the_standard_isotypic_component_is_the_standard_representation` — `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free modul…`
    - `tests/groups/test_restricted_actions.sage::test_the_invariants_of_the_permutation_module_are_the_trivial_representation` — `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free modul…`
- Introduced by: not bisected: the `sum(...)` over module elements with Python's integer start is in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: repaired in `dcfe72c`; one site; the two tests now report C04, the construction they ask for next. The class sum is routed through `Modules.linear_combination`, the operation the module owns for a finite family of generators, instead of spelling that fold beside it.

### C04 — A reduced acted module cannot build the morphism that restricts it

`representation.restrict_action_to(sub.inclusion())` raises `TypeError: ... belongs to Free module on Product of the family over {0,...,1} ..., not to Mor_Alg(...); apply the functor between the categories instead of constructing an arrow from another arrow (CON-17)`, so an isotypic component or an invariant submodule of a group representation cannot be produced with its restricted action.

- Defective call: src/sage_extensions/categories/modules/group_modules/group_modules.py:800 (restrict_action_to) into :1283 (_from_equivariant_images); the refusal is the Mor_Alg element-constructor check reached at src/sage_extensions/categories/abstract_categories/mor_categories.py:835.
- Failing tests (2, one file):
    - `tests/groups/test_restricted_actions.sage::test_the_standard_isotypic_component_is_the_standard_representation` — `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free modul…`
    - `tests/groups/test_restricted_actions.sage::test_the_invariants_of_the_permutation_module_are_the_trivial_representation` — `TypeError: Generic morphism: From: Free module on {[0], [1], [2]} over Fraction Field of Integer Ring To: Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring belongs to Free modul…`
- Introduced by: not bisected: the failure is reached through C03 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.
- Repair: open; the acted-module reduction; two tests.

### C05 — The conjugation morphism hands a GAP whole-group map to the element constructor

`G.conjugation_morphism()`, the map that sends an element to its inner automorphism, raises `TypeError: a GAP whole group map is private engine output; give generator images`, so `Aut(G)` cannot be reached from `G` and no inner-automorphism subgroup, kernel or index can be computed.

- Defective call: src/sage_extensions/categories/group/groups.py:5993 (conjugation_morphism) calls `automorphisms(libgap.ConjugatorAutomorphism(...))`, which is the public element constructor refusing at :4572.
- Failing tests (5, 3 files):
    - `tests/groups/test_group_automorphisms_archive.sage::test_conjugation_realizes_all_automorphisms_of_s3` — `TypeError: a GAP whole group map is private engine output; give generator images`
    - `tests/groups/test_group_automorphisms_archive.sage::test_s6_has_outer_automorphisms_of_index_two` — `TypeError: a GAP whole group map is private engine output; give generator images`
    - `tests/groups/test_groups_archive.sage::test_conjugation_on_d4_has_the_centre_as_kernel_and_inner_group_v4` — `TypeError: a GAP whole group map is private engine output; give generator images`
    - `tests/groups/test_groups_archive.sage::test_conjugation_on_s3_is_an_isomorphism_onto_its_automorphism_group` — `TypeError: a GAP whole group map is private engine output; give generator images`
    - `tests/groups/test_mathieu_automorphism_archive.sage::test_m12_inner_automorphisms_have_index_two_in_the_full_automorphism_group` — `TypeError: a GAP whole group map is private engine output; give generator images`
- Introduced by: not bisected: both the refusal (:4572) and the call that trips it (:5993) are in the root commit c731175 (2026-10-26, Zack Garza); the line was blamed there.
- Repair: open; one call site and the five tests that conjugate. Measured candidate repair, NOT landed: routing the conjugator through the documented protected crossing `automorphisms._from_engine_morphism(...)` builds the map and moves every one of the five to its next defect -- `AttributeError: 'OwnedGroupAutomorphismGroup...ArrowType' object has no attribute 'gap'` from `kernel()`, and M12's file did not finish in 360 s where it used to fail in 0.87 s -- so the crossing alone is not a repair.

### C06 — The order of a finitely presented group is refused

`presented.order()` raises `AssertionError: cannot compute the cardinality of the group ...: its finiteness is is_finite(...), it has no chosen free basis, and it is not known to be infinite and finitely generated`, so no group given by generators and relations has an order -- the most basic question one asks a presentation.

- Defective call: src/sage_extensions/categories/group/groups.py:459 (_group_cardinality), reached from :6130 (order).
- Failing tests (2, one file):
    - `tests/groups/test_group_hierarchy_archive.sage::test_the_coxeter_presentation_of_s3_presents_a_group_of_order_six` — `AssertionError: cannot compute the cardinality of the group Group generated by Group generators: [0 ↦ g_1, 1 ↦ g_2]: its finiteness is is_finite(Group generated by Group generators: [0 ↦ g_1, 1 ↦ g_2]…`
    - `tests/groups/test_group_hierarchy_archive.sage::test_one_generator_and_one_square_relator_present_the_group_of_order_two` — `AssertionError: cannot compute the cardinality of the group Group generated by Group generators: [0 ↦ g_1]: its finiteness is is_finite(Group generated by Group generators: [0 ↦ g_1]), it has no chose…`
- Introduced by: 42d7361 (2026-11-02, agent) 'fix: a decided finiteness is placed, and cardinality asks it'; blamed at :459.
- Repair: open; the cardinality decision for presented groups; two tests. The same refusal is #408's C22. Note this is also what makes C05's candidate repair unusable: `kernel().order()` on Aut(G) lands here.

### C07 — An acted group module is not placed in its character-representation category

`Modules(R[G])(M, action).character()` and `.brauer_character()` raise `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`; the ordinary and Brauer character surfaces exist, but the module the user builds is never placed in the category that carries them.

- Defective call: the acted-module route, `Modules(R[G])(module, action)`; the surface it does not reach is categories/modules/group_modules/group_modules.py:1738 (OrdinaryCharacterRepresentations.character) and :1777 (BrauerCharacterRepresentations.brauer_character).
- Failing tests (3, 2 files):
    - `tests/groups/test_group_law.sage::test_the_natural_permutation_module_of_s3_has_character_3_1_0` — `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`
    - `tests/groups/test_module_characters.sage::test_the_character_of_sign_plus_trivial_of_s3_is_2_0_2` — `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'character'`
    - `tests/groups/test_module_characters.sage::test_the_2_modular_brauer_character_of_the_order_three_action_of_c6_on_f2_squared_is_2_minus1_minus1` — `AttributeError: 'GeneralModules.parent_class[_CoefficientModuleEngine].ObjectType' object has no attribute 'brauer_character'`
- Introduced by: not bisected: the categories and their `_call_` refinements are in the root commit c731175 (2026-10-26, Zack Garza), and the acted-module constructor never refines into them.
- Repair: open; the placement of an acted module; three tests, ordinary and modular.

### C08 — A generator-image dictionary keyed by the group's generators is refused

`G.Mor(H)({g: image, ...})`, writing the dictionary over the generators `G.group_generators()` returns, raises `AssertionError: the dictionary does not define a homomorphism out of ...: it must give an image for every element of the free basis {0,...,0}, but it has keys (g_0,)`: the natural spelling of a homomorphism out of a free or presented group is refused.

- Defective call: src/sage_extensions/categories/group/groups.py:4470 (_element_constructor_ / _from_group_generator_images).
- Failing tests (2, 2 files):
    - `tests/groups/test_group_morphisms_archive.sage::test_cokernel_of_squaring_on_an_infinite_presented_group` — `AssertionError: the dictionary does not define a homomorphism out of Group generated by Group generators: [0 ↦ g_0]: it must give an image for every element of the free basis {0,...,0}, but it has key…`
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_infinite_presented_group_coequalizer_descends_homomorphism` — `AssertionError: the dictionary does not define a homomorphism out of Group generated by Group generators: [0 ↦ g_0]: it must give an image for every element of the free basis {0,...,0}, but it has key…`
- Introduced by: not bisected: the key comparison is in the root commit c731175 (2026-10-26, Zack Garza); blamed at :4470.
- Repair: open; the generator-image ingress; two tests, including the cokernel and coequalizer of an infinite presented group.

### C09 — The abelian coproduct refuses its own abelian factors

`AbelianGroups().coproduct_construction((C_2, C_2))` raises `TypeError: the coproduct of ... cannot be formed in Category of abelian groups: some factor is not an object of Category of abelian groups`, although both factors are cyclic; the coproduct of abelian groups, which is their direct sum, cannot be formed.

- Defective call: src/sage_extensions/categories/group/groups.py:5298 (_categorical_coproduct_construction).
- Failing tests (2, one file):
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_abelian_coproduct_of_two_cyclic_groups_is_product_not_free_product` — `TypeError: the coproduct of Group coproduct factors: [0 ↦ Cyclic group C_2 of order 2, 1 ↦ Cyclic group C_2 of order 2] cannot be formed in Category of abelian groups: some factor is not an object of…`
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_mixed_abelian_coproduct_injections_are_sections_of_selected_projections` — `TypeError: the coproduct of Group coproduct factors: [0 ↦ Group generated by Group generators: [0 ↦ g_0], 1 ↦ Cyclic group C_2 of order 2] cannot be formed in Category of abelian groups: some factor i…`
- Introduced by: not bisected: the membership test that refuses the factors is in the root commit c731175 (2026-10-26, Zack Garza); blamed at :5298.
- Repair: open; the coproduct construction of groups in a subcategory of abelian groups; two tests.

### C10 — The free-product injection has no engine crossing

Taking a factor injection out of a free product raises `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'` (after `KeyError: <id>`), so a free product's structure morphisms, and every cocone factorization through them, cannot be produced.

- Defective call: src/sage_extensions/categories/group/groups.py:5417 (injection of the free product), on the arrow type `OwnedIndexedFreeGroupMor`.
- Failing tests (2, one file):
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_free_product_of_infinite_free_and_finite_cyclic_groups` — `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'`
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_free_product_factors_a_cocone_into_a_non_gap_predicate_group` — `AttributeError: 'OwnedIndexedFreeGroupMor_with_category_with_category' object has no attribute '_from_engine_morphism'`
- Introduced by: not bisected: the injection and its arrow type are in the root commit c731175 (2026-10-26, Zack Garza); blamed at :5417.
- Repair: open; the free-product structure morphisms; two tests.

### C11 — The owned product construction is not placed in the categories its factors force

`Groups().product_construction((C_2, C_2)).object()` is not an object of `AbelianGroups()`, and the product of a free group with a cyclic group is not an object of `FinitelyPresentedAsGroup()`, so the product of groups does not report the structure its factors have.

- Defective call: the group product construction (`Groups().product_construction(...)` / `Groups().FinitelyPresentedAsGroup().product_construction(...)`); the placement the object does not get is the membership of its factors.
- Failing tests (2, one file):
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_group_product_retains_abelianity_from_factors_not_selected_category` — `assert Group of order 4 generated by Group generators: [(1 2) ↦ (1 2), (3 4) ↦ (3 4)] in Category of abelian groups`
    - `tests/groups/test_group_products_and_coproducts_of_presentations.sage::test_product_of_free_and_finite_cyclic_groups_transports_factor_maps` — `assert Group generated by Group generators: [0 ↦ g_0] x Cyclic group C_2 of order 2 in Category of finitely presented groups`
- Introduced by: not bisected: the construction is in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: open; the placement of a product object; two tests.

### C12 — `Groups().product` and `Groups().coproduct` answer the generic limit object

`Groups().product((C_2, C_3))` answers `Product of the family over {0,...,1}`, which is not an object of `Groups()` (and the same for `coproduct`), so the category-level product of groups cannot be asked its order or compared with `C_6`.

- Defective call: `Groups().product` / `Groups().coproduct` (the categorical limit in categories/abstract_categories/products.py), which answers the generic limit rather than the owned group construction that `product_construction` builds.
- Failing tests (2, one file):
    - `tests/groups/test_groups_archive.sage::test_finite_group_product_retains_group_structure_and_order` — `assert Product of the family over {0,...,1} in Category of groups`
    - `tests/groups/test_groups_archive.sage::test_group_coproduct_is_the_owned_free_product` — `assert Coproduct of the family over {0,...,1} in Category of groups`
- Introduced by: not bisected: the failure is reached through C03 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.
- Repair: open; the category-level product and coproduct of groups; two tests.

### C13 — The endset of a finite group action has no cardinality

`Mor_G(X, X).cardinality()` for a finite `G`-set raises `AssertionError: cannot compute the cardinality of Mor_Cyclic group C_3 of order 3(...)`: the equivariant self-maps of a finite action are finite and computable, and their number cannot be read.

- Defective call: src/sage_extensions/categories/sets/set_categories.py:2503 (cardinality), for the endset of an action; the construction supplies no exact value (this is #408's C17/C18 refusal class).
- Failing tests (1, one file):
    - `tests/groups/test_g_sets_torsor_archive.sage::test_the_equivariant_self_maps_of_the_regular_c3_set_are_its_three_translations` — `AssertionError: cannot compute the cardinality of Mor_Cyclic group C_3 of order 3({1, (1 2 3), (1 3 2)} with Cyclic group C_3 of order 3-action, {1, (1 2 3), (1 3 2)} with Cyclic group C_3 of order 3-…`
- Introduced by: not bisected: the refusal is in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: open; the endset of a finite group action; one test.

### C14 — `Subgroups(G)` has no cardinality

`Subgroups(C_6).cardinality()` raises `AssertionError: cannot compute the cardinality of Subgroups of Cyclic group C_6 of order 6`: the number of subgroups of a finite group is finite and computable, and cannot be read.

- Defective call: src/sage_extensions/categories/sets/set_categories.py:2503 for the object at src/sage_extensions/categories/group/groups.py:8204 (Subgroups).
- Failing tests (1, one file):
    - `tests/groups/test_groups_archive.sage::test_finite_group_subgroups_are_owned_and_keep_the_ambient_group` — `AssertionError: cannot compute the cardinality of Subgroups of Cyclic group C_6 of order 6: its construction supplies no exact value or decided finite enumeration (it is in Join of Category of finite…`
- Introduced by: not bisected: both the parameterized category and the refusal are in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: open; the subgroup set of a finite group; one test.

### C15 — A group carries no `abelianization`, and the functor refuses presented groups

`G.abelianization()` raises `AttributeError: ... object has no attribute 'abelianization'`: the functor is published only on the category (`Groups().abelianization()`), and for a finitely presented group that functor refuses with `AssertionError: the abelianization of the finitely presented group ... is defined, but the current preamble has no presentation-quotient route for G/[G,G]`.

- Defective call: the group's own surface (absent), and src/sage_extensions/categories/functors/abelianization.py:52 (the presented-group refusal).
- Failing tests (1, one file):
    - `tests/groups/test_owned_groups.sage::test_the_abelianization_of_the_free_product_of_c2_and_c3_is_c6` — `AttributeError: 'OwnedJoinCategory.parent_class[_GroupEngine].ObjectType' object has no attribute 'abelianization'`
- Introduced by: not bisected: the category-level functor and its presented-group refusal are in the root commit c731175 (2026-10-26, Zack Garza); blamed at abelianization.py:52. The same refusal is #408's C37.
- Repair: open; the abelianization of a group, as an object method and for presented groups; one test. The named repair is a quotient route G/[G,G] at the exact-sequence owner, which is a decision about coset enumeration, not a local patch.

### C16 — A ring morphism built inside a native computation is refused as an arrow of another Mor

Every Galois-group computation over `F_5` that names the Frobenius or a cyclotomic correspondence raises `TypeError: Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`, so the open subgroups of `Gal(F_5bar/F_5)` and the finite Galois groups it generates cannot be formed.

- Defective call: src/sage_extensions/categories/rings/ring_foundation.py:573 (_ringlike_mor_element), reached while a native ring computation builds a ring morphism.
- Failing tests (3, 2 files):
    - `tests/groups/test_open_absolute_galois_subgroups_archive.sage::test_the_open_subgroup_of_the_galois_group_of_f5_fixing_f25_has_index_two` — `Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`
    - `tests/groups/test_open_absolute_galois_subgroups_archive.sage::test_open_subgroups_of_the_abelian_galois_group_of_f5_are_their_own_conjugacy_classes` — `Defn: z3 |--> z3 is an arrow of another Mor; native ring computations use the protected engine crossing`
    - `tests/groups/test_profinite_groups_archive.sage::test_frobenius_generates_each_finite_galois_group_of_f5` — `Defn: z2 |--> z2 is an arrow of another Mor; native ring computations use the protected engine crossing`
- Introduced by: not bisected: the refusal is in root commit c731175 (2026-10-26, Zack Garza); the line was blamed there. The same refusal is reached in tests/objects after #408's closure repair, so it is filed there too; the two slices share the owner.
- Repair: open; the ring-morphism boundary of a native computation; three tests. Until it is repaired the algebraic closure these tests need is available (dda0328 landed on main), so the closure is no longer the obstruction and this is.

### C17 — A raw Sage integer is refused at the owned integer ring

`TypeError: cannot convert 3 into Integer Ring: it is a raw Sage element of Integer Ring; construct it from a ring of this session`, raised while the mod-3 cyclotomic character of `Gal(F_5bar/F_5)` is evaluated: an engine integer produced inside the computation cannot be used as an exponent in the owned ring.

- Defective call: src/sage_extensions/categories/rings/ring_foundation.py:6525 (the owned integer ring's element constructor).
- Failing tests (1, one file):
    - `tests/groups/test_profinite_character_mor_archive.sage::test_mod_three_cyclotomic_character_of_f5_has_kernel_of_index_two` — `TypeError: cannot convert 3 into Integer Ring: it is a raw Sage element of Integer Ring; construct it from a ring of this session`
- Introduced by: not bisected: the constructor's refusal is in root commit c731175 (2026-10-26, Zack Garza); the line was blamed there.
- Repair: open; the ingress of an engine integer into the owned integer ring, on a path the library itself computes; one test. The boundary is deliberate (`OWN-02`), so the repair is at the computation that produces the engine integer, not at the constructor.

### C18 — The base ring's scalar action on a group-algebra module element is refused

`QQ(2)/QQ(3) * total`, scaling a module element by a base-ring element, raises `TypeError: unsupported operand parent(s) for *: 'Fraction Field of Integer Ring' and 'Module over Group algebra of Symmetric group S_3 ...'`, so a linear combination with rational coefficients cannot be written.

- Defective call: the left scalar action on an acted module element (the ring element's `__mul__` does not reach the module's scalar multiplication).
- Failing tests (1, one file):
    - `tests/groups/test_restricted_actions.sage::test_reflection_in_the_trivial_line_is_plus_one_on_standard_and_minus_one_on_invariants` — `TypeError: unsupported operand parent(s) for *: 'Fraction Field of Integer Ring' and 'Module over Group algebra of Symmetric group S_3 over Fraction Field of Integer Ring on Free module on {[0], [1],…`
- Introduced by: not bisected: the failure is reached through C03 and C04 at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.
- Repair: open; the scalar action on module elements over a group algebra; one test.

### C19 — A quotient of two cardinals is refused

`group.cardinality() / alternating.cardinality()` raises `TypeError: unsupported operand type(s) for /: 'Cardinalities.parent_class' and 'Cardinalities.parent_class'`, so the index of a subgroup cannot be written as the quotient of two orders.

- Defective call: src/sage_extensions/categories/sets/cardinals.py, whose `Cardinalities` element has `__add__` (:717) and no `__truediv__`.
- Failing tests (1, one file):
    - `tests/groups/test_predicate_subgroups_archive.sage::test_even_permutations_of_s3_form_the_normal_subgroup_of_order_three` — `TypeError: unsupported operand type(s) for /: 'Cardinalities.parent_class' and 'Cardinalities.parent_class'`
- Introduced by: not bisected: the cardinal arithmetic is in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: open; cardinal division; one test. Whether `/` should exist on cardinals is a design question (the pole is at zero, and the index is a group-theoretic operation), not a test bug: the library bans `/` on modules for the same reason (#408's C44).

### C20 — The session's `matrix` takes one row family, not a ring and a row family

`matrix(ZZ, [[0,-1],[1,0]])`, Sage's own spelling for a matrix, raises `TypeError: matrix() takes 1 positional argument but 2 were given`; the session's `matrix` reads the coefficient ring from the entries only. And the one-argument form answers an engine matrix-space element, not the owned matrix-Mor its docstring states, which a preamble group then refuses.

- Defective call: src/sage_extensions/language_runtime.py:68 (`matrix`).
- Failing tests (1, one file):
    - `tests/groups/test_sl2z_serre_archive.sage::test_sl2z_is_generated_by_elements_of_orders_four_and_six_amalgamated_over_minus_one` — `TypeError: matrix() takes 1 positional argument but 2 were given`
- Introduced by: 14b9cc1 (2026-10-26, Zack Garza) 'Move the session namespace and the mathematics test suite from research'; blamed at :68.
- Repair: open; the session's `matrix`; one test. Measured candidate repair, NOT landed: accepting the ring-first form makes `matrix(ZZ, rows)` answer, but the object it answers is `Generic endomorphism of Free module ...` -- an engine matrix-space element -- and `Groups.SL(2, ZZ)(...)` then refuses it with `it is a Sage object, not an element of a preamble group`. The arity and that engine crossing are one defect of this constructor.

### C21 — The owned quadratic field has no `gen`

`QuadraticField(-1, 'i').gen()` raises `AttributeError: 'Owned_OwnedAlgebraParent_with_category' object has no attribute 'gen'`, so the generator of a number field cannot be named -- and no Galois action can be written on it.

- Defective call: the owned number-field parent (the object `QuadraticField(-1, 'i')` answers).
- Failing tests (1, one file):
    - `tests/groups/test_profinite_collection_ownership.sage::test_galois_group_of_gaussian_rationals_is_generated_by_complex_conjugation` — `AttributeError: 'Owned_OwnedAlgebraParent_with_category' object has no attribute 'gen'`
- Introduced by: not bisected: the failure is reached through the field construction at main's root commit, so a bisect of this signature reports the commit that unmasked it, not this defect.
- Repair: open; the generator of an owned number field; one test.

### C22 — Applying the identity endomorphism of a subobject set rebuilds the object

`action(identity)(subgroup)` on the stabilizer action of a subgroup set answers a *new* subgroup object rather than the subgroup, so `assert ... is subgroup` fails: the identity arrow of the classifying category does not act as the identity on the objects, and no equivariance can be stated.

- Defective call: `restricted_stabilizer_action` (src/sage_extensions/categories/group/predicate_subgroups.py:1297) and the stabilizer action at :1294.
- Failing tests (1, one file):
    - `tests/groups/test_predicate_kernel_and_stabilizer_subgroups_of_s4.sage::test_normalizer_retains_its_conjugation_action_functor` — `assert Subgroup of Symmetric group S_3 is Subgroup of Symmetric group S_3`
- Introduced by: not bisected: both are in the root commit c731175 (2026-10-26, Zack Garza); blamed at :1297.
- Repair: open; the stabilizer action on a subobject set; one test.

### C23 — A character is not a member of the set of irreducible characters

`group.trivial_character() in group.irreducible_characters()` is false, printing the trivial character as a member of a three-element set that contains a character of the same degree: the equality (or the hash) of two `Character` objects does not decide membership.

- Defective call: the membership test at tests/groups/test_groups_archive.sage:146 over the characters built by `irreducible_characters()` / `trivial_character()`.
- Failing tests (1, one file):
    - `tests/groups/test_groups_archive.sage::test_archived_finite_group_character_surface_is_live_on_the_owned_group` — `assert Character of degree 1 of Symmetric group S_3 in {Character of degree 1 of Symmetric group S_3, Character of degree 2 of Symmetric group S_3, Character of degree 1 of Symmetric group S_3}`
- Introduced by: not bisected: the character surface is in the root commit c731175 (2026-10-26, Zack Garza).
- Repair: open; equality and membership of finite-group characters; one test.

### C24 — The retained sweep is stored on the orbit object it describes

After an orbit search, the orbit object carries `_retained_transitions` in its `__dict__`, so state that belongs to the family's sweep is attached to a single orbit and answers a later question with a stale table; a caller that inspects the orbit sees an undocumented attribute.

- Defective call: src/sage_extensions/categories/group/g_sets.py:757 (the orbit's `__dict__` assignment).
- Failing tests (1, one file):
    - `tests/groups/test_the_orbit_schreier_family_reads_the_retained_sweep.sage::test_a_point_not_covered_by_the_retained_sweep_searches_as_before` — `+  where {'_point_set': {5}, '_permutation_representation': Generic morphism:\n  From: Cyclic group C_3 of order 3\n  To:   Symme...s.ParentMethods.act of {1, 5, (1 2 3), (1 3 2)} with Cyclic group C_…`
- Introduced by: 55592e9 (2026-11-07, D. Zack Garza) 'Read orbit generator permutations from the retained transition table'; blamed at :757.
- Repair: open; the retention of the orbit sweep; one test.

