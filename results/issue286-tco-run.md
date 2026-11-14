# #286, the `T_Co` run: what returned, what did not, and where it stops

Unit of sage-extensions#286 after #315 (`92e5a4cfb9`, the refusal outside GHS Lemma 7.8).
The call is the existing one: `PredicateSubgroups.isotropic_orbit_representatives(1|2)`,
`cusps`, `tits_building_incidence`, over `_subgroup_isotropic_orbit_representatives`.
**It does not return on `T_Co` for any row yet.** Each row's stage and stack is below.
No guard, cap or profile was added; nothing here is an acceptance value.

## The lattice, from the cited formula

`T_Co = <2> + E(2)`, `E = E8 + U`, `E8` negative definite: Dolgachev--Kondo, Izv. Math.
77:3 (2013), section 3, eq. (3.6), printed p. 513, as `def:gamma-co-groups` of
dzackgarza/research `38fa09935a` states it (`N = <2> + E(2)` with `E(2) = U(2) + E8(2)`).
Built as `Lattices(ZZ)([[2]]) + (NamedLattices.E8 + NamedLattices.U).twist(2)`;
`NamedLattices.Tco` now carries the citation and the sign argument in its docstring.

Computed from that construction:

| quantity | value |
| --- | --- |
| rank, signature | 11, (2, 9) |
| determinant | -2048 |
| even, 2-elementary | True, True |
| `A_{T_Co}` | `(Z/2)^11`, 2048 classes |
| isotropic classes | **528**, of which **527** nonzero |
| `q(h)`, `div(h)` | 2, 2 |
| `[h/2] = divided_discriminant_class(h)` | `q([h/2]) = 1/2`, `b(h/2,h/2) = 1/2` |
| `A_{U(2)} = <[ep/2], [fp/2]>` | order 4, `q = 0, 0, 1, 1`, `b([ep/2],[fp/2]) = 1/2` |

The 528/527 pair agrees with the record `coble_528_isotropic_classes.py` in the issue's
table. `tests/lattices/test_the_coble_lattice_from_the_cited_formula.sage` records these
values; it asserts no orbit count.

## The four rows

`R_Γ` is the image of `Stab_Γ(δ)` in `O(δ^⊥) = O(T_Co)`, `δ` the `(-2)`-vector of
`T_En` with `δ^⊥ ≅ T_Co`. The page's character data (`prop:gamma-co-images`) is the
input the call takes, and it is what each row was instantiated with:

| row | group as the call takes it | state |
| --- | --- | --- |
| `Γ = Γ^K_En = O(T_En)` | `R_{Γ^K_En}`; page (2) says it is `O(T_Co)` | **call does not return** |
| `Γ = Γ_En = Õ⁺(T_En)` | `R_{Γ_En}`; page (1) says it is `Õ⁺(T_Co) = O⁺ ∩ ker ρ̄`, built as `Tco.stable_orthogonal_group().intersection(Tco.O_plus())`, character data complete | **call does not return** |
| `Γ = Γ_{En,2}` | `R_{Γ_{En,2}} = ρ̄^{-1}(P)`, `P` the stabilizer in `O(A_{T_Co})` of the decomposition `[h/2]^⊥ = A_{U(2)} ⊥ A_{E8(2)}` | **`P` cannot be built**: `O(A_{T_Co})`'s own order is unreachable (row 3) |
| `Õ(T_Co)` (kernel row, not a `R_Γ`) | `Tco.stable_orthogonal_group()`, character data complete | **call does not return** (same stage as the two above) |

## Row 1 and row 2: the stage

Both enter the ambient `O(T_Co)` line classes and stop inside the port's
`primitive_marking_classes`, in the owned lift locus, which enumerates the elements of a
module. `faulthandler` at 600 s (row 1) and 600 s (row 2), identical tail:

```
File "sage_extensions/categories/isotropic_lifts.py", line 385 in integral_parameter_classes
File "sage_extensions/categories/isotropic_lifts.py", line 234 in _integral_lift_locus
File "sage_extensions/categories/isotropic_lifts.py", line 278 in integral_members
File "/work/src/sage_indefinite_port/indefinite/recursive.py", line 1720 in _isotropic_pointed_isometry
File ".../recursive.py", line 1597 in pointed_isometry
File ".../recursive.py", line 1771 in primitive_vector_classes
File ".../isotropic_induction.py", line 109 in _computed_isotropic_vector_classes
File ".../marked_lattices.py", line 195 in primitive_marking_classes
File "sage_extensions/categories/isotropic_orbits.py", line 1348 in _isotropic_orbit_representatives
File "sage_extensions/categories/lattice_morphisms.py", line 4441 in isotropic_orbit_representatives
```

with `isotropic_lifts.py:385` calling `modules/pure/modules.py:3374 elements()`, which
runs `finite_ordered_sets.from_indexed` and `fgp_module.list`. The locus is owned by the
open issues #92 (whose body names `integral_members()` as its own computation) and #57, so
no new issue is filed: the measurement is written up as a comment for #92 in
`results/issue92-tco-lift-locus-enumerates-a-module.md`.
Logs `.tmp/p286-probe4.log` (row 1), `.tmp/p286-probe5.log` (row 2).

## Row 3: the stage

`O(A_{T_Co}).cardinality()` does not return in 25 minutes; the stack is the engine
route `groups._finite_order` -> `torsion_form_modules._engine_orthogonal_group` ->
Sage's `TorsionQuadraticModule.orthogonal_group` -> `fqf_orthogonal._isom_fqf`, the
brute-force isometry enumeration `TRAPS.md` records at line 463. At `|A| = 2048` that
route is off its measured curve (the table there stops at `n = 6`). Since `P` is a
stabilizer inside `O(A_{T_Co})`, and `ρ̄^{-1}(P)` needs `P`, the `Γ_{En,2}` row stops
before the call is reached. Log `.tmp/p286-probe3.log`.

The order itself is not unknown: research records `|O(q)| = 46998591897600` from
`orbit(J) · |Stab(J)|` (issue #296's record), i.e. by a route that never builds the
group's own cardinality.

## What the page's proof step needs, and a library defect on the way

`prop:gamma-co-images(2)`'s proof uses "[h/2] is the characteristic class of
`q_{T_Co}`". Checked by hand on the computed form it holds:
`q(w) - b(w,w) = 0`, `q(u1+u2) - b(u1+u2, w) = 1`, `q(x) - b(x,w) = -k` on
`A_{E8(2)}`, and `1/2 + Z` cancels on the `w + z` classes. The library cannot check it:
`DiscriminantClass.is_characteristic` compares `q(x).lift() - b(x,v).lift()` against
`ZZ`, and on `A_{T_Co}` those lifts are owned value elements for which `in ZZ` is
`False` even when the value is `0`, so the method answers `False` for all 2048 classes.
Filed as `results/issue-to-file-discriminant-characteristic-undecided.md`.
Log `.tmp/p286-probe6.log`.

## Re-measured after #319 landed

The first readings were taken at `5fc4e01`. The other chat's `9fdcabe` (the Enriques
plane rows from the divided classes of Sterk's representatives) changed
`isotropic_orbits.py` and `predicate_subgroups.py`, both on this call's path, so the two
line rows were re-measured on `9fdcabe` (with that chat's further uncommitted edits in
`isotropic_orbits.py` and `predicate_subgroups.py` present, since the tree is shared):

| row | result on `9fdcabe` | log |
| --- | --- | --- |
| `O(T_Co)` line orbits | no return at 700 s, same stack ending `isotropic_lifts.py:385 -> modules.py:3374 elements() -> fgp_module.list` | `.tmp/p286-probe4-post319.log` |
| `Õ⁺(T_Co)` line orbits | no return at 700 s, same stack, entered at `orthogonal_quotients.py:2039` | `.tmp/p286-probe5-post319.log` |

The isotropic class count reproduced there unchanged: **528** isotropic, **527** nonzero,
57.7 s.

## Files

- `tests/lattices/test_the_coble_lattice_from_the_cited_formula.sage` -- construction,
  invariants, 528/527.
- `results/issue92-tco-lift-locus-enumerates-a-module.md` -- the call's blocker, as a
  report against #92.
- `results/issue-to-file-discriminant-characteristic-undecided.md` -- `is_characteristic`.
- `TRAPS.md`, the `T_Co` entry -- the two stages and their stacks.
