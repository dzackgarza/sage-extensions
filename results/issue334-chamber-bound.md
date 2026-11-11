# issue 334: the bound of the chamber of `II_{1,17}`, and the k = 2 genus

Stage 1 of #317. The public genus call closes the genus of `<-2k> + E8(-1)^2` for
`k = 1` and `k = 2` through the chamber of `II_{1,17}`; the two truncations that
stood on `main` (`coordinate_bound = 10` and the `E8` norm floor `-40`) are gone,
replaced by bounds proved from the chamber's own walls; the class counts are read
from cards `6JRX` and `6JRY` by tag; and the Siegel mass is asserted.

## 1. The three walls that carry the hyperbolic coordinates

`HyperbolicLattices(ZZ)(U + E8 + E8).fundamental_chamber().wall_roots()` returns
19 roots. Every one has square `-2` in the model's own Gram (asserted at each
call), and the model's Gram is `U` at `[0:2]` — `q(a, b) = 2ab` — orthogonal to
two `E8(-1)` Cartans at `[2:10]` and `[10:18]` (both asserted). So a vector is
`v = (a, b, x, y)`, `q(v) = 2ab + q(x) + q(y)`, and the chamber is the cone
`{v : b(r, v) >= 0}` over the 19 walls. Reading a wall `r = (alpha, beta, p, q)`
needs the hyperbolic components swapped, because the `U` half of the Gram is
`[[0, 1], [1, 0]]`: `b(r, v) = alpha*b + beta*a + b(p, x) + b(q, y)`.

Sixteen of the walls are the two blocks' simple roots — the unit vectors of
`[2:10]` and `[10:18]` — and the three that carry `(a, b)` are, in these
coordinates,

| wall | vector | inequality `b(r, v) >= 0` |
| --- | --- | --- |
| 16 | `(-1, 1, 0, 0, ..., 0)` | `-a + b >= 0` |
| 17 | `(0, -1, -2, -4, -6, -5, -4, -3, -2, -3, 0, ..., 0)` | `-a + b(-theta, x) >= 0` |
| 18 | `(0, -1, 0, ..., 0, -2, -4, -6, -5, -4, -3, -2, -3)` | `-b + b(-theta, y) >= 0` |

with `theta = (2, 4, 6, 5, 4, 3, 2, 3)` the block's highest root in the
library's labelling, `q(theta) = -2`, every coordinate at least `1`. Wall 16 is
the diagram's `A_1`; with the two affine nodes 17 and 18 it gives the
`2 E_8 + A_1` elliptic subdiagram of the 19 nodes of `II_{17,1}`
(H. A. Heckman, *Hyperbolic reflection groups and the Leech lattice*, master's
thesis, Radboud, Ch. 4: 19 nodes, `det = 0`, signature `(17, 1, 1)`,
`Sym(D) = Z/2`, and removing the middle node leaves `2 E-tilde_8`).

`issue334-probe2.log` and `issue334-probe4.log` print all 19 walls, `q(theta)`,
and the fact that the sixteen block walls are unit vectors.

## 2. The bound

**Hypotheses**, checked at every call in `_unimodular_complement_frame`: the
sixteen block walls are simple roots; the three remaining walls are exactly the
vectors above; `q(theta) = -2`; `theta`'s coordinates are all at least 1.

**Step 1 — the chamber.** Every vector of an `O(II_{1,17})`-orbit can be carried
into the closed chamber by a reflection (Vinberg's algorithm: E. B. Vinberg,
*Some arithmetical discrete groups in Lobacevskii spaces*, 1975; Conway–Sloane,
*SPLAG*, 3rd ed., Ch. 27, §2 and Fig. 27.1 for the `II_{9,1}` instance of the
same construction). So one representative of every class of the genus lies inside
it, which is what makes a chamber walk exhaustive at all (Nikulin, *Integral
symmetric bilinear forms and some of their applications*, Math. USSR Izv. 14
(1980), Proposition 1.15.1 with its proof, pp. 128–129).

**Step 2 — dominance in the blocks.** Walls 0–15 are the simple roots, so
`b(alpha_i, x) >= 0` and `b(alpha_i, y) >= 0`: both `E8(-1)` parts are dominant.
`E8` is unimodular, so a dominant vector is `x = -sum_i c_i omega_i` with
`c_i = b(alpha_i, x) >= 0` integral, and then `q(x) = -c^T C^-1 c <= 0`.

**Step 3 — signs and order.** Put `A = -a`, `B = -b`. Wall 16 gives `B >= A`;
walls 17 and 18 give `A >= b(theta, x)` and `B >= b(theta, y)`, and
`b(theta, x) = sum_i theta_i c_i >= 0` because every `theta_i >= 1` and every
`c_i >= 0`. Hence `A, B >= 0`, and `q(v) = 2k > 0` forbids `A = 0` or `B = 0`
(since `q(x) + q(y) <= 0`), so `a < 0` and `b < 0` with `|b| >= |a| >= 1`: a
chamber vector of positive square has both hyperbolic coordinates negative.

**Step 4 — the block norms.** `X := -q(x)`, `Y := -q(y)`. For `c >= 0` with
`theta^T c <= A`:

- Cauchy–Schwarz in the positive definite form `C^-1` gives
  `(theta^T c)^2 <= (theta^T C theta)(c^T C^-1 c)`, and
  `theta^T C theta = -q(theta) = 2`;
- `c |-> c^T C^-1 c` is convex, so over the simplex `{c >= 0, theta^T c = A}`
  its maximum is attained at a vertex, `c = (A / theta_i) e_i`;
- so `X <= A^2 Lambda` with `Lambda = max_i (C^-1)_ii / theta_i^2`.

`Lambda` is computed at every call from `-C^-1` and `theta` and asserted
`0 < Lambda <= 1`. For `E8` in the library's labelling the eight ratios
`(C^-1)_ii / theta_i^2` are

    (4/4, 14/16, 30/36, 20/25, 12/16, 6/9, 2/4, 8/9)

so `Lambda = 1`, `X <= A^2` and `Y <= B^2`, sharply: the vertex
`c = (A / theta_i) e_i` at the maximising `i` attains it, so no better *function
of a alone* bounds a block's norm, and the enumeration cannot be a box in
`(a, b)`.

**Step 5 — the enumeration.** `q(v) = 2k` reads `2AB = 2k + h` with
`h := X + Y >= 0`, and step 4 keeps `0 <= X <= min(h, A^2)` and
`0 <= Y <= min(h, B^2)`. So for a fixed height `h` the pairs `(A, B)` are the
divisors of `(2k + h)/2` with `A <= B` — finitely many — and each block's norm
is confined to an interval. The walk goes over `h = 0, 2, 4, ...` in increasing
order, so it is exhaustive over the closed chamber and each height is finite. It
stops when the classes' masses add up to the Siegel mass (Conway–Sloane,
*SPLAG*, 3rd ed., Ch. 16), which is the completeness certificate: a class it had
not reached yet would leave the mass short, and the call would not return rather
than return a short genus.

Two further hypotheses guard the route: the determinant must be even (every
vector of the even unimodular `II_{1,17}` has even square, so an odd `order` is
complemented by no vector at all), and the improper spinor kernel quotient must
be trivial (the returned tuple is one group, which is the genus's improper
spinor split only then; both genera here have quotient order 1 —
`issue334-probe5.log`).

## 3. What the bound replaced, and what it costs

`main` bounded the walk with `coordinate_bound = 10` on `a, b` and the norm
floor `-40` on a block, and its own docstring called both truncations. Both are
gone: `_dominant_block_vectors` enumerates a block's dominant vectors up to
whatever norm a height needs, with the coefficient cap derived from the same
positivity, and the height walk supplies the norm bound.

| genus | heights walked | `(A, B)` pairs | chamber vectors tested | past the walls | classes | walk |
| --- | --- | --- | --- | --- | --- | --- |
| `k = 1` | 16 (0, 2, …, 30) | 16 | 88 | 6 | 4 | 13.8 s |
| `k = 2` | 35 (0, 2, …, 68) | 72 | 697 | 12 | 9 | 27.6 s |

`issue334-probe4.log` (k = 1) and `issue334-probe6.log` (k = 2), whose walk is
the shipped one line for line; both close the mass exactly. The nine `k = 2`
classes appear at heights 0, 4, 4, 8, 14, 28, 28, 68, 68 — the 544-root
`D_17(-1)` and the 480-root class that closes the mass are the two at height 68.
The cost of the call is the chamber (69–77 s here) plus the exact PARI work per
class, not the walk.

## 4. The k = 2 path: what the probe did that the shipped code did not

The probe closed the `k = 2` mass in 30 s while the shipped path did not return
in 1080 s, and the difference is not the number of candidates admitted for
`d = 4`. It is one wrong number in the complement's rank:

    system = matrix(SageZZ, [covector])
    _, _, kernel = system.smith_form()
    basis = kernel[:, int(system.rank()):]
    if basis.ncols() != rank - 1:      # main: `rank` is the *lattice's* 17, so 16
        continue

Measured (`issue334-probe6.log`, first chamber vector of the model):

    covector dimensions (1, 18), rank 1, kernel dimensions (18, 18),
    basis dimensions (18, 17): basis.ncols() = 17, the lattice rank - 1 = 16,
    model_rank - 1 = 17

The covector is a `1 x 18` row of the *model*, so the kernel basis has
`model_rank - 1 = 17` columns and only the probe's `!= 17` accepted it. On
`main` every candidate of every rank-17 genus failed that test, so
`_genus_classes_through_the_chamber` returned `None` for every input and the
shipped route was never the chamber route: `k = 1` came out of the fallback
`neighbor_iteration` walk (116.8 s), and `k = 2` is the genus whose nine classes
that walk cannot reach — the 544-root `D_17(-1)` class among them — so it never
returned.

The shipped path is now the probe's algorithm with `model_rank - 1`. The root
count of `v^perp` is read before the exact isometry test, as in the probe
(`short_vector_list_up_to_length(2)` costs 0.02 s at rank 17), and the two
expensive operations run only for a class the walk has not seen: at rank 17,
`number_of_automorphisms` costs 1.04 s at `k = 1` and 6.77 s at `k = 2`, and
`qfisominit` 0.10 s and 6.22 s (`issue334-probe3.log`, on a VM carrying four
other projects' probes).

Measured on the public call:

    k = 1: 4 classes, mass exact, 96.51 s (the chamber is ~77 s of it)
    k = 2: 9 classes, mass exact, 27.11 s (the chamber is ~69 s of it)

and `_genus_classes` alone, with the chamber already built, at `k = 2`:
**25.6 s** (`issue334-probe6.log`), against the probe's 30 s and against no
return in 1080 s on `main`. The run quoted below is at the pushed commit, which
is the same branch rebased onto `main` at `6db8551` (the two commits that
landed after `7519715` touch `lattices.py` at lines 2298–6544, not this route).

## 5. The tests

`tests/lattices/test_genus_of_the_scattone_summands.sage`: the `k = 1` count
against card `6JRX` (4) and the `k = 2` count against card `6JRY` (9), both read
by tag through the directory's `card` abbreviation and neither typed into a test;
each genus's Siegel mass asserted against its own exact value; and both counts
taken through the public `genus().representatives()`.

    $ /sage/.venv/bin/python -m pytest tests/lattices/test_genus_of_the_scattone_summands.sage \
        -o addopts='' -p qc_sage_session -p sage_extensions.testing.suite_budget \
        -p sage_extensions.testing.test_lint --tb=short -rf --no-time-gates
    8 passed in 127.63s (0:02:07)

The same file was red on `test-lint` on `main` — four findings, `TL01` on
`import json` and `from pathlib import Path`, `TL13` on `__file__`, `TL10` on
`len()` — so it could not be run at all with the lint plugin loaded
(`issue334-test2.log`). It now reads its cards through the
`tests/lattices/conftest.py` abbreviation that the lint documents, and the two
`len()` calls are `sum(1 for _ in ...)`. The module for the branch this changed:

    $ ... pytest tests/lattices/test_genus.sage ...
    10 passed

## 6. Provenance

`src/sage_extensions/categories/lattices.py`: `_dominant_block_vectors`,
`_unimodular_complement_frame` and `_genus_classes_through_the_chamber` carry
the proof above in their docstrings, step by step, with the citation of each
step; every claim the walk rests on is asserted where it is used.
