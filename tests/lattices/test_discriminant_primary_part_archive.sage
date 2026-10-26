from sage_extensions.all import *


def test_a2_discriminant_primary_part_is_the_whole_three_group() -> None:
    discriminant = NamedLattices.A2.discriminant_group()
    primary = discriminant.primary_part(3)

    assert primary.cardinality() == discriminant.cardinality() == 3
    assert all(element in primary for element in discriminant.elements())


def test_the_discriminant_of_A5_splits_into_primary_parts_of_orders_two_and_three() -> None:
    r"""disc(A_n) = Z/(n+1) (Conway--Sloane, SPLAG, ch. 4), so disc(A5) = Z/6 =
    Z/2 + Z/3 by the Chinese remainder theorem."""
    discriminant = Lattices(ZZ)("A5").discriminant_group()

    assert discriminant.cardinality() == 6
    assert discriminant.primary_part(2).cardinality() == 2
    assert discriminant.primary_part(3).cardinality() == 3
    assert discriminant.primary_part(5).cardinality() == 1
