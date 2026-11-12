# #373: the setwise quotient lift is decided over all of `GL(I)`

`levi_quotient_lift` (`src/sage_extensions/categories/isotropic_parabolics.py`)
searched seven plane actions, `_plane_action_candidates`, and raised when none of
them reached the class action.  `GL(I) = GL_2(ZZ)` is infinite (Zemel,
arXiv:1902.08264v2, Lemma 1.1 printed p. 5 and Proposition 1.6 printed p. 10), so
that refusal decided nothing, and the three `..._has_no_levi_lift` tests of
`test_higher_rank_levi_lifts.sage` -- which ask for an absence -- failed on it.
The call now decides over the whole of `GL_2(ZZ)` and answers one of three
things: an element of `P_I` inducing the prescribed class action, a named
`LeviQuotientLiftAbsent` carrying the congruence that fails, or -- only when the
congruences are satisfiable and the one equation left undecided has no integral
solution at any of the classes returned -- a `NotImplementedError` naming that
equation.  `_plane_action_candidates` is deleted.

## The reduction, and where each step is cited

The block form is Dutour Sikirić–Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
**Theorem 4.9 and its proof, printed pp. 33–34**.  In the basis `(U | P | K)` of
`plane_block_basis` the Gram matrix is `((H, J, K), (J^t, 0, 0), (K^t, 0, A))`,
an isometry preserving the plane `P` is `((P_1, P_2, P_3), (0, Q_1, 0),
(0, Q_2, Q_3))` with `Q_3 A Q_3^t = A`, and `P B P^t = B` is the three equations

```
J = P_1 J Q_1^t,  K = P_1 J Q_2^t + P_1 K Q_3^t + P_3 A Q_3^t,
H = P_1 H P_1^t + {P_2 J^t P_1^t + P_1 J P_2^t} + {P_3 K^t P_1^t + P_1 K P_3^t} + P_3 A P_3^t.
```

1. **The plane action is free and the class action is the constraint.**  `Q_3` is
   the class action read on the `K` block, `Q_1` the plane action; `Q_2 = 0`
   loses nothing, because an element with `Q_1 = Q_3 = 1` and `Q_2 ≠ 0` lies in
   the unipotent radical, so the question is a condition on `Q_1`.

2. **`(E_2)`.**  The second equation determines `P_1 ∈ GL_k(QQ)` uniquely
   (printed p. 33), and the paper states the integrality criterion itself
   (printed p. 34): `J^t = Q_1 J^t P_1` gives `P_1^{-1} = (J^t)^{-1} Q_1 J^t`, so
   *"if we force `Q_1` to preserve the lattice `L_{J^T}` spanned by the rows of
   the matrix `J^T`, then `P_1` is integral"*.  It is read modulo `D = |det J|`,
   because `P_1 = J Q_1^{-t} adj(J)/D` and the numerator is a polynomial in the
   entries of `Q_1`.

3. **`(E_3)`.**  The third equation determines `P_3 ∈ M_{k,n-2k}(QQ)` uniquely
   (printed p. 33), and the paper bounds it (printed p. 34): *"there exists a
   denominator `d_3` such that `P_3 ∈ (1/d_3) M_{k,n-2k}(Z)`, for example
   `d_3 = |det(A)|`"*.  With `Q_2 = 0` and `E = |det A|` the condition is the
   congruence `(K Q_3^{-t} - P_1 K) adj(A) ≡ 0 (mod E)`.

4. **The coupling is linear, so the plane actions are a finite residue system.**
   With `U = Q_1^{-t}` (a bijection of `GL_2(ZZ)`) and `Omega = adj(J) K`, step 3
   reads

   ```
   Omega Q_3^{-t} adj(A) ≡ U Omega adj(A)  (mod E),
   ```

   because `adj(J)(K Q_3^{-t} - P_1K)adj(A) = Omega Q_3^{-t}adj(A) - U Omega
   adj(A)` and `adj(J) J = D`.  Its solutions are a coset of the square of the
   row-syzygy module of `Omega adj(A)` (`_row_congruence_coset`, Smith normal
   form), so `(E_2)` and `(E_3)` are both read modulo a modulus dividing
   `lcm(D, E)`, and `_general_linear_classes` covers every class of `GL_2(ZZ)`
   modulo that level.  One plane action per class satisfying both is therefore a
   **complete** description of the plane actions an integral lift can have, and an
   empty answer is a theorem about `GL_2(ZZ)`, not the exhaustion of a search.
   This is the shape Zemel gives the integral parabolic: arXiv:1902.08264v2,
   **Proposition 3.2 printed pp. 21–22** and **Theorem 3.4 printed p. 24** -- the
   image is `SL(I_{L*}, I) × Γ_Λ`, the plane actions confined to a congruence
   subgroup of `SL(I)` and the class actions otherwise free -- with the
   `ψ`-coordinate of the radical's part in the coset of `Hom(Λ, I)` modulo
   `Hom(Λ*, I)` that `b_M = (id_U − M)∘ι*` picks out (**Proposition 3.5 printed
   p. 25**): a class in a finite group, which is `(E_3)` above.

5. **The first equation is solved, not assumed.**  The right side of the system
   `(13)` is symmetric, so it has the rational solution `X = remainder/2`, and its
   kernel has dimension `k(k−1)/2` = 1 for a plane (printed p. 34); at one plane
   action its integral solutions are one coset of that one-parameter family, which
   `plane_block_parameter_period` covers completely.  The paper's denominator
   `d_2 | 2 d_3^3` bounds them only by `(1/d_2)M_{k,k}(Z)` -- a finite-index
   condition on the plane action, not an identity -- so `P_2` is solved exactly at
   each class over the complete residue system of the parameter, and the element
   built is verified to be an isometry inducing the prescribed class action.

## The change

`isotropic_parabolics.py`:

* **new** `LeviQuotientLiftAbsent(ValueError)` -- the named absence (exported from
  `all.py`).
* **new** `_general_linear_classes(m)` -- one integral matrix of determinant `±1`
  per class of `GL_2(ZZ/m)`, by a breadth-first walk over the two shears; the
  reduction `GL_2(ZZ) → GL_2(ZZ/m)` is not onto for `m ≥ 3`, so the sign is
  carried explicitly.
* **new** `_unimodular_lift(entries, m)` -- an integral matrix of determinant `±1`
  in a prescribed class, built by shifting the first column to coprime entries and
  running the Euclidean algorithm.
* **new** `_row_congruence_coset` / `_coset_elements` -- the solutions of
  `z · rectangle ≡ target (mod m)` as a coset, by Smith normal form, and an
  enumeration of the coset.
* **new** `_chinese_remainder_matrix` -- the class modulo `lcm(m_1, m_2)` of two
  compatible classes, for the case where neither level divides the other.
* **new** `plane_action_congruence_classes(quotient_action)` -- the derivation above
  in the docstring, with each step's printed page; returns the finite set, or
  raises `LeviQuotientLiftAbsent`.
* `levi_quotient_lift` -- searches that set together with
  `_elementary_plane_actions`, ordered by height, solves the first equation at
  each class and returns the first verified lift.
* `_elementary_plane_actions` -- the seven-matrix *generating* list the kernel's
  `Γ(2)` certificate needs; documented as not a decision device.
* the block's `Q_3` is now `quotient_block_matrix(γ)^t`: the paper uses the action
  on row vectors from the right, so the block entry is the transpose of the
  column-vector matrix on the `K` block.  The old path passed the frame matrix and
  tried both transposes; the two agree only when the frame is the `K` block, which
  is why that path worked at the planes measured before and not at the split
  `3U + <2>` plane, where the transvection needed the transpose.

`lattices.py`: `_levi_image_contains` answers `False` exactly on
`LeviQuotientLiftAbsent`, and lets the undecided-`P_2` `NotImplementedError`
propagate.

## Measured

One process each, pinned runtime, worktree `.scratch/wt373` at `28422f9`.  `D` and
`E` are `|det J|` and `|det A|`; `classes` is the size of the plane-action residue
system that satisfies `(E_2)` and `(E_3)`.

```
plane                         D   E    classes  identity/minus   exchange
TEn P1 (split)                2  256        2    lift 0.4 s      --
TEn P2 (non-split)            4   64       96    lift 0.4 s      --
T_Co plane of #360            4  128       96    lift 0.3 s      --
glued3 + U + <2>              3   18      972    lift 0.2 s      absent
glued2 + U                    2    4       32    lift 0.1 s      absent
glued2 + 2U                   2    4       32    lift 0.2 s      absent
```

The three exchanges are decided by the third equation: its linear congruence has
no solution at all (`glued3 + U + <2>` and `glued2 + 2U`), or none compatible with
`(E_2)` (`glued2 + U`).  That is the computational form of the divisibility
argument the three docstrings give by hand (`b(f, x) = 1` against `0 mod 3`, and
the parity of the `v` coefficient).

At the three planes of `#372`'s test the gluing block `Omega adj(A)` vanishes
modulo `|det A|` (`K = 0` at split `TEn P1`; `|det A| = 64` with content 128 at
`TEn P2`; `|det A| = 128` with content 256 at the `T_Co` plane), so there `(E_3)`
holds for every plane action that reaches `(E_2)` and the residue system is
`{Q_1 : Q_1` preserves `L_{J^T}}` modulo `|det J|`.

## Test results

`/sage/.venv/bin/python -m pytest <module> -q -o addopts='' -p qc_sage_session -p
sage_extensions.testing.suite_budget`, one module per process, at the change:

```
test_higher_rank_levi_lifts.sage                            8 passed in 33.97 s
test_higher_rank_levi_kernel.sage                            1 passed in 5.20 s
test_congruence_levi_images.sage                             1 passed in 10.49 s
test_subgroup_levi_images.sage                               3 passed in 11.31 s
test_the_plane_stabilizer_reaches_the_whole_quotient_group   1 passed in 119.82 s
test_setwise_stabilizer_discriminant_images.sage             2 passed in 50.66 s
test_the_setwise_action_at_a_plane.sage                      4 passed in 123.05 s
test_the_parabolic_completeness_of_an_enriques_plane.sage    4 passed in 131.46 s
```

and at `28422f9` (worktree `.scratch/wt372`) for the two modules whose cost the
gate flags:

```
test_higher_rank_levi_lifts.sage                            3 failed, 5 passed in 34.56 s
  gate: test_null_plane_levi_image_generators_realize_both_signs_on_a_line 29.87 s
test_the_plane_stabilizer_reaches_the_whole_quotient_group   1 passed in 146.17 s
  gate: test_the_plane_stabilizer_reaches_the_whole_quotient_orthogonal_group 145.53 s
```

So the three `..._has_no_levi_lift` assertions pass with their text unchanged
(they failed on `not in image`; `_levi_image_contains` now answers `False` on a
proved absence), and the `29.79 s` / `119.38 s` gate reports are pre-existing
costs, not this change's.  The `81.57 s` card row of
`test_the_setwise_action_at_a_plane.sage` is `#374`'s (75.7 s at main, 79.11 s at
`#372`).

## Not decided here, and not verified

* **The first equation `(13)` at a plane action.**  A class that satisfies
  `(E_2)` and `(E_3)` but whose `P_2` equation has no integral solution makes the
  call raise `NotImplementedError` naming `(13)`, with the paper's `d_2 | 2 d_3^3`
  as the modulus at which that equation would have to be decided; absence is not
  claimed there.  No plane of this repository reaches that branch, so it is
  present and untested.
* **The case where neither congruence level divides the other.**  When
  `|det J|` does not divide `|det A|` and vice versa, the two conditions are
  intersected by Chinese remainder (`_chinese_remainder_matrix`).  All six planes
  measured here have `|det J|` dividing `|det A|`, so that branch is untested as
  well.
* **A lift that only a plane action outside the elementary seven reaches** is
  found by the decision whenever one exists, because the set searched is complete;
  no test here exercises such a case, since at every plane measured the first
  small action already lifts.

## To be filed

`isotropic_parabolics.py` cites Theorem 4.9 as "printed p. 22" in eleven
docstrings (`plane_block_basis`, `plane_block_gram`, `plane_block_lift`,
`levi_lift_generators`, `parabolic_completeness_decision`, and others).  In
arXiv:2302.01679v2 the theorem and its proof are on printed pp. 33–34, and the
sentences those docstrings quote ("the second equation determines `P_1` ...", "a
denominator `d_3` ... `d_3 = |det A|`") are on printed pp. 33–34; what is on
printed p. 22 is Lemma 4.7 and Theorem 4.8.  The pages in this change are the
correct ones, and the older citations are left alone here.
