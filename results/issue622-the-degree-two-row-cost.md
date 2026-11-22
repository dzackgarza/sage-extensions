# The degree-two row of card 0128: which leg costs the time, and why

`#Γ̄_h` at `2d = 2` on card `0128` (`U + E8(-1)`, `O(U + E8(-1))`) gave no value
inside the 1800 s per-row cap (#622).  This note splits the row's construction
from its computation, names the leg and the stage that cost the row, and records
the repair with its owner.

## What the row is

The row is `tests/enriques_polarization_rows_by_card.py`'s
`0128:#Gamma_h:2`.  It takes the `O(U + E8(-1))`-classes of primitive vectors of
square `2d` (D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques
surfaces -- computational aspects*, arXiv:2302.01679v2, Table 4), builds the
arithmetic group `Γ_h` of each class by the coinvariant construction, and counts
the distinct triples of its orbits of primitive isotropic lines, planes and
flags.  At `2d = 2` the card states `#h = 1` and `#Γ̄_h = 1`.

## The split

The pinned image (Sage 11.0.beta5), the port the image carries at `54d12c2`
(descendant of the owner's pin `991b88b0`), tree `be381be`, a probe that times
one stage per line and caps each of them separately:

| stage | seconds |
| --- | --- |
| construction: `Enriques()` (the card's lattice, `M = 2W`, its transport, the coinvariant lattice) | 1.06 |
| construction: `W.Aut()` | 0.00 |
| computation: `#h` row, `O(W).vector_orbit_representatives(2)`, 1 class | 2.58 |
| construction: the class → `M` → the invariant lattice → `polarized(...)` | 0.00 |
| construction: `primitive_extension()`, `invariant_polarization()`, `invariant.O()`, its `stabilizer(h)` | 0.00 |
| computation: the stabilizer's generating family (5 elements, the port's marked-lattice route) | 0.13 |
| computation: its order, 1393459200 | 11.21 |
| computation: its image under `ρ`, 0.62 s; `coinvariant_extension_subgroup(stabilizer)` | 1.57 |
| computation: `Γ_h.isotropic_orbit_representatives(1)` — the **line** leg, 5 orbits | 34.31 |
| computation: `isotropic_orbit_representatives(2)` — the **plane** leg, 9 orbits | 23.88 |
| computation: `isotropic_orbit_representatives(2, flag=True)` — the **flag** leg | no return at 400 s |

Construction is 17 s of the row, and the `#h` row 2.6 s of it; the rest is
computation.  The library's own stage record of the same run:

```
isotropic orbit representatives            34.31 s   (lines)
  discriminant image                        0.00 s
  ambient O(L) row                          6.86 s
  coset splitting and transport            27.43 s
isotropic orbit representatives            23.88 s   (planes)
  discriminant image                        0.00 s
  ambient O(L) row                   0.00 + 0.58 + 0.98 + 4.81 s
  parabolic completeness decision      3.25 + 3.33 s
  coset splitting and transport            19.06 s
isotropic orbit representatives              open   (flags)
  discriminant image                        0.00 s
```

So the two legs #620 repaired decide, and the flag leg does not: the stage that
costs the row is the flag leg's stabilizer family.

## Why

`_yield_subgroup_isotropic_orbit_representatives` splits each ambient `O(T_En)`
orbit under `Γ_h` by the double cosets `ρ(Γ_h) \\ ρ(O(T_En)) / ρ(Stab(x))`
(D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6), so it needs the
exact finite image of the stabilizer of the ambient representative.
`OrthogonalCharacterQuotient.exact_isotropic_stabilizer_generators` certifies
that image: it bounds it above by the stabilizer of the representative's divided
discriminant classes and closes the image to that bound by exhibiting elements.

The seed of that closure is `isotropic_stabilizer_generators`, which for a flag
is `sage_indefinite_port`'s `flag_automorphism_generators`: it spells each
generator of the ambient action's stabilizer as a word in the ambient generating
family and multiplies the word out, re-deriving the matrix shape and re-owning
the base ring at every product.  #620 measured that route one rank down on the
same lattice (the plane's family: not returned at 480 s, 1.7 to 2.3 GB and
climbing) and repaired the plane by seeding from the plane's own parabolic
family; the flag was named there as the same defect one rank up.

## The repair, at its owner

`exact_isotropic_stabilizer_generators` needs elements of
`H = Stab_{Γ_0}(f)` from that line, not a family that generates `H`: the closure
below certifies `χ(H)` against the upper bound and raises when it cannot close.
A primitive isotropic flag `ℓ ⊂ P` is stabilized exactly by the elements of
`Stab_{O(L)}(P)` that carry `ℓ` onto itself — the definition of a stabilizer —
and `Stab_{O(L)}(P)` is the parabolic at `P`, whose elements the plane's own
block equations exhibit (D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2,
Theorem 4.9).  So the seed is that subfamily of the plane's parabolic family,
filtered by the subobject's own `stabilizes` predicate and by the ambient
group's membership predicate — the premise the plane's seed has carried since
#620, one rank up.

## What this change does not repair

* The flag leg's ambient `O(T_En)` row took 150.73 s for its one orbit.  Its
  owner is the flag branch of `_isotropic_orbit_representatives`, which has no
  certified shortcut like the plane branch's (`_isotropic_plane_orbit_representatives`
  cites Scattone's Corollary 5.4.8(2) and Sterk, Math. Z. 207 (1991),
  Proposition 4.6, for `T_En`'s two plane classes).  It is the same kind of unit:
  a cited classification of the ambient flag classes, or a route that reads the
  flags of a plane from the plane's own two isotropic lines.
* `parabolic_stabilizer_generators` is cached on the plane object, so the flag
  leg builds its own plane's family even where the plane leg already built one
  for an equal plane: two objects, two families, about five seconds each here.
* A flag whose top term is not a plane keeps the marked-lattice family: the
  parabolic's block form is constructed at rank two only
  (`parabolic_stabilizer_generators`, and `is_parabolic_complete` refuses any
  other rank), so a complete flag of length three or more is untouched.

## The run

The same probe, at the same tree, before and after this change; one process at a
time, the host shared with other projects' Sage jobs.

| leg | before | after | orbits |
| --- | --- | --- | --- |
| line | 34.31 s | 35.29 s | 5 |
| plane | 23.88 s | 23.30 s | 9 |
| flag | no return inside 400 s | 178.33 s | 18 |

The after-run's flag leg splits as 149.05 s of ambient `O(T_En)` flag row and
29.28 s of the split under `Γ_h` — the part this change is at, which at the
parent had not returned inside 249 s.

Card `gamma-h-1` states this group's three counts as 5 lines, 9 planes and
18 flags (D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Table 1), and the
degree-two class is one `O(U + E8(-1))`-class (`#h = 1`, Table 4), so the row's
`#Γ̄_h` is the card's 1.  The two legs that already decided agreed with the card
before this change; the flag leg now does too.

Row total after the change: 17 s of construction, 2.6 s of `#h`, and 252 s of
computation, against no value at all inside the 1800 s cap.

