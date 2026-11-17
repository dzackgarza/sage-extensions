# The basis adapted to a null flag: the ring it was rebased over, and the canonical span

Measured on the adopted runtime (`ghcr.io/dzackgarza/sage@sha256:59568577…`,
Sage 11.0.beta5 / Python 3.14, `/sage/.venv/bin/python`) on worktrees of `main`
`34c9be8`, with the indefinite port at `refs/remotes/omm/main` (`54d12c2e`), the
commit whose `IsotropicInduction.flag_action_data` the issue's traceback cites,
bound at `/work`.  With the port at its paused pin `991b88b0` that module has no
`flag_action_data`, so the ambient flag rows never ask for an adapted basis at
all and nothing here is reachable; every row measurement below is with
`54d12c2e`.  Probes and logs are under `.tmp/587-*`.

## 1. The datum, and the line that was wrong

`_engine_flag_adapted_rows` (`src/sage_extensions/tensors/tensor.py`) adapts a
basis to a chain of spans `T_1 < ... < T_k < M` by solving the relation `C` of a
smaller span to a larger one and rebasing by the Smith form of `C`:

```python
coefficients = rows.solve_left(adapted)          # tensor.py, _engine_flag_adapted_rows
diagonal, _left, right = coefficients.smith_form()
rebased = right.inverse() * rows
```

Sage's `solve_left` answers in the **fraction field** even for matrices over
`ZZ`.  For `S = I_2` and the row `A = (2, 1)` the returned `C` is a matrix over
`Rational Field`, and the Smith form taken there has its unimodular factor only
over that field:

| row | `smith_form()` of the relation over `QQ` | over `ZZ` |
|---|---|---|
| `(2, 1)` | `D = (1, 0)`, `V = ((1, -1/2), (0, 1))`, `V^-1 = ((1, 1/2), (0, 1))` | `D = (1, 0)`, `V = ((0, 1), (1, -2))`, `V^-1 = ((2, 1), (1, 0))` |
| `(1, 2)` | `D = (1, 0)`, `V = ((1, -2), (0, 1))` (integral) | the same |

`V^-1` over `QQ` is no basis change of the integer row lattice, and
`matrix_from_rows(range(1, 2))` picks the one row of it that happens to be
integral.  The stacked adapted basis is `((2, 1), (0, 1))` of determinant **2**,
so `flag_stabilizer`'s `change * generator * ~change` cannot invert:

```
ZeroDivisionError: Generic endomorphism of Integral lattice of rank 2 and
signature (0, 0) has no inverse …: its determinant 2 is not a unit of Integer Ring
```

Nothing here is chosen from an unordered container: the row is the span's own
coordinate row, one datum.  What the hash seed decides is **which** primitive row
the ambient flag row asks about — `U + U(2) + <-6>`'s row lists the line as
`2 e_0 + e_1` (row `(2, 1)`, determinant `2`) at `PYTHONHASHSEED=2` and as
`e_0 + 2 e_1` (row `(1, 2)`, determinant `-1`) at `PYTHONHASHSEED` 0 and 1.  The
order is chosen upstream, in the enumeration of the family's isotropic vector
classes; it is not this owner's and no pin of it is this owner's repair.

The minimal library call, with no lattice and no port:

```python
plane = ZZ.free_module(Sets.Δ[1])
first, second = (plane.module_generator(label) for label in plane.module_generating_set())
line = plane.subobject_on(Set((2 * first + second,)))
plane.general_linear_group().flag_stabilizer((line,))   # ZeroDivisionError on 34c9be8
```

## 2. The repair, in two statements

* The relation is accepted only when every coefficient is in the ring, and the
  Smith form is taken over the ring, where `V` is unimodular by construction.  A
  fractional coefficient is the step whose span does not contain the smaller
  one's row lattice, and it is refused as unsaturated, which is the answer that
  path already had.
* Each span enters in its integer row Hermite form: the unique matrix in the
  orbit of a span under unimodular row operations, and the form this repository
  already uses as a span key (`_span_key`,
  `categories/isotropic_orbits.py`).  Two listings of one span — the same
  sublattice by other generators, in another order, or with the other signs —
  reach one matrix, so the rows adapted to a flag are a function of the flag's
  spans and not of their listing.  The function then asserts that the rows it
  returns are a basis, so a non-unit determinant is a loud failure at this owner
  instead of a wrong basis downstream.

For the failing row the repaired basis is `(2 e_0 + e_1, e_0)`, determinant
`-1`, and the same span listed as `-2 e_0 - e_1` adapts to the same basis.

## 3. The measurements

| what | seeds | before | after |
|---|---|---|---|
| `tests/lattices/test_an_adapted_basis_of_a_null_flag_is_a_basis.sage` | 1 | 1 failed, 1 passed, 2.02 s (`ZeroDivisionError`, determinant `2`) | 2 passed, 2.14 s |
| the four incidence-gate tests, three files | 1 | 8 passed, 96.60 s | 8 passed, 68.06 s |
| the four incidence-gate tests, three files | 2 | 8 passed, 71.67 s | 8 passed, 63.10 s |
| the four incidence-gate tests, three files | 3 | 8 passed, 103.17 s | — |
| the four incidence-gate tests, three files | 4 | 8 passed, 118.46 s | — |
| the four incidence-gate tests, three files, port at its paused pin `991b88b0` | 1 | 8 passed (no adapted basis is asked for) | 8 passed, 102.76 s |
| the minimal call above | 1, 2 | `ZeroDivisionError`, determinant `2` | adapted basis `(2 e_0 + e_1, e_0)`, determinant `-1` |
| ambient flag row of `U + U(2) + <-6>` | 2 | `ZeroDivisionError`, determinant `2` | builds; 6 adapted bases, determinants `1, -1, 1, -1` |
| ambient flag rows of the five specimens | 0, 1, 2 | `<-6>` fails at seed 2 | every adapted basis has determinant `±1` at every seed |

The five specimens are `U + U(2) + <-2>`, `U + U(2) + <-4>`, `U + U(2) + <-6>`,
`U + U + <-2>` and `U + U + <-4>`.  Their flag-row cardinalities (2, 2, 2, 1, 1)
and every determinant above are computed, not card values; no lattice-database
card holds a row of any of them (lattice-database#7, lattice-database#13).

The four incidence-gate tests of `#585` are **not** red at seeds 1, 2, 3 or 4 on
`34c9be8`: the lattices they gate (`U + U(2) + <-2>`, `6JRS`, `U + U + <-4>`)
happen never to ask about a row whose relation is fractional, so the defect was
reachable on the family member `U + U(2) + <-6>` that the driver runs and not on
the gate's own lattices on this tree.  What is reproducible without a seed at all
is the minimal library call above, which is what the new test is.

The same four flag test files keep their failure set unchanged: 3 failed,
6 passed, 2 errors before and after, and all of those are pre-existing on
`34c9be8` — `test_complete_isotropic_flag_orbits.sage`'s rank-three rows are
refused by the pinned port, and `test_stabilizer_clauses.sage` carries four
lint findings.
