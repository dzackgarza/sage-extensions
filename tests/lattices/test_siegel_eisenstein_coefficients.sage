"""Siegel products are read as rationals when their square roots combine only after reduction."""

import pytest

from sage_extensions.all import *

E6_PLUS_A1 = [
    [2, 0, -1, 0, 0, 0, 0],
    [0, 2, 0, -1, 0, 0, 0],
    [-1, 0, 2, -1, 0, 0, 0],
    [0, -1, -1, 2, -1, 0, 0],
    [0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, -1, 2, 0],
    [0, 0, 0, 0, 0, 0, 2],
]


@pytest.mark.parametrize("value", (2, 8))
def test_the_siegel_product_of_e6_plus_a1_is_its_theta_coefficient(value):
    lattice = Lattices(ZZ)(E6_PLUS_A1)
    theta = lattice.theta_series(value + 1)
    assert lattice.genus().siegel_eisenstein_coefficient(value) == theta[value]
