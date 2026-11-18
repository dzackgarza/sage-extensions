# The cached sphere, the submanifold atlas, and the charts another file registered

Status: diagnosis only. No repair is landed in this note; the two candidate
repairs are named with what each costs.

## What is wrong

`SmoothManifolds().sphere(2)` is a cached method on the category, so one sphere
object serves every caller in a process.  `chart_on_open_subset` registers the
chart it cuts *on that manifold* -- that is what makes `open_submanifold_inclusion`
find it, since the inclusion is presented by a chart whose domain is the open
submanifold -- and `open_submanifold` then copies *every* ambient chart onto the
submanifold, restricted to it.

So a chart another construction registered on the sphere is still there for the
next caller, and it lands in the submanifold's atlas:

    sphere = SmoothManifolds().sphere(2)          # cached: one object per process
    sphere.chart_on_open_subset("V1", ...)        # registered on the sphere itself
    domain = sphere.atlas()["U_N"].domain()
    sphere.open_submanifold(sphere.open_submanifold_inclusion(domain)).chart_labels()
    # ('U_N', 'U_S', 'V1', ...)

Measured 2026-11-18 in the image rootfs, worktree of `41b75d7`:

    start: ('U_N', 'U_S')
    after V1 : ('U_N', 'U_S', 'V1')
    after V2 : ('U_N', 'U_S', 'V1', 'V2')
    after R1 : ('U_N', 'U_S', 'V1', 'V2', 'R1')
    sub charts: ('U_N', 'U_S', 'V1', 'V2', 'R1')

Two consequences follow, and both are defects rather than inconveniences.

1. `open_submanifold` states a transition between two of the submanifold's charts
   only when the *ambient* manifold states one between the same labels.  A chart
   cut on a subset has a transition to the chart it was cut from (stated by
   `chart_on_open_subset`), and no transition to the other ambient charts.  The
   submanifold therefore carries pairs of charts with no stated coordinate
   change, and the atlas is incomplete: a section, a form or a frame stated on
   one of those charts cannot be compared with anything written on the other.
   The failure surfaces as

       AssertionError: ... has no transition map from the chart 'U_S' to the
       chart 'U_N_overlap': none was defined with transition_map

   where `U_N_overlap` is a label an engine restriction carried, and the pair
   asked for is one `coordinate_vector_field` needs to state a frame on every
   chart.

2. `section`, `smooth_function` and `coordinate_vector_field` demand components
   on *every* chart of the atlas and a transition for *every* pair.  A section is
   fixed by its components on a cover, so the demand is stronger than the
   mathematics: one extra chart registered by an unrelated construction makes a
   frame that was stated correctly on the charts of its own presentation
   unstataeable.

Measured: the nine files of the tangent-bundle work pass 32 of 34 in one session,
and the two failures are the two-chart file, which passes alone (2 passed in
14.85 s); the same two fail identically on `41b75d7` without the session's
newest change (28 passed, 2 failed, same names).

## The two repairs, and what each costs

**Coverage in the atlas.**  `section` and `smooth_function` take components on a
cover and check agreement only between the charts they were given; the manifold
decides whether the given charts cover it.  The tree has no coverage decision
today: `declares_union` is the engine's, and the atlas does not expose it.  This
repair is the mathematically right one -- a section is fixed on a cover -- and it
makes the extra charts harmless instead of load-bearing.  It costs a coverage
predicate on the atlas, with its own refusal when coverage is undecided, and it
touches the two constructors and the frame check.

**Composition of the missing transitions.**  `open_submanifold` relates two
restricted charts through a third when the ambient manifold states no direct
change: `phi_t o phi_s^{-1} = (phi_t o phi_c^{-1}) o (phi_c o phi_s^{-1})`
whenever the intermediate chart meets both (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1).  It is smaller and it fixes the incomplete atlas
rather than working around it, but it needs a composition of two transitions as
an owned transition, with the intermediate overlap conditions carried into the
source chart -- the expression work is the same as the transitions already do,
and the overlaps are the part to get right.

Neither is landed here: the first needs a coverage predicate the tree does not
have, and the second was written and withdrawn inside one turn because the
composition was not verified on a manifold whose charts meet through a third.
The next reader should take the coverage repair first: it is the statement the
mathematics makes, and it does not depend on which charts a process happens to
have registered.
