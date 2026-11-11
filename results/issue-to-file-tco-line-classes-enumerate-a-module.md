# Issue to file: the `T_Co` primitive-isotropic line classes enumerate the elements of a module

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body. No open issue names this operation:
`_isotropic_pointed_isometry`, `integral_parameter_classes` and `isotropic_lifts` return
0 hits each on `repo:dzackgarza/sage-extensions is:issue`.

## Title

`isotropic_lifts.integral_parameter_classes` enumerates a module's elements, so the `T_Co` line-orbit call does not return

## Body

`sage-extensions#286` asks one public call for the `Γ`-orbits of primitive isotropic
vectors and planes of `T_Co = <2> + E(2)`, `E = E8 + U`, for `Γ = O(T_Co)`,
`Õ(T_Co)`, `Õ⁺(T_Co)` and the restricted stabilizers `R_Γ` of the Coble divisor. Every
row stops before any orbit is produced, at the same place: the ambient `O(T_Co)` line
classes, in the owned lift locus, which materializes the elements of a module.

Specimen: `Lattices(ZZ)([[2]]) + (NamedLattices.E8 + NamedLattices.U).twist(2)` (rank 11,
signature (2, 9), determinant -2048, even, `A = (Z/2)^11`), and

```python
L.Aut().isotropic_orbit_representatives(1)
```

`faulthandler` at 600 s:

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

`modules/pure/modules.py:3374 elements()` builds the whole finite ordered set through
`from_indexed`, and `fgp_module.list()` below it enumerates the module. The same stack
appears for the subgroup row `Tco.stable_orthogonal_group().intersection(Tco.O_plus())`
(`isotropic_orbit_representatives(1)` -> `orthogonal_quotients.py:2039`
`_subgroup_isotropic_orbit_representatives` -> the same ambient call), so the defect is
not in the subgroup split; it is in the ambient class computation the split starts from.

## Why it is a defect of the call and not a cost to accept

A primitive marking class is one class per orbit, and the lift locus is asked for the
integral members of one orbit at a time (`integral_members` on a locus). Enumerating the
*elements* of the ambient module to answer that question makes the cost the size of the
module, which is not bounded by anything the caller states, and which is what a bounded
locus exists to avoid. `integral_parameter_classes` takes its parameter set from
`elements()`, so the fix belongs at that locus: the parameter classes are the
integer-valued points of a stated lattice condition, not a listing of the module.

## Evidence

| row | call | stack at | log |
| --- | --- | --- | --- |
| `O(T_Co)` | `L.Aut().isotropic_orbit_representatives(1)` | 600 s | `.tmp/p286-probe4.log` |
| `Õ⁺(T_Co)` | `L.stable_orthogonal_group().intersection(L.O_plus()).isotropic_orbit_representatives(1)` | 600 s | `.tmp/p286-probe5.log` |

Environment: the adopted runtime (`sage-image/rootfs`, Sage 11.0.beta5, Python 3.14, port
source bound at `/work`), launched through `peakrss.py` with `PEAKRSS_LIMIT_MIB=6144`;
command `bash .scratch/issue315_launch.sh` with `PROBE=issue286_probe4.py` (resp. `…5.py`).

Reproduce with the probe files, which build the lattice from the cited formula and report
each stage as it is reached.

## Acceptance

`L.Aut().isotropic_orbit_representatives(1)` returns on `T_Co` without enumerating a
module's elements, and `#286`'s rows can then be measured; the value it must agree with
is not in this issue -- it is the `Γ`-row of the lattice-database card for `T_Co`
(lattice-database#7), which takes its values after the comparisons of `#316`, `#317` and
`#319` agree.
