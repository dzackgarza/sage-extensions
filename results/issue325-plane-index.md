# #325 — the plane index of $T_{\mathrm{En}}$, measured

Stage 1 under #280; the plane half of #286. This note records what the two
routes into `isotropic_plane_orbits` do on
$T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$, what the issue's recorded
`TypeError` actually was, and what blocks the acceptance. Numbers below are
measurements, not card values, except where a row of
`dzackgarza/lattice-database` is named by its tag. Measured on `1756b91` unless a
paragraph says otherwise.

## 1. The recorded `TypeError` is the image's baked-in port, not the pinned one

The issue, and `tests/lattices/test_setwise_stabilizer_of_an_enriques_plane.sage`,
record

```
TypeError: int() argument must be a string, a bytes-like object or a real number,
           not 'OwnedJoinCategory.element_class'
  eichler.py:488 right_coset_transversal -> eichler.py:464 stabilizer_of_lattice
  -> recursive.py:154  source_coordinates = tuple(int(coordinates(label)) for label in source_labels)
```

At the pinned port, `991b88b095a42a1e3679569ea42328c900c120f6`, that statement is
`source_coordinates = tuple(_integer(coordinates(label)) for label in
source_labels)` — `recursive.py:163`, not `154`.  Port commit `ab140b70`
("read integral coordinates through the field when a lattice is rational",
2026-11-01, an ancestor of the pin) replaced the bare `int` with
`edgewalk_scalars._integer` at exactly the four coordinate crossings the frame
names: `_column_matrix`, `_isometry_from_row_matrix`,
`_isometry_from_column_matrix` and `eichler._pullback_envelope_vector`.  Its own
message states the defect and its cause: "a lattice over ZZ states a coordinate
as its ring's own element and `int` reads it; a lattice over QQ states a
rational that does not admit `int`.  The failing path is `eichler.py:464`
handing the integer row-matrix boundary a rational envelope."

The text `int(coordinates(label))` at line 154 is the *runtime image's own* port,
baked in at `/repos/sage-indefinite-port` (`4f0ee50c`, 2026-11-01), which a
launcher that does not bind the port path reaches through the
`__editable__.sage_indefinite_port` entry on `sys.path`.  `.scratch/port`, the
checkout of 2026-10-31 (`61ac45a0`), carries the same line at 154.

Two runs of one probe, differing only in the port binding, settle it
(`.tmp/issue325-port-pinned.log`, `.tmp/issue325-port-baked.log`):

| call | pinned port `991b88b0` | image's port `4f0ee50c` |
| --- | --- | --- |
| `envelope.right_coset_transversal()` | 9 representatives, 12.86 s | `TypeError` at `recursive.py:154` |
| `recursive._isometry_from_row_matrix(L, L, identity)` | returns | returns |
| `eichler._isometry_from_row_matrix(L, identity)` | returns | returns |
| `EichlerRecursion().orthogonal_group_generators(T_En)` | 202 generators, 73 s | — |
| `O(T_En).group_generators()` (public) | 199 generators, 115 s | — |
| `O(T_En).isotropic_orbit_representatives(2)` (public) | 2, 67 s | — |

The baked run reproduces the recorded frame for frame.  So the port is not the
owner of this issue, and the recorded stack is a setup error of the launcher
that produced it, not a defect of the pin.

The `int`-on-owned-rational conversion is still a real property of this
repository: the owned rational element class does not admit `int`, and the
pinned port copes at its four crossings rather than the type being convertible.
That is a defect of the element class and is recorded here as one; it does not
block anything below, because the pinned port no longer asks.

## 2. The supplied-stabilizer route refuses, and why

`O(T_En)` here is the predicate subgroup $\rho^{-1}(\rho(O(L)))$ of `O(T_En)`:
`isotropic_plane_orbits` is an operation of the character-kernel subgroups, not
of the isometry Mor.

```
group.isotropic_plane_orbits((P1,), stabilizer_generators={0: family})
ValueError: ... the supplied generators generate a subgroup of index 134912 in
            rho(O(T_En)), while the orbit of the plane's divided classes has 527 points
```

`family` is `T_En.Aut().stabilizer(P1, action="setwise").group_generators()`,
which is `parabolic_stabilizer_generators()`: 150 generators on this tree (the
20 radical transvections, 120 lifted reflections and 12 Levi lifts, two of them
the identity).  That call costs 493 s on `1756b91`.

One family at a time against $Q = \rho(O(T_{\mathrm{En}}))$, order
$46998591897600$:

| family | generators | order of the generated image | index in $Q$ |
| --- | --- | --- | --- |
| `unipotent_radical_generators` | 20 | 1 | 46998591897600 |
| `quotient_reflection_generators` | 120 | 348364800 | 134912 = 527 · 256 |
| `levi_lift_generators` | 12 | 1 | 46998591897600 |
| all three | 150 | 348364800 | 134912 |

and the divided class set of $P_1$ has a $Q$-orbit of $527$ points, with
$|\mathrm{Stab}_Q(J_{P_1})| = 89181388800$ — index $527$.

An independent computation agrees on all 152 generators of the pre-filter
family: with the dual basis $G^{-1}$ and a class read off the fractional
coordinates of $L^\#/L$, the radical transvections and the Levi lifts move no
class, and all 120 reflections move classes.  So the trivial image of the
radical is not a conversion artifact: those generators fix $A_L$ because every
shift they induce is integral on $L^\#$ — for $p = e_1$, of divisibility one,
$b(p, u)$ is already an integer on $L^\#$; for $p = e_3$, of divisibility two,
$b(p, u) = \frac12$ would force $b(u, e_3) \notin \mathbb{Z}$, and no such
$u \in L^\#$ exists.

**The gap.** $[Q : \rho(G_{P_1})] = 527$ is the published index (D. Dutour
Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces — computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, §3.6 "The Tits
building", p. 22), and $527$ is also the size of the $Q$-orbit of the plane's
divided classes; the two agree, which is what the sandwich needs.  The family
generates a subgroup of index $134912 = 527 \cdot 256$, so it is **short of
$\rho(G_{P_1})$ by $256 = 2^8 = |A_{E_8(-2)}|$**: the three families are not a
generating set of $P_{P_1}$, and #295's module asserts their individual
properties, never that they generate.

The names in the family cannot close that gap: an Eichler transvection
$t(p, x)$ with $x \in p^\perp \cap L$ moves $L^\#$ by $b(p,u)x - b(x,u)p$ with
both coefficients integral, and an integral lift of a matrix on $P_1$ that
preserves the plane preserves the two classes $[e_3/2]$, $[e_4/2]$ of
$A_{U(2)}$.  The missing $2^8$ therefore lives in elements of $P_{P_1}$ that mix
the $E_8(-2)$ and $U(2)$ components of $A_L$; constructing them integrally is
the open step, and it is not a repair inside this call.

## 2b. The exact index, and the missing $2^8$ named

`stabilizer_discriminant_image()` was the candidate for computing
$\rho(G_{P_1})$ outright, on the strength of research#750
`thm:schreier-discriminant-image` (`writing/coble/computations/discriminant-form-descent.md`).
That theorem's hypotheses, read at the page and at
`def:stabilizer-congruence-data`:

1. $V$ finite dimensional over $\mathbb{Q}$ with a nondegenerate symmetric form $\beta$;
2. $L \subseteq V$ an integral nondegenerate lattice;
3. $M \subseteq V$ finitely generated and full with $L \subseteq M$, and $G \leq O(V)$ with $GM = M$;
4. $m \geq 1$ with $mM \subseteq L$ (or $mM \subseteq e_2L$, by `cor:stabilizer-modulus`);
5. $S \subseteq G$ finite and symmetric with $G = \langle S \rangle$;

and its conclusion is $\rho_L(\operatorname{Stab}_G(L)) = \langle \rho_L(k_{s,p}) \rangle$
over the Schreier elements $k_{s,p} = t_{sp}^{-1} s t_p$.

**It does not cover a rank-2 isotropic sublattice as stated, and the rank is not
what fails.**  The theorem's data contain no isotropic subspace: it computes the
stabilizer of a *lattice*.  Applying it to $P_1$ requires $G$ = the rational
stabilizer of $P_1$ in $O(V)$ and $L = T_{\mathrm{En}}$, so that
$\operatorname{Stab}_G(L) = \operatorname{Stab}_{O(T_{\mathrm{En}})}(P_1)$; then
(1)–(4) hold, and the hypothesis that fails is (5): a finite symmetric $S$ with
$G = \langle S \rangle$ **exactly**.  `isotropic_stabilizer_action` supplies the
approximate family $A_E$ together with the $GL(I)$-radical images, and nothing in
this tree exhibits that family as a generating set of the whole rational plane
stabilizer; a subgroup where the theorem needs $G$ returns a subgroup of the
wanted image.  Measured: the call had not returned on $T_{\mathrm{En}}$ after
11.3 min even for the rank-one line $\langle e_1 \rangle$
(`.tmp/issue325-exact-image.log`), against 30.4 s on $T_{\mathrm{Co}}$, so it is
not the closure for this issue either.

**What settles the index is a theorem, and it is on the page.**
`thm:enriques-integral-plane-stabilizers`
(`writing/coble/lattices-and-moduli/lattices.md:454`), proved, states
$$\rho\bigl(\operatorname{Stab}_{O(T_{\mathrm{En}})}(\varPi)\bigr) =
\operatorname{Stab}_{O(A,q)}\bigl(D(\varPi)\bigr)$$
for **every** primitive totally isotropic plane $\varPi$.  For $P_1$ it is
`lem:ten-base-stabilizers`, which computes $|F_1| = 89\,181\,388\,800$; for
$P_2$ the proof of the plane theorem computes $|F| = 1\,981\,808\,640 =
6 \cdot 40\,320 \cdot 2^{13}$, and $|Q|/23\,715 = 1\,981\,808\,640$.  So the
index per class is $527$ and $23\,715$ — card `029J`'s two plane indices — and
their sum is the card's `Otilde+` row, $24\,242$.

**The missing factor has a name.**  `lem:half-vector-eichler` gives, for a
primitive isotropic $\eta$ of divisibility two and $w \in T_{\mathrm{En}}^\#$,
the Eichler transvection $E_{\eta,w}$: it is integral, fixes $\eta$, preserves
every primitive isotropic plane through $\eta$, and its discriminant image is
$T_{d,[w]}$; these form a subgroup $U_d$ of order $2^8$
(`lem:half-vector-eichler`(3)).  The proof of `lem:ten-base-stabilizers` gets
$\rho(\operatorname{Stab}(P_1)) = L \cdot U_{d_1}$ with
$|L| = 348\,364\,800$ and $|U_{d_1}| = 2^8$, product $89\,181\,388\,800$.  The
family this repository builds is exactly $L$: its reflection image has order
$348\,364\,800$, and the $2^8$ it misses is $U_{d_1}$ — the images of the
transvections along a *half* lattice vector, $w \in T_{\mathrm{En}}^\#$, which no
integral-parameter transvection and no plane-preserving lift produces.

## 2c. The repair: the half-vector transvections

The obstruction of §2b is the transvection along a vector of the metric dual
that is not a lattice vector, and it is now in the family.

*Construction.*  For a primitive isotropic `e` of divisibility two and
`w ∈ L^#` with `b(e,w) = 0`, `2w ∈ L` and `q(w) ∈ Z`,

$$E_{e,w}(x) = x - b(w,x)e + b(e,x)w - \tfrac12 q(w)b(e,x)e,$$

the Eichler transvection formula — Dawes, section 2 equation (7), the
transcription `Lattices.ParentMethods.eichler_transvection` already carries for
`w ∈ L`; Gritsenko–Hulek–Sankaran, *The desingularization of the moduli space of
Enriques surfaces*, arXiv:0810.1614, section 3.1, equations (4)–(5); and
Scattone, *On the compactification of moduli spaces for algebraic K3 surfaces*,
Mem. Amer. Math. Soc. 374 (1987), section 3.7, Proposition 3.7.3, whose criterion
generates the radical of the parabolic at an isotropic sublattice by the
transvections over a basis of `e^⊥`.  With those hypotheses every coefficient is
an integer: `b(w,x) ∈ Z` because `2w ∈ L` and `L` is even, `q(w)/2 · b(e,x) ∈ Z`
because `q(w) ∈ Z` and `b(e,x) ∈ 2Z`, and `b(e,x)w ∈ L` because `b(e,x)` is even
and `2w ∈ L`.

*Owner.*  `Lattices.ParentMethods.half_vector_transvection_parameters` decides
the hypotheses on the dual basis and
`…eichler_transvection_half_vector` builds the isometry, asserting integrality of
every image before it constructs it;
`PrimitiveIsotropicSubobjects.half_vector_transvection_generators` collects them
for the plane, and `parabolic_stabilizer_generators` includes them beside the
radical, the reflected Levi factor and the plane lifts.  The plane-lift code
(`plane_block_lift`, `levi_lift_generators`) is untouched.

*The checks, on `T_En` at `P_1`.*  The metric dual's 12 basis vectors give 10
generators: one is excluded because `b(e,w) ≠ 0`, one gives the identity.  Each
is integral (constructed in `Aut(L)`), an isometry of `T_En` on the full Gram
matrix, and carries `P_1` onto itself —
`True / True / True` in `.tmp/issue325-halfvector.log`.

*Exactness by computation.*  In `O(A_L)`:

| family | order of the image | index in `Q` |
| --- | --- | --- |
| radical + reflections + plane lifts | 348 364 800 | 134 912 |
| half-vector transvections alone | 256 | 183 588 249 600 |
| all four | **89 181 388 800** | **527** |
| `Stab_Q(D(P_1))` (finite-group stabilizer) | **89 181 388 800** | **527** |

The last two orders are equal, and that equality — `ρ(G_{P_1})` against the
finite stabilizer both computed here — is the exactness, with no page used as
evidence.  The half-vector family alone is the `2^8` of §2b.

## 3. What returns today

* `O(T_En).isotropic_plane_orbits((P1, P2))` — the published-index route —
  returns `2` orbits, and `2` is card `029J`'s `O` row read by tag through
  `card_plane_orbit_row`.
* `O(T_En).isotropic_plane_orbits((P1,), stabilizer_generators={0: family})` —
  the #325 acceptance — **returns** since the half-vector transvections joined
  the family: the call closes the sandwich at `[Q : ρ(G_{P_1})] = 527 =
  |Q · J_{P_1}|`, and it raises rather than returning if the two indices differ.

`tests/lattices/test_the_enriques_plane_index_returns.sage`: `2 passed in
186.52 s` (`.tmp/issue325-green.log`); before the repair, the same module was
`1 failed, 1 passed` with the index `134912` of §2.

## 4. The five plane-orbit modules

On `1756b91` with the pinned port:

```
tests/lattices/test_unpolarized_enriques_strata.sage
tests/lattices/test_setwise_stabilizer_discriminant_images.sage
tests/lattices/test_enriques_anti_invariant_cusps.sage
tests/lattices/test_stable_isotropic_plane_orbits.sage
tests/lattices/test_enriques_plane_orbits_by_divided_classes.sage
  16 passed in 390.09 s, exit 0    (.tmp/issue325-five-modules-upstream.log)
```

All sixteen pass.  The `TypeError` that the issue records for ten of their
fourteen tests does not appear, and neither does any failure in the
orbit-realisation path.  Two of them were failing for a real reason on `3cf3e570`, where these
were measured first — on $U \oplus U(2)$ the plane is maximal isotropic, so
$P^\perp = P$, $K = P^\perp/P$ is the *zero* lattice and the Levi factor on it
is $O(0) = 1$; `quotient_reflection_generators` asked the zero lattice for its
shortest vector and raised `ValueError: the zero lattice has no nonzero vector
and no minimum` before reaching the guard written for a shell-less quotient
(`1 failed, 15 passed in 321.07 s`, `.tmp/issue325-five-modules.log`).  That
guard is on `main` already: `093a106` returns the empty family for $K = 0$, so
this unit carries no source change for it.

## 5. The $W(E_8)$ sentence

`results/issue295-enriques-plane-parabolic.md` said the 120 reflections' images
generate $W(E_8) = O(E_8)/\{\pm 1\}$.  It is $W(E_8) = O(E_8)$: $-1$ is the
longest element of the reflection group, so nothing is divided out.  The
sentence is corrected in that report and in the docstring of
`quotient_reflection_generators`, where the same sentence stood, with the
measurement of §2 beside it.

## 6. Where #325 stands

The issue's premise is refuted and its acceptance is not met.  The `TypeError` is
a stale-port setup error; the port at its pin answers every call in the recorded
stack.  The plane index on $T_{\mathrm{En}}$ does not return from the supplied
stabilizer generators because those generators are short of
$\rho(G_{P_1})$ by $256$, so the sandwich stays open at
$527 \le [Q : \rho(G_x)] \le 134912$ and the call refuses rather than returning
an unestablished count.  Completing the family is the next unit; #326 (Sterk's
non-split $P_2$) is untouched.
