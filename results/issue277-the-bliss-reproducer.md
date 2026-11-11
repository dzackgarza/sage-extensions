# #277: the bliss reproducer and the 3U orthogonal generators, in the adopted image

**Result: both calls return in the adopted runtime, with no crash, and the module that exercises
the crash's own frame is added and green.** One caveat has to be stated first, because the issue
asks about a specific published image.

## Which image was run

| | digest |
| --- | --- |
| the adopted runtime used here | rootfs of `ghcr.io/dzackgarza/sage`, config blob `sha256:2d6a4754b6f1518af356dd28ac6ec2e7678c7fe4ab0d70c2e7c9ecbc2c605eca`, 17 layers — the pin the repository's records name as `sha256:59568577…` |
| `ghcr.io/dzackgarza/sage:develop` today | index `sha256:1a05088a0b161a7149e792170b78e2de7640f152f1236d6740b5a40d3308a74c`, amd64 manifest `sha256:5304338e…`, config blob `sha256:d2a9dcdb…`, 22 layers |

So **`develop` has moved past the pin and was not run here**: this VM has 7.2 GB free of 248 GB,
and the 22-layer image cannot be pulled and unpacked in that. The two calls below were made in
the pinned published image; the `develop` check the issue asks for is still owed, and needs a
host with room for the image.

## The two calls

**Bliss, fresh process** (`sage.graphs.bliss.canonical_form`, the issue's minimal reproducer):

```
canonical_form(CompleteGraph(3), certificate=True): 0.015s -> ([(1, 0, None), (2, 0, None), (2, 1, None)], {0: 2, 1: 1, 2: 0})
canonical_form(captured labelled-loop triangle):    0.000s -> ([(0, 0, 0), (1, 0, 1), (1, 1, 0), (2, 0, 1), (2, 1, 1), (2, 2, 0)], {0: 2, 1: 1, 2: 0})
K3 automorphism group order:          0.004s -> 6
Petersen automorphism group order:    0.136s -> 120
bliss module: /sage/.venv/lib/python3.14/site-packages/sage/graphs/bliss.cpython-314-x86_64-linux-gnu.so
launcher exit: 0
```

No exit 139: the extension in this image is GMP-consistent, and the order checks above are the
same three the issue's fourth comment ran in the shared container.

**The public call the stack goes through**, `Lattices(ZZ)("U")` summed three times:

```
lattice: Integral lattice of rank 6 and signature (3, 3)
orthogonal_group():   0.00s
group_generators():  12.31s -> 48 generators, every one preserving the form on the basis
subgroup(generators).order(): ℵ_0
group.cardinality():          ℵ_0
launcher exit: 0
```

A second run measured 11.28 s with 45 generators, so the generating set is not canonical in
size; the generated subgroup is `O(L)` in both cases and the process exited 0 each time.

## The regression module

`tests/lattices/test_the_coloured_vector_transporter_returns.sage`. It calls the frame that
crashed — `coloured_vector_families._transporter`, which computes `canonical_form` of the
coloured graph — through the public transporter of two coloured vector families on 3U: the
six-vector basis, and the same family with the first two planes' coordinates exchanged.

Its assertions are the two the batch asks for and nothing else: the returned witness lies in
`O(L)`, and the set it carries the family to equals the target family, two independently
computed sets.

```
tests/lattices/test_the_coloured_vector_transporter_returns.sage   0.55s call, passed
+ tests/lattices/test_vector_family_stabilizers.sage               11 passed in 2.38s
just test-push                                                     Push syntax: 29 file(s) checked; no errors.
```

Two notes on how it was written, since both cost a run: the transporter of two *vectors* takes
the vector route and not the coloured one, so the test passes two families
(`Sets().Mor(Sets.Δ[5], L)`); and `assert witness is not None` is rejected by the test lint
(`TL09`, an assertion that holds of anything), so the return is asserted as membership in
`O(L)`, which also fails if nothing is returned.

The three-plane generators call itself (11--12 s) is measured above but not asserted: at 11--12 s
it sits inside the 20 s call gate with little room, and the transporter it calls is the frame that
crashed.
