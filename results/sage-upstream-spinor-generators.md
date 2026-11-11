# Upstream report: `Genus.spinor_generators` returns at most one prime

For the Sage issue tracker. Found while repairing `sage-extensions#330` with the
environment measured below.

**Version.** SageMath 11.0.beta5 (release date 2026-10-28), Python 3.14, source read at
`sage/quadratic_forms/genera/genus.py` in the pinned image; the site is
`GenusSymbol_global_ring.spinor_generators`, `genus.py:2624-2663`.

**Summary.** `spinor_generators` stops after the first prime it accepts, for every genus
whose spinor-kernel quotient is nontrivial, because each accepted prime is adjoined to
the *quotient's* generator list instead of to the subgroup accumulated so far. The
returned list therefore has at most one element, and every consumer that counts spinor
genera from its length reports two.

**The defect.** `genus.py:2653-2662`:

```python
        while not U.order() == q:
            p = P.next(p)
            if p.divides(self.determinant()):
                continue
            g = Q(A.delta(p))
            if g.gap() in U.gap():  # containment in sage is broken
                continue
            else:
                spinor_gens.append(p)
                U = Q.subgroup((g,) + Q.gens())
```

`U` starts as the trivial subgroup and the loop wants to accumulate primes until
`U == Q`. But `Q.gens()` are generators of the *quotient*, so
`Q.subgroup((g,) + Q.gens())` is `Q` itself: after the first appended prime the loop
condition `U.order() == q` holds and the walk stops. Equivalently, the containment test
`g.gap() in U.gap()` is only asked about the trivial subgroup, so any prime with a
nonzero class is accepted.

**Reproduction** (`diag(1, 20, 400)`, the genus Benham–Hsia, *On spinor exceptional
representations*, Nagoya Math. J. 87 (1982), §2.3, p. 252, use as an example):

```
sage: from sage.quadratic_forms.genera.genus import Genus
sage: G = Genus(matrix.diagonal(ZZ, [1, 20, 400]))
sage: G.spinor_generators(False)
[3]
sage: G.spinor_generators(True)
[3]
sage: A, K = G._improper_spinor_kernel()
sage: A.quotient(K).order()
4
sage: A.quotient(K).exponent()
2
```

One prime for a quotient of order four. The quotient's own `Q.gens()` are
`(f1, 1, f2)` — they include the identity, and they span `Q` by construction.

**Consequence in `Genus.representatives`.** `genus.py:3071-3074` seeds the
mass-stopped neighbour traversal from `self.spinor_generators(proper=False)`, so on this
genus the traversal starts in two of the four spinor genera and cannot leave them:

```
sage: G.representatives(backend='sage')
Warning: not all classes in the genus were found
(6 matrices)
```

six of the genus's twelve classes, mass `3/4` against the genus mass `3/2`. The
traversal's own completeness test is the mass, and it is not met.

**Proposed fix.** Adjoin the new prime to the accumulated subgroup and use the subgroup
order as the containment test, which is what the `# containment in sage is broken`
comment is about:

```python
        while not U.order() == q:
            p = P.next(p)
            if p.divides(self.determinant()):
                continue
            g = Q(A.delta(p))
            enlarged = Q.subgroup(tuple(U.gens()) + (g,))
            if enlarged.order() == U.order():
                continue
            spinor_gens.append(p)
            U = enlarged
```

Every accepted prime doubles `U.order()`, because `A = \prod_{p \mid 2d} Z_p^\times /
Z_p^{\times 2}` is a product of copies of `Z/2` and so is its quotient; the doubling is
worth asserting inside the loop.

**Effect, measured with the fix applied to the class at runtime.** On
`diag(1, 20, 400)`: `spinor_generators(False)` becomes `[3, 11]`, and
`G.representatives(backend='sage')` returns twelve matrices with the warning gone — the
full class set, mass `3/2`. On `diag(1, 20, -400)` the quotient is of order two and the
call already returns one prime. Primes are tried in increasing order starting at three;
two divides the determinant of the specimen, and the coprimality condition excludes it
in general.

**Second, smaller point, same function.** `_improper_spinor_kernel` (`genus.py:2586`)
falls through to `_proper_is_improper` (`genus.py:2688`) whenever `K` is a proper
subgroup of `A`, and that routine draws `V.random_element()` until a vector satisfies
its valuation conditions, so the *route* to `_improper_spinor_kernel` is randomized.
Four fresh evaluations on each specimen above gave the same order every time, so the
answer looks invariant, but a deterministic choice of the vector would remove the
question.

**Downstream consumer.** `sage-extensions` read the spinor-genus count as
`2 ** len(G.spinor_generators(proper=False))` and reported two for this genus; it now
reads the order of `A/K` directly and no longer depends on this function, but
`Genus.representatives(backend='sage')` on a definite genus with more than two spinor
genera still returns half the classes, which is why this is worth fixing upstream.
