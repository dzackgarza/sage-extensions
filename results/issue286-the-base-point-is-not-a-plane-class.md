# The base point of `Gamma_{Co,2}` is not a liftable plane class

**Lemma.** Let `J_0 = A_{U(2)} = <[ep/2],[fp/2]>` be the point that cuts
`Gamma_{Co,2} = rho^{-1}(P_0)` out, `P_0 = Stab_{O(q)}(J_0)`, and `J = [P/2]` the
class of a primitive isotropic plane.  Then `J_0` is **not** of the form `[P/2]`
for any plane `P`: the two families of order-four isotropic subgroups of `A_L`
are different families, and the class map of
`results/issue286-the-class-map-on-double-cosets.md` has domain the `J`-family
alone.

## The two families, measured

| family | `|Stab_{O(q)}|` | `O(q)`-orbit |
| --- | ---: | ---: |
| `A_{U(2)}` (the U(2) block's dual classes) | 696729600 | 67456 |
| `J = [P/2]` (a plane's divided classes) | 1981808640 | 23715 |

(`results/issue286-the-gamma-co-2-distribution-measured.md` for the `T_Co`
numbers.)  Different stabilizer orders and different orbit lengths, so the two
families cannot be one orbit of subgroups; and on the smallest specimen the
difference is visible directly.

## The smallest case, checked by content

`U + U(2) + <-4>`: `|O(q)| = 12`, three liftable classes forming one `O(q)`-orbit,
two planes in the `Gamma` row.  Comparing orbit **element lists** -- not the GAP
objects' identity, which a `!=` between engine sets compares
(`.scratch/w286-probes/probe-fibre.log`):

```
plane orbits: 2
the class orbit size: 3
  orbit 0 (J_0 is 0): 1 elements
  orbit 1 (J_0 is 0): 2 elements
  orbit 2 (J_0 is 0): 1 elements
plane classes are distinct: True
they are in the same P_0-orbit: False
neither is J_0's orbit: True
```

`P_0`'s orbits on the three liftable classes have sizes `2` and `1`, and `J_0`'s
own `P_0`-orbit is a third, of size `1`: `J_0` is not one of the three.  The two
plane classes fall one in each of the two liftable orbits, so the fibre of the
class map is `1` at each -- the row's `2` is `1 + 1`.

## Correction to the previous round

The previous round's check compared `libgap` sets with `!=`, which is an
identity comparison on engine objects, so its three "True" lines were vacuous.
The claims it made happen to be true -- rechecked here by element lists -- but
the check itself was not a check, and the sentence "their `P_0`-orbits are
distinct" is only now supported.  That is recorded rather than quietly fixed.

The other correction is mathematical: the class map's target is the `J`-family,
and `J_0` is not in it, so a fibre of `0` over the `P_0`-orbit containing `J_0`
is not a defect -- there is no such orbit in the target.  On `T_Co` the six
`P_0`-orbits measured in
`results/issue286-the-gamma-co-2-distribution-measured.md` are already orbits on
the `J`-family, so that measurement stands; what was wrong was my reading of it
as orbits on a set that contained `J_0`.

## Status

The last datum -- which `P_0`-orbit carries two of the seven `T_Co` orbits --
is unchanged in kind: it is the fibre of the class map over one of the six
orbits, and it is read from the row's seven representatives.  What this lemma
removes is the wrong target: the base point is not a class the fibres are taken
over.
