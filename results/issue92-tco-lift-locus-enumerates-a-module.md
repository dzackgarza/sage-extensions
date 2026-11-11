# Report against sage-extensions#92: the `T_Co` lift locus enumerates a module's elements

Not a new issue: the locus this measurement lands in is owned by **open** issues.
Searched `repo:dzackgarza/sage-extensions is:issue`:
`isotropic_lifts` -> 2 hits, **#57** and **#92**, both open;
`integral_parameter_classes` -> 1 hit, **#18**, open.  #92's body states the ownership
explicitly: "`categories/isotropic_lifts.py:IsotropicReductionLiftTorsors`.  The torsor,
its action, section/base-point data and `integral_members()` computation remain research
implementations", with "keep the rational/integral distinction and complete fibre
obligation".  `integral_members` is the frame on the stack below, so this belongs to #92's
acceptance and is reported here for the orchestrator to post as a comment there.  This
project's GitHub connection reads issues and cannot create or comment on them.

## What was measured

`sage-extensions#286` asks one public call for the `Gamma`-orbits of primitive isotropic
vectors and planes of `T_Co = <2> + E(2)`, `E = E8 + U`, for `Gamma = O(T_Co)`,
`Otilde(T_Co)`, `Otilde+(T_Co)` and the restricted stabilizers `R_Gamma`.  Every row stops
before any orbit is produced, at the ambient `O(T_Co)` line classes:

```python
L = Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)
L.Aut().isotropic_orbit_representatives(1)
```

`faulthandler` at 600 s, on the adopted runtime:

```
File "sage_extensions/categories/modules/pure/modules.py", line 3377 in <lambda>
File "sage_extensions/categories/sets/finite_ordered_sets.py", line 397 in from_indexed
File "sage_extensions/categories/modules/pure/modules.py", line 3374 in elements
File "sage_extensions/categories/isotropic_lifts.py", line 385 in integral_parameter_classes
File "sage_extensions/categories/isotropic_lifts.py", line 234 in _integral_lift_locus
File "sage_extensions/categories/isotropic_lifts.py", line 278 in integral_members
File "/work/src/sage_indefinite_port/indefinite/recursive.py", line 1720 in _isotropic_pointed_isometry
File ".../recursive.py", line 1597 in pointed_isometry
File ".../recursive.py", line 1771 in primitive_vector_classes
File ".../isotropic_induction.py", line 109 in _computed_isotropic_vector_classes
File ".../isotropic_induction.py", line 75 in isotropic_vector_classes
File ".../marked_lattices.py", line 195 in primitive_marking_classes
File "sage_extensions/categories/isotropic_orbits.py", line 1348 in _isotropic_orbit_representatives
File "sage_extensions/categories/lattice_morphisms.py", line 4441 in isotropic_orbit_representatives
```

`integral_parameter_classes` takes its parameter set from `modules`' `elements()`, which
runs `from_indexed`, which calls `fgp_module.list()`: the whole finite module is
materialized as an ordered set.  The specimen is rank 11, signature (2, 9), determinant
-2048, `A = (Z/2)^11`.

The same stage is reached from the subgroup row --
`Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)`
enters at `orthogonal_quotients.py:2039 _subgroup_isotropic_orbit_representatives` and
then calls the same ambient operation -- so the stop is in the ambient class computation,
not in the subgroup split #286's call performs.

## Why it is the computation's defect and not a cost to accept

A marking class is one class per orbit; the caller asks the lift locus for the integral
members of one locus at a time.  Answering that by listing the module's elements makes the
cost the size of the module, which the caller never states and which the locus exists to
avoid.  Under #92's own contract ("complete fibre obligation", "rational/integral
distinction") the fibre is a set of integral points of the locus, and it can be described
without an enumeration of the ambient module.

## Evidence

| row | call | stack at | log |
| --- | --- | --- | --- |
| `O(T_Co)` | `L.Aut().isotropic_orbit_representatives(1)` | 600 s | `.tmp/p286-probe4.log` |
| `Otilde+(T_Co)` | `...intersection(L.O_plus()).isotropic_orbit_representatives(1)` | 600 s | `.tmp/p286-probe5.log` |

Environment: adopted runtime (`sage-image/rootfs`, Sage 11.0.beta5, Python 3.14), port
source bound at `/work`, launched under `peakrss.py` with `PEAKRSS_LIMIT_MIB=6144` via
`bash .scratch/issue315_launch.sh` with `PROBE=issue286_probe4.py` (resp. `...5.py`).

## Acceptance, as it stands for #286

`L.Aut().isotropic_orbit_representatives(1)` returns on `T_Co` without enumerating a
module's elements.  `#286`'s rows can then be measured; the value they must agree with is
the `Gamma`-row of the lattice-database card for `T_Co` (lattice-database#7), which takes
its values only after the comparisons of #316, #317 and #319 agree.
