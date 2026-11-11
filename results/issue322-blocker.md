# #322: measured, with the structural method's missing primitive named

`integral_parameter_classes` (`isotropic_lifts.py:385`) lists the parameter module's
elements to find the residue classes whose lift is integral. The issue asks for the
classes to be computed from the module's structure. This report records what the unit
measured, the criterion that is proved, and the owned primitive the implementation needs
and does not have. **The method is not implemented in this unit.**

## Measured: the size of the search, and the cost of one test

Specimen: `T_Co = <2> + (U + E8(-1))(2)` from Dolgachev--Kondo, Izv. Math. 77:3 (2013),
eq. (3.6), p. 513; marked line `<e_1>` (the `U(2)` generator `ep`), identity reduction.

| quantity | value | log |
| --- | --- | --- |
| parameter space rank | 9 | `.tmp/p322-probe2.log` |
| `P/mP` cardinality | **262144 = 4^9** | `.tmp/p322-probe2.log` |
| one class test (`parameterization`, then `integral_restriction`) | **0.353 s + 0.039 s** | `.tmp/p322-probe3.log` |
| Witt base point integral | **True** | `.tmp/p322-probe3.log` |
| `U + <2>`, the small control | `|P/mP| = 2`, locus 2 classes | `.tmp/p322-probe5.log` |

So the present method spends about 0.39 s per class over 262144 classes: roughly 28
hours, which is why the public call does not return at 700 s. The listing is not the
whole cost -- the per-class integrality test is a rational isometry construction -- but
for this lattice the **locus is decided by one lattice condition**, below, and the listing
is what prevents asking that question.

## The criterion that is proved, and what it needs

Eichler's transvection formula (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
(4)--(5), already cited in this module's docstring) gives, for a primitive isotropic `f`
of an even lattice `L'` and `x` in its rational span,

    E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x .

Two consequences, both elementary and both checked by hand:

- `E_{f,x}` preserves `L'` **iff** `x` lies in `L'`. If `x` is in `L'` each term is
  integral (`q(x)/2` by evenness of `L'`); conversely a `y` with `b(y,f) = 1`, which a
  primitive isotropic `f` supplies, gives `x = [b(y,x) - q(x)/2] f - (E(y) - y)` in `L'`.
- Since `phi(a) = E_{f,s(a)} phi(0)` and `phi(x+y) = E(y) phi(x)`, the integral residue
  locus is the kernel of the class map `a + mP |-> s(a) + L'`, **when `phi(0)` is
  integral**. On `T_Co` with the identity reduction, `phi(0)` is integral (measured
  above), so the locus there is that kernel: a subgroup of `P/mP`, of index at most
  `|A_{L'}| = 2048`, in place of a 262144-class search.

## The missing primitive

Computing that kernel needs the section `s` on a basis of `P` as **coordinates in `L'`**,
and then an exact integer Smith form. Both parts are available only outside the owned
boundary:

- the coordinate extraction that exists is Mor-level
  (`framing_morphism().lift(...)`, `ModulesOverIntegralDomains(...).generic_fibre_map()`),
  and the pairings it produces are owned value elements;
- feeding those to Sage's matrix/Smith machinery fails at the coercion, measured:
  `ValueError: Fraction Field of Integer Ring is not in Category of sets with partial maps`
  (`.tmp/p322-probe7.log`), because an owned value element is not a Sage rational.

So the structural method needs one owned operation that does not exist yet: a
**rational coordinate matrix of a module morphism into a lattice, together with its Smith
normal form, computed inside the owned value modules** -- or an owned "is this rational
vector in this lattice" test that is O(rank^2) rather than an isometry construction. With
either, the kernel above is a two-line computation; without one, any implementation would
convert the owned values by hand or restate the transvection formula outside
`eichler_transvection`, which is the parallel-implementation route the repository forbids.

I did not ship a guessed criterion. The two cheap alternatives are false in general: when
`phi(0)` is **not** integral the locus is not the kernel above (the transvection must
compensate the base point's fractional part), so a criterion that skips the base test
would silently change the lift decision on every non-identity reduction -- which is
exactly the port's case.

## State of the tree

- `tests/lattices/test_the_coble_lattice_line_orbit_call_returns.sage` is the regression
  test through the public call. It is **red**: the call does not return, and its stop at
  the listing frame is recorded in this commit (`.tmp/p322-red.log`).
- The existing tests of this module and the `029J` rows: `.tmp/p322-gate-existing.log`.
