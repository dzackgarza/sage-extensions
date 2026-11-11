# #295 — the setwise stabilizer's generators carry discriminant images

## The red failure on `7858c09d97`, measured

The acceptance path is `B.Aut().stabilizer(P, action="setwise").group_generators()`
followed by `B.discriminant_representation()` on each. On `7858c09d97` it raised
before producing a single generator:

```
B = U + U + I_{0,7}, P = <e_1, e_2>
B.Aut().stabilizer(P, action="setwise")
  ModuleNotFoundError: No module named 'sage_indefinite_port.indefinite.pairing_slices'
    lattice_morphisms.py:3723 in setwise_stabilizer
```

log: `.tmp/qc-evidence/issue295-red-module-not-found.log`.

**The `ValueError` the issue predicts is not what happens on this tree.** That
message ("goes from L to L to L, so it is not an isometry from L to L") is raised by
`LatticeIsometryMor._morphism_from_images` when a `LatticeIsometryMethods` whose
endpoints are not *identical* to the receiving parent's is passed in. Measured here,
the setwise stabilizer already returns its generators as isometries of `L` itself:
`generators not on the lattice object itself: 0` of 92, and `rho` then accepted every
one of them. So that half of the issue's premise was closed earlier, by
`54c43b0` (`discriminant_representation` takes an isometry by matrix or from an equal
copy) together with the port's marking-class routing. What remained was the stale
import, and then a second, different failure below.

## The two repairs

1. **`setwise_stabilizer` and `pointwise_stabilizer` no longer require the absent
   module.** Both built a `vector_witness` from
   `sage_indefinite_port.indefinite.pairing_slices`, which the pinned port does not
   ship (its modules are `marked_lattices`, `isotropic_induction`, `eichler`,
   `pointwise_shell`, `exact_isotropic`, `recursive`, …). The witness is *optional
   retained data* for vector equivalence, not part of the generator computation:
   `_subgroup_vector_equivalence_witness` falls back to the ambient group's own
   vector-equivalence decision, which is the same decision. Both stabilizers now
   construct without it, and their docstrings say why.

2. **The `identity` routing wrapper no longer copies a docstring by inspecting source.**
   With the import gone the `U ⊕ U(2)` and `B` calls returned, but
   `T_En.Aut().stabilizer(P, action="setwise")` died inside the port's plane branch:

   ```
   predicate_subgroups.py:414 one() -> groups.py:1604 one()
     -> lattice_morphisms.py:3158 identity -> mor_foundation.py:405 __get__
     -> functools.update_wrapper -> instancedoc.InstanceDocDescriptor.__get__
     -> sageinspect.sage_getsourcelines -> inspect.getfile
     -> TypeError: <class 'object'> is a built-in class
   ```

   log: `.tmp/qc-evidence/issue295-t-en-identity-metadata.log`. `ObjectLevelOperation`
   wrapped its routed operation with `functools.update_wrapper`, whose `__doc__` copy
   reads Sage's `InstanceDocDescriptor`; on a dynamically generated element class
   (`_generated_arrow_type`, and every `OwnedJoinCategory` parent class built that way)
   that descriptor cannot recover a source file and raises. `mor_foundation.py` now
   copies the operation's name, module and annotations and copies `__doc__` only when
   it is already a string, leaving the descriptor readable through `__wrapped__`.
   Nothing about the operation is skipped — only the introspection that formats help
   text — and no isometry check is relaxed.

## What the call returns now

```
B = U + U + I_{0,7}, P = <e1, e2>
  setwise stabilizer      92 generators in 16.8 s
  on the lattice itself   92 of 92
  rho on every generator  0 failures
  O(q_B)                  |A_B| = 0, |O(q_B)| = 1, so the images generate the trivial
                          group: the order returned for B is 1

U + U(2), P = <e1, e2>
  setwise stabilizer      13 generators in 3.7 s
  rho on every generator  0 failures, 0.9 s for all 13
  #321 plane call with those generators as `stabilizer_generators={0: …}`
                          2 plane orbits  (the count #321's own test asserts)

B(2) = T_Co
  setwise stabilizer      92 generators in 16.9 s
  rho on one generator    blocked: O(q_{B(2)}) does not build (below)
```

## The order in O(q_{B(2)})

`|⟨ρ(Stab_{O(B)}(P))⟩| = 247726080 = 2^18 · 3^3 · 5 · 7`, computed after
transporting the 92 generators to `B(2) = T_Co` (`B.doubled_form()`: `O(B) → O(B(2))`
on the same module, the form doubled) and taking each one's
`discriminant_isometry()`. The order is read from the faithful action on the 2048
classes of `A`: a linear map fixing every class is the identity, so the permutation
group and the image group are isomorphic and have the same order. Cost: 220 s, of
which 195 s is the 92 discriminant isometries. `[O(q_{B(2)}) : image] = 189720`
against `|O(q_{B(2)})| = 46998591897600`.

This number is *not* produced by `O(A_{T_Co})`, because that object cannot be built on
this tree:

```
A = (Z/2)^11, 2048 classes
A.orthogonal_group()
  -> groups.py _finite_order -> _engine_group
  -> torsion_form_modules.py:2839 _engine_orthogonal_group
  -> sage/modules/torsion_quadratic_module.py:875 orthogonal_group
  -> sage/groups/fqf_orthogonal.py:563 _isom_fqf -> :533 orbits      no return at 180 s
```

log: `.tmp/qc-evidence/issue295-O-q-B2-engine-wall.log`. So
`diskriminant_representation()` on `T_Co` — which is `discriminant_morphism` →
`O(A).from_morphism` → the same engine — does not return either, and the order above is
the same group read through the permutation action instead of through `O(q)`. The
engine wall is the module the fast path `_engine_elementary_two_orthogonal_generators`
does not catch: the associated bilinear form of this even form on `(Z/2)^11` is
degenerate, so the rank test that selects that path fails.

## The Enriques lattice

`T_En.Aut().stabilizer(P, action="setwise")` still does not return. With the metadata
failure repaired the call proceeds into the port's rank-two marked-lattice branch
(`isotropic_induction.plane_automorphism_generators` → `_stabilizer_generators` →
`recursive.isotropic_stabilizer_action`) and had not returned after 3000 s in
`.tmp/qc-evidence/issue295-gate-setA.log`'s superseded run — the same wall #316
recorded at 1500 s for `isotropic_stabilizer_generators` on `T_En`. That is the
remaining obstruction to the issue's second acceptance item, and it is the port's
parabolic computation, not this repository's stabilizer plumbing.

## Tests

```
tests/lattices/test_setwise_stabilizer_discriminant_images.sage
  test_every_setwise_stabilizer_generator_has_a_discriminant_image        23.86 s
  test_the_divided_class_plane_call_takes_the_setwise_stabilizer_generators 15.46 s

one run, the module plus four neighbours:
  test_unpolarized_enriques_strata (029J `O` rows), test_enriques_anti_invariant_cusps,
  test_stable_isotropic_plane_orbits, test_enriques_plane_orbits_by_divided_classes
  16 passed in 311.70 s, exit 0
```

Run under the repository addopts with `--no-time-gates --timeout=0`, as the four
`T_En` rows require (102.49 s, 56.00 s, 40.13 s, 27.80 s) and as
`test_every_setwise_stabilizer_generator_has_a_discriminant_image` now does too
(23.86 s: 16.8 s of it is the stabilizer's own generator computation).
