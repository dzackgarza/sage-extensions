# #603: certified generators of a primitive vector's stabilizer, item by item

Second round, after the reviewer's findings on `41f21a69`.  The issue asks for a
public call that returns, for **every** primitive vector `v` of an indefinite
lattice `L`, generators of `Stab_{O(L)}(v)` built by the library's own
construction, with a proof that the family generates the stabilizer, and for a
card comparison.  Numbers are from runs on the adopted runtime in a worktree of
`main = a6f2dfe` (tree bound at `/repos/sage-extensions`, the port at `/work`,
time gates on).

## 1. What changed in this round

**The generation argument was false, and is replaced.**  `b580e31` paired the
reversing members of the parabolic's family (`g_0 g`) and claimed
`g_1 g_2 = (g_1 g_0)(g_0 g_0)(g_0 g_2)`.  That product is `g_1 g_0^4 g_2`, and
the pairing drops the conjugates `a^{-1} t a` of the members that already fix
`v`.  The reviewer's counterexample: in `S_4` with `f = (12)(34)` even and
`r = (02)` odd, `ker(sgn)` in `\langle f, r\rangle` has order six while `f` and
`r^2 = 1` generate two.  The family is now **Schreier's**, for the two cosets of
the kernel with transversal `{1, a}`: the words `w_{tP}^{-1} t w_P` over the
symmetric generator family.  Each fixes the coset it is applied to, and they
generate the kernel -- every kernel element is a word in the generators and the
correction `w_{tP}^{-1} t w_P` is what keeps a running product in the coset it
has reached.  That argument is in the method's docstring.

**The non-isotropic primitive vector is now owned.**  With
`K = v^\perp \cap L` of rank `n-1` and `L_0 = Zv \perp K` of finite index in
`L`, an isometry of `K` extends to `L` fixing `v` exactly when it preserves the
gluing subgroup `H = L/L_0` of `A_{L_0}`: overlattices of `L_0` correspond
bijectively to the isotropic subgroups of `A_{L_0}` (Nikulin, *Integral
symmetric bilinear forms and some of their applications*, Math. USSR Izv. 14
(1980), Proposition 1.4.1).  So

    Stab_{O(L)}(v) = { sigma in O(K) : (1 + sigma)(H) = H },

which is the stabilizer of a point under the action of `O(K)` on the finite set
of subgroups of `A_{L_0}`, and the same Schreier family over the orbit of `H`
generates it.  The classes are integer tuples from the Smith form of `L_0`'s Gram
matrix, the orbit and the words are exact integer arithmetic, and the extension
of `sigma` is `x |-> (b(x,v)/b(v,v)) v + sigma(x - (b(x,v)/b(v,v)) v)` on the
framing; a non-integral image raises, which is what a complement isometry not
preserving `H` produces.  `setwise=True` allows `-1` on the line.

## 2. Acceptance

**Public, library-owned generators for every primitive vector: MET for the
isotropic and non-isotropic cases; three regimes remain the port's, and they are
stated in the docstrings.**

| `v` | construction | family | time |
| --- | --- | --- | --- |
| isotropic, `K_I = v^\perp/Zv` of rank >= 1 | Schreier over the kernel of the sign in the rank-one parabolic (#459's family) | 17 on `026E` | 2.1 s |
| isotropic, `K_I = 0` | the integral pointwise perpendicular kernel | empty on `U` (the stabilizer is trivial) | 0.3 s |
| non-isotropic, `H = L/L_0` trivial | the complement's own isometries, extended by the identity on `Zv` | 2 on `U + A1` at its `A1` generator | 0.2 s |
| non-isotropic, `H` of order two | Schreier over the orbit of `H` | 1 on `U` at `e+f`, generating `{1, e<->f}` | 0.4 s |
| non-isotropic, larger `K` | same | 9 on `026E` at its norm-`-2` generator | 0.8 s |

Generation is proved in the code (the Schreier argument above, plus the gluing
correspondence), and two orders are checked in the tests where the group is
finite: `U` at `e+f` gives order two pointed and order four setwise.

**A card comparison: MET, narrowly.**  Card `026E`'s certified
`integral.primitive_orbits` row (one `O`-orbit and one `SO`-orbit of primitive
isotropic vectors) is compared in the tests, and card `0016`'s `O` row is the
other.  Card `029J`'s cited stabilizer index 1 for `L_1 = Ze_1` is reproduced by
the construction in the earlier round's measurement (12--23 s, over the 20 s call
ceiling, so recorded rather than landed).

## 3. The red

`test_the_setwise_stabilizer_of_a_nonsingular_line_returns` fails at
`41f21a69`, on `U` -- the smallest indefinite lattice there is:

    ValueError: ... does not mark a totally isotropic sublattice: Isom and Aut of
    other sublattice markings are the preamble's (research#399)

That is the port refusing the marking outright, and the setwise stabilizer of a
nonsingular line is now built beside the isotropic line and plane slots.  The
other six tests pass at `41f21a69` as well: the port's *pointed* families do fix
their vectors on these specimens, uncertified and unproved, so the red names the
one place where its route is wrong rather than merely uncertified.

## 4. Boundaries, stated rather than crossed

* A pointwise stabilizer of a sublattice of **rank two and up** is not owned
  here: the port's route is kept.
* An **odd** lattice, a **non-primitive** vector, or a base ring other than `ZZ`:
  the port's route.
* The non-isotropic construction's cost is `|orbit of H| * |O(K)'s generators|`
  isometries of `L`; the orbit is the orbit of `H` in the finite group
  `A_{L_0}`, and on `T_Co` and `T_En` that group is large, so no measurement
  there is recorded.
* `T_Co` and research#760's cusp-5 root orbits are not run here.

## 5. Runs, and what was not run

    TREE=<worktree> LOG=<log> FILES=<files> bash .tmp/launch591-test.sh

* `tests/lattices/test_the_pointed_stabilizer_of_a_primitive_vector.sage`:
  7 passed in 3.65 s.  At the parent `41f21a69`: 1 failed, 6 passed in 8.23 s.
* `tests/lattices/test_the_line_stabilizer_family_is_rebuilt_from_its_factors.sage`,
  `tests/lattices/test_pointwise_stabilizer_of_an_isotropic_line_vector_equivalence.sage`,
  `tests/lattices/test_pointwise_stabilizers_of_coordinate_sublattices.sage`,
  `tests/lattices/test_the_stabilizer_generators_carry_the_radical.sage`:
  15 passed in 8.56 s.
* `tests/lattices/test_sublattice_stabilizer_vector_decisions.sage` and
  `tests/lattices/test_degenerate_pointed_vectors.sage` do not collect in this
  tree: their own test-lint findings (`TL01`, `TL07`, `TL09`, `TL10`, `TL11`).
  Pre-existing, not repaired here.
* Not run: the `ast-grep` gates, `just test`, the full suite, anything on `T_Co`.
