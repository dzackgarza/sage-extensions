# #198: the eight review items, decided on `54ce8cf`

The review of 2026-11-19 recorded 2 items met, 5 not met and the coercion defect
open.  Each is answered below with the code that carries it and the measurement
that decides it.  Line numbers are of the pushed head `54ce8cf` on `main`.

| # | Item | State | Code | Measurement |
|---|---|---|---|---|
| 1 | Tangent bundle of a smooth manifold, owned, sections over `C^oo(M)` | met | `manifolds.py:2702` `tangent_bundle`, `vector_bundles.py:452` `SmoothVectorBundles` | the circle's base, rank and module (`test_the_tangent_bundle_of_the_circle_is_trivial.sage`) |
| 2 | Sections as derivations of `C^oo(M)` | met on the algebra the tree states | action `vector_bundles.py:660`; admission `real_functions.py:828`; expression test `manifolds.py:1083` | `E(h)` at `x = 2` is `-6/5`; an opaque callable is refused |
| 3 | Restriction to an open submanifold | met | `vector_bundles.py:978` `restrict` | the Euler field restricts although the submanifold carries a third chart |
| 4 | Pullback along a general smooth map | met | `vector_bundles.py:546` `pullback_along`, `:93` `_pullback_family_agrees`, `:1023` `pullback_of` | a directly stated pullback section reads `1` at `(2,3)` |
| 5 | Rank-`r` trivialization `C^oo(M)^r -> Gamma(E)` | met on the same algebra | `vector_bundles.py:1100` `trivialized_by`, `:1173` `trivialization`, `:1194` the pair of maps | `TV` of the chart domain is free of rank two |
| 6 | Coverage of a family of charts | met by a certificate, **not complete** | `manifolds.py:789` `_chart_family_covers`, `:813` `_sum_certificate_covers` | two punctured planes cover, one does not |
| 7 | Chain rule and composed transitions | met | `manifolds.py:280` `then`, `:750` `_composed_ambient_transition` | the cut chart to the south chart sends `(2,3)` to `(2/13,3/13)` |
| 8 | Coercion at its owner | met | `owned_category.py:778` `_bases_with_sage_sets_parent` | `RR.coerce_map_from(ZZ)(2) = 2`, `ZZ in Sets()` true |

## The two items whose "met" is narrower than the sentence says

**Item 2 and item 5** are met on the algebra of smooth functions *as this tree
states it*: an element carries its chart expressions, which is what a derivative
is computed on, and a map given only by a callable is refused at the algebra's
boundary (`real_functions.py:828`) rather than admitted and then refused by every
operation that needs an expression.  That is a deliberate narrowing of admission,
stated in the commit that made it; the alternative -- an unevaluated derivative of
an opaque map -- would be a definedness claim the tree cannot compute.

**Item 6** is decided by a sufficient certificate: when the cutting conditions of a
family sum to something decided nowhere-vanishing, the family covers.  A family
that covers without such a certificate -- conditions with no common real zero but a
mixed-sign sum -- is refused.  That refusal is stated in the message, so it is a
refusal of one certificate rather than a claim that the family does not cover.

## The measurements

`probes/acceptance.py` and `probes/acceptance2.py` of the turn that wrote this
note, in the image rootfs against this head:

    derivation E(h) at x=2: -6/5
    opaque refused
    restricted on ('U_N', 'U_S')
    TV frame rank: 2
    map: 2 | ZZ in Sets(): True
    two punctures cover: True | one: False
    composed change (2,3) -> (2/13, 3/13)
    direct pullback section value: 1
