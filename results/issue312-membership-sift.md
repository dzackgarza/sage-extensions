# #312: the membership question at Sterk's first cusp, one stabilizer chain, and what still costs the minute

**Result.** Membership in `G_v` is decided by sifting one stabilizer chain of
`ρ(Γ_{En,2})`, built once and shared by every cusp, and the per-root question at
Sterk's first cusp costs **0.106 s of CPU**, of which the sift is 0.3 ms and the
discriminant image of the lift 0.086 s.  What the question used to cost and no
longer does is the Levi evaluation — `λ(reflection) ∈ O(N)`, built per candidate
and read by nothing: two `contains_root_reflection` calls (which still build it)
took 5.78 s of wall time in the loaded run below.  The restricted chamber at the
five cusps still does not return: what remains is Vinberg's own enumeration, not
the membership question.

Measured on the adopted runtime (Sage 11.0.beta5 on the `ghcr.io/dzackgarza/sage`
image pinned in the repository's notes, the indefinite port bound at `/work`).
The CPU figures are `time.process_time()` in the Sage process, so they are not
inflated by the other chats' jobs that were running at the same time; the wall
figures are quoted with the load average they were taken at.

## 1. What the question is

`IsotropicVectorReductionImage.contains_root_reflection(root)` decides whether
the reflection of `N = v^⊥/Zv` in the class of `root` lies in
`G_v = λ(Γ ∩ P_v)`.  The criterion is #312's:

    σ ∈ G_v  ⟺  ρ(g) ∈ ρ(K_v)ρ(Γ),   g any lift of σ in P_v.

At Sterk's five cusps `ρ(K_v)` is trivial (measured: order 1, the test
`test_the_kernel_of_the_levi_map_acts_trivially_on_the_discriminant_group`), so
the question is one membership in `ρ(Γ_{En,2}) ≤ O(A_L)`, a group of order
`696729600`.

## 2. The repair, in two parts

**The sift.** `OrthogonalCharacterQuotient.discriminant_image_membership()`
returns a `DiscriminantImageMembership`: the subgroup `ρ(Γ)` inside the
`O(A_L)` engine the library already owns for `O(A_L)` (the same subgroup
`discriminant_image()` returns as owned data), with membership answered by
GAP's `\in` on it — the sifting test through a Schreier–Sims stabilizer chain
(A. Seress, *Permutation Group Algorithms*, Cambridge University Press 2003,
Chapter 4).  The object is cached on the quotient, which is cached on the
subgroup, so one chain serves all five cusps.  No list of the image's elements
is built anywhere: at order `696729600` that is not an option.  The question
went from **0.02 s to 0.0003 s** of CPU.

**The lift, not the Levi image.** `admits_root` used to answer the question by
first evaluating the Levi map `λ(reflection) ∈ O(N)` and handing that to
`contains` — a 10-dimensional isometry built per candidate root, ~0.5 s of CPU,
and *not used by the criterion at all*: the criterion is a statement about the
lift.  `contains_lift(g)` states exactly that and is what `admits_root` calls
now.  The Levi evaluation survives where it is the point — in
`contains_root_reflection`, which starts from a vector of `L` and therefore also
checks that the lift descends to the reflection in the right class.

One more: `cusp_chamber` memoises `admits_root` by the root's coordinates.  The
measured repeat rate is 1%, so this is not where the time went.

| step of one question | CPU |
| --- | --- |
| coordinates of the root in `N` | 0.0002 s |
| `class_lift` (the class lifted to `v^⊥`) | 0.0036 s |
| the reflection of `L` in that lift | 0.0157 s |
| its discriminant image `ρ(g)` | 0.0864 s |
| **the sift** | **0.0003 s** |

Twenty candidate roots taken from the search itself, on a quiet machine.

## 3. The first cusp is still not reached, and the control says why

`cusp_chamber` returns Vinberg's algorithm on `N` restricted by `admits_root`.
At `Sterk_1`, `max_decompositions=4000`, the run asked **1400 questions in 964 s
of wall time (360 s of CPU)** and had not closed; at `max_decompositions=400` it
had not returned after 2200 s.  99 of every 100 questions are about a root not
seen before, so the cost is the number of candidates Vinberg's decomposition
walk puts in front of the filter.

The control, on the same `N` at the same cusp:

```
[   119.3s] the unrestricted chamber: 10 walls, complete True, 13.2s wall 3.3s cpu
[   518.3s] the same walls under the filter: 9 of 10 admitted, 399.0s wall 102.4s cpu
    squares: [-4, -4, -4, -4, -4, -4, -4, -4, -4, -4]
```

Vinberg's algorithm on the whole of `O(N)` closes in **3.3 s of CPU**, and the
filter admits nine of its ten walls: the chamber of the reflection subgroup is
the larger polyhedron of Sterk's diagram (twelve walls, 4.3.5, p. 19), and the
enumeration has to go far deeper to close it.  The 102 s of CPU in that line are
almost all one-off — the first question builds `ρ(Γ)` in the `O(A_L)` engine
(one `ρ` sweep over the ambient generating family), the ten questions after it
are 0.1 s each.

So: the membership question is repaired and measured; **the five cusp chambers
are not delivered**, and what is missing is a cheaper enumeration of the
restricted polyhedron — a controlling vector inside the chamber, or avoiding the
`ρ` construction per candidate (it is 0.086 of the 0.106 s, and it depends only
on the class of the lift in `A_L`).  The card rows this would be compared with
are read and matched already (`tests/cards`
`integral.cusp_chambers` of `029J`, five rows: 4.3.5 with 12 walls, 4.3.6 with
10, 4.3.7 with 12, 4.3.8 with 11, 4.3.9 with 13).


## 4. Two measurements the comparison will need

`Sterk.selected_isotropic_vectors()` and the card's `integral.cusp_chambers` rows
name the same five cusps, and **four of the five vectors agree term by term**.
The exception is 4.3.8: the card states the cusp as `(0, 0, 2, 1, -4, -5, -7,
-10, -8, -6, -4, -2)` and the library's `Sterk_4`, built as
`c(b["ep"] + 2 b["fp"]) + α`, is `(0, 0, 1, 2, -4, …)`.  They are two
representatives of one cusp — both primitive and isotropic, and the card's row is
the authority — so a wall-count comparison must pair the rows with the cusps by
the paper's order, not by exact vector equality.  The test
`test_the_five_cusps_are_the_chamber_rows_of_card_029j` pins the count of
agreements (four) rather than pretending to five.

Card 029J's five rows, as read by tag at `e8a7f88`:
4.3.5 with 12 walls (printed p. 19), 4.3.6 with 10 (p. 21), 4.3.7 with 12
(p. 22), 4.3.8 with 11 (p. 23), 4.3.9 with 13 (p. 24).

## 5. The one count that differs, and it differs before any chamber runs

`Sterk.sterk_roots()["Sterk_5"]` — `Sterk.sterk5_in_U_E8_2()`, "Sterk 5's
fourteen roots in `U + E8(2)` coordinates" in `sterk.py` — holds **14** roots,
and card `029J`'s `integral.cusp_chambers` row for that cusp, statement **4.3.9**,
states `wall_count: 13` with thirteen wall vectors.  Both values are recorded
here and neither is typed into the test.  Which is right is not decided by
anything measured in this work: the chamber that would decide it does not return
(§3), so this is a discrepancy between the library's transcription of Sterk's
figure and the database's row for it, filed for whoever owns the transcription.
