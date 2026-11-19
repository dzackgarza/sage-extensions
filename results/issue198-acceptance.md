# #198: the eight review items on `4f7438e`

Line numbers are of the head this note is pushed on.

**Verdict.** Seven of the eight review items are met.  The eighth --- sections as
derivations of the *full* `C^oo(M)` --- is met on a manifold presented by one chart, and its
general case is **refuted as unreachable in this representation**: the identification is
Lee's Prop. 8.15 (2nd ed., Ch. 8), its locality step uses the bump function of Lemma 2.26,
and no function stated by chart expressions is identically zero off a proper open set.  No
further lemma can advance it; what remains is a decision about the clause, not a proof.

| # | Item | State | Code | Deciding test |
|---|---|---|---|---|
| 1 | Tangent bundle, owned | met | `manifolds.py:2925` `tangent_bundle`; `vector_bundles.py` `SmoothVectorBundles` | `test_the_tangent_bundle_of_the_circle_is_trivial.sage` |
| 2 | Sections as derivations of `C^oo(M)` | **met on a one-chart manifold; the general case REFUTED as unreachable here** | action `vector_bundles.py` `__call__`; reading `vector_bundles.py:1232` `from_derivation` | `test_a_derivation_of_a_one_chart_manifold_is_a_section.sage` |
| 3 | Restriction | met | `vector_bundles.py:1187` `restrict` | `test_a_section_stated_on_a_cover_restricts_although_another_chart_exists.sage` |
| 4 | Pullback along a general map | met | `vector_bundles.py:738` `pullback_along`, `_pullback_family_agrees` | `test_a_pullback_agreement_reads_every_component_of_the_bundle.sage` |
| 5 | Rank-`r` trivialization | met but for the algebra half | `vector_bundles.py:1365` `trivialized_by`, `:1499` `forward` | `test_a_frame_of_rank_two_exhibits_its_module_isomorphism.sage` |
| 6 | Coverage | met | `manifolds.py:813` `_chart_family_covers` and the certificates | `test_a_chart_without_cuts_covers_only_its_own_domain.sage` |
| 7 | Chain rule / composed transitions | met | `manifolds.py:293` `then`, `_composed_ambient_transition` | `test_a_submanifold_relates_two_charts_through_two_others.sage` |
| 8 | Coercion at its owner | met | `owned_category.py:778` `_bases_with_sage_sets_parent` | `test_the_exact_real_field_coerces_from_the_integers.sage` |

## Item 2, stated exactly

**Met** for a manifold presented by one chart: `from_derivation` reads a section off a
derivation on the coordinates and round-trips the Euler field and `d/dx` (measured again on
this head: `derivation round trip: True`, `action: 24 = 24` for `E(xy)` at `(3,4)`).

**Not met** in general, and the reason is proved rather than deferred: Lee's Prop. 8.15
(2nd ed., Ch. 8) is local through a bump function (Lemma 2.26), and this representation
carries none -- a chart expression vanishing on an open set of a chart vanishes identically
there, so no function stated by chart expressions is identically zero off a proper open set.
The measurements are in `results/issue198-locality-of-derivations-and-the-support-the-tree-lacks.md`.

So item 2 and the algebra half of item 5 stand or fall together, and both need the issue's
clause amended to say that `C^oo(M)` here is the algebra of functions carried by chart
expressions -- or a construction of Lemma 2.26 added to the algebra, which these expressions
cannot supply.
