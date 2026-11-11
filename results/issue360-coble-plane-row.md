# #360: the plane row and the Tits-building incidence of `T_Co` for `O(T_Co)`

The lattice is `NamedLattices.Tco` = `⟨2⟩ ⊕ U(2) ⊕ E₈(−2)` = `⟨2⟩ ⊕ (U ⊕ E₈(−1))(2)`,
D. Dolgachev and S. Kondō, *Enriques surfaces and Borel–Weil–Bott type duality*,
Izv. Math. 77:3 (2013), §3 eq. (3.6), printed p. 513 (rank 11, signature (2, 9),
det −2048, `A_{T_Co} = (Z/2)^11` with 2048 classes, `|O(q)| = 46 998 591 897 600`).

The calls are the public ones: `isotropic_orbit_representatives(1)`, `(2)`,
`cusps(1)`, `cusps(2)`, `tits_building_incidence()` on `Tco.Aut()`, and the
divided-class plane call `isotropic_plane_orbits(representatives)` on the
subgroup `ρ̄⁻¹(ρ(O(T_Co)))` of that lattice.

The page proofs the values are compared with are research #645's, read at
`writing/coble/lattices-and-moduli/the-heegner-line-and-the-coble-arithmetic-group.md`
of `e4d8bdcc301aaee775fbda3baff948ccef1a8d43`:

* `thm:coble-plane-stabilizer-image` item 5: for `H = Q`, i.e. `Γ = Orth(B)`,
  "a single double coset over the whole 23715, the one `Orth(B)`-orbit of planes
  of this section" — `O(T_Co)` has **one** orbit of primitive isotropic planes;
* `thm:plane-fibre` item 1: `|Stab_{O(q)}(J)| = 1 981 808 640` and
  `|ρ(Stab_{O(B)}(P))| = 247 726 080`, so the plane fibre has index **8**;
* `thm:plane-fibre` item 2 with `prop:coble-planecusp-finite` item 3: the
  liftable order-four isotropic subgroups number `23715 = 527·270/6`, so
  `Γ_Co = Õ⁺(T_Co)` has `23715·8 = 189 720` plane orbits;
* `thm:plane-half-index` item 4: `Γ_Co` has **527** orbits of primitive
  isotropic vectors, one per nonzero isotropic class;
* `thm:plane-fibre`, *the incidence*: each liftable `J` has three nonzero
  classes, one per `0`-cusp, so **three** line classes lie in every plane class.

## The refusal the plane-orbit call carried, and what replaces it

`isotropic_plane_orbits` counted `Γ`-orbits of planes as `ρ(Γ)`-orbits on the
finite set of divided-class points of each `O(L)`-representative.  That count is
the orbit count exactly when `ρ(G_x) = Stab_Q(J_x)`; otherwise it is too small
(`|Q·J_x| ≤ [Q : ρ(G_x)]`).  #321 made the call refuse where the equality was
not established, and `T_Co` was its motivating victim: it is not isometric to
`N = U ⊕ U(2) ⊕ E₈(−2)`, so the published indices `527`, `23715` did not apply.

Measured at a plane of `T_Co` (the specimen of `tests/lattices/test_the_tco_plane_orbit_and_its_composed_automorphisms.sage`,
`P = ⟨ep + fp − Σaᵢ, 2h − (a₁ + a₂ + 2a₃ + ⋯ + 2a₇)⟩`), one process:

```
plane.is_parabolic_complete()               True      (2.7 s, after the three factors)
  unipotent_radical_index()                 1         6.4 s
  levi_plane_action_index(trivial_on_quotient=True)   1    41.0 s
  levi_quotient_image_index(trivial_on_plane=True)    1     4.9 s
parabolic_stabilizer_generators()           105 generators
stabilizer_discriminant_image_orders()      (1981808640, 247726080)      79.7 s
stabilizer_discriminant_image_index()       8
splitting_complement()                      None (the plane does not split off T_Co)
```

So #331/#366 do establish the setwise stabilizer at a `T_Co` plane, and its
discriminant image has index **8** in the stabilizer of its order-four isotropic
subgroup — the page's own index, computed.  But that is also why the class-set
count cannot be the plane count here: it is short by exactly that factor, at
every class.  The call therefore takes the precise route instead of the
approximate one: at a representative whose parabolic is complete it computes the
double cosets `ρ(Γ) \ ρ(O(L)) / ρ(G_x)` themselves
(`_orbits_from_stabilizer`, through `splitting_isometries`), and it refuses only
where `is_parabolic_complete()` is `False`, naming that plane and the missing
factor.  The published-index route of the Enriques lattice is untouched.

## A prerequisite repair the run needed

`PrimitiveIsotropicSubobjects.plane_block_basis` completed the plane's basis to a
`ZZ`-basis of `P^⊥` and then of `L` by keeping standard basis vectors in order
while they raised the rank.  That is not a completion: at the `T_Co` plane above
it returned `11` rows of determinant `2`, so the block form — and with it the
whole parabolic — refused (`unipotent_radical_index` raised
`AssertionError: ... the ranks came out as 7 and 2 with determinant 2`).
Both completions are now the cokernels': `P` is saturated in `P^⊥` and `P^⊥` in
`L`, a finitely generated torsion-free module over `ZZ` is free
(`finite_free_trivialization`), and lifting that trivialization's basis points
back along the cokernel projection completes the basis.  On `T_En` at Sterk's
`P₁` and `P₂` the same method returns determinant `±1` as before; on `T_Co` it
returns determinant `1`.

## The rows

One process, `PEAKRSS_LIMIT_MIB=6144`, at the tree of this commit (`.tmp/qc-evidence/issue360-coble-plane-row.log`):

```
T_Co rank 11 signature (2, 9) det -2048 classes 2048 |O(q)| 46998591897600
[23:08:27] setup: 15.8 s
[23:08:27] isotropic_orbit_representatives(2) ...
    23:17:33  stop: PariError: sorry, qfsolve, dim >= 10 is not yet implemented
```

`L.Aut().isotropic_orbit_representatives(2)` on `T_Co` **does not return**.  It
stops after 9 min 6 s inside the ambient plane classification:

```
lattice_morphisms.py:4871  isotropic_orbit_representatives
isotropic_orbits.py:1600   _isotropic_orbit_representatives
isotropic_orbits.py:1416   _isotropic_plane_orbit_representatives
isotropic_orbits.py:1393   _planes_through_line        -> INDUCTION.isotropic_vector_classes(quotient)
isotropic_induction.py:84  _computed_isotropic_vector_classes
lattices.py:4687           is_isotropic
lattice_engines.py:496     _isotropic_vector_witness   -> qfsolve(gram over QQ)
PariError: sorry, qfsolve, dim >= 10 is not yet implemented
```

The one `O(T_Co)` line orbit is reached, its reduction `v^⊥/⟨v⟩ ≅ I_{1,8}(2)` is
built, and the port's classification asks that lattice whether it is isotropic —
through PARI's `qfsolve`, which refuses at dimension `>= 10`.  Deciding isotropy
of an indefinite lattice without a witness search is the prerequisite that owner
needs (`#335` is the same classification not returning on `T_En`); it is not
this issue's repair and nothing here papers over it.  `tits_building_incidence()`
stops at the same line, since its first plane cusp comes from this row.

What does return, by the route this issue's change installs
(`.tmp/qc-evidence/issue360-plane-orbit-by-stabilizer.log`):

```
index [O(L) : Gamma] = 1
[23:07:04] T_Co isotropic_plane_orbits: 73.7 s
T_Co PLANE ROW: 1
  representative: Integral lattice of rank 2 and signature (0, 0) | primitive True | rank 2
  divided classes: ['0', '2*[h] + [a3] - [a4] + 2*[a7] - 2*[a8]',
                    '[ep] + [fp] + [a1] + [a2] - [a4] + [a8]',
                    '2*[h] + [ep] + [fp] + [a1] + [a2] + [a3] - 2*[a4] + 2*[a7] - [a8]']
```

— the plane's ambient orbit, split by the plane's own stabilizer: **one** orbit,
which is research #645's `thm:coble-plane-stabilizer-image` item 5 value, with
`[O(T_Co) : Γ] = 1` so the double-coset space is the single point the identity
names.

## The comparison with the page proofs

| row | page value (research #645) | computed |
| --- | --- | --- |
| `O(T_Co)` plane orbits | **1** — `thm:coble-plane-stabilizer-image` item 5, "a single double coset over the whole 23715, the one `Orth(B)`-orbit of planes" | **1**, on the plane's own stabilizer route (73.7 s); the ambient route does not return (the stop above) |
| index per finite class, `[Stab_{O(q)}(J) : ρ(Stab_{O(T_Co)}(P))]` | **8** — `thm:plane-fibre` item 1, `1981808640 / 247726080` | **8**, with both orders computed (`stabilizer_discriminant_image_orders() = (1981808640, 247726080)`) |
| `O(T_Co)` line orbits | **1** — `thm:plane-half-index` item 4 has `Γ_Co` read 527 orbits from `|O(q)| / |ρ(S)|`, so `O(T_Co)` itself is transitive (`thm:unpolarized-cusps`) | 1, recorded in `results/issue286-tco-rows.md`; this turn's run reaches the line orbit before the stop and does not print its count |
| the incidence | each liftable `J` carries three nonzero classes, one per `0`-cusp (`thm:plane-fibre`, *the incidence*), so a plane class contains three line classes | not computed: `tits_building_incidence()` stops at the same line |

Two values agree and none disagrees, so nothing is filed on research this turn.
The rows this issue does **not** run (its acceptance is the `O(T_Co)` row; the
kernel and restricted rows follow once their line rows return): `Õ(T_Co)` and
`Õ⁺(T_Co)` plane orbits, whose page value is `23715·8 = 189720`
(`thm:plane-fibre` item 3) — the change above is what makes that count
reachable, since with `ρ(Γ) = 1` the double cosets are `1·Q/ρ(G_x)` and number
`189720` rather than the `23715` the class-set route returns.
