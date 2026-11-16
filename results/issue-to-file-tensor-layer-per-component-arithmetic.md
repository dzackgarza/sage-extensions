# Issue to file under #518: the tensor layer's outer products and sums cross into the owned ring once per component

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body under #518, against the tensor package. No
repair is made here: #539 states the Eichler transvection as the tensor expression its
issue requires, and the arithmetic that expression costs is the tensor layer's own.

## Title

A rank-two tensor update costs one owned-ring operation per component, where the engine
does the same four operations in four calls

## Body

`src/sage_extensions/tensors/tensor.py`:

- `Tensor.tensor_product` (`:754`) enumerates both factors' index tuples and forms each
  nonzero entry by `self[left_index] * right_value`, an owned-ring multiplication per
  pair, then a second owned-ring addition per collision.
- `_CoordinateTensor._add_` (`:2183`), `_sub_` (`:2193`) and `_lmul_` (`:2206`) build a
  new component tuple with one owned-ring operation per component.
- `_CoordinateTensorModule._element_constructor_` converts every component through
  `_owned_coordinate_component` (`:2385`), one owned-ring call per component.

So a type-(1,1) statement of `rank^2` components costs `rank^2` owned-ring operations
per operation applied to it. The review of `fd727b41` measured the consequence on the
Eichler transvection, one call best of five on `(U + <6>)^k`: 0.0012 s to 0.0069 s at
rank 3, 0.0014 s to 0.0181 s at rank 6, and **0.0020 s to 0.0928 s at rank 12** (46x) --
the rank `T_Co` has.

Each of those operations is one engine operation on the same data: an outer product of a
vector with a covector is a rank-one matrix, a sum of two type-(1,1) tensors is a matrix
addition, and a scalar multiple is a matrix rescale. `Tensor.__mul__` already says so for
the integral and rational rings: it calls `_engine_component_matrix` and
`_engine_component_vector` and raises the result once with `_owned_engine_element`. The
four operations of the transvection's expression (`id`, two outer products, three sums)
are therefore four engine calls, not `4 * rank^2` owned-ring ones. The per-component
elements are the object's shape, not the waste; the waste is that the arithmetic over
them is done one element at a time where the exact engine does the whole array.

## Repair

Route `tensor_product`, `_add_`, `_sub_` and `_lmul_` through the engine for the
integral and rational rings, as `Tensor.__mul__` already does for its two-vector
evaluation: outer products as one matrix product of a column by a row, sums and scalar
multiples as matrix arithmetic, each result crossed back once. Rings that are neither
`_owned_integers()` nor `_owned_rationals()` keep the generic component path. The public
statement of any consumer does not change, and no test may bound a call count
(AGENTS.md, *Performance claims*): the measurement is the record, on `eichler_transvection`
at rank 12, and the tensor form's own equation test is unchanged.
