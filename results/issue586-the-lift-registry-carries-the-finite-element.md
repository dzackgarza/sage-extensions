# The lift registry carries the finite element, and one plane's action is a product in `O(A_L)`

`results/issue585-the-incidence-decided-by-divided-classes.md` priced the
incidence walk at 53.4 ms a plane at plane 10 and 66.1 ms at plane 1000, of
which **51.44 ms and 64.65 ms** are one call: `_divided_class_action` read the
composite `s_P s_{P_0}^{-1}`'s dual action by inverting its matrix, and the
row's lifts are words in the ambient generators whose entries grow with the
plane.  At 66.1 ms the row of 189720 planes is 12540 s against the driver's
10800 s cap.

The datum that removes the term is the finite element the split already
evaluates on its own lifts.  This note records where that element was evaluated
and dropped, what the registry now carries, and what the walk costs and decides
with it.

## 1. Where the element is evaluated and dropped

`OrthogonalCharacterQuotient._iter_splitting_isometries_in_im_rho_from_image`
has two routes, and both compute a lift's discriminant image and then throw it
away.

**The orbit route** (a caller passes a point of the finite `im rho`-set: the
line rows, through `splitting_isometries_from_line_class`).  For every lift it
evaluates the whole character map and uses one component as a check of its own
word section:

```python
for lift in lifts:
    image_of_lift = self.image(lift)
    if image_of_lift["discriminant"] != key_disc:
        raise ArithmeticError("splitting lift's discriminant image disagrees ...")
    yield lift
```

`self.image(lift)` is a `discriminant_morphism` construction -- the 51-65 ms --
evaluated on every lift, compared, and dropped.  `image_of_lift["discriminant"]`
*is* `rho(lift)`: it is the element, not something to be converted into it.

**The coset-walk route** (the plane rows, which hold the parabolic's generators
and no point of the finite set).  Here the lift is spelled as a word along a
breadth-first tree over the right-coset action of `im rho`, and the route
evaluated `rho` on **one** lift, at the end, as a check of its parent
bookkeeping; every other lift's finite element was never materialized, because
the element for a reached coset would have to come from a
`PreImagesRepresentative` word problem (101.8 ms a coset, `#390`'s measurement).

So the answer to the unit's first question is: the element the split evaluates
is exactly the lift's finite element, it is the discriminant component of
`self.image`, and on the orbit route it is evaluated **per lift** and dropped.
On the plane row's route it is evaluated once per row, and the per-lift element
is a product of the split's own `rho`-images of the ambient generators -- the
same `rho`, one product per tree edge, no matrix inversion.

That one-per-row check had never run either.  It multiplied elements of the
*coset action* by an element of `im_rho_perm`, which GAP refuses
(`List Element: <list>[10] must have an assigned value`) -- and it could not
have reached that line before, because the walk's first representative on a
kernel row is the base point, whose word is empty: the branch compared the
identity with itself.  Making the per-lift element live is what ran it, and the
check the code makes now is the spelled element against the character map, on
the first lift whose word is not empty.  This is a defect the repair surfaced
and did not introduce; the earlier check was vacuous, not wrong.

## 2. What is registered

`register_isotropic_lift(plane, lift, parabolic_generators, discriminant_image)`
now retains the finite element in the same span-keyed record as the lift, and
three readers answer from that one hit: `registered_isotropic_lift(plane)` for
the pair, `isotropic_lift_of(plane)` for the lift (unchanged answer), and
`isotropic_lift_discriminant_of(plane)` for the element -- the datum itself, not
a function of it.

Where the element comes from, per route:

* **orbit route**: `image_of_lift["discriminant"]`, the character map's own
  evaluation the route already makes to check itself.  Nothing new is computed;
  the drop is removed.
* **coset-walk route**: the very expression that composes the lift's generators,
  applied to their `rho`-images: `rho` is a homomorphism of the owned laws, so
  `values[reached] = A * values[parent]` is mirrored by
  `images[reached] = rho(A) * images[parent]`.  The `rho`-images are
  `ambient_discriminant_images()`, the split's own sweep over the ambient
  generating family, crossed back to the owned `O(A_L)` once per walk generator
  (not once per lift).  The mirror is order-for-order, so it is independent of
  which side the engine's law composes on.
* **the identity registrations** of a row's source plane: `O(A_L)`'s one.

The element is checked against the character map where the route can afford it:
once per row, on the first tree-spelled lift whose word is not empty
(`images[point] == self.image(value)["discriminant"]`), and -- in the slice
measurement of section 4 -- for **every** one of the 1000 planes' registered
elements against `lift.discriminant_morphism()`.

The walk's action is then `_composite_divided_class_action`:
`_element_to_engine(O(A_L), target_image * ~reference_image)` -- one product and
one inversion in a finite group of order 46998591897600, crossed to the engine
the classes live in.  The inversion-based route is not kept as a second
implementation: `_divided_class_action` is gone, and the only other place the
dual action is read is `image()` itself.

The eager materializer `_splitting_isometries_in_im_rho_from_image`, whose only
caller was `splitting_isometries_from_line_class`, is gone with it: it would
have had to drop the element to return what it returned.

## 3. What a step costs

Measured on `T_Co`'s own `Otilde` plane row, `.tmp/issue586/probe-586-walk.py`,
band means at plane 10, 100 and 1000 of one run (log: `.scratch/586/walk-586.log`):

| step a plane | planes 1-10 | planes 91-100 | planes 901-1000 |
| --- | ---: | ---: | ---: |
| the registered lift and its element, one span-keyed hit | 0.922 ms | 0.884 ms | 0.766 ms |
| the composite as an element | 0.648 ms | 0.711 ms | 0.571 ms |
| **its action on `A_L`** | **3.634 ms** | **0.782 ms** | **0.363 ms** |
| the three carried class pairs | 0.038 ms | 0.037 ms | 0.034 ms |
| the three line keys | 0.035 ms | 0.037 ms | 0.017 ms |
| **the walk** | **5.277 ms** | **2.450 ms** | **1.787 ms** |
| the dual action of the same planes' composites, same loop | 46.8 ms | 60.2 ms | 60.2 ms |

`walk-586.log`: `Otilde` on `T_Co`, 1000 planes of the row, the division check
running beside the walk for the first hundred planes.  A second run without
that check (`walk-row-100.log`, 100 planes) reads 3.481 ms at the first ten and
**0.605 ms at the hundred**, walk 4.968 ms and **2.014 ms**, with the span
0.813 ms, the composite 0.542 ms, the carries 0.033 ms and the keys 0.021 ms.

Two readings of the table.  The action's first-ten figure is the warm-up of the
first calls in the process: it decays 33.3, 16.8, 11.3, 8.6, 6.9, 5.8, 5.0, 4.5,
4.0, 3.6 ms over the row's first ten planes and settles at 0.36 ms.  A ten-plane
slice therefore measures the construction, not the coefficient; the coefficient
of a row is the plane-1000 band's.  And the plane-100 band is the one band that
carries the comparison route's own work in its neighbourhood (60 ms a plane of
dual action plus three carries), which is why it sits above the plane-1000 band
in the first log and at 0.605 ms in the second.

The registered element costs nothing per plane beyond its own record: the walk
reads it in the span-keyed hit it already made for the lift.  The bands of
`walk-586.log` grow 1347.7 MiB to 1349.8 MiB over 990 planes, **2.2 KB a
plane**, against the 7.9 KB a plane `results/issue585-the-incidence-decided-by-
divided-classes.md` measured for the same walk without the element.  That the
difference is the constructions the dual action leaves behind is consistent with
the arithmetic and is **not** established by a separate measurement here.

## 4. The edges are the ones the dual action decides

`walk-586.log` re-decides every plane of the first hundred by the route the walk
used before: the composite's own dual action, `move.discriminant_morphism()`
crossed to the same engine model, carried into the same three class pairs, and
compared as class sets.  **30 of 30** carried class pairs over the row's first
ten planes and **300 of 300** over its first hundred agree -- 297 of those at
planes 2 to 100, which is the window
`results/issue585-the-incidence-decided-by-divided-classes.md` reports 297 of
297 in, its 30 of 30 counting the base plane's identity move as this does.  The
keys carried by the two actions are equal wherever the pairs are, because the
key is a function of the pair; the 473 keys and 3000 edges of the thousand-plane
run are the walk's own, and no key disagrees with the dual route's.

The registered elements themselves are checked harder than once a row: all
**1000 of 1000** planes' elements are compared with their lift's own
`discriminant_morphism()` in the same run, at 52-60 ms a comparison, and
**none** disagrees.  That is the statement the unit's warning is about -- a
second, cheap implementation of the dual action could disagree consistently with
the class route and no edge comparison would see it; the element registered here
*is* the dual action's value on each lift, read from the split's own `rho`.

## 5. Extrapolation at 189720 planes

| coefficient | source | 189720 planes | against the 10800 s cap |
| --- | --- | ---: | ---: |
| 66.1 ms a plane | the dual action, `#585`'s plane-1000 band | 12540 s | over by 1740 s |
| 2.450 ms a plane | this walk, band of planes 91-100 | 465 s | 23x under |
| **1.787 ms a plane** | **this walk, band of planes 901-1000** | **339 s** | **32x under** |
| 2.014 ms a plane | this walk, second run, band of planes 91-100 | 382 s | 28x under |
| 5.277 ms a plane | this walk, the row's first ten planes, warm-up | 1001 s | 11x under |

The number a dispatch should carry is **339 s** for the walk at 189720 planes,
against 12540 s for the same walk before, with the row's other terms unchanged
(`#585`'s section 5: the relation 0.07 GiB, the plane row's representatives
11.4-12.0 GiB, the fixed cost 1.25-1.4 GiB).  The walk is no longer anywhere near
the cap: the plane row's memory and `#584`'s representatives are what bound the
row now, and the walk's own remaining terms are the two isometry operations that
are still per plane -- the span key 0.77 ms and the composite itself 0.57 ms.

## 6. What this does not fix

* **The composite is still a per-plane product in `O(L)`.**  `move = target_lift
  * ~reference_lift` costs 0.57-0.71 ms a plane and is read only by the one
  transport check the walk makes at each plane of the first covering; the action
  no longer needs it.  Removing it from the walk's loop is a change to that
  check's placement, not to the action, and is not made here.
* **The span key is the walk's largest remaining term**, 0.77 ms a plane, and it
  is the same lookup the registry answered with before.
* **The row still cannot be run here**: 189720 planes of `T_Co` is what the
  driver dispatches, and the two kernel rows still need the plane row's
  representatives (`#584`).

## 7. A pre-existing failure this measurement met

The gate that consumes this walk,
`tests/lattices/test_the_incidence_decided_by_divided_classes.sage`,
`tests/lattices/test_a_row_computes_one_plane_covering.sage` and
`tests/lattices/test_the_incidence_line_vertex_is_named_by_the_finite_image.sage`,
fails four of its eight tests under some values of `PYTHONHASHSEED`, in the
*ambient flag row* of `U + U(2) + <-2>` and not in either incidence route:

```
src/sage_extensions/categories/modules/module_morphisms/module_morphisms.py
  flag_stabilizer -> change * generator * ~change
ZeroDivisionError: Generic endomorphism of Integral lattice of rank 2 and
signature (0, 0) has no inverse ...: its determinant -2 is not a unit of
Integer Ring
```

The adapted basis `_engine_flag_adapted_rows` returns is not unimodular for that
plane module under those seeds.  It is **pre-existing**: a plain export of
`43e0f72` (`git archive`, no change of this note) fails the same four tests at
`PYTHONHASHSEED=1` and passes at 0, 2, 3 and 4; the tree this note's change sits
on fails the same four at 0 and 1 and passes at 2 to 6, and a change shifts
which seeds trip a hash-order defect without adding a failure: no test id fails
here that does not fail at the base.  The defect needs its own reproduction and
its own repair; it is not this issue's, and it makes the gate flaky for every
change that touches it.

