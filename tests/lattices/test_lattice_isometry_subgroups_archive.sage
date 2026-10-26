r"""The orthogonal group of the rank-one root lattice."""

from sage_extensions.all import *


def test_the_reflection_in_the_root_generates_O_A1_of_order_two() -> None:
    r"""\(O(\langle -2\rangle) = \{\pm 1\}\), and \(s_r(r) = -r\)."""
    lattice = Lattices(ZZ)("A1")
    root = lattice.basis_vector(0)
    reflection = lattice.reflection(root)
    orthogonal = lattice.O()

    subgroup = orthogonal.subgroup((reflection,))

    assert reflection(root) == -root
    assert orthogonal.order() == 2
    assert subgroup.order() == 2
