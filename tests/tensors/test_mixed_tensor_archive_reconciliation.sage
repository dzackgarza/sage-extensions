r"""Contraction, trace and evaluation of mixed tensors on `M = \mathbb{Z}^2`.

A `(p, q)`-tensor is an element of `M^{\otimes p} \otimes (M^\vee)^{\otimes q}`, the
`(p, q)` piece of the mixed tensor algebra of `M`; its components are indexed upper
slots first.  Every value below is computed by hand from the component formulas
`c(v) = \sum c_i v^i`, `(v \otimes c)^i_j = v^i c_j` and
`b(v, w) = \sum b_{ij} v^i w^j`.
"""

from sage_extensions.all import *


def _plane():
    module = ZZ.free_module(2)
    return module, module.mixed_tensor_algebra()


def test_contracting_a_vector_with_a_covector_is_the_natural_pairing() -> None:
    r"""`c(v) = 5 \cdot 2 + 7 \cdot 3 = 31`, in either order."""
    module, _algebra = _plane()
    vector = module((2, 3))
    covector = module.dual_module()((5, 7))

    assert vector.contract(covector) == 31
    assert covector.contract(vector) == 31
    assert covector(vector) == 31


def test_contracting_a_two_zero_tensor_in_one_slot_leaves_a_vector() -> None:
    r"""`(e_1 \otimes e_1 + e_2 \otimes e_2)` contracted with `c = (4, 9)` in its second
    slot is the vector `(4, 9)`."""
    module, algebra = _plane()
    symmetric = algebra.graded_piece((2, 0))([[1, 0], [0, 1]])
    covector = module.dual_module()((4, 9))

    assert symmetric.contract(covector, slot=1) == module((4, 9))


def test_the_outer_product_of_a_vector_and_a_covector_has_trace_their_pairing() -> None:
    r"""`v \otimes c` for `v = (2, 3)`, `c = (5, 7)` is `[[10, 14], [15, 21]]`, with
    trace `31 = c(v)`."""
    module, algebra = _plane()
    product = module((2, 3)).tensor_product(module.dual_module()((5, 7)))

    assert product == algebra.graded_piece((1, 1))([[10, 14], [15, 21]])
    assert product.trace() == 31


def test_tracing_an_upper_against_the_lower_slot_of_a_two_one_tensor_leaves_a_vector() -> None:
    r"""For `T^{00}_0 = T^{11}_1 = 1` and all other components 0,
    `\sum_j T^{ij}_j = (1, 1)`."""
    module, algebra = _plane()
    three = algebra.graded_piece((2, 1))([[[1, 0], [0, 0]], [[0, 0], [0, 1]]])

    assert three.trace(slot=1, other_slot=0) == module((1, 1))


def test_evaluating_a_one_two_tensor_on_v_twice_is_evaluating_on_v_v() -> None:
    r"""`\mu^0_{jk} = \delta_{jk}`, `\mu^1_{jk} = 1 - \delta_{jk}`; for `v = (2, 3)`,
    `\mu(v, v) = (2^2 + 3^2, 2 \cdot 2 \cdot 3) = (13, 12)`."""
    module, algebra = _plane()
    multiplication = algebra.graded_piece((1, 2))([[[1, 0], [0, 1]], [[0, 1], [1, 0]]])
    vector = module((2, 3))

    assert multiplication(vector)(vector) == multiplication(vector, vector)
    assert multiplication(vector, vector) == module((13, 12))


def test_a_bilinear_form_on_one_vector_is_a_covector() -> None:
    r"""For `b = [[1, 2], [3, 4]]` and `v = (5, 7)`, `b(v, -) = (5 + 21, 10 + 28) =
    (26, 38)` and `b(v, v) = 26 \cdot 5 + 38 \cdot 7 = 396`."""
    module, algebra = _plane()
    form = algebra.graded_piece((0, 2))([[1, 2], [3, 4]])
    vector = module((5, 7))

    assert form(vector) == module.dual_module()((26, 38))
    assert form(vector)(vector) == form(vector, vector)
    assert form(vector, vector) == 396
