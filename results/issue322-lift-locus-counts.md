# #322: how often `integral_parameter_classes` runs per ambient call on `T_Co`, and its owner cost

The call: `T_Co.Aut().isotropic_orbit_representatives(1)` with
`T_Co = <2> + (U + E8(-1))(2)`, rank 11, signature (2, 9).  On main it returns — one
representative of a primitive isotropic line, recorded by #292 at 1017.69 s on a loaded VM and
424.5 s quiet.  The issue's open obligation is the *method*: `integral_parameter_classes` decides
the finite integral lift locus "by one constructed lift per coset", and the count of its calls per
ambient call had not been measured.

## 1. What the method does

`IsotropicReductionLiftTorsors.integral_parameter_classes` (`isotropic_lifts.py`) is `@cached_method`
and does two things:

* it reads the candidate classes from the *parameter module's structure*: one integer Smith form of
  the section's coordinates on a basis of `P` gives `steps = (denominator // gcd(smith_ii,
  denominator))_i`, and the cosets of the transvection kernel `K` in `P/mP` are enumerated by
  `coset_steps = (gcd(step_i, m))_i` — `|P/mP|/|K|` of them, 512 on `T_Co` at `m = 2`.  (The old
  defect, listing every element of the module, is gone: this part is structural.)
* for each of those cosets it then builds `phi(a) = E_{f,s(a)} o base` as an isometry, composes it
  with the base lift into a *morphism*, and asks that morphism for its integral restriction
  (`lifts_integrally`).  This is the part the issue names.

## 2. The count, with the stack

Counted by replacing `integral_parameter_classes` with a wrapper that prints the caller frames and
delegates to the cached original, over one whole ambient call (`.tmp/p322-probe1c.log`):

```
CALL 1 begins at   34.7s  from _integral_lift_locus <- integral_members
                             <- recursive.py:1720 _isotropic_pointed_isometry <- pointed_isometry
CALL 2 begins at  232.7s  (the same stack)
CALL 3 begins at  386.1s  (the same stack)
CALL 4 begins at  548.7s  (the same stack)
CALL 5 begins at  856.5s  (the same stack)
CALL 6 begins at 1042.4s  (the same stack)
CALL 7 begins at 1237.6s  (the same stack)
CALL 8 begins at 1557.6s  (the same stack)
```

So the call is **not** once per ambient call: it is once per *candidate* that the port's
`_isotropic_pointed_isometry` (`sage_indefinite_port/indefinite/recursive.py:1720`) tests, each
candidate a fresh reduction object with its own cached locus.  Eight candidates had been tested by
1557.6 s, at 150-320 s per locus on this VM, and the ambient call had still not returned at the
harness cap -- against #292's 1017.69 s loaded and 424.5 s quiet for the whole row, which is the
same per-candidate cost on a machine carrying fewer foreign jobs.  The multiplier is therefore the
number of candidates, not a cache miss: **one locus per candidate, and every locus enumerates the
same 512 cosets on `T_Co` at `m = 2`.**

That is what makes the repair worth its cost: at ~150 s per locus and several children, the row is
minutes even when it returns, and the locus is the only part of it that this unit owns.

## 3. The owner cost, at the deepest frame

The faulthandler stack inside that call (`.tmp/p310b-probe7.log`, and #310's §5):

```
integral_parameter_classes -> lifts_integrally -> parameterization -> ambient.eichler_transvection
  -> Lattices._eichler_transvection_column_matrix (lattices.py:7520-7522)
  -> the owned ring's __add__ -> _operand_in_ring -> _element_constructor_
```

so the per-coset cost is (i) one Eichler transvection built as a matrix through the ring's own
addition, entry by entry, and (ii) one composed morphism with its integral restriction.  Both are
paid 512 times per reduction object on `T_Co`.

## 4. What was attempted and not landed

The intended repair is to decide each coset from the formula instead of from a constructed lift:
Eichler's transvection is

    E(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x,     x = s(a),

so `phi(a)`'s columns are the base lift's columns shifted by multiples of `f` and of `x`, and
"integral" is "every entry integral".  Written that way, the 512 cosets cost 512 small rational
column operations instead of 512 isometries.

It was written and it does not typecheck against the data: `base = self.base_point()` is an
isometry of the **ambient** rank-11 rational space (the parameterization composes it as
`self(ambient.eichler_transvection(...) * base)`), while `source` is a reduction *sublattice*; so
`base(source.module_generator(label))` raised

    TypeError: e_0 does not describe an element of Lattice of rank 11 and signature (2, 9)

(`.tmp/p322-probe2.log`).  The lift the integrality test reads is `self(E(a) * base)` — the ambient
composite pushed through the torsor's reduction — so a faithful coordinate evaluation needs the
torsor's factorization of `self(.)` into a rational map from the ambient space to the target and one
from the source into it.  That factorization is not stated at any owner today, and guessing it would
silently change which classes the locus returns: a wrong formula does not raise, it returns a
different set.  It is therefore reverted rather than landed, and the missing step is named here:
`IsotropicReductionLiftTorsors` must expose how `self(isometry)` acts on matrices, and then the
locus is a coordinate computation on the parameter module.
