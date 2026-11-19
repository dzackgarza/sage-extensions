# The last item is a computation, and no lemma remains

The item is: which of the five non-fixed `P_0`-orbits on `T_Co`'s liftable
classes carries two of `Gamma_{Co,2}`'s seven plane orbits.  Everything a lemma
can say about it has now been said, in this order:

| what a lemma could settle | verdict | where |
| --- | --- | --- |
| the `Gamma`-orbits are the double cosets `P_0 \ O(q) / rho(Pi_P)` | proved | `results/issue286-the-class-map-on-double-cosets.md` |
| a well-defined class map from those to the `P_0`-orbits of classes | proved | same |
| the base point `A_{U(2)}` is not itself a liftable class `[P/2]` | proved | `results/issue286-the-base-point-is-not-a-plane-class.md` |
| fibres as `|O| m / |P_0|` summed over classes | **refuted** | `results/issue286-the-fibre-formula-refuted.md` |
| the seven partition the `189720` cosets, none uniform | proved | `results/issue286-the-seven-partition-189720-cosets.md` |
| six positive integers summing to seven: one `2`, five `1` | proved | `results/issue286-the-six-partial-sums.md` |
| the fixed class carries exactly one orbit | proved | `results/issue286-the-fixed-class-is-decided.md` |

What is left is the five non-fixed fibres, i.e. the numbers

```
# (P_0-orbits on the cosets of rho(Pi_P) over O_i),  i = 1..5,
```

with orbit sizes `13440, 8192, 1680, 210, 192`, and the answer is `2` at exactly
one of them.

## Why it is a run and not a turn

The coset space has index `[O(q) : rho(Pi_P)] = 189720` in a group of order
`4.7 * 10^13`; the orbits are the double cosets, and the library's own record of
the last attempt at a GAP double-coset computation on this group is a memory
kill (`results/issue381-kernel-row-runner-kill.md`, the `DoubleCoset` membership
wall).  The heap this needs is a runner's, exactly as the incidence rows were.
The call to dispatch, once `class_orbit_partial_sums(plane)` exists, is one
line per row, and the check is `2, 1, 1, 1, 1` over the five measured orbit
sizes.

## Why no further lemma

Each of the eight lemmas above was cheap and decisive; the last three narrowed
the answer to "one of five, with these sizes".  A ninth would have to compute the
double cosets, which is not a lemma but an enumeration -- and this loop has
already produced one refuted lemma and two corrections by running ahead of its
evidence.

## Status

Item: **open, and now blocked only on a dispatched computation**, with the check
pre-stated.  Every other acceptance item of `#286` stage 1 is met, item by item,
in `results/issue286-acceptance-final.md`.

No code changed; no red test.
