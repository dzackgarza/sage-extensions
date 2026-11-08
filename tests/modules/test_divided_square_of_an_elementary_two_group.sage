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
