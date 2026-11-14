# #343: the height enumeration's domain is `HyperbolicLattices`, and the sum is handed in

**Result: `tests/lattices/test_isotropic_height_enumeration.sage` is green on `main`, with its
expected values unchanged.** The defect was the test's input construction: `Lattices(ZZ)("U") +
Lattices(ZZ)("A1")` is a hyperbolic lattice by signature but is a `Lattices` object, and
`isotropic_elements_below_height` is a method of the `HyperbolicLattices` owner, which a lattice
enters only by being handed to it.

## The failure, on `main` at `43a0604`

```
$ pytest tests/lattices/test_isotropic_height_enumeration.sage
F                                                                        [100%]
tests/lattices/test_isotropic_height_enumeration.sage:16: in test_the_isotropic_vectors_…
    vectors = lattice.isotropic_elements_below_height(timelike, 1)
E   AttributeError: 'OwnedJoinCategory.parent_class[_SparseFreeModuleParent].ObjectType'
    object has no attribute 'isotropic_elements_below_height'
1 failed in 0.91s
```

The sum is not a non-hyperbolic lattice — it *is* hyperbolic, with signature `(1, 2)`; what it
is not is an object of the category that owns the method:

```
sum: Integral lattice of rank 3 and signature (1, 2)
category: Category of infinite countable finitely generated nondegenerate even chosen
          orthogonal lattice sums over Integer Ring
has the method: False
```

## The domain, and its source

A hyperbolic lattice is a free $\mathbb Z$-module of finite rank with an integral symmetric
bilinear form of signature $(n,1)$: V. V. Nikulin, *Reflection groups in hyperbolic spaces and
the denominator formula for Lorentzian Kac--Moody Lie algebras*, Izvestiya: Mathematics 60
(1996), no. 2, doi:10.1070/IM1996v060n02ABEH000072, arXiv:alg-geom/9503003v6, **§1.1, equation
(1.1.1) and the sentence after it, preprint p. 3**:

> Let $S\colon M\times M\to\mathbb Z$ (1.1.1) be a hyperbolic (i.e. of signature $(n,1)$)
> integral symmetric bilinear form over $\mathbb Z$. Here $M$ is a free $\mathbb Z$-module of a
> finite rank. To be shorter, we call $S$ as hyperbolic lattice.

`(1,n)` is the same lattice with its form twisted by $-1$, which is why this owner admits both
spellings. So the method's domain is hyperbolic lattices, and the test's object was outside it
by construction, not by signature.

The entry route is the category's own, and it is now stated with the citation where the
category is defined (`HyperbolicLattices`' class docstring) and where the method is
(`isotropic_elements_below_height`'s docstring): hand the lattice to
`HyperbolicLattices(ZZ)(L)`, which checks the signature and refines.

## Why the repair is not in `+`

`Lattices.ParentMethods.__add__` documents itself as "the two-index case of
`Lattices(R).orthogonal_sum`, in the concatenated basis", and returns a `Lattices` object; the
sum's category is the join of what its operands carry, and neither operand is a hyperbolic
lattice here (`Lattices(ZZ)("U")` is a plain `Lattices` object too, which is why
`HyperbolicLattices.an_object()` hands `U` in as well). Nor is there a uniform rule `+` could
apply: the sum of a hyperbolic lattice with a definite one has signature $(n,1)$ again, while
the sum of two hyperbolic lattices has index of inertia at least two and is not hyperbolic. So
`+` was left alone, and the class docstring now says why.

## The repair

* `tests/lattices/test_isotropic_height_enumeration.sage` — one line:

  ```
  lattice = HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))
  ```

  The module docstring names the domain and its source, and the entry route. **The expected
  values are unchanged**: cardinality 5 and the five vectors $0,\pm e,\pm f$.
* `src/sage_extensions/categories/hyperbolic_lattices.py` — the definition's citation at its
  owner: the module docstring, the `HyperbolicLattices` class docstring (with the reason `+`
  does not enter the category) and `isotropic_elements_below_height`'s docstring (with the
  constructor that does). No executable line changed.

Measured on the repaired tree:

```
sum signature: (1, 2)
refined in 0.00s: category includes "Category of hyperbolic lattices over Integer Ring"
same generators: True
isotropic_elements_below_height(timelike, 1): 0.11s
cardinality: 5
elements: ['-e_0', '-e_1', '0', 'e_1', 'e_0']
```

## Green

```
$ pytest tests/lattices/test_isotropic_height_enumeration.sage --durations=0
.                                                                        [100%]
0.30s call     …::test_the_isotropic_vectors_of_U_plus_A1_of_height_at_most_one_are_zero_and_plus_minus_e_f
1 passed in 0.70s
```

with the repository's time gates **on** and the test-lint plugin loaded: `0 findings` on the
module. The neighbouring modules that construct `HyperbolicLattices` and are cheap to run are
recorded with it in the run of this unit (`test_hyperbolic_root_lengths_and_vinberg.sage`,
`test_cusp_lattices.sage`).
