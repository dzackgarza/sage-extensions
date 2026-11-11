# #336 — the free parameter of the plane block equations

`plane_block_lift` (`isotropic_parabolics.py`) solves the block equations of Dutour
Sikirić--Hulek, Theorem 4.9 (arXiv:2302.01679v2, printed p. 22) in the basis
$(U \mid P \mid K)$ of `plane_block_basis`.  Two equations determine $P_1$ and $P_3$,

$$P_1 = J Q_1^{-t} J^{-1},\qquad P_3 = (K - P_1 K)\,A^{-1},$$

and the third is a linear system for $P_2$:

$$(P_1 J P_2^t)^t + P_1 J P_2^t = \mathrm{remainder}.$$

Its solutions are one coset, $P_2 = (\mathrm{remainder}/2 + sK)^t (P_1J)^{-t}$ over the
skew matrices $sK$, $K = \binom{\ 0\ -1}{1\ \ \ 0}$, so the integral ones are decided by
one rational parameter $s$.

## The exact criterion

Substituting $P_1 = JQ_1^{-t}J^{-1}$ gives $P_1J = JQ_1^{-t}$, hence
$(P_1J)^{-t} = J^{-t}Q_1$, and the linear part of $P_2$ in $s$ is

$$K\,(P_1J)^{-t} = K\,J^{-t}Q_1 = K\,\frac{\mathrm{adj}(J)^t}{\det J}\,Q_1 .$$

With $Q_1$ the integral plane action, its entries' denominators divide $\det J$.  So the
integrality of $P_2$ is periodic in $s$ with a period dividing $|\det J|$, and it is
computed as the least common multiple of the denominators of that matrix:
`plane_block_parameter_period(action)`.

## What that says about the range it replaced

The old search was $s \in [-2|\det J| - 2,\ 2|\det J| + 2]$, i.e. $4|\det J| + 5$
consecutive integers.  Since the period divides $|\det J|$, that range contained a
complete residue system, so **the failure mode the issue describes cannot occur for an
integral plane action**: a lift that exists was not reported as `None` because of the
range.  (A non-integral action cannot be lifted at all: the block matrix carries $Q_1$
itself, and the block is rejected before the parameter matters.)

Measured, to check the argument rather than trust it: over every integral $2 \times 2$
plane action with entries in $[-4, 4]$, on both planes of $T_{\mathrm{En}}$ —

```
P1: det J 2, 124 actions with P1 and P3 integral, 0 with no integral parameter,
    0 needing a non-integral parameter, 0 with every solution outside the old range
P2: det J 4, 360 actions with P1 and P3 integral, 0 with no integral parameter,
    0 needing a non-integral parameter, 0 with every solution outside the old range
```

and for the actions the parabolic's own family lifts, the period is $2$ at both planes
and the admissible parameter is $0 \bmod 2$: the coset always meets
$[-2|\det J|-2, 2|\det J|+2]$.

So the second half of #336's acceptance — "a test gives a candidate whose admissible
parameter lies outside the old range" — has no instance, and the first commit is red
only because the new method does not exist on `main`.  What the repair buys is that the
completeness is now computed and stated instead of resting on an unstated inequality of
a magic constant, and the test pins that inequality.

## What changed

* `plane_block_parameter_period(action)` — the period, with the derivation above in its
  docstring;
* `plane_block_lift` iterates `range(period)` instead of the bounded range, so its
  `None` now means *no* integral solution, and its docstring says so;
* `TRAPS.md`: the entry written under #331 that recorded this as a defect is corrected
  here — it is not one.

## Evidence

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates tests/lattices/test_the_plane_block_lift_coset.sage
2 passed in 88.55s (0:01:28)      # 86.56 s of it the period test, both families built

same run, the #331 modules:
  tests/lattices/test_the_parabolic_completeness_of_an_enriques_plane.sage   4 passed
  tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage       2 passed

red, on 698e661 with the test module only:
1 failed, 1 passed in 81.39s
  test_the_parameter_period_divides_the_plane_block_determinant: AttributeError:
  no attribute 'plane_block_parameter_period'   (the API red; see above for why no
  defect red exists)
```

