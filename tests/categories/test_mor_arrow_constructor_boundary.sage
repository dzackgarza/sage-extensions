r"""An arrow on a two-point set does not define an arrow on a different domain."""

import pytest

from sage_extensions.all import *


def test_a_whole_isomorphism_is_not_restricted_by_a_set_map_constructor():
    two = Sets.Δ[1]
    one = Sets.Δ[0]
    identity = Sets().Core().Mor(two, two).identity()
    maps = Sets().Mor(one, two)

    with pytest.raises(ValueError):
        maps(identity)
