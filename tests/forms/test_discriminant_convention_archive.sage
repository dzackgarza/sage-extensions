from sage_extensions.all import *


def test_peters_sterk_example_1_6_9_uses_nikulins_quadratic_convention() -> None:
    lattice = Lattices(ZZ)([[-2, 1, 0], [1, 2, 1], [0, 1, -2]])
    discriminant = lattice.discriminant_group()
    factors = discriminant.invariant_factors()

    assert factors.cardinality() == 1
    assert factors[0] == 12

    third_dual_class = discriminant.module_generators()[2]
    assert third_dual_class.additive_order() == 12
    assert third_dual_class.b(third_dual_class).lift() == QQ(7) / 12
    assert third_dual_class.q().lift() == QQ(19) / 12


def test_quadratic_and_bilinear_values_obey_the_nikulin_polarization() -> None:
    lattice = Lattices(ZZ)([[-2, 1, 0], [1, 2, 1], [0, 1, -2]])
    discriminant = lattice.discriminant_group()
    x = discriminant.module_generators()[2]

    polarized = (2 * x).q().lift() - 2 * x.q().lift()
    twice_bilinear = 2 * x.b(x).lift()
    difference = QQ(polarized - twice_bilinear)
    assert difference in ZZ
    assert ZZ(difference) in ZZ.ideal(2)
