# issue 317 — the k = 2 genus of `<-4> + E8(-1)^2`: 8 of 9 classes, and the ninth

Pasted runs, adopted runtime (Sage 11.0.beta5), provider at `/repos/sage-extensions`,
port `991b88b0` bound at `/work`.  Every line below is copied from a probe log in
`.scratch/` (`issue317_probe*.log` under `.tmp/`), no figure is reconstructed.

## The genus has nine classes

Sage's own genus mass, and the mass of the eight classes the plane-quotient
search reached (`issue317-probe10.log`, `issue317-probe11.log`):

    genus mass 642332179/18881368343036559360000
    NEW class 1: |Aut| 49662885888000, det -4
    NEW class 2: |Aut| 106542032486400, det -4
    NEW class 3: |Aut| 809053559193600, det -4
    NEW class 4: |Aut| 1941728542064640000, det -4
    NEW class 5: |Aut| 1371195958099968000, det -4
    NEW class 6: |Aut| 129448569470976000, det -4
    NEW class 7: |Aut| 3767021862912000, det -4
    NEW class 8: |Aut| 334764638208000, det -4

The eight are distinct (`|Aut|` separates them) and their reciprocal orders
leave an exact shortfall:

    sum 1/|Aut| over 8 = 2698873/79333480432926720000
    mass               = 642332179/18881368343036559360000
    difference: -1/46620662575398912000

`46620662575398912000 = 2^17 * 17!`, and that is `|Aut(D_17(-1))|`
(`issue317-probe12c.log`):

    D_17: rank 17 det -4 even True
    same genus as <-4> + E8(-1)^2: True
    |Aut(D_17)| = 46620662575398912000
    mass shortfall after the eight = 1/46620662575398912000;
      equal to 1/|Aut(D_17)|: True

So the genus has nine classes and the missing one is `D_17(-1)`.

## The ninth plane is not yet constructed

A primitive isotropic plane of `Lambda_4` is `<u, c>` with `u` isotropic and `c`
isotropic in the complement `C` of one hyperbolic plane (probes 16, 18, 19, 20
established that the general family reduces to this, and that `E^perp` of any
plane contains no isotropic vectors outside the plane, because the quotient
`E^perp/E` is negative definite — so the plane classes are isolated vertices of
any local move and cannot be reached by walking).  Candidate counts tried with
the `det = -4` and 544-root pre-filter, all without reaching `D_17`:

    probe 16: 180000 candidates in 900.3s   (rank-one family, |q| to 36)
    probe 17: 102063 candidates in 400.1s   (both generators lifted, p = 1, 2, 3)
    probe 18:   2850 candidates                (|q| to 200, thin m pools)
    probe 19:   1855 candidates                (large isotropic growth vectors)
    probe 20:    138 candidate pairs           (coordinate-free complement)

Probe 20 also shows why the "mixed" family is not new: with `a, b` in the
complement `C`, `q(a) + 2b(a,b) + q(b) = q(a+b) - q(a) + q(a+b)` up to the
sign of `q`, so the condition is exactly "`a + b` isotropic in `C`", which is
the family probes 10/16/18 already covered.

## What is delivered

The k = 1 genus closes completely: four classes, and the reciprocal orders add
up to the mass exactly (`issue317-genus-of-the-scattone-summands.log`).  The
k = 2 genus does not, so the owner's mass assertion refuses it and it does not
return eight classes as if they were nine.

## The ninth plane: two more families tried, both closed

Every family above fixed the first generator to `e1`.  Planes through a *sampled*
isotropic vector `u` were then tried, since nothing forces a plane class to
contain a vector equivalent to `e1`.

`issue317-probe24.log` (sampled `u`, second generator solved from the two exact
conditions `2(ab + cd) = s` and `b(alpha_u, alpha) = -b(m_u, m)`):

    7 sampled u, 565 planes, 5 classes in 954.9 s
    |Aut| 1941728542064640000   roots 480
    |Aut| 49662885888000        roots 204
    |Aut| 809053559193600       roots 264
    |Aut| 106542032486400       roots 224
    |Aut| 1371195958099968000   roots 480
    mass 17081521/555334363030487040000 vs 642332179/18881368343036559360000  (short)

The root counts are the informative part: the reachable quotients carry 204, 224,
264 or 480 roots, and `D_17(-1)` carries the maximum 544 = 2*17*16.  So the
missing class is not a rare needle in the same haystack — it is the class with the
largest root system in the genus, and none of the sampled `u` reaches it.

`issue317-probe22.log` (isotropic `c` drawn from kernel-basis combinations of the
complement, `u` sampled):

    1400 hyperbolic splits, 17778 planes, 1 class  (the generator almost never
    produces an isotropic c, so the family is empty in practice)

`issue317-probe23.log` (hyperbolic pair inside the complement, then
`c = x + (s/2) y + m'`): 0 splits in 56 s — small combinations of the complement's
kernel basis contain no isotropic vector, so that parametrisation needs a
reduction of the complement first and is not usable as written.

## Status of the batch

- k = 1 complete by the mass: done, pushed.
- k = 2: 8 of 9 classes; the ninth is `D_17(-1)` (verified in the genus; its
  `|Aut| = 2^17 * 17!` is exactly the mass shortfall).  Not complete, so the mass
  assertion refuses the family.
- The plane rows and the card comparison are therefore **not** delivered: both
  need the ninth plane.
- `just test` cannot run on this host: its `_sage-bin` probe requires a Sage
  executable, and the only Sage is inside the adopted PRoot runtime, whose
  interpreter the probe reports as "not executable".  The same `pytest`
  invocation was run through the runtime launcher instead.
