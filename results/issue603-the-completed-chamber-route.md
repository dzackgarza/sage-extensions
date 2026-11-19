# #603: the divisibility-two row, and the proper-image lemma that remains

## Scope

This note records two separate outcomes. It does not close #603 for every
primitive isotropic vector.

* the rank-zero Levi image at the smallest divisibility-two specimen is now
  computable;
* the divisibility-two cusp `L_2 = Ze_3` of card `029J` now has a public
  pointed generating family, with its discriminant image certified against the
  card;
* a general presentation of a **proper** Levi image as a point stabilizer over
  lift-torsor residues was not needed for that cusp and is not implemented.

The previous rank-two fixed-part argument remains false: fixing `v` does not
fix `<v,w> + K~`, because the unipotent shift moves `w` by an element of
`v^perp`.

## The red, at the smallest lattice

On `U(2)` the first basis vector is primitive isotropic of divisibility two and
`K_I = 0`.  At `4d34c434`,

    reduction.pointwise_levi_image().cardinality()

raised `ZeroDivisionError` in `_definite_automorphisms`, which normalized the
empty Gram matrix by `gcd(0)` (1 failed in 1.47 s).  The empty form now returns
order one and no generators, and the generated subgroup at rank zero is the
trivial subgroup of the one-dimensional matrix group, avoiding Sage's refusal
to construct a degree-zero matrix group.  The red is
`tests/lattices/test_the_zero_reductions_pointwise_levi_image.sage`, commit
`7b1d758`; the repair is `6891f78`.

This is a defect of the Levi computation, not an invented red for the pointed
vector call, whose separate rank-zero branch already returned the empty family.

## The red at 029J

`tests/lattices/the_enriques_pointed_stabilizer_row.py` now requires a pointed
family at both cusps and, with `-id`, computes each line-stabilizer image index
from that family itself.  The row was widened at `78b8770` and its harness
corrected at `a6b5323`.

At `2126fac`, the row printed

    L_1: 1 ker-rho orbits in its O(N)-orbit, 3.9 s
    L_2: 527 ker-rho orbits in its O(N)-orbit, 103.4 s
    pointed family at L_1 = Ze_1: 36 generators, 11.8 s
    L_1: pointed family's line-stabilizer image index 1

and the run was killed at 400 s while still inside `L_2`'s pointed call.  Thus
the independent card comparison was already green but the public pointed
family at `L_2` was still red by non-return, not by a weaker timing assertion.
This row is in the rows tier and is not collected by pytest.

## What the construction uses

1. **Parabolic and Levi map.** For `I = Zv`, `P_I = Stab_{O(L)}(I)`, with
   `P_I^1 = Stab_{O(L)}(v)`.  The descent `lambda: P_I -> O(K_I)`,
   `K_I = I^perp/I`, is the quotient block of an isometry preserving a
   primitive isotropic sublattice (Dutour Sikiric--Hulek,
   arXiv:2302.01679v2, Theorem 4.9, printed pp. 33--34).  A vector in the
   pointed parabolic fixes `v` exactly, not up to sign.
2. **Unipotent kernel and lifts.** The unipotent radical is the kernel of
   `lambda`; the Levi quotient and its split over a field are Zemel,
   arXiv:1902.08264v2, Proposition 1.6, printed p. 10.  Integral lift
   candidates form marked-line torsors, evaluated by Eichler transvections
   (Gritsenko--Hulek--Sankaran, arXiv:0810.1614v1, section 3.1, equation (4)
   on printed p. 8 and the additive composition law (5) on printed p. 9).
   The library's finite parameter-residue locus decides whether an integral
   pointwise lift exists.
3. **A generating family for the quotient group.** Allcock's completed
   edgewalk supplies the wall reflections of the full reflection group `W(K_I)`
   and generators of the chamber-symmetry group.  They generate `O(K_I)`:
   `W(K_I)` is normal because conjugation permutes integral root reflections;
   an isometry takes the chamber to a chamber; an element of `W(K_I)` brings
   that image back, so its product with the original isometry is a chamber
   symmetry.  This is the content of Vinberg's normalizer factorization, cited
   as Belolipetsky, arXiv:1506.03111v4, Lemma 2.3, printed p. 7.  A
   nonreflective report declines; it never substitutes a reflection subgroup
   for `O(K_I)`.
4. **The target's Levi image is full.** At `029J`'s `L_2`, all ten wall
   reflections of `K_I = U + E8(-2)` have integral pointwise lifts.  (The first
   six were measured in 200.93 s; the remaining four in 145.10 s, excluding
   setup.)  Since the completed chamber and these lifts cover a generating
   family of `O(K_I)`, `M_I^1 = O(K_I)` here.  Consequently the Schreier
   pointed-parabolic family can be used directly: one lift of each quotient
   generator, together with the unipotent kernel and the two-coset Schreier
   correction for `P_I/P_I^1` (Seress, *Permutation Group Algorithms*, Lemma
   4.2.1, printed p. 57).

## What is green

At `ce9b63e`, the whole row completed:

    pointed family at L_1 = Ze_1: 31 generators, 9.5 s
    L_1: pointed family's line-stabilizer image index 1
    pointed family at L_2 = Ze_3: 541 generators, 320.6 s
    L_2: pointed family's line-stabilizer image index 527
    probe exit: 0

After rebase, the independent `L_2` probe alone completed at `d9768dc`:

    family 541 time 273.8913113169838
    index 527 card (1, 527) time 296.2728541070246
    probe exit: 0

The current source and test blobs are byte-identical to those at `d9768dc`
(`git diff --quiet` on all touched files).  Another run under heavy load was
killed at 520 s without printing a family and is not counted as evidence in
either direction.

The established small files are 11 passed in 15.97 s with time gates on.  The
zero-reduction file and its four pointwise-Levi neighbours were 5 passed in
2.49 s.  The adopted port revision is
`991b88b095a42a1e3679569ea42328c900c120f6`.

## Acceptance, item by item

* **Zero-rank Levi computation at the smallest divisibility-two lattice:**
  MET.
* **Public pointed family at divisibility two on `029J`'s `L_2`:** MET, and
  its discriminant-image index with `-id` is the card's 527, not merely the
  index computed by the independent finite-image route.
* **Library-owned generation in the submitted case:** MET by the completed
  chamber, the ten integral pointwise lifts, the parabolic exact sequence and
  Schreier's lemma.  No ambient `O(K_I)` answer from the indefinite port is
  used on this path.
* **Every primitive isotropic vector of divisibility greater than one:** NOT
  CLAIMED.  In particular no chamber-symmetry result is transferred to a
  lattice that did not produce a completed chamber, and no generation result
  is inferred from the card alone.
* **The research `T_Co` cusp-5 computation:** NOT RUN here.

## The precise remaining lemma

Let `L` be even over `ZZ`, `v` primitive isotropic, `K = v^perp/Zv`, and let
`lambda` be the Levi map. Suppose `M = lambda(P_v^1)` is **proper** in `O(K)`.
What is not implemented is an explicit finite `O(K)`-set `X` of residues of the
integral lift torsors such that

    M = Stab_{O(K)}(x_M)

for a named point `x_M in X`.  Given such an action, Schreier's lemma returns
generators of `M`; one integral pointwise lift of each, together with the
integral kernel generators of the identity lift torsor, then generates `P_v^1`.
The exact sequence supplies the final equality, but it does not construct `X`
or prove that its stabilizer is `M`.  In the `029J` cusp above `M = O(K)`, so
this additional lemma is not needed.

## Not run

No full suite, no `just test`, no ast-grep gates (ast-grep is not installed),
and no `T_Co` run.  The older `test_edgewalk_fundamental_domain.sage` does not
collect because of its own pre-existing TL09 finding; its K3 option tests were
therefore not part of the evidence.  The default edgewalk calls used by the
repair were measured directly and returned reflectivity certificates in about
one to three seconds on the target reductions.
