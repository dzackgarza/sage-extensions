r"""Arithmetic in cyclic groups and the vanishing of coprime tensor products."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z2_tensor_z3_is_zero_and_four_equals_one_in_z3() -> None:
    r"""(Z/m) (x) (Z/n) = Z/gcd(m, n), so Z/2 (x) Z/3 = 0; 4 = 1 mod 3."""
    two = Modules(ZZ).direct_sum_of_cyclics((2,))
    three = Modules(ZZ).direct_sum_of_cyclics((3,))
    tensor = two.tensor_product(three)
    assert tensor.cardinality() == 1
    assert tensor.pure_tensor(two.module_generator(0), three.module_generator(0)) == tensor.zero()
    g = three.module_generator(0)
    assert g != three.zero()
    assert 4 * g == g
    assert 3 * g == three.zero()
