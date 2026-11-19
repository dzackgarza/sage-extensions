# #198: the eight review items, decided on `1f38572`

The review of 2026-11-19 recorded 2 items met, 5 not met and the coercion defect open.
Each is answered below with the code that carries it and the measurement that decides it.
Line numbers are of the head this note is pushed on, `1f38572`.

| # | Item | State | Code | Measurement |
|---|---|---|---|---|
| 1 | Tangent bundle of a smooth manifold, owned, sections over `C^oo(M)` | met | `manifolds.py:2854` `tangent_bundle`; `vector_bundles.py:452` `SmoothVectorBundles` | the circle's tangent bundle has rank 1 |
| 2 | Sections as derivations of `C^oo(M)` | met on the algebra the tree states | action `vector_bundles.py:660`; admission `real_functions.py:828`; expression test `manifolds.py:1225` | `E(h)` at `x = 2` is `-6/5`; an opaque callable is refused at the algebra |
| 3 | Restriction to an open submanifold | met | `vector_bundles.py:978` `restrict` | a field stated on two charts restricts to a domain carrying a third |
| 4 | Pullback along a general smooth map | met | `vector_bundles.py:546` `pullback_along`, `:93` `_pullback_family_agrees`, `:1023` `pullback_of` | a directly stated pullback section reads `1` at `(2,3)` |
| 5 | Rank-`r` trivialization `C^oo(M)^r -> Gamma(E)` | met on the same algebra | `vector_bundles.py:1100` `trivialized_by`, `:1173` `trivialization`, `:1194` the pair of maps | the chart domain's `TV` is free of rank two |
| 6 | Coverage of a family of charts | met by three exact certificates | `manifolds.py:802` `_chart_family_covers`, `:827` `_unrestricted_labels`, `:865` `_sum_certificate_covers`, `:926` `_member_conditions_in_chart`, `:968` `_conditions_share_no_zero` | two punctured planes cover; two doubly cut charts missing the origin do not |
| 7 | Chain rule and composed transitions | met | `manifolds.py:293` `then`, `:763` `_composed_ambient_transition` | the cut chart to the south chart sends `(2,3)` to `(2/13,3/13)` |
| 8 | Coercion at its owner | met | `owned_category.py:778` `_bases_with_sage_sets_parent` | `RR.coerce_map_from(ZZ)(2) = 2`, and `ZZ in Sets()` is true |

## The measurement

One probe of the turn that wrote this note, in the image rootfs against this head:

    1/2 rank: 1 | E(h): -6/5
    2 opaque refused
    3 restricted: ('U_N', 'U_S')
    5 TV rank: 2
    4 direct pullback section: 1
    6 punctures cover: True | doubly cut miss origin: False
    7 composed: (2/13, 3/13)
    8 map: 2 | ZZ in Sets(): True

## Two things that are narrower than the sentences, both stated in code

**Item 2 and item 5** are met on the algebra of smooth functions *as this tree states
it*: an element carries its chart expressions, and a map given only by a callable is
refused at admission (`real_functions.py:828`).  That is a deliberate narrowing, stated in
the commit that made it.

**Item 6** decides by three exact certificates -- a nowhere-vanishing sum, a trivial
ideal, and a nowhere-vanishing sum of squares -- applied to the product of each member's
cuts.  A family certified by none of them is refused, and the messages say so.  The case
that remains undecided is written up with its exact polynomial and the Gram matrix that
certifies it in `results/issue198-the-degree-four-gap-and-why-the-cheap-reading-adds-nothing.md`.
