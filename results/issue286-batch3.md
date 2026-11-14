# #286, batch 3: the Scattone plane classes by their quotients, and `Gamma_{En,2}`

Branch at `5570c5952e`.  Nothing on T_Co is run.  **Neither item closes**, and no
card comparison is claimed in this batch.  What changed is that each stop is now a
specific measured wall with the machinery on both sides of it built and checked.

## Item 1, `6JRX` / `6JRY` planes: the class machinery runs, the search reaches 3 of 4 and 5 of 9

The target the instruction names -- LLL-reduce every form before automorphism and
isometry calls, separate candidates by cheap invariants, drive the enumeration by the
Smith--Minkowski--Siegel mass -- is the right one, and it works.  What it does not do
is enumerate the plane classes from a bounded shape family.

### What runs

On the genus of `E8(-1)^2 + <-2k>` (rank 17, negative definite; the sign of the form
does not change isometry classes):

```
seed LLL-reduced: .lll()                        0.0 s
|Aut(seed)|                                     1941728542064640000   in 0.3 s
conway mass (SMS)                               2499347/9440684171518279680000  in 1.1 s
theta_series(8)                                 18.8 s       (too slow to separate candidates)
short_vector_list_up_to_length(6)               PARI stack overflow at 1 GiB
automorphism_group()                            does not return (>90 s, killed)
qfisom on two LLL-reduced rank-17 forms          0.0-3.1 s, occasionally minutes
```

`number_of_automorphisms()` answers in 0.3 s although `automorphism_group()` hangs:
both are PARI `qfauto`, but only the first returns the order without building the
matrix group.  Sage's `algorithm="orbits"` neighbour route needs the second (through
`orbits_lines_mod_p`), which is why the genus never enumerated; Sage's own default
heuristic would have chosen `"random"` at this \(p^n\).

Random \(p\)-neighbours at \(p=3\), every neighbour LLL-reduced, candidates bucketed by
`|Aut|` (the invariant the mass needs anyway) and compared by `qfisom` only inside a
bucket:

```
k = 1: 4 classes in 19 s from 10 neighbours,
       sum 1/|Aut| = 2499347/9440684171518279680000 = mass   EXACT
       |Aut| = 1941728542064640000, 12804747411456000,
               5393690394624000,   1371195958099968000
```

So the class number of the genus of `E8(-1)^2 + <-2>` is **4**, certified by the mass
equality rather than by a count.  That is the card's four plane rows if Scattone's
bijection is used, but the bijection is what item 1 has to establish, so it is not
used here as a comparison.

\(k=2\) (det 4, mass `642332179/18881368343036559360000`): the traversal found
`|Aut|` = 1941728542064640000, 49662885888000, 106542032486400 and then entered a
`qfisom` between two candidates with equal `|Aut|` that did not return in over six
minutes, and the run was stopped.  **`h(2) = 9` is not measured.**

### The quotient invariant, and a correction to batch 2

For a primitive isotropic plane \(E\) of \(\Lambda_{2k}\), \(Q = E^\perp/E\) is
computed from the Gram matrix alone: the kernel of the two covectors, its saturation,
the Smith normal form of the plane's two coordinate rows, and the Gram of the
remaining rows.  Cost 0.15 s per plane and no Julia bridge, against the 25-35 s cold
and 5 GiB growth of the reduction route.

It is checked against a case whose answer is known by hand.  For
\(E = \langle e_a, x_b\rangle \subset \Lambda_2\) the perpendicular is
\(\langle e_a, x_b\rangle \perp E_8(-1)^2 \perp \langle -2\rangle\), so
\(Q = E_8(-1)^2 \perp \langle-2\rangle\); the routine returns exactly that Gram matrix
(bit-identical, det \(-2\)).

**Correction.** Batch 2's finding stands but its lattice must be stated exactly: the
card's lattice has *unimodular* \(E_8\) summands.  A probe that used the scaled block
\(2E_8\) instead produced quotients of determinant \(-131072\) and a rank-21 lattice of
signature \((18,3)\), which is not \(\Lambda_{2k}\); nothing measured on that
construction is a statement about the card.

### The bounded search is incomplete, and says so

Candidates \(e = \alpha x + \beta y + w_1 + w_2 + t z\) of
\(K = v^\perp/\langle v\rangle = U \perp E_8(-2)^2 \perp \langle-2k\rangle\) with
\(q(e)=0\), i.e. \(2\alpha\beta = n_1 + n_2 + 2k t^2\) over every factorisation, E8
block norms \(0, 2, 4, 6\), \(t \le 3\), 1200 shapes:

```
k = 1: 3 classes  (|Aut| 1941728542064640000, 5393690394624000, 1371195958099968000)
       sum 1/|Aut| = 103651/555334363030487040000  <  mass      INCOMPLETE
       missing the class of |Aut| = 12804747411456000
k = 2: 5 classes  (|Aut| 1941728542064640000, 129448569470976000, 809053559193600,
                   1371195958099968000, 106542032486400)
       sum 1/|Aut| = 5903731/555334363030487040000 <  mass       INCOMPLETE
```

Every quotient found has determinant \(\pm 2k\): one genus, as the fixture states, so
the mass is the right certificate and the shortfall is a statement about the search,
not about the theory.  The mass check refuses to report a complete family, which is
the honest outcome; the four and nine plane rows are **not** reproduced.

Two consequences for whoever continues:

- the search must be closed, not widened: the plane classes are the classes of a
  genus of class number 4 (measured) and 9, so a search that reaches the class number
  is complete by the mass, and one that does not must raise.  The missing candidates
  are presumably those whose \(E_8\) parts are not both from the low shells: the
  \(k=1\) class of `|Aut| = 12804747411456000` was reached by the *genus* traversal at
  \(p=3\) and by no shape tried here, which names it as the shape to find.
- cost per class decision is dominated by `qfisom` when two classes share `|Aut|`
  (minutes, unbounded).  A class test that is exact and cheap at rank 17 is the
  missing capability, not a faster search.

## Item 2, `029J` row `gamma-en-2`: the group is the right one and is built; the orbit call does not return

The construction in the handoff is the library's own and it works:

```
Involutions.I_En.invariant_lattice()                  rank 10, det -1024, signature (1,9)  0.2 s
  isotropic generator pairs with nonzero pairing       only (gen 0, gen 1), b = 2
  h = gen 0 + gen 1:  q(h) = 4, primitive              = e_ep + e_fp, degree 2
Involutions.I_En.polarized(h).coinvariant_extension_subgroup()                    24.0 s
  contains_character_kernel()                         True
  character_data_is_complete()                        True
  finite_character_quotient()                         0.0 s
  image_order()                                       46998591897600   80.3 s   (= |O(q)| of the issue)
  subgroup_image_order()                              696729600         0.1 s   (= |W(E8)|)
  [O(q) : rho(Gamma)]                                 67456             0.0 s
Gamma.isotropic_orbit_representatives(1)              did not return in 1500 s (exit 124)
```

So `Gamma_{En,2}` is a complete character kernel in `O(T_En)` with the discriminant
image the handoff predicts, and the eight-parameter row now has a constructed group
whose image order is exactly the `|O(q)|` the issue quotes.  The stop is downstream:
splitting the two `O(T_En)` line orbits into `Gamma`-orbits goes through
`splitting_isometries_from_line_class` → `_splitting_isometries_in_im_rho_from_image`,
which asks libGAP for `IsomorphismPermGroup` and `DoubleCosets` of a finite group of
order 46998591897600.  Neither the line row (5) nor the plane row (9) is produced.

The reformulation to take next, and it is not a new algorithm: the same method's own
hypothesis -- `isotropic_line_stabilizer_image` certifies
`rho(Stab_{O(L)}(v)) = Stab_{O(q)}(c)` -- makes the double cosets
`rho(Gamma) \ O(q) / Stab(c)` the `rho(Gamma)`-orbits on the `O(q)`-orbit of `c`, which
is the set of isotropic classes of \(A_{T_{\mathrm{En}}}\) up to sign: 265 pairs, all
of them small.  That set is enumerated by `covering_discriminant_classes(0)` and acted
on by the images of `discriminant_generator_lifts()`, so the count is a finite
permutation-group computation on 265 points rather than a coset enumeration in a group
of order \(4.7\times10^{13}\).

## Acceptance build

No test module is touched in this batch, so the touched-module build is unchanged from
`5570c5952e`, and the two comparisons the brief asks for are **not delivered**.  The
existing `029J` `O` row module was re-run on this tree as a regression check, with the
port bound at `/work` and `/work/src` ahead on `PYTHONPATH`:

```
tests/lattices/test_unpolarized_enriques_strata.sage   2 passed in 61.61 s   (gate ON)
  lines: 38.75 s > 20 s      planes: 22.54 s > 20 s          session exits red on cost
same module with --no-time-gates                       2 passed in 66.14 s   (exit 0)
```

so the two `029J` `O`-row comparisons still agree and the gate is red on the same
per-call cost that batch 1 recorded, not on a disagreement.  Two setup facts, both
re-measured here, since each costs a run: without `-b <port>:/work` the module fails in
`recursive.py:154` with the port's `TypeError` on an owned coordinate, and binding the
port without putting `/work/src` ahead on `PYTHONPATH` imports the image's port copy and
fails the same way.  That failure is a setup artefact (already recorded in `TRAPS.md`),
not a finding about the row.

## Measurements that did not survive scrutiny

- the probe lattice `U^2 + (2E_8)^2 + <-2k>` (scaled E8 blocks) is not \(\Lambda_{2k}\);
  its quotients have determinant \(-131072\) and it has signature \((18,3)\).  Every
  reading from it is discarded above.
- `QuadraticForm.automorphism_group().order()` is not a usable measurement at rank 17:
  it hangs where `number_of_automorphisms()` takes 0.3 s.
