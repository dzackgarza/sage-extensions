r"""GL of a two-dimensional space over F3 has order (9-1)(9-3)=48.

The first basis image has eight nonzero choices. The second has six
choices outside its span. Forgetting a form preserves this module group.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("formed", (False, True), ids=("module", "formed-module"))
def test_finite_module_automorphisms_retain_their_exact_finite_group(formed):
    field = PrimeFields()(3)
    module = Lattices(ZZ)("U").base_change(field.quotient_map()) if formed else field.free_module(2)
    group = module.general_linear_group()
    assert group.is_finite() is True
    assert group in Groups().Finite()
    assert group.cardinality() == cardinal(48)
