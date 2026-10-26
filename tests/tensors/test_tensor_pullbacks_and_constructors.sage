r"""Pullbacks of covariant tensors along non-square maps, and the coordinate tensor constructors.

For $f: V \to W$ and a covariant tensor $T$ of type $(0, q)$ on $W$, $(f^*T)(v_1, \dots, v_q) =
T(f v_1, \dots, f v_q)$; for $q = 1$ this is $c \circ f$, whose components are $c A$ for the matrix
$A$ of $f$.  Pullback is defined only for covariant tensors whose indices have the rank of $W$.  A
type-$(1, 1)$ tensor $A$ evaluates on a covector $c$ and a vector $v$ as $c A v$.  Every value by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def folding_map():
    r"""$f: \mathbb Z^3 \to \mathbb Z^2$, $e_0 \mapsto e_0$, $e_1 \mapsto e_1$, $e_2 \mapsto e_0 + e_1$."""
    space, plane = ZZ ^ 3, ZZ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    return space.Mor(plane)({0: x, 1: y, 2: x + y})


def test_a_covector_pulls_back_to_its_composite_with_the_map() -> None:
    r"""$c = (2, -1)$ and $f$ as above: $f^*c = c A = (2, -1, 2 - 1) = (2, -1, 1)$."""
    covector = tensor.covector(ZZ, [2, -1])

    assert covector.pullback(folding_map()) == tensor.covector(ZZ, [2, -1, 1])


def test_a_bilinear_form_pulls_back_to_a_transpose_g_a_on_three_space() -> None:
    r"""$G = [[2, 1], [1, 3]]$ pulled back along $f$: $A^t G A$ with $A = [[1, 0, 1], [0, 1, 1]]$ is
    $[[2, 1, 3], [1, 3, 4], [3, 4, 7]]$."""
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 3]])

    assert gram.pullback(folding_map()) == tensor(ZZ, (), (3, 3), [[2, 1, 3], [1, 3, 4], [3, 4, 7]])


def test_the_cube_of_the_second_coordinate_pulls_back_along_the_shear_to_all_ones() -> None:
    r"""$T = e_1^* \otimes e_1^* \otimes e_1^*$ and $P e_0 = e_0 + e_1$, $P e_1 = e_1$: every $P e_i$ has
    second coordinate $1$, so $(P^*T)_{ijk} = 1$ for all $i, j, k$."""
    plane = ZZ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    shear = plane.Mor(plane)({0: x + y, 1: y})
    cube = tensor(ZZ, (), (2, 2, 2), [[[0, 0], [0, 0]], [[0, 0], [0, 1]]])
    ones = tensor(ZZ, (), (2, 2, 2), [[[1, 1], [1, 1]], [[1, 1], [1, 1]]])

    assert cube.pullback(shear) == ones


def test_only_covariant_tensors_of_the_codomain_rank_pull_back() -> None:
    r"""A vector has an upper index, so it has no pullback; a covector on $\mathbb Z^3$ does not pull back
    along a map into $\mathbb Z^2$."""
    with pytest.raises(TypeError):
        tensor.vector(ZZ, [1, 2]).pullback(folding_map())
    with pytest.raises(ValueError):
        tensor.covector(ZZ, [1, 2, 3]).pullback(folding_map())


def test_reading_a_bilinear_form_as_a_matrix_keeps_its_components() -> None:
    r"""The components of $G = [[2, 1], [1, 3]]$ read as a type-$(1, 1)$ tensor are the same matrix."""
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 3]])

    assert tensor.matrix(ZZ, gram) == tensor.matrix(ZZ, [[2, 1], [1, 3]])
    assert tensor.matrix(ZZ, 2, 3) == tensor(ZZ, (2,), (3,), [0, 0, 0, 0, 0, 0])
    assert tensor.matrix(ZZ, 2, 2, [1, 2, 3, 4]) == tensor.matrix(ZZ, [[1, 2], [3, 4]])


def test_currying_a_rectangular_bilinear_tensor_selects_the_correct_dual_coordinates() -> None:
    source, target = ZZ.free_module(2), ZZ.free_module(3)
    pairing = tensor(ZZ, (), (2, 3), [[1, 2, 3], [4, 5, 6]])
    correlation = pairing.curry_bilinear(source, target)

    assert correlation.domain() is source
    assert correlation.codomain() is target
    assert correlation(source.module_generator(0)) == (
        target.module_generator(0) + 2 * target.module_generator(1) + 3 * target.module_generator(2)
    )
    assert correlation(source.module_generator(1)) == (
        4 * target.module_generator(0) + 5 * target.module_generator(1) + 6 * target.module_generator(2)
    )


def test_currying_a_bilinear_tensor_from_a_zero_module_retains_the_target_rank() -> None:
    source, target = ZZ.free_module(0), ZZ.free_module(3)
    pairing = tensor(ZZ, (), (0, 3), [])
    correlation = pairing.curry_bilinear(source, target)

    assert correlation.domain() is source
    assert correlation.codomain() is target
    assert correlation(source.zero()) == target.zero()


def test_vectors_from_a_rank_and_from_their_nonzero_components() -> None:
    r"""The zero vector of rank $3$ and the vector with only second component $5$."""
    assert tensor.vector(ZZ, 3) == tensor.vector(ZZ, [0, 0, 0])
    assert tensor.vector(ZZ, {1: 5}) == tensor.vector(ZZ, [0, 5])


def test_feeding_a_vector_to_a_matrix_leaves_the_vector_a_v() -> None:
    r"""$A = [[1, 2], [3, 4]]$, $v = (1, -1)$: filling the lower slot gives $A v = (-1, -1)$, and the
    covector $c = (1, 2)$ then gives $c A v = -3$; a trilinear form on $\mathbb Z^2$ fed two vectors
    leaves the covector $T(v, w, -)$."""
    a = tensor.matrix(ZZ, [[1, 2], [3, 4]])
    v = tensor.vector(ZZ, [1, -1])
    cube = tensor(ZZ, (), (2, 2, 2), [[[0, 0], [0, 0]], [[0, 0], [0, 1]]])
    e1 = tensor.vector(ZZ, [0, 1])

    assert a(v) == tensor.vector(ZZ, [-1, -1])
    assert tensor.covector(ZZ, [1, 2]) * a(v) == -3
    assert cube(e1, e1) == tensor.covector(ZZ, [0, 1])
    assert cube(e1, e1, e1) == 1
