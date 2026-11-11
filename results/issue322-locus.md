# #322: the lift locus from the parameter module's structure

`integral_parameter_classes` (`isotropic_lifts.py`) used to decide its residue locus by
listing the parameter module's elements and building a rational isometry per class. On
`T_Co` that module has 262144 classes and one class costs 0.39 s, so the public call never
returned. It now computes the locus as the kernel of one map of finite groups.

## The criterion, with its citation

Eichler's transvection formula (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
(4)--(5); the citation this module already carried) writes, for a primitive isotropic `f`
of an even lattice `L'` and `x` in its rational span,

    E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x .

`E_{f,x}` is an isometry of `L'` exactly when `x` lies in `L'`: if `x` is in `L'` every
term is integral, `q(x)/2` because `L'` is even; conversely a `y` with `b(y,f) = 1`, which
a primitive isotropic `f` supplies, gives `x = [b(y,x) - q(x)/2] f - (E(y) - y)`, and that
lies in `L'` because `f` does.

With the parameterization `phi(a) = E_{f,s(a)} phi(0)` and `phi(x+y) = E(y) phi(x)`, an
**integral base point** makes the integral residue locus the kernel of

    a + mP |-> s(a) + L'      in  L'^vee/L' = A_{L'} ,

a subgroup of `P/mP` of index at most `|A_{L'}|`.

## The computation

1. `s` on a basis of `P`, as a rational coordinate matrix in a basis of `L'`. This is
   `Modules.ParentMethods.rational_coordinates` -- the owner of the lattice's ambient
   coordinates, in `categories/modules/pure/modules.py` -- which lifts through the
   degree-zero augmentation and reads the coefficients into the exact rational field.
2. Clear denominators (`d`), and take the integer Smith form `B = U D V` of the resulting
   integer matrix `B`. Then `B a` is integral exactly when `(D V a)_i` is a multiple of `d`,
   that is when `(V a)_i` is a multiple of `d / gcd(D_ii, d)`.
3. Enumerate the multiples of those steps modulo the period `m` and map each back to its
   class `a = V^{-1} w`. The result is the locus, as classes of `P/mP`.

The old listing is gone. A base point that is not integral is **refused** with the reason
in the error: with a nonintegral `phi(0)` the transvection must also cancel its fractional
part, so the locus is not that kernel, and no cheap criterion is proved for it.

## Measured

| quantity | value | log |
| --- | --- | --- |
| `T_Co`: parameter rank, `|P/mP|`, period | 9, 262144 = 4^9, `m = 4` | `.tmp/p322-probe2.log` |
| cost of one class test, before | 0.353 s + 0.039 s | `.tmp/p322-probe3.log` |
| `T_Co` lift locus (identity reduction of `<e_1>`), after | see `.tmp/p322-locus-size.log` | |
| `U + <2>` control | `|P/mP| = 2`, locus 2 classes | `.tmp/p322-probe11.log` |
| `U(2) + <2>` control | `|P/mP| = 4`, locus **2** classes | `.tmp/p322-probe11.log` |
| `U + U + <2>` control | `|P/mP| = 8`, locus 8 classes | `.tmp/p322-probe11.log` |

Every class the new method returns on the three controls was checked to give an integral
lift by the expensive test (`.tmp/p322-probe11.log`), so the criterion and its indexing
agree with the lift itself where both are affordable.

## The call on `T_Co`

`L.Aut().isotropic_orbit_representatives(1)` and
`Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)`
(`.tmp/p322-reps.log`):

| group | orbits returned | representative |
| --- | --- | --- |
| `O(T_Co)` | **1** | `e_2`, `[v/2] = [1]`, `div = 2` |
| `Õ⁺(T_Co)` | see the run | |

Compared with research's `coble_isotropic_orbits.py` (`computations/reports/`, runs of
2026-11-05), which records the `O(q)`-orbits on the 528 isotropic classes of `A_{T_Co}`:
`{0}` and one orbit of 527 nonzero classes. The page's transfer of that to `O(T_Co)` is
`thm:unpolarized-cusps` (one orbit, transitive), which the `O(T_Co)` row agrees with; the
`Õ⁺(T_Co)` row is `sec-cusp-lifting`'s 527. No count is asserted in a test: the counts are
page proofs and lattice-database card values (lattice-database#7), not card rows yet.
