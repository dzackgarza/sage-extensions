# #616: what the returned plane-stabilizer family is verified to cover, and the one block it is not

**Result of this turn.** The unipotent block and the remaining translations are covered by the
returned family's own members; the quotient action is covered by a finite order comparison.  The
**plane projection onto `GL(Pi)` is not established**, and the reason is narrower than "the argument
is long": the library's Levi plane group is not the set of integral matrices satisfying the equations
read off the Gram blocks it returns, so there is no independent statement of that group to compare
the family's plane actions against.  That is the open step, and nothing below claims completeness.

## 1. What is verified, from the returned family's own members

At a primitive isotropic plane `Pi` of `T_En = U + U(2) + E8(-2)`, the public operation
`TEn.Aut().stabilizer(Pi, action="setwise")` returns the block family.  Filtering that family -- only
its own members, not `unipotent_radical_generators` -- by "fixes `Pi` pointwise and acts trivially on
`I^perp/I`" and reading each member's block coordinates `(c, tau, a)`
(`unipotent_block_coordinates`), the parameters `c` of those members span the parameter lattice:

| plane | returned family | members in the radical | parameter rank | central index | index in `U_I` |
| --- | --- | --- | --- | --- | --- |
| `ZZ e + ZZ Sterk_4` | 163 | (see note) | 16 of 16 | 1 | 1 |
| type `{2,4,5}` | 134 | (see note) | 16 of 16 | 1 | 1 |

Note: the count of radical members is not printed here because the count is not the statement; the
index is.  The computation is the one `unipotent_radical_index` performs, run on the filtered
returned family instead of on `unipotent_radical_generators`; both give `1`, which is what the
containment check added to `parabolic_completeness_decision` was for.

`levi_quotient_image_index(trivial_on_plane=True)` is `1` at both planes: the quotient images of the
members that fix `Pi` pointwise generate the finite group `O(I^perp/I)` outright.

So of the three blocks the family must cover, two are covered by computation on the family itself.

## 2. The open block, in mathematical terms

Let `M = image(P_I -> GL(I) x O(I^perp/I))` and `M_1 = pr_{GL(I)}(M)`.  The family's plane projection
is `A_1 = <g_11(f) : f in F, g_22(f) = 1>`.  Completeness of that block is `A_1 = M_1`.

`parabolic_completeness_decision` obtains `[GL(I) : A_1] = 1` (or a certified congruence value) by
combining three finite facts: the classes of the family's plane actions modulo two, the set
`liftable_plane_action_classes()` -- the classes that admit an integral lift -- and a `Gamma(2)`
certificate inside the group the actions generate.  That reasoning is sound only if

> **(L)** `M_1` is a congruence subgroup of `GL(I)` containing `Gamma(2)`, and its image modulo two
> is exactly the set of classes that admit an integral lift.

**(L) is the unproved step.**  It is not a finite computation on one lattice: it asserts the shape of
`M_1` for every input the decision accepts.

## 3. Evidence that the obvious form of (L) is not the library's `M_1`

`plane_block_gram()` returns the blocks `(H, J, K_0, A)`.  Reading the Levi conditions off the Gram
`s = ((H, J, K_0), (J^t, 0, 0), (K_0^t, 0, A))` gives, for the Levi part `diag(g_11, 1, g_22)`,

    g_11^t J = J,   g_11^t H g_11 = H,   g_11^t K_0 = K_0.

Computed at `ZZ e + ZZ Sterk_4` and at type `{2,4,5}`, `Gamma(2)` -- the subgroup that (L) needs
inside `M_1` -- satisfies the first equation and fails the others, and the returned family's plane
actions do not satisfy the three either.  So these are not the defining equations of the library's
`M_1`: the block convention of `plane_block_gram` and the convention the Levi conditions are stated
in differ, and until that is settled there is no second computation of `[GL(I) : M_1]` to compare
`[GL(I) : A_1]` with.

## 4. What would settle it

1. State `M_1` in the same block convention as `plane_block_gram()` -- the equations above, with the
   convention pinned by the Gram blocks as returned -- and check `Gamma(2) <= M_1` there;
2. then `M_1` is congruence, `M_1 / Gamma(2)` is its image modulo two, `[GL(I) : M_1] =
   |GL_2(F_2)| / |M_1 mod 2|`, and `A_1 <= M_1` with equal indices gives `A_1 = M_1`;
3. the `Gamma(2)`-inside-`A_1` certificate the decision already computes then closes the block.

Nothing in this note is a completeness claim, and the orbit row `(1, 1, 2, 1, 2)` of the eight
antipodal pairs is not used as evidence for one.
