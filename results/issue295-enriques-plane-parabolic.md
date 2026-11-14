# #295 — the parabolic at a primitive isotropic plane of $T_{\mathrm{En}}$, in this repository

## 1. Where the call stops

`T_En.Aut().stabilizer(P, action="setwise").group_generators()`, one process,
`PEAKRSS_LIMIT_MIB=6144`, `faulthandler.dump_traceback_later(120, repeat=True)`,
killed at 900 s with no generator returned
(`.tmp/issue295e-stack.log`). The dumps are not all the same frame, which is the
point: the computation is grinding, not blocked in one C routine.

```
[   0.2] stabilizer object
Timeout (0:02:00)!   File "sage/categories/category.py", line 463 in __classcall__
Timeout (0:04:00)!   <invalid frame>
Timeout (0:06:00)!   File ".../abstract_categories/objects.py", line ??? in __contains__
Timeout (0:10:00)!
  File ".../modules/module_morphisms/module_morphisms.py", line 1117 in _call_
  File ".../sets/set_categories.py", line 810 in __call__
  File ".../abstract_categories/mor_categories.py", line 1631 in __call__
  File ".../categories/lattice_morphisms.py", line 1549 in integral_restriction
  File ".../categories/lattices.py", line 3202 in integral_isometry
  File "/work/src/sage_indefinite_port/indefinite/isotropic_induction.py", line 304 in <genexpr>
  File "/work/src/sage_indefinite_port/indefinite/isotropic_induction.py", line 304 in _stabilizer_generators
  File "/work/src/sage_indefinite_port/indefinite/isotropic_induction.py", line 316 in plane_automorphism_generators
  File "/work/src/sage_indefinite_port/indefinite/marked_lattices.py", line 118 in automorphism_group_generators
  File ".../categories/lattices.py", line 1925 in _marked_automorphism_generators
  File ".../categories/lattice_morphisms.py", line 4093 in _marking_stabilizer_generators
  File ".../categories/lattice_morphisms.py", line 3760 in <lambda>
  File ".../categories/group/groups.py", line 1174 in selected_resolution
  File ".../categories/abstract_categories/objects.py", line 116 in realize
  File ".../categories/abstract_categories/objects.py", line 383 in selected_resolution
  File ".../categories/group/groups.py", line 5639 in selected_group_resolution
  File ".../categories/group/groups.py", line 5661 in group_generators
  File "/probe.py", line 29 in <module>
```

So the part that does not finish is **the port's conversion of each rational
generator of its integral-structure action into an integral isometry**:
`plane_automorphism_generators` → `_stabilizer_generators` maps
`lattice.integral_isometry(...)` over the action's generator family
(`isotropic_induction.py:304`), and each map calls
`LatticeIsometryMor.integral_restriction`, which evaluates the rational isometry
on all twelve generators inside the repo's morphism machinery. `isotropic_stabilizer_action`
itself, the reduction, and the orbit computation are not the wall; one
conversion, and then the next, is.

This is not a port edit: the port is paused. The repair is that this repository
answers the question itself (section 2), and the dispatch in
`Lattices.ParentMethods._marked_automorphism_generators` prefers its answer for
a plane marking of an indefinite **even** lattice.

## 2. The construction

`PrimitiveIsotropicSubobjects.parabolic_stabilizer_generators()`
(`src/sage_extensions/categories/isotropic_parabolics.py`) is the union of three
families, one per factor of the parabolic's published block decomposition:

| factor | construction | where |
| --- | --- | --- |
| unipotent radical $U_I$ | the Eichler transvections $t(p,x)$ for $p$ in the plane's basis and $x$ in a $\mathbb{Z}$-basis of $p^\perp$ | `unipotent_radical_generators` |
| Levi on $P^\perp/P$ | the reflections in the root shells of the definite quotient $K=P^\perp/P$, lifted into $P^\perp$ through the isotropic reduction's frame | `quotient_reflection_generators` |
| Levi on $P$ | the integral lifts of the elementary matrices of $GL_2(\mathbb{Z})$, by the block equation $g|_P J g|_U^t = J$ with $J=(b(p_i,u_j))$ | `levi_lift_generators` |

**The block form.** An isometry preserving a primitive isotropic plane $P$
satisfies $g(P)\subseteq P$ and $g(P^\perp)\subseteq P^\perp$, so in the basis
$(U \mid P \mid K)$, $U$ a complement of $P^\perp$ and $K$ a frame of
$P^\perp/P$, it is

$$g=\begin{pmatrix} g_{11} & 0 & 0\\ g_{21} & g_{22} & g_{23}\\ g_{31} & 0 & g_{33}\end{pmatrix},\qquad
J = g_{11}^t J g_{22},\quad g_{33}^t A g_{33} = A,$$

with $g_{22}$ the Levi action on $P$, $g_{33}$ the Levi action on $K$, and
$g_{23}, g_{31}, g_{11}, g_{21}$ the unipotent blocks. This is Dutour Sikirić and
Hulek, *Moduli of polarised Enriques surfaces — computational aspects*,
J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, §"The Tits building",
Theorem `theorem_isotropic_k_planes` (printed p. 22), read in the arXiv source
`Enriques_compu_rev.tex` of that version: their `P` has the block matrix with
blocks `P_1, P_2, P_3; Q_1, Q_2, Q_3` and the equations `J = P_1 J Q_1^T`,
`K = P_1 J Q_2^T + P_1 K Q_3^T + P_3 A Q_3^T`, and they state their convention
explicitly — "we use the action on row vectors from the right". This module uses
column vectors, so their `P_1 J Q_1^T` reads $g|_P J g|_U^t$ here; the same
statement is quoted in the docstring of `levi_lift_generators`.

**The radical.** For isotropic $p$ and $x \in p^\perp$,

$$t(p,x)(y) = y - b(x,y)\,p + b(p,y)\,x - \tfrac12 q(x)\,b(p,y)\,p$$

(Gritsenko–Hulek–Sankaran, arXiv:0810.1614, §3.1, (4)–(5), already transcribed
by this repository in `Lattices.ParentMethods.eichler_transvection`, which cites
Dawes §2 (7)) is an integral isometry of an **even** lattice, fixes $p$, and
sends $k \in P^\perp$ to $k - b(x,k)p \in k + P$; so it lies in the radical. The
family is the one Eichler's criterion takes, one parameter per basis vector of
$p^\perp$: Dutour Sikirić–Hulek, arXiv:2302.01679v2, subsection "Approximate
models and the case of signature $p,q\geq 2$", Lemma `sublattice_approx_model`,
which cites Eichler's criterion and Scattone, Ph.D. thesis, §3.7,
Proposition 3.7.3 — "we simply need the generators of $\mathrm{SL}_2(\mathbb{Z})^2$
and the transvections $E_{e_i,v_{i,j}}$ with $(v_{i,j})$ a $\mathbb{Z}$-basis of
$e_i^\perp$". Its printed page is 22 in the JLMS printing cited by card `029J`;
the arXiv text was the copy read.

**Why the three families are the whole parabolic when the lattice splits.** If
$L = P \perp U \perp K$ with $(P,U)$ an orthogonal summand and $K = P^\perp/P$,
then (i) the radical is generated by the transvections, (ii) the image in
$O(K)$ is generated by the reflections of $K$'s shells when $K$ is definite and
generated by its root system, and (iii) the image in $GL(P)$ is the subgroup of
$M \in GL_2(\mathbb{Z})$ with $J M^{-1} J^{-1}$ integral, which for
$J = \mathrm{diag}(1,2)$ is $\Gamma^0(2) = \{b \text{ even}\}$, generated by
$\begin{pmatrix}1&0\\1&1\end{pmatrix}$, $\begin{pmatrix}1&2\\0&1\end{pmatrix}$
and $\pm 1$; an isometry then differs from the lift of its own $(g|_P, g|_K)$ by
an element of the radical. `is_parabolic_complete` is that hypothesis, decided
by the vanishing of the pairing of the complement with the frame of $K$.

**Where it is not the whole parabolic.** $T_{\mathrm{En}}$ at Sterk's *second*
representative $P_2 = \mathbb{Z}(2e_1+2e_2+w)+\mathbb{Z}e_3$ does not split —
its complement pairs nontrivially with $K$, `is_parabolic_complete()` is False,
`levi_lift_generators` returns nothing, and the public call keeps the port's
route for it. That is a real limit of this unit and it is recorded as such: the
acceptance item is "a primitive isotropic plane", and it is $P_1$ that returns.
The plane rows of #316/#321 are unaffected: both representatives there are
closed, $P_1$ by these generators and $P_2$ by the published indices.

## 3. What the public call returns on $T_{\mathrm{En}}$ at $P_1$

```
T_En.Aut().stabilizer(P1, action="setwise").group_generators()
  unipotent radical      20 generators   1.5 s
  Levi on P^perp/P      120 generators  32 s   (one shell of 240 vectors, +-paired)
  Levi on P              12 generators
  total                 152 generators  34 s
  isometries of T_En    152 of 152
  discriminant images   rho on all 152 in 15.4 s
```

The 120 reflections come from the single shell of $K = E_8(-4)$ (the catalogue's
doubling of $E_8(-2)$): 240 vectors, $w$ and $-w$ giving one reflection each.
Their images in $O(K)$ generate $W(E_8) = O(E_8)$, the whole Levi factor
there: the reflection group *is* the orthogonal group of $E_8$, because $-1$
is its longest element, so no sign class is divided out.

Measured against the discriminant image, these families are not the whole
parabolic: the reflections' images generate a subgroup of index
$134912 = 527 \cdot 256$ in $Q = \rho(O(T_{\mathrm{En}}))$ (order
$46998591897600$), while the radical and the Levi-on-$P$ lifts have trivial
image and the divided class set of $P_1$ has a $Q$-orbit of $527$ points.
The plane index therefore does not close from these generators;
`results/issue325-plane-index.md` records the measurements.

## 4. Evidence

Committed and pushed as `58a6d50`, `c20a05d`, `093a106` on `main`
(`git ls-remote` → `refs/heads/main = 093a1063cabcf5d594f2bb2bc8cb88e6e1344c09`).

* red, before the construction: the test module at `d2cb8bd` (test, digest and
  reader only, in a worktree at that commit) — `pytest exit: 124`, no result
  inside a 240 s cap (`.tmp/issue295-red-enriques-plane.log`).
* green: the module as pushed, `1 passed` in 76 s
  (`.tmp/issue295-gate-pushed2.log`).
* the stack: `.tmp/issue295e-stack.log`.
* the construction probe (generator counts, isometry and plane checks, `rho`):
  `.tmp/issue295k-closure.log`.

### The index certificate is not in this unit

Feeding the generators to `O(T_En).isotropic_plane_orbits(...,
stabilizer_generators={0: ...})` never reaches the sandwich: the call realizes
each orbit through the port's right-coset transversal and raises
`TypeError: int() argument must be a string, a bytes-like object or a real
number, not 'OwnedJoinCategory.element_class'` at
`sage_indefinite_port/indefinite/recursive.py:154`, via
`eichler.py:488 right_coset_transversal -> eichler.py:464
stabilizer_of_lattice`.  That is port code and the port is paused, so the test
asserts the generators' own properties and records the obstruction in its
docstring; the index it would have compared is card `029J`'s Otilde+ row, read
by tag through `sage_extensions.lattice_database.card_plane_orbit_row`, whose
citation gives `527` and `23715` in `rho(O(T_En))` (Dutour Sikirić--Hulek,
§3.6, p. 22).

### The module gate's other failures are pre-existing

Five modules, 14 tests: `10 failed, 4 passed in 143 s`.  Every failure is that
same port `TypeError`, in the orbit-realisation path.  Baselined at the fetched
remote head without these commits: `test_unpolarized_enriques_strata` (both
tests) and
`test_setwise_stabilizer_discriminant_images::test_the_divided_class_plane_call_...`
fail there identically, and the Coble discriminant-image test passes both there
and here (`.tmp/issue295-baseline.log`).  The other seven failures lie in modules
that were not baselined, so that part rests on the error being the same one.
