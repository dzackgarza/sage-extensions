# Item 4: the pullback transport law, reproduced, and what a repair needs

Status: no repair landed.  The reviewer's item-4 defect is reproduced exactly, the
transport law the code implements is wrong for a general map (not only mis-dimensioned),
and both halves are stated below with the case that shows them.

## The reproduction

`tests/objects/test_a_pullback_agreement_reads_every_component_of_the_bundle.sage`
(the file the turn wrote, not landed): $S^1$ with both stereographic charts, the map
$x \mapsto (x, 0)$ into $S^2$'s north chart stated on both charts of the circle, and the
pullback $f^*TS^2$, of rank two over a one-dimensional base.

On `f2cc1e0` both of its tests fail in the same place:

    ValueError: zip() argument 2 is longer than argument 1
      at `_pullback_family_agrees`, in
      carried = tuple(... subs(dict(zip(target_symbols, composed, strict=True))) ...)

`composed` has one entry per coordinate of the bundle's chart (two, the sphere's), and
`target_symbols` has one per coordinate of the base's chart (one).  So a rank-two pullback
over a one-dimensional base cannot be stated at all -- the reviewer's example, confirmed.

## The second half: the law itself, not only its dimension

Replacing the base's dimension by the bundle's rank and reading the components in the
image chart's symbols makes the disagreement case refuse correctly, and then the *agreement*
case fails:

    the family states no one section of the pullback: on the chart U_N the component 0 is
    x1, and the component stated on the chart U_S carries it to y1 there, which leaves the
    residual x1 - y1

That is not a bug in the test but a bug in the law.  The code transports by the derivative
of the composite map `T = f` read in the target chart, i.e. it treats the components as a
vector field on the base pushed along $f$.  For a section of $f^*E$ the components are
coordinates in the frame of the **bundle's** chart at $f(q)$ (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 10), so two charts $V_s, V_t$ of the codomain contribute the
Jacobian of the codomain's coordinate change evaluated at the image point, and no
derivative of $f$ at all:

    a_t(x) = J_{V_s -> V_t}( T_s(x) ) . a_s(x)

For $f = \mathrm{id}$ that reduces to the Jacobian of the base's own chart change, which is
why the identity-map and reflection specimens passed: there the codomain change *is* the
base change.  For a map between different manifolds the two differ, and the current code
computes the wrong one -- a wrong answer rather than a refusal, which is why it went
unseen.

## What a repair needs

1. `_pullback_family_agrees` takes the bundle's rank and reads each side in the **codomain**
   chart that the base chart is represented in (`mapping.chart_maps()` gives that chart,
   and the composite `T_s` is already computed).
2. The Jacobian is of the codomain's coordinate change between the two image charts,
   evaluated at `T_s(x)`, with the substitution into the target base chart's coordinates
   applied to the *resulting functions*, not to the Jacobian's entries.
3. The engine vector field must not be built for a pullback section at all: it is a vector
   field on the base, and a section of $f^*E$ is not one unless $f$ is the identity.  Its
   absence is already what `__call__` checks for, so it is a deletion, not a guard.

The test file above is the red for 1 and 2, and it is the file to land with the repair.
