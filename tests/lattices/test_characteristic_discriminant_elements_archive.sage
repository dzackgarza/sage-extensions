from sage_extensions.all import *


def test_the_divided_class_of_a_basis_vector_of_u2_is_not_characteristic() -> None:
    r"""On ``A_{U(2)} = (ZZ/2)^2`` every class has ``b(x, x) = 0``, so only ``0`` is characteristic.

    For ``x = (a e + b f)/2`` one has ``b(x, x) = ab`` in ``QQ/ZZ``, which is
    zero; a characteristic ``c`` must then pair trivially with every class,
    hence ``c = 0``, and ``e/2`` is a nonzero class.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    first, _second = lattice.module_generators()
    divided_class = lattice.divided_discriminant_class(first)

    assert not divided_class.is_characteristic()


def test_diagonal_two_minus_two_has_a_characteristic_divided_class() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    first, second = lattice.module_generators()
    divided_class = lattice.divided_discriminant_class(first + second)

    assert divided_class.is_characteristic()
