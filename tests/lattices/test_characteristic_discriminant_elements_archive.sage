from sage_extensions.all import *


def test_the_divided_class_of_a_basis_vector_of_u2_is_not_characteristic() -> None:
    r"""On ``A_{U(2)} = (ZZ/2)^2`` every class has ``b(x, x) = 0``, so only ``0`` is characteristic.

    For ``x = (a e + b f)/2`` one has ``b(x, x) = ab`` in ``QQ/ZZ``, which is
    zero; a characteristic ``c`` must then pair trivially with every class,
    hence ``c = 0``, and ``e/2`` is a nonzero class.  The definition is
    Ito--Ohashi's (Michigan Math. J. 63 (2014), 159-188, Section 2, p. 162):
    an element ``x`` of a finite quadratic form ``(A, b, q)`` with
    ``q : A -> QQ/2ZZ`` and ``b : A x A -> QQ/ZZ`` is characteristic when
    ``b(x, a) = q(a) (mod 1)`` for every ``a`` in ``A``.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    first, _second = lattice.module_generators()
    divided_class = lattice.divided_discriminant_class(first)

    assert not divided_class.is_characteristic()


def test_diagonal_two_minus_two_has_a_characteristic_divided_class() -> None:
    r"""The divided class of ``e + f`` on ``diag(2, -2)`` answers characteristic.

    By the definition the module's other docstring cites (Ito--Ohashi,
    Michigan Math. J. 63 (2014), Section 2, p. 162): the class
    ``(e + f)/2`` pairs with each class ``x`` as ``q(x)`` does, the four
    differences ``q(x) - b(x, (e+f)/2)`` being ``0``, ``1``, ``0`` and ``0``.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    first, second = lattice.module_generators()
    divided_class = lattice.divided_discriminant_class(first + second)

    assert divided_class.is_characteristic()
