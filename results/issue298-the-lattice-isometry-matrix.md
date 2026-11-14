# #298 — an isometry between two isometric lattices, returned as a matrix

Stage 2 of the Coble programme, under #281.  Two commits on `main`: `28422f9` (the call and its test)
and `f7eaa5d` (the decision's direction restored).  Everything below was measured on the adopted
runtime (Sage 11.0.beta5, source pin `9f1680d2a7bcf001e50714768e6066e6652d1708`) in a worktree of
`omm/main = 524f4231`.

**Result.** `Lattices.isometry_matrix_to(other)` returns a matrix `M` with `M^T G_self M = G_other`
for two integral lattices that are isometric and raises `ValueError` when none exists;
`is_isometric_to` is the same decision read as a boolean, so the library decides isometry in one
place.

## 1. The call

`src/sage_extensions/categories/lattices.py`, on `Lattices.ParentMethods`:

- **`isometry_matrix_to(other)`** — the matrix whose columns are the coordinates, in `self`'s selected
  basis, of the images of `other`'s selected generators.  A vector of `other` with coordinate column
  `x` therefore has image `M x`, and the form equation `M^T G_self M = G_other` is exactly the
  statement that `x |-> M x` preserves the form; read the other way, `M` is the change of basis that
  writes `other`'s form as `self`'s on the columns.  The engine's matrix is untrusted, and the
  equation is checked on the returned object.
- **`_isometry_absent(other)`** — the one decision, `Isom(self, other).is_empty()`, with the
  undecidable case raising.  **`is_isometric_to(other)`** is `not _isometry_absent(other)`.
- The witness per regime is the Mor's own, and each step is cited in the docstring:
  - equal Gram matrices — the identity;
  - a definite pair — Sage's `QuadraticForm.is_globally_equivalent_to`, i.e. PARI's `qfisom` (The
    PARI Group, *PARI/GP* reference card, "Arithmetic functions on lattices");
  - an indefinite pair of rank at least three — the port's Eichler recursion
    (`sage_indefinite_port.indefinite.marked_lattices.isometry` -> `EichlerRecursion.isometry`, its
    isotropic reduction, induction and pointed equivalence);
  - an indefinite binary pair — the port's cycle walk (`_binary_indefinite_isometry_matrix`).

`isometry_to` is untouched and still returns the Mor rather than a matrix; `is_isometric` is
untouched and still returns the proposition when undecided.

## 2. Why the decision's direction was restored

The first commit asked `Isom(other, self)`.  Every existing consumer had asked `Isom(self, other)`,
and while most regimes are endpoint-symmetric by construction — genus, spinor-genus count,
discriminant form, signature — the indefinite binary branch returns "not isometric" when its witness
search finds no matrix, so the answer depends on the direction it is asked.  The second commit asks
the original question again, takes the witness `W` of `Isom(self, other)` with
`W^T G_other W = G_self`, checks that equation, and returns `W^-1`, which is the matrix of the
inverse isometry and satisfies the documented `M^T G_self M = G_other`.  Unimodularity is a
consequence of the checked equation, since equal ranks and nondegenerate Gram matrices of equal
determinant force `det W = ±1`, and the promised equation is checked again on the returned object.

## 3. The measured pairs

| pair | decision | witness | returned matrix | Gram equation |
| --- | --- | --- | --- | --- |
| `U + <-1>` against `I_(1,2)` | not empty, 0.43 s | 0.77 s | unimodular, `det = 1` | holds |
| `U + U + <-1>^7` against `U + I_(1,8)` | not empty, 0.12 s | 26.5 s, the port's recursion | unimodular, `det = 1` | holds |
| `<1>` against `<-1>` | empty, 0.00 s | — | the call raises `ValueError` | — |

The returned object is the owned matrix over `ZZ` (an element of `ZZ.matrix_space(rank, rank)`), the
same object `gram_matrix()` returns, so `matrix.transpose() * left.gram_matrix() * matrix ==
right.gram_matrix()` is a comparison of two such matrices.

Both isometric pairs have different Gram matrices, so the matrix is not the identity and the equation
is a real check; the test transports `other`'s generators through `M` and compares the transported
Gram matrix with `other`'s.

The second pair is the one that matters for the Coble work: its signature `(2, 9)` has positive index
two, so neither `qfisom` nor the Lorentzian case reaches it, and the witness is the port's Eichler
recursion.  It is also the pair that made the first commit's direction change visible as a risk: the
decision there is a genus/spinor-genus comparison, but the binary branch is not.

## 4. The test

`tests/lattices/test_the_isometry_matrix_between_isometric_lattices.sage`, three tests: the rank-three
pair (Gram equation, determinant, the transported generators' Gram, both directions of the decision),
the rank-eleven indefinite pair (same), and the refusal (`<1>` against `<-1>`: `is_isometric_to` is
`False` both ways and `isometry_matrix_to` raises `ValueError` both ways).

Measured, one session, `-p qc_sage_session -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --no-time-gates`: `3 passed in 28.42 s`, the rank-eleven call
26.64 s, no lint findings.  The 26.6 s call is over the local 20 s call ceiling, which the gate
reports and does not enforce.

## 5. What it unblocks

`results/issue370-the-coble-root-orbits.md` §5 uses the call to certify that Sterk's diagram 4.3.9's
model `U + E8(-2)` **is** the boundary lattice `K_J` at that cusp — `is_isometric_to` answers `True`
in 9.0 s and `isometry_matrix_to` returns the witness in 3.1 s.  The transport of the printed roots
themselves uses the library's own embedding `Embeddings.U_E8_2_into_TEn` rather than the returned
witness, because that is *one stated map* rather than one of the `O(K_J)`-many the isometry call may
return, and the two do not give the same root classes: the library embedding gives three root classes
of `K_I` at that cusp, the returned witness one.
