# #591 — the T_Co discriminant-kernel acceptance, item by item

The contract has four mathematical items and one attribution item. This note
gives each one its smallest deciding probe, its measured answer, and the file
and line the answer lives at. **The generation proof is not delivered**; what
changed is *where* the obstruction sits, and the source statement that carried
the wrong obstruction is corrected (`lattices.py:4457`). Sections 6 and 7 are
the later round: they run both per-generator checks over a family of 24
elements instead of two, and they measure the kernel at two finite levels
(`Γ(2)/Γ(4)` at ranks three to five and eleven, and `Γ(2)/Γ(8)` at rank three),
which is what a generation proof must clear and what the natural family already
clears.

The lattice, measured (`NamedLattices.Tco`, tree `d029087`):

```
rank 11  det -2048  signature (2, 9)  even True
2-elementary True  |A_L| 2048 = 2^11  A_L = (Z/2)^11
rank_2 0  rank_3 11
```

## 1. The attribution item: the owner of the Schreier selection

`NamedLattices.Tco.stable_orthogonal_group()` returns

```
sage_extensions.categories.group.predicate_subgroups.PreimageSubgroups.parent_class
category: Join of Category of preimage subgroups and Category of facade sets
```

not a `KernelSubgroups` object, as the issue comment states:

* the selection is installed in `PreimageSubgroups.ParentMethods.__init__`,
  `categories/group/predicate_subgroups.py:1646`, at the three lines
  `:1655`–`:1657` — `_fix_selected_generating_morphism(self, lambda preimage:
  preimage.schreier_generating_morphism())` under the test
  `not _retains_group_resolution(self) and self.supergroup().has_selected_group_resolution()
  and preimage_morphism.codomain() in OwnedFiniteGroups()` (`:1650`–`:1654`);
* the method it installs is `:1678`, whose body is `:1684`
  `self.coset_space(generators=generators).schreier_generating_morphism()`;
* the construction that consumes the index is `_TransversalCosets.__init__`,
  `categories/group/groups.py:673`, which builds
  `libgap.RightTransversal(...)` (`:677`) — one GAP list entry per coset.

The probe on the object itself:

```
has_finite_coset_space           True
has_selected_group_resolution    True
preimage_morphism().codomain()   Orthogonal group of A_L   cardinality 46998591897600
target_subgroup()                trivial, cardinality 1     (measured in 10.5 s)
```

So the coset space the family is indexed by has order
`46998591897600 = 2^21 3^5 5^2 7 17 31`, one member per element of `O(A_L)`,
and the refusal of `stable_orthogonal_group_generators()` on the same lattice
(`lattices.py:4404`) and this silent selection disagree about whether a
generating family is available. The selection is not a defect in what it
computes — Schreier's lemma really does produce generators — it is a route the
library cannot realize.

## 2. What the group is: T_Co is the double of an odd unimodular lattice

This is the item that changes the shape of the problem, and it is two lines of
linear algebra. Let `M = <1> + U + E8(-1)`, so `G_T = 2 G_M` entrywise
(measured: `True`). Then for an integral matrix `X`,

  `X^T G_T X = G_T`  ⟺  `X^T G_M X = G_M`,

so **`O(T_Co) = O(M)` as subgroups of `GL_11(Z)`**, and, measured,

```
M: rank 11  det -1 (unimodular)  signature (2, 9)  even False
   rank_2 11  rank_3 11  |A_M| 1
```

`M` is the odd unimodular model: `rank_2(M) = 11 >= 6`, it has Witt index two,
it splits off `U + U`, and it represents `-2`. Every one of those is a
hypothesis the issue and the refusal quote — and the group they are hypotheses
about is `O(T_Co)`. `rank_p` is read from a Gram matrix, so it is a property of
the basis-and-rescaling, not of the group: `rank_2` is `0` for `T_Co` and `11`
for `M`, and the two Gram matrices present the same rational form and the same
orthogonal group.

Neither number can be traded for the other. Rescaling the form by `c` gives
Gram `c G_M`, and `G_M` is unimodular with an odd entry on the `<1>` summand:
`rank_2(c G_M) = 0` exactly when `c` is even, and `c` odd leaves `c G_M` not
even. So **evenness and `rank_2 >= 6` are mutually exclusive among rescalings of
this form** — Kneser's `rank_2 >= 6` hypothesis can never be met by an even
lattice presenting this group, which closes the one repair the recorded
reasoning left open ("find another basis").

What survives of the refusal is therefore parity, not rank: `|A_L| = 2^11`
gives `L = 2L^#`, hence `Õ(T_Co) = ker(O(L) -> O(L/2L)) = ker(O(M) -> O(M/2M))`,
the principal congruence subgroup of level two of the **odd** unimodular
`M = I_{2,9}`. The statements the library cites (Allcock's Theorem 1.1,
Kneser's theorem and Gritsenko–Hulek–Sankaran Proposition 3.4 as quoted there)
are stated for even lattices, or for `Λ(2)` of rank ten; none has these
hypotheses.

## 3. The per-generator checks

Two checks are demanded of every generator, and both exist and run here.

* **Integral isometry.** `L.integral_isometry` (`lattices.py:4149`) descends a
  rational isometry onto `L` and refuses one that does not preserve it. For a
  candidate written as a matrix, the check is `X^T G_T X = G_T`; for the two
  elements below it is an equality of integral matrices.
* **Trivial discriminant action.** `element.discriminant_morphism() ==
  trivial`, the check the refusal already performs on its own family at
  `lattices.py:4594`.

On `T_Co` that second check has a cheaper exact form, and this is worth
recording because the acceptance asks for it "for each generator" on a group
whose discriminant action cannot be enumerated: `|A_L| = 2^rank` gives
`L = 2L^#`, so `g` acts trivially on `A_L = L^#/L` exactly when
`g ≡ 1 (mod 2L)`, i.e. when every entry of `X - I` is even. Verified, through
the library, on two elements (probe `7.34 s`):

```
root reflection in h   built; discriminant image trivial True; in S True; order two True
-1                     built; discriminant image trivial True; in S True; order two True
```

(`h` is the `<2>` generator: `q(h) = 2` and `b(h, x) = 0` for every other
module generator, so its reflection is the `<2>` sign change.) Every norm-two
vector of `T_Co` gives such an element, since `v in L = 2L^#` forces
`(v, L) ⊂ 2Z` and hence `s_v ≡ 1 (mod 2L)`; the root system of an indefinite
lattice is infinite, so this is a certified *subfamily*, never a generating
set, and it is not stored as one. §6 runs both checks over a family of 24 such
elements rather than two, and adds the control that shows the second check is
not vacuous.

## 4. The generation proof: not delivered

`Õ(T_Co)` is a level-two congruence subgroup of an odd unimodular lattice of
rank 11 and Witt index 2. Nothing in this repository proves it generated by a
finite set, and this note does not supply one. What can be stated exactly:

* **The generic route cannot be repaired.** Schreier's lemma writes one word per
  coset of `O(L)/Õ(T_Co)`; that number is `46998591897600` (measured above), and
  `_TransversalCosets.__init__` (`groups.py:673`) materializes one entry per
  coset before any word is written. A family indexed by that transversal has
  `4.7 * 10^13` members before the word length is counted — the selected
  generating family of `O(T_Co)` is `251` elements, measured here in `262.6 s`
  (`L.Aut().group_generators()`; an earlier record of this count said `196`),
  so the family has `1.18 * 10^16` words — and the route is not slow, it is
  unavailable: no resource budget makes it return.
* **Every cited statement fails on parity, not on rank**, per §2. The one
  published family the issue names (Dutour Sikirić–Hulek, Lemma 4.2, the
  subgroup generated by `SL_2(Z)^2` and Eichler transvections) is asserted
  finite-index and is not a generation statement, so under the acceptance's own
  last clause it may not be stored.
* **A proof must therefore be a level-two generation theorem for the odd
  unimodular `I_{2,9}`** — `O(M)` generated by reflections in odd-norm vectors,
  or `Γ(2)` generated by elementary orthogonal transvections, with the
  finite quotient `Γ(2)/E(2)` computed rather than enumerated. Neither is
  claimed here.

Consequence for the database field: `arithmetic-group.otilde-t-co.generator_morphisms`
stays absent, and the sentence the certificate carries should now say the group
is the level-two kernel of the odd unimodular `I_{2,9}` whose `rank_2` is 11,
not that `rank_2 = 0` blocks every transvection statement.

## 5. The source change

`stable_orthogonal_group_generators`'s docstring (`lattices.py:4457`) concluded from
`rank_2(T_Co) = 0` that "it contains no hyperbolic plane and no theorem of
transvections or reflections reaches `Õ(L)`". The second clause reads a
Gram-matrix invariant as a group-theoretic one, and §2 shows the group it is
read for is `O(I_{2,9})`, whose `rank_2` is 11 and which splits off two
hyperbolic planes. The refusal stays; the reason is restated as parity, with the
rescaling argument that closes it. No computed value changes, so no test can be
red: `rank_p` is read only in this message and in its own docstring
(`grep -n 'rank_p(' src/`), and no branch depends on it.

## 6. The per-generator checks on a family, not on two elements

`results/issue591-the-kernel-levels.py` is the probe behind this section and
§7; it runs in one process in the pinned image. Part 1 builds a family inside
`Õ(T_Co)` and checks each member twice — exactly an isometry of `L` (its column
matrix `M` satisfies `M^T G_T M = G_T` on the lattice's own Gram matrix, and the
coordinate vector of every image rebuilds that image), and exactly in the kernel
(every entry of `M - 1` even, which for `|A_L| = 2^rank` is the trivial action on
`A_L`) — and the library's own `discriminant_morphism()` identity. The family is
the reflections at the norm-two vectors `h + v` (`h` the `<2>` generator, `v`
isotropic in `U(2) + E8(-2)`: the two `U(2)` basis vectors), the reflection at
`h`, `-1`, and the integral Eichler transvections `t(v, a)` with `a ⟂ v`:

```
   rank 11  det -2048  signature (2, 9)  |A_L| 2048
   rank of (G/2) mod 2 11  level-four available dimension 66
   family size 24; every member: isometry of L, == 1 (mod 2L), rho trivial
   family level-four span 11
   control: the reflection at the norm--4 root e_a1 is an isometry True and is the identity mod 2L False
   ... (the eight simple roots of E8(-2), all eight the same)
```

The control is the point of the second check: a reflection at a norm-`-4` root
of the `E8(-2)` summand *is* an isometry of `L` and is *not* the identity modulo
`2L`, so `M - 1 ≡ 0 (mod 2)` is a real condition and not a restatement of being
an isometry. What the family certifies is membership; it is a subfamily of an
infinite root system and is not stored as a generating set, per the acceptance's
last clause.

## 7. The levels of the kernel: what a generation proof has to clear, measured

Two facts make a finite piece of `Õ(T_Co)` computable exactly.

* **The level-four quotient is elementary abelian.** For `M = 1 + 2A` one has
  `(1+2A)(1+2B) = 1 + 2(A+B) (mod 4)`, so `Γ(2)/Γ(4) → M_n(F_2)`, `M ↦ (M-1)/2
  (mod 2)`, is a homomorphism onto an `F_2`-space: the image of a subgroup is a
  subspace and the image of a generating set is the span of its members'.
* **An exact isometry satisfies one quadratic equation there.** With
  `G_T = 2H` and `M = 1 + 2A`, the condition `M^T G_T M = G_T` reads
  `A^T H + H A + 2 A^T H A = 0`, so modulo two `A^T H̃ + H̃ A = 0`. That space
  has dimension `n(n+1)/2`: `6`, `10`, `15` at ranks three, four, five and
  `66` at rank eleven.

Part 2 measures the whole kernel's image against the §6 family's, at the ranks
where an exact generating set is available (`|O(A_L)| = 2, 8, 72`, so Schreier's
family over `O(A_L)` returns); part 3 compares the two subgroups they generate
inside `O(L/8L)`, through the action on the 512 vectors of `L/8L`:

```
   rank 3: |A_L| 8   |O(A_L)| 2   level-four available dimension 6
      exact family: 8 elements, level-four span 3
      the family : 8 elements, level-four span 3
   rank 4: |A_L| 16  |O(A_L)| 8   level-four available dimension 10
      exact family: 96 elements, level-four span 4
      the family : 10 elements, level-four span 4
   rank 5: |A_L| 32  |O(A_L)| 72  level-four available dimension 15
      exact family: 1872 elements, level-four span 5
      the family : 12 elements, level-four span 5
== part 3: the two subgroups inside O(L/8L), rank 3
   exact family: 8 generators on 512 points, order 64
   the family: 8 generators on 512 points, order 64
   the family is contained in the exact family: True
   the exact family is contained in the family: True
```

Three statements, and one thing that is *not* stated.

1. The whole kernel's image at level four has dimension exactly `n`, at each of
   ranks three, four and five — not the `n(n+1)/2` the isometry condition
   allows. The level-four layer of `Õ` is one dimension per rank.
2. The §6 family's image has the same dimension at every one of those ranks, and
   dimension `11 = n` on `T_Co` even though the kernel's own image cannot be
   measured there. So no level-four dimension separates the natural family from
   a generating set, and the same holds at level eight at rank three, where the
   two subgroups of `O(L/8L)` coincide.
3. A completeness proof therefore cannot be assembled from these quotients, and
   a disproof has to be either structural or at a level no computation run here
   witnesses (rank four at level eight is a permutation degree of `65536`).

What is not stated: that the family generates. Spanning a quotient is necessary,
never sufficient, and nothing above is a generation statement — the acceptance's
first item stays undelivered for the reason §4 gives.



## The runs

The first two probes ran inside the pinned image (`Sage 11.0.beta5`, port
`991b88b0`) against tree `d029087`, the base the first two commits were rebased
from, one job at a time, `PEAKRSS_LIMIT_MIB=6144`; that commit is docstring-only,
so no measured value depends on it:

```
probe-issue591    T_Co and M invariants, the preimage owner, |O(A_L)|   13.3 s to the index
probe-issue591b   the two per-generator checks through the library       7.34 s
```

The sections 6 and 7 runs are the committed script, on tree `93b5dbb`, in the
same image, one process, `timeout 1200`, stdout redirected:

```
~/sage-image/run.sh -w /work -b <tree>:/work -b ~/ai-review-ci:/ci -- \
  /bin/sh -c 'export HOME=/root;
    export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work;
    /sage/.venv/bin/python -u /work/results/issue591-the-kernel-levels.py'
exit 0, 290.9 s
```

Peak tree RSS 340 MiB on the second probe. The tests of the two touched
behaviours are `tests/lattices/test_the_stable_orthogonal_group_generators_refuse.sage`
and `tests/lattices/test_the_coble_lattice_carries_no_generating_set.sage`.
