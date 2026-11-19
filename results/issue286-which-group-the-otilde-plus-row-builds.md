# Which group the `Otilde+` row builds, and where 527 comes from

## 1. The group, from the code

The driver's `Otilde+` row is `lattice.stable_positive_orthogonal_group()`
(`tests/coble_gamma_co_2_incidence_rows.py:764-765`), and that name is built as

```
subgroup = self.stable_orthogonal_group().intersection(self.O_plus())
```

(`src/sage_extensions/categories/lattices.py:5108`), where

* `stable_orthogonal_group()` is `ker(O(L) -> O(A_L))`, "the kernel of the
  discriminant reduction morphism" (`lattices.py:4850-4856`, citing
  Gritsenko–Hulek–Sankaran, arXiv:0810.1614 §1);
* `O_plus()` is `O(L) cap ker sn_R`, the real spinor kernel
  (`lattices.py:6038-6044`).

So the row builds **exactly** `Otilde^+(T_Co) = O^+(T_Co) cap ker(rho)`, the
stable group the owner names.  For `T_Co` it additionally carries a proved
95-generator ordinary family, `stable_positive_orthogonal_group_generators`
(`lattices.py:5126-5156`, research `thm:coble-positive-kernel-ninety-five-generators`,
commit `d77e0deae2`), installed as the subgroup's selected generating morphism.

No proof is needed for the identification beyond that line: the two definitions
are the same intersection.

## 2. The smallest specimens where the stable group and the kernel differ

They differ wherever the kernel holds an element of spinor sign `-1`, and on
`U + U(2) + <-4>` that is 264 of its 888 generators.  Measured
(`.scratch/w286-probes/probe-stable.log`, one process):

| lattice | `|O(q)|` | kernel index in `O(L)` | stable index | kernel line orbits | stable line orbits |
| --- | ---: | ---: | ---: | ---: | ---: |
| `U + U(2) + <-4>` | 12 | 12 | **24** | 4 | **4** |
| `U + U(2) + <-2>` | 2 | 2 | **4** | 3 | **3** |

The stable group is a proper subgroup -- index 24 against 12, 4 against 2, i.e.
exactly twice -- and **the two rows return the same number of primitive
isotropic lines**.  So the spinor condition, which cuts the kernel in two, does
not split any line orbit on these lattices.

## 3. Where 527 comes from, and why it cannot be 2

For `T_Co`: `[O(q) : rho(Stab_{O(T_Co)}(v))] = 46998591897600 / 89181388800 =
527`, and the row returns 527.  The 527 is also the number of nonzero isotropic
classes of `A_{T_Co}`, and `#331` measured the stabilizer image
`89181388800 = |O(q)| / 527` independently.

The reason a subgroup of the kernel cannot do better than one orbit per class is
elementary: an element of `ker rho` acts trivially on `A_L`, so it carries the
divided class `[v/div v]` of a line to itself.  Lines in different nonzero
isotropic classes are therefore never in the same `Gamma`-orbit for any
`Gamma <= ker rho`, and there are 527 of them.  **527 is a lower bound for every
subgroup of the kernel**, `Otilde` and `Otilde^+` alike, and 2 is impossible for
either -- whatever the group's index, spinor condition or generating family.

What *is* two is the card's `isotropic_orbits` for `T_Co`
(`results/issue286-the-class-orbit-decomposition.md`): the `O(q)`-orbits on the
isotropic classes are `{0}` and the 527, so **2 orbits of classes**, not 2
orbits of lines.  That is the most likely source of the expectation, and the two
counts are different quantities: one is a count of classes under `O(q)`, the
other a count of lines under a kernel.

## A correction this turn's red test found

The candidate red test asserted the kernel's line count equals the number of
nonzero isotropic classes -- true on `T_Co` (527 and 527) and **false** on
`U + U(2) + <-2>`, where the row returns 3 lines over 2 classes.  So the "index
1 over every class" is a `T_Co` fact and not a general one, and the assertion was
withdrawn rather than weakened.  What survives, and is measured above, is that
the stable group and the kernel return the same row.
