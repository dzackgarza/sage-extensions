r"""Successive coordinate differences in <2>^20 have Gram 2 A19.

The difference lattice is the kernel of the coordinate-sum map. Its Gram
has diagonal 4, adjacent entries -2 and determinant 20 times 2^19.
"""

from sage_extensions.all import *


def test_coordinate_differences_have_the_full_scaled_a19_gram() -> None:
    lattice = Lattices(ZZ)([
        [2 if i == j else 0 for j in range(20)] for i in range(20)
    ])
    basis = tuple(lattice.module_generators())
    root_images = tuple(basis[i] - basis[i + 1] for i in range(19))
    differences = lattice.subobject_on(root_images)
    roots = tuple(differences.inclusion().lift(root) for root in root_images)

    assert differences.module_rank() == cardinal(19)
    assert differences.determinant() == ZZ(20 * 2**19)
    assert all(differences.q(root) == ZZ(4) for root in roots)
    assert all(
        differences.b(roots[i], roots[j]) == ZZ(4 if i == j else -2 if abs(i - j) == 1 else 0)
        for i in range(19) for j in range(19)
    )
