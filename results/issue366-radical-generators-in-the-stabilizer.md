# #366: the setwise stabilizer's generators carry the radical, and the parabolic at P₂ is generated

## The answer

At Sterk's `P_2` of `T_En` (card `029J`):

| quantity | value | how |
| --- | --- | --- |
| `L.Aut().stabilizer(P, action="setwise").group_generators()` | **132** elements | the block-equation family of `parabolic_stabilizer_generators()` (139 elements, 132 distinct), which is the whole parabolic here |
| the radical's block generators inside that family | **17 of 17** | `unipotent_radical_block_generators()`, one per parameter-lattice vector and one for the centre |
| the centre's generator inside it | **yes** | `unipotent_central_generator()` |
| translation rank of the family's radical members | **(16, 16)**, from 42 members | `unipotent_translation_rank`, against the radical's own `2 rank(P₂^⊥/P₂) = 16` |
| the family's central members | **3**, coordinates `2, 1, 0` | `unipotent_central_coordinate` — one of them is a generator of `Z`, and `0` is the identity, which the family also carries |
| `unipotent_radical_index()` | **1** | #365 |
| `is_parabolic_complete()` | **True** | `parabolic_completeness_decision()`: all three factors are 1 |
| `parabolic_obstruction()` | **None** | nothing left to name |

## What the public call returned before, and why it now returns the block family

`O(L).stabilizer(P, action="setwise")` is `Lattices.stabilizer`'s sublattice branch, which
calls `setwise_stabilizer(embedding)`; its generating family comes from the marked-diagram
contract `_marked_automorphism_generators`.  That method hands a primitive isotropic
*plane* marking to the block-equation construction when
`PrimitiveIsotropicSubobjects.is_parabolic_complete()` is `True`, and otherwise to the
indefinite port's `automorphism_group_generators`.

Before this turn the predicate was `False` at `P_2` (it only tested the splitting
hypothesis), so the call went to the port.  `.tmp/qc-evidence/issue366-public-before.log`:
**23 elements in 16.2 s, carrying 1 of the radical's 17 block generators and the centre's
generator** — the issue's item 1 is exactly that shortfall.

The predicate is now a computation (`parabolic_completeness_decision`), it is `True` at
`P_2`, and the call returns the block family, which contains the radical's generators by
construction: **132 distinct elements in 7.0 s once the family was built**, all seventeen
radical generators and the centre's generator among them
(`.tmp/qc-evidence/issue366-completeness.log`).

## The three factors, and the citation

`P_I` maps onto `M \subseteq \GL(I) \times O(I^{\perp}/I)` with kernel `U_I`, so a
subgroup of `P_I` that contains `U_I` is `P_I` exactly when its image is `M` — the
correspondence between the subgroups of a group containing a normal subgroup and the
subgroups of the quotient.  The statement used, and the only one cited, is

> J. S. Milne, *Group Theory*, version 4.01 of 6 November 2025, **Theorem 1.47
> (Correspondence Theorem)**, printed **p. 22**: "there is a one-to-one correspondence
> {subgroups of `G` containing `N`} ↔ {subgroups of `\bar G`}" under
> `H \mapsto \alpha(H)` and `\bar H \mapsto \alpha^{-1}(\bar H)`, with **Corollary 1.48**,
> printed **p. 23**, for the quotient map `g \mapsto gN`.

It was read here, in the copy of Milne's notes downloaded to
`.scratch/refs/milne-gt.pdf` and extracted with `pdftotext`; the proof on p. 23 carries the
step the argument uses, `\alpha^{-1}\alpha(H) = HN`, "which equals `H` if and only if
`H \supset N`".

The three factors at `P_2`, all computed and all `1`:

* `unipotent_radical_index()` — the family contains a generating family of `U_I` (its
  parameter lattice is every parameter that lifts, and it contains a generator of `Z`);
* `levi_plane_action_index(trivial_on_quotient=True)` — every plane action in
  `GL_2(ℤ)` occurs with a *trivial* quotient action, so `M` contains `GL_2(ℤ) × 1`
  (the `\Gamma(2)` certificate: Sanov's two shears and `-1`, plus the mod-2 image of order
  six);
* `levi_quotient_image_index(trivial_on_plane=True)` — the members that fix the plane
  pointwise (the quotient reflections of `quotient_reflection_generators`, 64 of them,
  among others) have images generating all of `O(P_2^\perp/P_2)`, so `M` contains
  `1 × O(P_2^\perp/P_2)`.

`M` is a subgroup of that product and contains both factors, so `M` is the product; the
family's image is `M` and its kernel part is `U_I`, so the family is `P_I`.

At `P_1`, which splits, the answer does not need this: the third block equation reads
`0 = P_3 A Q_3^t` and forces `P_3 = 0` for every quotient action, so the admissible pairs
are already the whole product.

Only the *image* half needs the citation; the radical half needed the same correspondence
statement one level down, and it is cited in `unipotent_radical_block_generators` — where
the previous turn's citation of Robinson, *A Course in the Theory of Groups*, 1.4.6 and
1.3.3, has been replaced by Milne's, because no copy of Robinson is available on this
machine and a citation that cannot be read here is not a citation.

## The two relations that held only in a split basis

`unipotent_radical_rank`'s docstring stated the block conditions as
`\tau + c^t A_K = 0` and `a + a^t + c^t A_K c = 0`.  Those are the equations of a basis
with `J = 1_2` and `K = b(U, K) = 0` — a splitting plane in a unimodular plane basis — and
`P_2` has neither (`J = 2 \cdot 1_2`, and `K` has a nonzero entry).  The docstring now
states what the code solves,

```
A = 1,   τ = -J⁻¹ cᵗ A_K,   J a + aᵗ Jᵗ = -(Kc + cᵗ Kᵗ + cᵗ A_K c),
```

in the ordering of `_unipotent_block_matrix` (`a` the `(P, U)`-block, `c` the `(K, U)`-block,
`\tau` the `(P, K)`-block), and says why the shorter forms do not apply.  The equation in
the #353 report `results/issue353-unipotent-radical-at-p2.md` is corrected the same way,
with a pointer to this turn.

## The test

`tests/lattices/test_the_stabilizer_generators_carry_the_radical.sage`, three tests, all
through `L.Aut().stabilizer(P, action="setwise").group_generators()`:

1. every element of `unipotent_radical_block_generators()` and the centre's generator are
   members of the returned family;
2. the members of the family that fix the plane pointwise and act trivially on
   `P_2^\perp/P_2` — decided on the plane's own basis and by the reduction's own test —
   have translations of the rank the radical's translation image has;
3. some member of the family is a *generator* of `Z`: it fixes `P_2^\perp` pointwise, and
   its coordinate on the centre's generator has absolute value one.

No count, rank or index in it is typed.

## Evidence

| file | what it is |
| --- | --- |
| `.tmp/qc-evidence/issue366-public-before.log` | the public call before the change: 23 elements, 1 of the 17 radical generators |
| `.tmp/qc-evidence/issue366-completeness.py`, `.log` | the probe: the three factors, the predicate and the obstruction at `P_2` and `P_1`, and the public family at `P_2` |
| `.tmp/qc-evidence/issue366-tests.log` | the acceptance run |
| `.tmp/qc-evidence/issue366-lint.log` | `test_lint` on the new and changed test files |
| `.tmp/qc-evidence/issue366-regression.log` | the neighbouring files with the change |
| `.tmp/qc-evidence/issue366-base.log` | the same set on the fetched main without it |

## What this does not claim

The block equations of Dutour Sikirić–Hulek, Theorem 4.9, are an *algorithm* for the
subgroup `M` of integral points (their Alg 1 computes it as a set-stabilizer in
`GL_n(Z/dZ)` plus Schreier's lemma), not a generating set of it; the generation here rests
on the three computed factors and on Milne's correspondence theorem, not on that
algorithm.

`levi_quotient_image_index(trivial_on_plane=True)` needs `P^\perp/P` definite, which holds
at a maximal isotropic plane of a `(2, n)` lattice and fails at a non-maximal one; there
the decision reports `False` with that refusal as the reason, which is what the predicate's
`False` has always meant — not established.  The same holds for a parameter lattice the
enumeration refuses and for a plane action whose `\Gamma(2)` certificate does not settle
the congruence level.
