# #365: the parameter lattice of the unipotent radical at P₂, decided class by class

## The answer

At Sterk's `P_2` of `T_En`, in the block basis `(U | P | K)` of `plane_block_basis()` —
Dutour Sikirić–Hulek, *Moduli of polarised Enriques surfaces — computational aspects*,
JLMS 110 (2024), arXiv:2302.01679v2, **Theorem 4.9** (`theorem_isotropic_k_planes`),
proof, printed **p. 22** — an element of `U_I` has the block matrix

```
g = ( 1 0 0 )        A = 1,   τ = -J⁻¹ cᵗ A_K,   J a + aᵗ Jᵗ = -(Kc + cᵗ Kᵗ + cᵗ A_K c),
    ( a 1 τ )
    ( c 0 1 )
```

and the parameters `c` that occur are decided exactly, class by class, with no residue
table:

| quantity | value | how |
| --- | --- | --- |
| modulus at which the lift condition depends only on the class of `c` | **2** | derived from the two equations, then verified |
| classes decided | `65536 = 2¹⁶` | every one of them |
| admissible classes | **4096** | `unipotent_parameter_lifts` on each class |
| rank of the parameter lattice | **16** | `unipotent_parameter_lattice()` |
| covolume (index in `ℤ¹⁶`) | **16** | Hermite normal form of the admissible classes together with `2·ℤ¹⁶` |
| admissible classes are a subgroup | **yes** | `4096 · 16 = 65536`, checked, not assumed |
| `τ(U_I)` | rank **16**, covolume **1** | `unipotent_translation_basis()`, the whole coordinate lattice of `Hom(K, P)` |
| `c = e₂`, `c = e₃` of the #364 turn | **both in the lattice** | `unipotent_parameter_coordinates` returns their coordinates |
| `U_I` | rank `17 = 16 + 1` | `unipotent_radical_rank()`, `unipotent_translation_kernel_rank()` |
| `unipotent_radical_index()` at `P_2` | **1** | the block generators cover `τ(U_I)` and the centre |

The lattice, written out: `2e₁, 2e₂, 2e₃, 2e₄, e₅, …, e₁₆` in the listing
`unipotent_parameter_vector` uses (coordinate `2i + j` is the coefficient of the `i`-th
basis vector of `K` in the image of the `j`-th basis vector of the plane).  So a
parameter lifts exactly when the first two basis vectors of `K = P_2^⊥/P_2` have even
coefficients in both plane columns; twelve of the sixteen unit parameters lift and four
do not.

## The modulus, and why it is 2

The two equations are conditions on `c` alone, and each is a condition on its class:

**The translation.** `τ = -J⁻¹ cᵗ A_K` is linear in `c`.  With `J⁻¹ = adj(J)/det J`,
`τ` is integral exactly when `adj(J) cᵗ A_K` is divisible by `det J` entrywise, which
depends on `c` modulo the least `m` with `m · adj(J) cᵗ A_K ≡ 0 (mod det J)` for every
integral `c` — the lcm, over the sixteen coordinates, of `det J / gcd(det J, entry)`
of `adj(J)` composed with that coordinate.  At `P_2` the block data is
`J = 2 · 1₂` (so `det J = 4`, `adj(J) = 2 · 1₂`) and `A_K` has an odd entry, so that
least modulus is **2**: modulo `1` the condition fails, modulo `2` it is `cᵗ A_K` even.

**The plane block.** The right side `S(c) = -(Kc + cᵗ Kᵗ + cᵗ A_K c)` is quadratic in
`c`, so the modulus is not read off term by term.  Along a step of length `m`,

```
S(c + m d) - S(c) = -m(Kd + dᵗ Kᵗ) - m² dᵗ A_K d - m(cᵗ A_K d + dᵗ A_K c),
```

a quadratic function of `d` plus a bilinear function of `(c, d)`.  `S(c)` has an
integral `a` exactly when it lies in `Λ_J = {J a + aᵗ Jᵗ}`, which at `P_2` is
`diag(4, 2, 4) · Sym₂(ℤ)` (index `32` in `Sym₂(ℤ)`): with `J = 2 · 1₂` the equation is
`2(a + aᵗ) = S`, integral exactly when the diagonal of `S` is divisible by `4` and its
off-diagonal by `2`.  `K = b(U, K)` has a single nonzero entry `1` at `P_2` — that is
what "the plane does not split" means in these coordinates — so `m = 1` leaves
`-Kd - dᵗKᵗ` outside `Λ_J`, and `m = 2` puts every one of the three families inside it.
The modulus is therefore **2**.

`unipotent_parameter_modulus()` derives both and then *recomputes* both conditions on
the lcm before returning it, so the number is verified and not only derived.  The
families above are finite: a quadratic function is determined by its values on the
coordinate vectors and on the pairwise sums, and a bilinear one by its values on pairs
of coordinate vectors, so sixteen plus 120 plus 256 membership tests decide the whole
family — no range is searched and no residue is tabulated.

## Deciding every class

`unipotent_parameter_lifts` applies the two exact tests to one parameter: `τ`'s
integrality by the divisibility above, and `a`'s existence by membership of `S(c)` in
`Λ_J`, which is `adj(H) s ≡ 0 (mod det H)` for the Hermite basis `H` of `Λ_J`.  Neither
is a search, so `False` means no element of `U_I` has that parameter.

`unipotent_parameter_lattice()` runs that predicate on each of the `2¹⁶` classes and
takes the Hermite normal form of the `4096` admissible ones together with `2` times the
coordinate lattice.  The result has rank `16` and index `16`, and
`4096 · 16 = 65536` exactly, which is the subgroup check of item 2: the product is the
count of classes in `ℤ¹⁶` only when the admissible classes are closed under addition,
and it would be larger otherwise.  The check is an assertion in the method, not a
remark.

## What the two parameters of the #364 turn are

The #364 turn recorded that "the elements with `c = e₂` and `c = e₃` lie in `U_I` but
are outside the enumerated parameter lattice", in the listing its own
`unipotent_radical_index` used — column-major over `(position, column)`, `0`-based — so
those two parameters are the ones supported on the **third and fourth** basis vectors
of `K` in the first plane column.  Measured here: both lie in the lattice, both have an
element over them (`unipotent_radical_element`), and each element fixes `P_2` pointwise
and acts trivially on `P_2^⊥/P_2`.

The reading matters, so it is worth stating what is *not* true: in the listing the
lattice itself uses (`2i + j`, row by row), the parameters at coordinates `0`–`3` — the
first two basis vectors of `K` in both columns — do not lift at all, and the test pins
that too.  A unit parameter is admissible or not depending on which basis vector of `K`
it sits over, and no ordering makes all sixteen of them admissible.

The previous tree's lookup-table method returns the same sixteen lattice vectors as this
exact decision (compared as row sets).  What changes is the derivation: the residue
table and its claim that the conditions on the `d`-part are linear over `ℤ/2` are gone,
replaced by an exact decision per class plus the subgroup verification, and a modulus
that is derived instead of assumed to be `2`.  An enumeration whose residue table is
wrong returns a lattice that is too small without saying so; this one cannot, because
every class at the derived modulus is decided by the equations themselves.

## The test

`tests/lattices/test_the_parameter_lattice_of_the_unipotent_radical.sage`, five tests
through the public calls, comparing computed values only — no count, rank or index in it
is typed:

1. every Eichler transvection of the plane that lies in `U_I` (selected by the radical's
   own definition) has its parameter in the returned lattice, with the coordinates round
   trip asserted, so a lattice listed in one ordering and read in another fails;
2. the parameters supported on the third and fourth basis vectors of `K` — the #364
   turn's `e₂`, `e₃` — are in the lattice, and the elements over them fix `P_2`
   pointwise and act trivially on `P_2^⊥/P_2`;
3. every basis vector of the lattice has an element of `U_I` over it, its parameter read
   back off the block matrix equals the basis vector, and the translations of the whole
   family reach the rank the radical's translation image has;
4. the parameters on the first two basis vectors of `K` have no lift, which is the part
   of `ℤ¹⁶` outside the lattice;
5. the centre's generator has vanishing parameter, translates nothing, and still moves a
   vector of `P_2^⊥`, so it is a generator of `ker τ` and not the identity.

## The calls, as they now report

`.tmp/qc-evidence/issue365-parameters.log` (20 s for the whole probe, plane included):

```
unipotent_parameter_modulus() = 2
unipotent_parameter_class_counts() = (2, 65536, 4096)
|unipotent_parameter_lattice| = 16 | rank = 16 | index = 16
|unipotent_translation_basis| = 16 | rank = 16 | covolume in Hom(K, P) = 1
unipotent_translation_rank() = (16, 16)
unipotent_radical_rank() = 17 | unipotent_translation_kernel_rank() = 1
the plane's Eichler transvections: count = 14 | outside the lattice: 0
    translation rank of the transvections = (12, 16)
central generator: parameter (0,…,0) | skew 1 | pointwise True | trivial True
|unipotent_radical_block_generators| = 17
|unipotent_radical_generators| = 31
unipotent_radical_index() = 1
is_parabolic_complete() = False
```

The unit parameters, one line each in the log: `(0,0)`, `(0,1)`, `(1,0)`, `(1,1)` do
not lift and have no element; the other twelve lift and their elements were built and
checked to lie in `U_I`.

The same probe runs the split plane `P_1` of `T_{\mathrm{En}}`, because the decision has
to return there too and because the centre's generator is a lattice generator there and
not the skew matrix the earlier code assumed:

```
==== P_1: splits = True
  J = [1, 0, 0, 2] | K = b(U,K) has 0 nonzero entries
  unipotent_parameter_modulus() = 1
  unipotent_parameter_class_counts() = (1, 1, 1)
  |unipotent_parameter_lattice| = 16 | rank = 16 | index = 1
  |unipotent_translation_basis| = 16 | rank = 16 | covolume in Hom(K, P) = 256
  unipotent_radical_rank() = 17 | unipotent_translation_kernel_rank() = 1
  central generator: c = 0 | tau = 0 | a = [0, -2, 1, 0] | coordinate on the centre's lattice = 1
  unipotent_radical_index() = 1 | is_parabolic_complete() = True
  the plane's transvections in U_I: 18 | outside the parameter lattice: 0
  the sixteen unit parameters lift: all True
```

At `P_1` the block `K = b(U, K)` vanishes (the plane splits), so the quadratic part of
the second equation is the only one and the modulus is `1`: every parameter lifts, as it
must at a splitting plane, where the radical is generated by the transvections alone
(Scattone's hypothesis is met there).

## The centre, and a defect the decision exposed

`unipotent_central_generator` used to build the element with `skew = 1`, i.e. with
`(a_{12} - a_{21})/2 = 1`.  That is not the generator of `Z` in general.  `Z` is the
lattice of integral `a` with `Ja` skew, which is `J^{-1}\operatorname{so}_2(\ZZ)`, and at
`P_1` — where `J = \operatorname{diag}(1,2)` — its generator is `((0,-2),(1,0))`, whose
`(a_{12} - a_{21})/2` is `-3/2`.  Half of `Z` is then out of reach of the skew scalar and
the old code raised `ArithmeticError` at `P_1` rather than answering, which broke
`is_parabolic_complete()`'s own test there.  It now returns the generator of that lattice
(:meth:`_unipotent_central_matrix`, least `s` with `s \operatorname{adj}(J) K` divisible
by `\det J`), and `unipotent_radical_index` reads a central member's coordinate on that
generator rather than the skew scalar.

## Evidence

| file | what it is |
| --- | --- |
| `.tmp/qc-evidence/issue365-parameters.py` | the probe: block data, modulus, classes, lattice, transvections, centre, index |
| `.tmp/qc-evidence/issue365-parameters.log` | its run, on the pinned runtime |
| `.tmp/qc-evidence/issue365-tests.log` | the acceptance run of the three test files |
| `.tmp/qc-evidence/issue365-lint.log` | `test_lint` on the new test file |

## Regression check on the neighbouring modules

The eight files that drive `parabolic_stabilizer_generators`, `unipotent_radical*` or
`parabolic_obstruction` were run with this commit and, for the three that fail, without it
at the fetched main `7ef38d5`:

```
9 failed, 19 passed in 349.11s      # with this commit, .tmp/qc-evidence/issue365-regression.log
  test_higher_rank_unipotent_kernel                  3 failed
  test_parabolic_induction                           2 failed
  test_pointwise_levi_images                         4 failed
9 failed, 4 passed in 4.96s         # the same three files on the base, .tmp/qc-evidence/issue365-base.log
```

The nine ids are the same on both sides, so the pre-existing set is unchanged; on the base
they are `AttributeError: 'EichlerRecursion' object has no attribute
'isotropic_quotient_kernel_generators'`, a port module this runtime does not ship, and not
something this commit touches.

One failure in that selection was this commit's to fix. The first run of it — with
`test_the_unipotent_radical_of_a_plane.sage` as it stood — was `10 failed, 18 passed`
(`.tmp/qc-evidence/issue365-regression-earlier-test.log`), the tenth being that file's
assertion that every member of `unipotent_radical_generators()` is one of the plane's
Eichler transvections. The family carries the block generators of `#365`'s lattice now, so
that assertion is false and the test asserts the three memberships that are true instead —
some transvections are in the family, some are not, and some members of the family are not
transvections — and it is green in the acceptance run.

## What this does not claim

`is_parabolic_complete()` is still `False` at `P_2`, and the radical is no longer the
reason: what is missing is the Levi pairing — a subdirect product of `GL_2(ℤ)` and
`O(P_2^⊥/P_2)` need not be the product, and for the returned generators the plane action
determines the quotient action.  That is #331's factor.  The generation of `U_I` itself is
here: the block generators cover a `ℤ`-basis of `τ(U_I)` and contain a generator of `Z`,
and `U_I` is a central extension of `τ(U_I)` by `Z` (Robinson, *A Course in the Theory of
Groups*, 2nd ed., GTM 80, **1.4.6**, printed p. 20, and **1.3.3**, p. 9, cited in
`unipotent_radical_block_generators`), so the family generates the radical.
`unipotent_radical_index()` returns `1` and the #353 test's assertion of an infinite index
is replaced by that measurement.
