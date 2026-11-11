# #326 — the parabolic at a plane of $T_{\mathrm{En}}$ that does not split

Sterk's two representatives of the primitive isotropic planes of
$T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$ are $P_1 = \mathbb{Z}e_1 + \mathbb{Z}e_3$
and $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3$ (H. Sterk, Math. Z. 207 (1991),
Proposition 4.6, p. 29).  $P_1$ splits off the lattice; $P_2$ does not — no complement
of $P_2^\perp$ is orthogonal to $P_2^\perp/P_2$, so `splitting_complement()` answers
`None`.

## Where the call stopped

On the fetched main (`1756b91`), with the new test added there unchanged:

```
FAILED tests/lattices/test_the_stabilizer_of_a_non_split_enriques_plane.sage::test_the_plane_that_does_not_split_has_integral_levi_lifts
E       assert () != ()
1 failed, 1 passed in 29.30s
```

`levi_lift_generators()` returned nothing whenever the plane did not split, so
`parabolic_stabilizer_generators()` was the radical and the quotient reflections only
and `Lattices._isotropic_plane_parabolic_generators` returned `None`, handing the
public call to the indefinite port's rank-two route — which on the recorded runs of
#295 did not return inside the caps (`results/issue295-enriques-plane-parabolic.md`).
On this tree that port route *does* return (27.76 s, checks passing), which is why the
red is the repository's own construction and not the public call.

## The construction

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, **Theorem 4.9**
(`theorem_isotropic_k_planes`), proof, printed **p. 22**, read in the arXiv source
`Enriques_compu_rev.tex` of that version.  In a basis $(U \mid P \mid K)$ — $U$ a
$\mathbb{Z}$-complement of $P^\perp$, $K$ a completion of the plane to a $\mathbb{Z}$-basis
of $P^\perp$ — an isometry preserving $P$ has the block form

$$g = \begin{pmatrix} P_1 & P_2 & P_3\\ 0 & Q_1 & 0\\ 0 & Q_2 & Q_3\end{pmatrix},
\qquad J = P_1 J Q_1^t,\quad K = P_1 J Q_2^t + P_1 K Q_3^t + P_3 A Q_3^t,$$

with the third equation the linear system (Equa_P2) for $P_2$, "which obviously has a
solution", its kernel of dimension $k(k-1)/2$.  Their $K = b(U, K)$ block is what
vanishes only for a splitting plane: the split case is $P_3 = 0$, and at $P_2$ it is
not.

`plane_block_basis` builds that basis without asking $U$ to be orthogonal to $K$;
`plane_block_gram` returns $(H, J, K, A)$; `plane_block_lift(action)` solves the three
equations over the integers for a given plane action and returns the isometry, or
`None` when the integrality fails for every parameter of the one-dimensional kernel;
`levi_lift_generators` runs it over the elementary matrices of $GL_2(\mathbb{Z})$ and
keeps the ones that come out.

The paper's own caveat is the reason a search is the construction: an extension is
rational for every isometry of $P^\perp$ but integral only on a finite-index subgroup —
"we could not find a universal construction of such a lattice.  However, in all the
cases we considered, a practical algorithm allowed us to solve this problem".

## Measured on $T_{\mathrm{En}}$

```
P1 (split):     det J 2, K block zero      13 integral lifts   (all isometries)
P2 (non-split): det J 4, K block nonzero   18 integral lifts   (all isometries)
```

With the radical and the quotient reflections: $P_1$ has $20 + 120 + 13 = 153$
generators, $P_2$ has $21 + 64 + 18 = 103$, which is the family the public call returns.

## Tests

```
tests/lattices/test_the_stabilizer_of_a_non_split_enriques_plane.sage   3 passed in 110.58s
  test_the_plane_that_does_not_split_has_integral_levi_lifts        4.32 s
  test_the_setwise_stabilizer_of_the_plane_that_does_not_split_has_generators  59.24 s
tests/lattices/test_setwise_stabilizer_of_an_enriques_plane.sage        46.56 s   (#295, P1, unchanged)
```

Run with `--no-time-gates`: the shared VM measured 3.12 s for the session star import
against the recorded 3 s ceiling, and the two plane calls here are minutes, like the
$P_1$ test of #295.  The new test asserts no count and no index of its own
computation; it names Theorem 4.9 and its printed page.

The port is paused and was not edited.
