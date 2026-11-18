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

## Which operation starts it

Located on `main` `fbf2911` by wrapping `sage_julia_bridge.interface.Julia.call`
and recording the first caller's stack; every timing is in one fresh process:

```
CC(1)           0.00 s   no bridge call at all
CC(2*I)        64.64 s   the first bridge call
CC(2*I) == 2*I  0.22 s   bridge already up, one round trip
```

and the first call's stack is

```
sage_extensions/rings/complex.py:370  _neg_
sage_extensions/rings/complex.py:350  __mul__
sage_extensions/rings/complex.py:353  __rmul__
```

So `2*I` as an element of `CC` is built by a multiplication and a negation that
both route through calcium, and the first of them pays the bridge's start.
`CC(1)` does not. The 0.22 s equality after it is the pipe round trip the
profiler counts at `sage_julia_bridge/interface.py:581(call)`.

The repair is a decision about which arithmetic route answers an exact element
of `CC` — whether an algebraic element is decided in `qqbar`, which the same
module already converts to calcium at `complex.py:105`/`:128`, or in calcium —
and it belongs to the owned complex field, not to this issue. It is one issue,
with the lines above as its starting point.
