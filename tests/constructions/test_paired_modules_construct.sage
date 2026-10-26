r"""Paired modules retain both factors, their value module, and the pairing.

Hölder duality pairs ``ell^1`` with ``ell^oo`` by summation into ``RR``.  The
zero sequences pair to zero and the category remembers the two distinct factors.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_holder_pairing_retains_left_right_value_modules_and_zero_pairing() -> None:
    left = ell(1, NN, RR)
    right = ell(oo, NN, RR)
    paired = left * right

    assert paired in PairedModules(RR)
    assert paired.left_module() is left
    assert paired.right_module() is right
    assert paired.value_module() == RR.regular_module()
    assert paired.pairing(left.zero(), right.zero()) == RR.zero()
