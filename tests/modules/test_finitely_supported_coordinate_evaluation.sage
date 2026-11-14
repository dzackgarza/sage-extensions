r"""Coordinates of a finitely supported function have the declared scalar values."""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("ring", (ZZ, QQ), ids=("integers", "rationals"))
def test_free_module_coordinate_values_at_present_and_absent_basis_labels(ring):
    module = ring.free_module(3)
    first, second, third = tuple(module.module_generating_set())
    point = module.linear_combination({first: ring(2), second: ring(3)})
    coordinates = point.to_vector()
    assert coordinates(first) == ring(2)
    assert coordinates(second) == ring(3)
    assert coordinates(third) == ring.zero()
    assert all(coordinates(label).parent() is ring for label in (first, second, third))
    zero_coordinates = module.zero().to_vector()
    assert all(zero_coordinates(label) == ring.zero() for label in (first, second, third))
