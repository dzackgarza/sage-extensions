r"""Integer and polynomial ideals realize the public ideal arithmetic."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_ideal_arithmetic_and_quotients() -> None:
    four = ZZ.ideal(4)
    six = ZZ.ideal(6)
    twelve = ZZ.ideal(12)

    assert twelve in CommutativeIdeals(ZZ)
    assert twelve.ring() is ZZ
    assert twelve.contains_ambient_element(ZZ(24))
    assert not twelve.contains_ambient_element(ZZ(6))
    assert twelve.congruent(ZZ(13), ZZ(1))
    assert four.sum(six) == ZZ.ideal(2)
    assert four.intersection(six) == ZZ.ideal(12)
    assert four.product(six) == ZZ.ideal(24)
    assert four.colon(six) == ZZ.ideal(2)
    assert four.ideal_quotient(six) == ZZ.ideal(2)
    assert twelve.radical() == ZZ.ideal(6)
    assert twelve.power(2) == ZZ.ideal(144)
    assert twelve.quotient_ring().cardinality() == cardinal(12)
    assert ZZ.ideal(5).residue_cardinality() == cardinal(5)
    assert ZZ.ideal(5).is_prime()
    assert ZZ.ideal(5).is_maximal()
    assert not ZZ.ideal(6).is_prime()
    assert twelve.saturation(six) == ZZ.ideal(1)
    assert twelve.ideal_saturation(six) == ZZ.ideal(1)
    assert twelve.ideal_generators().cardinality() == cardinal(1)
    assert len(tuple(twelve.primary_decomposition())) == 2


def test_localized_integer_ideal_contracts_back_to_itself() -> None:
    ideal = ZZ.ideal(5)
    local = ZZ.localize_at_prime(5)
    extended = ideal.extension_to_localization(local)

    assert extended.contraction() == ideal
    assert extended.contraction_from_localization() == ideal


def test_polynomial_ideal_radical_intersection_and_hilbert_polynomial() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axis = plane.ideal(x)
    other_axis = plane.ideal(y)
    origin = plane.ideal(x, y)

    assert axis.intersection(other_axis) == plane.ideal(x * y)
    assert plane.ideal(x**2).radical() == axis
    assert axis.is_prime()
    assert not axis.is_maximal()
    assert origin.is_maximal()
    assert axis.hilbert_polynomial_value(10) == 1


def test_integer_ideal_is_fixed_by_the_identity_of_its_fraction_field() -> None:
    ideal = ZZ.ideal(5)
    identity = QQ.Mor(QQ).identity()

    assert ideal.image_under_fraction_field_automorphism(identity) == ideal

