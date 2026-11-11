# #350: `test_reflection_hyperbolic` — a missing `represents` on a local ring, and three domains

**Result: the module is green, `5 passed in 3.07s`.** The four failures had two causes, and
neither of them was a defect in `represents`.

## The four failures, on `main` at `c52ed41`

```
1 failed, 4 passed → four of five red, each on a missing name:

test_the_root_length_forty_nine_form_does_not_represent_one     line 67
  lattice.localize_at_prime(7).represents(1)
  AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'represents'
  (first: KeyError: 'represents')

test_vinberg_enumeration_closes_the_polyhedron_of_u_plus_a1     line 79
  lattice.vinberg_simple_roots(max_decompositions=200)
  AttributeError: … has no attribute 'vinberg_simple_roots'

test_u_plus_a1_is_reflective_but_not_cocompact                  line 103
  lattice.is_reflective(max_decompositions=200)
  AttributeError: … has no attribute 'is_reflective'

test_the_edgewalk_and_vinbergs_algorithm_agree_that_u_plus_a1_is_reflective  line 113
  lattice.edgewalk_is_reflective()
  AttributeError: … has no attribute 'edgewalk_is_reflective'
```

## Cause 1: `represents` on the localization — no owner, by the method's own domain

`Lattices.ParentMethods.represents` (`src/sage_extensions/categories/lattices.py:4561`) cites
Serre, *A Course in Arithmetic*, Ch. IV, §1 (pp. 27–34, the general section; §2 is the
\(p\)-adic one, pp. 35–40) and states its domain in the first paragraph: "The lattice is
nondegenerate of finite rank over `QQ`, `AA` or `ZZ`." Its dispatch enforces that:

```python
case _ if _engine_ring(ring) is not SageZZ:
    assert False, (f"representation of {value} by {self!r} is decided here over ZZ, QQ, AA and
    RR, not over {ring}")
```

Measured on the failing specimen:

```
localized = lattice.localize_at_prime(7)
  type:       OwnedJoinCategory.parent_class
  category:   modules with a represented selected finite-presentation backend / localized modules
  has represents: False    has gram_tensor: False    has b: False    has q: False
```

`localize_at_prime` is a **module** operation (`categories/modules/pure/modules.py:3171`,
"Return the localized module `M_p` at a represented prime"): it localizes the module and the
form is not part of the result. So the object the test asked is not a lattice at all, and the
ring it lives over is outside `represents`'s cited domain — neither the ring's category
(`Lattices(local ring)`, which the object is not in) nor the local-form object owns the call.

**What the test asked of it and what the source says.** The value is the paper's, and it is an
*integral* statement: N. Bogachev and A. Kolpakov, *Thin hyperbolic reflection groups*,
arXiv:2112.14642v4, **§6.2, p. 9** — "Hence \(q(r) = 49m_2^2 + 14m_1m_3 - 28m_2m_3 + 6m_3^2\).
However, \(q\) does not integrally represent \(1\)." The test's modulo-\(7\) sentence is its own
proof of that statement, not a second value.

So the localized assertion is deleted and the integral one stays, decided by
`lattice.represents(1)` with the citation above; the module docstring records why the local
half is not asked here. There is no card for this lattice either: the catalogue's pin
`dbc9fc6` holds no rank-three lattice of signature `(1,2)` with `|det| = 2401`, so nothing was
read by tag.

## Cause 2: `U + A1` is a `Lattices` object, and the algorithms live on `HyperbolicLattices`

The three remaining failures are #343's defect on one more module: the reflection algorithms
are methods of `HyperbolicLattices`, whose class docstring states the domain — a lattice of
signature \((n,1)\) or \((1,n)\) (V. V. Nikulin, *Reflection groups in hyperbolic spaces and the
denominator formula for Lorentzian Kac--Moody Lie algebras*, Izvestiya: Mathematics 60 (1996),
no. 2, arXiv:alg-geom/9503003v6, §1.1, (1.1.1), preprint p. 3) — and that "a lattice enters this
category by being handed to it: `HyperbolicLattices(ZZ)(L)` checks the signature and refines
`L`". `+` returns a `Lattices` object, as its own docstring says, so the test's sum never
entered the category.

The repair is the same one #343 accepted: `u_plus_a1()` now returns
`HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))`, and the four assertions on it
are untouched.

## Runs

```
$ pytest tests/lattices/test_reflection_hyperbolic.sage --durations=0
.....                                                                    [100%]
1.62s call  …test_the_edgewalk_and_vinbergs_algorithm_agree_that_u_plus_a1_is_reflective
0.72s call  …test_vinberg_enumeration_closes_the_polyhedron_of_u_plus_a1
0.20s call  …test_vinbergs_criterion_bounds_the_root_lengths_of_the_bogachev_kolpakov_lattices
0.10s call  …test_the_root_length_forty_nine_form_does_not_represent_one
0.01s call  …test_u_plus_a1_is_reflective_but_not_cocompact
5 passed in 3.07s
```

Time gates on, test-lint plugin loaded, no findings.

## What is not done

`represents` over a localized ring is not implemented, and no attempt was made to make
`localize_at_prime` on a lattice return a form-carrying lattice: the first is mathematics this
library does not have (the local \(p\)-adic decision it does have is
`_Genus.local_representations`, used inside `represents` for the `ZZ` case), and the second
would change the meaning of an inherited module method that other callers use. The local
half of the paper's argument is therefore stated, not asserted.

## Adjustment: no typed value survives, and the verdicts come from card 0026

Every assertion the module makes is now either read by tag or computed from the lattice.

| assertion at `9cbc5fa` | disposition |
| --- | --- |
| `lattice.determinant() == -2401` | **deleted** — an invariant of the test's own Gram matrix, not a value |
| `signature_pair().first() == 1`, `.second() == 2` | **deleted**, same reason |
| `lengths.cardinality() == 6`, the six listed divisors | **deleted** — a derivation in the docstring, not a card |
| `lengths.cardinality() == 10`, the ten listed divisors, `4 not in lengths`, `21 not in lengths` | **deleted** |
| the same test, replaced by the property | **kept, changed**: `bound = 2 * lattice.discriminant_module().exponent()` per lattice, and every returned length is checked to divide it — no length and no divisor typed |
| `is_reflective(max_decompositions=200) is True` (twice) | **kept, changed** to `is bool(card 0026's hyperbolic.reflective)` |
| `edgewalk_is_reflective() is True` | **kept, changed** to `is bool(card 0026's hyperbolic.reflective)` |
| `is_cocompact(max_decompositions=200) is False` | **deleted** — no card field holds cocompactness |
| `not lattice.represents(1)` on the Bogachev--Kolpakov form | **deleted** — no card holds it; the test that held it is deleted, since nothing else remained in it |
| `roots.cardinality() >= 3`, `walls.cardinality() >= 3`, the per-root involution/negation checks | **kept** — structural claims about what the walk returns, not lattice values |

The reflective verdict is read once from the digest's `hyperbolic_reflectivity` row for card
`0026` (`U + A1(-1)`, Gram `[[0,1,0],[1,0,0],[0,0,-2]]`, `reflective: true`, certified), and the
lattice the module builds is checked against that card's Gram, so the comparison is about the
card's lattice and not a lookalike. The test whose subject was the Bogachev--Kolpakov form is
gone with its assertion, and the docstring sentences that stated what the library does not do
or what the test does not ask went with it.

Runs on the adjusted module:

```
$ pytest tests/lattices/test_reflection_hyperbolic.sage --durations=0
....                                                                     [100%]
1.51s  test_the_edgewalk_and_vinbergs_algorithm_agree_that_u_plus_a1_is_reflective
0.71s  test_vinberg_enumeration_closes_the_polyhedron_of_u_plus_a1
0.47s  test_vinbergs_criterion_bounds_the_root_lengths_of_the_bogachev_kolpakov_lattices
4 passed in 3.09s

$ just test-push
Push syntax: 29 file(s) checked; no errors.
exit 0
```
