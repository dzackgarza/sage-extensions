# #319 — the card rows of the 87 numerical polarizations and of card 0128

The issue asks for one module that reads each card value by its tag and compares
it with the public orbit call of #286, naming the paper, the table and the page
of the version read; a disagreement is a defect of the call, and a tolerance or
a skipped row is not a pass.  The module is
`tests/enriques_polarization_rows_by_card.py`; the long rows run in the image
job `enriques-polarization-rows`, and the rows that fit the per-test gate are
decided by `tests/lattices/test_the_enriques_polarization_degrees_by_card.py`.

## Which card row is compared through which call

| card row | read by tag as | compared through | state at this commit |
| --- | --- | --- | --- |
| `0128` `#h`, degrees `2 … 72` | `card("polarization_counts", "rows")[2d]["primitive_classes"]` | `NamedLattices.E10.Aut().vector_orbit_representatives(2d, content=1)` | **36 of 36 equal**, one process, 2–6 s a degree (measured on the source's g-basis model of the same lattice; `NamedLattices.E10` gives the same counts at degrees 2 and 8) |
| `0128` `#\bar\Gamma_h` | `[2d]["group_classes"]` | degree 4: the distinct orders of the classes' groups, conjugate subgroups having equal order (Table 4, p. 17; the class invariant is the order and the orbit sizes, p. 11); other degrees: the distinct line/plane/flag triples | **degree 4 decided and equal (348364800 and 92897280 are distinct, so the two classes are not conjugate)**; the other degrees need the plane and flag rows |
| `gamma-h-N` `#I_1` (lines) | `card("arithmetic_groups", tag)["line_orbits"]` | `Gamma_h.isotropic_orbit_representatives(1)` | **87 of 87 equal** (`results/issue17-gamma-h-line-rows.md` records the run over all 87); the smallest card re-measured at this commit: `gamma-h-3` → 5 in 61.7 s, after the ambient $O(N)$ line row (13.6 s) in the same process |
| `gamma-h-N` `#I_2` (planes) | `["plane_orbits"]` | `isotropic_orbit_representatives(2)` | undecided (`gamma-h-3`, the smallest plane row, did not return in 480 s) |
| `gamma-h-N` `#I_12` (flags) | `["flag_orbits"]` | `isotropic_orbit_representatives(2, flag=True)` | undecided (not measured: it reads the same ambient rank-2 classes, and its stabilizer search is the one the plane shortcut does not cover) |

## The defect this round repaired: `#h` is the primitive stratum

Card `0128`'s Table 4 states `#h` per degree, and the sentence with the table
says which vectors it counts: "the first line shows the number `#h` of orbits of
**primitive** vectors in a given degree" (D. Dutour Sikirić, K. Hulek, *Moduli of
polarised Enriques surfaces — computational aspects*, J. London Math. Soc. 110
(2024), arXiv:2302.01679v2, Table 4, printed p. 17).  The module read it as
`vector_orbit_representatives(2d)`, which is the whole square-`2d` shell: content
is an isometry invariant, so that shell is the disjoint union of the classes of
content `c` with `c² | 2d`, and the source disregards the non-primitive ones —
"the list of [CDGK, Appendix] also contains nonprimitive numerical polarizations,
which we disregard in our approach since they do not lead to new moduli spaces"
(section 3.5, p. 19).  The row now reads
`vector_orbit_representatives(2d, content=1)`, and the same classes feed the
row's `#\bar\Gamma_h` line.

Measured on the card's lattice, one process, all 36 degrees:

```
primitive stratum == card's #h : 36 of 36, 0 disagreements
whole shell      != card's #h : 13 of 36, at 8, 16, 18, 24, 32, 36, 40, 48,
                                50, 54, 56, 64, 72
degree 8: card 2, primitive 2, shell 3
          (the extra class is 2v with q(v) = 2, of content 2 and square 8)
degree 16: card 4, primitive 4, shell 6
degree 72: card 16, primitive 16, shell 23
```

So before this round the module would have printed a `DEFECT` block for 13 card
rows the call reproduces, and would have built `Gamma_h` from non-primitive
vectors at those 13 degrees.

No library answer is wrong here: `vector_orbit_representatives(square)` returns
every content stratum, as its own docstring states, and `content=1` is the
primitive one.  The defect was the module's reading, so the red evidence is the
module's own run (`#h: expected 2, call 3` at degree 8) rather than a failing
test of a library call.  The guard that keeps the reading is
`test_the_degree_eight_row_counts_the_primitive_class_alone`: it asserts both
that the card's row is the primitive count and that the shell of square 8 is
strictly larger, so a reader that drops `content=1` fails it.

## The change, and what runs in the gate

`tests/lattices/test_the_enriques_polarization_degrees_by_card.py` decides the
part of Table 4 that fits the gate: the smallest row (degree 2) and the smallest
degree where the two readings differ (degree 8), read by card tag:

```
tests/lattices/test_the_enriques_polarization_degrees_by_card.py ...  [100%]
7.24s call  test_the_degree_eight_row_counts_the_primitive_class_alone
5.02s call  test_the_smallest_degree_row_is_the_cards_orbit_count
0.08s call  test_the_named_lattice_is_the_cards_lattice
3 passed in 13.61s
```

The 34 other degrees are the same row of the same card and are compared by the
image job, which the orchestrator dispatches; nothing here narrows that job.

## The undecided rows, and the defect they are

The plane and flag rows of a `gamma-h-N` card do not return, so the module
reports them `UNDECIDED` and the run is red — the state the issue calls a
non-pass.  The block to file, with the lattice and the group:

```
dzackgarza/sage-extensions — the plane and flag rows of the public
isotropic-orbit call do not return on Gamma_h
  lattice: 029J (U + U(2) + E8(-2), rank 12, signature (2,10), determinant 1024)
  group:   gamma-h-3 = Gamma_h of case 3, S = overline{7}, |Gamma-bar_h| = 92897280
  row:     #I_2 = 10, #I_12 = 19 (D. Dutour Sikirić, K. Hulek,
           arXiv:2302.01679v2, Table 1, p. 13)
  measured at this commit: Gamma_h,3 builds in 3.2 s after the lattice's 1.0 s;
           isotropic_orbit_representatives(1) returns the card's 5 in 61.7 s;
           isotropic_orbit_representatives(2) was still running at the 480 s cap
           of its run ("planes: UNDECIDED after 480s"), and the same module's
           gamma-h-4 line row PASSes (expected 6, call 6) in 58 s
```

The connected GitHub connection of this session cannot create issues (it reads
issues and writes branches), so this block is what the orchestrator posts.

## The plane row: which branch it takes, and what that branch costs

The plane row of a `gamma-h-N` card is one call of
`PredicateSubgroups.isotropic_orbit_representatives(2)`, and on the smallest
card -- `gamma-h-3`, case 3, $S=\overline{\{7\}}$, $|\bar\Gamma_h| = 92897280$ --
it does not return in 480 s.  Two cheap questions decide which of the row's
three routes it takes, and both are measured:

```
Gamma_h,3 finite-character quotient: index 505920,
    spinor_kernel False, determinant_kernel False, has_discriminant True
P1 is_parabolic_complete: True  in  0.8 s
P2 is_parabolic_complete: True  in 25.7 s
```

So the row cannot take the `O^+` route: `_plane_orbit_from_odd_stabilizer` is
entered only for a subgroup that cuts the spinor character alone, and
$\Gamma_h$ cuts a discriminant condition and no sign kernel.  It also does not
fall back to the stabilizer closure -- both ambient representatives certify
their parabolic as complete -- so the row is inside
`_iter_transported_planes(quotient, representative, family)`, whose splitting
walk is `_iter_splitting_isometries_in_im_rho(family, spellings=True)`, and
that call passes **no `point`**.

That is the whole of it: the walk's own docstring says which computation each
form is.  With a `point` it computes the `rho(Gamma)`-orbits on the finite
`im rho`-orbit of that point -- "the isotropic classes of `A_L`, or the images
of the isotropic planes" -- and that is the route the line rows take: the class
set `{c, -c}` is passed as the point.  Without one it runs
the double-coset enumeration in `im rho`, and the same docstring records what
that costs at this size: "the double-coset enumeration in a group of order
`|im rho|` does not return at the Enriques size, while the orbit walk of the
class set under the `im rho`-generators terminates".  The plane row is that enumeration,
in a finite image in which `rho(Gamma_h)` has index 505920.

Passing the plane's divided class set $J_x$ as the point would put the row on
the fast side of that sentence, and the set's stabilizer in $Q$ is
$\rho(G_x)$ exactly when the published indices certify it (527 and 23715 for
$T_{\mathrm{En}}$, DSH §3.6, p. 22) -- and not otherwise: on
$T_{\mathrm{Co}}$ the stabilizer is bigger by a factor 8, which
`isotropic_plane_orbits`'s docstring records and which is why that call asks
for the certificate instead of assuming it.

The library already owns a finite computation of the same orbits,
`isotropic_plane_orbits(representatives)`: its divided-class decomposition
returns $\Gamma_{\mathrm{En},2}$'s 9 and $\widetilde{O}^+$'s 24242, the rows
of card `029J`, and its hypothesis $\rho(G_x) = \mathrm{Stab}_Q(J_x)$ is
certified from the published indices 527 and 23715 (Dutour Sikirić--Hulek,
§3.6, p. 22).  That hypothesis genuinely fails on $T_{\mathrm{Co}}$, by a
factor 8, which the call's own docstring records.  Whether the row may read its
count off that decomposition is therefore a decision about when the hypothesis
holds, not a performance tweak, and it is not made here: the row keeps the
exact double-coset walk and the card's plane row stays `UNDECIDED`.

## The plane row has two entries, and neither decides the smallest card

The number the card states is one thing; the entry point that returns it is
another.  Card `gamma-h-3` states `#I_2 = 10` (Table 1, p. 13), and the library
offers two public computations of that count, both measured here on that card:

```
<group>.isotropic_orbit_representatives(2)      still running at 480 s
<group>.isotropic_plane_orbits(P1, P2)          still running at 300 s
```

The first is the row #286 names, and the section above says which of its routes
it takes and why that route cannot return at this size.  The second is the
divided-class decomposition: its hypothesis $\rho(G_x) = \mathrm{Stab}_Q(J_x)$
is the one the published indices 527 and 23715 certify for $T_{\mathrm{En}}$
(Dutour Sikirić--Hulek, §3.6, p. 22), and it is the call a reader would reach
for to decide the row by another route.  It does not decide this card inside
five minutes either, so the hypothesis question is not the whole gap: a plane
row of a *subgroup* of $\Gamma_{\mathrm{En},2}$ is not answered by either entry
today.

The stage record says where the second one went.  Its constructor's first
stage is `discriminant images`, and that stage alone runs to the end of the
300 s:

```
  299.38s  returned  discriminant images        [divided-class plane row]
   0.58s  raised    divided-class orbit set     [divided-class plane row]
 299.99s  raised    divided-class plane row
```

`discriminant images` is `_DividedClassPlaneOrbitDecomposition.__init__`.
Nothing in that stage touches the class sets -- they are built after it, in
0.58 s before the interrupt -- but the two objects inside it that a reader would
blame are both instant, measured in a fresh process on the same group:

```
group.finite_character_quotient()          0.0 s
group.discriminant_image().order()         0.0 s   = 92897280
```

92897280 is card `gamma-h-3`'s own `|\bar\Gamma_h|`, so the finite image is
computed at once and agrees with the card.  Three of the constructor's remaining
lines, timed one at a time in the same process, are:

```
_im_rho_engine_and_section()                    83.1 s   (a group of size 46998591897600, 4 generators)
group.discriminant_image().group_generators()    0.7 s
_divided_discriminant_classes(lattice, P1)       0.2 s   (4 classes)
```

The ambient image with its word section is the largest of the three by two
orders of magnitude; the class sets, which are what the decomposition is for,
are 0.2 s.  The measured lines do not sum to the stage's 299 s, so the rest of
that stage -- the subgroup's image inside the engine and its generating set, and
the class points -- remains unattributed here.

That is where the acceptance's plane and flag rows stand, and the defect block
above is unchanged.

## What this round did not do

* The plane route and the flag route are not repaired: they are #390/#391's
  cost question (one double coset per class-set point), not a reading here.
* `#\bar\Gamma_h` is compared at degree 4 only (the two classes' groups have
  different orders).  The other 35 degrees need the orbit sizes, hence the same
  plane and flag rows.
* `tests/lattices/test_enriques_polarization_orbits.sage` carried 261
  parametrized comparisons of the same rows inside the per-test gate, each one
  public call of tens of seconds to 203 s against a 20 s call ceiling.  They are
  gone: the file keeps the decode and the card pinning that the comparison rests
  on (`6 passed in 1.05s`), and the rows themselves are compared by the image
  job.
