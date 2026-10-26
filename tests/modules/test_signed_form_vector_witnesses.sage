r"""Signed vectors of symmetric bilinear forms come from their Gram tensor.

[2] is positive definite; diag(2,-2) is indefinite; the hyperbolic
matrix [[0,1],[1,0]] has diagonal function 2xy, of both signs.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("rank, rows, has_negative", ((1, [[2]], False), (2, [[2, 0], [0, -2]], True), (2, [[0, 1], [1, 0]], True)))
def test_signed_witnesses_use_the_actual_diagonal_form(rank, rows, has_negative):
    module = ZZ.free_module(tuple(range(rank)))
    formed = FormModules(ZZ)(module.bilinear_hom_space(ZZ)(rows))

    positive = formed.positive_vector()
    negative = formed.negative_vector()

    assert positive in formed
    assert formed.norm(positive) > 0
    if has_negative:
        assert negative in formed
        assert formed.norm(negative) < 0
    else:
        assert negative is None
