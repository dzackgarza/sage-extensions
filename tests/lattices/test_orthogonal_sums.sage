r"""The orthogonal direct sum as the monoidal operation on lattices.

``+`` is the orthogonal sum and ``**`` its iterate, so signature adds,
discriminant multiplies, and the zeroth power is the unit.
"""

from sage_extensions.all import *


def test_the_orthogonal_power_adds_signatures_and_multiplies_discriminants() -> None:
    plane = Lattices(ZZ)("U")

    assert (plane ** 3).module_rank() == 6
    assert (plane ** 3).signature_pair() == signature_pair(3, 3)
    assert (plane ** 3).determinant() == -1
    assert (plane ** 3).is_unimodular()


def test_a_definite_power_keeps_its_definiteness_and_squares_its_discriminant() -> None:
    root_lattice = Lattices(ZZ)("A2")

    assert (root_lattice ** 2).signature_pair() == signature_pair(0, 4)
    assert (root_lattice ** 2).determinant() == 9
    assert (root_lattice ** 2).is_negative_definite()
