r"""Primitive isotropic vectors in even 2-elementary lattices have the three standard cusp types."""

from sage_extensions.all import *  # noqa: F401,F403


def test_divisibility_one_isotropic_vector_has_odd_type() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    vector = lattice.module_generators()[0]

    assert vector.div() == 1
    assert lattice.get_isotropic_type(vector) == "Odd"


def test_divisibility_two_u2_vector_is_even_ordinary() -> None:
    lattice = NamedLattices.U_2
    vector = lattice.module_generators()[0]

    assert vector.div() == 2
    assert not vector.divided_discriminant_class().is_characteristic()
    assert lattice.get_isotropic_type(vector) == "Even ordinary"


def test_characteristic_divisibility_two_vector_is_even_characteristic() -> None:
    lattice = Lattices.IPQ(1, 1).twist(2)
    first, second = lattice.module_generators()
    vector = first + second

    assert vector.q() == 0
    assert vector.div() == 2
    assert vector.divided_discriminant_class().is_characteristic()
    assert lattice.get_isotropic_type(vector) == "Even characteristic"
