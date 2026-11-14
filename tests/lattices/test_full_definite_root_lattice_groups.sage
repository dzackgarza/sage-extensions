r"""Full integral groups of the simply laced root lattices.

The full groups have orders 12 for A2, 1152 for D4 and 696729600
for E8: W(A2) extended by its diagram involution, W(D4) extended
by triality, and W(E8), respectively (Bourbaki, Groupes et algebres
de Lie, chapters IV--VI). A scalar multiple preserves the group.
The provider's root lattices are negative definite.
"""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize(
    "name,scalar,order",
    (("A2", 1, 12), ("D4", -1, 1152), ("E8", 2, 696729600)),
    ids=("negative_A2", "positive_D4", "negative_E8_twice"),
)
def test_the_delivered_generators_generate_the_full_definite_group(name, scalar, order):
    lattice = Lattices(ZZ)(name).twist(ZZ(scalar))
    orthogonal = lattice.O()
    family = tuple(orthogonal.group_generators())
    basis = tuple(lattice.module_generators())

    assert orthogonal.subgroup(family).cardinality() == cardinal(order)
    for isometry in family:
        for first in basis:
            assert isometry.inverse()(isometry(first)) == first
            for second in basis:
                assert lattice.b(isometry(first), isometry(second)) == lattice.b(first, second)
