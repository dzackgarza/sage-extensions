# #299: the chamber's vertex computation ran in two rings, and the stabilizer of its rays

## The result

`is_cocompact` and `_chamber_vertex_squares` return on `U + E8(-2)` and on
`U(2) + E8(-2)`, built from their Gram matrices through
`HyperbolicLattices(ZZ)(Lattices(ZZ)(rows))`, at `max_roots=20, max_decompositions=2000`.
`vinberg_simple_roots` returned the ten walls of each before the repair and still does.

## The cause, measured

Both calls failed at the same line, `hyperbolic_lattices.py:703`:

```python
wall_normals = [engine_vector(_framing_coordinates(root)) * gram for root in roots]
```

```
File "sage/modules/free_module_element.pyx", line 594, in sage.modules.free_module_element.vector
File "sage/modules/free_module_element.pyx", line 695, in sage.modules.free_module_element.prepare
TypeError: unable to find a common ring for all elements
```

`_framing_coordinates` is the one place where a lattice element's framing coordinates
become data for a computation that runs in the private engine ring.  Its docstring said
"at a private engine boundary", but it returned the coordinates it read from the element's
`to_vector()`, which are **owned-ring** elements.  Everything downstream of it in
`_chamber_vertex_squares` is engine data — the Gram comes from
`_engine_component_matrix`, the wall normals are multiplied by it, and the walls become a
`Cone` whose rays are Sage vectors — so the vector constructor was asked for a common ring
over owned coefficients and could not find one.  The three callers differed only in whether
they happened to coerce:

| caller | what it does with the coefficients | before |
| --- | --- | --- |
| `_vinberg_search`, line 550 | hands them to the `vinal` port as a coordinate vector | worked, because the port reads them as integers |
| `_chamber_vertex_squares`, line 703 | builds an engine vector and multiplies by the engine Gram | `TypeError` |
| `isotropic_elements_below_height`, line 911 | owned divisibility and an owned quotient | worked, because it stayed in the owned ring |

So the mismatch was not in the chamber method's arithmetic; it was in the boundary helper,
which crossed into the engine ring and did not lower.  A coercion at line 703 would have
left the third caller and every future caller to discover the same thing separately.

## The owner repaired

`_framing_coordinates` now returns the coefficients **lowered** through
`_engine_element(ring, coordinate)` — the lowering companion of `_owned_engine_element`,
which the same file already uses at lines 205, 320 and 330 — so every caller receives
engine data from the boundary that is documented to produce it.  The two supporting edits:

- `isotropic_elements_below_height`, the one caller that needed owned coefficients, now
  does its divisibility test and its reconstruction in the engine ring (`engine_square`
  lowered once, `engine_square.divides(coordinate)`, `int(coordinate // engine_square)`)
  and reads the candidate back as integers, which is how `_vinberg_search` already reads a
  root row.  Its mathematics is unchanged: the same integrality condition, on the same
  coordinates.
- `_chamber_vertex_squares` states the one ring it computes in: Gram, wall normals and
  polyhedral cone are engine data, and each vertex ray is raised back into the owned ring
  only for the final contraction.  Its docstring also now says what the measurement shows
  about the sign of a square — nonzero inside the light cone, negative or positive
  according as the form presents `(n,1)` or `(1,n)` — which is why `is_cocompact` reads
  only whether a square is zero.

Nothing at the call sites coerces, and no owned element is substituted for an engine one:
the crossing happens once, at the boundary, in the direction the module's contract names.

## The recorded values

Measured at the tree this file ships with (`.scratch/issue299_squares.py`,
`.tmp/299-squares.log`).  These are **recorded, not asserted**: no card row holds them
(below), so the test asserts only what has an oracle.

| lattice | card | walls | vertex squares | zeros | `is_cocompact` |
| --- | --- | --- | --- | --- | --- |
| `U + E8(-2)` | `0124` | 10 | `(0, 4, 12, 10, 8, 6, 4, 2, 0, 2)` | **2** | `False` |
| `U(2) + E8(-2)` | `0125` | 10 | `(0, 36, 84, 60, 40, 24, 12, 20, 8, 4)` | **1** | `False` |

Both numbers agree with the issue's statement (two ideal vertices for the `(10,8,0)` type,
one for the `(10,10,0)` type), and the reflective certificate is `True` at these bounds, so
the wall set is the whole chamber and the ray set is the whole vertex set.

## The cards

Both lattices have cards in `dzackgarza/lattice-database` at the digest's pin
`e8a7f880dd21931d54da1e99217e924db9c88e33`, and the digest's own `gram-index.json` maps
the exact Gram matrices this library builds to them:

- `lattices/0124.md` — `U + E8(-2)`, `aliases: (r, a, delta) = (10, 8, 0)`, determinant
  `-256`, genus symbol `II_{1,9} (2: 1^2:2^8)`;
- `lattices/0125.md` — `U(2) + E8(-2)`, genus symbol `II_{1,9} (2: 2^10)`, determinant
  `-1024`.

Neither card has a cusp-chamber block: **no row of either card holds an ideal-vertex
count**, and neither holds a wall count for the chamber this issue measures.  What they do
hold is `root_span.roots` — the ten simple roots of the 2-elementary root span, which are
*not* the Vinberg walls (recorded above: the Vinberg roots include `(-1, 1, 0, ..., 0)` of
square `-2` and `(0, -2, -2, -3, -4, -6, -5, -4, -3, -2)` of square `-4`).  The row that
would certify this issue's numbers is

    integral.cusp_chambers.<subgroup>.ideal_vertices

— the block `029J` carries as `integral.cusp_chambers.{subgroup}.{cusp, statement,
wall_count, printed_page, figure}`, where it counts *walls* at a cusp and cites a printed
page rather than counting ideal vertices.  That is the missing card row, on both `0124` and
`0125`; the digest is not extended for it here, because a refresh would add two cards whose
rows the test does not read.

## Runs, on the tree this file ships with

Red, at the parent of the repair commit, with the file as it ships:

```
tests/lattices/test_the_chamber_vertex_squares_and_cocompactness.sage
1 failed, 1 passed in 16.88s
```

The failure is `is_cocompact`, at `hyperbolic_lattices.py:703`, the `TypeError` above.  The
half that passes is itself a measurement: the chamber's rays are reachable through the
public owner (`fundamental_chamber(...).primitive_rays()`) at that parent, so the wall set,
the chamber and its rays were all intact and the broken step was only the dual-cone
computation `is_cocompact` reads.  The second test therefore compares the two routes rather
than re-reading the same engine rays.

Green, after the repair:

```
tests/lattices/test_the_chamber_vertex_squares_and_cocompactness.sage
tests/lattices/test_hyperbolic_root_lengths_and_vinberg.sage
tests/lattices/test_the_subgroup_cusp_chamber.sage
9 passed, 288 warnings in 67.09s (0:01:07)
```

Two neighbours were also run and are **not** green, identically at this tree and at its
parent `a36d86a`, so neither is this repair's:

- `tests/lattices/test_edgewalk_source_options.sage` — 4 failed in 8.94 s at `a36d86a` and
  4 failed here: `edgewalk_fundamental_domain() got an unexpected keyword argument
  'option_norms'`, `cannot import name 'edgewalk_isometry'`.  Those are the paused port's
  API, and they fail identically when this session's launcher leaves `/work/src` off
  `PYTHONPATH`.
- `tests/lattices/test_isotropic_height_enumeration.sage` — 1 failed in 5.42 s at
  `a36d86a` and 1 failed here: the test calls `isotropic_elements_below_height` on
  `Lattices(ZZ)("U") + Lattices(ZZ)("A1")` without wrapping it in `HyperbolicLattices`, so
  the lattice has no such method.  The method is exercised through the wrapped call in
  `test_hyperbolic_root_lengths_and_vinberg.sage` (`plane.n(...)`), which is green here,
  so the caller this repair edited is covered.

## What is not claimed

No ideal-vertex count is asserted: the two numbers above are recorded from the operation
and no card row certifies them.  Stage 2 of the issue — the Coxeter diagram at every
0-cusp, under #281 after #285 — is untouched.
