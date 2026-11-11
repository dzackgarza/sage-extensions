# #354: the preimage call is blocked at the kernel's generating set

**No code change.** The call the issue asks for is `rho_L^{-1}(P)`'s generators, and the route
the batch names — lifts of `P`'s generators together with generators of `ker rho_L` — cannot be
completed: the second part has no owner in this library, and the owner says so in a named
constant. What is verified here is the first half's warrant and the failure's precise site.

## The statement, and where its hypothesis stands on 0125

V. V. Nikulin, *Integral symmetric bilinear forms and some of their applications*,
Math. USSR-Izv. 14 (1980), 103--167, **Theorem 1.14.2, p. 125**: for an even indefinite lattice
`L`, `O(L) -> O(q_L)` is onto. This repository already cites it with that page, at
`src/sage_extensions/categories/lattices.py:1744` (for "`T` unique in its genus with
`O(T) -> O(q_T)` surjective") and again at `:7776`.

The form of the hypothesis that the literature quotes for the surjectivity clause is
`rank(L) >= l(A_L) + 2` (so arXiv:1801.00287, Lemma 3.1, quoting the same theorem). **On 0125 it
fails.** Measured there, `M(2) = U(2) + E8(-2)`:

```
rank 10, signature (1, 9), determinant -1024
A_M: ten invariant factors, all 2  ->  |A_M| = 1024, l(A_M) = 10
```

`10 >= 12` is false, so Theorem 1.14.2 in that form does not deliver onto-ness on this lattice.
The shape the literature gives an escape for is `rank = l_2` with `q` carrying a `u(2)` summand,
and `q(M(2)) = q(U(2)) + q(E8(-2))` with `q(U(2)) = u(2)` is exactly that shape — but confirming
that clause needs the printed page, which is not in this checkout, and it is not needed:

**onto-ness on 0125 is established by computation instead.**

```
|O(q)|:        46998591897600   in 14.38s
|rho(O(M))|:   46998591897600   in 11.22s
equal, so rho_M is onto
```

`|rho(O(M))|` is `M.discriminant_image()`, the image of the selected generators of `O(M)`; it
equals `|O(q)|`, so the selected generators already reach every discriminant automorphism.

## The blocker: the kernel has no generating set

`ker rho_M = Õ(M)`, `M.stable_orthogonal_group()` (`lattices.py:4199`). Its generators, if asked:

```
stable_orthogonal_group():    0.00s
group_generators():           no return within 240 s (probe stopped)
```

because they are constructed by Schreier's lemma on the coset space `O(L)/ker rho` =
`O(q)`, of order 46 998 591 897 600. That is the observed failure of the issue restated
precisely: not a slowness in the transporter but a Schreier family over `4.7e13` cosets.

The owner states the gap itself, and the name is the one to work against:

* `src/sage_extensions/categories/orthogonal_quotients.py:1854` —
  `_MISSING_ARITHMETIC_GENERATING_SET = ("Over an indefinite lattice L, O(L) is an infinite
  arithmetic group and no generating set of this subgroup is known.  The missing operation is a
  generating set for an arithmetic subgroup of O(L), which belongs in lattice_engines.py")`.
* `src/sage_extensions/categories/orthogonal_quotients.py:776`,
  `OrthogonalCharacterQuotient.subgroup_generator_lifts`, whose docstring ends (lines 800--805):
  "This is the presented generator family whose discriminant images a consumer can build itself;
  it contains no claim about generating `Gamma` itself (the stable kernel of `O(L) -> O(A_L)`
  inside the subgroup is needed for that: an open capability of the lattice-engine owner, named
  by `_MISSING_ARITHMETIC_GENERATING_SET`)."

So the lifts of `P`'s generators exist and are cheap — `Lattices...discriminant_lift`
(`lattice_morphisms.py`, "Return `g` in `O(L)` inducing `automorphism`", exact, `None` when
there is none) — but the set they form does not generate `rho^{-1}(P)`: it misses `Õ(M)`
entirely. Returning it as "generators of `G_e`" would be the wrong object, and a test that
compares `|rho(<lifts>)|` with `|P|` would pass on it while the group were wrong, since every
kernel element is invisible to `rho`.

## What is therefore still owed

1. A generating set for an arithmetic subgroup of `O(L)` at `lattice_engines.py` — the named
   missing operation. For `M(2)` the candidates worth checking against a printed statement are
   the Eichler transvections `t(c, a)` of Gritsenko--Hulek--Sankaran, arXiv:1012.4155v2, §8.3,
   equation (49) (defined there for `c` isotropic and `a` in `c^perp`); that survey states their
   properties but no generation theorem, so the citation that they generate `Õ(L)` is not yet in
   hand. The library's own `eichler_transvection` (`isotropic_parabolics.py:501`) and
   `complement_eichler_transvections` (`eichler_criterion.py:305`) are built for `2U + K`
   Eichler models, and `M(2)` contains no `U` summand.
2. The order of the decomposition stabilizer, computed in `O(q)`. Two routes were tried and are
   not yet measured: walking the `O(q)`-set of 2-dimensional subspaces from `A_{U(2)}` (a BFS
   over `O(q)`'s four generators that had not returned in ten minutes), and counting the
   subspaces of that isometry type directly, which the probe attempted and lost to a comparison
   defect (`form.q(point) == form.zero()` is not the right zero for a `Q/2Z`-valued form), so no
   number is claimed.

`A_{U(2)}` inside `A_M` is computable and was computed: the primitive duals of the `U(2)` basis
vectors give classes `[0]` and `[1]` of order two, so `A_{U(2)} = {0, [0], [1], [0]+[1]}` in
`A_M`'s coordinates, consistent with `A_M = A_{U(2)} + A_{E8(-2)}` and `q(U(2)) = u(2)`.
