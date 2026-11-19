# Three kernel line orbits over two classes: the decomposition, and what does not explain it

The specimen is `U + U(2) + <-2>`: `|A| = 8`, `|O(q)| = 2`, two nonzero
isotropic classes, and the kernel row returns three primitive isotropic lines.
Measured in one process (`.scratch/w286-probes/probe-3over2.log`):

| entry | value |
| --- | --- |
| nonzero isotropic classes of `A_L` | **2** |
| `O(L)`-orbits of primitive isotropic lines (**ambient** row) | **2** |
| `ker rho`-orbits of them | **3** |

and, per ambient orbit,

| ambient orbit | its divided class | `|Stab_{O(q)}(class)|` | the kernel's datum | kernel orbits |
| --- | --- | ---: | --- | ---: |
| 0 | `[0] + 2*[2]` | **2** | `NOSPLIT` | **1** |
| 1 | `-[2]` | **1** | a split, `([f1], False)` | **2** |

`1 + 2 = 3`.  So the extra orbit is not a second class: it is the **second
ambient orbit**, which the kernel splits in two.

## What this rules out

The formula I proposed last round -- "the class contributes
`[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]` orbits" -- is wrong on this specimen, in both
directions:

* the class with `|Stab(v̄)| = 2` contributes **one** orbit, not two, and the
  kernel's own datum for it is `NOSPLIT`;
* the class with `|Stab(v̄)| = 1` contributes **two**, where the quotient
  `[Stab(v̄) : ρ(Stab_Γ(v))] = 1/1` is 1.

So the stabilizer of the divided class does not decide the split.  What the two
rows read instead is the two entries the driver already carries: the **ambient
line row**, whose orbits are the units the kernel refines, and
`isotropic_line_stabilizer_image`, whose answer for a line is either `NOSPLIT`
-- the sign witness or trivial quotient proving `G_0 = G Stab(x)`, one orbit --
or a family of double cosets, one per kernel orbit
(`orthogonal_quotients.py`, `splitting_isometries_from_line_class`).  The second
ambient orbit's datum `([f1], False)` is a pair, so that line's kernel orbits are
indexed by a class together with a divisibility datum, not by the class alone.

## What that means for the item

`#286` asks for `[Stab_{O(q)}(v̄) : ρ(Stab_{O(T_Co)}(v))]` per finite class.  On
`T_Co` it is 1 for every one of the 527 classes and the arithmetic is exact
(`results/issue286-which-group-the-otilde-plus-row-builds.md`): 527 classes, one
orbit each, since the ambient row there is a single orbit mapping bijectively to
the classes.  On this specimen the same quotient is 2 at one class and 1 at the
other, which would give 3 -- but only by accident: the split that actually
happens is on the class with quotient 1.

So the per-class index is not the splitting factor in general, and the issue's
phrase "the index ... per finite class" names a quantity that agrees with the
orbit count exactly when the ambient row and the class row are the same
partition -- which holds on `T_Co` and fails here.  The general form is the
double-coset space `Γ\O(L)/Stab_{O(L)}(v)` restricted to one ambient orbit,
computed by `isotropic_line_stabilizer_image`, and its pieces are indexed by a
class *and* that second datum.

## Owed

The pair `([f1], False)` is not decoded here: what the second entry is, and why
its presence for one ambient orbit and absence for the other, is the remaining
question.  It is a small-lattice question (this specimen answers in 12 s) and it
is what a general statement of the per-class index needs.
