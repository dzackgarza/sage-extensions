# #600: the chart-domain consumer file, verified

**Result: `tests/objects/test_manifold_atlas_transition_expressions.sage`
passes on `main` `10b012c`: 5 passed in 139.98 s.**  It was reported two turns
ago as yielding no result in 420 s, which was this host's load and not the
file; nothing in the chart-domain repair is implicated.

## Measurement

Run in the pinned image (Sage 11.0.beta5, port `991b88b0`), time gates on,
load 12.28 on four cores:

```
tests/objects/test_manifold_atlas_transition_expressions.sage
  123.11 s  test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field  (:113)
   11.74 s  test_the_transition_of_two_charts_of_the_plane_evaluates_forward_and_inverse_on_points
    1.12 s  test_the_charts_of_the_complex_projective_plane_change_coordinates_by_ratios
    0.46 s  test_the_overlap_of_two_charts_on_proper_open_subsets_is_where_the_transition_is_defined
    0.12 s  test_a_chart_of_a_proper_open_subset_is_a_section_of_the_functions_on_that_subset
  5 passed in 139.98 s
  star import 2.51 s (ceiling 3 s), collection under 6 s
```

The first test of the file, which does not reach a chart domain — it builds a
transition map — passes alone in 6.72 s, so the earlier stall was not a hang in
this file's construction path.

## The one row over the call ceiling is pre-existing

`test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field`
(`tests/objects/test_manifold_atlas_transition_expressions.sage:113`) takes
123.11 s against the 20 s per-call ceiling.  The same row on the parent
`43c8db6`, which does not carry the chart-domain repair, takes **152.19 s**:

```
.git worktree at 43c8db6, one test selected:
  152.19 s call, 1 passed, 4 deselected in 157.65 s
```

So the overrun is the cost of a complex chart's coordinate section, it is not
this repair's, and it is not chart domains'.  It needs its own issue: the
connector that pushed this reads issues and pushes commits but cannot create
one.
