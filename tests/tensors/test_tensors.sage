r"""Pairings, index lowering and raising, composition, dualization and pullback of
tensors and linear maps on free modules.

Every value is computed by hand from the component formulas; matrices act on
column vectors, and a linear map is given by the images of the basis vectors.
"""

from sage_extensions.all import *

import pytest


def _linear_map(source, target, columns):
    r"""The linear map sending the `i`-th basis vector of ``source`` to ``columns[i]``."""
    return source.Mor(target)(
        {source.module_generator(index): target(column) for index, column in enumerate(columns)}
    )


def test_covector_vector_product_is_the_natural_pairing() -> None:
    r"""`c = (2, -1, 4)`, `v = (5, 6, 7)`: `c(v) = 10 - 6 + 28 = 32`."""
    module = ZZ.free_module(3)
    covector = module.dual_module()((2, -1, 4))
    vector = module((5, 6, 7))

    assert covector * vector == 32
    assert covector(vector) == 32


def test_bilinear_form_lowers_an_index() -> None:
    r"""`b = [[2, 1], [1, 3]]`, `v = (4, 5)`: `b(-, v) = (13, 19)` and `b(v, v) = 147`."""
    module = ZZ.free_module(2)
    form = module.mixed_tensor_algebra().graded_piece((0, 2))([[2, 1], [1, 3]])
    vector = module((4, 5))
    lowered = form * vector

    assert lowered == module.dual_module()((13, 19))
    assert lowered(vector) == 147


def test_composition_of_linear_maps_is_the_matrix_product() -> None:
    r"""`A = [[1, 0, 2], [0, 1, 3]]: \mathbb{Z}^3 \to \mathbb{Z}^2` and
    `B = [[1, 2], [3, 4], [5, 6]]: \mathbb{Z}^2 \to \mathbb{Z}^3` give
    `AB = [[11, 14], [18, 22]]` and `A(7, 8, 9) = (25, 35)`."""
    plane = ZZ.free_module(2)
    space = ZZ.free_module(3)
    left = _linear_map(space, plane, ((1, 0), (0, 1), (2, 3)))
    right = _linear_map(plane, space, ((1, 3, 5), (2, 4, 6)))
    composite = left * right

    assert composite(plane.module_generator(0)) == plane((11, 18))
    assert composite(plane.module_generator(1)) == plane((14, 22))
    assert left(space((7, 8, 9))) == plane((25, 35))


def test_the_dual_map_has_the_transposed_matrix() -> None:
    r"""For `A = [[1, 2, 3], [4, 5, 6]]: \mathbb{Z}^3 \to \mathbb{Z}^2`, the dual map
    sends a covector `c` to `c \circ A`: the dual basis covectors go to the rows
    `(1, 2, 3)` and `(4, 5, 6)`, and `c = (2, -1)` goes to `(-2, -1, 0)`."""
    plane = ZZ.free_module(2)
    space = ZZ.free_module(3)
    linear = _linear_map(space, plane, ((1, 4), (2, 5), (3, 6)))
    dual_map = linear.dual_module_morphism()
    covectors = plane.dual_module()

    assert dual_map(covectors((1, 0))) == space.dual_module()((1, 2, 3))
    assert dual_map(covectors((0, 1))) == space.dual_module()((4, 5, 6))
    assert dual_map(covectors((2, -1))) == space.dual_module()((-2, -1, 0))


def test_the_inverse_of_a_unimodular_matrix_is_integral() -> None:
    r"""`[[2, 1], [1, 1]]` has determinant 1 and inverse `[[1, -1], [-1, 2]]`."""
    plane = QQ.free_module(2)
    linear = _linear_map(plane, plane, ((2, 1), (1, 1)))
    inverse = linear.inverse()

    assert linear.determinant() == 1
    assert inverse(plane.module_generator(0)) == plane((1, -1))
    assert inverse(plane.module_generator(1)) == plane((-1, 2))
    assert inverse * linear == plane.Mor(plane).identity()


def test_the_inverse_pairing_has_the_inverse_gram_matrix() -> None:
    r"""The copairing inverse to `b = [[2, 1], [1, 1]]` is the `(2, 0)`-tensor
    `[[1, -1], [-1, 2]]`."""
    plane = QQ.free_module(2)
    algebra = plane.mixed_tensor_algebra()
    pairing = algebra.graded_piece((0, 2))([[2, 1], [1, 1]])

    assert pairing.dual_tensor() == algebra.graded_piece((2, 0))([[1, -1], [-1, 2]])


def test_the_dual_pairing_is_covariant_on_the_dual_module() -> None:
    r"""The inverse matrix is contravariant on $M$ and covariant when read as the induced pairing on $M^*$."""
    plane = QQ.free_module(2)
    pairing = plane.mixed_tensor_algebra().graded_piece((0, 2))([[2, 1], [1, 1]])

    assert pairing.dual_pairing() == tensor(QQ, (), (2, 2), [[1, -1], [-1, 2]])


def test_the_inverse_pairing_raises_an_index() -> None:
    r"""Raising `c = (3, 5)` with `b^{-1}` gives `v = (3 - 5, -3 + 10) = (-2, 7)`, and
    lowering `v` with `b` returns `c`."""
    plane = QQ.free_module(2)
    pairing = plane.mixed_tensor_algebra().graded_piece((0, 2))([[2, 1], [1, 1]])
    covector = plane.dual_module()((3, 5))
    raised = pairing.dual_tensor() * covector

    assert raised == plane((-2, 7))
    assert pairing * raised == covector


def test_pulling_back_a_bilinear_form_along_a_linear_map_is_p_transpose_b_p() -> None:
    r"""`b = [[2, 1], [1, 3]]`, `P = [[1, 1], [0, 1]]`: `P^T b P = [[2, 3], [3, 7]]`."""
    plane = ZZ.free_module(2)
    forms = plane.mixed_tensor_algebra().graded_piece((0, 2))
    change = _linear_map(plane, plane, ((1, 0), (1, 1)))

    assert forms([[2, 1], [1, 3]]).pullback(change) == forms([[2, 3], [3, 7]])


def test_integral_fractions_enter_a_zz_tensor_as_integers() -> None:
    r"""`G = [[2/1, -1], [-1, 2]]` over $\mathbb{Z}$: Python fractions with
    denominator 1 are integers, so the tensor admits them; a non-integral
    fraction is still rejected."""
    from fractions import Fraction

    gram = tensor(ZZ, (), (2, 2), [[Fraction('2'), -1], [-1, 2]])
    assert gram == tensor(ZZ, (), (2, 2), [[2, -1], [-1, 2]])
    assert gram.is_symmetric()
    with pytest.raises(TypeError):
        tensor(ZZ, (), (2, 2), [[Fraction('1/2'), 0], [0, 1]])
