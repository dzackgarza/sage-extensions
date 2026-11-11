# #340 and #285 — what is measured here, and the step each one is missing

Both units stop at a measurement, not at an opinion: #340's abort is not reproducible in
the runtime this session can run, and #285's acceptance asks for a chamber the tree
cannot produce.  The pasted output below is from the adopted image
`ghcr.io/dzackgarza/sage@sha256:59568577510bd76fc9c405c81e6cb185656a193a24ee08b33e1b8b7fa6ae9d2b`
(Sage 11.0.beta5) on main at the time of writing.

## #340 — `genus_class_number()` on `A2 + <18>`: the inputs are printed, and the call answers

The path in the traceback is `genus_class_number` → `representatives` → `class_number` →
`_genus_classes` → the mass certificate

```python
found_mass = sum(SageQQ.one() / found.number_of_automorphisms() for found in found_forms)
```

The forms that reach `number_of_automorphisms` for
`[[2, 1, 0], [1, 2, 0], [0, 0, 18]]` — printed by walking the same enumeration, with
`scale = 1` because the genus is even:

```
mass: 1/12
neighbor_iteration at 2, uncapped: 2 forms
  [0] Hessian [2, 0, 0, 0, 6, -3, 0, -3, 6] det 54
      |Aut| = 24 in 0.00 s
      owned orthogonal_group order = 24 in 0.19 s
  [1] Hessian [2, 1, 0, 1, 2, 0, 0, 0, 18] det 54
      |Aut| = 24 in 0.00 s
      owned orthogonal_group order = 24 in 0.04 s
```

Both are even, positive definite, integral, ternary of determinant 54, and PARI's
`qfauto` answers each in 0.00 s; the owner's own `orthogonal_group().order()` agrees
(24 = 24), so the number the mass certificate uses is right on both routes here.  There
is no form in this enumeration that could need gigabytes of PARI stack.

The owner-contract module passes in this runtime, all twelve tests:

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates tests/lattices/test_lattice_database_owner_contracts.sage
12 passed in 52.06s
```

**Why the image was not used.** `ghcr.io/dzackgarza/sage:develop` currently resolves to
`sha256:5304338e93819c8f568b7f1f07e1b41afb383f0d18bf22221b8b45de483ad017` (linux/amd64),
whose layers total **15.2 GB compressed** over 22 layers — the largest single layer is
11.5 GB.  This host has 26 GB free and no OCI runtime (no `docker`, `podman`, `skopeo`,
`oras` or `crane` on PATH), so that image cannot be pulled, unpacked and run here.  The
runtime in use is the older pinned digest, which is why the same call answers.

**Missing step.**  Run
`tests/lattices/test_lattice_database_owner_contracts.sage` inside
`ghcr.io/dzackgarza/sage:develop` on a host that can hold the image, printing
`found.Hessian_matrix()` immediately before each `number_of_automorphisms()` call.  If
those matrices are the two above, the fault is in that build's `qfauto`/`allocatemem`
path and belongs upstream in Sage, not in this owner; if they are different, the print
names the form to fix here.  Nothing in this repository can be changed on the evidence
available: the inputs are correct, small, and answered.

## #285 — the cusp-anchored chamber: the tree's inventory, and the step that is missing

Measured at Sterk's cusps of `T_En = U + U(2) + E8(-2)`:

```
cusps: ['Sterk_1', 'Sterk_2', 'Sterk_3', 'Sterk_4', 'Sterk_5']
Sterk_2 vector coordinates: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
reduction lattice: rank 10, signature (1, 9),
  gram [[-4, 2, 0, ...], ..., [0,0,0,0,0,0,0,0,1,0]]      # E8(-2) + U, in 1.0 s
recorded Sterk root counts: Sterk_1 12, Sterk_2 10, Sterk_3 12, Sterk_4 11, Sterk_5 14
vinberg_simple_roots(controlling_vector=cusp) raised AttributeError:
  'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'
  object has no attribute 'vinberg_simple_roots'
```

So three things are already true and were checked, not assumed:

* the cusp vectors exist and are the recorded ones (`Sterk.selected_isotropic_vectors()`;
  Sterk's cusp 2 is the lattice's own `ep` basis vector);
* `v^\perp/v` at that cusp is the recorded reduction lattice `E8(-2) + U`, rank 10,
  signature (1,9), from `primitive_isotropic_subobject(v).isotropic_reduction()`;
* the recorded chamber data exists in `sterk.py` (`sterk_roots()`, `diagrams()`,
  `diagram_layouts()`) with 12, 10, 12, 11, 14 roots.

And two things are not:

* `vinberg_simple_roots` is not reachable from a plain lattice: the Vinberg operations are
  `HyperbolicLattices` member methods, so the public operation has to be built on that
  category, not on `Lattices`;
* `_vinberg_search(controlling_vector, max_roots, max_decompositions)` enumerates the
  whole `W(L)`.  It has no way to restrict the group.  The issue's own second comment
  records why that is the whole problem: Sterk 1991 §4.3.1, p. 17 takes the chamber of
  `G_v`, the **image of the integral stabilizer** `\Gamma_v` in `O(v^\perp/\mathbb{Z}v)`,
  and the recorded diagrams have 10, 12, 11, 14 walls while the full-group chamber of
  `U + E8(-2)` has ten.  Only one of the five recorded diagrams is the full group's
  chamber; at 12, 11 and 14 walls the chamber is that of a proper reflection subgroup.

**Missing step.**  Vinberg's algorithm for the reflection subgroup generated by the
reflections of `\Gamma_v`, i.e. (i) the induced image
`\Gamma_v \to O(v^\perp/\mathbb{Z}v)` for a `\Gamma` given by generators, and (ii) a root
filter in `_vinberg_search` admitting only the roots whose reflections lie in that image.
Without (ii) the operation can return the full-group chamber, which reproduces one of the
five recorded diagrams and would silently disagree with the other four — which is why no
partial operation is landed here under the issue's name.

## What this commit is

Evidence only: no source change, because neither issue has a defect or an operation here
that the measurements justify.  #340's call answers correctly in this runtime and the
image that aborts cannot be run; #285's operation needs the subgroup-restricted Vinberg
step named above, and shipping the full-group chamber under the issue's acceptance would
be a false claim about Sterk's cusps 3, 4 and 5.
