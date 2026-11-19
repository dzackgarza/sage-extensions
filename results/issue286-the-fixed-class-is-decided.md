# The fixed class is decided: it carries exactly one orbit

**Lemma.** Let `L` be even, indefinite and nondegenerate `2`-elementary, so
`rho: O(L) -> O(A_L, q)` is onto (Nikulin, *Integral symmetric bilinear forms and
some of their applications*, Math. USSR-Izv. 14 (1980), pp. 103--167, Theorem
3.6.3), `J_0` an order-four totally isotropic subgroup, `P_0 = Stab_{O(q)}(J_0)`,
`Gamma = rho^{-1}(P_0)`.  If a liftable class `J_f` is fixed by `P_0`, then
`P_0 = Stab_{O(q)}(J_f)`, and consequently every plane `P` with `J_P = J_f`
satisfies `rho(Pi_P) <= P_0` and the class carries **exactly one** `Gamma`-orbit
of planes.

## Proof

`P_0 <= Stab(J_f)` is what "fixed" means.  Both are stabilizers of points of one
`O(q)`-orbit -- `J_0` and `J_f` are both liftable classes, hence both in the
`23715`-element orbit (`results/issue286-the-gamma-co-2-distribution-measured.md`)
-- so `|P_0| = |Stab(J_f)| = 1981808640`; a subgroup of finite index `1` is the
whole group, so `P_0 = Stab(J_f)`.

A plane's stabilizer image satisfies `rho(Pi_P) <= Stab_{O(q)}(J_P)` -- the
equivariance of the divided class under a lattice isometry, the content of
Dutour Sikirić--Hulek, arXiv:2302.01679v2, **Lemma 3.6, printed p. 22** -- so with
`J_P = J_f` we get `rho(Pi_P) <= Stab(J_f) = P_0`.  Last round's criterion
(`results/issue286-the-fixed-class-carries-one-coset-orbit.md`) then gives one
orbit.

## What this settles

The fixed class never doubles, and this is now **proved rather than tested**: it
needs no `IsSubgroup` call, because the two subgroups are equal by order.  So of
the seven plane orbits, one sits over the fixed class with fibre one, and the
remaining **six** sit over the five non-fixed class-orbits -- one of which carries
two (`results/issue286-the-six-partial-sums.md`).

That is the last point at which a lemma could speak: the five non-fixed orbits'
fibres are the coset computation `class_orbit_partial_sums` of
`results/issue286-the-partial-sums-need-a-method.md`, whose check is now sharper
-- five class-orbits carrying six orbits means the five fibres are
`2, 1, 1, 1, 1` in some order, with the two on the orbit carrying two.

## Note on the previous round

The previous round left the inclusion `rho(Pi_P) <= P_0` as "one `IsSubgroup`
call, the exact next check".  It is not needed: equal orders give it, and this
turn's proof replaces that planned computation.  Nothing was run; the claim is
arithmetic on two measured orders and the definition of "fixed".

No code changed, so no red test.
