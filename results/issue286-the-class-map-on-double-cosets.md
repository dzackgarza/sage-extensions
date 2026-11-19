# The class map on the double cosets: proved, and it carries the last datum

**Lemma.** Let `L` be even, indefinite and nondegenerate `2`-elementary, so
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3; the article's page range is what this repository cites and the theorem's
own printed page is not in front of me); let `J_0` be an order-four totally
isotropic subgroup of `A_L`, `P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`,
and `P` a primitive isotropic plane with class `J_P = [P/2]`.  Then the map

$$
P_0\backslash O(q)/\rho(\mathrm{Stab}_{O(L)}(P)) \longrightarrow
\{\,P_0\text{-orbits on the liftable classes } J\,\}, \qquad
[P_0 g \rho(\Pi_P)] \mapsto P_0\cdot gJ_P
$$

is **well defined** and **surjective**.  Smallest case: `U + U(2) + <-4>`,
`|O(q)| = 12`, `|P_0| = 4`, three liftable classes, two planes in the row.

## Proof

*Well defined.*  Two representatives of one double coset differ by `p in P_0` on
the left and `h in rho(Pi_P)` on the right.  `P_0` fixes `J_0`, and `h` acts on
classes as an isometry of `A_L`; the class attached to `g` is `gJ_P`, and

$$
(p g h)J_P = p\,(g\,(hJ_P)) = p\,(gJ_P),
$$

because `rho(Pi_P) <= Stab_{O(q)}(J_P)` -- the stabilizer of a plane's own
stabilizer image fixes the plane's class, which is the equivariance of the
divided class under an isometry of the lattice (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, **Lemma 3.6, printed p. 22**, whose double-coset
correspondence is the same statement for the orbits).  So the value is an
element of the `P_0`-orbit `P_0·gJ_P`, independent of the representative.

*Surjective.*  `rho(O(L)) = O(q)`, so every class is `gJ_P` for some `g`, and
every double coset is nonempty.

## Checked at the smallest case

`.scratch/w286-probes/probe-map2.log`, one process:

```
plane orbits: 2
the two classes are distinct: True
their P_0-orbits are distinct: True
J_0 is on neither: True
```

So on this specimen the map is a bijection of two double cosets onto two
`P_0`-orbits, and neither plane sits over the base class `J_0` that cuts `Gamma`
out.  That is consistent with, and sharper than, the earlier count `2 = 2`.

## What the lemma does for the last datum

It turns "which class-orbit carries two of the seven orbits" into **the fibre of
an explicit map** -- the map above -- instead of an unexplained coincidence.  The
fibre is 1 exactly when no two double cosets share a `P_0`-orbit of classes, and
`T_Co` is the case where one fibre is 2 (six class-orbits, seven orbits,
`results/issue286-the-gamma-co-2-distribution-measured.md`).  Computing that fibre
needs the double-coset representatives, which is what the plane row produces; the
lemma says precisely which comparison to make on them, and it is why no cheaper
route exists: the classes alone lose exactly the information the fibre carries.

## Status of the item

The map is proved and checked; the fibre at `T_Co` is owed to the `#391` row's
seven representatives, and the lemma fixes the check to be run on them -- group
the seven by `P_0·gJ_P` and read which group has two.  No code changed, so no red
test this turn; the probe is the check.
