r"""The mixed tensor algebra `\bigoplus_{p,q} M^{\otimes p} \otimes (M^\vee)^{\otimes q}` of `M = \mathbb{Q}^2`.

Its product is the tensor product, bigraded by `(p, q)`, with unit `1` in bidegree
`(0, 0)`, and it is bilinear.
"""

from sage_extensions.all import *


def _vector_and_covector():
    module = QQ.free_module(2)
    return module, module((1, 2)), module.dual_module()((3, 4))


def test_vector_times_covector_is_their_outer_product_in_bidegree_one_one() -> None:
    r"""`v = (1, 2)`, `c = (3, 4)`: `v \otimes c` has components `v_i c_j =
    [[3, 4], [6, 8]]`, and its trace is `c(v) = 11`."""
    module, vector, covector = _vector_and_covector()
    algebra = module.mixed_tensor_algebra()
    one_one = algebra.graded_piece((1, 1))

    product = algebra.include(vector) * algebra.include(covector)

    assert product.homogeneous_component((1, 1)) == vector.tensor_product(covector)
    assert product.homogeneous_component((1, 1)) == one_one([[3, 4], [6, 8]])
    assert product.homogeneous_component((1, 0)) == algebra.graded_piece((1, 0)).zero()
    assert product.homogeneous_component((1, 1)).trace() == 11
    assert algebra.one() * product == product
    assert product * algebra.one() == product


def test_the_mixed_tensor_product_distributes_over_sums() -> None:
    r"""`(e_1 + e_2) \cdot c = e_1 \otimes c + e_2 \otimes c`."""
    module = QQ.free_module(2)
    algebra = module.mixed_tensor_algebra()
    first = module((1, 0))
    second = module((0, 1))
    covector = module.dual_module()((1, 1))

    product = (algebra.include(first) + algebra.include(second)) * algebra.include(covector)

    assert product.homogeneous_component((1, 1)) == (
        first.tensor_product(covector) + second.tensor_product(covector)
    )
    assert product.homogeneous_component((1, 1)) == algebra.graded_piece((1, 1))([[1, 1], [1, 1]])
