# #597 — the stable orthogonal group of `T_Co` has no published generating set, and the refusal now says so

`T_Co = <2> + U(2) + E8(-2)`, rank 11, signature `(2, 9)`, even, 2-elementary,
`det = -2048`, `|A_L| = 2048`. The two arithmetic-group cards carry the index
and no generating family: `46998591897600 = |O(A_{T_Co}, q)|` for the
discriminant kernel `Õ(T_Co)` and `93997183795200 = 2 * 46998591897600` for its
spinor part `Õ⁺(T_Co)`. This note answers the four questions of the issue: what
the refusal is, why no case can be added for this lattice, what the generic
route costs when measured, and what the certificate can state.

## 1. The refusal, and what it is refusing

Two calls, two different refusals.

**`stable_orthogonal_group_generators()`** (lattices.py) guarded its one
constructive route with three invariants of card `0125` — the code at
`61b3fa1`, the parent this lands on:

```python
assert (
    ring is _owned_integers()
    and rank == 10
    and int(signature.first()) == 1
    and int(signature.second()) == 9
    and self.is_even() is True
    and self.is_p_elementary(ring(2)) is True
    and int(self.discriminant_group().cardinality()) == 1024
), (
    f"the Bertini-involution generation statement covers only L = Lambda(2) "
    ...
)
```

`rank == 10`, `signature == (1, 9)`, `|A_L| == 1024` are the invariants of card
`0125`, not hypotheses of a theorem about the lattice in hand. So the refusal
is **a missing case in a dispatch whose content is a literature-coverage
claim** — not a rank bound in the mathematics (rank enters only as card `0125`'s
rank), not a discriminant-form hypothesis (`T_Co` *passes* the even and
2-elementary checks it is asked), and not an engine limitation (GAP builds
`O(A_L)` without complaint; the wall in §4 is the size of a transversal, not a
capability). The sentence behind the check is Allcock's Theorem 1.1, whose
hypothesis is a rank-10 lattice.

**`stable_orthogonal_group()`** does not refuse at all: it returns in `0.02 s`
a subgroup whose `has_selected_group_resolution()` is `True`, and whose
`group_generators()` therefore takes the Schreier route. That call does not
return; §4 measures it.

## 2. What the refusal is a limit on: `Õ(T_Co)` is a level-two congruence subgroup

`T_Co = 2·N` with `N = <1> + U + E8(-1) = <1> + II_{1,9}`, the odd unimodular
lattice of signature `(2, 9)`; the Gram matrices agree entrywise after `2·`.
Write `L = T_Co`. Since `|A_L| = 2^11 = 2^rank`, `L = 2L^#`: `L/2L` and
`2L^#/2L` both have order `2^11`, and `2L^#/2L` is `L^#/L = A_L`, so the
inclusion `L <= 2L^#` is an equality. Then

* every pairing `B(x, y)` of two vectors of `L` is even, so the Gram matrix
  reduced mod 2 vanishes and `rank_2(L) = 0`;
* `x |-> x/2` is a bijection `L/2L -> A_L` (`x in L = 2L^#` gives `x/2 in L^#`)
  and it is `O(L)`-equivariant because an isometry is `Z`-linear, so
  `ker(rho_L) = ker(O(L) -> GL(11, F_2))`.

So `Õ(T_Co)` **is the principal congruence subgroup of level 2** — Allcock's
`W_237(2) = ker(O(Λ) -> O(Λ/2Λ))` is this same kernel for `Λ = E8 + U`
(arXiv:1601.00103v2, p. 2, where `V = Λ/2Λ` carries `x·x/2 mod 2`), with
`Λ(2) = U(2) + E8(-2)` the rank-10 summand of `T_Co`.

That is the whole mathematical content of the refusal: the object the cards
need is a level-two congruence subgroup, and `rank_2(T_Co) = 0` is the extreme
case of the family for which no such generation statement is published.

## 3. Why no case can be added: every published statement fails a hypothesis on `T_Co`

| statement | hypothesis | `T_Co` |
|---|---|---|
| Allcock, Thm 1.1 (p. 2; proof pp. 6–8): Bertini involutions generate `W_237(2)` | `L = Λ(2) = U(2) + E8(-2)`, rank 10, signature (1,9), `|A_L| = 2^10` | rank 11, signature (2,9), `|A_L| = 2^11`; **and the family is infinite** — one involution per decomposition `Λ = E8 + U` |
| Kneser, Satz 4 (as quoted by Gritsenko–Hulek–Sankaran, arXiv:0810.1614, Thm 1.1): `O'(L) = <σ_a σ_b>`, `a² = b² = -2` | even, Witt index ≥ 2, represents `-2`, `rank_3 ≥ 5`, `rank_2 ≥ 6` | `rank_2 = 0` |
| Gritsenko–Hulek–Sankaran, Prop. 3.4 (pp. 11–12): `Õ⁺(L) = <Γ_J(L_0), σ_1>` | `L = U + U_1 + L_0` (two hyperbolic planes), `rank_3 ≥ 5`, `rank_2 ≥ 6` | no hyperbolic plane: one has determinant `-1`, so `rank_2 ≥ 2` is necessary and `rank_2 = 0` |
| Dutour Sikirić–Hulek, arXiv:2302.01679v2, `Existence_ApproximateModel` | signature `p, q ≥ 2`, dimension ≥ 7 | applies — but it generates an approximate subgroup `Ap(L)`, and the identification `Ap(L) = Õ(L)` is unpublished |

`rank_2 = 0` is not a search failure but the exact opposite of what the
transvection and reflection theorems ask: a hyperbolic plane is unimodular, and
`T_Co` splits off none — every sublattice of positive rank has even
determinant. `rank_3(T_Co) = 11` and the Witt index is 2, so the running
hypotheses of Kneser's theorem hold; `rank_2 ≥ 6` is the one that does not, and
it is the one no rescaling of the lattice can repair.

The three refusals this library has recorded are the same phenomenon:
card `0125 = Λ(2)` has `rank_2 = 0`, `N = U + U(2) + E8(-2)` (issue #17) has
`rank_2 = 2`, and `T_Co` has `rank_2 = 0` — all below Kneser's `6`.

## 4. The cost of the only route the library can state

`Õ(L) = ker(rho_L)`, and `rho: O(L) -> O(A_L)` is onto — measured, not
assumed. `|O(A_{T_Co}, q)| = 46998591897600` in `1.44 s`, and the library's own
`|rho(O(T_Co))|` is the same number in `34.60 s` (the card's
`orthogonal_group_order`). So the Schreier family of Seress, *Permutation Group
Algorithms*, Lemma 4.2.1, p. 57 — the construction `discriminant_preimage`
documents — is indexed by a transversal of `O(A_L)` and by the generators of
`O(L)`: `46998591897600` cosets times **196** generators, the library's
selected generating family of `O(T_Co)` (196 elements, not the 126 the issue
quotes), which is `9.2 · 10^15` words.

Measured on the current runtime (`Sage 11.0.beta5`, image
`sha256:59568577…`), one job, `PEAKRSS_LIMIT_MIB=6144`, inner
`timeout -s KILL 600`:

```
L = <2> + U(2) + E8(-2)
  rank 11 det -2048 signature (2, 9) even True 2-elementary True
  |A_L| 2048   [0.20s]
stable_orthogonal_group() -> {g in O(...) : rho_L(g) lies in a subgroup ...} [0.02s]
  has_selected_group_resolution: True
                        <- no further line: group_generators() never returned
```

The first datum that call needs is `libgap.RightTransversal` of `O(A_L)` modulo
the trivial subgroup (`_TransversalCosets.__init__`, `categories/group/groups.py`),
which has one entry per coset. Resident memory while it was being built:
**1.315 GB at 131 s, 2.794 GB at 344 s, 4.173 GB at 524 s**, peak tree RSS
**4607 MiB**, peak single-process `VmHWM` **4681 MiB**, exit status `124` at the
inner cap — linear at about `8 MB/s`, not a plateau, with the traversal
incomplete when the cap killed it. One entry per coset at even one byte per
coset is `4.7 · 10^13` bytes, and at the measured rate the 6 GiB cap is reached
in about thirteen minutes: the same wall the issue records as `124` for a
thirty-minute probe.

## 5. What the certificate can state

`lattice-database#7`'s second acceptance is met on the index, with the
generation clause recorded as not supplied:

> The discriminant kernel `Õ(T_Co)` has index `46998591897600 = |O(A_{T_Co}, q)|`
> in `O(T_Co)`, read from the finite orthogonal group of the discriminant form
> (card `6JRR`, `integral.discriminant_form.orthogonal_group_order`), not from
> its coset space; the spinor part `Õ⁺(T_Co)` has index twice that,
> `93997183795200`. The library supplies **no** generating set. `Õ(T_Co)` is
> `ker(O(T_Co) -> O(T_Co/2T_Co))`, the principal congruence subgroup of level 2
> of `O(T_Co) = O(<1> + II_{1,9})`; `rank_2(T_Co) = 0` and `T_Co` contains no
> hyperbolic plane, so Kneser's theorem (`rank_2 ≥ 6`) and
> Gritsenko–Hulek–Sankaran's Prop. 3.4 (two hyperbolic planes) do not apply;
> Allcock's Bertini family generates the level-two kernel only for
> `Λ(2) = U(2) + E8(-2)` (rank 10), and it is infinite. The only route the
> library can state, the Schreier family over a transversal of `O(A_L)`, is
> `46998591897600` cosets times 196 generators and does not return (measured
> above).

Two consequences for the card pipeline, both outside this repository's push
capability:

* `data.generator_morphisms` stays absent on both `T_Co` arithmetic-group cards,
  with the sentence above attached.
* The digest this repository reads (`tests/cards/lattice-database-enriques.json`,
  `_provenance.rows.arithmetic_group`) lists `data.cardinality`,
  `data.abstract_structure`, `data.line_orbits`, `data.plane_orbits`,
  `data.flag_orbits`, `data.reference.citation`, `latex`, `lattice` and
  `parent_group` — **not** `data.generator_morphisms`. A card that gained a
  generating set would still not reach the library until that row is added to
  the digest's row list.

## 6. The code change

`stable_orthogonal_group_generators()` now states its limit instead of
asserting a card's identity: the same hypotheses are checked, and a lattice
that fails one is refused with a `ValueError` naming the failing hypothesis and
its value on the lattice in hand — rank, signature and `|A_L|` for Allcock's
statement, `rank_2` and `rank_3` for Kneser's and Gritsenko–Hulek–Sankaran's.
`rank_p(L)` is new: Gritsenko–Hulek–Sankaran's invariant, read as the number of
Smith invariants of the Gram matrix that `p` does not divide, which is the rank
of the Gram matrix mod `p` (their §1 definition: the maximal rank of a
sublattice whose determinant is coprime to `p`). Card `0125`'s path is
unchanged and still raises its own `ValueError` after certifying the Bertini
family.

`tests/lattices/test_the_coble_lattice_carries_no_generating_set.sage` asserts
the mathematics the refusal rests on — `|A_L| = 2^rank`, `rank_2 = 0`,
`rank_3 = 11` — the refusal itself (`ValueError`, not an `AssertionError`), and
the finite orthogonal group of the discriminant form against card `6JRR`'s own
`orthogonal_group_order`. The `discriminant_image()` computation that gives the
index directly takes `34.60 s` on this lattice, over the suite's 20 s per-call
ceiling, so the module asserts the card row against `|O(A_{T_Co}, q)|`, which
`rho` is onto.

## The run

`pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint --durations=0` on the two files, time gates
on:

```
tests/lattices/test_the_coble_lattice_carries_no_generating_set.sage ... [ 75%]
tests/lattices/test_the_stable_orthogonal_group_generators_refuse.sage . [100%]
5.46s call  ...test_the_stable_orthogonal_group_generators_refuse_on_card_0125
1.30s call  ...test_the_finite_orthogonal_group_of_the_coble_discriminant_form_is_the_card_row
0.18s call  ...test_the_coble_lattice_refuses_its_generating_set_by_stating_the_hypothesis
(9 durations < 0.005s hidden)
============================== 4 passed in 7.60s ===============================
[peakrss] peak tree RSS : 530 MiB
```

The test lint on both files: no findings. On the parent `61b3fa1`, with only the
test file added and the same command, `2 failed, 1 passed in 2.44 s`: the
refusal test fails because the call raises `AssertionError` there —
`lattices.py:4419`, "the Bertini-involution generation statement covers only
L = Lambda(2) ... but Integral lattice of rank 11 and signature (2, 9) has rank
11 ..." — so `pytest.raises(ValueError)` sees no refusal; the second test fails
because `rank_p` does not exist at that commit; and the card-row test passes
there as it does after the repair, since it does not depend on the change.

## What is not claimed

No generating set is returned, so nothing is claimed to generate. The level-two
identification is proved above for any lattice with `|A_L| = 2^rank`; it is not
a substitute for a generation theorem, and the sentence the card carries says
so. Nothing here bears on `Õ⁺` beyond the factor two: `[Õ : Õ⁺] = 2`, so a
generating set of `Õ` and one element outside `Õ⁺` would give `Õ⁺`, and the
refusal of the first is the refusal of both.
