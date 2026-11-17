# A cache entry answers for the object at its address, while that object is there

This note reports the conversion of the library's address-keyed cache
decorators to the form `#592` settled on: **membership is not an identity
question, applied where it operates** -- the registry's answer -- plus a **datum
key where the object really carries a name**.  The base tree is `a75373b`; the
population is the one `#592` counted and filed, and the count is stated at the
end by search.

## 1. The population, and the three forms the conversion uses

At `a75373b` the library holds **196** cache decorators that take an explicit
`key=`.  **100** of them key on addresses and constants only -- the key names no
object the entry would hold, so the answer belongs to an address and is wrong the
moment another object occupies it.  Those 100 are this unit, and **96** remain
that name an object.

The swap is not one decorator, because the three decorators being replaced keep
their answers for three different lengths of time, and a single registry would
have changed that:

| replaces | form | what an entry lives as long as |
| --- | --- | --- |
| `cached_function` | `_address_registry` | the function: the answer is held, the arguments are recorded weakly and the entry answers nothing once one of them is not the object at its address |
| `cached_method` | `_instance_address_registry` | the instance: the table of entries is the instance's own, as `cached_method`'s cache is |
| `weak_cached_function(cache=0)` | `_weak_address_registry` | the answer: it is recorded weakly, so an answer nothing else holds is computed again |

The second is not a convenience.  A module-level table keyed on `id(self)` for a
`cached_method` answers would keep every instance alive whose answer names it --
which is most of the sites here, since the answer is built *from* the instance
(`category_constructions.object` returns an object of `self`, `functors.core
.component` an arrow of `self`).  The per-instance table keeps exactly
`cached_method`'s contract, so the swap changes what the key means and not what
lives how long.  The third is the same point for the four construction
registries `#592` left holding their values weakly on the plane row's path.

All three keep, for every entry, a *recoverable reference* to the arguments the
answer was computed for, and answer only when each of those arguments is still
the object at its address; otherwise the function is computed again.  That is
`#592`'s third statement, and it is what makes the address safe as a lookup:
the address is still how a live object is found, but it is never the *name* of
an answer.

## 2. The 100 sites, and the choice at each

Two forms, chosen per site:

* **the principle** -- the address was a proxy for "this live object", the answer
  is a construction of it, and the object carries no name a key could compare.
  This is 95 of the 100.
* **a datum key** -- the old key already *normalized* an argument to a canonical
  object, or named the datum the answer is built on.  There the address was
  standing in for that object, and keying on the object preserves exactly the
  partition the old key had, where the registry's finer key would have split it.
  This is 5 of the 100, argued individually below.

The five datum keys:

* `algebras.py:906 _algebra_tensor_square_functor` -- the key was
  `id(_owned_ring(base_ring))`: the functor is the tensor square *over the owned
  ring*, and `_owned_ring` returns one parent per ring.  Keying on the raw
  argument would build a second functor for a second spelling of one ring, and
  the functor is a category parameter, read by identity downstream.
* `ring_foundation.py:4097 as_algebra_over` -- the same shape, `_own_ring`.
* `cat.py:191 functor_mor` -- the key was `(id(self.object(domain)),
  id(self.object(codomain)))`: the Mor is named by its endpoints' *images*, not
  by the categories it was asked about, so the datum is the pair of images.
* `relative_spec.py:179` and `:194` -- the key was `id(datum)` and dropped the
  engine and the construction data.  The spectrum is named by its datum, so the
  datum is the key; the engine is added, because it is part of the answer and was
  silently ignored before (two engines for one datum answered the first's
  spectrum).  `construction_data` remains outside the key, as it was.

Each of the other 95 is a principle site, and the table below names the addresses
its key used and the form it took.  The table's line numbers are the base tree's
`@`-line.

| site | function | the addresses its key used | form |
| --- | --- | --- | --- |
| `categories/abstract_categories/arrow_categories.py:108` | `_walking_arrow_functor` | `category, arrow` | principle — `_address_registry` |
| `categories/abstract_categories/arrow_categories.py:553` | `_object_on` | `functor` | principle — `_instance_address_registry` |
| `categories/abstract_categories/arrow_categories.py:992` | `_object_on` | `arrow` | principle — `_instance_address_registry` |
| `categories/abstract_categories/arrow_categories.py:1229` | `_object_on` | `arrow` | principle — `_instance_address_registry` |
| `categories/abstract_categories/arrow_categories.py:1750` | `as_slice_object` | `subobject` | principle — `_instance_address_registry` |
| `categories/abstract_categories/cat.py:1455` | `_functor_object` | `functor` | principle — `_address_registry` |
| `categories/abstract_categories/cat.py:191` | `functor_mor` | `self.object(domain), self.object(codomain)` | datum — the functor's objects |
| `categories/abstract_categories/cat.py:1663` | `evaluation` | `index` | principle — `_instance_address_registry` |
| `categories/abstract_categories/category_constructions.py:183` | `object` | `underlying_object` | principle — `_instance_address_registry` |
| `categories/abstract_categories/category_constructions.py:443` | `pair` | `first, second` | principle — `_instance_address_registry` |
| `categories/abstract_categories/functor_images.py:172` | `object` | `preimage` | principle — `_instance_address_registry` |
| `categories/abstract_categories/mor_categories.py:2119` | `_category_packet` | `category` | principle — `_address_registry` |
| `categories/abstract_categories/presheaves.py:1199` | `trivial_coverage` | `site_category` | principle — `_address_registry` |
| `categories/abstract_categories/presheaves.py:1007` | `family` | `target` | principle — `_instance_address_registry` |
| `categories/abstract_categories/presheaves.py:1099` | `family` | `target` | principle — `_instance_address_registry` |
| `categories/abstract_categories/presheaves.py:1610` | `comparison` | `covering_family` | principle — `_instance_address_registry` |
| `categories/abstract_categories/presheaves.py:1769` | `_object_on` | `functor, descent_data` | principle — `_instance_address_registry` |
| `categories/abstract_categories/products.py:741` | `_parallel_pair_diagram` | `left, right, target_category` | principle — `_address_registry` |
| `categories/abstract_categories/products.py:1001` | `_parallel_family_diagram` | `morphisms, target_category` | principle — `_address_registry` |
| `categories/abstract_categories/products.py:1759` | `construction` | `diagram` | principle — `_instance_address_registry` |
| `categories/abstract_categories/products.py:1866` | `construction` | `diagram` | principle — `_instance_address_registry` |
| `categories/algebras/algebras.py:906` | `_algebra_tensor_square_functor` | `_owned_ring(base_ring)` | datum — the owned ring |
| `categories/algebras/algebras.py:5780` | `_algebra_structure_view` | `ring, structure_map` | principle — `_address_registry` |
| `categories/algebras/cohomology_algebras.py:216` | `_cohomology_algebra_from_dga` | `dga` | principle — `_address_registry` |
| `categories/algebras/de_rham_algebras.py:241` | `_de_rham_algebra_from_source` | `algebra` | principle — `_address_registry` |
| `categories/algebras/derivations.py:760` | `_derivations` | `algebra, target_module` | principle — `_address_registry` |
| `categories/algebras/free_algebras.py:629` | `_symmetric_algebra_of_free_module` | `generating` | principle — `_address_registry` |
| `categories/algebras/kahler_differentials.py:309` | `_cached_kahler_differentials` | `algebra` | principle — `_address_registry` |
| `categories/algebras/restricted_graded_algebras.py:207` | `_restrict_graded_algebra_scalars` | `algebra, ring_map` | principle — `_address_registry` |
| `categories/coloured_vector_families.py:1050` | `_realization` | `lattice, family` | principle — `_weak_address_registry` |
| `categories/divisors/cartier_divisor_groups.py:361` | `_total_quotient_sheaf` | `scheme` | principle — `_address_registry` |
| `categories/divisors/cartier_divisor_groups.py:376` | `_unit_sheaf` | `ring_sheaf` | principle — `_address_registry` |
| `categories/divisors/cartier_divisor_groups.py:391` | `_regular_unit_sheaf` | `scheme` | principle — `_address_registry` |
| `categories/divisors/cartier_divisor_groups.py:406` | `_cartier_divisor_quotient_sheaf` | `scheme` | principle — `_address_registry` |
| `categories/divisors/cartier_divisor_groups.py:970` | `_cartier_section_classes` | `quotient_sheaf` | principle — `_address_registry` |
| `categories/divisors/invertible_sheaves.py:314` | `_whole_to_basis` | `open_object` | principle — `_instance_address_registry` |
| `categories/divisors/linearizations.py:654` | `_c2_diagonal_product_projective_action` | `projective_product, OwnedGroups().C(2) if group is None else group` | principle — `_address_registry` |
| `categories/divisors/linearizations.py:747` | `_projective_line_coordinate_swap_action` | `projective_line, OwnedGroups().C(2) if group is None else group` | principle — `_address_registry` |
| `categories/divisors/picard_groups.py:406` | `_invertible_sheaf_class_group` | `scheme` | principle — `_address_registry` |
| `categories/functions/convolution.py:37` | `_symbolic_convolution` | `left, right` | principle — `_address_registry` |
| `categories/functions/convolution.py:134` | `_convolution_pairing` | `left, right` | principle — `_address_registry` |
| `categories/functors/algebra_scalar_change.py:429` | `_algebra_base_change_adjunction` | `ring_map` | principle — `_address_registry` |
| `categories/functors/commutator_lie_algebras.py:64` | `_commutator_lie_algebra` | `algebra` | principle — `_address_registry` |
| `categories/functors/core.py:690` | `component` | `obj` | principle — `_instance_address_registry` |
| `categories/functors/de_rham.py:137` | `_degree_zero_data` | `dga` | principle — `_instance_address_registry` |
| `categories/functors/group_actions.py:184` | `_group_algebra_augmentation_ring_map` | `algebra` | principle — `_address_registry` |
| `categories/functors/scalar_change.py:474` | `_base_change_adjunction` | `ring_map` | principle — `_address_registry` |
| `categories/functors/scalar_change.py:479` | `_restriction_coextension_adjunction` | `ring_map` | principle — `_address_registry` |
| `categories/functors/scalar_change.py:142` | `composite_ring_map` | `second_ring_map` | principle — `_instance_address_registry` |
| `categories/group/g_objects.py:1122` | `_affine_invariant_action` | `acted` | principle — `_instance_address_registry` |
| `categories/group/g_objects.py:1195` | `affine_quotient` | `acted` | principle — `_instance_address_registry` |
| `categories/group/g_objects.py:1204` | `quotient_morphism` | `acted` | principle — `_instance_address_registry` |
| `categories/group/magmas.py:988` | `_unit_group` | `monoid` | principle — `_address_registry` |
| `categories/group/profinite/absolute_galois_group.py:907` | `_canonical_absolute_galois_group` | `field` | principle — `_address_registry` |
| `categories/lattice_morphisms.py:6098` | `_lattice_mor` | `domain, codomain` | principle — `_weak_address_registry` |
| `categories/lattice_morphisms.py:6106` | `_lattice_embedding_mor` | `domain, codomain` | principle — `_weak_address_registry` |
| `categories/lattice_morphisms.py:6114` | `_lattice_isometry_mor` | `domain, codomain` | principle — `_weak_address_registry` |
| `categories/lattice_morphisms.py:4334` | `_family_stabilizer` | `family` | principle — `_instance_address_registry` |
| `categories/lattices.py:2502` | `_object_on` | `oriented` | principle — `_instance_address_registry` |
| `categories/lattices.py:4584` | `base_change` | `ring_map` | principle — `_instance_address_registry` |
| `categories/modules/connections.py:721` | `_connections` | `module` | principle — `_address_registry` |
| `categories/modules/fibered_modules.py:261` | `base_change_adjunction` | `scalar_map` | principle — `_instance_address_registry` |
| `categories/modules/framed/formed/form_modules.py:1588` | `_formed_module_base_change` | `source, ring_map` | principle — `_address_registry` |
| `categories/modules/framed/framed_free_modules.py:1746` | `_owned_free_module_on` | `ring, module_generating_set` | principle — `_address_registry` |
| `categories/modules/framed/framed_free_modules.py:824` | `base_change` | `ring_map, _extra_construction_data` | principle — `_instance_address_registry` |
| `categories/modules/framed/framed_free_modules.py:1076` | `base_change` | `ring_map, _extra_construction_data` | principle — `_instance_address_registry` |
| `categories/modules/general_modules.py:620` | `_function_module` | `module, domain` | principle — `_address_registry` |
| `categories/modules/graded_direct_sums.py:253` | `_direct_sum_framing_source` | `ring, pieces` | principle — `_address_registry` |
| `categories/modules/graded_modules.py:78` | `_parity_key` | `parity` | principle — `_address_registry` |
| `categories/modules/internal_mor.py:54` | `_internal_mor_model_data_from_endpoints` | `source, target` | principle — `_address_registry` |
| `categories/modules/powers.py:881` | `_divided_square` | `module` | principle — `_address_registry` |
| `categories/modules/pure/modules.py:550` | `scalar_extension` | `ring_map` | principle — `_instance_address_registry` |
| `categories/real_affine_spaces.py:29` | `_canonically_based_affine_space` | `vector_space` | principle — `_address_registry` |
| `categories/rings/commutative_algebra.py:5585` | `_prime_localization` | `source, prime_ideal` | principle — `_address_registry` |
| `categories/rings/ring_foundation.py:5429` | `Mor` | `domain, codomain` | principle — `_instance_address_registry` |
| `categories/rings/ring_foundation.py:2416` | `principal_localization_comparison` | `source_ring` | principle — `_instance_address_registry` |
| `categories/rings/ring_foundation.py:4097` | `as_algebra_over` | `_own_ring(base_ring)` | datum — the owned ring |
| `categories/schemes/geometric_cohomology.py:226` | `_projective_space_line_bundle_derived_global_sections` | `sheaf` | principle — `_address_registry` |
| `categories/schemes/geometric_cohomology.py:265` | `_projective_space_de_rham_hypercohomology` | `space` | principle — `_address_registry` |
| `categories/schemes/geometric_cohomology.py:1255` | `_complex_realization` | `scheme, scalar_embedding` | principle — `_address_registry` |
| `categories/schemes/gluing.py:1321` | `pullback` | `morphism` | principle — `_instance_address_registry` |
| `categories/schemes/gluing.py:1742` | `global_section_pullback` | `descent` | principle — `_instance_address_registry` |
| `categories/schemes/gluing.py:7378` | `object` | `sheaf` | principle — `_instance_address_registry` |
| `categories/schemes/relative_proj.py:2783` | `_finite_atlas_projectivization` | `sheaf` | principle — `_address_registry` |
| `categories/schemes/relative_proj.py:2825` | `_affine_projectivization` | `sheaf` | principle — `_address_registry` |
| `categories/schemes/relative_proj.py:1302` | `projectivization_base_change` | `ring_map` | principle — `_instance_address_registry` |
| `categories/schemes/relative_proj.py:2522` | `projectivization_base_change` | `ring_map` | principle — `_instance_address_registry` |
| `categories/schemes/relative_proj.py:638` | `projectivization_base_change` | `ring_map` | principle — `_instance_address_registry` |
| `categories/schemes/relative_spec.py:179` | `_relative_spectrum` | `datum` | datum — the datum and its engine |
| `categories/schemes/relative_spec.py:194` | `_finite_atlas_relative_spectrum` | `datum` | datum — the datum and its engine |
| `categories/schemes/ringed_spaces.py:821` | `_affine_de_rham_complex` | `scheme` | principle — `_address_registry` |
| `categories/schemes/ringed_spaces.py:1174` | `zariski_coverage` | `scheme` | principle — `_address_registry` |
| `categories/schemes/ringed_spaces.py:1571` | `distinguished_affine_coverage` | `scheme` | principle — `_address_registry` |
| `categories/schemes/ringed_spaces.py:606` | `module_descent_datum` | `cover` | principle — `_instance_address_registry` |
| `categories/schemes/ringed_spaces.py:2174` | `associated_sheaf` | `module` | principle — `_instance_address_registry` |
| `categories/schemes/schemes.py:2443` | `_projective_section_restriction` | `scheme, ring` | principle — `_address_registry` |
| `categories/schemes/schemes.py:3124` | `_affine_spectrum_over` | `algebra, base` | principle — `_address_registry` |
| `categories/schemes/schemes.py:2118` | `module_pullback` | `sheaf` | principle — `_instance_address_registry` |
| `categories/sets/set_categories.py:4809` | `_cartesian_product_of` | `family` | principle — `_address_registry` |
| `categories/sets/set_categories.py:6572` | `_coproduct_of_indexed_family` | `family` | principle — `_address_registry` |

## 3. The comparison

`#592`'s own comparison, not the spans: on \(U \oplus U(2) \oplus \langle -2
\rangle\) the rows keep **3 line cusps, 2 plane cusps and 4 incidence
certificates**, each certificate's line lying in its plane with both transporters
reaching their cusps
(`tests/lattices/test_a_cusp_names_its_plane_by_span.sage`, run on both trees).
The row's representative *choice* moves between runs, so a span comparison across
trees proves nothing and the orbit count and the relation are what compare.

The suite: `tests/categories tests/modules tests/objects tests/sets`, the same
command on both trees, gives **identical FAILED and ERROR id sets** -- 510 ids,
211 failed, 519 passed, 299 errors on each.  Attaching the evidence: the two
sorted id lists are byte-identical.

## 4. The row

`Otilde(T_Co)`, 200 draws from
`OrthogonalCharacterQuotient._iter_splitting_isometries_in_im_rho` of the plane's
certified parabolic, one transport, one span key, one `register_isotropic_lift`
and one cusp wrapper a draw; the row keeps the cusp named by the plane's span and
drops the plane (`PROBE_SHAPE=cusps`).  Before is the base tree `a75373b`, after
is this tree.

| run | tree | planes | 1 -> 10 | 10 -> 100 | 100 -> 200 | 200 -> 400 | rss at the end | planes alive beside the source | lifts retained | wall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `row-base` | base | 200 | 0.4 | 0.3 | 6.0 | -- | 1130.0 MiB | 0 | 200 | 197.7 s |
| `row-new` | converted | 200 | 2.7 | 5.3 | 9.8 | -- | 1399.8 MiB | 0 | 200 | 216.2 s |
| `row2-base` | base | 400 | 3.6 | 12.0 | 14.3 | 15.8 | 1317.0 MiB | 0 | 400 | 205.1 s |
| `row2-new` | converted | 400 | 0.4 | 0.2 | 3.3 | 10.9 | 1264.2 MiB | 0 | 400 | 198.5 s |

(KiB a plane; the first two runs are `PROBE_CHECKPOINTS=10,100,200`, the second two
add 400.)

**What this shows and what it does not.**  The row releases its representatives on
both trees: **0** planes of the row are alive beside the source at 200 planes and
at 400, and the drop test is **0 of 20** on each.  The per-plane band is *not* a
stable quantity between runs: the base tree gives 6.0 KiB a plane over 100 -> 200
in one run and 14.3 in the next, and `#592` recorded 1.2 KiB for the same probe on
the same tree.  So the comparison that matters is between runs of the same shape:
at 400 planes the converted tree is the leaner of the two in every band (10.9
against 15.8 KiB a plane over 200 -> 400), and at 200 planes it is the dearer
(9.8 against 6.0) -- the two orders disagree, which is what a 5x run-to-run spread
does to a two-point comparison.

Extrapolating the last band to 189 720 planes gives **2.0 GiB** on the converted
tree (10.9 KiB a plane) and **2.9 GiB** on the base (15.8 KiB), both under the
4 GiB a four-GiB runner can take, and neither near `#592`'s 0.22 GiB, which was a
leaner draw of representatives than either of today's runs.  The band also grows
with the plane count on both trees, because the lift registry holds one lift a
plane and the probe reports them retained (`lifts_retained` = the plane count):
that growth is the split's, not the cusps', and it is the same on both trees.

## 5. The count, by search

Two searches, both run on the converted tree and both in `.tmp/issue593/`:

**The population this issue names.**  `probe-address-keys.py` (the probe `#592`
counted with, `.tmp/subobject-identity/`) walks every function under `src/` and
classifies each cache decorator's `key=`:

```
[probe] cache decorators under src/: 101
[probe] of them with a key of addresses and constants only: 0
[probe] of them with a key that names an object: 100
```

The total is 101 rather than 196 because 95 of the converted sites no longer take
a `key=` at all, and the five datum keys do: the 100 address-only sites are
**zero**.  The 100 that name an object are the 95 of the base tree plus the five
datum keys.

**The wider question, an address inside a key that also names something.**
`mixed.py` asks whether a key that *mentions* an address holds the object whose
address it mentions, which is what makes the address safe: 67 keys mention an
address, **55 hold every object they address** (`(id(x), x)` and its kin: the
entry keeps `x`, so `id(x)` cannot be reused while the entry lives), and **12 do
not**:

| site | key | what it addresses |
| --- | --- | --- |
| `_lattice.py:513` | `_lattice_on_gram` | the category, the module and the axiom classes, beside `gram`, `names`, `root_system_type_name` compared by value |
| `_lattice.py:1363` | `_orthogonal_sum_on_family` | the ring, the index set and each summand |
| `algebras.py:5567` | `_owned_algebra_view` | `constructing_category`, `labels`, every category, every construction datum, the ring placement |
| `derivations.py:1310` | `_graded_derivations` | the algebra and the target module, beside `int(shift)` |
| `free_algebras.py:371` | `_native_free_algebra` | the generating module and the constructing category, beside `flavor` |
| `free_algebras.py:1300` | `_finitely_presented_algebra_from_data` | the presentation ring, the relations, the extra categories, the construction data |
| `groups.py:1831` | `_own_group` | the group, free basis, presentation source, symmetric points, Coxeter matrix, linear data |
| `form_modules.py:2780`, `:3798` | `reframing_isometry` | **each generator** of the sequence, not the sequence |
| `pure/modules.py:5912` | `_restricted_scalars_view` | the module, the ring map and every datum |
| `number_fields.py:130`, `:164` | `_number_field_of`, `_number_field_extension` | `element_parent(polynomial)`, a parent derived from a polynomial the key holds by value |

These twelve are **not** converted, and not approximately.  The address-only swap
is not available at any of them, for one of three reasons:

1. **The key compares a value by value.**  Seven of the twelve carry a `flavor`, a
   `degree`, a `gram`, a `names` or a construction datum beside the address.
   `_address_registry` keys *every* argument by its address, so a degree or a
   flavor built at the call site would miss every time -- the cache would stop
   caching, and an object that is equal but not identical would be answered from
   the entry at its address, which is the defect and not the repair.
2. **The address is of an element inside a sequence.**  `reframing_isometry` keys
   the *generators*, and the registry keys the sequence object: a different key,
   not a repair of this one.
3. **The addressed object is derived.**  `element_parent(polynomial)` is a parent
   computed from a value the key already holds; naming the parent would compare
   parents by `==`.

The alternative at all twelve is to replace `id(x)` by `x`, which makes the key
compare `x` by `==`.  `#592` measured what that costs: two subobjects of one span
are two objects with two Mors, and a key that compares them by `==` answers the
question about the second with the first's.  Deciding, per object, that its
equality *is* its identity is a datum decision -- the form this issue uses for
five sites and argues above -- and it needs its own measurement for each of the
twelve.  That is the next population, and its number is twelve.

## 6. What was run, and what was not

All in the pinned image through `.scratch/593/launch.sh` and `run-tests.sh`
(`#592`'s launchers, retargeted), `PYTHONHASHSEED=0`.  The base tree is a clone of
`a75373b` at `.scratch/593base2` -- a clone rather than a worktree because the
stage recorder runs `git rev-parse HEAD` inside the image, and a worktree's
`.git` file points outside it.

| what | result |
| --- | --- |
| the comparison on \(U \oplus U(2) \oplus \langle -2\rangle\), both trees | 3 line cusps, 2 plane cusps, 4 certificates, identical edges; 3 passed in 15.5 s (new) and 13.2 s (base) |
| `tests/categories tests/modules tests/objects tests/sets`, both trees | identical FAILED/ERROR id sets: 510 ids, 211 failed, 519 passed, 299 errors |
| the row at 200 planes, both trees | section 4 |
| the drop test, both trees | 0 of 20 planes alive on each |
| the count | section 5 |

Not run: the rest of `tests/lattices`, which does not return inside a budget one
command may take; the whole suite, for the same reason; and the `ast-grep` gates,
which are not installed on this host.

## 7. On a test for the population

The defect is an answer computed for an object that has been collected; reaching
it needs the subject's address to be occupied by the next object.  At many of the
100 the answer *names* its subject -- the constructed object keeps the arrow, the
module, the scheme it was built from -- so the subject cannot be collected while
the answer is retained, and the stale answer is latent: it becomes reachable the
moment the value stops naming its subject, which is exactly what the plane row
did in `#592`.  At the rest the address would have to be reused on purpose, and
`gc` plus an allocation of the same size class does not do that deterministically
(in the experiment recorded in `.tmp/issue593/test-decorators.py`, the freed
address was taken by the *second* allocation).  A test that depends on that is a
coin-flip, so none is added here; the red test for this defect is `#592`'s
(`test_a_dropped_plane_is_collected.sage`), which passes on both trees, and the
conversion is checked by the comparison and the id sets of section 3.
