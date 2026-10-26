r"""Indefinite orthogonal-group dispatch keeps integral and rational forms distinct."""

import pytest

from sage_extensions.all import *


def test_the_rational_hyperbolic_plane_contains_nonintegral_isometries() -> None:
    plane = Lattices(QQ)("U")
    e, f = plane.module_generators()
    dilation = plane.O()({0: plane.scalar_multiple(2, e), 1: plane.scalar_multiple(QQ(1) / 2, f)})

    assert dilation(e).b(dilation(f)) == e.b(f)
    assert dilation(e) not in Lattices(ZZ)("U")


def test_only_the_integral_indefinite_group_reaches_the_port() -> None:
    assert Lattices(ZZ)("U").O().cardinality() == 4
    rational_group = Lattices(QQ)("U").O()
    with pytest.raises(AssertionError):
        rational_group.group_generators()
    with pytest.raises(AssertionError):
        rational_group.cardinality()
