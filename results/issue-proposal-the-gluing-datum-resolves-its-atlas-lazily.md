# Proposed issue for the orchestrator: a glued scheme pays all C(n,2) pair transitions to exist

Filed from #575, whose last open line is the Sterk2 specimen test's call against the
20 s ceiling.  The cost there is not #575's operation -- the vertex-to-chart join is
0.55 s -- but the gluing of the seventeen-chart fan it is asked on.  No existing issue
owns this: `src/sage_extensions/categories/schemes/gluing.py` is named in commits for
#593, #541 and #592, and none of them is about what the datum resolves at construction.
Please file this and order it with the other scheme-layer cost units.

Suggested title:

> a glued scheme pays all C(n,2) pair transitions to exist, 10.2 s of a 12.9 s seventeen-chart variety

Body:

```
`_toric_variety` supplies a family of `_face_transition` for every pair of maximal
cones (`categories/schemes/toric/toric_schemes.py:2259-2264`).
`_FiniteSchemeGluingDatum.__init__` resolves both directions of every pair
(`categories/schemes/gluing.py:954-957`) and verifies them (`:965-966`) before
`_glued_scheme` (`:967`) builds the scheme.  For a fan with n maximal cones that is
2*C(n,2) isomorphisms of localizations before any chart can be asked for.

It is not a verification pass that could simply be deferred: the scheme's own overlaps
are the transitions.  `overlap(source, target)` is
`transition_between(source, target).forward().domain()` (`gluing.py:1037-1038`), and
`transition_between` reads the family, so the forward map of every pair is needed for
the scheme to exist in the form this datum builds.

Measured on cd58a62, sage 11.0.beta5, image sha256:59568577..., load average 12.85 on
four CPUs, on the normal fan of the Sterk2 specimen (17 rays, 17 maximal cones):

  toric_variety total      12.89 s
    pair transitions       10.20 s   (79%)
    17 charts               1.73 s   (13%)
    glue_affine_atlas       0.18 s
    native realization      0.01 s
  one vertex normal cone    0.53 s
  its chart                 0.02 s
  atlas lookup at its cone  0.014 s

The consumer this bites is `tests/schemes/test_sterk_polygon_vertex_charts.sage:165`:
the row it decides is the chart of a vertex and its identification with the atlas, and
the whole variety has to exist first.  That file's specimen call is 7.26 s on an idle
host, 12.9-14 s at load average 12.9, and 28-180 s at load average 25-32 -- the same
co-tenancy under which this host also reports the session star import at 12.84 s against
its 3 s ceiling, so the ceilings here are the host's own.

Proposed acceptance:
- a glued scheme answers its charts and its atlas without materializing pair
  transitions it is not asked for, and any such deferral keeps the datum's checks
  before a transition or overlap is answered;
- the seventeen-chart Sterk2 fan builds for its charts plus its native realization
  (1.74 s here), and the specimen test's call fits 20 s at load average 20;
- the failure set of the scheme-layer consumers (open complements, products,
  blow-ups, the toric atlas gluing tests) is unchanged at the same base commit, judged
  by test id and not by count.

Not a proxy: #575 did not trim its test, did not use --no-time-gates and did not raise
the ceiling; the row it decides passes its assertions at every load measured.
```

Install, since this connection cannot create issues:

```
gh issue create --repo dzackgarza/sage-extensions \
  --title "a glued scheme pays all C(n,2) pair transitions to exist, 10.2 s of a 12.9 s seventeen-chart variety" \
  --body-file results/issue-proposal-the-gluing-datum-resolves-its-atlas-lazily.md
```
