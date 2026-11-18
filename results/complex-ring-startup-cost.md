# The first `CC` arithmetic in a process pays the Julia bridge's start

**Measured on `main` `7214c54`, pinned image (Sage 11.0.beta5, port
`991b88b0`), load 23:**

```
ComplexManifolds().affine_space(1, name="C")        629.72 s   (first, cold)
  its atlas chart, function ring, point, coordinate,
  one evaluation, a second coordinate section        0.06 / 0.00 / 0.40 / 0.00 / 0.00 / 0.00 s
the whole row again under cProfile (warm)            1.29 s
  of which sage_julia_bridge/interface.py:581(call)  1.21 s, 11 pipe reads
  and sage_extensions/rings/complex.py:592(relation) 1.26 s cumulative
```

The `peakrss` attribution of the pytest run that holds the row confirms a
`julia` process at 1644 MiB peak beside python at 316 MiB.

So the first `CC` (calcium) arithmetic in a fresh interpreter starts the
sage-julia bridge, and every later `CC` operation is a round trip on its pipe.
That start is what `tests/objects/test_manifold_atlas_transition_expressions.sage:113`
pays — the first row of its file to touch `CC` — and it is why the row measures
123.11 s at load 12 and 152.19 s at load 19 while every other row of the file
is under 12 s, and why a run of the whole file at load 19–27 gave no result in
420 s.  It is not the cost of a chart coordinate section: that section builds
in 0.00 s and evaluates in 0.00 s once the bridge is up.

What this costs anyone: any test row that touches `CC` pays it, so the 20 s
per-call ceiling cannot hold for such a row on a loaded host, whatever the row
does.

This needs an issue of its own — the start of the sage-julia bridge at the
first `CC` operation — which the GitHub connection that pushed this cannot
create.  Nothing in it is a defect of this repository's chart or manifold code.
