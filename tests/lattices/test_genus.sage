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


def test_indefinite_isotropic_genus_has_complete_spinor_seed_enumeration() -> None:
    r"""For an isotropic indefinite lattice of rank at least three, each spinor
    genus contains one class (Conway--Sloane, *Sphere Packings, Lattices and Groups*,
    3rd ed., Ch. 15, §9.1, Thm. 14).  This isotropic ternary specimen has trivial
    improper spinor quotient, so the complete seed list is empty and the genus
    enumeration must return its single class.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 4, 0], [0, 0, -5]])
    genus = lattice.genus()

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice([1, 1, 1]).norm() == 0
    assert genus.spinor_genus_count() == 1
    assert genus.class_number() == 1
    assert genus.representatives().cardinality() == 1
    assert tuple(lattice.spinor_genus_class_numbers()) == (ZZ(1),)


def test_published_four_spinor_genus_is_counted_from_all_generators() -> None:
    r"""Benham--Hsia, *On spinor exceptional representations*, Nagoya Math. J.
    87 (1982), §2.3, p. 252, identify ``diag(1, 20, 400)`` as a genus with four
    spinor genera and twelve classes.  This checks the public consumer of Sage's
    spinor-generator list against the independent four-way partition.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 20, 0], [0, 0, 400]])
    genus = lattice.genus()

    assert lattice.spinor_genus_count() == 4
    assert genus.class_number() == 12
    assert genus.representatives().cardinality() == 12
    assert genus.mass() == QQ(3) / 2
    numbers = tuple(lattice.spinor_genus_class_numbers())
    assert len(numbers) == 4
    assert sum(numbers) == 12


def test_indefinite_genus_enumerates_each_nontrivial_spinor_seed() -> None:
    r"""The isotropic ternary lattice ``diag(1, 20, -400)`` has improper
    spinor quotient of order two.  Conway--Sloane, *Sphere Packings, Lattices
    and Groups*, 3rd ed., Ch. 15, §9.1, Thm. 14, says each spinor genus of an
    isotropic indefinite lattice of rank at least three is one class; hence
    this genus has exactly two.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 20, 0], [0, 0, -400]])
    genus = lattice.genus()

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice([20, 0, 1]).norm() == 0
    assert genus.spinor_genus_count() == 2
    assert genus.class_number() == 2
    assert genus.representatives().cardinality() == 2
    assert tuple(lattice.spinor_genus_class_numbers()) == (ZZ(1), ZZ(1))


def test_indefinite_signature_does_not_imply_rational_isotropy() -> None:
    r"""The isotropic spinor-genus theorem cannot be applied from signature alone.

    For ``x^2 + y^2 = 3 z^2``, reduction modulo 3 forces ``x`` and ``y``
    to be divisible by 3; substitution then forces ``z`` to be divisible by
    3.  Thus ``diag(1, 1, -3)`` has no nonzero rational isotropic vector,
    despite having real signature ``(2, 1)``.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, -3]])

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice.is_isotropic() is False
