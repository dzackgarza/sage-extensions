r"""Contraction, trace, outer product, index gymnastics and pullback of coordinate tensors.

A type-$(p, q)$ tensor on free modules has $p$ upper and $q$ lower indices.  Contracting an
upper index against a lower one is the natural pairing $V \otimes V^* \to R$ applied in those
slots; on type-$(1, 1)$ tensors it is matrix composition and the trace.  For $A, B$ of type
$(1, 1)$, contracting the upper and lower index of $A$ inside $A \otimes B$ gives
$\operatorname{tr}(A) B$.  A bilinear form $b$ lowers an index by $v \mapsto b(v, -)$; a
unimodular $b$ raises it by $b^{-1}$.  The pullback of a bilinear form $G$ along $P$ is
$P^{t} G P$.  Every value is computed by hand from these component formulas.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_private_modular_pairing_realization_uses_exact_products_when_int64_would_overflow() -> None:
    r"""Engineering regression for the private contraction, not a replacement
    for the owned quotient-valued form assertions.

    Modulo m, the rows are (-4,-3), (3,5) and the symmetric form is
    [[-1,-2],[-2,-3]], yielding [[-91,115],[115,-144]]. Computing the
    unreduced products with int64 would overflow even though all inputs fit.
    """
    import numpy

    from sage_extensions.tensors.tensor import _engine_modular_pairing_pullback

    modulus = 10**12 + 39
    coordinates = numpy.array(((modulus - 4, modulus - 3), (3, 5)), dtype=numpy.int64)
    form = numpy.array(
        ((modulus - 1, modulus - 2), (modulus - 2, modulus - 3)), dtype=numpy.int64
    )
    assert _engine_modular_pairing_pullback(form, coordinates, modulus).tolist() == [
        [modulus - 91, 115],
        [115, modulus - 144],
    ]
    assert _engine_modular_pairing_pullback(
        form, coordinates, modulus, diagonal_only=True
    ).tolist() == [modulus - 91, modulus - 144]


def test_a_bilinear_form_evaluates_as_v_transpose_g_w() -> None:
    r"""$G = [[2, 1], [1, 3]]$, $v = (4, 5)$, $w = (1, -1)$: $G(-, v)$ pairs as $v^t G = (13, 19)$
    and $G(v, w) = 13 - 19 = -6$; $G$ is symmetric."""
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 3]])
    v = tensor.vector(ZZ, [4, 5])
    w = tensor.vector(ZZ, [1, -1])

    assert gram.contract(v, w) == -6
    assert gram(v, w) == -6
    assert gram(w, v) == -6
    assert gram * v == tensor.covector(ZZ, [13, 19])
    assert gram.is_symmetric()
    assert not tensor(ZZ, (), (2, 2), [[0, 1], [0, 0]]).is_symmetric()


def test_contracting_matrices_is_composition() -> None:
    r"""$A = [[1, 2], [3, 4]]$, $B = [[0, 1], [1, 0]]$: $AB = [[2, 1], [4, 3]]$ and
    $A^2 = [[7, 10], [15, 22]]$; $A(1, 1) = (3, 7)$."""
    a = tensor.matrix(ZZ, [[1, 2], [3, 4]])
    b = tensor.matrix(ZZ, [[0, 1], [1, 0]])

    assert a * b == tensor.matrix(ZZ, [[2, 1], [4, 3]])
    assert b * a == tensor.matrix(ZZ, [[3, 4], [1, 2]])
    assert a.contract(a, slot=0, other_slot=0) == tensor.matrix(ZZ, [[7, 10], [15, 22]])
    assert a * tensor.vector(ZZ, [1, 1]) == tensor.vector(ZZ, [3, 7])


def test_traces_of_a_tensor_product_of_matrices() -> None:
    r"""$\operatorname{tr} A = 5$ and $\operatorname{tr} B = 0$, so tracing the $A$-slots of
    $A \otimes B$ gives $5B$ and tracing the $B$-slots gives $0 \cdot A = 0$."""
    a = tensor.matrix(ZZ, [[1, 2], [3, 4]])
    b = tensor.matrix(ZZ, [[0, 1], [1, 0]])
    product = a.tensor_product(b)

    assert a.trace() == 5
    assert b.trace() == 0
    assert product.trace(0, 0) == 5 * b
    assert product.trace(1, 1) == tensor.matrix(ZZ, [[0, 0], [0, 0]])


def test_the_outer_product_of_two_vectors() -> None:
    r"""$(4, 5) \otimes (1, -1)$ has components $v_i w_j$: $[[4, -4], [5, -5]]$, of type $(2, 0)$."""
    v = tensor.vector(ZZ, [4, 5])
    w = tensor.vector(ZZ, [1, -1])
    outer = v.tensor_product(w)

    assert outer == tensor(ZZ, (2, 2), (), [[4, -4], [5, -5]])
    assert w.tensor_product(v) == tensor(ZZ, (2, 2), (), [[4, 5], [-4, -5]])


def test_the_type_of_a_tensor_product_adds_the_types() -> None:
    r"""$A \otimes A$ of a type-$(1, 1)$ tensor has type $(2, 2)$; $v \otimes v$ of a vector has
    type $(2, 0)$."""
    a = tensor.matrix(ZZ, [[1, 2], [3, 4]])
    v = tensor.vector(ZZ, [4, 5])

    assert a.tensor_product(a).tensor_type() == (2, 2)
    assert v.tensor_product(v).tensor_type() == (2, 0)


def test_the_hyperbolic_form_lowers_and_raises_by_swapping() -> None:
    r"""On $U = (\mathbb Z^2, [[0, 1], [1, 0]])$: $b((4, 5), -) = (5, 4)$, and $U$ is unimodular with
    $U^{-1} = U$, so raising $(3, 7)$ gives $(7, 3)$; raising undoes lowering."""
    module = ZZ ^ 2
    hyperbolic_plane = FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))
    v = tensor.vector(ZZ, [4, 5])
    c = tensor.covector(ZZ, [3, 7])

    assert v.lower_index(hyperbolic_plane) == tensor.covector(ZZ, [5, 4])
    assert c.raise_index(hyperbolic_plane) == tensor.vector(ZZ, [7, 3])
    assert v.lower_index(hyperbolic_plane).raise_index(hyperbolic_plane) == v


def test_pulling_back_a_form_along_a_shear_is_p_transpose_g_p() -> None:
    r"""$P e_0 = e_0 + e_1$, $P e_1 = e_1$ and $G = [[2, 1], [1, 3]]$: $P^t G P = [[7, 4], [4, 3]]$."""
    plane = ZZ ^ 2
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    shear = plane.Mor(plane)({0: e0 + e1, 1: e1})
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 3]])

    assert tensor.from_morphism(shear) == tensor.matrix(ZZ, [[1, 0], [1, 1]])
    assert gram.pullback(shear) == tensor(ZZ, (), (2, 2), [[7, 4], [4, 3]])


def test_the_dual_of_a_unimodular_pairing_is_the_inverse_copairing() -> None:
    r"""The dual of the pairing $[[0, 1], [1, 0]]$ is the copairing with the inverse matrix, which is
    again $[[0, 1], [1, 0]]$; over $\mathbb Q$, the dual of $[[2, 1], [1, 3]]$ is
    $\frac15 [[3, -1], [-1, 2]]$."""
    swap = tensor(ZZ, (), (2, 2), [[0, 1], [1, 0]])
    gram = tensor(QQ, (), (2, 2), [[2, 1], [1, 3]])

    assert swap.dual_tensor() == tensor(ZZ, (2, 2), (), [[0, 1], [1, 0]])
    assert gram.dual_tensor() == tensor(QQ, (2, 2), (), [[3 / 5, -1 / 5], [-1 / 5, 2 / 5]])


def test_changing_the_ring_keeps_the_components() -> None:
    r"""$G = [[2, 1], [1, 3]]$ over $\mathbb Z$ and over $\mathbb Q$ have the same components."""
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 3]])

    assert gram.change_ring(QQ) == tensor(QQ, (), (2, 2), [[2, 1], [1, 3]])
    assert gram - gram == tensor(ZZ, (), (2, 2), [[0, 0], [0, 0]])
    assert 3 * gram == tensor(ZZ, (), (2, 2), [[6, 3], [3, 9]])
