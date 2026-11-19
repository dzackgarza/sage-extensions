# The fibre formula is refuted: it counts class-orbits, not plane orbits

**Refuted lemma.** *The number of `Gamma_{Co,2}`-orbits of planes over a
`P_0`-orbit `𝒪` of liftable classes is `|𝒪|·m(𝒪)/|P_0|`, with
`m(𝒪) = |P_0 cap rho(Pi_P)|`*
(`results/issue286-the-fibre-formula.md`).

**Why it is false.**  Sum the formula over the six measured `P_0`-orbits on the
23715 liftable classes of `T_Co`:

$$
\sum_{i=1}^{6} \frac{|\mathcal{O}_i|\,m_i}{|P_0|}
= \frac{1}{|P_0|}\sum_{x\in X} |P_0 \cap \mathrm{Stab}_{O(q)}(x)|,
$$

where `X` is the `O(q)`-orbit of classes and the sum runs over its points.  The
orbit-counting identity -- Cauchy--Frobenius, *the number of orbits of a finite
group acting on a finite set is the average number of fixed points* (Burnside,
*Theory of Groups of Finite Order*, 2nd ed., **§119, printed p. 191**) -- gives

$$
\sum_{x\in X} |H_x| = |H|\cdot \#\{H\text{-orbits on }X\},
\qquad H = P_0,
$$

so the formula's total is exactly the **number of `P_0`-orbits on the classes**,
six, and *not* the number of `Gamma`-orbits of planes.  For `T_Co` that is
`6 != 7`: the row has seven.  The formula therefore computes a tautology -- a
sum that equals a class-orbit count whatever the plane stabilizers do -- and its
agreement at `U + U(2) + <-4>` (where class-orbits and plane orbits are both `2`)
was a coincidence of that specimen, not a verification.

## What the refutation explains

`7 - 6 = 1` is exactly the part the classes cannot see.  The double-coset space
`P_0 \ O(q) / rho(Pi_P)` is the true carrier of the `Gamma`-orbits
(`results/issue286-the-class-map-on-double-cosets.md`), and the map from it to
the class-orbits is not injective: one class-orbit carries two double cosets.
The formula replaced that map by the classes alone, which by Cauchy--Frobenius
can only count class-orbits.

This also retires last round's consequence: the claim that "four of the five
`k_i` are 1 and one is 2" used the total `7`, which the refutation shows the
formula cannot reach -- with the correct total `6` over six orbits the arithmetic
constrains nothing beyond `sum k_i = 6`.

## What stands

* The double-coset correspondence and the class map
  (`results/issue286-the-class-map-on-double-cosets.md`) are untouched: they
  never summed a fibre over the classes.
* `T_Co`'s six class-orbits of sizes `13440, 8192, 1680, 210, 192, 1` stand, as
  does the seven-plane row (`results/issue286-the-gamma-co-2-distribution-
  measured.md`).
* What is owed is unchanged and is now exactly stated: the fibre of the
  double-coset-to-class map at the one class-orbit that carries two, which is a
  property of `P_0 \ O(q) / rho(Pi_P)` and is read from the row's seven
  representatives.

No code changed; no red test.  The refutation is arithmetic plus Cauchy--Frobenius
at the cited page.
