# The fibre of the class map, in closed form

**Lemma.** Let `L` be even, indefinite, nondegenerate `2`-elementary, so
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3; the article's page range is what this repository cites and the theorem's
own printed page is not in front of me).  Let `J_0` be an order-four totally
isotropic subgroup, `P_0 = Stab_{O(q)}(J_0)`, `Gamma = rho^{-1}(P_0)`, `P` a
primitive isotropic plane with `J_P = [P/2]`, and `𝒪 = P_0·J_P` its `P_0`-orbit
inside the liftable family.  Then the number of `Gamma`-orbits of planes over
`𝒪` is

$$
\frac{|\mathcal{O}|\cdot[\mathrm{Stab}_{O(q)}(J_P) : \rho(\Pi_P)]}
     {[P_0 : P_0\cap \rho(\Pi_P)]},
$$

and in particular is `|𝒪|·|P_0 cap Stab(J_P)| / |P_0|` whenever
`rho(Pi_P) = Stab_{O(q)}(J_P)`.

## Proof

The right cosets of `rho(Pi_P)` lying over `𝒪` are those `g rho(Pi_P)` with
`gJ_P in 𝒪`; over one class `J` there are `[Stab(J) : rho(Pi_P)]` of them, since
`rho(Pi_P) <= Stab(J)` -- the plane's stabilizer image fixes the plane's class
(the equivariance of the divided class under a lattice isometry, Dutour
Sikirić--Hulek, arXiv:2302.01679v2, **Lemma 3.6, printed p. 22**).  So there are
`|𝒪|·[Stab(J) : rho(Pi_P)]` cosets to divide among the `Gamma`-orbits.

`P_0` acts on them by left multiplication, and the `Gamma`-orbits over `𝒪` are
exactly its orbits there (that is the double-coset correspondence of the same
lemma, proved in `results/issue286-the-class-map-on-double-cosets.md`).  The
orbit of `g rho(Pi_P)` has size `[P_0 : P_0 cap g rho(Pi_P) g^{-1}]`, and
`g rho(Pi_P) g^{-1} = rho(Pi_{gP})` is the image at another plane of the same
`O(L)`-orbit, so the denominator does not depend on `g`: the count is the
quotient above.

## Verified at the smallest case

`U + U(2) + <-4>`: `|O(q)| = 12`, `|P_0| = 4`, `rho(Pi_P) = Stab(J)` of order 4
at both planes (`.scratch/w286-probes/probe-fibrelem.log`):

| plane | `|𝒪|` | `|P_0 ∩ Stab(J)|` | `|P_0|` | formula | the row |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 2 | 4 | **1** | — |
| 1 | 1 | 4 | 4 | **1** | — |
| | | | | `1 + 1 = 2` | **2** |

So the row's two orbits are the formula's two, and the class counts alone
(`2` and `1`) would not have given them.

## What it settles for the last datum

On `T_Co` the datum "which of the six `P_0`-orbits carries two orbits" is now the
six numbers `|P_0 cap rho(Pi_P)|` -- one per orbit, each computable from a
representative plane's parabolic and the base point's stabilizer, with
`|P_0| = 1981808640` and the orbit sizes `13440, 8192, 1680, 210, 192, 1` already
measured.  The formula also says the whole row is `7 = sum_i |𝒪_i|·m_i/|P_0|`,
so the six `m_i` are constrained by a linear identity -- a check on any value
computed later, and a cheap one.

No code changed, so no red test this turn; the probe is the verification.
