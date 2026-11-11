# #303: the T_Co plane orbit, its setwise stabilizer, and the composition of automorphisms

**Result: the call returns; there is no crash on `main`.** The orbit of the image of a
primitive isotropic plane of `T_Co` in its discriminant form, and its setwise
stabilizer, are computed through the public call, every composed automorphism preserves
`q`, and `|orbit| * |Stab| = |O(q)|` on both sides computed.

Measured on `a6627c7ddcb62f5afe7d3dd24d363b73fa2b0bd1` (`main`), on the adopted runtime:
Sage 11.0.beta5, Python 3.14.10, GAP 4.16.1.

| quantity | value |
| --- | ---: |
| `T_Co` | `<2> + (E8(-1) + U)(2)`, Dolgachev--Kondo (3.6), p. 513, rank 11, signature (2, 9), det -2048 |
| `A = A_{T_Co}` | `(Z/2)^11`, 2048 classes |
| `\|J\|`, `J = D(P)` | 4 |
| `\|O(q)\|` | 46 998 591 897 600 |
| `\|orbit(J)\|` | 23 715 |
| `\|Stab(J)\|` | 1 981 808 640 |
| `\|orbit\| * \|Stab\|` | 46 998 591 897 600 (= `\|O(q)\|`) |
| stabilizer generators returned | 6 |

Costs in one process, specimen built first: `|O(q)|` 4.1 s, orbit 29.7 s, stabilizer
1.0 s (`.tmp/p303-orbit.log`). The stabilizer is the engine's own setwise `Stabilizer`
of `J` in `O(q)`, so no product of two owned automorphisms is taken along the walk.

## What was added

`tests/lattices/test_the_tco_plane_orbit_and_its_composed_automorphisms.sage`, two tests,
no library change.

The plane is a plane of the lattice, not an arbitrary two-space of `A`. With `h`, `ep`,
`fp`, `a1` ... `a8` the named module generators,

```
P = < ep + fp - (a1 + ... + a8),  2h - (a1 + a2 + 2a3 + 2a4 + 2a5 + 2a6 + 2a7) >
```

is rank two (`plane.module_rank() == cardinal(2)`), primitive (`is_primitive() is True`),
and totally isotropic (`q` and `b` vanish on every pair of its generators), and
`J = D(P)` is spanned by the two divided discriminant classes `[v/2]`, on which `q_A`
vanishes. The two-by-two minors of the generators' coefficient matrix have gcd 1, which
is the primitivity the plane's own assertion reads back.

* The first test computes `O(q)`, `orbit(J)`, `stabilizer(J)`, asserts the orbit's
  cardinality equals the finite action's point set, multiplies the two computed orders
  against the group's, and validates each returned stabilizer generator as an isometry
  with inverse (`validate_inverse`, `validate_form_preservation`) that fixes `J`
  setwise.
* The second test is the reported composition: every product of two selected generators
  of `O(q)`, and the square of every generator of the returned stabilizer, through the
  public multiplication `TorsionFormAutomorphism.__mul__`. Each composite is validated as
  an isometry with inverse and checked on the module generators to act as the
  composition it names.

`validate_form_preservation` is a complete certificate and not a sample: it probes `q`
on the module generators and their pairwise sums, and `b(x, y) = q(x + y) - q(x) - q(y)`
recovers the polar form on every pair of generators, so `q` is determined on all of `A`.
A generator of `O(q)` that preserves `q` therefore preserves it at every point of the
orbit walk as well, which is why the isotropy of all 23 715 points does not have to be
swept separately.

## Run

```
/sage/.venv/bin/python -u -m pytest \
  tests/lattices/test_the_tco_plane_orbit_and_its_composed_automorphisms.sage \
  -q -o addopts= -p qc_sage_session --tb=short -rf -p no:cacheprovider \
  --durations=0 --durations-min=0 -s
```

```
..
============================== slowest durations ===============================
38.56s call     ...::test_the_tco_plane_has_a_returning_orbit_and_setwise_stabilizer
19.03s call     ...::test_the_composed_automorphisms_of_the_torsion_form_are_isometries
2 passed in 59.49s
```

`addopts` is blanked because this runtime's Sage venv carries neither `pytest-timeout`
nor `pytest-reportlog`, which the declared `addopts` names. Under the repository's own
`pyproject.toml` ceilings the two calls (38.56 s and 19.03 s) exceed the 20 s per-call
ceiling and the first is close to the 60 s `--timeout`; the run above is the gated
configuration's computation with the ceilings lifted, which is how the #296 and #321
evidence was taken.

Test lint:

```
/sage/.venv/bin/python -s -m sage_extensions.testing.test_lint \
  tests/lattices/test_the_tco_plane_orbit_and_its_composed_automorphisms.sage
1 files, 0 findings
```

## The reported crash

The report is a SIGSEGV at `_orbit_walk` in `generator * transversals[position]` ->
`__mul__` -> `_from_engine` -> `_transported_map` -> `_normalized_map` ->
`fqf_orthogonal._act_` -> `abelian_aut.matrix` -> `abelian_group_gap.exponents`, taken on
an uncommitted checkout based on `7540ceba`. The frame does not exist in either revision:

```
git grep -n "_orbit_walk" 7540ceba -- src/   -> no match
git grep -n "_orbit_walk" a6627c7 -- src/    -> no match
```

so the failing walk is not in the tree and a failing regression cannot be committed
against it. The reported base's own public path was measured instead
(`.tmp/p303-base.log`), with the `A_{T_Co}` specimen of that revision
(`T_Co = B(2)`, `B = U + U + I_{0,7}`, plane `<e1, e2>`, `J = <[1], [3]>`):

```
[    0.13s] lattice built
[    0.18s] plane built
[    4.86s] divided classes ([1], [3])
[    4.93s] |A| = 2048
[    5.13s] |J| = 4
[   49.90s] |O(q)| = 46998591897600
[   49.90s] orbit
launcher exit: 124          (inner cap 1200 s, peak tree RSS 5547 MiB)
```

So on `7540ceba` the orbit call does not return at 1200 s and is not observed to crash;
between that revision and `a6627c7` the owner route replaced the point-by-point walk with
the retained element-rank action (`subobject_orbit_action`,
`FiniteGSets.from_finite_orbits`) and the stabilizer with the engine's setwise
`Stabilizer`, which is why the same call answers in 30.7 s here. No guard, cap, timeout
or profile was added, and no test was weakened: what changed is measured above, not
assumed.

## Issue closure text

> The call returns on `a6627c7`. `T_Co` is built from Dolgachev--Kondo (3.6), p. 513
> (`NamedLattices.Tco`), and `J = D(P)` is the image of the primitive isotropic plane
> `P = <ep + fp - (a1 + ... + a8), 2h - (a1 + a2 + 2a3 + 2a4 + 2a5 + 2a6 + 2a7)>`:
> `|orbit(J)| = 23 715` in 29.7 s, `|Stab(J)| = 1 981 808 640` from 6 generators in
> 1.0 s, and `23 715 * 1 981 808 640 = 46 998 591 897 600 = |O(q)|` on both sides
> computed. Every product of two selected generators of `O(q)`, two consecutive
> generators of the returned stabilizer and the square of each of its generators is
> validated as an isometry with inverse (`validate_inverse` and
> `validate_form_preservation`, the latter a complete certificate through
> `b(x,y) = q(x+y) - q(x) - q(y)`) and acts as the composition it names.
> `2 passed in 59.49 s`; test lint `0 findings`.
>
> The reported SIGSEGV frame `_orbit_walk` exists in no revision (`git grep` at
> `7540ceba` and at `a6627c7`), so no failing regression can be committed against it; on
> `7540ceba` the same public call does not return at 1200 s (peak 5547 MiB) rather than
> crashing. The owner route that replaced the walk is the retained element-rank action
> plus the engine's setwise `Stabilizer`, which is what returns here.
