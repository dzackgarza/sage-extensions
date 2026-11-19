# The two failures of image run 44428467714, and what each was

Run 44428467714 (`main`, `rows O`, `restricted_stabilizer true`, `cap 21600`)
failed in both jobs.  Neither failure was the mathematics; both were the
driver's, and both are repaired here with a red test on a small input.

## 1. The `O` row: a regression on `main`, from the plane class index

```
tests/coble_gamma_co_2_incidence_rows.py:922 in main
AttributeError: 'OwnedLatticeIsometryMor_with_category_with_category' object
has no attribute 'contains_character_kernel'
```

The `O` row is the ambient `O(L)`, the one row of the four with no finite
character quotient; the three others are subgroups cut out by one.  The plane
class index the previous round added is `[Stab_{O(q)}(J) : rho(Stab_Gamma(P))]`,
a quotient of two orders of that image, so it is not defined at the ambient row
-- and the guard asked every row for it, after the row had already decided.

The commit is `fb8da5b` (`fix: the plane class index is returned, and the
drivers record page values`), which is this line's own; the `O` row passed in run
43556671111 because the line did not exist then.  The repair is the driver's
capability read, the idiom its own route decision and transport count already
use:

```
if arguments.plane_class_index and getattr(subgroup, "finite_character_quotient", None) is not None:
```

Red test: `tests/engineering/test_the_ambient_row_runs_through_the_driver.py`
runs the `O` row of `6JRS = U + U + <-2>` through the driver's `main` and asks
for exit status 0.  On the parent it prints the row's decided line (one edge over
one line and one plane cusp) and then raises the reported `AttributeError`:
3.53 s red, 3.65 s green.

## 2. The restricted-stabilizer row: `delta` taken from the wrong lattice

```
lattice_morphisms.py:4300 stabilizer -> :4328 _family_stabilizer
coloured_vector_families.py:862 _realization -> :314 __init__
AttributeError: 'OwnedJoinCategory.element_class[_SparseFreeModuleElement]'
object has no attribute 'domain'
```

The row built `delta = e - f` from `NamedLattices.TEn` and the subgroup from the
coinvariant extension.  The subgroup's supergroup's lattice is the
construction's own -- an equal but distinct copy of `T_En` -- so `delta` was a
vector of a lattice none of the subgroup's isometries is an isometry of, and
`O(L).stabilizer` treated it as a family, which the family realization cannot
realize.

**On `main`, with the checkout on `PYTHONPATH`:** `--lattice TEn` reproduces the
reported error exactly (`.scratch/w286-probes/restricted-ten-main.log`, tree
`4070871`); `--lattice small` passes (`exit 0`, 16.0 s,
`.scratch/w286-probes/restricted-small-main.log`).  So the workflow's
`PYTHONPATH: src` fix at `f9f4e69d8a` was necessary and not sufficient: the
`TEn` row fails on `main` too.

The repair: `delta_and_perpendicular` takes the subgroup, reads its lattice once,
supplies the vector per specimen, and asserts both that the vector is an element
of that lattice and that its square is `-2`.  Red test:
`tests/engineering/test_the_restricted_stabilizer_row_reports_its_status.py` runs
the `TEn` row under a three-second cap and asks for `undecided` (exit 1) --
which is the row's correct answer, its stabilizer needing minutes -- where the
parent raises the reported error while constructing.  2.86 s red, 5.50 s green.

After the repair, one process per row:
`--lattice small --cap 120` returns 0 in 24.4 s with the two descriptions
agreeing (`|rho(R)| = 2` equal to the driver's `|Stab(J)|`, spinor signs 40 of
`+1`, 21 of `-1`); `--lattice TEn --cap 30` returns 1, undecided, with `delta`
accepted in the subgroup's lattice (perp rank 11, isometric to `T_Co`)
(`.scratch/w286-probes/fixed-restricted-five.log`).

## 3. A third failure found while repairing the first, on `main` since 2026-11-17

`tests/engineering/test_the_incidence_row_reports_a_broken_contract_apart_from_an_undecided_row.py`
had two tests failing on `main` before this round, for a reason unconnected to
either row:

```
TypeError: row_contract() missing 1 required positional argument: 'route'
```

`row_contract` took a `route` argument at `8fc0f49` (#381) and the
`incidence_row_contract` binding in `tests/engineering/conftest.py` was not
updated with it.  The binding now forwards the route, defaulting to the
certificate route.  That file: 8 passed in 6.48 s, where it was 2 failed and 8
passed.  No red of my own is claimed for it: the red is those two tests on
`main`.

## 4. The run to dispatch, inputs named

| input | value | why |
| --- | --- | --- |
| `rows` | `O` | re-runs the row whose regression this round repairs; it passed in 43556671111 and failed in 44428467714 |
| `restricted_stabilizer` | `"true"` | re-runs the restricted-stabilizer row with `delta` taken in the subgroup's lattice |
| `lattice` | `Tco` | the row's object |
| `route` | `certificate` | the `O` row has no character quotient and takes the certificate route whatever is asked, which the driver logs |
| `cap` | `21600` | the restricted row's own ceiling (a GitHub-hosted job is capped at six hours); the `O` row needs ~170 s |
| `budget` | `28800` | unchanged |

Files run (adopted runtime, `--no-time-gates`, `PYTHONPATH=src` with the checkout
bound):

```
tests/engineering/test_the_ambient_row_runs_through_the_driver.py          1 passed   3.65 s
tests/engineering/test_the_restricted_stabilizer_row_reports_its_status.py 1 passed   5.50 s
tests/engineering/test_the_incidence_row_..._undecided_row.py              8 passed   6.48 s
tests/lattices/test_the_kernel_incidence_rows.sage                         2 passed  67.93 s
   (its `u_u_m4` row 48.73 s against the 20 s gate, as before)
combined run of the three engineering files: 10 passed in 14.88 s
```
