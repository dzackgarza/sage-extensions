# #133: the acceptance, item by item

The issue's delta reads, verbatim: *"the category of Coxeter systems `(W, S)`
owns:"* the seven bullets below.  A system is built by `Groups.Coxeter(m)` from
its Coxeter matrix `m`; the method column gives the declaration that decides
the item and where it lives in `src/sage_extensions`.

| # | acceptance item, as the issue words it | declaration that decides it | file:line | holds |
| --- | --- | --- | --- | --- |
| 1 | "word length and reduced words" | `word_length(element)`, `reduced_word(element)` — least number of simple reflections, and one word of that length multiplying to the element, by breadth-first search of the Cayley graph | `categories/group/groups.py:8433`, `:8462` | yes |
| 2 | "simple systems, positive roots and the fundamental chamber" | the simple system is the retained family `group_generators()`; `simple_roots()`; `positive_roots()` (orbit of the simple roots over the real algebraic numbers, positivity decided in an ordered field); `fundamental_chamber()` (the dual cone of the simple roots, as a subset of `V`) | `groups.py:6377` (`group_generators`), `:8539`, `:8582`, `:8651` | yes, with the caveat that the chamber is represented as a point set and not as a polyhedral cone |
| 3 | "for finite `W`, the longest element `w_0` and the degrees `d_i`" | `longest_element()`; `degrees()` from the Coxeter element's eigenvalues | `groups.py:8501`, `:8730` | yes |
| 4 | "the ring of invariants `k[V]^W`, with its Molien series, toward GIT quotients `V // W`" | `molien_series()`, the Hilbert series `prod_i 1/(1-t^{d_i})` of the invariant ring | `groups.py:8701` | no: the series holds, the ring and `V // W` do not |
| 5 | "the Poincaré series `W(t)` as a rational function in general (Steinberg's formula from the finite parabolic subgroups; the product formula and Solomon's identity for finite `W`; Bott's formula for affine `W`)" | `poincare_series()`, by Steinberg's formula over the nerve and Solomon's product on each finite parabolic | `groups.py:8762` | yes for the series, in every case checked (finite, affine, hyperbolic); Steinberg and Solomon are the routes used, Bott's formula is not |
| 6 | "`chi(W) = 1/W(1)`" | `euler_characteristic()` | `groups.py:8792` | yes |
| 7 | "the growth rate of infinite `W`, as a Perron or Salem number. These two classes of real algebraic integers are owned if not already present." | `growth_rate()`; the classes as `PerronNumbers` and `SalemNumbers`, condition sets of the owned real algebraic numbers decided from the minimal polynomial | `groups.py:8821`; `categories/rings/ring_foundation.py:8035`, `:8060`, `:8085`, `:8090`; bound at `rings/__init__.py:170-171` | yes, with the finding that an affine or finite growth rate is `1` and is in neither class |
| 8 | "Crystallographic groups are constructed as stabilizers `GL(V)_L` of lattices `L <= V`. The existing chamber code (`categories/chamber_complexes.py`) and the Vinberg route thread into this owner." | the stabilizer is `Lattices(...).Aut()`, which is the lattice's own owner; nothing hands a chamber's wall roots to the Coxeter group | `categories/chamber_complexes.py:80` (`fundamental_chamber`), `categories/hyperbolic_lattices.py:1863`, `:2115` | no |

## Item 4: what the ring needs

`degrees()` gives the degrees, so `molien_series()` is the Hilbert series of a
polynomial ring on `n` homogeneous generators of those degrees: Molien's series
is decided.  The ring itself is not: `categories/algebras/graded_algebras.py`
carries no Hilbert or Molien series operation and no datum of generator degrees,
`k[V]` carries no action of `W` (so `k[V]^W` cannot be cut out as a fixed
subring or fixed module), and no GIT quotient type `V // W` exists.  Deciding it
needs a graded polynomial presentation whose generators carry degrees, the
action of `W` on that ring, and then the fixed subring: three constructions, not
a declaration to add.

## Item 5: the affine case, and Bott's formula

The series is right in the affine case by measurement, not by a formula of
Bott's: the affine `A_2` system gives `W(t) = (1+t+t^2)/(1-t)^2`, and the
Cayley graph layers of its three simple reflections computed in the group
engine are

```
affine A2 layers: [1, 3, 6, 9, 12, 15, 18, 21]
```

i.e. `3k` above the first layer, which is the series' expansion.  The form
`W_f(t)/(1-t)^n` that one might expect for an affine system is *not* what the
group has (`W_f(A_2) = 1+2t+2t^2+t^3` here), so the affine case is asserted from
the series and this layer count, and no affine-specific formula is claimed.

## Item 7: the two classes, and what they exclude

Perron numbers are the real algebraic integers `alpha > 1` all of whose other
conjugates have smaller modulus (Lind, *The entropies of topological Markov
shifts and a related class of algebraic integers*, Ergodic Theory Dynam.
Systems 4 (1984)); Salem numbers are those with every other conjugate of
modulus at most `1` and one on the unit circle.  Both classes are condition sets
of the owned real algebraic numbers, decided exactly from the roots of the
minimal polynomial in the algebraic closure.  Consequence worth stating: the
growth rate of a finite or affine system is `1`, which is in neither class, so
the issue's "growth rate of infinite `W` as a Perron or Salem number" is a
statement about the hyperbolic cases; the `(2,3,7)` group's rate is in both
classes.

## Item 8: the chamber route

Two things stand in the way, and neither is a declaration to add:

1. The chamber complex is built by `HyperbolicLattices.chamber_complex`
   (`categories/hyperbolic_lattices.py:2115`), i.e. by `fundamental_chamber`
   (`:1863`), which is the Vinberg route and is gated by the wall-Gram
   recognizer at `categories/vinberg_invariants.py:316`
   (`is_acute_angled_hyperbolic_polytope_gram`), which rejects a degenerate wall
   Gram; #152 owns that defect.
2. In this checkout the route could not be exercised at all: building a chamber
   reaches `timing.stage` and dies in `current_commit()` at
   `timing.py:248`, `git -C /repos/sage-extensions rev-parse HEAD` exiting 128,
   because this work is done in a linked worktree whose `.git` file points
   outside the proot binding.  That is an environment fact, recorded here so
   nobody reads the absence of a chamber specimen as a passing check.

## Specimens, and what decides each

| specimen (issue wording) | decided by | value |
| --- | --- | --- |
| `W(E_8)` degrees and `W(1) = 696729600` | `degrees()` and the product of the degrees | `(2, 8, 12, 14, 18, 20, 24, 30)`, product `696729600` |
| `W(A_2)(t) = 1 + 2t + 2t^2 + t^3` | `poincare_series()`, cross-multiplied | numerator `t^3+2t^2+2t+1`, denominator `1` |
| affine `A_1`: `W(t) = (1+t)/(1-t)` | `poincare_series()`, cross-multiplied | `(t+1)/(1-t)` |
| `(2,3,7)`: Salem growth rate, Lehmer's number | `poincare_series()` denominator; `growth_rate()`; membership in the two classes | denominator `t^10+t^9-t^7-t^6-t^5-t^4-t^3+t+1`, rate `1.1762808182599176...`, in both classes |
| E_8's positive roots (no issue specimen) | `positive_roots()` at rank 8 | 120 roots, 3.03 s |

## What was run

`sage 11.0.beta5`, `/sage/.venv/bin/python`:

```
$ python -m pytest -o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget \
    -p sage_extensions.testing.test_lint --durations=0 -q \
    tests/objects/test_coxeter_diagram_a2.sage \
    tests/groups/test_the_degrees_and_growth_series_of_a_coxeter_system.sage
29 passed in 12.05s
```

Those two files are the ones that consume the change; no suite and no
whole-library gate was run.
