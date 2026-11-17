r"""The quadratic module on the Enriques discriminant group.

For A=(Z/2)^10, the direct-sum law for Gamma^2 gives
Gamma^2(A)=(Z/4)^10 + (Z/2)^45. Each cyclic summand contributes
Gamma^2(Z/2)=Z/4, and each unordered pair contributes Z/2 tensor Z/2.
See the Whitehead and Roby formulas cited in test_powers.sage.
"""

from sage_extensions.all import *


def test_the_divided_square_has_the_exact_cyclic_factors() -> None:
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((2,) * 10)
    square = module.divided_square()

    assert tuple(square.invariant_factors()) == (ZZ(2),) * 45 + (ZZ(4),) * 10
    assert square.cardinality() == cardinal(2**65)


def test_divided_powers_of_z_mod_two_have_the_roby_orders() -> None:
    r"""``Gamma^d(Z/2)`` has order ``gcd(2^j binomial(d,j): 1 <= j <= d)``.

    Roby's divided-power relations give orders 4, 2 and 8 in degrees
    2, 3 and 4.  These include complementary monomials beyond the
    quadratic classifier.  The degree-zero divided power is Z.
    """
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((2,))

    assert module.divided_power_module(0).module_rank() == 1
    for degree, order in ((2, 4), (3, 2), (4, 8)):
        assert tuple(module.divided_power_module(degree).invariant_factors()) == (ZZ(order),)
