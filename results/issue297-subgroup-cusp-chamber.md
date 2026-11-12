# #297: the subgroup cusp chamber, anchored at a 0-cusp, with the membership sifted in the finite discriminant quotient

**Result: delivered.** `subgroup_cusp_chamber(cusp, generators=...)` on a
hyperbolic lattice takes a primitive isotropic vector naming the 0-cusp and the
generators of the finite-index subgroup `Γ′`, and returns the fundamental
chamber of the reflection part of `Γ′` anchored at that cusp: its walls as root
vectors with their inner products.  The membership question a root's reflection
asks is decided where it is decidable — in the finite discriminant quotient,
by one sifting test of a Schreier–Sims stabilizer chain — and the walk is
Vinberg's own, anchored at the vertex of the full chamber that the subgroup
filter admits most walls of.

Specimen: the Enriques cusp lattice `U(2) ⊕ E8(−2)` (`SEn`, rank 10, signature
(1,9), determinant −1024) with the twelve reflections that Sterk's first
diagram names, at the cusp `ep`.

## 1. The call and its citations

`HyperbolicLattices.ParentMethods.subgroup_cusp_chamber` (this commit).  The
statements it rests on:

- **The algorithm and its termination.**  E. B. Vinberg, *On the groups of unit
  elements of certain quadratic forms*, Math. USSR Sb. 16 (1972), §3.2
  (pp. 27–29): the construction after Proposition 3 (p. 27) takes the point
  `p_0` and the unique cell of `Γ′` coinciding with `P_0` near it; Proposition 4
  (p. 28) states that the polyhedron cut out by the normals listed is that cell;
  Proposition 5 (p. 29) states that the list breaks off once that polyhedron has
  finite volume.  The wall set therefore needs no separate certificate of
  completeness: the algorithm's own stop is the certificate.
- **The membership.**  A. Seress, *Permutation Group Algorithms*, Cambridge
  University Press 2003, chapter 4: the Schreier–Sims stabilizer chain and its
  sifting test.  The discriminant images of the given generators generate a
  subgroup of the finite orthogonal group `O(A_L)`, and one sift answers each
  root's question; the cost of a question is the length of the chain, never the
  size of the group.
- **The anchor.**  The controlling vector is a vertex of the chamber of the full
  reflection group `W(L)`, selected among the vertices of positive square whose
  through-walls are a `Z`-basis of the vertex's orthogonal complement by how
  many of its walls the subgroup filter admits.  Every vertex of that chamber
  lies in the chamber of every reflection subgroup of `W(L)` — a group generated
  by fewer reflections cuts out a bigger polyhedron — so the search anchored
  there computes the subgroup's own chamber by the three statements of Vinberg
  1972 §3.2 above.

## 2. The wall count against the card

The probe run (`.tmp/issue297-probe5.log`, the adopted runtime, the #297
worktree at this commit):

```
[1] lattice: Integral lattice of rank 10 and signature (1, 9)
[2] twelve roots transported, squares: [-4]
[3] subgroup of O(A) order: 696729600
[4] the twelve generators sift in
[5] anchor vertex: (9, (1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) full chamber took 31.05884289741516
[6] walls: 12 complete: True
    squares: [-4]
    sifts: 247
    elapsed: 637.628116607666
    total: 720.6676642894745
```

Twelve walls, complete, all of square −4 — the `gamma-en-2` row 4.3.5 of card
`029J` (H. Sterk, *Compactifications of the period space of Enriques surfaces,
Part I*, Math. Z. 207 (1991), §4.3.5, p. 19), read by tag.  The anchor vertex
`(1, 1, 0, …)` is Sterk's own `x = e′ + f′` (§4.3.5, p. 19), the vertex of the
full chamber whose nine walls the filter admits.

The subgroup of `O(A)` that the twelve reflections' discriminant images
generate has order `696729600` — the order of `ρ(Γ_{En,2})` that the #312
results file quotes — and the sift admits the twelve generators and 247
distinct roots in all, of which the twelve walls.

## 3. The test

`tests/lattices/test_the_subgroup_cusp_chamber.sage` (this commit) asserts the
wall count against the card row, with the paper and page cited in the test.
The run (`.tmp/issue297-test.log`, the adopted runtime, the #297 worktree at
this commit, `--no-time-gates` for the legitimately expensive walk):

```
[run] /sage/.venv/bin/python -m pytest tests/lattices/test_the_subgroup_cusp_chamber.sage -p qc_sage_session -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint -o addopts= -v --no-time-gates
============================= test session starts ==============================
platform linux -- Python 3.14.10, pytest-9.1.1, pluggy-1.7.0 -- /sage/.venv/bin/python
time gates OFF (--no-time-gates): star import 2.43 s (ceiling 3 s), collection ceiling 6 s, each test call ceiling 20 s
rootdir: /repos/sage-extensions
configfile: pyproject.toml
plugins: platformdirs-4.13.5, anyio-4.15.1
collecting ... collected 3 items

tests/lattices/test_the_subgroup_cusp_chamber.sage::test_the_full_chamber_of_the_cusp_lattice_has_ten_walls PASSED [ 33%]
tests/lattices/test_the_subgroup_cusp_chamber.sage::test_the_subgroup_cusp_chamber_at_the_first_cusp_has_the_card_wall_count PASSED [ 66%]
tests/lattices/test_the_subgroup_cusp_chamber.sage::test_the_root_filter_removes_a_wall_whose_reflection_it_refuses PASSED [100%]

========================== test-call performance gate ==========================
tests/lattices/test_the_subgroup_cusp_chamber.sage::test_the_subgroup_cusp_chamber_at_the_first_cusp_has_the_card_wall_count: 170.23 s > 20 s
================= 3 passed, 120 warnings in 179.36s (0:02:59) ==================
[exit] 0
```

Three passed: the two existing filter tests and the new card-row test.  The
170.23 s call is the walk itself (the probe measured 637.6 s under load, the
test run 170.23 s on a quieter machine); the gate is off for it by the flag the
repository's own expensive-row convention uses.


## 4. The `I_{1,8}(2)` run

The second specimen, recorded and not asserted (`.tmp/issue297-probe6.log`, the
adopted runtime, the #297 worktree at this commit).  The cusp vector of `T_Co`
is Sterk's third selected vector read in the Coble lattice; the reduction at it
is the Coble cusp lattice `I_{1,8}(2) = ⟨2⟩ ⊕ E8(−2)`, and the cusp's printed
roots are filtered to the nine that lie in `delta^perp`, transported to `T_Co`,
and read as classes of the boundary lattice:

```
[1] cusp vector of T_Co: e_ep + e_fp - 2*e_a1 - 3*e_a2 - 4*e_a3 - 6*e_a4 - 5*e_a5 - 4*e_a6 - 3*e_a7 - 2*e_a8
[2] reduction: Integral lattice of rank 9 and signature (1, 8)
    rank: 9 signature: (1, 8) determinant: 512
[3] roots: 12 inside delta^perp: 9
[4] classes: 9 squares: [-4, -2]
    reflections: 9
[5] cusp of N: e_0 - 2*e_1 - 3*e_2 - 4*e_3 - 4*e_4 - 3*e_5 - e_6 - 2*e_7 - 2*e_8
[6] walls: 11 complete: True
    squares: [-4, -2]
    elapsed: 21.014062881469727
    total: 479.2985417842865
```

Eleven walls, complete, all of square `−4` or `−2`.  The call on the Coble cusp
lattice at one cusp, with the nine reflections the transported roots name,
returns a chamber of eleven walls in twenty-one seconds.

