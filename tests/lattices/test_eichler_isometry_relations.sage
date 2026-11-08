r"""Isometry equality respects the additive law of Eichler transvections.

For e null and a,b in e-perp, t(e,a)t(e,b)=t(e,a+b).
The identity holds over ZZ, QQ and QQ[t], with their actual coefficients.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("ring_name", ("integers", "rationals", "polynomials"))
def test_the_transvection_product_equals_the_sum_parameter_isometry(ring_name) -> None:
    if ring_name == "polynomials":
        ring = QQ.polynomial_ring(("t",))
        coefficient = ring.algebra_generator("t")
    elif ring_name == "rationals":
        ring = QQ
        coefficient = QQ(1) / QQ(2)
    else:
        ring = ZZ
        coefficient = ZZ(2)
    ambient = Lattices(ring)([
        [0, 1, 0, 0], [1, 0, 0, 0],
        [0, 0, 0, 1], [0, 0, 1, 0],
    ])
    e1, _f1, e2, f2 = tuple(ambient.module_generators())
    parameter = ambient.scalar_multiple(coefficient, e2)
    first = ambient.eichler_transvection(e1, parameter)
    second = ambient.eichler_transvection(e1, f2)
    product = first * second
    direct = ambient.eichler_transvection(e1, parameter + f2)

    assert product == direct
    assert hash(product) == hash(direct)
    assert product != first
    assert (~product) * product == ambient.Aut().identity()
