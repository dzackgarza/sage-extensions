# #286, batch 2: the definite route for the Scattone planes, and `Gamma_{En,2}`

Branch at `056932f`.  Nothing on T_Co is run.  **Neither item closes**: both stop at a
named step, measured below.  No comparison with a card value is claimed in this batch.

## Item 1, `6JRX` / `6JRY` planes: stopped at the genus enumeration of `<-2k> + 2E8(-1)`

The instruction's method is confirmed as the right target.  The port's own fixture states
it (`tests/fixtures/DATA_SOURCES.md:172` and
`k3_modular_strata.json::type_ii_correspondence`): "E -> E^perp/E is a bijection from the
O(Lambda_{2k})-orbits of primitive isotropic planes onto the genus G(k) of
`<-2k> + 2E8(-1)`, so there are h(k) orbits".  In this repository that genus member is
`Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2k]])` -- rank 17, signature
(0,17), `|det| = 2k`, negative definite -- and, since `E8(-1)^2` is a unimodular summand of
`Lambda_{2k}`, `E^perp = E8(-1)^2 perp W` with `W` of rank 3 inside `U^2 + <-2k>` and
`E ∩ E8(-1)^2 = 0` (that summand is negative definite), so `K_E = E^perp/E` has rank 17 and
determinant `+-2k`.

What runs:

```
genus of E8(-1)^2 + <-2>                builds in 0.0 s
genus mass (Smith--Minkowski--Siegel)   2499347/9440684171518279680000 in 1.1 s
plane quotient K_E, first candidate     25-35 s cold, ~1 s warm afterwards
17 candidate shapes on Lambda_2         all give det -2 (one genus, as the theory says)
```

What stops:

```
genus_class_number()  > 6 GiB in 38 s, killed at 6324 MiB
  Genus._genus_classes -> neighbor_iteration(algorithm="orbits")
  -> p_divisible_vectors -> automorphism_group -> PARI qfauto
  -> PARIError: the PARI stack overflows (current size: 1073741824)
is_globally_equivalent_to(form, form)   qfisom overflow at 1 GiB
the same after pari.allocatemem(3 GiB)  overflow at 3 GiB
nineteen sequential K_E builds          tree RSS 6681 MiB, julia 4907 MiB, killed
```

So the completeness check the instruction names (the mass formula) is available, and the
class enumeration that the mass would certify is blocked inside PARI at rank 17 on this
host, in both directions: `qfauto` for the neighbour traversal and `qfisom` for the class
comparison.  Two consequences already measured and recorded in `TRAPS.md`: the class
comparison must not fall back on `is_isometric` (it is `negation(Isom(other).is_empty())`
and merged 17 different shapes into one class in 0.0 s each), and a batch of `K_E`
computations cannot run in one process because the Julia bridge grows past the guard.

Next step: enumerate the genus without the bridge.  The classes are gluings of
`E8(-1)^2` with a rank-1 piece inside `U^2 + <-2k>`, which is a finite combinatorial
enumeration over isotropic subgroups of a small discriminant group; it needs the
realisation of each gluing as a plane, which is the step after that.

## Item 2, `029J` rows `gamma-en-2` and `otilde-plus-t-en`: stopped at a vector stabilizer's discriminant image

The definition is now pinned from the source the issue names.  Alexeev--Engel--Garza--
Schaffler, *Compact moduli of Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025),
Definition 2.6 (arXiv:2312.03638): `Gamma_{En,2}` is the image in `O(T_En)` of
`{g in O(L) | g o I_En = I_En o g and g(h) = h}`, where `h = e + f in U(2) = S_dP` is the
degree-2 polarization (`e^2 = f^2 = 0`, `e.f = 2`), and `Gamma_{En,2} = Gamma_En ∩ Gamma_dP`
with `Gamma_En = O(T_En)`, `Gamma_dP = O(T_dP)`.

Built in this repository as `T_En.Aut().stabilizer(h)` with `h = e_ep + e_fp`:

```
h = e_ep + e_fp: q(h) = 4 (bilinear convention, h^2 = 2), primitive, div(h) = 2
O.stabilizer(h)                    0.0 s
contains_character_kernel()        False
character_data_is_complete()       False
finite_character_quotient()        ValueError: no finite character quotient
isotropic_orbit_representatives(1) AssertionError: "cut out by a predicate that is not a
  character kernel ... The missing operation is a generating set for an arithmetic
  subgroup of O(L), which belongs in lattice_engines.py"
```

So the row cannot start: the splitting needs `rho(Gamma)` in `O(A_{T_En})`, and a vector
stabilizer is not a determinant/spinor/discriminant preimage, so the character machinery
refuses it by design rather than guessing an image.  The derivation the instruction asks
for -- the image from `O(Q)`, the map on `D^perp/D ≅ A_Q` and `GL(P)` -- is exactly this
missing operation; for the *plane* rows `Q = P^perp/P` is negative definite (rank 8 on
`T_En`) and `O(Q)` is a finite PARI computation, but for `Gamma_{En,2}` itself the
stabilized object is a vector, so its `Q = h^perp/<h>` is indefinite (rank 11, signature
(1,9)) and the same recipe does not apply unchanged.
