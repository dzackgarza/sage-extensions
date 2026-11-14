# #302: `O(q).group_generators()` on the four-element form of `U ⊕ U(2)`

## The measurement

`L = U ⊕ U(2)`, `q` its discriminant form on four elements, `|O(q)| = 2`.  Measured on the
parent of the fix and on `main`, same probe (`.scratch/issue302_breakdown2.py`), same order of
calls:

| step | at `14a506a616` (the reported commit) | at `c52ed41e` (this tree) |
| --- | --- | --- |
| `lattice.discriminant_group()` | 0.42 s | 0.34 s |
| `form.orthogonal_group()` | 0.01 s | 0.01 s |
| **`group.cardinality()`** — the first call that builds the engine group | **50.66 s** | **0.58 s** |
| `group.group_generators()` | 0.08 s (engine already built) | 0.05 s |
| Julia imported | **yes** (a `julia` process, 2515 MiB peak) | no |

## The step that took the time

`TorsionFormOrthogonalGroup._engine_group` → `_engine_orthogonal_group`
(`modules/framed/formed/torsion_form_modules.py`).  The first call that needs the group's
order or its generators builds it, so the issue's 32.7 s landed on `group_generators()` and
the 50.66 s above on `cardinality()`: same construction, different first caller.  At
`14a506a616` the two-primary branch of that function read

```python
part_order, matrices = _oscar_lattices.finite_form_isometry_group(
    gram, part.invariants(), part._modulus, part._modulus_qf
)
```

— OSCAR's normal-form isometry-group algorithm, i.e. a Julia process start plus a Julia
computation, to produce a group of order two.  That is the whole 32.7 s / 50.66 s.

## The repair, at that owner

`4df29b8` and `6ae0242` replaced the branch: an elementary two-primary part is now read from
**GAP Forms**' full classical orthogonal group, with the half-integral direction split off
first (`_engine_two_primary_odd_orthogonal_generators`).  So the engine group of this form is
now the group the library computes for the form itself, from the classical group of the
quadratic space over `GF(2)`, and no Julia process is started.

The generators follow from the same place, which is what the issue asks for:

```python
@cached_method
def _computed_group_generators(self):
    return finite_ordered_set(
        tuple(self._from_engine(generator) for generator in self._engine_group().gens())
    )
```

— the family is the generators of that already-computed group, raised to form automorphisms.
No cache stands in front of a slow step; the one cache here (`@cached_method`) sits on the
cheap raising of a fast group's own generators.

This unit therefore adds no library change: the repair is at the owner and already landed.
What it adds is the guard that the repair's property holds, and the measurement above showing
where the time was and that it is gone.

## The test

`tests/lattices/test_the_form_orthogonal_group_generators_generate_it.sage`: build the form,
take `group.group_generators()`, form `group.subgroup(family)`, and compare
`generated.cardinality()` with `group.cardinality()`.  Both numbers are computed by the
objects themselves — no count is typed, and an empty or non-generating family reads as a
smaller order and fails.

```
tests/lattices/test_the_form_orthogonal_group_generators_generate_it.sage
1 passed in 3.17s
just test-lint on that file: 1 files, 0 findings
```

## What is not claimed

The family has two elements for a group of order two on this tree (one on the old tree): GAP's
`GeneratorsOfGroup` may return a redundant generator, and this unit neither asserts the
family's size nor trims it.  Nor is any timing asserted in the test — the numbers above are
the evidence, not the guard.
