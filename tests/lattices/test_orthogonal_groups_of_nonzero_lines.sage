r"""For a nonzero line form, a*u^2=a has precisely the solutions u=+-1."""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("ring", (ZZ, QQ), ids=("integral", "rational"))
@pytest.mark.parametrize("coefficient", (1, 2, -1, -2, 30))
def test_a_nonzero_line_has_the_full_sign_group(ring, coefficient) -> None:
    lattice = Lattices(ring)([[coefficient]])
    basis = next(iter(lattice.module_generators()))
    group = lattice.O()
    group_generators = tuple(group.group_generators())

    assert tuple(generator(basis) for generator in group_generators) == (-basis,)
    assert int(group.cardinality()) == 2
    assert all(generator(generator(basis)) == basis for generator in group_generators)
    assert all(lattice.b(generator(basis), generator(basis)) == ring(coefficient) for generator in group_generators)
