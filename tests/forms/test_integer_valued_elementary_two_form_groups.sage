r"""Full isometry groups of the integer-valued elementary two-forms.

The hyperbolic and anisotropic planes over F2 have orthogonal groups
of orders 2 and 6. In dimension four their orders are 72 and 120.
The generated subgroup is tested, as well as preservation of the actual
discriminant quadratic form on every element.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize(
    "planes,anisotropic,order",
    ((1, False, 2), (0, True, 6), (2, False, 72), (1, True, 120)),
    ids=("hyperbolic-plane", "anisotropic-plane", "plus-four", "minus-four"),
)
def test_the_actual_generated_group_preserves_the_complete_form(planes, anisotropic, order) -> None:
    lattices = Lattices(ZZ)
    ambient = lattices("D4") if anisotropic else lattices("U").twist(ZZ(2))
    for _index in range(planes if anisotropic else planes - 1):
        ambient = ambient + lattices("U").twist(ZZ(2))
    form = ambient.discriminant_quadratic_form()
    orthogonal = form.O()
    group_generators = tuple(orthogonal.group_generators())

    assert orthogonal.subgroup(group_generators).cardinality() == cardinal(order)
    assert all(form.q(generator(point)) == form.q(point) for generator in group_generators for point in form)

