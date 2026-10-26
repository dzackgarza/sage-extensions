r"""The identity cannot invert a constant map on two distinct points.

Conversely, the transposition is its own inverse. These two equations
separate unchecked inverse-pair data from the session's strict validator.
"""

import pytest

from sage_extensions.all import *


@pytest.fixture
def checking_flag():
    previous = strict_checking()
    yield strict_checking
    strict_checking(previous)


def test_the_global_strict_flag_controls_inverse_pair_validation(checking_flag):
    points = Sets.Δ[1]
    maps = Sets().Mor(points, points)
    core = Sets().Core().Mor(points, points)
    constant = maps(lambda _point: points(0))
    identity = maps.identity()
    swap = maps(lambda point: points(1 - int(point)))
    checking_flag(False)
    declared = core(constant, identity)
    assert declared.forward() is constant
    with pytest.raises(ValueError):
        declared.validate_inverse_pair()

    checking_flag(True)
    with pytest.raises(ValueError):
        core(constant, identity)
    transposition = core(swap, swap)
    assert transposition.inverse() * transposition == core.identity()
