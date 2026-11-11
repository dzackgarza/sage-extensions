# #331 — ρ(G_{P}) decided by computed orders, at Sterk's two planes of T_En

$T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$, $P_1 = \mathbb{Z}e_1 + \mathbb{Z}e_3$,
$P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3$ with $q(w) = -8$ (H. Sterk, Math. Z. 207
(1991), Proposition 4.6, p. 29).

## The two subgroups

* Upper.  For $g \in \mathrm{Stab}_{O(L)}(P)$ the divided discriminant classes
  $[u/\mathrm{div}(u)]$ of the plane's primitive directions are permuted by $\rho(g)$, so
  $\rho(G_P) \subseteq \mathrm{Stab}_{O(q)}(D(P))$, and
  $|\mathrm{Stab}_{O(q)}(D(P))| = |O(q)| / |O(q)\cdot D(P)|$.
* Lower.  The images of the generators `parabolic_stabilizer_generators` returns.

Both computed from the permutation action of $O(q)$ on its own 1024-element discriminant
group, built from $O(q)$'s four generators (GAP; the permutation group's order is checked
against $O(q)$'s own).

```
|O(q_{T_En})|                       46998591897600
orbit of D(P1) under O(q)                527        |Stab_{O(q)}(D(P1))| =  89181388800
orbit of D(P2) under O(q)              23715        |Stab_{O(q)}(D(P2))| =   1981808640
```

$527 = 17\cdot31$ and $23715 = 3^2\cdot5\cdot17\cdot31$ are the indices Dutour
Sikirić--Hulek, arXiv:2302.01679v2, section 3.6 (the Tits building), p. 22, give for the
stabilizer images of $P_1$ and $P_2$; $527 + 23715 = 24242$ is card `029J`'s
$\widetilde{O}^+$ plane row, read by tag.  The bound at $P_1$, 89181388800, is also the
order #325 measures for `Stab_Q(D(P1))` in the finite group.

## The lower side on this tree, and what closes it

```
returned family at P2 (103 generators: radical + quotient reflections + 18 lifts)
  |<rho(generators)>| =        483840    index in the bound = 4096 = 2^12
```

So the plane lifts of #326 do not fill the bound: the image is short by $2^{12}$.

With #325's half-vector Eichler transvections among the generators (their commit
`1f2fa77`, not on `main` when this was measured; `half_vector_transvection_generators`,
the transvections $E_{e,w}$ for $w \in L^{\#}$, $2w \in L$, $b(e,w) = 0$ — Dawes,
section 2 equation (7); Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
equations (4)--(5); Scattone, Mem. AMS 374, section 3.7, Proposition 3.7.3), the family
has 120 generators and

```
|<rho(generators)>| =  1981808640 = |Stab_{O(q)}(D(P2))|     exact, index 1
```

which is the equality `stabilizer_discriminant_image_is_exact()` reports.  At $P_1$ the
same commit's measurement is 89181388800 against this bound, index 527.

## What this decides, and what it does not

$\rho(G_{P_2}) = \mathrm{Stab}_{O(q)}(D(P_2))$ of order 1981808640 follows *once the
half-vector transvections are in the family*, without any generation claim for $G_{P_2}$
itself; the generation statement of #331 stays open and `parabolic_obstruction()` still
names it.  Index of $\rho(G_{P_2})$ in $O(q)$: **23715**, card `029J`'s cited value for
$P_2$; for $P_1$: 527.

## Evidence

```
tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage   1 passed in 34.78s
  the two bound indices 527 and 23715, their sum against card 029J's Otilde+ row (24242),
  and card 029J's O row (2), all read by tag.
```

Run with `--no-time-gates` (shared VM; the session star import has measured 3.1 s against
the recorded 3 s ceiling) and `-o addopts= -p qc_sage_session -p suite_budget -p test_lint`.
