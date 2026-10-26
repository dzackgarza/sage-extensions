from sage_extensions.all import *


def test_level_uses_the_quadratic_discriminant_form_for_even_lattices() -> None:
    lattice = Lattices(ZZ)([[2]])

    assert lattice.discriminant_module().exponent() == 2
    assert lattice.level() == 4


def test_level_of_an_odd_lattice_is_the_bilinear_level() -> None:
    lattice = Lattices(ZZ)([[3]])

    assert not lattice.is_even()
    assert lattice.discriminant_module().exponent() == 3
    assert lattice.level() == 3


def test_unimodular_even_lattice_has_level_one() -> None:
    lattice = Lattices(ZZ)("E8")

    assert lattice.is_even() and lattice.is_unimodular()
    assert lattice.level() == 1


def test_genus_of_a2_is_determined_by_signature_and_discriminant_form() -> None:
    r"""An even lattice's genus is fixed by its signature and discriminant
    quadratic form (Nikulin 1979, Cor. 1.9.4); ``A2`` is negative definite of
    determinant ``3``.
    """
    lattice = Lattices(ZZ)("A2")
    genus = Lattices(ZZ).genus(signature_pair(0, 2), lattice.discriminant_quadratic_form())

    assert genus == lattice.genus()
    assert genus.determinant() == 3
    assert genus != Lattices(ZZ)([[-2, 0], [0, -2]]).genus()


def test_local_genus_symbol_and_excess_detect_nonisometry() -> None:
    a2 = Lattices(ZZ)("A2")
    diagonal = Lattices(ZZ)([[-2, 0], [0, -2]])
    genus = a2.genus()

    assert genus.level(3) == 3
    assert genus.excess(3) == 2
    assert a2.is_locally_isometric(a2, 3)
    assert not a2.is_locally_isometric(diagonal, 3)


def test_definite_genus_mass_and_class_number_are_exact() -> None:
    genus = Lattices(ZZ)("A2").genus()

    assert genus.class_number() == 1
    assert genus.representatives().cardinality() == 1
    assert genus.mass() == ZZ(1) / 12
