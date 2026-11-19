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
| `0128` `#\bar\Gamma_h` | `[2d]["group_classes"]` | the distinct line/plane/flag triples over those classes | undecided: it needs the plane and flag rows |
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

## What this round did not do

* The plane route and the flag route are not repaired: they are #390/#391's
  cost question (one double coset per class-set point), not a reading here.
* `#\bar\Gamma_h` is compared nowhere yet: it needs the same plane and flag
  rows.
* `tests/lattices/test_enriques_polarization_orbits.sage` still carries 261
  parametrized comparisons of the same rows inside the per-test gate.  Each is
  one public call of tens of seconds to 203 s (`results/issue17-gamma-h-line-rows.md`
  records 10-20 s a card for `gamma-h-2` to `gamma-h-87` and 203 s for
  `gamma-h-1`, on a warm process), against a 20 s call ceiling and a 60 s
  timeout, so the file cannot pass the gate; the same rows are decided by the
  image job, which is where the module keeps them.  Removing or re-homing that
  copy is not part of this round's change.
