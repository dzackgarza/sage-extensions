# #375: the certify run's line-orbit call returns on both of its cards

**Result: at `main` `5fffcee`, `dzackgarza/lattice-database`'s
`tests/test_certify_process.py::test_a_search_that_never_ends_does_not_hold_back_other_cards`
passes with this repository bound at `/repos/sage-extensions` (`1 passed in
195.08s`), and the run's own log prints the `integral.primitive_orbits` value it
computes for **both** cards of that test — `0016` and `0012` — with every row
equal to the card's.** The refusal the issue records is real, is the one the same
report reproduces below by node id at the revision it was taken on (`main`
`523e797`), and its repair is #345's `44f097f` at the owner
`Lattices.ParentMethods.isotropic_lines_by_divided_class`; this unit records the
certify-side reproduction, decides it on the current head, and covers the second
card of that run by tag in this repository's tests.

## The card, the call, and the arguments

The test certifies two cards in a fresh root: `prepare_card(root, "0016")` plus a
copy of `lattices/0012.md`. `0016` is the hyperbolic plane `U`
(`gram_tensor [[0, 1], [1, 0]]`, rank 2, signature (1, 1), determinant −1) and
`0012` is `A2` (`[[2, -1], [-1, 2]]`, rank 2, positive definite, determinant 3).

The stopping field is `integral.primitive_orbits`. In
`latticedb/sage_genus.py:208` it is
`lambda lattice: _orbit_series(lattice.primitive_orbit_series())`, so the call
that raises is the preamble's public

    lattice.primitive_orbit_series()

on the lattice built from card `0016`'s `gram_tensor`, which for an indefinite
lattice is `lattice_orbit_invariants._primitive_isotropic_line_series`: for each of
the eight subgroups `O, SO, Otilde, SOtilde, O+, SO+, Otilde+, SOtilde+` it asks
`subgroup.isotropic_orbit_representatives(1).cardinality()`. For `Otilde` — the
stable orthogonal group, `ker rho` — rank one and index one take the divided-class
route `orthogonal_quotients._line_orbit_from_divided_classes`, with the
representative that the port returns for the single `O(U)`-orbit of isotropic
lines.

## The reproduction, by node id, with `main` at `523e797` bound

Runtime: `~/sage-image/rootfs` (Sage 11.0.beta5 / Python 3.14, config
`sha256:2d6a4754…`), `run.sh -w /work` with the port pin `991b88b0` at `/work`,
the sage-extensions worktree at `/repos/sage-extensions`, and
`dzackgarza/lattice-database` at `8113d7e` at `/repos/lattice-database`; the node
body is byte-identical at `8113d7e` and at `28a5f59`, the ref the evidence reads
(`diff` of the two files' `test_a_search_that_never_ends…` bodies: empty).

```
$ /sage/.venv/bin/python -m pytest \
    tests/test_certify_process.py::test_a_search_that_never_ends_does_not_hold_back_other_cards -s
0016 derive
0016 {'integer_valued': True}
0016 {'elementary_primes': []}
0016 {'genus_symbol': 'II_{1,1}'}
0016 {'genus_class_count': 1}
0016 {'overlattice_count': 1}
0016 {'hyperbolic_index': 1}
0016 {'automorphism_group_generator_morphisms': [[[-1, 0], [0, -1]], [[0, -1], [-1, 0]]]}
0016 {'discriminant_form': {'orthogonal_group_order': 1, 'isotropic_classes': 1, 'isotropic_orbits': 1}}
Traceback (most recent call last):
  File "/repos/lattice-database/src/latticedb/sage_genus.py", line 338, in <lambda>
    lambda: {field: SERIES[field](lattice, request["series_bound"]) if field in SERIES else VALUES[field](lattice)},
  File "/repos/lattice-database/src/latticedb/sage_genus.py", line 208, in <lambda>
    "primitive_orbits": lambda lattice: _orbit_series(lattice.primitive_orbit_series()),
                                                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/repos/sage-extensions/src/sage_extensions/categories/lattices.py", line 3672, in primitive_orbit_series
    return primitive_orbit_series(self, bound=bound)
  File "/repos/sage-extensions/src/sage_extensions/categories/lattice_orbit_invariants.py", line 179, in primitive_orbit_series
    return _primitive_isotropic_line_series(lattice)
  File "/repos/sage-extensions/src/sage_extensions/categories/lattice_orbit_invariants.py", line 143, in _primitive_isotropic_line_series
    "constant": subgroup.isotropic_orbit_representatives(1).cardinality(),
  File "/repos/sage-extensions/src/sage_extensions/categories/group/predicate_subgroups.py", line 506, in isotropic_orbit_representatives
    return _subgroup_isotropic_orbit_representatives(self, rank, flag=flag)
  File "/repos/sage-extensions/src/sage_extensions/categories/orthogonal_quotients.py", line 2156, in _subgroup_isotropic_orbit_representatives
    from_divided_classes = _line_orbit_from_divided_classes(subgroup, representative)
  File "/repos/sage-extensions/src/sage_extensions/categories/orthogonal_quotients.py", line 2118, in _line_orbit_from_divided_classes
    return tuple(
           ^^^^^
  File "/repos/sage-extensions/src/sage_extensions/categories/orthogonal_quotients.py", line 2120, in <genexpr>
    lattice.primitive_isotropic_vector_of_divided_class(component, divisor)
  File "/repos/sage-extensions/src/sage_extensions/categories/lattices.py", line 6252, in primitive_isotropic_vector_of_divided_class
    raise ValueError(
ValueError: no primitive isotropic vector of Integral lattice of rank 2 and signature (1, 1)
  has divisor 1 and divided class -[1]: the residue loop is exhausted -- every one of the 1
  residues of L/1L was tried, each with its 1 translations k in K/1K and every divisor pair of
  q(w)/(2h) in the residue classes of a and b, and no candidate passed q = 0, primitivity,
  divisor 1, and the class check
0012 derive
0012 {'integer_valued': True}
…
0012 {'primitive_orbits': {'O': {'constant': 0, 'z': [0, 1, 0, 0], …}, …}}
…
=========================== short test summary info ============================
FAILED tests/test_certify_process.py::test_a_search_that_never_ends_does_not_hold_back_other_cards
1 failed in 203.45s (0:03:23)
ChildProcessError: /repos/lattice-database/src/latticedb/sage_genus.py failed on 0016 (exit status 1)
```

The frames, the lattice (`Integral lattice of rank 2 and signature (1, 1)` = `U`),
the divisor 1 and the refused class are the issue's, character for character: the
observed `orthogonal_quotients.py:2118` is the `return tuple(` that this
revision's function ends with, and the `ValueError` is the one the loop's
emptiness produces. Card `0012`'s worker returns its rows in the same run — only
`0016` stops.

## The cause, at its owner

`Lattices.ParentMethods.isotropic_lines_by_divided_class(d)` enumerates the
residues of `L/dL`, and for a residue `(a mod d, b mod d, w mod d)` in a scaled
hyperbolic pair `e, f` with `b(e, f) = h` orthogonal to a complement `K`, solves

    q(a e + b f + w) = 2 h a b + q(w) = 0,   i.e.   a b = -q(w)/(2 h),

over the integral pairs `(a, b)` compatible with the residue. Its pair enumeration
returned `((0, 0),)` when `q(w) = 0`, and `(0, 0)` is the zero vector, which the
construction then rejects as not primitive. At divisor 1 the residue of `L/1 L` is
the single point, so `w = 0` and `q(w) = 0` for every candidate: **the loop could
not produce a primitive isotropic vector at divisor 1 on any lattice.** `U` is the
smallest witness — its basis vector `e` is primitive, isotropic, of divisor 1, and
its divided class is the representative's — and the measured state at the owner,
with `main` at `523e797`:

```
U rank 2, det -1, b(e,f) = 1
div(e) = 1, q(e) = 0, primitive = True
U.divided_discriminant_class(e): [1]
U.isotropic_lines_by_divided_class(1): {}                     <- the empty map
U.primitive_isotropic_vector_of_divided_class(class(e), 1): RAISED
U.primitive_orbit_series(): RAISED (2.32 s)
A2.primitive_orbit_series(): returns, all eight rows as card 0012 states them
```

The `-[1]` in the message is a printing of the same class: `[1]` and `-[1]` in
`A_U = L^#/L = 0` compare equal and hash equal here, so the loop's keys and the
requested class were never a mismatch — the map was empty.

## The repair, and what it rests on

The repair is `44f097f` ("Solve the divided-class equation's vanishing case, so
divisor 1 finds its vectors", #345), in `lattices.py`, and it is the fix this
issue needs: it decides `a b = 0` by its solutions `(a, 0)` and `(0, b)` (helpers
`class_steps`, `vanishing_pairs`) instead of by the single pair `(0, 0)`, leaving
the four candidate checks (`q(v) = 0`, primitivity, `div(v) = d`, class agreement)
in place, so a missing candidate can only make a class report absent.

Each statement the repair uses, with its source:

1. **`q(a e + b f + w) = 2 h a b + q(w)`.** `q(x) = b(x, x)` with `b` bilinear
   (this lattice's own `q`), `e, f` isotropic, `b(e, f) = h`, and `⟨e, f⟩`
   orthogonal to `K` — a one-line expansion, not an algorithm: no external page is
   needed and none is cited (the identity is printed in the owner's docstring).
2. **`a b = 0` implies `a = 0` or `b = 0`.** `ZZ` is an integral domain.
3. **`[v/d]` depends only on the residue `v mod d L`.** `(v + d x)/d = v/d + x` and
   `x ∈ L` is zero in `A_L = L^#/L`, so the class is a function of the residue;
   this is the residue loop's own premise, printed in the owner's docstring.
4. **The divisor-one case is `w = 0`, `q(w) = 0`.** `L/dL` has one residue when
   `d = 1`, so the complement part vanishes and case 2 applies to every candidate.

None of the four is a hand-rolled generation or enumeration claim over a
published theorem; they are the complete solution of the equation the construction
already wrote down. The correspondence the *consumer*
(`orthogonal_quotients._line_orbit_from_divided_classes`) rests on — `ker rho`-orbits
of lines ↔ `rho(G)`-classes of divided classes, with fibre
`[Stab_{rho(G)}(c) : rho(H)]` — is orbit–stabilizer for the action of `G/ker rho`
through `rho`, and the function computes that index from the two exact images
rather than assuming it, refusing (returning `None`) when it is not one.

## The state on `main` at `5fffcee`

Owner measurements, same runtime, same worktree:

```
U.divided_discriminant_class(e): [1]
U.divided_class_residue(class, 1): (1, 0)
U.isotropic_lines_by_divided_class(1): {[1]: e_0}
U.primitive_isotropic_vector_of_divided_class(class, 1): e_0
U.isotropic_lines_by_divided_class(1, classes=(class,)): {[1]: e_0}
U.primitive_orbit_series(): {O 1, SO 2, Otilde 1, SOtilde 2, O+ 1, SO+ 2, Otilde+ 1, SOtilde+ 2} in 4.15 s
A2.primitive_orbit_series(): {O 0, SO 0, Otilde 0, SOtilde 0, O+ 0, SO+ 0, Otilde+ 0, SOtilde+ 0} in 0.07 s
class(e) = [1], class(-e) = -[1], equal: True, hashes equal: True
Otilde(U) line orbits: one
```

The certify run itself, `1 passed in 195.08s`, with `-s` so the worker's own
values are in the log — both cards reach the field and return the cards' rows:

```
0016 {'primitive_orbits': {'O': {'constant': 1, …}, 'SO': {'constant': 2, …},
      'Otilde': {'constant': 1, …}, 'SOtilde': {'constant': 2, …}, 'O+': {'constant': 1, …},
      'SO+': {'constant': 2, …}, 'Otilde+': {'constant': 1, …}, 'SOtilde+': {'constant': 2, …}}}
0012 {'primitive_orbits': {'O': {'constant': 0, 'z': [0, 1, 0, 0], 'w': [0, 0, 0, 0]}, …
      'SOtilde': {'constant': 0, 'z': [0, 2, 0, 0], …}, …}}
Certification time budget exhausted
1 passed in 195.08s (0:03:15)
```

The budget line is the test's own 150 s deadline (`genus.certify(…, time.time() +
150, workers=2)`), not a stop inside a field: both cards' `integral.primitive_orbits`
returned before it, and the two assertions the test makes hold.

### Re-verified on the pushed head

This change sits on `fbb1a76` (one commit after `5fffcee`, #373, which touches
`IsotropicReductions` only), and the same two runs there give: the series test
`2 passed in 52.12s`, and the certify node id `1 passed in 161.20s`, with the
run's log printing both cards' `integral.primitive_orbits` exactly as above.

## The test in this repository

`tests/lattices/test_primitive_orbit_series_on_the_catalogued_lattices.sage` now
covers **both cards of that certify run** by tag. The digest gained `0012`,
regenerated (not edited) by `tests/cards/refresh_lattice_database_enriques.py`
whose `PRIMITIVE_ORBIT_TAGS` names the three cards this row group reads; the
refresh at the digest's own pinned ref `dbc9fc6a` reproduces the committed file
byte for byte before the addition, so the diff is the one entry:

```
tests/cards/lattice-database-enriques.json         | 145 +++++++++++++++++++++++++
tests/cards/refresh_lattice_database_enriques.py   |   6 +-
…test_primitive_orbit_series_on_the_catalogued_lattices.sage |  54 +++++---
```

The test builds each lattice from the card's `gram_tensor` and compares every term
the call returns — the line count `constant` and the norm rows `z` and `w` — with
the card's `integral.primitive_orbits` row for the same subgroup, on `0016`
(`U`), `0012` (`A2`, the definite card of the certify run) and `026E`. The
non-vacuity check is now per card: `0016` and `026E` state a positive `O` line
count, and `0012` states `constant 0` with a nonzero `z`, which the call returns.

```
$ /sage/.venv/bin/python -m pytest \
    tests/lattices/test_primitive_orbit_series_on_the_catalogued_lattices.sage \
    -p sage_extensions.testing.test_lint -p sage_extensions.testing.suite_budget --no-time-gates
2 passed in 61.43s (0:01:01)
```

## What this unit does not do

- The baked copy in the image reported `definite_lattices.py:294 _square_shell` →
  `AttributeError: 'int' object has no attribute 'parent'` on the same run. That
  is a ring-crossing defect repaired on `main` before this unit (#291; the
  comment at `_roots_of_square`, which now takes `square` from the lattice ring),
  not a second cause here: at `5fffcee` card `0012`'s `roots`/`norms` and the
  definite branch all return, as the run log above shows.
- The evidence ref of this issue (`lattice-database` `28a5f592df`) is not the
  clone head used here (`8113d7e`); the node body was checked identical rather
  than assumed.
- No library edit: the defect is #345's, repaired at its owner at `44f097f`, and
  the measurements above are of `main` as it stands.
