# #316 — the Γ_{En,2} and Õ⁺ plane rows of T_En, by divided classes

## What the call returns, measured

`<group>.isotropic_plane_orbits(representatives)` returns one
`IsotropicPlaneOrbit` per orbit of primitive isotropic planes of the subgroup,
computed in the finite discriminant image `Q = rho(O(T_En))`,
`|Q| = 46998591897600`. One process, `PEAKRSS_LIMIT_MIB=6144`:

```
P1 = Z e_1 + Z e_3                    Q-orbit of its class point  527     0.0 s
P2 = Z(2e_1+2e_2+w) + Z e_3           Q-orbit of its class point  23715   0.3 s
                                                              total  24242  = 029J `Otilde+` planes
rho(Gamma_En,2)-orbits on the 24242-point union                 9           = 029J `gamma-en-2` planes
   orbit lengths 2, 120, 135, 270, 270, 1575, 3780, 8640, 9450   (sum 24242)
|rho(Gamma_En,2)| = 696729600 = |W(E8)|,  [Q : rho(Gamma_En,2)] = 67456,  |rho(Otilde+)| = 1
```

`527` and `23715` are exactly the stabilizer-image indices Dutour Sikirić–Hulek
print, so the class-point orbit and the coset space `Q / rho(Stab)` have equal
size; `24242` is their sum, and the nine orbits at `Gamma_En,2` are the count
Alexeev–Engel–Garza–Schaffler state for the 1-cusps of `F_{En,2}`.

## The theorem each step cites

| step | statement | citation |
| --- | --- | --- |
| the two `O(T_En)`-orbits and their representatives | `P_1 = Z e_1 + Z e_3`, `P_2 = Z(2e_1+2e_2+w)+Z e_3`, `w^2 = -8` | Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991), Prop. 4.6 (p. 29); lines: Prop. 4.5 (p. 28) |
| the same representatives in the standard `U`, `U(2)` bases | `(e_1,e_2)` for `U`, `(e_3,e_4)` for `U(2)` | Dutour Sikirić–Hulek, *Moduli of polarised Enriques surfaces — computational aspects*, JLMS 110 (2024), arXiv:2302.01679, §3.6, p. 22 |
| double cosets reduce to the finite quotient | `U = Õ(L) ⊂ K = Γ`: `K \ G / H` ↪ `K/U \ G/U / H̄` bijectively | Dutour Sikirić–Hulek, Lemma 3.6, printed p. 22 |
| the plane indices `527`, `23715` and the `24242` 1-cusps | the images of `Stab(P_1)`, `Stab(P_2)` have index `527`, `23715`; `M̃_En` has 528 0-cusps and 24242 1-cusps | Dutour Sikirić–Hulek, §3.6, p. 22 |
| `Γ_{En,2}` | the image in `O(T_En)` of `{g ∈ O(L) : g I_En = I_En g, g(h)=h}`; `Γ_{En,2} = Γ_En ∩ Γ_dP` | Alexeev–Engel–Garza–Schaffler, *Compact moduli of Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025), Def. 2.6 |
| the quotient whose boundary is counted | `F_{En,2} = D(T_En)/Γ_{En,2}` | same, Def. 2.7 |
| `Γ_{En,2}`'s boundary | the five folded diagrams are the Coxeter diagrams of `W(Γ_{En,2,e})` over the isotropic `e mod Γ_{En,2}`, and `F_{En,2}` has exactly five 0-cusps | same, Cor. 3.12 |
| the 9 one-dimensional cusps | "There are five 0-cusps … There are also 9 distinct 1-cusps" | same, §3.3, p. 590 |

Page numbers for the JLMS printing are the card's own citation row; the AEGS
statements above were read in the arXiv text (2312.03638), which is where the
wording of Def. 2.6, Def. 2.7 and Cor. 3.12 was checked. The AEGS volume is
printed as **259** by the issue and as **249** by `029J`'s `gamma-en-2`
citation; that discrepancy is not resolved here.

## The defect the body names, checked against the code

Both claims hold, with one correction:

* the plane call does route through the integral stabilizer: on `T_En`
  `_subgroup_isotropic_orbit_representatives` computes
  `line_image` only for `rank == 1`, so for rank 2 it goes through
  `orthogonal_group.isotropic_stabilizer_generators(plane)`;
* **correction**: for a plane that call reaches the port's
  `plane_automorphism_generators`, not `line_automorphism_generators` /
  `_stabilizer_generators` — those are the rank-1 branch
  (`src/sage_extensions/categories/isotropic_orbits.py:_isotropic_stabilizer_generators`
  → `automorphism_group_generators(Ar(Lattices), ...)` → rank 1 or 2);
* the class-set orbit route of `d3a8abf783` exists only for rank 1
  (`if not flag and rank == 1` in `_subgroup_isotropic_orbit_representatives`),
  confirmed.

The two-hyperbolic-plane re-read: `T_En = U ⊥ U(2) ⊥ E8(-2)` has one hyperbolic
plane with pairing `±1`, so `_two_hyperbolic_planes` is false there and the
Eichler route of #315 cannot be reinstated on this specimen. The route taken here
does not need it: the class point is the divided discriminant class set, and the
identification of its `Q`-orbit with `Q/rho(Stab)` is certified by the published
indices rather than by a transitivity theorem.

## Prerequisite repair

`vector_stabilizer_generators` evaluated `category.apex_stabilizer(marked)`
eagerly and passed it to `_marking_stabilizer_generators`, which **ignores** it
for indefinite lattices. `apex_stabilizer` → `pointwise_stabilizer`, whose first
statement imports `sage_indefinite_port.indefinite.pairing_slices`, a module the
pinned port does not have. `Γ_{En,2}` therefore failed to build in most fresh
processes. The apex stabilizer is now read only when `lattice.is_definite()`,
where it is used; the indefinite branch passes `None`. Definite behaviour is
unchanged. Two further imports of the same absent module
(`lattice_morphisms.py:3723`, `:4018`) are left in place and recorded in
`TRAPS.md`: they belong to other entry points.

## Tests, and their cost

```
tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage   4 passed in 471.33 s   exit 0
  (addopts blanked; log .tmp/qc-evidence/issue316-plain-pytest.log)

same module + test_unpolarized_enriques_strata.sage +
test_enriques_anti_invariant_cusps.sage +
test_line_stabilizer_image_requires_eichlers_hypothesis.sage
  repository addopts with --no-time-gates --timeout=0:
  10 passed in 468.06 s, exit 0      (log .../issue316-gate-setA.log)
  row calls: Gamma_En,2 224.95 s, Otilde+ 100.31 s;
  neighbours: 64.19 s, 39.75 s, 20.36 s, 2.84 s, 0.79 s, 0.02 s, 10.12 s, 3.39 s

the same set under the untouched addopts: the Gamma_En,2 row is killed by
pytest-timeout at 60 s and the 20 s call gate names it, so the session ends
without a verdict      (log .../issue316-gate-default-addopts.log)
```

`just test-lint` on the new module: **1 file, 0 findings**.

The two row calls are over the 20 s call gate; the `029J` `O` row in the same run
is at 64.19 s and 39.75 s on the same intrinsic cost (the ambient generating
family of `O(T_En)`, 199 generators, is what `_im_rho_engine_and_section`
builds). So the module is reported under the repository's own documented
`--no-time-gates --timeout=0` flag set, and the cost is a finding, not hidden.

## Not verified here

* The JLMS printed pages were not read directly; §3.6, Lemma 3.6 and p. 22 are
  cited as the card records them, against arXiv text that was read.
* The `otilde-plus-t-en` row was compared through `029J`'s
  `integral.primitive_orbits.Otilde+` block: the separate arithmetic-group card
  with that tag was not fetched (the `arithmetic-groups` index is what `029J`
  lists the tag from).
* Nothing on `T_Co` and nothing in #315's line-stabilizer branch is run or
  touched.
