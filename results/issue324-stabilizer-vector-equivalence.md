# 324 — vector equivalence under a lattice stabilizer gets its owner

Stage 1, under #280. The consumer: on an indefinite lattice $L$ and a primitive
sublattice $I$, decide whether two vectors of $L$ lie in one orbit of
$\mathrm{Stab}_{O(L)}(I)$, and return a witness in that stabilizer when they do.

## What was red

`tests/lattices/test_isotropic_plane_stabilizer_vector_equivalence.sage`,
commit `3cf3e57`, run on `2f9eeb33`:

```
FAILED ...::test_the_setwise_stabilizer_of_a_primitive_isotropic_plane_transports_a_vector
FAILED ...::test_the_setwise_stabilizer_separates_vectors_of_different_reduction_content
FAILED ...::test_the_pointwise_stabilizer_of_the_plane_decides_vectors_completely
3 failed in 1.10s
```

all three at `src/sage_extensions/categories/orthogonal_quotients.py:1711`:

```
AssertionError: cannot list the elements of {g in O(Integral lattice of rank 4 and
signature (2, 2)) : g fixes ... pointwise}: it is cut out by a predicate that is
not a character kernel, so its elements must be listed inside O(L), and Integral
lattice of rank 4 and signature (2, 2) is not definite.  Over an indefinite
lattice L, O(L) is an infinite arithmetic group and no generating set of this
subgroup is known. ...
```

The stabilizer constructors retained no `vector_witness`, so
`_subgroup_vector_equivalence_witness` fell through every exact route to the
finite listing, which exists only for a definite lattice. The docstrings at the
time claimed the ambient group's decision "is the same decision"; it is not —
$O(L)$-equivalence is a strictly coarser relation than $P_I$-equivalence.

## The owner

`PrimitiveIsotropicSubobjects` (`categories/isotropic_parabolics.py`), the
object that owns the parabolic $P_I = \mathrm{Stab}_{O(L)}(I)$, now carries two
decisions, and `pointwise_stabilizer` / `setwise_stabilizer` retain the matching
one as their `vector_witness`:

* `pointwise_vector_equivalence_witness(left, right)` — a decision for the
  pointwise stabilizer. For $I$ maximal isotropic ($I = I^\perp$) that group is
  exactly the kernel $\ker(P_I \to O(I^\perp))$: an element fixing $I$ pointwise
  stabilizes $I^\perp$ and acts trivially on $I = I^\perp$, and conversely. The
  kernel is what
  `IsotropicReductions._pointwise_perpendicular_kernel_data` retains as a
  *complete integral parameter module*: an element fixing $J = I^\perp$
  pointwise is uniquely $1 + N$ with $N \colon L/J \to \mathrm{rad}(J)$ linear,
  and the isometry equations $b(Nf_a, f_b) + b(f_a, Nf_b) = 0$ are homogeneous
  integral linear equations whose solution module is the parameter module. The
  map parameter $\mapsto 1+N$ is a group homomorphism from an additive lattice,
  so "is there $k$ with $k(\text{left}) = \text{right}$" is one integer linear
  system, solved exactly by Smith normal form (`_integral_solution`). `None` is
  then a decision.
* `vector_equivalence_witness(left, right)` — for the parabolic itself, the
  product of its Levi factor and unipotent radical, $1 \to U_I \to P_I \to M_I
  \to 1$ with $M_I \le GL(I) \times O(I^\perp/I)$ (this module's own statement).
  Exact outcomes: $q$ differs $\Rightarrow$ `None`; the content of
  $b(\text{left},-)|_I$ or of $b(-,\text{left})$ differs from the target's
  $\Rightarrow$ `None`, since an element of $P_I$ acts on $\mathrm{Hom}(I,ZZ)$
  and on $\mathrm{Hom}(L,ZZ)$ by unimodular changes of coordinates, which
  preserve the content (the gcd of the values on a basis); an element of the
  pointwise kernel carries one onto the other $\Rightarrow$ that isometry is
  returned. Otherwise the call **refuses**, naming the undecided part: the image
  of $P_I$ in $O(I^\perp)$, whose orbits on the reduction $I^\perp/I$ are not
  computed here (`levi_lift_generators` holds the closed-form Levi lifts that
  such a computation would reduce by).

No element of the infinite group is listed and no generating family of it is
selected. Both methods evaluate the witness on the two endpoints before
returning it.

Sources used, each for the statement the code runs on:

* the parabolic exact sequence and the Levi target $GL(I) \times O(I^\perp/I)$:
  `isotropic_parabolics.py`'s module statement, whose block equation for the
  Levi lift is Dutour Sikirić–Hulek, *Moduli of polarised Enriques surfaces —
  computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
  §"The Tits building", Theorem `theorem_isotropic_k_planes`, printed p. 22, as
  recorded at `levi_lift_generators`;
* the Eichler transvections generating the unipotent radical: Gritsenko–Hulek–
  Sankaran, arXiv:0810.1614, §3.1, equations (4)–(5), as recorded at
  `unipotent_radical_generators`;
* the complete integral parameter module of the pointwise kernel: the owner
  `IsotropicReductions._pointwise_perpendicular_kernel_data`, whose derivation
  is stated there and in the port's `Lorentzian.g:115-249`.

## `vector_orbit_set`

The import of `sage_indefinite_port.indefinite.pairing_slices` is gone (the
pinned port, `991b88b0`, does not ship that module). The call now returns the
acting group's own orbit-representative computation through
`vector_orbit_representatives`: the shell's representatives under $O(L)$, split
by a finite character quotient where the subgroup has one, and the finite
listing where a definite lattice supplies it. A predicate subgroup over an
indefinite lattice refuses there, and that refusal propagates.

## Green

`tests/lattices/test_isotropic_plane_stabilizer_vector_equivalence.sage`,
`3 passed in 1.07 s`. The three claims are relations only; no number in the
module is a computation's own output.

## One defect found on the way, and one repaired elsewhere

1. `isotropic_parabolics.PrimitiveIsotropicSubobjects.quotient_reflection_generators`
   raised on a **maximal** isotropic plane, because the Levi quotient
   $I^\perp/I$ is then the zero lattice and `shortest_vectors()` asked the zero
   lattice for a minimum: `ValueError: the zero lattice has no nonzero vector
   and no minimum`. Reached from
   `parabolic_stabilizer_generators` → `_isotropic_plane_parabolic_generators`,
   so `setwise_stabilizer(...).group_generators()` did not return on
   $U \oplus U(2)$ at $\langle e_1, e_3\rangle$. **Repaired by `093a1063ca`**
   ("Give no reflection generator for a trivial Levi quotient"): a rank-zero
   quotient returns no reflection, which is the trivial Levi factor. The vector
   decision above never needed those generators.
2. `PrimitiveIsotropicSubobjects.unipotent_group_generators` calls
   `RECURSION.isotropic_quotient_kernel_generators` (`lattices.py:10549`), which
   the pinned port's `EichlerRecursion` does not define:
   `AttributeError: 'EichlerRecursion' object has no attribute
   'isotropic_quotient_kernel_generators'`. Still open. The same family blocks
   `levi_image` / `levi_lift` at plane rank: `_levi_integral_lift_or_none` calls
   `RECURSION.isotropic_quotient_lift`, which the pinned port also does not
   define, so the Levi image is read from the images of the generating family
   instead (`quotient_image_lifts`, #327).

## Left red, deliberately

`tests/lattices/test_sublattice_stabilizer_vector_decisions.sage` was red before
this work and stays red. Its stabilizers are of a **non-isotropic** line
$\mathbb{Z}(e + 3f) \subset U$, for which no owner decides vector equivalence,
and its third test calls `vector_orbit_set(...).equivalent(...)` and iterates
the result, an interface the absent port module alone provided. The file is also
blocked by four `test_lint` findings (`TL09`, `TL01`, `TL07` ×2), so it does not
collect at all under the session plugin. It is not rewritten here: the three
claims it makes have no owner yet, and deleting them would be weakening a test.
