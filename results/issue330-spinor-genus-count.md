# 330 — the spinor-genus count on `diag(1, 20, 400)`, and where Sage's generator list stops

Stage 1, under #280. The consumer result: `L.spinor_genus_count()` returns the number of
spinor genera in the genus of $L$, computed by a cited method; #317's genus enumeration
uses that count as a completeness check.

## Sources: which were read, which were not

| source | state |
|---|---|
| Benham–Hsia, *On spinor exceptional representations*, Nagoya Math. J. **87** (1982), §2.3, p. 252 | **not on this machine; not read here, and no copy exists in the project.** The value four is the issue's and the named test's, corroborated below by computation. |
| Cassels, *Rational Quadratic Forms*, Ch. 11 §3 and §1 | **read** (§1 p. 200, §3 pp. 207–211) |
| Conway–Sloane, *Sphere Packings, Lattices and Groups*, Ch. 15 §9 | **read** (pp. 388–391) |
| Sage's implementation of the spinor-norm quotient, `sage/quadratic_forms/genera/genus.py:2547-2663`, pinned image | read |

Benham–Hsia is the one source still missing; it is Nagoya Math. J. 87 (1982) 247–260,
DOI `10.1017/S0027763000020031`. Project Euclid serves the volume but answered this
machine with a bot challenge, and Cambridge Core holds the article behind its own front
end; neither was worked around.

## The two sources that were read, and the convention they fix

**Cassels, Ch. 11, §3, "Number of spinor genera".** The section opens on **p. 207**: "In
this section we show that the number of spinor genera in a genus is equal to the order of
a certain group which depends, of course, on the genus and which is readily computable",
for dimension at least three ((3.1), p. 207). That group is (3.15) on **p. 209**,
$G_P = R_P/S_PT_P$, with $R_P = \prod_{p\in P}\theta(V_p) = \prod_{p\in P}\mathbf Q_p^\times$
by Lemma 3.1, (3.2), on p. 207; $S_P = \prod_{p\in P}\theta(\Lambda_p)$, the product of
the local spinor-norm images ((3.10), p. 209); and $T_P$ the rationals that are units away
from $P$ ((3.12)–(3.14), p. 209). **Theorem 3.1 with Note 2, p. 211**, says the set of
spinor genera is a principal homogeneous space over $G_P$: the number of them is
$|G_P|$, the index of $\prod_p\theta(\Lambda_p)\cdot T$ in $\prod_p\mathbf Q_p^\times$.
Equation (3.16) on p. 209, $g^2 = 1$ for every $g \in G_P$, is why that order is a power
of two.

**Conway–Sloane, Ch. 15, §9.** **p. 389**: "Each genus is partitioned into a number of
spinor genera (the number is always a power of 2). There is a group of spinor operators
acting transitively on the spinor genera". **p. 388**: "The current use of the term
differs slightly from Eichler's (by replacing the orthogonal group by the special
orthogonal group in some places)". **p. 390**, §9.3: "We call $r \in \mathbf Q$
automorphous if it is the spinor norm of a **proper** integral automorphism of $f$",
with the same word for the $p$-adic version; Theorems 16 and 17 on the same page name the
spinor kernel by those numbers, and Theorem 15(b) on p. 389 is the rank-$\geq 3$ hypothesis.

**Their convention is the proper one, and the code now follows it.** Cassels defines
$\theta$ on $O^+(V)$ (Ch. 10, §3, p. 178) and takes $\theta(\Lambda_p)$ to be its image on
$O^+(\Lambda_p)$ (Ch. 11, §1, p. 200); Conway–Sloane say the same in the two passages
above. The method's default was `proper=False`, the improper count, which admits improper
isometries and partitions more coarsely; `_Genus.spinor_genus_count` now defaults to
`proper=True` and its docstring carries the statements, the pages and the convention.
`proper=False` remains for `_genus_classes`, whose enumeration partitions by the improper
spinor genus and says so. Measured after the change: four under both conventions on
`diag(1, 20, 400)`, two under both on `diag(1, 20, -400)`, and two under both on the genus
of `[[-9,1,0],[1,7,0],[0,0,2]]`, the specimen of the `lattices.py` doctest, so that
doctest's `> 1` is unaffected. On a genus where the two differ the public count reports the
source's proper one; the three genera measured here are not such a genus, and no other
genus of this library was measured for the question.

## Which of the two was the defect

**Sage's `spinor_generators`, not our use of it.** Measured on `diag(1, 20, 400)`
(SageMath 11.0.beta5, release date 2026-10-28):

```
G.spinor_generators(False) = [3]
G.spinor_generators(True)  = [3]
A, K = G._improper_spinor_kernel();  A.quotient(K).order() = 4, exponent 2
```

One prime for a quotient of order four. `genus.py:2662` reads
`U = Q.subgroup((g,) + Q.gens())`: `Q.gens()` generate the quotient, so `U` is the whole
quotient after the first accepted prime and the walk stops there. Every genus gets at
most one prime, so `2 ** len(...)` is at most two — our formula and our `proper=False`
flag were both right, and the flag does not matter here since the proper and improper
quotients are equal (`_improper_spinor_kernel` short-circuits and returns the proper
pair).

The same broken list is what `Genus.representatives(backend='sage')` seeds its
mass-stopped traversal from (`genus.py:3071-3074`), so the defect has a second symptom
in the tree: a definite genus with more than two spinor genera enumerates half its
classes. On this specimen, with the walk repaired at runtime, `representatives` returns
twelve matrices instead of six and stops printing `Warning: not all classes in the genus
were found`.

## The repair

Both consumers in `categories/lattices.py` now go through one selection:

* `_spinor_kernel_quotient(genus, proper=...)` — the quotient
  $A/K = \prod_{p\mid 2d}\mathbf Z_p^\times/\mathbf Z_p^{\times 2} / K$ that Sage
  retains; its order **is** the count, the index of the spinor-norm image;
* `_spinor_generating_primes(genus, proper=...)` — the walk Sage intends: primes coprime
  to the determinant in increasing order, each kept only when adjoining it to the
  *accumulated* subgroup enlarges it, with the doubling asserted because $A$ is a product
  of copies of $\mathbf Z/2$. On this genus it returns `(3, 11)`.

`_Genus.spinor_genus_count(proper=False)` returns the quotient's order, not the length of
a generator list; the keyword states which convention is meant (the improper one is what
the enumeration and the previous implementation used), and the docstring says so.
`_genus_classes` seeds its traversal from `_spinor_generating_primes` and hands those
seeds to Sage's own `neighbor_iteration` — the engine Sage's `representatives` uses —
with the same neighbour prime Sage picks and the same mass stop, so the traversal is
again Sage's and only its seeds changed.

## The count

`L.spinor_genus_count()` on `diag(1, 20, 400)` is **4**, under either convention.

Corroboration that does not use the count formula at all: the same enumeration partitions
the genus's **12** classes as $(3,3,3,3)$, one group per spinor genus, and the
automorphism orders of the twelve classes sum to the genus mass $3/2$ — all asserted by
the named test, which is unchanged. The indefinite sibling `diag(1, 20, -400)` gives
**2**, one class per spinor genus, which is the other test in the module.

## Green, and the module

The named test, assertion unchanged:

```
tests/lattices/test_genus.sage::test_published_four_spinor_genus_is_counted_from_all_generators
1 passed, 9 deselected in 12.64s
```

Red at the base commit `67c96ef` was exactly this one test and no other:

```
$ tests/lattices/test_genus.sage      (clean worktree at 67c96ef)
E       assert 2 == 4
E        +  where 2 = spinor_genus_count()
tests/lattices/test_genus.sage:91: AssertionError
1 failed, 9 passed in 7.44s
```

and the whole module on the repaired tree:

```
$ tests/lattices/test_genus.sage      (repaired)
10 passed in 9.44s
```

The other nine tests passed at the base because their genera have a spinor quotient of
order at most two, where Sage's single prime is a spanning set; the specimen is the
smallest genus in the module whose quotient is of order four.

## Neighbouring modules

`_genus_classes` is what `_Genus.representatives`, `class_number` and the mass checks read,
so the modules that enumerate genera were run too, against a clean worktree at `67c96ef`:

| modules | repaired tree | clean `67c96ef` |
|---|---|---|
| `test_splag_genus_archive`, `test_splag_51ab_genus_archive`, `test_genus_existence_archive` | `1 failed, 3 passed in 2.44s` | `test_genus_existence_archive` alone: `1 failed, 1 passed in 1.68s`, the same id |
| `test_definite_genus_mass_archive`, `test_theta_series_and_covolume` | `6 passed in 6.49s` | `6 passed in 4.41s` |

The one failure is
`test_genus_existence_archive.sage::test_a2_discriminant_genus_exists_exactly_when_the_signature_satisfies_milgram`,
which is red on both trees. `test_genus_of_the_scattone_summands.sage` was dropped from
the set: it is already lint-red at the base commit (TL01 ×2 on `import json` and
`from pathlib import ...`, TL13 on `__file__`) and does not collect under the session
plugin, so it is evidence for nothing here.
