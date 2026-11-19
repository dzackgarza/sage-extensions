# #603: the divisibility-two row and the proper Levi image

## Scope

This note records the divisibility-two outcomes. It does not close #603 for
every primitive isotropic vector.

* the rank-zero Levi image at the smallest divisibility-two specimen is now
  computable;
* the divisibility-two cusp `L_2 = Ze_3` of card `029J` now has a public
  pointed generating family, with its discriminant image certified against the
  card;
* a proper Levi image now has a pointwise integral-structure action with
  generators over its finite residue module, without the port's marked-lattice
  entry.

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

## The proper-image branch

The rank-five lattice

    [[0, 2, 0, 0, 0], [2, 0, 1, 0, 0], [0, 1, 0, 2, 0],
     [0, 0, 2, 0, 0], [0, 0, 0, 0, -2]]

has a primitive isotropic first generator of divisibility two with reduction
`U(2) + <-2>`.  One certified generator of `O(K_I)` has no integral pointwise
lift, so `M_I` is proper.

`PrimitiveIsotropicSubobjects.pointed_stabilizer_action` now builds the
pointwise action at that owner: rational lifts of the certified `O(K_I)`
generators, the same lifts sheared along the isotropic line, and the pointwise
kernel at the common lift denominator.  Its stable containing module is the
orbit span of the explicitly bounded residue module, and
`IntegralStructureAction` returns the stabilizer as the preimage of a point
stabilizer in that finite module.  `pointed_stabilizer_generators` reads that
stabilizer back into `O(L)` and checks that every member fixes `v`.

The existing public family was already correct on this specimen; there was no
value red to write.  The new regression test therefore records the proper
branch rather than manufacturing a failure:
`test_a_proper_pointwise_levi_image_still_has_the_full_finite_image` passed in
4.83 s, with ten tests deselected.  It asserts that one chamber generator
lacks a pointwise lift, at least one has one, and that both the owned family and
the public pointed call generate the same finite image as the liftable
chamber generators.

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
* **Proper Levi image, point stabilizer over finite residues:** MET for the
  even integral case with an available `O(K_I)` family.  The owned action and
  its rank-five regression are described in “The proper-image branch.”
* **Every primitive isotropic vector of divisibility greater than one:** MET,
  for the radical and for the public pointed family alike.  The radical's
  parameter lattice is `X`, the item below; the public family is answered by
  the residue action, whose group now contains `U_I`, so it no longer depends
  on the lifting torsor's even-lattice case and no parity gate remains.
  `029J`'s `L_2` keeps the card row it was certified on, and an odd lattice of
  divisibility greater than one is answered by the owned route rather than by
  the port.
* **The integral kernel of the pointwise parabolic at a line of every
  divisibility:** MET.  With `d` the divisibility of `e`, a partner `w` of
  `b(e,w) = d` and `J = I^\perp`, the radical is the image of the parameter
  lattice
  `X = {u in J : b(u,J) <= dZ, u in L, b(u,u) + 2b(w,u) in 2dZ}` under
  `u |-> E_{e,u/d}`, with kernel `Z e`; the pairing in the third condition is
  additive modulo `2d` there, so `X` is a lattice, and it is cut out by one
  Smith normal form of the Gram matrix of `J` followed by one congruence.  At
  `d = 1` it is the even part of `J`, so this is the same family as before and
  not a second construction.  Asserted on `U(2) + <2>`, `U(3) + <3>` and
  `U(2) + <2> + <2>`
  (`tests/lattices/test_the_pointwise_radical_of_a_divisible_isotropic_line.sage`),
  which were `3 failed in 9.91 s` at `c6cd4e1` on the refusal this replaces and
  are `3 passed in 7.94 s` on the repair.
* **The integral kernel of the pointwise parabolic at a line of divisibility
  one, odd lattices included:** MET.  The radical is the Eichler transvections
  at the even-square parameters, exact on an odd lattice and on an even one
  whose `K_I` is not unimodular, and both factors of the exact sequence are
  computable on the nonreflective odd specimen.  See “The nonreflective
  quotient.”  The higher-divisibility case is the item above, which replaces
  this one's parameters by `X`.
* **The public pointed family at an odd lattice of any divisibility:** MET.
  The residue action's rational group is the lifts of `O(K_I)`'s generators
  together with the pointwise Levi kernel `U_I`, so it is exactly `P_I^1` and
  its integral stabilizer is exactly `P_I^1`; the gate that answered an odd
  lattice with `None` is gone.  `U(2) + <3>` and `U(3) + <3>` answer in 1.09 s
  and 0.31 s
  (`tests/lattices/test_the_public_pointed_family_of_a_divisible_odd_line.sage`;
  the same calls went to the port at 16.29 s before).
  *Correction to the earlier items of this list:* the residue action's group
  omitted the radical at **every** divisibility and parity, not only at the
  odd case — the perpendicular kernel it used is trivial at a line — so the
  families the card rows were certified on generated proper subgroups of
  `P_I^1`.  The card values are finite-image statements and stand; the
  families did not, and they do now.
* **The research `T_Co` cusp-5 computation:** MET.  Sterk's fifth cusp
  vector is primitive isotropic of divisibility two in `T_Co`; the public
  pointed call returned 25 generators in 12.65 s including setup, and every
  generator fixes it.  The parent had not returned at 520 s.

## The proper-image construction

Let `L` be even over `ZZ`, `v` primitive isotropic, `K = v^perp/Zv`, and let
`lambda` be the Levi map. For a proper `M = lambda(P_v^1)`, the action built at
`pointed_stabilizer_action` has stabilizer `P_v^1`: its rational generators are
one lift of each certified generator of `O(K)` and the pointwise kernel at the
common lift denominator, and its finite module is the orbit span of the residue
bound `2 d^2 |disc(K)|^2 [L : i^*(L)]`.  `IntegralStructureAction` cuts the
stabilizer out as a point stabilizer in that module, so its ordered Schreier
family generates `P_v^1`.  The remaining limitation is input availability, not
this construction: an `O(K)` family must be supplied, and the completed
chamber supplies it only for a reflective hyperbolic `K`.

## The nonreflective quotient

The remaining universal case is a nonreflective `K_I`.  The decisive small
specimen is

    L = U + K,   K = NamedLattices.BogachevKolpakovNonReflective,

with `L` of signature `(2, 3)` and the pointed vector `e` the first generator of
the `U` summand.  Here `K` has signature `(1, 2)`, `e` is primitive isotropic
of divisibility one, and `K` is nonreflective: the edgewalk answers `False` in
7.18 s.  The quotient is not the obstruction to having generators — the port's
`O(K)` call returns 12 generators in 10.63 s.

What does not return is the pointwise finite-residue action: on this `L`,
`subobject.pointed_stabilizer_generators()` was still running at 520 s at
1.08 GiB, and the public port fallback did not return at 120 s.  This is a cost
bound, not a demonstrated absent family.  The residue bound
`2 d^2 |disc(K_I)|^2 [L : i^*(L)]` is valid but its orbit span is too large to
enumerate here.

The narrow supported cases are already handled: on each of the two
Bogachev--Kolpakov nonreflective lattices themselves, an `isotropic_vector()`
has rank-one reduction; the owned action returns 28 generators in 4.38 s and
56 in 31.01 s respectively, all fixing the vector.

**Residual requirement, sharpened again.**  Enumerating all 112 classes of
`O(A_K)` and deciding each by the rational extension's integral restriction
shows that **all 112 lift**: the liftable subgroup is the whole finite quotient,
in 6.63 s.  Therefore `M_I = O(K_I)` on this specimen.  The Levi image is not
the obstruction.

What remains is the integral unipotent kernel for an **odd** lattice.  The
existing marked-line lift torsor refuses an odd target by an explicit evenness
assertion, while the rational pointwise action exists and its residue span is
too large to enumerate (520 s at 1.08 GiB).

**That lemma is now proved and implemented, at divisibility one.**  The
statement as sharpened there is not the right one: `b(x,J) subset ZZ` is
automatic for `x in J`, and the second condition is the parameter's own
`q(x) even`, not a condition on `b(v,y)`.

> `U_I = ker(P_I^1 -> O(K_I))` is `{E_{e,x} : x in P} / (E_{e,x} = 1 for
> x in Z e)`, where `P = {x in I^perp : q(x) in 2 ZZ}`.

* `q(x)/2` is the only coefficient of `E_{e,x}` outside `ZZ`
  (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, (4), printed p. 8), so the
  integral transvections are exactly the parameters of even square: all of
  `I^perp` on an even lattice, an index-two sublattice on an odd one.
* Completing `e` to `e, w` with `J = I^perp = Z e + Z w` and `b(e,w) = 1`,
  an element of `U_I` sends `y in J` to `y + c(y) e` and `w` to `w + z` with
  `z in J`; the isometry equations are `c(y) = -b(y,z)` and
  `b(z,z) + 2b(w,z) = 0`, and `x = z + lambda e` has `E_{e,x} = g`.  So the
  assignment is onto and `P / Z e` is the radical, of rank `rank K_I`.  The
  parameters are `P`; `Hom(K_I, ZZ)` and `K_I` are both wrong containers, and
  a non-unimodular `K_I` (where they differ by `|disc K_I|`) is not an
  obstruction.
* Independence of `K_I` being unimodular, and of the lattice being even, is
  asserted on `U + <2> + <2>` (even, `disc K_I = 4`, radical of rank two) and
  on `U + <3>` and `U + BK_nonref` (odd), in
  `tests/lattices/test_the_pointwise_radical_of_a_primitive_isotropic_line.sage`.

The other factor is the section.  When the chosen lifts of `K_I` span a
primitive `K'` whose `M = K'^perp` is unimodular, `L = M + K'`,
`id_M + sigma` is an integral isometry for every `sigma in O(K_I)`, and `M`
contains the marked line, so `M_I = O(K_I)` and the section needs no residue
orbit.  That is `_reduction_lift_splitting`, which `lift_isometry` and the new
pointwise section both read; where the lattice does not split, the marked-line
torsor keeps deciding emptiness from the finite residue locus.

Measured on the adopted port revision `991b88b0`, at
`L = U + BK_nonref` (rank 5, signature (2,3), odd, `disc 2401`, marked vector
of divisibility one):

| step | result | time |
|---|---|---|
| `O(K_I)` family | 13 generators | 2.43 s |
| `id_M + sigma` for all 13 | integral, fixing `v`, right Levi class | 0.61 s |
| `\|rho(O(K_I))\|` | 112 | (in the same run) |
| the radical's parameters | 4, rank 3 after `Z e` | 0.08 s |

The new test file is `4 passed in 9.45 s` on the repair and `4 failed in
9.56 s` at `8fe6b05`; its slowest call is 2.19 s and its fastest 0.06 s.
`tests/lattices/test_pointwise_levi_images.sage`, the consumer of
`pointwise_levi_lift` and `unipotent_kernel`, is `4 passed in 6.78 s`.  Both
runs are with `--no-time-gates`; collection took 6.50 s against the 6 s
ceiling in the repair's worktree before and after the change, which is the
pre-existing overrun of that tree and not this line's.

**Still open after this.**  Nothing on the acceptance list.  What is open
beside it: the witness that would decide the residue action's exactness from
outside -- whether a generator of `U_I` lies in the action's stabilizer -- is
not askable, because an integral isometry is not coerced into the action's
rational group; measured, it answers `False` in both directions and even for
an element that is one of that group's generators.  And the plane case,
`U_I` at null rank two and up, still carries the parameter-lattice question
recorded above.

No full suite, no `just test`, no ast-grep gates (ast-grep is not installed).
The older `test_edgewalk_fundamental_domain.sage` does not
collect because of its own pre-existing TL09 finding; its K3 option tests were
therefore not part of the evidence.  The default edgewalk calls used by the
repair were measured directly and returned reflectivity certificates in about
one to three seconds on the target reductions.

## The list at `a7632ba`, item by item

Every acceptance item is met.  Each is anchored here at that commit: the site
that does the work, and the test that asserts it.

| item | the site | the test |
|---|---|---|
| Zero-rank Levi computation at the smallest divisibility-two lattice | `lattice_morphisms.py:3418` (`_definite_automorphisms`, whose zero-content guard returns the order `1` and no generators) and `:4688` (`_engine_subgroup_from_generators`, the rank-zero trivial subgroup) | `test_the_zero_reductions_pointwise_levi_image.sage:13` |
| Public pointed family at `029J`'s `L_2`, its discriminant image of index 527 | `isotropic_parabolics.py:1168` (`pointed_stabilizer_generators`) over the action at `:202` | `tests/lattices/the_enriques_pointed_stabilizer_row.py:65` |
| Library-owned generation in the submitted case, by the completed chamber | `lattice_morphisms.py:4736` (`_computed_group_generators`) with `hyperbolic_lattices.py:2229` and `:2252` (the edgewalk call) | the row script above, on the chamber's own generators; citation Belolipetsky, arXiv:1506.03111v4, Lemma 2.3, printed p. 7 |
| Proper Levi image, point stabilizer over finite residues | `isotropic_parabolics.py:202` | `test_the_pointed_stabilizer_of_a_primitive_vector.sage:251` |
| The research `T_Co` cusp-5 computation | `isotropic_parabolics.py:1168` | `test_the_pointed_stabilizer_of_a_primitive_vector.sage:303` |
| Integral kernel of the pointwise parabolic at a line of every divisibility | `lattices.py:13492` (the family), `:13613` (the parameter lattice), `:13704` (the transvection at a rational parameter), `:13565` (the Bezout partner) | `test_the_pointwise_radical_of_a_divisible_isotropic_line.sage:80`, `:85`, `:90`, and at divisibility one `test_the_pointwise_radical_of_a_primitive_isotropic_line.sage:59`, `:96`, `:116`, `:142` |
| Public pointed family at an odd splitting lattice | `isotropic_parabolics.py:1168` with `:311` (the kernel in the rational group) | `test_the_public_pointed_family_of_an_odd_isotropic_vector.sage:89`, `:108` |
| Public pointed family at an odd lattice of any divisibility | `lattices.py:3027` and `:3089` (no parity gate remains); `isotropic_parabolics.py:202`, `:311` | `test_the_public_pointed_family_of_a_divisible_odd_line.sage:58`, `:63` |

Two things are open *beside* the list, and neither is an acceptance item: the
coercion that would let one ask whether an integral isometry lies in the
residue action's rational group -- it answers `False` in both directions and
even for an element that is one of that group's generators -- and the plane
case's parameter lattice at null rank two and up.

## Withdrawal: the residue action's exactness

The claim that `_pointed_stabilizer_action`'s rational group *is* `P_I^1`, and
that its integral stabilizer is therefore `P_I^1`, is **withdrawn**.  Its
rational generators are one rational lift `g~_i` of each generator of `O(K_I)`
together with `U_I`'s integral generators, and a `g` in `P_I^1` lies in the
group they generate only when the correction `g w^{-1} -- w` being the word in
the `g~_i` whose Levi class is `lambda(g)` -- is integral.  That is not shown
and fails in general: a word in rational lifts is a rational isometry, and
nothing in the construction makes it integral.  The withdrawn argument read a
`QQ`-linear span for a generated group, which is the step that does not follow.

Everything that rested on it therefore returns to NOT MET:

* the public pointed family at `029J`'s `L_2`: its finite discriminant image is
  checked, and that does not certify generation of the discriminant kernel;
* the proper Levi image: the action lifts generators of *all* of `O(K_I`) while
  the claim is about `M_I`, and filtering `O(K_I)`'s generators need not
  generate `M_I`;
* the odd splitting lattice as a *library-owned* claim: the split extension is
  exact, but its `O(K_I)` input is the port's for indefinite `K`, and the test
  compares against that same family;
* the odd lattice of any divisibility;
* `T_Co`'s cusp 5, whose test asserts only that the family is non-empty and
  fixes its vector.

What stands is what never rested on that argument: the zero-rank computation,
the line kernel at every divisibility (a self-contained block computation over
`ZZ`), and the chamber's quotient family as the narrower claim about `O(K_I)`,
with the same caveat about its input.

## The non-isotropic line: the first NOT MET item, as one lemma

**Lemma.**  Let `L` be a nondegenerate integral lattice over `ZZ`, `v` in `L`
primitive with `b(v,v) != 0`, `K = v^\perp \cap L`, `L_0 = Z v \perp K` and
`H = L/L_0`, read as a subgroup of `A_{L_0} = L_0^\#/L_0`.  Then

    Stab_{O(L)}(v) = { sigma in O(K) : (1 \oplus sigma)(H) = H },

the map being `sigma |-> (1 \oplus sigma)|_L`, and the Schreier family over the
orbit of `H` under `O(K)` generates that group.  No parity hypothesis appears.

**Proof.**  `L_0` has finite index in `L`: every `x` in `L` is
`(b(x,v)/b(v,v)) v + k` with `k` in `K` over `QQ`, so `L/L_0` is cyclic, of
order `|b(v,v)|/d` with `d` the divisibility of `b(-,v) -- dividing
`|b(v,v)|`, not equal to it in general.

(i) `1 \oplus sigma` is an isometry of the orthogonal direct sum
`L_0 = <v> \perp K`; it preserves `L_0^\#` because it preserves `L_0`, hence
acts on `A_{L_0}`; and `L = \pi^{-1}(H)` under `\pi: L_0^\# \to A_{L_0}` gives
`(1 \oplus sigma)(L) = L` exactly when `(1 \oplus sigma)(H) = H`.
(ii) `sigma |-> (1 \oplus sigma)|_L` is a bijection onto `Stab_{O(L)}(v)`:
injective because the extension determines `sigma`, surjective because an
isometry of `L` fixing `v` preserves `K = v^\perp \cap L` and agrees on the
finite-index sublattice `L_0`.
(iii) For a group acting on a set, the stabilizer of a point is generated by
the words `w_{tP}^{-1} t w_P` over a spanning tree of the orbit: each fixes the
point, and a word fixing the point can be rewritten through the transversal at
every step into such words.

**Sources.**  None are quoted, and the three steps above are the whole proof:
the only overlattice involved is `L` itself, so the correspondence is the
definition of `H`.  Nikulin's Proposition 1.4.1 is therefore not cited, and no
printed page is claimed for it -- this workspace's sources hold no copy of
Nikulin.

**Consequence, and what it repaired.**  The evenness gate at `lattices.py:3079`
refused every odd lattice at a non-isotropic vector and sent it to the port;
it is removed.  `U + <3>` at its norm-three vector and the disc-three specimen
`<x,k> = [[1,-1],[-1,-2]]` at `v = 2x - k` are answered by this construction,
the second with `b(v,v) = 6`, `K = <-2>`, `[L : Zv + K] = 2` and stabilizer of
order two
(`tests/lattices/test_the_pointed_stabilizer_of_an_odd_nonsingular_vector.sage`;
`2 passed in 15.15 s`, and the pre-existing
`test_a_nonsingular_vector_in_an_odd_lattice_is_answered_here` still passes on
the owned route).  No red is claimed: the port answers these specimens too
(`U + <3>` in 0.80 s, `U + <3> + <3>` in 0.69 s), so what changed is which
construction answers, and that is not observable from the answer.

## The correction lemma: integrality is a coset of the radical

The withdrawn argument needed exactly one step, and it is a lemma about the
kernel the earlier turns built.

**Lemma.**  Let `L` be an integral lattice over `ZZ` of any parity, `v` a
primitive isotropic vector of divisibility `d`, `J = v^\perp`, `w` a partner
with `b(v,w) = d`, and

    X = {u in J : b(u,J) <= d ZZ,  q(u) + 2 b(w,u) in 2d ZZ},

which is the parameter lattice of the radical: `E_{v,u}` is an integral
isometry exactly for `u` in `X`, and `u |-> E_{v,u}` kills exactly `Z v`.
Then for any `g~` in `O(L \otimes QQ)` with `g~(v) = v`, if
`g~ E_{v,x_0}` is integral for one `x_0` then `g~ E_{v,x}` is integral for
every `x` in `x_0 + X`; and if `x_1`, `x_2` are both admissible then
`x_1 - x_2` lies in `X`.  So the admissible parameters are empty or one coset
of `X`.

**Proof.**  `E_{v,x_0+u} = E_{v,x_0} E_{v,u}` is the composition law
`E_{v,x} E_{v,y} = E_{v,x+y}` of Gritsenko--Hulek--Sankaran,
arXiv:0810.1614, section 3.1, equation (5), printed p. 9; `E_{v,u}` is an
integral isometry of `L` for `u` in `X` by equation (4) there, printed p. 8,
which is the integrality computation `X` is defined by; so the product is
integral.  Conversely `E_{v,x_1} E_{v,x_2}^{-1} = E_{v,x_1-x_2}` is integral
by the same two equations with `x_2` replaced by `-x_2`, so `x_1 - x_2` is a
parameter of an integral transvection, which is `X`.

**Code.**  `_corrected_pointwise_levi_lift` (`lattices.py`) tries one
representative per class of `(1/N) J` modulo `X`, `N` the divisibility times
the rational lift's denominator, and decides each by the exact restriction of
the corrected rational isometry to `L`; it runs after the split section and
before the marked-line torsor, which stays as the fallback.  The red is the
torsor's evenness assertion: the two odd divisible lines were
`2 failed in 9.27 s` at `999c928` on `isotropic_lifts.py:525`, and are
`2 passed in 6.65 s` with the correction
(`tests/lattices/test_the_pointwise_levi_lift_of_an_odd_line.sage`).  At
`T_Co`'s fifth cusp the public pointed call is 4.89 s against 4.40 s before,
and the first three of its nine `O(K_I)` generators lift integrally in 0.08 s
each, so the search is cheap at rank eleven.

**What it does not do.**  It decides the lift; it does not assemble the
pointed family from integral lifts.  That needs generators of `M_I`, and the
liftability predicate cuts `M_I` out of `O(K_I)` without producing a
generating set of it -- a filtered generating set of `O(K_I)` need not
generate `M_I`.  That is the next question, not this lemma's.

## $M_I$'s generators: the reduction, and a refutation of the filtering route

**Lemma (reduction).**  For a family `{g_s}` of integral lifts of a set
`S <= M_I`, `\langle g_s \rangle . U_I = P` if and only if
`\langle S \rangle = M_I`.

**Proof.**  `lambda` carries `\langle g_s \rangle . U_I` onto
`\langle S \rangle` with kernel `U_I`; it carries `P` onto `M_I` with the same
kernel.  Two subgroups with the same image and the same kernel under one
homomorphism coincide.

So the pointed family is exact exactly when the lifted set generates `M_I`,
and the question is `M_I`'s generators -- not the family's assembly.

**Refutation of the filtering route.**  The liftability predicate decides
membership in `M_I`; it does not produce a generating set, and the only route
it offers -- take a generating set of `O(K_I)` and keep what lifts -- is not a
theorem about `M_I`: for `O(K_I) = (Z/2)^2 = \langle a, b \rangle` and `M_I`
the diagonal `\langle ab \rangle`, both `a` and `b` lie outside `M_I` while
their product lies in it, so the filtered set is empty and generates the
trivial group.  Two further observations from the specimens:

* the rank-five proper-image specimen (`L` of rank five, signature (2,3),
  `K_I` of rank three and discriminant `-8`, infinite `O(K_I)`) has three
  generators, of which two lift and one does not, so filtering *does* leave
  generators there -- it is the general statement that fails, not that
  specimen;
* a second generating set cannot be manufactured by translating the first:
  for a liftable `t` the set `{s t}` needs `t^{-1}` in its span to generate,
  and it need not, which the same specimen shows
  (`\langle s t \rangle != O(K_I)`, measured).

Whether a lattice realizes the `(Z/2)^2` pair is open and is not claimed.

**The next lemma, stated but not proved.**  `M_I` contains a principal
congruence subgroup of `O(K_I)` at an explicit modulus `m` built from the
divisibility, the lift denominators and the discriminant of `K_I`.  If it
holds, `M_I` has finite index, its generators are one lift per generator of
the finite subgroup `M_I/m` together with generators of the congruence kernel,
and the five withdrawn items can be re-argued on that basis.  The step that
is missing is that a `\tau` congruent to the identity at `m` has a *rational*
lift of denominator dividing `m`, hence a correctable one -- plausible from
the correction lemma's bound and not established.

## The congruence lemma, proved: `Gamma_{K_I}(d)` lies in `M_I`

The lemma stated above is true with `m = d`, and the lift is a formula rather
than a search.  Fix `J = v^\perp`, a partner `w` with `b(v,w) = d`, and
`J = Z v \perp K'` with `K'` spanned by the lifts `kappa_i` of `K_I`'s frame --
orthogonal, since `v` is orthogonal to `J`.  For `tau` in `O(K_I)` write
`tau^\sharp` for the isometry of `J` that fixes `v` and acts as `tau` on `K'`.

**Lemma.**  If `tau` is congruent to the identity modulo `d`, then

    g(v) = v,  g(kappa_i) = tau^\sharp(kappa_i) + c_i v,  g(w) = w,
    c_i = b(w, kappa_i - tau^\sharp(kappa_i)) / d

is an integral isometry of `L` with `g(v) = v` and `lambda(g) = tau`.

**Proof.**  `kappa_i - tau^\sharp(kappa_i)` lies in `d J` because `tau` is the
identity modulo `d` on the frame, and `b(w, J)` lies in `ZZ`, so `c_i` is an
integer.  `g` is `ZZ`-linear on the basis `(v, kappa_i, w)` of `L`, hence
integral.  It preserves the pairings of that basis: `(v,v)`, `(v,kappa_i)` and
`(v,w)` because `tau^\sharp` fixes `v` and `b(v, J) = 0`; `(kappa_i,kappa_j)`
because `tau^\sharp` is an isometry of `J`; `(w,w)` because `w` is fixed; and

    b(g kappa_i, g w) = b(tau^\sharp kappa_i, w) + c_i d = b(kappa_i, w)

by the definition of `c_i` and the symmetry of `b`.  So `g` is an isometry of
`L`, and it acts as `tau` on `J / Z v`.  **Sources.**  None are quoted; the
proof is the computation on that basis.

**Consequences.**  `[O(K_I) : M_I] <= [O(K_I) : Gamma_{K_I}(d)] <=
|GL_r(ZZ/d)|`, so `M_I` has finite index and the coset graph `O(K_I)/M_I` is
finite; membership in `M_I` is decidable by the correction lemma, so BFS on
that graph followed by Schreier's lemma yields generators of `M_I`, and by the
reduction lemma above the pointed family is then exact.  The lift itself is
`O(r^2)` arithmetic, with no search and no denominator bound.

**Consistency, measured on the rank-five proper-image lattice** (`d = 2`,
`K_I` of rank three, discriminant eight).  Of the three generators of
`O(K_I)`, the residues of their matrices modulo two are
`(1,1,0,1,1,0,0,0,0)`, `0` and `0`; the first is not congruent to the
identity and does not lift, the other two are and do, and the first is an
involution (`g_0^2` is the identity) whose failure to lift is exactly the
witness that `M_I != O(K_I)` there.  The lemma is sharp at that element: it
excludes precisely the one that fails.

**What remains.**  The Schreier step -- BFS over the finite coset graph with
the lift predicate as the membership test, then the Schreier family -- is
stated above as the route and is not implemented here.





