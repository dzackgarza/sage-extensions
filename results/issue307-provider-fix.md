# #307: the rational hyperbolic triangle's acute-angle predicate — provider repair

For the orchestrator to post on this repository's issue #307 and, as the dependency edge, on
`lattice-database` issue #18. The accepting result is the database's own public call,
`WeightedGraph.model_validate(<the card>).properties()`, on the affected form and
scalar-restriction laws; nothing here needs a further measurement unit.

## The reported symptom

`lattice-database#18`, provider `7494af73`:

```
File "/repo/src/latticedb/graphs.py", line 251, in properties
    hyperbolic = self._presents_mirrors() and invariants.is_acute_angled_hyperbolic_polytope_gram()
File "/repos/sage-extensions/src/sage_extensions/categories/vinberg_invariants.py", line 343,
    if any(gram[i, i] <= 0 for i in positions):
TypeError: '<=' not supported between instances of 'OwnedJoinCategory.element_class'
           and 'OwnedJoinCategory.element_class'
```

Card: `graphs/hyperbolic-triangle-2-3-infinity.md` — three walls of norm 1, bonds of Gram
`-1/2` (order 3) and `-1` (order infinity), Gram `[[1, -1/2, 0], [-1/2, 1, -1], [0, -1, 1]]`.

## The three defects, in the order they surface

1. **A rational's order.** `QQ`'s element class is `OwnedJoinCategory.element_class`, whose
   MRO has no `_OwnedRingElement`, so it inherited Sage's `Element.__le__`; `ZZ` worked only
   because its element class derives from `_OwnedRingElement`. Both parents are in
   `OwnedOrderedRings()`, so the comparisons belong to that category, not to one
   realization's element base. Moved `__lt__/__le__/__gt__/__ge__` and
   `_ordered_comparison` into `OwnedOrderedRings.ElementMethods`
   (`categories/rings/ring_foundation.py`), still decided by the parent's retained engine.
   MRO evidence: `.tmp/issue307_mro.log`.

2. **Which value object a pairing reads.** `is_acute_angled_hyperbolic_polytope_gram` builds
   `FormModules(ring)(module.bilinear_hom_space(ring)(gram))` with `ring = QQ` and then reads
   `signature_pair()`, which needs a ring-valued form. `bilinear_hom_space` re-read *every*
   owned ring through its regular module, so the codomain became `Free module on {[0]} over
   QQ` and `gram_tensor()` refused it —
   `TypeError: … needs values in a ring`. `_regular_module_reading` now re-reads only the
   **restriction** of a ring, which is what #293 reported; a bare ring stays the value ring.

3. **One module structure per semilinear arrow.** With (2) in place the same construction
   reached `SemilinearModuleMorphism`, whose endpoints were validated against
   `domain.base_ring()` — which for `QQ` is `ZZ` — so it answered
   `a semilinear map into Fraction Field … lies over a ring map into one of ['Integer Ring']`.
   The arrow now requires its endpoints to be modules over the rings its scalar map names
   (`Modules(scalar_map.domain())`, `Modules(scalar_map.codomain())`), and the restriction,
   the defining linear morphism and the restricted codomain all use that one structure
   (`categories/modules/fibered_modules.py`).

4. **A ring's own scalar action.** (2) leaves `QQ` itself as the codomain of a `QQ`-valued
   form, and `Modules`' generic `scalar_multiple` resolves the acting ring through
   `base_ring()` — `ZZ` for `QQ` — so evaluating that form at `(1/2)e_0` raised
   `TypeError: no conversion of this rational to integer`. A ring is the regular left module
   over itself and its own action is multiplication; `OwnedRings.ParentMethods`
   now supplies it, and the generic base-ring action is used unchanged whenever the base ring
   can read the scalar, so no existing reading moves (`categories/rings/ring_foundation.py`).
   Trade avoided: at the base commit the pairing was `QQ`-linear but had no Gram; with only
   (2) it had a Gram but was not `QQ`-linear. Both now hold.

## Evidence

Red, at the pushed base `7494af73` (`git archive` export, same runtime and wrapper), from the
database's own test that asserts the card's classes:

```
tests/test_geometric.py::test_graph_cards_derive_distinct_datum_from_shared_coxeter_order
E   TypeError: '<=' not supported between instances of 'OwnedJoinCategory.element_class'
               and 'OwnedJoinCategory.element_class'
1 failed, 4 deselected in 1.85s
```

and the same at this repository's red commit `abb2b10` (`.tmp/issue307_red.log`):

```
collected 2 items
tests/lattices/test_the_rational_hyperbolic_triangle_gram.sage FF        [100%]
FAILED ...::test_the_owned_rationals_are_ordered
FAILED ...::test_the_rational_triangle_is_an_acute_angled_hyperbolic_polytope
============================== 2 failed in 0.81s ===============================
```

Green, the affected set with the declared gate (addopts intact, nothing blanked):

```
tests/lattices/test_the_rational_hyperbolic_triangle_gram.sage
tests/modules/test_scalar_change_between_z_and_q.sage
tests/modules/test_restriction_of_scalars_on_morphisms.sage
tests/modules/test_restricted_scalars_action.sage
============================== 15 passed in 1.73s ==============================
```

Green, the database's own public call (this repository's working tree bound at
`/repos/sage-extensions`, database at `/lattice-database`):

```
tests/test_geometric.py::test_graph_cards_derive_distinct_datum_from_shared_coxeter_order
1 passed, 4 deselected in 2.14s
tests/test_rational_forms.py
3 passed in 1.22s
```

The passing test asserts, on the published cards, `a2-su21-satake` →
`("Coxeter", "Dynkin", "simply laced", "Satake")` and `hyperbolic-triangle-2-3-infinity` →
`("Coxeter", "hyperbolic Coxeter polytope")`.

Not claimed: `tests/test_geometric.py` has two other failures,
`test_k3_hodge_diamond_and_lattice_link_are_published` and
`test_symmetric_spaces_and_analytic_variety_are_published`, both
`KeyError: '0011'` / `KeyError: '0015'` inside `site.build` (`latticedb/site.py:524`). They
fail identically against the base provider `7494af73`, so they are database data, not this
repository's, and are not part of this report.

## The wider affected set, diffed against the base

`tests/modules` is shared module foundation, which is exactly what defects 3 and 4 touch, so
it was run as a set and its FAILED ids were diffed against a clean `git archive` export of
`7494af73` (never absolute counts):

```
current tree : 99 failed, 184 passed in 55.80s   (all 79 files, 283 tests)
base 7494af73: 99 failed,  30 passed in 18.51s   (the 37 failing files only)
diff of the two FAILED-id sets: empty  →  0 new failures
```

The base is narrower on purpose — only the files that fail here need re-running to prove a
failure is pre-existing — so its pass count is not comparable; the id sets are.

Six lattice modules were run with the gate on:

```
tests/lattices/test_vinberg_invariants.sage
tests/lattices/test_vinberg_number_fields.sage
tests/lattices/test_hyperbolic_root_lengths_and_vinberg.sage
tests/lattices/test_norm_two_root_types.sage
tests/lattices/test_coxeter.sage
tests/lattices/test_reflective_root_system_components_of_definite_lattices.sage
======================== 3 failed, 29 passed in 35.03s ========================
```

The three FAILED ids are identical at `7494af73`, on unrelated pre-existing defects
(`KeyError: Real Algebraic Field`, a real-embedding ring map, `unable to find a common ring`)
— not part of this repair. The same three files at the base also failed

```
test_vinberg_invariants.sage::test_the_invariant_matrix_with_t_equal_one_everywhere_is_the_affine_A2_triangle
E   TypeError: unsupported operand parent(s) for <: 'Fraction Field of Integer Ring' and '<class 'int'>'
    vinberg_invariants.py:493: if ratio < 4 and ratio not in (0, 1, 2, 3)
```

which is defect 1 at a second site (`ratio < 4` on a rational), and that test now passes: one
base failure fixed, none added.

Gates: the new test file is lint-clean under the repository's own `test_lint`. Two
selection-size costs are pre-existing and recorded under #306 with their exact comparison,
`results/issue-proposal-reflective-root-enumeration-cost.md`: the `tests/modules` collection
(15.80 s here against 15.85 s at base, ceiling 6 s) and
`test_norm_two_root_types.sage::test_two_copies_of_e8_and_a_norm_minus_two_line_give_e8_e8_a1`
(21.95 s here against 20.90 s at base, ceiling 20 s). Neither gate was changed, warmed,
reordered or suppressed; the directory-sized selection was run with the plugins' own
documented one-off flags, which still report every call over the call ceiling.

## The repository's check contract for this repair, and what it returned

There is no client-side Git hook in this checkout to invoke: `git rev-parse --git-dir` is
`.git`, there is no `.git/hooks/` directory, `core.hooksPath` is unset, and there is no
`.pre-commit-config.yaml`; CI carries `development.yml`, `ambient.yml` and `readme.yml`. The
gates this repository declares for a change are the `just` recipes, so the checks below were
run through them on this tree, in this order, after the merge:

```
just test-push        Push syntax: 86 file(s) checked; no errors.        exit 0
just test-commit      Staged syntax: <the committed files>; no errors.   exit 0
just test-lint <the two test files this repair touches>
                      2 files, 0 findings                               exit 0
just test <the four-file affected set>              15 passed in 2.29s   exit 0
just test <the three vinberg modules>
                      3 failed, 11 passed; the 3 ids are the pre-existing ones below
just test-lint (whole tree)
                      770 files, 1261 findings (TL01..TL13)             exit 1
```

Two of those are failures whose owner is not this repair, and neither is used as acceptance:

- **Tree-wide `test-lint`.** 1261 findings across 770 files, none in a file this repair
  touches (the scoped run is 0 findings). It is registered pre-existing debt of the same kind
  `TRAPS.md` already records per file ("registered, not repaired"), it is not on the
  publication path (`justfile`: *No full-tree scan on the publication path*), and no issue id
  in this tree owns it. It is not repaired here and it is not evidence about #307 either way.
- **The two cost ceilings**, both measured identical at the base and recorded under #306:
  `tests/modules` collection 15.80 s against 15.85 s (ceiling 6 s), and
  `test_two_copies_of_e8_and_a_norm_minus_two_line_give_e8_e8_a1` 21.95 s against 20.90 s
  (ceiling 20 s).

What the acceptance rests on is the passing public behaviour, not a failure count: the
database's own `properties()` on the published card answers
`("Coxeter", "hyperbolic Coxeter polytope")`, the same call raises the reported `TypeError` on
the base provider, and the four form/scalar-restriction laws pass with the declared gate. The
99 pre-existing `tests/modules` failures are recorded only to show this repair added none —
their ids are identical at the base, which is a statement about scope, not about them being
acceptable.
