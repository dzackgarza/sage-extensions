# #372: the setwise quotient action at an isotropic plane

`lattices.py:11993` and `:12040` asked the paused indefinite port for
`isotropic_quotient_lift` and `isotropic_quotient_kernel_generators`, which the
pinned port does not ship, so the setwise action `P_I -> O(K_I)` at a plane raised
`AttributeError` at both sites.  Both are now computed here, from the Gram matrix
and the published block form of the integral parabolic.

## The construction

Two factors, as the sources state them.

**Zemel**, *The Structure of Integral Parabolic Subgroups of Orthogonal Groups*,
arXiv:1902.08264v2, section 1: the parabolic at `U` maps onto a Levi quotient
`P_U -> GL(U) x O(W)` with `W = U^perp/U` (**Lemma 1.1, printed p. 5**), its
kernel is the unipotent radical, and the quotient is the semi-direct product in
which `GL(U) x O(W)` acts on that radical (**Proposition 1.6, printed p. 10**, and
**Corollary 1.7, printed p. 12** for the two actions being independent).  So the
class action is the caller's and the plane action is the free coordinate.

**Dutour Sikirić–Hulek**, arXiv:2302.01679v2, **Theorem 4.9, printed pp. 33–34**:
in the basis `(U | P | K)` with `K = P^perp/P` the Gram matrix is
`B = ((H, J, K), (J^t, 0, 0), (K^t, 0, A))`, an isometry preserving `P` is
`((P_1, P_2, P_3), (0, Q_1, 0), (0, Q_2, Q_3))`, and `P B P^t = B` gives

```
J = P_1 J Q_1^t,     K = P_1 J Q_2^t + P_1 K Q_3^t + P_3 A Q_3^t,
H = P_1 H P_1^t + {P_2 J^t P_1^t + P_1 J P_2^t} + {P_3 K^t P_1^t + P_1 K P_3^t} + P_3 A P_3^t.
```

The second equation determines `P_1` from the plane action alone, the third the
`K`-mixing block, and the first is a linear system for `P_2` whose kernel has
dimension `k(k-1)/2` — one for a plane — so its integral solutions are one coset
of a one-parameter family, searched over a complete residue system
(`plane_block_parameter_period`).  The paper's own remark on p. 34 is the
integrality statement used here: *"if we force `Q_1` to preserve the lattice
`L_{J^T}` spanned by the rows of the matrix `J^T`, then `P_1` is integral"*.

So:

| operation | what computes it |
| --- | --- |
| `plane_block_lift(action, quotient_action)` | the three equations above, `Q_3` prescribed, `Q_2 = 0` (no loss: a nonzero `Q_2` differs by an element of the radical), result checked against the pairing and against the class action it was asked for |
| `levi_quotient_lift(class_action)` | the same with the plane action searched over `_plane_action_candidates` |
| `levi_quotient_kernel_generators()` | `ker(P_I -> O(K_I)) = U_I ⋊ Γ'`, `Γ' = {A : a lift with Q_1 = A, Q_3 = 1 exists}`; the family is the radical's generators plus the lifts found, and `Γ'` is pinned by two computed indices (below) |
| `levi_quotient_image_is_all()` | split case: the pointwise block lifts every class action; otherwise `levi_quotient_image_index(trivial_on_plane=True) == 1` |

`Γ'` is bracketed by two indices that are both computed, and the kernel generators
are returned only when they agree: `H = <the plane actions of the lifts found>` is
a subgroup of `Γ'` (`[GL_2 : H]` by the `Γ(2)` certificate of Sanov's generators),
and `Γ'` is a subgroup of `{A : J A^{-t} J^{-1} integral}` — the stabilizer of
`L_{J^T}` above — whose index is the number of classes of `GL_2(ZZ/|det J|)` that
satisfy that congruence, counted directly.  Equal indices force all three groups
to coincide.  Measured: index `1` at Sterk's `P_2` of `T_{En}` (where
`levi_plane_action_index(trivial_on_quotient=True)` independently gives `1`) and at
the `T_{Co}` plane of #360, and index `3` at `P_1`, where `J = diag(1, 2)` makes
`Γ'` the `Γ^0(2)` the library's own docstring names.

## Measured

One process each, in the pinned runtime.

```
T_En P_1:  det J = 2   -1 and the shear lift, the other shear does not; pointwise lift of -1 exists
T_En P_2:  det J = 4   -1, both shears and the swap lift; pointwise lift of -1 exists
T_Co plane (of #360):  det J = 4   the same four lift; pointwise lift of -1 exists
```

The tests, at the change (`TREE=…/wt372` sweep, one module per process,
`-p qc_sage_session -p sage_extensions.testing.suite_budget`):

```
test_the_setwise_action_at_a_plane.sage   4 passed in 124.51 s
  …::test_the_tenriques_plane_row_is_the_card_row  79.11 s > 20 s   (the gate, not an assertion)
test_higher_rank_levi_kernel.sage         1 passed in 4.14 s   (was 1 failed at 72c40a2d69)
test_higher_rank_levi_lifts.sage          3 failed, 5 passed in 34.02 s   (was 8 failed)
test_congruence_levi_images.sage          1 passed
test_subgroup_levi_images.sage            3 passed
```

The five that now pass in `test_higher_rank_levi_lifts` are the ones that ask for a
*lift*: the split transvection, the `T_{Co}`-style split image sections, the glued
plane whose lift moves the null basis, and the rank-zero negation.  The three that
fail are the ones that ask for an *absence* — the quotient exchange at the two
glued planes and the exchange over an infinite quotient — and they fail with the
named refusal of `levi_quotient_lift`, not with a wrong answer.

## Not decided here, and to be filed

* **Absence.** `levi_quotient_lift` searches the seven plane actions
  `_plane_action_candidates` lists and raises when none reaches the class action.
  A refusal is not an absence: the class action may need a plane action outside
  that list, and the three `..._has_no_levi_lift` assertions of
  `test_higher_rank_levi_lifts.sage` are exactly a decision of that kind.  Their
  own docstrings prove absence by a divisibility argument against the pairing
  (`b(f, x) = 1` against `0 mod 3`); the computational form of that argument — a
  necessary congruence on `(Q_1, Q_3)` read off the third equation — is what is
  missing, and it is what would make those three pass.
* **The plane row's cost.** `test_the_tenriques_plane_row_is_the_card_row` asserts
  `2 = card_plane_orbit_row("029J", "O")` and its single call takes 79.11 s: the
  public plane-orbit call at `T_{En}` costs 75.7 s on its own, measured at main
  before this change, so the cost is the plane row's and not the setwise action's.
  The pre-existing `test_the_parabolic_completeness_of_an_enriques_plane.sage`
  trips the same 20 s gate at 87.8 s at main.
* The file `tests/lattices/test_the_setwise_action_at_a_plane.sage` is new and its
  first three tests are cheap (the three planes' image and kernel, under a second);
  only the card row is expensive.
