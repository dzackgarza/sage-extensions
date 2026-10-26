r"""A zero rank-one form is degenerate; [2] over ZZ is not perfect.

The form [1] is nondegenerate and unimodular. These determinant
computations hold with the global construction checks both off and on.
Objects are constructed through the top-level FormModules category.
"""

import pytest

from sage_extensions.all import *


@pytest.fixture(params=(False, True))
def strict_setting(request):
    previous = strict_checking()
    strict_checking(request.param)
    yield
    strict_checking(previous)


@pytest.mark.parametrize("entry, nondegenerate, unimodular", ((0, False, False), (2, True, False), (1, True, True)))
def test_form_properties_read_the_actual_pairing(strict_setting, entry, nondegenerate, unimodular):
    module = ZZ.free_module(("e",))
    form = module.bilinear_hom_space(ZZ)([[entry]])
    formed = FormModules(ZZ)(form)

    assert formed.determinant() == entry
    assert formed.is_nondegenerate() is nondegenerate
    assert formed.is_unimodular() is unimodular
