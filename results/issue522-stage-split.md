# #522: where the time of `subgroup_cusp_chamber` at Sterk's first cusp goes

**Result: the call is over the ceiling, and it is over it for two reasons, both
inside the walk.**  The restricted walk at Sterk's first cusp enumerates every
solution of each layer's norm equation and only then asks the wall condition,
so the layers at height 12 and above write down 187 426 and 334 144 candidates
of which **all** lie outside the walls it has already written; and each
membership question that decides whether a candidate is a wall costs 0.12 s, of
which 0.107 s is the passage of the reflection to its discriminant image.

The measurement comes before the repair, so this note is the measurement; the
two repairs it names are the work that follows it.

## 1. What the call is, and the ceiling it is over

`HyperbolicLattices(ZZ)(NamedLattices.SEn).subgroup_cusp_chamber(cusp,
group_generators=<Sterk's twelve reflections>)` returns the chamber of the
reflection subgroup at Sterk's first cusp; card `029J`'s `gamma-en-2` row 4.3.5
records 12 walls.  The suite's per-test call ceiling is 20 s
(`src/sage_extensions/testing/suite_budget.py`, `TEST_CALL_CEILING`) with a
60 s pytest-timeout hang bound, and the test alone in the published image did
not return inside 590 s at load 12.

Every number below is the call's own body, timed from a probe bound at
`/probe.py` and run through `~/sage-image/run.sh -w /work` with the provider
tree at `/repos/sage-extensions` and the port repo at `/work`
(`.scratch/wt522_launch.sh` in the repository checkout).  The probes and their
logs are in the checkout's `.scratch/` and `<tree>/.tmp/`, not on `main`: they
are measurements, not evidence files.

## 2. The stage split

Measured on tree `9dc74cbce989b0fe49cd5e4b2b7b81d32203b895` (`.tmp/probe522_stages.py`
and `.tmp/probe522_stages.log`), each stage of the call's own body:

```
     0.08 s  SEn
     0.25 s  Sterk_1 roots: 12
     3.80 s  images (12)
     3.85 s  subgroup
     6.47 s  full chamber vertices: 10
     6.85 s  anchor chosen: (9, (1, 1, 0, 0, 0, 0, 0, 0, 0, 0))
   225.75 s  fundamental chamber: 12 walls, sifts 247
   225.75 s  complete: True
```

So the chamber is 218.9 s of the 225.75 s, on 247 distinct membership
questions; the twelve discriminant images and the subgroup built from them are
3.85 s, the vertices of the full chamber 2.62 s, and the anchor's ten questions
are inside the 0.38 s after them.  Repeated on `762126c` the same prefix costs
22.76 s of which 20.31 s is the discriminant group and the twelve images
(`<tree>/.tmp/probe522d_walk.log`): this host is the slower one and the load
differs, so the prefix is between 7 s and 23 s and the chamber stage is the one
the ceiling is about.

## 3. The walk's own breakdown

The walk at the anchor, instrumented layer by layer (`.tmp/probe522_layers.py`,
`.tmp/probe522_layers.log`, tree `9dc74cb`):

```
    walk built: 2 coset representatives, root lengths [1, 2, 4]
    layer    3: k=4 height=0 candidates=    242 outside=      0   0.473 s written=0
    layer    4: k=4 height=2 candidates=    120 outside=    119   0.018 s written=9
    layer    7: k=4 height=4 candidates=   1065 outside=   1063   0.306 s written=9
    layer    9: k=4 height=6 candidates=   2885 outside=   2885   0.213 s written=10
    layer   11: k=4 height=8 candidates=  18780 outside=  18779   3.983 s written=10
    layer   13: k=4 height=10 candidates= 42732 outside=  42732  10.470 s written=11
    layer   16: k=4 height=12 candidates=187426 outside=187426  25.894 s written=11
```

(`outside` is the number of candidates that pair positively with a wall
already written, i.e. the ones conditions (58) of Vinberg 1972, §4.1, p. 30
exclude.)  The counts are reproduced on `762126ccdf9bc7208de5fcb3d16e4f5383ded82b`
by a walk instrumented from this chat, which also records the two layers past
height 12 (`.scratch/probe522d_walk.py`, `<tree>/.tmp/probe522d_walk.log`):

```
    layer   16: k=4 height=12 candidates= 187426 outside= 187426 written=11
    layer   17: k=4 height=14 candidates= 334144 outside= 334144 written=11
```

**The enumeration's candidates are the walls' complements.**  From height 8
upwards every candidate the walk writes down already violates (58) against a
wall it has written, so the layer's cost is spent producing solutions the
algorithm then discards, and the cost is set by the deepest wall's height
(Sterk's third wall, at height 64 from `x = e' + f'`).  `Roots_decomposed_into`
restricts the enumeration to the cell at the controlling vector — the nine
normals through `x` — and not to the walls accepted after them.

## 4. What one membership question costs

The same three steps, timed one at a time on `762126c`
(`.scratch/probe522c_sift.py`, `<tree>/.tmp/probe522c_sift2.log`):

```
    per question of 12: reflection 0.0084 s, image 0.1073 s, sift 0.0040 s
    five discriminant_isometry calls: 0.0132 s each
    five from_morphism: 0.0898 s each
```

So the sift is not the cost: the passage of the reflection to its discriminant
image is, and inside it `from_morphism` — the normalization of the form's
module maps into the finite group — is 0.09 s.  The reflection itself is
0.0084 s.  Asked 247 times this is 30 s of the walk; asked once per candidate
of a deep layer it would be far more.

## 5. The two repairs this names

1. **A discriminant action of a lattice reflection that costs what its matrix
   costs.**  The action of an isometry of an integral lattice on `A_L` is the
   dual action `x -> x (R^{-1})^t` on the dual frame, where `R` is the
   isometry's own matrix; the two frames — the dual one and the invariant-factor
   one the finite-form engine acts on — differ by a fixed change of basis, read
   once.  An element is then one inverse and two products of ten-by-ten
   matrices, and the two presented module maps it also carries are asked for on
   first request rather than at construction.
2. **`_FilteredVinAl.Roots_decomposed_into` restricted to the walls already
   written.**  Vinberg's (58) is the condition against every normal already
   written down.  In the coefficients `d` along the cell's normals the cone
   condition `u <= 0` is *not* the orthant `d >= c`: the cell's Gram is a
   Stieltjes matrix, so `G^{-1} >= 0` makes `u <= 0` imply `d >= c`, but the
   converse fails and the relaxation is not a small one.  The enumeration
   therefore runs in the candidate's normal coordinates `u = -f`, `f >= 0`,
   where (58) is one-sided, and the walls written after the cell enter as upper
   bounds there.

## 6. What the two repairs measure

The enumeration, layer by layer, on `762126c` with the two repairs
(`.scratch/probe522j_real.py`, `<tree>/.tmp/probe522j_real4.log`):

```
    layer    4: k=4 height=2  written= 9 constraints=0 candidates=     1 outside=0
    layer    7: k=4 height=4  written= 9 constraints=0 candidates=     2 outside=0
    layer    9: k=4 height=6  written=10 constraints=1 candidates=     0 outside=0
    layer   11: k=4 height=8  written=10 constraints=1 candidates=     1 outside=0
    layer   13: k=4 height=10 written=11 constraints=2 candidates=     0 outside=0
    layer   16: k=4 height=12 written=11 constraints=2 candidates=     0 outside=0
    layer   17: k=4 height=14 written=11 constraints=2 candidates=     0 outside=0
    layer   20: k=4 height=16 written=11 constraints=2 candidates=     1 outside=0
    layers 20, candidates 247, outside 0
    layers 1.24 s, sifts 247 in 40.92 s
```

247 candidates for the whole walk, none of them outside a wall already
written.  The same walk before the change enumerated 587 394 candidates in the
layers this session saw (heights 0 to 14, `.scratch/probe522d_walk.py`) and was
killed at 560 s without returning; the walk's own record of its earlier cost is
1 855 003 candidates, 337.8 s of root test and 92.9 s of dependence check, in
`_FilteredVinAl.IsNewRoot`.  What is left of the call is now the membership
question and nothing else.  The figures
above are at load average 20 on this four-CPU host, where one question costs
0.17 s; the same question cost 0.12 s at load 4 (`§4`), so the sift figures are
load-bound and the candidate counts are not.
