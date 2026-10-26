r"""Tensor products retain both factors and their universal bilinear map.

For ``M=ZZ^2`` and ``N=ZZ``, the tensor product has rank two.  The universal
bilinear map sends ``(m,n)`` to ``m tensor n``; classifying that same bilinear
map back into the tensor product yields the identity morphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_tensor_line():
    left = ZZ.free_module(2)
    right = ZZ.free_module(1)
    return left, right, left.tensor_product(right)


def test_tensor_product_retains_its_factors_and_pure_tensors() -> None:
    left, right, product = _plane_tensor_line()
    factors = product.tensor_factors()
    pure = product.pure_tensor(left.module_generator(0), right.module_generator(0))

    assert product in TensorProductModules(ZZ)
    assert product in Modules(ZZ)
    assert product.module_rank() == 2
    assert factors.cardinality() == cardinal(2)
    assert product.tensor_factor(0) is left
    assert product.tensor_factor(1) is right
    assert isinstance(pure, product.ElementType)


def test_tensor_product_universal_bilinear_map_classifies_to_identity() -> None:
    left, right, product = _plane_tensor_line()
    bilinear = product.universal_bilinear_map()
    factor = product.from_bilinear_map(product, bilinear)
    pure = product.pure_tensor(left.module_generator(1), right.module_generator(0))

    assert bilinear(left.module_generator(1), right.module_generator(0)) == pure
    assert factor == product.Mor(product).identity()
    assert factor(pure) == pure


def test_tensor_product_module_morphisms_have_identity() -> None:
    _left, _right, product = _plane_tensor_line()
    identity = product.Mor(product).identity()

    assert identity(product.zero()) == product.zero()
    assert identity * identity == identity


def test_redundantly_presented_zero_factor_has_zero_tensor_products() -> None:
    hyperbolic = Lattices(ZZ)("U")
    zero = hyperbolic.correlation_morphism().cokernel()
    line = ZZ.free_module(1)
    assert zero.is_zero()
    assert zero.module_generating_set().cardinality() == cardinal(2)

    for product in (zero.tensor_product(line), line.tensor_product(zero), zero.tensor_product(zero)):
        assert product in TensorProductModules(ZZ)
        assert product.module_generating_set().cardinality() == cardinal(0)
        assert product.is_zero()
        assert product.pure_tensor(product.tensor_factor(0).zero(), product.tensor_factor(1).zero()) == product.zero()
        assert product.universal_bilinear_map() == product.Mor(product).identity()
