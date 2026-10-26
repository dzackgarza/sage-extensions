"""Root generators retain exact scalar-valued forms at large integral scales."""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("scale", (1, 2**34))
def test_scaled_a2_is_generated_by_its_reflective_roots(scale):
    lattice = Lattices(ZZ)([[2 * scale, -scale], [-scale, 2 * scale]])
    roots = lattice.root_module_generating_set()
    assert all(root.is_root() for root in roots)
    assert lattice.subobject_on(tuple(roots)).inclusion().is_surjective()
