# `Gamma_{Co,2}`'s distribution over the liftable classes: measured, and not what I assumed

The owed datum was "which classes `J` carry `Gamma_{Co,2}`'s seven plane
orbits".  Two probes answer most of it and correct two things I had asserted.

## The two order-four subgroups are not the same one

`A_{U(2)} = <[ep/2],[fp/2]>` -- the U(2) summand's discriminant form, which is
the point the driver's `_decomposition` builds and the page's `P` stabilizes --
is **not** the plane class `J = [P/2]`, which is spanned by a plane's *divided*
classes.  They have different stabilizers and different orbits:

| class set | `|Stab_{O(q)}|` | `O(q)`-orbit |
| --- | ---: | ---: |
| `A_{U(2)}` (the U(2) block's dual classes) | **696729600** | **67456** |
| `J = [P/2]` (a plane's divided classes) | **1981808640** | **23715** |

Measured in one process (`.scratch/w286-probes/probe-distribution.log`,
`probe-distribution2.log`).  The first number, `696729600`, is `|W(E8)|` -- the
same order the earlier session measured as `Gamma_{En,2}`'s discriminant image
in `O(T_En)`, which is a cross-check on the identification rather than a
coincidence.

The issue's index is over the *second* family: "the liftable order-four isotropic
subgroups `J = [P/2]`", 23715 of them.  Both notes that used `A_{U(2)}` and
`[P/2]` interchangeably were loose, and this is where the two part.

## The distribution, measured

`P_0 = Stab_{O(q)}([P/2])`, of order 1981808640, acts on the orbit of `[P/2]`,
which is the 23715 liftable classes.  Its orbits there split as

$$
13440 + 8192 + 1680 + 210 + 192 + 1 = 23715,
$$

**six** orbits, measured in 5.5 s after the stabilizer (GAP `Orbits` with
`OnSets`, the same engine as `stabilizer_of_classes`).  So the class set is not
one orbit; it splits into six pieces of very different sizes, one of which is a
single fixed class -- `[P/2]` itself.

## What that settles, and what it does not

`Gamma_{Co,2} = rho^{-1}(P_0)` has **seven** plane cusps and the classes fall
into **six** `P_0`-orbits, so the two counts are different and the earlier
"equivalently" in `results/issue286-the-coble-2-plane-row-over-its-classes.md`
was wrong: the plane orbits do not sit one per class-orbit.  Seven orbits over
six class-orbits means exactly one class-orbit carries two of them.

What is still owed is *which* one -- the remaining step is to place the row's
seven representatives on the six orbits, and that needs the row's
representatives, i.e. the `#391` plane computation.  What is no longer owed is
the shape: the partition of the 23715 classes is measured, and the row's orbits
are seven pieces over its six.

## Cost, and why no test

The measurement is 24 s end to end from a fresh process (group 4 s, the class set
8 s, the stabilizer 3 s, the orbit 3 s, the decomposition 6 s), which is over
the 20 s call ceiling, so it is recorded as a probe and not as a gate test.  The
smaller specimens in `results/issue286-the-coble-2-plane-row-over-its-classes.md`
(eight and sixteen classes) remain the gated checks of the row's shape.
