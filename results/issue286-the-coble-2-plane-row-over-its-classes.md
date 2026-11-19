# The `Gamma_{Co,2}` plane row over the liftable classes `J`

The one row whose finite image is not trivial behaves unlike the two kernel
rows, and this note measures by how much at the sizes a command reaches.

## Measured

Probe `.scratch/w286-probes/probe-gamma-co-2.py` (logs `probe-gam.log`'s successor
`probe-gam2.log`), every number computed in one process:

| lattice | `|A_L|` | `|O(q)|` | `|Stab(J_0)|` | liftable `J` | `Gamma_{Co,2}` plane cusps |
| --- | ---: | ---: | ---: | ---: | ---: |
| `U + U(2) + <-2>` | 8 | 2 | 2 | 1 | **1** |
| `U + U(2) + <-4>` | 16 | 12 | 4 | 3 | **2** |
| `T_Co` | 2048 | 46998591897600 | 1981808640 | **23715** | **7** (recorded, run 43556671111) |

On `U + U(2) + <-4>` the two cusps sit over two **distinct** classes `J`, and
neither is the base class `J_0` that cuts the subgroup out
(`tests/lattices/test_the_coble_2_plane_row_over_the_liftable_classes.sage`).

## What that rules out

The kernel rows satisfy `cusps = (liftable J) * (ambient index)`: `2·1 = 2`,
`3·1 = 3`, `23715·8 = 189720`.  `Gamma_{Co,2}` does not: `2 ≠ 3·1` and
`7 ≠ 23715·8`.  So the ambient index of
`results/issue286-the-plane-class-index-is-the-fibre.md` is the fibre of the
*ambient* row over the classes, and of a kernel row because there `ρ(Γ) = 1`;
for `Gamma_{Co,2}`, whose `ρ(Γ) = Stab_{O(q)}(J_0)` is not trivial, the row's
orbits are spread over a few classes and the count is far below the class count.

## What is still owed, said exactly

For `T_Co` the owed datum is **which** `J` carry `Gamma_{Co,2}`'s seven plane
orbits -- equivalently the `P_0`-orbits of classes those seven represent, where
`P_0 = Stab_{O(q)}(A_{U(2)})`.  Nothing here computes it: the row itself is the
1685 s computation of the `#391` gate file, and the seven classes are read off
its representatives, so the datum comes with that row and not before it.  What
is established is the relation it must satisfy -- seven orbits over at most
seven `P_0`-orbits of the 23715 classes -- and the small-case shape of it.

## The test

`tests/lattices/test_the_coble_2_plane_row_over_the_liftable_classes.sage`: on
`U + U(2) + <-4>`, the liftable class count is computed from `|O(q)|` and the
class stabilizer, the row is the public orbit call, and each returned plane's own
class is built from its divided classes; the row has two cusps against three
classes, the two classes are distinct, and neither is the base class.  Measured
33.65 s under a VM at load 20 (the row alone is 6.84 s of it, from the probe).
