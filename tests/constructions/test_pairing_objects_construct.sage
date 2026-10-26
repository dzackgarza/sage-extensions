r"""Paired modules and formed modules share one pairing-bearing interface."""

from sage_extensions.all import *  # noqa: F401,F403


def test_non_diagonal_pairing_uses_the_common_pairing_owner() -> None:
    left = ell(1, NN, RR)
    right = ell(oo, NN, RR)
    paired = left * right

    assert paired in PairingObjects(RR)
    assert paired.left_module() is left
    assert paired.right_module() is right
    assert paired.value_module() == RR.regular_module()
    assert paired.pairing(left.zero(), right.zero()) == RR.zero()


def test_formed_module_is_the_diagonal_pairing_case() -> None:
    module = ZZ.free_module(2)
    formed = FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))
    left, right = formed.module_generators()

    assert formed in PairingObjects(ZZ)
    assert formed.left_module() is formed
    assert formed.right_module() is formed
    assert formed.value_module() == ZZ.regular_module()
    assert formed.pairing(left, right) == formed.b(left, right)
