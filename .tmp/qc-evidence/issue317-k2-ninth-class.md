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

## Where Sage's mass-stopped traversal stops, and what is not the cause

Measured on the k = 2 summand genus (`issue317-probe29.log`):

    k = 1: det -2, spinor_genus_count 1, spinor_generators(proper=False) []
           Sage's Genus.representatives uses p = 3
    k = 2: det -4, spinor_genus_count 1, spinor_generators(proper=False) []
           Sage's Genus.representatives uses p = 3

- **Seeds are not the cause.** Both genera have one improper spinor genus, so
  `spinor_generators(proper=False)` is empty and Sage seeds the traversal with
  the representative alone (`seeds = [Q]`).
- **The prime is not the cause.** Sage skips p = 2 because 2 divides the
  determinant, and runs at p = 3.  A repaired walk run at p = 2, 3, 5, 7
  (`issue317-probe25d.log`) reaches the same seven classes as at 3, 5, 7
  (`issue317-probe25c.log`): 328 attempts, 7 classes, mass ratio 0.99977 against
  the genus mass, stopping for the budget rather than for the mass.
- **The stop condition is a defect, and it is not sufficient on its own.**
  `neighbor_iteration` starts `mass_count` at zero and adds only *discovered
  neighbours*: the traversal seeds are never counted, so `mass == mass_count`
  cannot fire unless the seed class is rediscovered as one of its own
  neighbours, and the loop then ends when its waiting list empties and returns
  whatever it sampled.  `issue317-probe25.log` shows the shape of that: with
  per-candidate `qfisominit` cost it made 36 attempts in 123 s and returned one
  class.  Accumulating the mass over *all* classes including the seed
  (`issue317-probe25b/c/d`) repairs the accounting, and after that repair the
  walk still stops at seven.
- **What binds is the neighbour sampling.** The two classes it never reaches are
  the ones with 384 roots and 544 roots (`D_17(-1)`); the seven it does reach
  carry 204, 224, 244, 264, 304 and 480.  `find_primitive_p_divisible_vector__random`
  gives a bounded sample per class, and the class-valued neighbour set needs the
  mod-p line orbits — `orbits_lines_mod_p`, hence `automorphism_group()`, which
  does not return at rank 17 (the same stop that was diagnosed for k = 1).

So the k = 2 genus still returns seven of nine with the mass short, and the
assertion keeps refusing the family.  The plane rows and the card comparison
remain undelivered for that reason.

## The spinor-genus split, restored and demonstrated

`_genus_classes` returns one group per improper spinor genus again.  A genus with
one spinor genus returns its single group (the split *is* one group); a genus
with several labels each class by a walk from its seeds at a prime in the
improper spinor kernel, and refuses rather than guesses if a class is reached
from no seed or from two.  `issue317-probe27b.log` and `issue317-probe28.log`:

    diag(3,4,9)   spinor_genus_count 2, class number 2, spinor_genus_class_numbers (1, 1)
    diag(1,16,17) spinor_genus_count 2, class number 8, spinor_genus_class_numbers (4, 4)
    diag(1,16,20) spinor_genus_count 2, class number 6, spinor_genus_class_numbers (3, 3)

The caller that reads the split is `IntegralLatticeMethods.spinor_genus_class_numbers`
(`lattices.py:5087`), which takes `classes[0]` as the representative's spinor
genus and sorts the rest by size.  `spinor_genus_count` does **not** read it: it
is `2 ** len(genus.spinor_generators(proper=False))` (`lattices.py:665`).  The
lattice of the failing `test_published_four_spinor_genus_is_counted_from_all_generators`
is `diag(1, 20, 400)`, positive definite of rank 3, written down by Benham--Hsia,
*On spinor exceptional representations*, Nagoya Math. J. 87 (1982), §2.3, p. 252
as a genus with four spinor genera; Sage's symbol yields two generators, so the
count is 2, and the same `2 == 4` failure reproduces on a `git archive` copy of
the base commit.  It is untouched by this change because it never reaches
`_genus_classes`.

## The ninth class: the prime ladder and an exhaustive p = 2 sweep

Two more measurements, both from the repaired accounting (the mass accumulated
over *all* classes including the seed, which Sage does not do).

`issue317-probe30b.log` — the sampled walk at fifteen primes
(2, 3, 5, 7, 11 … 47), 1440 lines drawn:

    8 classes, mass 2698873/79333480432926720000, ratio 0.99999937,
    shortfall 1/46620662575398912000
    |Aut| / roots: 1941728542064640000/480, 1371195958099968000/480,
                   106542032486400/224, 809053559193600/264,
                   3767021862912000/304, 49662885888000/204,
                   334764638208000/244, 129448569470976000/384

The 384-root class arrives at p = 2, so widening the prime set does help (it took
the walk from seven to eight).  The 544-root class does not arrive at any of the
fifteen primes.

`issue317-probe31b.log` — an exhaustive sweep of the seed's 2-divisible lines
instead of a sample (`find_primitive_p_divisible_vector__next(2, …)`, every
reduced neighbour cached so each distinct one is tested once), 33296 of the
131071 lines of `N/2N` in 3223 s at 13 lines/s:

    5 classes, mass 5903731/555334363030487040000, ratio 0.917
    shortfall includes 1/46620662575398912000

so p = 2 from the seed's class does not produce it either, and at 13 lines/s the
whole 131071-line sweep is 2.8 h.

What is left is a *complete* class-valued neighbour set at an odd prime: at p = 3
that is the 6.4e7 isotropic lines of `N/3N`, which is `orbits_lines_mod_p` — the
computation that needs `automorphism_group()` and does not return at rank 17.
Sampling cannot substitute for it: fifteen primes and 1440 sampled lines, or
33296 exhaustively enumerated lines at p = 2, reach eight classes and not the
ninth, whose mass is exactly 1/|Aut(D_17(-1))| of the genus.
