# #133: what the Coxeter system owns now, and what it does not

A Coxeter system is built by `Groups.Coxeter(m)` from its Coxeter matrix `m`,
and the operations below are methods of that object, in
`src/sage_extensions/categories/group/groups.py`.

## Landed, with the statement that decides it

| acceptance item | statement | file:line |
| --- | --- | --- |
| word length | `word_length(element)` → the least number of simple reflections whose product is `element` | `groups.py:8346` |
| reduced words | `reduced_word(element)` → one reduced word, as a finite family of simple reflections whose product is `element` | `groups.py:8375` |
| longest element of a finite `W` | `longest_element()` → the unique element of greatest length; its length is the number of positive roots | `groups.py:8414` |
| degrees `d_i` of a finite `W` | `degrees()` → the degrees of the invariant ring `k[V]^W`, read off the Coxeter element | `groups.py:8452` |
| Poincaré series as a rational function | `poincare_series()` → `W(t) = sum_w t^l(w)`, Steinberg's formula in general and Solomon's product for finite `W` | `groups.py:8484` |
| `chi(W) = 1/W(1)` | `euler_characteristic()` → the reciprocal growth series at `1`, the orbihedral Euler characteristic of the chamber complex | `groups.py:8514` |
| growth rate as an algebraic number | `growth_rate()` → `1` over the least positive real pole of `W(t)`, an element of the real algebraic numbers | `groups.py:8543` |

The degrees come from the eigenvalues of the Coxeter element, whose
multiplicities are read off the power sums `tr(c^k)` by the discrete Fourier
transform on `Z/h`; the geometric representation is built over `Q(zeta_L)` with
`L` a multiple of every `2m_vw`, folded into `Q(zeta_0)` where `z` is a
primitive root of unity of that order.  Finiteness of a standard parabolic
subsystem is the existing ellipticity decision of `CoxeterDiagrams`, so no
second criterion for `W_J` finite was introduced.

## Closure specimens of the issue

- `W(A_2)(t) = 1 + 2t + 2t^2 + t^3`, asserted by cross-multiplication against
  `poincare_series()`.
- The affine `A_1` group (`m = [[1, aleph_0], [aleph_0, 1]]`) has
  `W(t) = (1+t)/(1-t)`.
- `W(E_8)` has degrees `2, 8, 12, 14, 18, 20, 24, 30`, with product
  `696729600 = |W(E_8)|`.
- The `(2,3,7)` triangle group (`m = [[1,3,2],[3,1,7],[2,7,1]]`) has the growth
  series `W(t) = P(t)/Q(t)` with `Q` Lehmer's polynomial
  `t^10 + t^9 - t^7 - t^6 - t^5 - t^4 - t^3 + t + 1` up to sign and
  `P = -(t+1)^2 (t^2+t+1) (t^6+t^5+t^4+t^3+t^2+t+1)`, so its growth rate is
  Lehmer's number `1.1762808182599176...`, the largest root of `Q`.  Its
  reciprocal growth series at `1` is `-1/84`.

The growth series of that group was checked against a computation that shares
no code with it: the layers of the Cayley graph of the three simple
reflections, built from the exact geometric representation over `Q(zeta_28)`
and counted by distinct matrices (faithful by Tits' theorem, so distinct
matrices are distinct elements).  The scratch probe printed

```
1 3 cum 4
2 5 cum 9
3 7 cum 16
4 9 cum 25
5 12 cum 37
6 16 cum 53
7 20 cum 73
8 24 cum 97
9 28 cum 125
10 33 cum 158
11 40 cum 198
counts: [1, 3, 5, 7, 9, 12, 16, 20, 24, 28, 33, 40]
```

and the series expands to `1, 3, 5, 7, 9, 12, 16, 20, 24, 28, 33, 40, 48`.
This is also what fixed the sign and the `t^{l(w_0^J)}` factor of the
Steinberg sum: the variant `sum_J (-1)^|J| t^|J| / W_J(t)` gives `7` elements at
level `2` and the variant with the longest element of `W_J` gives `5`, the
number counted above.

## Not landed

1. **Simple systems, positive roots and the fundamental chamber.** The simple
   system is the retained family `group_generators()`, and the chamber of a
   *lattice* reflection group is `hyperbolic_lattices.py:1863`
   `fundamental_chamber(...)`, whose Vinberg route is gated by the wall-Gram
   recognizer at `vinberg_invariants.py:316`
   (`is_acute_angled_hyperbolic_polytope_gram`), which rejects a degenerate wall
   Gram; #152 owns that defect and its redundant-wall specimen.  Positive roots
   of a Coxeter system given only by its matrix are computed nowhere: for an
   infinite `W` they are infinite, so the item needs a stated finite
   presentation (the Tits cone or the Davis complex) before it is a computation.
2. **The ring of invariants `k[V]^W` with its Molien series.** `degrees()` gives
   the degrees, so `Molien(t) = prod_i 1/(1-t^{d_i})` is available as a rational
   function, but there is no owned object for the ring: `graded_algebras.py` has
   no Hilbert or Molien series operation, and no graded polynomial presentation
   whose generators carry the degrees exists, so there is nothing that could
   answer `hilbert_series()` or be the quotient `V // W`.
3. **Perron and Salem numbers as owned classes.** `growth_rate()` returns an
   element of the owned real algebraic numbers, and the test decides Lehmer's
   number by evaluating Lehmer's polynomial at it and separating the root above
   `1`.  The two *classes* are not declared anywhere; `rings/` owns `AA` and
   `QQbar` as rings only, and `categories/sets/` has no predicate-subobject
   machinery for a class of numbers, so this is a design step rather than a
   declaration to add.
4. **Bott's formula for affine `W`.** Not used; the series is the general
   Steinberg formula, which covers the affine case (the affine `A_1` specimen
   above) without it.

## What was run

`sage 11.0.beta5`, `/sage/.venv/bin/python`, image
`ghcr.io/dzackgarza/sage@sha256:59568577...`:

```
$ python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
    -p sage_extensions.testing.test_lint --durations=0 -q \
    tests/groups/test_the_degrees_and_growth_series_of_a_coxeter_system.sage
13 passed in 3.02s

$ ... tests/objects/test_coxeter_diagram_a2.sage tests/groups/test_the_degrees_and_growth_series_of_a_coxeter_system.sage
21 passed in 3.18s
```

Only the file written here and its one consumer file in `tests/objects/` were
run; no suite was run.
