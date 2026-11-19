# The six partial sums need a library method, not a test-side computation

The lemma of the previous round reduces the last datum to six numbers

```
S_i = sum over the cosets over O_i of |P_0 cap g rho(Pi_P) g^{-1}|,
```

with `S_i = |P_0|` for five of them and `2|P_0|` for the doubling one.  A test
that computes them was written this turn and **could not be landed**: it needs
four things a lint-clean session test may not name.

```
tests/lattices/test_each_class_orbit_sums_to_the_stabilizer_order.sage:42: TL01 from sage.libs.gap.libgap import ...
:47: TL02 private attribute ._engine_group
:77,78,79: TL10 len(): ask for a cardinality
```

The test computed, on `U + U(2) + <-4>`, `P_0`'s orbits on the liftable classes
and, for each, the sum of `|P_0 cap Stab(J)|` over its classes -- the specimen
where each class carries one coset, so the coset sum is the class sum.  It used
`libgap` for the stabilizers, `_engine_group` for the class sets, and `len` for
the orbit count: exactly the three names the test lint forbids (TL01, TL02,
TL10).  There is no test-side rewording that fixes this, because the quantities
are engine-level.

**What the item needs, precisely.**  A method on `OrthogonalCharacterQuotient` --
the owner that already carries `plane_class_index` and `class_orbits` -- with the
signature and semantics

```
class_orbit_partial_sums(plane) -> tuple of (orbit size, sum)
```

returning, for each `P_0`-orbit of liftable classes, the sum of
`|P_0 cap g rho(Pi_P) g^{-1}|` over the cosets of `rho(Pi_P)` over that orbit.
Once that exists, the check is one line in a session test: the sums over the
fixed index set are `|P_0|` five times and `2|P_0|` once.

**Why it is not written here.**  It is a new public computation over the engine's
double-coset data -- the same shape as `class_orbits`, which took a round to get
right after two wrong attempts -- and this session has already landed three
capabilities (`class_orbits`, `plane_class_index`, the no-split reasons) whose
first drafts were wrong.  A fourth, drafted in a turn's tail after a lint
rejection, is the pattern that produced those errors.

## Status

The lemma stands (previous round, proved); its check needs the method above, and
the two `T_Co` facts it must reproduce are known: six orbits of sizes
`13440, 8192, 1680, 210, 192, 1`, and sums `|P_0|` five times with `2|P_0|`
once.  No code changed this turn and no test landed; the failed test is recorded
with its lint lines rather than deleted silently.
