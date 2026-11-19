# The locality lemma: true, and not provable in this representation

## The lemma

> **Lemma.** Let $M$ be a smooth manifold, $D$ a derivation of $C^\infty(M)$, and $f, g$
> smooth functions that agree on an open neighbourhood of a point $p$. Then
> $(Df)(p) = (Dg)(p)$.

Its consequence is the one item 2 needs: a derivation is read chart by chart, so
`from_derivation` could be written on any manifold, not only where one chart presents it.

**Source.** Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 8, Prop. 8.15: the map
$V \mapsto (f \mapsto Vf)$ is an isomorphism from the vector fields onto the derivations of
$C^\infty(M)$.  The step that makes it local is the standard one, and it needs a function
that is identically $1$ near a point and $0$ outside an open set: if $f$ vanishes on a
neighbourhood of $p$, choose $\chi$ with $\chi \equiv 1$ near $p$ and $\operatorname{supp}\chi$
inside that neighbourhood; then $\chi f \equiv 0$, so
$0 = D(\chi f)(p) = \chi(p) (Df)(p) + f(p)(D\chi)(p) = (Df)(p)$.  The existence of such a
$\chi$ is Lee, Lemma 2.26 (the bump function, built from $e^{-1/x}$), and it is used through
partitions of unity.  I cite the proposition and lemma numbers; the page numbers of this
edition were not checked against a copy this turn.

## Verdict in this tree: REFUTED as provable here

Two measured facts on `0d72661`, in the image rootfs.

**A bump function of the kind the lemma needs cannot be stated.** A function on $S^1$ is
stated by one expression per chart, and what a chart expression can express is rational in
the chart's coordinate.  The best the tree does is a *soft* bump:

    h_N(x) = 1/(1+x^2)  on U_N        h_S(y) = y^2/(1+y^2)  on U_S
    h at the south pole (north coordinates 0)     1
    h at the north pole (south coordinates 0)     0

It is smooth, global, and never vanishes: $h_N$ is zero only where $1 = 0$.  Lee's argument
needs $\chi$ to be **identically** zero outside an open set, and no chart expression on
$S^1$ can be: an expression that vanishes on an open set of a chart vanishes identically on
that chart, so a function that is $\equiv 0$ off a proper open set is $\equiv 0$ everywhere
on every chart it is stated on.  The tree has no compactly supported smooth functions, and
therefore no bump function.

**And the reading is refused exactly where the lemma would be needed.** On the circle,
`from_derivation` answers

    refused -- cannot read a section off a section of rank-1 smooth real vector bundle …

which is the guard the previous turn's test pins: one chart of the circle is not a cover, so
its coordinates are not elements of $C^\infty(S^1)$.

## What would unblock it

A construction of a smooth function on $M$ that is $1$ on a neighbourhood of a point and $0$
outside a chart -- Lee's Lemma 2.26 expressed in the tree's chart data.  That is a new
element of the algebra, not a repair: it needs chart expressions with a genuine zero set on
each chart, which the rational expressions of this representation can give only where the
numerator vanishes on an open set, i.e. never.  So the honest statement is that item 2's
general case is **out of reach of this representation**, not that it awaits a patch, and the
issue's algebra clause is the place to say so.
