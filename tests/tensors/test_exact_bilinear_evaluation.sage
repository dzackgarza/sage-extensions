r"""Exact rectangular contractions retain their owned scalar and both slots."""

from sage_extensions.all import *


def test_rectangular_integer_pairing_keeps_arbitrarily_large_coefficients() -> None:
    scale = ZZ(10**40 + 3)
    form = tensor(ZZ, (), (2, 3), [[2 * scale, 3 * scale, 5 * scale], [7 * scale, 11 * scale, 13 * scale]])
    left = tensor.vector(ZZ, [17, 19])
    right = tensor.vector(ZZ, [23, 29, 31])
    value = form.contract(left, right)

    assert value == ZZ(21673) * scale
    assert value.parent() is ZZ


def test_rectangular_rational_pairing_retains_its_denominators() -> None:
    form = tensor(QQ, (), (2, 3), [[QQ(a) / QQ(7) for a in row] for row in ((2, 3, 5), (7, 11, 13))])
    left = tensor.vector(QQ, [QQ(17) / QQ(3), QQ(19) / QQ(3)])
    right = tensor.vector(QQ, [23, 29, 31])
    value = form.contract(left, right)

    assert value == QQ(21673) / QQ(21)
    assert value.parent() is QQ


def test_an_empty_bilinear_slot_evaluates_to_the_owned_zero() -> None:
    form = tensor(ZZ, (), (0, 3), ())
    value = form.contract(tensor.vector(ZZ, []), tensor.vector(ZZ, [2, 3, 5]))

    assert value == ZZ.zero()
    assert value.parent() is ZZ
