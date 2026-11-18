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

## 6. Re-decided against the level-four theorem

The five items below are decided on this tree. None of them is a generation
proof, and the one that would be is stated as open with its exact statement.

| item | state | where |
|---|---|---|
| the preimage owner | decided: `PreimageSubgroups`, not `KernelSubgroups` | `predicate_subgroups.py:1646`, install `:1655`-`:1657`, method `:1678`/`:1684`; the index it consumes at `groups.py:673`/`:677` |
| integral isometry, per generator | delivered | `tests/lattices/test_the_coble_kernel_candidates_pass_the_generator_checks.sage`, `lattices.py:4149` is the descending check the library owns |
| trivial discriminant action, per generator | delivered | same file; the library's own assert for a constructed family is `lattices.py:4594` |
| a generating family, provably complete | **open** | `stable_orthogonal_group_generators`, `lattices.py:4404`, refuses; nothing is stored as a generating set |
| no coset enumeration in the proof | delivered for the level-four statement | `\Gamma(2)/\Gamma(4) \cong (\mathbb{Z}/2)^{56}` by linear algebra in 56 dimensions, not by the 46 998 591 897 600-coset transversal |

**The 56 candidates.**  The test file carries 56 vectors of square `\pm 2` in
`T_Co`'s own form, i.e. of square `\pm 1` in the odd unimodular half, in the
catalogue's basis; it builds each reflection with `L.reflection`, which is the
library's own integral reflection, checks the displacement of every generator
against the reflection formula, and asserts for every one that its discriminant
image is trivial and that it lies in `stable_orthogonal_group()`.  The family is
not stored anywhere else and is not the value of any field: a candidate whose
completeness is open is not a generating set.  What makes the family worth
carrying is the level-four statement: with `X = I + 2A` the exact identity
`A^T G_M + G_M A + 2 A^T G_M A = 0` forces, after the divided diagonal, the row
sums `\sum_{k \ne i} A_{ik} = 0` beside symmetry, ten independent conditions on
the 66-dimensional symmetric space, so `\Gamma(2)/\Gamma(4)` is
`(\mathbb{Z}/2)^{56}`; the 56 classes of the candidates were checked to be
independent, hence they generate `\Gamma(2)` modulo `\Gamma(4)`.

**What that does not give, and why it cannot be upgraded cheaply.**  A family
that generates modulo `\Gamma(4)` generates only if `\Gamma(4)` is inside the
subgroup it generates.  Two facts bound that: the reflection classes span all
56 dimensions, so no level-four computation can separate the family from
`\Gamma(2)`; and no finite-level computation can, since `H\cdot\Gamma(2^k) =
\Gamma` for every `k` is compatible with `H` of infinite index (`3\mathbb{Z}`
inside `\mathbb{Z}` with the `2`-power filtration).  The statement that would
close it is `\Gamma(4) \leq \langle S\rangle`, equivalently that the maximal
elementary abelian quotient of `\Gamma` is exactly `\Gamma/\Gamma(4)`; if it
holds, the Frattini argument turns the 56 candidates into `\Gamma = \langle S\rangle`
outright.

**The database end, measured.**  `tests/cards/lattice-database-enriques.json`
lists the arithmetic-group rows as `data.cardinality`,
`data.abstract_structure`, `data.line_orbits`, `data.plane_orbits`,
`data.flag_orbits`, `data.reference.citation`, `latex`, `lattice` and
`parent_group`; `data.generator_morphisms` is not among them, so the field is
absent at both ends — the library refuses to produce it and the digest this
repository reads would not carry it if it did.

## 7. Level eight: the ceiling of the reflection mechanism

`results/coble-kernel-level-eight.py` computes, exactly and with no engine, what the
reflections reach one level below the level-four statement. A reflection in a vector of
square `\pm 1` is an involution, so squares contribute nothing to `\Gamma(4)/\Gamma(8)`;
a product of two reflections lies in `\Gamma(4)` exactly when the two vectors agree
modulo two.

```
commutators of the 56 candidates          1540 classes, span 54
two-fold reflection products              2016 classes, span 54   (six unit vectors per class)
commutators and two-fold products                           span 54
four-fold reflection products (sampled)                     span 54
```

(An independent run over 3584 two-fold products, eight vectors per class, gave the same
54, and 67 four-fold products also stayed inside it; the counts move with the sample, the
dimension does not.)

So one 54-dimensional subspace of the level-four class space contains **every** reflection
product sampled, including classes produced by four-fold words that are not commutators.
The class space itself is 54- or 55-dimensional: 55 is the alternating-space bound, 54 is
what these products reach.

That makes the remaining question binary and decidable by one computation:

* if the level-four class space is 55-dimensional, then **no subgroup generated by
  reflections in square-`\pm 1` vectors is all of `\Gamma`**, the 56 candidates do not
  generate, and any generating set must carry an element outside the reflection mechanism;
* if it is 54-dimensional, the reflections are level-eight complete and the missing step
  is one level deeper.

Deciding it needs one explicit element of `\Gamma(4)` whose class lies outside the
54-space: `X = I + 4Y` with `Y` integral and `Y^T G_M + G_M Y + 4Y^T G_M Y = 0`, solved for
`Y` in a class the reflections cannot reach. That lifting is a linear system modulo four in
121 unknowns per class, and it is the next computation to run — noted here rather than
claimed.

What this settles for the acceptance: the reflection family, which is the only family the
literature supplies for this lattice, is capped at level eight by a 54-versus-55 count. The
database field stays absent either way, and nothing is stored as a generating set.

## 8. Conjugating the level-four span by isometries outside the kernel

The reflection span at level four is normalised by nothing on its face: a conjugate of a
level-four element by *any* isometry of `M` is again level four, so an isometry outside
`\Gamma` could carry a class out of the 54-dimensional span and settle the 54-versus-55
question in the negative. Ten such isometries were tried, each checked to be an integral
isometry of `M` with a nontrivial image modulo two: the eight reflections in the `E_8`
coordinate vectors of square `-2`, the swap of the two hyperbolic coordinates, and the
product of the swap with one of the `E_8` reflections. Every one of the 1540 commutator
classes was conjugated by each, and the span stays **54** in all ten cases: no class left
the span.

So the conjugation mechanism does not produce the missing dimension. What remains is the
lifting congruence itself: find `Y` integral with `Y^T G_M + G_M Y + 4Y^T G_M Y = 0` whose
class modulo two lies outside the 54-space, or prove no such `Y` exists. Two facts bound
it and are worth recording with the search: every level-four class is alternating (the
55-dimensional bound), and every reflection product so far — commutators, two-fold words,
four-fold words, and all ten conjugates — lies in the same 54.

## The run of the level-eight script

`python3 results/coble-kernel-level-eight.py` completes from the repository root and
reproduces every number above: the reflection span `54` from `1540` commutators, the
two-fold and four-fold products inside it, and the conjugation stage reporting
`isometries outside Gamma that move a level-four class out of the span: 0` for all ten
isometries. Measured at load 35: `exit 0`, 8 min 37 s wall; the arithmetic is exact
integers and no engine is loaded.

Why no reflection word escapes the 54, as an argument rather than a sample. The classes of
the 56 reflections are a basis of the level-two class space, so a word in reflections lies
in `\Gamma(4)` exactly when its class sum vanishes; modulo `\Gamma(8)` such a word reduces to
a product of commutators and squares of the generators, and squares of reflections are the
identity. Hence every reflection word's level-four class is a sum of commutators of the
basis classes, which is the 54-dimensional span computed above — reached by 1540
commutators, and not exceeded by two-fold words, four-fold words, ten conjugations, or the
3182 unit vectors across 56 classes that were searched for a vanishing three-fold class sum
(none exists: a sum of two distinct basis classes is not a reflection class).

The ambient side is not a lifting problem in disguise. `\Gamma(4)/\Gamma(8)` is the
level-four modulo level-eight congruence quotient of `O(M)(Z_2)`, whose dimension is the
alternating-space bound 55; the question is whether the *global* points `O(M)(Z)` fill that
quotient or only its 54-dimensional reflection part. That is exactly what Kneser's strong
approximation theorem decides for a simply connected isotropic group: `\operatorname{Spin}(M)`
is simply connected and `M` has Witt index two, so if the theorem applies in the form that
`O(M)(Z)` surjects onto every congruence quotient of `O(M)(Z_2)`, then the quotient is the
full 55 and **no subgroup generated by reflections is `\Gamma`** — the 56 candidates
included.

What this repository needs for that step is one input it does not carry: the statement of
strong approximation for `\operatorname{Spin}(I_{2,9})` with its hypotheses and printed
page, in the form that gives surjectivity onto the level-four quotient. Every other step of
the fork is decided here; that citation is not, and without it the 54-versus-55 question
stays open by exactly this much.

The citation this needs, and how far a search got. The theorem is Kneser's strong
approximation (`[Kne66]`, *Starke Approximation in algebraischen Gruppen*, J. Reine Angew.
Math.), which is applied to lattices in exactly this way in the opening pages of
G. Chenevier, *Statistics for Kneser p-neighbours*, arXiv:2104.06846, where the reduction
is stated as: strong approximation plus a single spinor genus in the genus gives the
transitivity of the isometry class under the local data, and the paper notes that its
Theorem 7.10 covers odd unimodular lattices as well. For `M = I_{2,9}` the genus is a single
class (odd unimodular lattices are determined by rank and signature), so the spinor genus
is one too.

What is still missing is not the reference but the statement in the form used here:
surjectivity of `O(M)(Z)` onto `O(M)(Z_2)` modulo the level-eight subgroup, i.e. through the
double cover `\operatorname{Spin}(M)\to O(M)` with the component group accounted for. That
is the one input this repository does not carry, and the level-four 54-versus-55 question
waits on it.

The statement itself, now in hand. G. Chenevier, *Statistics for Kneser p-neighbours*,
arXiv:2104.06846v2, states it as his Lemma 3.4 (p. 11), "a reformulation of Kneser's strong
approximation theorem for Spin groups [Kne66]": for a non-degenerate quadratic space `V`
over `Q` with `dim V >= 3` and a prime `p` with `V_p` isotropic, the proof uses

    Spin_V(A_f) = Spin(V) . K' . Spin(V_p),

and the corollary used there is Corollary 3.7 (p. 13): when no exceptional set of primes is
needed the spinor class group `\Sigma(K)` is trivial, and in general `\Sigma(K)` sits in
`(\mathbb{Z}/N_T)^\times/(\mathbb{Z}/N_T)^{\times 2}` for the set `T` of primes at which the
level structure is imposed. For `M = I_{2,9}` the space is isotropic at every p, the genus is
a single class, and Section 5.5 of the same paper records the consequence used here: when
`V_\infty` is isotropic, `s : X(K) \to S(K)` is bijective, so the level structures of a
congruence level form as many classes as `S(K) = \Sigma(K)^*` has.

So the fork is not strong approximation after all; it is the order of the spinor class group
at the level-eight structure, which Corollary 3.7 bounds by
`(\mathbb{Z}/8)^\times/(\mathbb{Z}/8)^{\times 2}` when only the prime 2 is exceptional. That
finite group is the last object to compute, and it decides whether the level-eight quotient
has one class (the reflections are level-eight complete at 54) or more (they are not, and the
56 candidates fail).

What is recorded here is the theorem with its locus and the reduction to `\Sigma(K_8)`; the
order of that group is not computed in this repository.

The spinor class group at level eight, evaluated. Chenevier's (3.3)-(3.4) split
`S(K) = \Delta/\iota(O(V)K)` into `\Delta_1(K) = (A_f^\times/A_f^{\times2})/\langle Q_{>0},
\operatorname{sn} K^\pm\rangle` and `\Delta_2(K) = \{\pm1\}^P/\langle\pm1, \det K\rangle`.

* `\Delta_1(K) = 1`: `\operatorname{sn} : O(V) \to Q^\times/Q^{\times2}` is onto when `V` is
  isotropic and `\dim V \ge 3` (Lemma 3.1, from O'Meara), and the positive rationals map onto
  `A_f^\times/A_f^{\times2} = \oplus_p \mathbb{Z}/2` because any finite parity pattern is
  realised by a positive rational. So the first quotient is trivial for every `K`.
* `\Delta_2(K) = 1`: the level-eight condition bites only at `2`, so `K_p = O(L_p)` at every
  odd `p`, and `\det O(L_p) = \{\pm1\}` for a unimodular `L_p`; hence `\det K = \{\pm1\}^P`.

So `S(K) = 1` for the level-eight structure, and by (5.6) with `V_\infty` isotropic the
class set `X(K)` is a single point: `O_V(A_f) = O(V)K_8` — the level structures form one
class. Taking `g` in the level-four subgroup of `O(M)(Z_2)`, `g = \gamma k` with `\gamma` in
`O(V)` and `k \in K_8` gives `\gamma \in O(M)(Z) \cap K_4 = \Gamma(4)` and `\gamma \equiv g`
modulo eight; every level-four class is therefore global.

**Consequence.** `\Gamma(4)/\Gamma(8)` is the full 55-dimensional class space, one dimension
more than the 54 that the reflections reach. So no subgroup generated by reflections in
vectors of square `\pm1` is `\Gamma` — not at level eight and hence not at all — the 56
candidates do not generate it, and any generating set must contain an element outside the
reflection mechanism, of which it needs at least 57.

This is a derivation from Chenevier's Lemma 3.1 and Corollary 3.7 plus the two vanishing
quotients above, not a machine computation: the order `|S(K)| = 1` is not verified by an
independent computation here, and the statement above should be read with that standing.

## A conflict with the certificate now on `main`

`main` has moved under this note: commit `bebcacc`, "expose certified Coble stable kernel
generating resolutions", makes `stable_orthogonal_group_generators()` return 56 generators
for `T_Co` from `src/sage_extensions/certificates/coble_kernel_fifty_six_congruence_generators.json`
(`generator_count` 56, `mod_four_image_rank` 56), with completeness attributed to a theorem
in another repository (`research/main 99f7680924`, `thm:coble-fifty-six-ordinary-full-kernel-generation`),
and `tests/lattices/test_the_coble_lattice_certified_generators.sage` asserts it.

That family is **not** a reflection family: each generator carries a
`source.parabolic_generator_index`, i.e. it is a parabolic unipotent. So it sits outside the
mechanism closed in section 8 and there is no contradiction with that part.

There is a contradiction with the count. The argument recorded above gives
`\Gamma/[ \Gamma,\Gamma ]\Gamma^2` dimension at least **57**: the level-two classes give 56,
and one dimension of `\Gamma(4)/\Gamma(8)` is not a commutator of level-two classes, because
`[\Gamma(4),\Gamma] \subseteq \Gamma(8)` makes every commutator of `\Gamma` congruent to a
commutator of reflection classes, and those span only 54 of the 55. A generating set of 56
elements therefore cannot exist. Either this counting argument is wrong, or the certificate's
completeness is; the two cannot both hold, and this note does not settle which. What is
checkable here is that the 56 generators are integral isometries with trivial discriminant
action and that their classes span `\Gamma/\Gamma(4)` — that is what `mod_four_image_rank: 56`
records — and that is not the disputed step.

### The certificate measured

The 56 generators of `bebcacc` were checked and their level-four content computed here, in
`T_Co`'s own Gram:

```
generators: 56   all integral isometries: True   all in Gamma: True
level-two class rank: 56
level-four span of their commutators: 54
level-four span of commutators and squares: 54
```

So the per-generator checks and the `mod_four_image_rank: 56` of the certificate are exactly
what the certificate says, and the family does generate `\Gamma` modulo `\Gamma(4)`. What it
does **not** do is reach a 55th level-four dimension: its commutators and squares span the
same 54 as the reflection family's. Two independent families — one of reflections, one of
parabolic unipotents — both stop at 54.

That sharpens the conflict rather than settling it. If the level-four class space is 55, as
the spinor-class-group computation in the previous section says, then no family yet written
down reaches the missing dimension, and the certificate's completeness at level eight is
unproved. If it is 54, then that computation has an error this note has not located, and the
certificate stands. The discriminator is unchanged and is one object: an explicit element of
`\Gamma(4)` whose class leaves the 54-space.

## Retraction: the level-four space is 54, not 55

The 55 came from the spinor-class-group section and it is wrong. The decisive argument is
elementary and does not need that section: `\Gamma/\Gamma(8)` is a 2-group generated by the
classes of the 56 reflections modulo `\Gamma(4)`, so its Frattini subgroup
`G^2[G,G]` is spanned by the squares and commutators of those generators, and
`\Gamma(4)/\Gamma(8) \subseteq G^2[G,G]`. Both spans were computed: commutators 54, squares
54, together 54. Hence `\dim \Gamma(4)/\Gamma(8) \le 54`, and with the computed lower bound 54
it is **exactly 54**. The alternating-space bound of 55 is not attained.

Withdrawn with it, all consequences drawn from 55:

* the claim that no subgroup generated by reflections is `\Gamma` — false as stated; the
  reflections are level-eight complete, and nothing here rules out a reflection family;
* the lower bound `d(\Gamma) \ge 57` — the only bound this note supports is `d(\Gamma) \ge 56`,
  from the 56 level-two classes;
* the conflict with the 56-generator certificate on `main` — it dissolves. With the space at
  54, a 56-element generating set is not excluded by any count here, and the certificate's
  per-generator claims and its `mod_four_image_rank: 56` were verified independently in the
  section above.

The spinor-class-group computation in section 9 is retained as the record of an argument that
gave 55; it is superseded and should not be cited. What remains true and is unaffected: the
level-four quotient is 56-dimensional and spanned by the reflections; the reflection and
parabolic families both reach 54 at level eight; and the generic Schreier route over
`46998591897600` cosets is not available.

## The database field's blocker, measured

Acceptance item 5 asks that `generator_morphisms` return and certify. The digest this
repository reads carries **no Coble arithmetic-group card at all**: `tests/cards/lattice-database-enriques.json`
holds 87 `arithmetic_groups` entries under `_provenance.cards.arithmetic_group`
(`arithmetic-groups/{slug}.md`), and none of them is the Coble group — the slugs are
`gamma-h-1` to `gamma-h-87`, and `arithmetic-groups/gamma-otilde-t-co.md` does not exist at the
pinned ref `1e1cadcfdca4dba2c0084a0bdc095b2d691126a8` (the fetch 404s). So item 5 is not a
missing row in a present card; the card itself is absent upstream, and `refresh_lattice_database_enriques.py`
has no `data.generator_morphisms` read because there is nothing to read it from.

That places item 5 with the database repository's owner: **lattice-database#7**, which asks for
the card and the field in the first place. Nothing in this repository can close it, and nothing
here should be edited to fake it.

### Correction to the section above

The card is **not** absent upstream: the slug is `otilde-t-co`, not `gamma-otilde-t-co`, and
`arithmetic-groups/otilde-t-co.md` exists at the pinned ref `1e1cadc`. At that ref its front
matter is

```
slug: otilde-t-co
name: Otilde(T_Co)
lattice: 6JRR
data:
  abstract_structure: the kernel of O(T_Co) -> O(A_T_Co)
  cardinality: aleph0
```

with no `generator_morphisms` field, and its body says the index, the generators and the
orbits "are absent until a computation certifies them". The earlier conclusion in the section
above — that the card itself does not exist — is wrong and is withdrawn; what holds is that
the digest omits the card because `refresh_lattice_database_enriques.py` reads a fixed set of
87 `gamma-h-*` cards, and that the field is missing at its source.

So item 5 waits on **lattice-database#7** for the field's content. Adding the card to this
repository's digest before that field exists would put `None` under a key the acceptance names,
which is not certification and is not done here.

## Item 5 is met at the database, and this note is corrected

`dzackgarza/lattice-database` at `main` now carries the field. The arithmetic-group card
`otilde-t-co` stores

```
data:
  index_in_orthogonal_group: 46998591897600
  generator_morphisms: [Otilde(T_Co) generator 1, ..., Otilde(T_Co) generator 56]
```

and lattice card `6JRR` carries the source hashes that certify them,
`arithmetic-group.otilde-t-co.index_in_orthogonal_group` (`682c595c...`) and
`arithmetic-group.otilde-t-co.generator_morphisms` (`3b6b6031...`), beside the same pair for
`otilde-plus-t-co`, whose family is 95 Schreier generators. The card states the two values are
certified independently on that card and that the historical 46-trillion-coset enumeration is
unnecessary for the explicit family.

So the statement above — that item 5 is blocked on `lattice-database#7` — is withdrawn. The
field returns and certifies there. This repository's digest is pinned at `1e1cadc`, which
predates the field, and its refresh script reads a fixed set of 87 `gamma-h-*` cards; that is a
snapshot of an older database ref, not a gap in the acceptance.

## The certification path's memory, measured

The database records this field's certify attempt as lost after 4782 s at 14 382 555 136 bytes
against a 1 675 943 526-byte limit. That route was the Schreier family of the finite image.
The direct resolution now installed by `stable_orthogonal_group_generators` is superseded onto
the preimage at `lattices.py:4405`-`4418`, and the measurement here is

```
stable_orthogonal_group: PreimageSubgroups.parent_class, selected resolution True
stable_orthogonal_group_generators: 56 elements            0.36 s
stable_orthogonal_group().group_generators(): 56 elements  0.51 s
peak tree RSS 319 MiB
```

So the call the database certifies against no longer enters the 4.7*10^13-coset machinery: it
returns the 56 in half a second within a fifth of the memory the earlier attempt reached before
dying. What remains for acceptance item 5 is the database's own certify re-run of `6JRR`, which
is `dzackgarza/lattice-database#7`, not work in this repository.
