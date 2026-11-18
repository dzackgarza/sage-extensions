# An exact element of `CC` is answered through calcium, so its first arithmetic pays the Julia bridge's start

A row that builds one exact complex number blows the 20 s per-call ceiling of
the test suite on any loaded host, because `CC(2*I)` builds its element by a
multiplication and a negation that both route through calcium, and the first
calcium operation in a process starts the sage-julia bridge.

## What it costs, measured

One fresh process, `main` `fbf2911`, pinned image (Sage 11.0.beta5, port
`991b88b0`), load 12–23:

| operation | time |
| --- | ---: |
| `CC(1)` | 0.00 s, no bridge call |
| `CC(2*I)` | **64.64 s**, the first bridge call |
| `CC(2*I) == 2*I` after it | 0.22 s |
| `ComplexManifolds().affine_space(1, name="C")` cold, at load 23 | **629.72 s** |

The first call's stack, with `sage_julia_bridge.interface.Julia.call` wrapped to
record its first caller:

```
sage_extensions/rings/complex.py:370  _neg_
sage_extensions/rings/complex.py:350  __mul__
sage_extensions/rings/complex.py:353  __rmul__
```

`peakrss` of the pytest run that holds the row attributes 1644 MiB peak to a
`julia` process beside 316 MiB to python.

## What it does to the suite

`tests/objects/test_manifold_atlas_transition_expressions.sage:113` is the first
row of its file to touch `CC`, so it pays the start: 123.11 s at load 12 and
152.19 s at load 19 against the 20 s per-call ceiling, while every other row of
the same file is under 12 s, and a whole-file run at load 19–27 gave no result
in 420 s. The chart coordinate section that row exercises builds in 0.00 s and
evaluates in 0.00 s once the bridge is up — the row is not slow, the first
`CC` element is.

## The decision this needs

Which arithmetic route answers an **exact** element of `CC`: algebraic elements
in `qqbar`, which `sage_extensions/rings/complex.py` already converts to
calcium at `:105` and `:128`, or all elements in calcium through the bridge.
`CC` is calcium-backed and its elements are not all algebraic, so a `qqbar`
route for the algebraic ones is a second algorithm over the same field and
needs the owner's ruling, not a patch. The alternatives are that, or making
the bridge's start cheap, or a stated exemption for rows that touch `CC`.

## Acceptance, if this is taken

- `CC(2*I)`'s arithmetic is answered within the suite's 20 s call ceiling on a
  host at load 20, with the route it takes named in the source.
- whichever route is chosen, `CC`'s identity is unchanged: the same elements,
  the same equality, and every existing `CC` row still green.
- if the answer is an exemption rather than a route, the suite states which
  rows pay the bridge and why.

This is filed here because the GitHub connection that pushed the measurement
reads issues and pushes commits and cannot create one.
